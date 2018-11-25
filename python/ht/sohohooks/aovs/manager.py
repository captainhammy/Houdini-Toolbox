"""This module contains classes and functions for high level interaction
with AOVs.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import glob
import json
import os

# Houdini Toolbox Imports
from ht.sohohooks.aovs.aov import AOV, AOVGroup, IntrinsicAOVGroup

# Houdini Imports
import hou

# =============================================================================
# CLASSES
# =============================================================================

class AOVManager(object):
    """This class is for managing and applying AOVs at render time."""

    def __init__(self):
        self._aovs = {}
        self._groups = {}
        self._interface = None

        self._init_from_files()

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __repr__(self):
        return "<AOVManager AOVs:{} groups:{}>".format(
            len(self.aovs),
            len(self.groups),
        )

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _build_intrinsic_groups(self):
        """Build intrinsic groups."""
        # Process any AOVs that we have to look for any intrinsic groups.
        for aov in self.aovs.itervalues():
            for intrinsic_name in aov.intrinsics:
                # Intrinsic groups are prefixed with "i:".
                name = "i:" + intrinsic_name

                # Group exists so use it.
                if name in self.groups:
                    group = self.groups[name]

                # Create the group and add it to our list.
                else:
                    group = IntrinsicAOVGroup(name)
                    self.add_group(group)

                # Add this AOV to the group.
                group.aovs.append(aov)

    def _init_from_files(self):
        """Initialize the manager from files on disk."""
        file_paths = _find_aov_files()

        readers = [AOVFile(file_path) for file_path in file_paths]

        self._merge_readers(readers)

        self._build_intrinsic_groups()

    def _init_group_members(self, group):
        """Populate the AOV lists of each group based on available AOVs."""
        # Process each of the group's includes.
        for include in group.includes:
            # If the AOV name is available, add it to the group.
            if include in self.aovs:
                group.aovs.append(self.aovs[include])

    def _init_reader_aovs(self, reader):
        for aov in reader.aovs:
            variable_name = aov.variable

            # Check if this AOV has already been seen.
            if variable_name in self.aovs:
                # If this AOV has a higher priority, replace the previous
                # one.
                if aov.priority > self.aovs[variable_name].priority:
                    self.add_aov(aov)

            # Hasn't been seen, so add it.
            else:
                self.add_aov(aov)

    def _init_reader_groups(self, reader):
        for group in reader.groups:
            self._init_group_members(group)

            group_name = group.name

            # Check if this group has already been seen.
            if group_name in self.groups:
                # If this group has a higher priority, replace the previous
                # one.
                if group.priority > self.groups[group_name].priority:
                    self.add_group(group)

            # Hasn't been seen, so add it.
            else:
                self.add_group(group)

    def _merge_readers(self, readers):
        """Merge the data of multiple AOVFile objects."""
        # We need to handle AOVs first since AOVs in other files may overwrite
        # AOVs in group definition files.
        for reader in readers:
            self._init_reader_aovs(reader)

        # Now that AOVs have been made available, add them to groups.
        for reader in readers:
            self._init_reader_groups(reader)

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def aovs(self):
        """Dictionary containing all available AOVs."""
        return self._aovs

    @property
    def groups(self):
        """Dictionary containing all available AOVGroups."""
        return self._groups

    @property
    def interface(self):
        """Any AOVViewerInterface assigned to the manager."""
        return self._interface

    # =========================================================================
    # METHODS
    # =========================================================================

    def add_aov(self, aov):
        """Add an AOV to the manager."""
        self.aovs[aov.variable] = aov

        if self.interface is not None:
            self.interface.aovAddedSignal.emit(aov)

    def add_aovs_to_ifd(self, wrangler, cam, now):
        """Add auto_aovs to the ifd."""
        import IFDapi
        import IFDsettings
        import soho

        # The parameter that defines which automatic aovs to add.
        parms = {
            "enable": soho.SohoParm(
                "enable_auto_aovs",
                "int",
                [1],
                skipdefault=False
            ),
            "auto_aovs": soho.SohoParm(
                "auto_aovs",
                "str",
                [""],
                skipdefault=False
            ),
        }

        # Attempt to evaluate the parameter.
        plist = cam.wrangle(wrangler, parms, now)

        if plist:
            # Adding is disabled so bail out.
            if plist["enable_auto_aovs"].Value[0] == 0:
                return

            aov_str = plist["auto_aovs"].Value[0]

            # Parse the string to get any aovs/groups.
            aov_items = self.get_aovs_from_string(aov_str)

            # Write any found items to the ifd.
            for item in aov_items:
                item.write_to_ifd(wrangler, cam, now)

            # If we are generating the "Op_Id" plane we will need to tell SOHO
            # to generate these properties when outputting object.  Look for
            # the "Op_Id" variable being exported and if so enable operator id
            # generation.
            for aov in flatten_aov_items(aov_items):
                if aov.variable == "Op_Id":
                    IFDapi.ray_comment("Forcing object id generation")
                    IFDsettings._GenerateOpId = True

                    break

    def add_group(self, group):
        """Add an AOVGroup to the manager."""
        self.groups[group.name] = group

        if self.interface is not None:
            self.interface.groupAddedSignal.emit(group)

    def clear(self):
        """Clear all definitions."""
        self._aovs = {}
        self._groups = {}

    def get_aovs_from_string(self, aov_str):
        """Get a list of AOVs and AOVGroups from a string."""
        aovs = []

        aov_str = aov_str.replace(',', ' ')

        for name in aov_str.split():
            if name.startswith('@'):
                name = name[1:]

                if name in self.groups:
                    aovs.append(self.groups[name])

            else:
                if name in self.aovs:
                    aovs.append(self.aovs[name])

        return aovs

    def init_interface(self):
        """Initialize an AOVViewerInterface for this manager."""
        from ht.ui.aovs.utils import AOVViewerInterface

        self._interface = AOVViewerInterface()

    def load(self, path):
        """Load a file."""
        readers = [AOVFile(path)]

        self._merge_readers(readers)

    def reload(self):
        """Reload all definitions."""
        self.clear()
        self._init_from_files()

    def remove_aov(self, aov):
        """Remove the specified AOV from the manager."""
        if aov.variable in self.aovs:
            self.aovs.pop(aov.variable)

            if self.interface is not None:
                self.interface.aovRemovedSignal.emit(aov)

    def remove_group(self, group):
        """Remove the specified group from the manager."""
        if group.name in self.groups:
            self.groups.pop(group.name)

            if self.interface is not None:
                self.interface.groupRemovedSignal.emit(group)


class AOVFile(object):
    """Class to handle reading and writing AOV .json files."""

    def __init__(self, path):
        self._path = path

        self._aovs = []
        self._data = {}
        self._groups = []

        if self.exists:
            self._init_from_file()

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _create_aovs(self, definitions):
        """Create AOVs based on definitions."""
        for definition in definitions:
            # Insert this file path into the data.
            definition["path"] = self.path

            # Construct a new AOV and add it to our list.
            aov = AOV(definition)
            self.aovs.append(aov)

    def _create_groups(self, definitions):
        """Create AOVGroups based on definitions."""
        for name, group_data in definitions.iteritems():
            # Create a new AOVGroup.
            group = AOVGroup(name)

            # Process its list of AOVs to include.
            if "include" in group_data:
                group.includes.extend(group_data["include"])

            # Set any comment.
            if "comment" in group_data:
                group.comment = group_data["comment"]

            if "priority" in group_data:
                group.priority = group_data["priority"]

            # Set any icon.
            if "icon" in group_data:
                group.icon = os.path.expandvars(group_data["icon"])

            # Set the path to this file.
            group.path = self.path

            # Add the group to the list.
            self.groups.append(group)

    def _init_from_file(self):
        """Read data from the file and create the appropriate entities."""
        with open(self.path) as handle:
            data = json.load(handle)

        if "definitions" in data:
            self._create_aovs(data["definitions"])

        if "groups" in data:
            self._create_groups(data["groups"])

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def aovs(self):
        """List containing AOVs defined in this file."""
        return self._aovs

    @property
    def groups(self):
        """List containing AOVGroups defined in this file."""
        return self._groups

    @property
    def path(self):
        """File path on disk."""
        return self._path

    @property
    def exists(self):
        """Check if the file actually exists."""
        return os.path.isfile(self.path)

    # =========================================================================
    # METHODS
    # =========================================================================

    def add_aov(self, aov):
        """Add an AOV for writing."""
        self.aovs.append(aov)

    def add_group(self, group):
        """Add An AOVGroup for writing."""
        self.groups.append(group)

    def contains_aov(self, aov):
        """Check if this file contains an AOV with the same variable name."""
        return aov in self.aovs

    def contains_group(self, group):
        """Check if this file contains a group with the same name."""
        return group in self.groups

    def remove_aov(self, aov):
        """Remove an AOV from the file."""
        idx = self.aovs.index(aov)

        del self.aovs[idx]

    def remove_group(self, group):
        """Remove a group from the file."""
        idx = self.groups.index(group)

        del self.groups[idx]

    def replace_aov(self, aov):
        """Replace an AOV in the file."""
        idx = self.aovs.index(aov)

        self.aovs[idx] = aov

    def replace_group(self, group):
        """Replace a group in the file."""
        idx = self.groups.index(group)

        self.groups[idx] = group

    def write_to_file(self, path=None):
        """Write data to file."""
        data = {}

        for group in self.groups:
            groups = data.setdefault("groups", {})

            groups.update(group.as_data())

        for aov in self.aovs:
            aovs = data.setdefault("definitions", [])

            aovs.append(aov.as_data())

        if path is None:
            path = self.path

        with open(path, 'w') as handle:
            json.dump(data, handle, indent=4)

# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

def _find_aov_files():
    """Find any .json files that should be read."""
    # Look for the specific AOV search path.
    if "HT_AOV_PATH" in os.environ:
        directories = _get_aov_path_folders()

    else:
        directories = _find_houdinipath_aov_folders()

    all_files = []

    for directory in directories:
        all_files.extend(glob.glob(os.path.join(directory, "*.json")))

    return tuple(all_files)


def _find_houdinipath_aov_folders():
    """Look for any config/aovs folders in the HOUDINI_PATH."""
    # Try to find HOUDINI_PATH directories.
    try:
        directories = hou.findDirectories("config/aovs")

    except hou.OperationFailed:
        directories = ()

    return directories


def _get_aov_path_folders():
    # Get the search path.
    search_path = os.environ["HT_AOV_PATH"]

    # If '&' is in the path then following Houdini path conventions we'll
    # search through the HOUDINI_PATH as well.
    if '&' in search_path:
        # Find any config/aovs folders in HOUDINI_PATH.
        hpath_dirs = _find_houdinipath_aov_folders()

        # If there are any then we replace the '&' with those paths.
        if hpath_dirs:
            search_path = search_path.replace('&', ':'.join(hpath_dirs))

    return tuple(search_path.split(":"))

# =============================================================================
# FUNCTIONS
# =============================================================================

def build_menu_script():
    """Build a menu script for choosing AOVs and groups."""
    menu = []

    if MANAGER.groups:
        for group in sorted(MANAGER.groups.keys()):
            menu.extend(["@{}".format(group), group])

        menu.extend(["_separator_", ""])

    for aov in sorted(MANAGER.aovs.keys()):
        menu.extend([aov, aov])

    return tuple(menu)


def flatten_aov_items(items):
    """Flatten a list that contains AOVs and groups into a list of all AOVs."""
    aovs = []

    for item in items:
        if isinstance(item, AOVGroup):
            aovs.extend(item.aovs)

        else:
            aovs.append(item)

    return tuple(aovs)


def load_json_files():
    """Load .json files into the manager."""
    result = hou.ui.selectFile(
        pattern="*.json",
        chooser_mode=hou.fileChooserMode.Read,
        multiple_select=True,
    )

    paths = result.split(" ; ")

    for path in paths:
        path = os.path.expandvars(path)

        if os.path.exists(path):
            MANAGER.load(path)

# =============================================================================

MANAGER = AOVManager()

