"""This module contains classes and funcions for high level interaction
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
from ht.utils import convertFromUnicode

# Houdini Imports
import hou

# =============================================================================
# CLASSES
# =============================================================================

class AOVManager(object):
    """This class is for managing and applying AOVs at rendertime."""

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self):
        self._aovs = {}
        self._groups = {}
        self._interface = None

        self._initFromFiles()

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __repr__(self):
        return "<AOVManager aovs:{} groups:{}>".format(
            len(self.aovs),
            len(self.groups),
        )

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def interface(self):
        """Any AOVViewerInterface assigned to the manager."""
        return self._interface

    # =========================================================================

    @property
    def aovs(self):
        """Dicionary containing all available AOVs."""
        return self._aovs

    # =========================================================================

    @property
    def groups(self):
        """Dictionary containing all available AOVGroups."""
        return self._groups

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _buildIntrinsicGroups(self):
        """Build intrinsic groups."""
        # Process any AOVs that we have to look for any instrinsic groups.
        for aov in self.aovs.itervalues():
            if aov.intrinsic is not None:
                # Intrinsic groups are prefixed with "i:".
                intrinsic_name = "i:" + aov.intrinsic

                # Group exists so use it.
                if intrinsic_name in self.groups:
                    group = self.groups[intrinsic_name]

                # Create the group and add it to our list.
                else:
                    group = IntrinsicAOVGroup(intrinsic_name)
                    self.addGroup(group)

                # Add this AOV to the group.
                group.aovs.append(aov)

    # =========================================================================

    def _initFromFiles(self):
        """Intialize the manager from files on disk."""
        file_paths = _findAOVFiles()

        readers = [AOVFile(file_path) for file_path in file_paths]

        self._mergeReaders(readers)

        self._buildIntrinsicGroups()

    # =========================================================================

    def _initGroupMembers(self, group):
        """Populate the AOV lists of each group based on available AOVs."""
        # Process each of the group's includes.
        for include in group.includes:
            # If the AOV name is available, add it to the group.
            if include in self.aovs:
                group.aovs.append(self.aovs[include])

    # =========================================================================

    def _mergeReaders(self, readers):
        """Merge the data of multiple AOVFile objects."""
        # We need to handle AOVs first since AOVs in other files may overwrite
        # AOVs in group definition files.
        for reader in readers:
            for aov in reader.aovs:
                variable_name = aov.variable

                # Check if this AOV has already been seen.
                if variable_name in self.aovs:
                    # If this AOV has a higher priority, replace the previous
                    # one.
                    if aov.priority > self.aovs[variable_name].priority:
                        self.addAOV(aov)

                # Hasn't been seen, so add it.
                else:
                    self.addAOV(aov)

        # Now that AOVs have been made available, add them to groups.
        for reader in readers:
            for group in reader.groups:
                self._initGroupMembers(group)

                group_name = group.name

                # Check if this group has already been seen.
                if group_name in self.groups:
                    # If this group has a higher priority, replace the previous
                    # one.
                    if group.priority > self.groups[group_name].priority:
                        self.addGroup(group)

                # Hasn't been seen, so addit.
                else:
                    self.addGroup(group)

    # =========================================================================
    # STATIC METHODS
    # =========================================================================

    @staticmethod
    def addAOVsToIfd(wrangler, cam, now):
        """Add auto_aovs to the ifd."""
        import IFDapi
        import IFDsettings
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

            # Construct a manager-laf
            manager = findOrCreateSessionAOVManager()

            # Parse the string to get any aovs/groups.
            aovs = manager.getAOVsFromString(aov_str)

            # Write any found items to the ifd.
            for aov in aovs:
                aov.writeToIfd(wrangler, cam, now)

            # If we are generating the "Op_Id" plane we will need to tell SOHO
            # to generate these properties when outputting object.  Look for
            # the "Op_Id" variable being exported and if so enable opid
            # generation
            for aov in aovs:
                if aov.variable == "Op_Id":
                    IFDapi.ray_comment("Forcing object id generation")
                    IFDsettings._GenerateOpId = True

                    break

    # =========================================================================
    # METHODS
    # =========================================================================

    def addAOV(self, aov):
        """Add an AOV to the manager."""
        self._aovs[aov.variable] = aov

        if self.interface is not None:
            self.interface.aovAddedSignal.emit(aov)

    # =========================================================================

    def addGroup(self, group):
        """Add an AOVGroup to the manager."""
        self.groups[group.name] = group

        if self.interface is not None:
            self.interface.groupAddedSignal.emit(group)

    # =========================================================================

    def clear(self):
        """Clear all definitions."""
        self._aovs = {}
        self._groups = {}

    # =========================================================================

    def getAOVsFromString(self, aov_str):
        """Get a list of AOVs and AOVGroups from a string."""
        aovs = []

        aov_str = aov_str.replace(',', ' ')

        for name in aov_str.split():
            if name.startswith('@'):
                name = name[1:]

                if name in self.groups:
                    aovs.append(self.groups[name])

            else:
                if name in self._aovs:
                    aovs.append(self._aovs[name])

        return aovs

    # =========================================================================

    def initInterface(self):
        """Initialize an AOVViewerInterface for this manager."""
        from ht.ui.aovs.utils import AOVViewerInterface
        self._interface = AOVViewerInterface()

    # =========================================================================

    def load(self, path):
        """Load a file."""
        readers = [AOVFile(path)]

        self._mergeReaders(readers)

    # =========================================================================

    def reload(self):
        """Reload all definitions."""
        self.clear()
        self._initFromFiles()

    # =========================================================================

    def removeAOV(self, aov):
        """Remove the specified AOV from the manager."""
        if aov.variable in self.aovs:
            self.aovs.pop(aov.variable)

            if self.interface is not None:
                self.interface.aovRemovedSignal.emit(aov)

    # =========================================================================

    def removeGroup(self, group):
        """Remove the specified group from the manager."""
        if group.name in self.groups:
            self.groups.pop(group.name)

            if self.interface is not None:
                self.interface.groupRemovedSignal.emit(group)

# =============================================================================

class AOVFile(object):
    """Class to handle reading and writing AOV .json files."""

    def __init__(self, path):
        self._path = path

        self._aovs = []
        self._data = {}
        self._groups = []

        if self.exists:
            self._initFromFile()

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def aovs(self):
        """List containing AOVs defined in this file."""
        return self._aovs

    # =========================================================================

    @property
    def groups(self):
        """List containing AOVGroups defined in this file."""
        return self._groups

    # =========================================================================

    @property
    def path(self):
        """File path on disk."""
        return self._path

    # =========================================================================

    @property
    def exists(self):
        """Check if the file actually exists."""
        return os.path.isfile(self.path)

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _initFromFile(self):
        """Read data from the file and create the appropriate entities."""
        with open(self.path) as handle:
            data = json.load(handle, object_hook=convertFromUnicode)

        if "definitions" in data:
            self._createAOVs(data["definitions"])

        if "groups" in data:
            self._createGroups(data["groups"])

    # =========================================================================

    def _createAOVs(self, definitions):
        """Create AOVs based on definitions."""
        for definition in definitions:
            # Insert this file path into the data.
            definition["path"] = self.path

            # Construct a new AOV and add it to our list.
            aov = AOV(definition)
            self.aovs.append(aov)

    # =========================================================================

    def _createGroups(self, definitions):
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

    # =========================================================================
    # METHODS
    # =========================================================================

    def addAOV(self, aov):
        """Add an AOV for writing."""
        self.aovs.append(aov)

    # =========================================================================

    def addGroup(self, group):
        """Add An AOVGroup for writing."""
        self.groups.append(group)

    # =========================================================================

    def containsAOV(self, aov):
        """Check if this file contains an AOV with the same variable name."""
        return aov in self.aovs

    # =========================================================================

    def containsGroup(self, group):
        """Check if this file contains a group with the same name."""
        return group in self.groups

    # =========================================================================

    def removeAOV(self, aov):
        """Remove an AOV from the file."""
        idx = self.aovs.index(aov)

        del self.aovs[idx]

    # =========================================================================

    def removeGroup(self, group):
        """Remove a group from the file."""
        idx = self.groups.index(group)

        del self.groups[idx]

    # =========================================================================

    def replaceAOV(self, aov):
        """Replace an AOV in the file."""
        idx = self.aovs.index(aov)

        self.aovs[idx] = aov

    # =========================================================================

    def replaceGroup(self, group):
        """Replace a group in the file."""
        idx = self.groups.index(group)

        self.groups[idx] = group

    # =========================================================================

    def writeToFile(self, path=None):
        """Write data to file."""
        data = {}

        for group in self.groups:
            groups = data.setdefault("groups", {})

            groups.update(group.getData())

        for aov in self.aovs:
            aovs = data.setdefault("definitions", [])

            aovs.append(aov.getData())

        if path is None:
            path = self.path

        with open(path, 'w') as handle:
            json.dump(data, handle, indent=4)

# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

def _findAOVFiles():
    """Find any .json files that should be read."""
    # Look for the specific AOV search path.
    if "HT_AOV_PATH" in os.environ:
        # Get the search path.
        search_path = os.environ["HT_AOV_PATH"]

        # If '&' is in the path then following Houdini path conventions we'll
        # search through the HOUDINI_PATH as well.
        if '&' in search_path:
            # Find any config/aovs folders in HOUDINI_PATH.
            hpath_dirs = _findHoudiniPathAOVFolders()

            # If there are any then we replace the '&' with those paths.
            if hpath_dirs:
                search_path = search_path.replace('&', ':'.join(hpath_dirs))

        directories = search_path.split(":")

    else:
        directories = _findHoudiniPathAOVFolders()

    all_files = []

    for directory in directories:
        all_files.extend(glob.glob(os.path.join(directory, "*.json")))

    return all_files


def _findHoudiniPathAOVFolders():
    """Look for any config/aovs folders in the HOUDINI_PATH."""
    # Try to find HOUDINI_PATH directories.
    try:
        directories = hou.findDirectories("config/aovs")

    except hou.OperationFailed:
        directories = ()

    return directories

# =============================================================================
# FUNCTIONS
# =============================================================================

def buildMenuScript():
    """Build a menu script for choosing AOVs and groups."""
    manager = findOrCreateSessionAOVManager()

    menu = []

    if manager.groups:
        for group in sorted(manager.groups.keys()):
            menu.extend(["@{0}".format(group), group])

        menu.extend(["_separator_", "---------"])

    for aov in sorted(manager.aovs):
        menu.extend([aov, aov])

    return menu


def createSessionAOVManager():
    """Create an AOVManager stored in hou.session."""
    manager = AOVManager()
    hou.session.aov_manager = manager

    return manager


def findOrCreateSessionAOVManager(rebuild=False):
    """Find or create an AOVManager from hou.session."""
    manager = None

    if hasattr(hou.session, "aov_manager") and not rebuild:
        manager = hou.session.aov_manager

    else:
        manager = createSessionAOVManager()

    return manager


def loadJsonFiles():
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
# GLOBALS
# =============================================================================

MANAGER = findOrCreateSessionAOVManager(rebuild=True)

