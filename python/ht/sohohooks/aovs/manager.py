"""This module contains classes and functions for high level interaction
with AOVs.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import glob
import json
import os

# Houdini Toolbox Imports
from ht.sohohooks.aovs.aov import AOV, AOVGroup, IntrinsicAOVGroup
from ht.sohohooks.aovs import constants as consts
from ht.sohohooks.aovs import sources

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

        self._source_manager = sources.AOVSourceManager()

        self._init_from_files()

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __repr__(self):
        return "<AOVManager AOVs:{} groups:{}>".format(
            len(self.aovs),
            len(self.groups),
        )

    # -------------------------------------------------------------------------
    # NON-PUBLIC METHODS
    # -------------------------------------------------------------------------

    def _build_intrinsic_groups(self):
        """Build intrinsic groups.

        :return:

        """
        # Process any AOVs that we have to look for any intrinsic groups.
        for aov in self.aovs.values():
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

                # TODO: Add signal and emit that the intrinsic group changed
                if aov not in group.aovs:
                    # Add this AOV to the group.
                    group.aovs.append(aov)

#                    if self.interface is not None:
 #                       self.interface.aovAddedSignal.emit(aov)

    def _init_from_files(self):
        """Initialize the manager from files on disk.

        :return:

        """
        file_paths = _find_aov_files()

        file_sources = [self._source_manager.get_file_source(file_path) for file_path in file_paths]

        self._merge_sources(file_sources)

        self._build_intrinsic_groups()

    def _init_group_members(self, group):
        """Populate the AOV lists of each group based on available AOVs.

        :param group: A group to populate.
        :type group: ht.sohohooks.aovs.aov.AOVGroup
        :return:

        """
        # Process each of the group's includes.
        for include in group.includes:
            # If the AOV name is available, add it to the group.
            if include in self.aovs:
                group.aovs.append(self.aovs[include])

    def _init_source_aovs(self, source):
        """Initialize aovs from a reader.

        :param source: A source reader.
        :type source: AOVFile
        :return:

        """
        for aov in source.aovs:
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

    def _init_source_groups(self, source):
        """Initialize groups from a reader.

        :param source: A source reader.
        :type source: AOVFile
        :return:

        """
        for group in source.groups:
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

    def _merge_sources(self, sources):
        """Merge the data of multiple AOVFile objects.

        :param sources: A list of file readers.
        :type sources: list(AOVFile)
        :return:

        """
        # We need to handle AOVs first since AOVs in other files may overwrite
        # AOVs in group definition files.
        for source in sources:
            self._init_source_aovs(source)

        # Now that AOVs have been made available, add them to groups.
        for source in sources:
            self._init_source_groups(source)

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def aovs(self):
        """dict: Dictionary containing all available AOVs."""
        return self._aovs

    @property
    def groups(self):
        """dict: Dictionary containing all available AOVGroups."""
        return self._groups

    @property
    def interface(self):
        """AOVViewerInterface: A viewer interface assigned to the manager."""
        return self._interface

    @property
    def source_manager(self):
        return self._source_manager

    # =========================================================================
    # METHODS
    # -------------------------------------------------------------------------

    def add_aov(self, aov):
        """Add an AOV to the manager.

        :param aov: An aov to add.
        :type aov: ht.sohohooks.aovs.aov.AOV
        :return:

        """
        self.aovs[aov.variable] = aov

        if self.interface is not None:
            self.interface.aov_added_signal.emit(aov)

    def add_aovs_to_ifd(self, wrangler, cam, now):
        """Add auto_aovs to the ifd.

        :param wrangler: A SOHO wrangler.
        :type wrangler: object
        :param cam: A SOHO camera.
        :type cam: soho.SohoObject
        :param now: The evaluation time.
        :type now: float
        :return:

        """
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
        """Add an AOVGroup to the manager.

        :param group: A group to add.
        :type group: ht.sohohooks.aovs.aov.AOVGroup
        :return:

        """
        self.groups[group.name] = group

        if self.interface is not None:
            self.interface.group_added_signal.emit(group)

    def clear(self):
        """Clear all definitions.

        :return:

        """
        self._aovs.clear()
        self._groups.clear()

    def get_aovs_from_string(self, aov_str):
        """Get a list of AOVs and AOVGroups from a string.

        :param aov_str: A string containing aov/group names.
        :type aov_str: str
        :return: A tuple of aovs and groups.
        :rtype: tuple

        """
        result = []

        aov_str = aov_str.replace(',', ' ')

        for name in aov_str.split():
            if name.startswith('@'):
                name = name[1:]

                if name in self.groups:
                    result.append(self.groups[name])

            else:
                if name in self.aovs:
                    result.append(self.aovs[name])

        return tuple(result)

    def init_interface(self):
        """Initialize an AOVViewerInterface for this manager.

        :return:

        """
        from ht.ui.aovs.utils import AOVViewerInterface

        self._interface = AOVViewerInterface()

    def load(self, path):
        """Load a file.

        :param path: The file to load.
        :type path: str
        :return:

        """
        sources = [self.source_manager.get_file_source(path)]

        self._merge_sources(sources)

    def load_source(self, source):
        self._merge_sources([source])

        self._build_intrinsic_groups()

    def load_section_source(self, section):
        source = self.source_manager.get_asset_section_source(section)

        self.load_source(source)

    def reload(self):
        """Reload all definitions.

        :return:

        """
        self.clear()
        self._init_from_files()

    def remove_aov(self, aov):
        """Remove the specified AOV from the manager.

        :param aov: The aov to remove
        :type aov: ht.sohohooks.aovs.aov.AOV
        :return:

        """
        if aov.variable in self.aovs:
            self.aovs.pop(aov.variable)

            if self.interface is not None:
                self.interface.aov_removed_signal.emit(aov)

            for group in self.groups.values():
                if aov in group.aovs:
                    group.aovs.remove(aov)

                if not group.aovs:
                    self.remove_group(group)

    def remove_group(self, group):
        """Remove the specified group from the manager.

        :param group: The group to remove
        :type group: ht.sohohooks.aovs.aov.AOVGroup
        :return:

        """
        if group.name in self.groups:
            self.groups.pop(group.name)

            if self.interface is not None:
                self.interface.group_removed_signal.emit(group)

    def remove_source(self, source):
        for aov in source.aovs:
            self.remove_aov(aov)

        for group in source.groups:
            self.remove_group(group)

        self.source_manager.remove_source(source)

    def remove_section_source(self, section):
        source = self.source_manager.get_asset_section_source(section)

        self.remove_source(source)

    def clear_hip_source(self):
        self.remove_source(self.source_manager.hip_source)
        self.remove_source(self.source_manager.unsaved_source)

    def init_hip_source(self):
        self.clear_hip_source()

        self.source_manager.hip_source.reload()
        self.load_source(self.source_manager.hip_source)

        self.source_manager.unsaved_source.clear()
        self.load_source(self.source_manager.unsaved_source)



# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

def _find_aov_files():
    """Find any .json files that should be read.

    :return: json files to be read.
    :rtype: tuple(str)

    """
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
    """Look for any config/aovs folders in the HOUDINI_PATH.

    :return: Folder paths to search.
    :rtype: tuples(str)

    """
    # Try to find HOUDINI_PATH directories.
    try:
        directories = hou.findDirectories("config/aovs")

    except hou.OperationFailed:
        directories = ()

    return directories


def _get_aov_path_folders():
    """Get a list of paths to search from HT_AOV_PATH.

    :return: Folder paths to search.
    :rtype: tuple(str)

    """
    # Get the search path.
    search_path = os.environ["HT_AOV_PATH"]

    # If '&' is in the path then following Houdini path conventions we'll
    # search through the HOUDINI_PATH as well.
    if '&' in search_path:
        # Find any config/aovs folders in HOUDINI_PATH.
        directories = _find_houdinipath_aov_folders()

        # If there are any then we replace the '&' with those paths.
        if directories:
            search_path = search_path.replace('&', ':'.join(directories))

    return tuple(search_path.split(":"))


# =============================================================================
# FUNCTIONS
# =============================================================================

def build_menu_script():
    """Build a menu script for choosing AOVs and groups.

    :return: The menu script.
    :rtype: tuple(str)

    """
    menu = []

    if MANAGER.groups:
        for group in sorted(MANAGER.groups.keys()):
            menu.extend(["@{}".format(group), group])

        menu.extend(["_separator_", ""])

    for aov in sorted(MANAGER.aovs.keys()):
        menu.extend([aov, aov])

    return tuple(menu)


def flatten_aov_items(items):
    """Flatten a list that contains AOVs and groups into a list of all AOVs.

    :param items: A list of items to flatten,
    :type items: tuple
    :return: All the items flattened into a tuple of aovs.
    :rtype: tuple(ht.sohohooks.aovs.aov.AOV)

    """
    aovs = []

    for item in items:
        if isinstance(item, AOVGroup):
            aovs.extend(item.aovs)

        else:
            aovs.append(item)

    return tuple(aovs)


def load_json_files():
    """Load .json files into the manager.

    :return:

    """
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
