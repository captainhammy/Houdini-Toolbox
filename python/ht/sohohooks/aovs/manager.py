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
from ht.sohohooks.aovs.aov import AOV, AOVGroup
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
        return "<AOVManager>"

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def interface(self):
        """Any AOVViewerInterface assigned to the manager."""
        return self._interface

    @property
    def aovs(self):
        """Dicionary containing all available AOVs."""
        return self._aovs

    @property
    def groups(self):
        """Dictionary containing all available AOVGroups."""
        return self._groups

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _initFromFiles(self):
        """Intialize the manager from files on disk."""
        file_paths = _findAOVFiles()

        readers = [AOVFileReader(file_path) for file_path in file_paths]

        self._mergeReaders(readers)

    def _initGroupMembers(self, group):
        """Populate the AOV lists of each group based on available AOVs."""
        # Process each of the group's includes.
        for include in group.includes:
            # If the AOV name is available, add it to the group.
            if include in self.aovs:
                group.aovs.append(self.aovs[include])

    def _mergeReaders(self, readers):
        """Merge the data of multiple AOVFileReader objects."""
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
    # METHODS
    # =========================================================================

    def addAOV(self, aov):
        """Add an AOV to the manager."""
        self._aovs[aov.variable] = aov

        if self.interface is not None:
            self.interface.aovAddedSignal.emit(aov)

    @staticmethod
    def addAOVsToIfd(wrangler, cam, now):
        """Add auto_aovs to the ifd."""
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

    def addGroup(self, group):
        """Add an AOVGroup to the manager."""
        self.groups[group.name] = group

        if self.interface is not None:
            self.interface.groupAddedSignal.emit(group)

    def clear(self):
        """Clear all definitions."""
        self._aovs = {}
        self._groups = {}

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

    def initInterface(self):
        """Initialize an AOVViewerInterface for this manager."""
        from ht.ui.aovs.utils import AOVViewerInterface
        self._interface = AOVViewerInterface()

    def load(self, path):
        """Load a file."""
        readers = [AOVFileReader(path)]

        self._mergeReaders(readers)

    def reload(self):
        """Reload all definitions."""
        self.clear()
        self._initFromFiles()

    def removeAOV(self, aov):
        """Remove the specified AOV from the manager."""
        if aov.variable in self._aovs:
            self._aovs.pop(aov.variable)

            if self.interface is not None:
                self.interface.aovRemovedSignal.emit(aov)


class AOVFileReader(object):
    """This class handles reading AOVs and AOVGroups from files."""

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, path):
        self._aovs = []
        self._groups = []
        self._path = path

        self.readFromFile()

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
        """Path of the file being read."""
        return self._path

    # =========================================================================
    # METHODS
    # =========================================================================

    def createAOVs(self, definitions):
        """Create AOVs based on definitions."""
        for definition in definitions:
            # Insert this file path into the data.
            definition["path"] = self.path

            # Construct a new AOV and add it to our list.
            aov = AOV(definition)
            self.aovs.append(aov)

    def createGroups(self, definitions):
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

    def readFromFile(self):
        """Read data from the file and create the appropriate entities."""
        with open(self.path) as fp:
            data = json.load(fp, object_hook=convertFromUnicode)

        if "definitions" in data:
            self.createAOVs(data["definitions"])

        if "groups" in data:
            self.createGroups(data["groups"])


class AOVFileWriter(object):
    """This class handles writing AOVs and AOVGroups to a file."""

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self):
        self._data = {}

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def data(self):
        """Data dictionary to be written to .json file."""
        return self._data

    # =========================================================================
    # METHODS
    # =========================================================================

    def addAOV(self, aov):
        """Add an AOV for writing."""
        definitions = self.data.setdefault("definitions", [])

        definitions.append(aov.data())

    def addGroup(self, group):
        """Add An AOVGroup for writing."""
        groups = self.data.setdefault("groups", {})

        groups.update(group.data())

    def writeToFile(self, path):
        """Write added data to file."""
        if os.path.exists(path):
            with open(path, 'r') as fp:
                file_data = json.load(fp, object_hook=convertFromUnicode)

                if "groups" in self.data:
                    groups = file_data.setdefault("groups", {})

                    for name, group_data in self.data["groups"].iteritems():
                        groups[name] = group_data

                if "definitions" in self.data:
                    definitions = file_data.setdefault("definitions", [])

                    for definition in self.data["definitions"]:
                        definitions.append(definition)

            with open(path, 'w') as fp:
                json.dump(file_data, fp, indent=4)

        else:
            with open(path, 'w') as fp:
                json.dump(self.data, fp, indent=4)

# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

# TODO: Use a custom scan path if available?
def _findAOVFiles():
    """Find any .json files that should be read."""

    try:
        directories = hou.findDirectories("config/aovs")

    except hou.OperationFailed:
        directories = []

    all_files = []

    for directory in directories:
        all_files.extend(glob.glob(os.path.join(directory, "*.json")))

    return all_files


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

