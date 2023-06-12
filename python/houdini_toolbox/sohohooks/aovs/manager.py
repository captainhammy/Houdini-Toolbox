"""This module contains classes and functions for high level interaction
with AOVs.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Future
from __future__ import annotations

# Standard Library
import glob
import json
import os
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

# Houdini Toolbox
from houdini_toolbox.sohohooks.aovs import constants as consts
from houdini_toolbox.sohohooks.aovs.aov import AOV, AOVGroup, IntrinsicAOVGroup

# Houdini
import hou

if TYPE_CHECKING:
    from houdini_toolbox.ui.aovs.utils import (
        AOVViewerInterface,  # pylint: disable=ungrouped-imports
    )

    import soho  # type: ignore


# =============================================================================
# CLASSES
# =============================================================================


class AOVManager:
    """This class is for managing and applying AOVs at render time."""

    def __init__(self) -> None:
        self._aovs: Dict[str, AOV] = {}
        self._groups: Dict[str, AOVGroup] = {}
        self._interface: Optional[AOVViewerInterface] = None

        self._init_from_files()

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"<AOVManager AOVs:{len(self.aovs)} groups:{len(self.groups)}>"

    # -------------------------------------------------------------------------
    # NON-PUBLIC METHODS
    # -------------------------------------------------------------------------

    def _build_intrinsic_groups(self) -> None:
        """Build intrinsic groups.

        :return:

        """
        # Process any AOVs that we have to look for any intrinsic groups.
        for aov in list(self.aovs.values()):
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

    def _init_from_files(self) -> None:
        """Initialize the manager from files on disk.

        :return:

        """
        file_paths = _find_aov_files()

        readers = [AOVFile(file_path) for file_path in file_paths]

        self._merge_readers(readers)

        self._build_intrinsic_groups()

    def _init_group_members(self, group: AOVGroup) -> None:
        """Populate the AOV lists of each group based on available AOVs.

        :param group: A group to populate.
        :return:

        """
        # Process each of the group's includes.
        for include in group.includes:
            # If the AOV name is available, add it to the group.
            if include in self.aovs:
                group.aovs.append(self.aovs[include])

    def _init_reader_aovs(self, reader: AOVFile) -> None:
        """Initialize aovs from a reader.

        :param reader: A source reader.
        :return:

        """
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

    def _init_reader_groups(self, reader: AOVFile) -> None:
        """Initialize groups from a reader.

        :param reader: A source reader.
        :return:

        """
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

    def _merge_readers(self, readers: List[AOVFile]) -> None:
        """Merge the data of multiple AOVFile objects.

        :param readers: A list of file readers.
        :return:

        """
        # We need to handle AOVs first since AOVs in other files may overwrite
        # AOVs in group definition files.
        for reader in readers:
            self._init_reader_aovs(reader)

        # Now that AOVs have been made available, add them to groups.
        for reader in readers:
            self._init_reader_groups(reader)

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def aovs(self) -> Dict[str, AOV]:
        """Dictionary containing all available AOVs."""
        return self._aovs

    @property
    def groups(self) -> Dict[str, AOVGroup]:
        """Dictionary containing all available AOVGroups."""
        return self._groups

    @property
    def interface(self) -> Optional[AOVViewerInterface]:
        """A viewer interface assigned to the manager."""
        return self._interface

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def add_aov(self, aov: AOV) -> None:
        """Add an AOV to the manager.

        :param aov: An aov to add.
        :return:

        """
        self.aovs[aov.variable] = aov

        if self.interface is not None:
            self.interface.aov_added_signal.emit(aov)  # type: ignore

    def add_aovs_to_ifd(self, wrangler: Any, cam: soho.SohoObject, now: float) -> None:
        """Add auto_aovs to the ifd.

        :param wrangler: A SOHO wrangler.
        :param cam: A SOHO camera.
        :param now: The evaluation time.
        :return:

        """
        import IFDapi
        import IFDsettings  # type: ignore
        import soho

        # The parameter that defines which automatic aovs to add.
        parms = {
            "enable": soho.SohoParm("enable_auto_aovs", "int", [1], skipdefault=False),
            "auto_aovs": soho.SohoParm("auto_aovs", "str", [""], skipdefault=False),
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
                    IFDsettings._GenerateOpId = True  # pylint: disable=protected-access

                    break

    def add_group(self, group: AOVGroup) -> None:
        """Add an AOVGroup to the manager.

        :param group: A group to add.
        :return:

        """
        self.groups[group.name] = group

        if self.interface is not None:
            self.interface.group_added_signal.emit(group)  # type: ignore

    def attach_interface(self, interface: AOVViewerInterface) -> None:
        """Initialize an AOVViewerInterface for this manager.

        :return:

        """
        self._interface = interface

    def clear(self) -> None:
        """Clear all definitions.

        :return:

        """
        self._aovs.clear()
        self._groups.clear()

    def get_aovs_from_string(self, aov_str: str) -> Tuple[Union[AOV, AOVGroup], ...]:
        """Get a list of AOVs and AOVGroups from a string.

        :param aov_str: A string containing aov/group names.
        :return: A tuple of aovs and groups.


        """
        result: List[Union[AOV, AOVGroup]] = []

        aov_str = aov_str.replace(",", " ")

        for name in aov_str.split():
            if name.startswith("@"):
                name = name[1:]

                if name in self.groups:
                    result.append(self.groups[name])

            else:
                if name in self.aovs:
                    result.append(self.aovs[name])

        return tuple(result)

    def load(self, path: str) -> None:
        """Load a file.

        :param path: The file to load.
        :return:

        """
        readers = [AOVFile(path)]

        self._merge_readers(readers)

    def reload(self) -> None:
        """Reload all definitions.

        :return:

        """
        self.clear()
        self._init_from_files()

    def remove_aov(self, aov: AOV) -> None:
        """Remove the specified AOV from the manager.

        :param aov: The aov to remove
        :return:

        """
        if aov.variable in self.aovs:
            self.aovs.pop(aov.variable)

            if self.interface is not None:
                self.interface.aov_removed_signal.emit(aov)  # type: ignore

    def remove_group(self, group: AOVGroup) -> None:
        """Remove the specified group from the manager.

        :param group: The group to remove
        :return:

        """
        if group.name in self.groups:
            self.groups.pop(group.name)

            if self.interface is not None:
                self.interface.group_removed_signal.emit(group)  # type: ignore


class AOVFile:
    """Class to handle reading and writing AOV .json files.

    :param path: The path to the file.

    """

    def __init__(self, path: str) -> None:
        self._path = path

        self._aovs: List[AOV] = []
        self._data: Dict[Any, Any] = {}
        self._groups: List[AOVGroup] = []

        if self.exists:
            self._init_from_file()

    # -------------------------------------------------------------------------
    # NON-PUBLIC METHODS
    # -------------------------------------------------------------------------

    def _create_aovs(self, definitions: List[dict]) -> None:
        """Create AOVs based on definitions.

        :param definitions: AOV definition data.
        :return:

        """
        for definition in definitions:
            # Insert this file path into the data.
            definition["path"] = self.path

            # Construct a new AOV and add it to our list.
            aov = AOV(definition)
            self.aovs.append(aov)

    def _create_groups(self, definitions: dict) -> None:
        """Create AOVGroups based on definitions.

        :param definitions: AOVGroup definition data.
        :return:

        """
        for name, group_data in list(definitions.items()):
            # Create a new AOVGroup.
            group = AOVGroup(name)

            # Process its list of AOVs to include.
            if consts.GROUP_INCLUDE_KEY in group_data:
                group.includes.extend(group_data[consts.GROUP_INCLUDE_KEY])

            # Set any comment.
            if consts.COMMENT_KEY in group_data:
                group.comment = group_data[consts.COMMENT_KEY]

            if consts.PRIORITY_KEY in group_data:
                group.priority = group_data[consts.PRIORITY_KEY]

            # Set any icon.
            if consts.GROUP_ICON_KEY in group_data:
                group.icon = os.path.expandvars(group_data[consts.GROUP_ICON_KEY])

            # Set the path to this file.
            group.path = self.path

            # Add the group to the list.
            self.groups.append(group)

    def _init_from_file(self) -> None:
        """Read data from the file and create the appropriate entities.

        :return:

        """
        with open(self.path, encoding="utf-8") as handle:
            data = json.load(handle)

        if consts.FILE_DEFINITIONS_KEY in data:
            self._create_aovs(data[consts.FILE_DEFINITIONS_KEY])

        if consts.FILE_GROUPS_KEY in data:
            self._create_groups(data[consts.FILE_GROUPS_KEY])

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def aovs(self) -> List[AOV]:
        """List containing AOVs defined in this file."""
        return self._aovs

    @property
    def groups(self) -> List[AOVGroup]:
        """List containing AOVGroups defined in this file."""
        return self._groups

    @property
    def path(self) -> str:
        """File path on disk."""
        return self._path

    @property
    def exists(self) -> bool:
        """Check if the file actually exists."""
        return os.path.isfile(self.path)

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def add_aov(self, aov: AOV) -> None:
        """Add an AOV for writing.

        :param aov: The aov to add.
        :return:

        """
        self.aovs.append(aov)

    def add_group(self, group: AOVGroup) -> None:
        """Add An AOVGroup for writing.

        :param group: The group to add.
        :return:

        """
        self.groups.append(group)

    def contains_aov(self, aov: AOV) -> bool:
        """Check if this file contains an AOV with the same variable name.

        :param aov: The aov to check.
        :return: Whether the aov is in this file.

        """
        return aov in self.aovs

    def contains_group(self, group: AOVGroup) -> bool:
        """Check if this file contains a group with the same name.

        :param group: The group to check.
        :return: Whether the group is in this file.

        """
        return group in self.groups

    def remove_aov(self, aov: AOV) -> None:
        """Remove an AOV from the file.

        :param aov: The aov to remove.
        :return:

        """
        idx = self.aovs.index(aov)

        del self.aovs[idx]

    def remove_group(self, group: AOVGroup) -> None:
        """Remove a group from the file.

        :param group: The group to remove
        :return:

        """
        idx = self.groups.index(group)

        del self.groups[idx]

    def replace_aov(self, aov: AOV) -> None:
        """Replace an AOV in the file.

        :param aov: An aov to replace.
        :return:

        """
        idx = self.aovs.index(aov)

        self.aovs[idx] = aov

    def replace_group(self, group: AOVGroup) -> None:
        """Replace a group in the file.

        :param group: A group to replace.
        :return:

        """
        idx = self.groups.index(group)

        self.groups[idx] = group

    def write_to_file(self, path: Optional[str] = None) -> None:
        """Write data to file.

        If `path` is not set, use the AOVFile's path.

        :param path: Optional target path
        :return:

        """
        data: Dict[str, Union[Dict, List]] = {}

        for group in self.groups:
            group_data = data.setdefault(consts.FILE_GROUPS_KEY, {})

            group_data.update(group.as_data())  # type: ignore

        for aov in self.aovs:
            aov_data = data.setdefault(consts.FILE_DEFINITIONS_KEY, [])

            aov_data.append(aov.as_data())  # type: ignore

        if path is None:
            path = self.path

        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=4)


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _find_aov_files() -> Tuple[str, ...]:
    """Find any .json files that should be read.

    :return: json files to be read.

    """
    # Look for the specific AOV search path.
    if "HT_AOV_PATH" in os.environ:
        directories = _get_aov_path_folders()

    else:
        directories = _find_houdinipath_aov_folders()

    all_files = []

    for directory in directories:
        all_files.extend(glob.glob(os.path.join(directory, "*.json")))

    return tuple(str(f) for f in all_files)


def _find_houdinipath_aov_folders() -> Tuple[str, ...]:
    """Look for any config/aovs folders in the HOUDINI_PATH.

    :return: Folder paths to search.

    """
    # Try to find HOUDINI_PATH directories.
    try:
        directories = hou.findDirectories("config/aovs")

    except hou.OperationFailed:
        directories = ()

    return directories


def _get_aov_path_folders() -> Tuple[str, ...]:
    """Get a list of paths to search from HT_AOV_PATH.

    :return: Folder paths to search.

    """
    # Get the search path.
    search_path = os.environ["HT_AOV_PATH"]

    # If '&' is in the path then following Houdini path conventions we'll
    # search through the HOUDINI_PATH as well.
    if "&" in search_path:
        # Find any config/aovs folders in HOUDINI_PATH.
        directories = _find_houdinipath_aov_folders()

        # If there are any then we replace the '&' with those paths.
        if directories:
            search_path = search_path.replace("&", ":".join(directories))

    return tuple(search_path.split(":"))


# =============================================================================
# FUNCTIONS
# =============================================================================


def build_menu_script() -> Tuple[str, ...]:
    """Build a menu script for choosing AOVs and groups.

    :return: The menu script.

    """
    menu = []

    if AOV_MANAGER.groups:
        for group in sorted(AOV_MANAGER.groups.keys()):
            menu.extend([f"@{group}", group])

        menu.extend(["_separator_", ""])

    for aov in sorted(AOV_MANAGER.aovs.keys()):
        menu.extend([aov, aov])

    return tuple(menu)


def flatten_aov_items(items: Tuple[Union[AOV, AOVGroup], ...]) -> Tuple[AOV, ...]:
    """Flatten a list that contains AOVs and groups into a list of all AOVs.

    :param items: A list of items to flatten,
    :return: All the items flattened into a tuple of aovs.

    """
    aovs = []

    for item in items:
        if isinstance(item, AOVGroup):
            aovs.extend(item.aovs)

        else:
            aovs.append(item)

    return tuple(aovs)


def load_json_files() -> None:
    """Load .json files into the manager.

    :return:

    """
    result = hou.ui.selectFile(
        pattern="*.json", chooser_mode=hou.fileChooserMode.Read, multiple_select=True
    )

    paths = result.split(" ; ")

    for path in paths:
        path = os.path.expandvars(path)

        if os.path.exists(path):
            AOV_MANAGER.load(path)


# =============================================================================

AOV_MANAGER = AOVManager()
