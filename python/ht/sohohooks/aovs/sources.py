
import json
import os

from ht.sohohooks.aovs.aov import AOV, AOVGroup, GroupBasedAOV

import hou



class AOVSourceManager(object):
    """Manager class for aov sources."""

    def __init__(self):
        self._file_sources = {}
        self._group_sources = {}
        self._otl_sources = {}

    def getFileSource(self, filepath):
        if filepath in self._file_sources:
 #           print "cached ", filepath
            return self._file_sources[filepath]

        source = AOVFileSource(filepath)
        self._file_sources[filepath] = source

#        print "get source", source, source.groups

        return source

    def getGroupSource(self, group):
        if group in self._group_sources:
            return self._group_sources[group]

        source = AOVGroupSource(group)
        return source

    def getAssetSectionSource(self, section):
        if section in self._otl_sources:
            return self._otl_sources[section]

        source = AOVAssetSection(section)
        self._otl_sources[section] = source

        return source


class BaseAOVSource(object):

    def __init__(self, path):
        self._path = path

        self._aovs = []
        self._data = {}
        self._groups = []

        self._read_only = False

        if self.exists:
            self._initFromSource()

    def __repr__(self):
        return "<{} {}>".format(
            self.__class__.__name__,
            self.path
        )

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _initFromSource(self):
        """Read data from the file and create the appropriate entities."""
        data = self._loadData()

        if "definitions" in data:
            self._createAOVs(data["definitions"])

        if "groups" in data:
            self._createGroups(data["groups"])

    # =========================================================================

    def _createAOVs(self, definitions):
        """Create AOVs based on definitions."""
        for definition in definitions:
            # Insert this file path into the data.
            definition["source"] = self

            # Construct a new AOV and add it to our list.
            aov = AOV(definition)
            self.aovs.append(aov)

    # =========================================================================

    def _createGroups(self, definitions):
        """Create AOVGroups based on definitions."""
        for name, group_data in definitions.iteritems():
            # Create a new AOVGroup.

            definitions = []

            if "definitions" in group_data:
                definitions = group_data.pop("definitions")

            group_data["name"] = name
            group = AOVGroup(group_data)

            # Set the path to this file.
            group.source = self

            # Add the group to the list.
            self.groups.append(group)

            if definitions:
            #if "definitions" in group_data:
                group_source = AOVGroupSource(group)

             #   for definition_data in group_data["definitions"]:
                for definition_data in definitions:
                    definition_data["source"] = group_source
                    aov = GroupBasedAOV(definition_data, group)
                    group.aovs.append(aov)


    def _getData(self):
        data = {}

        if self.groups:
            group_definitions = data.setdefault("groups", {})

            for group in self.groups:
                group_definitions.update(group.getData())

        if self.aovs:
            definitions = data.setdefault("definitions", [])

            for aov in self.aovs:
                definitions.append(aov.getData())

        return data

    def _loadData(self):
        pass

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

    @property
    def read_only(self):
        return self._read_only

    # =========================================================================
    # METHODS
    # =========================================================================

    def addAOV(self, aov):
        """Add an AOV for writing."""
        self.aovs.append(aov)

    def addGroup(self, group):
        """Add An AOVGroup for writing."""
        self.groups.append(group)

    def containsAOV(self, aov):
        """Check if this file contains an AOV with the same variable name."""
        return aov in self.aovs

    def containsGroup(self, group):
        """Check if this file contains a group with the same name."""
        return group in self.groups

    def removeAOV(self, aov):
        """Remove an AOV from the file."""
        idx = self.aovs.index(aov)

        del self.aovs[idx]

    def removeGroup(self, group):
        """Remove a group from the file."""
        idx = self.groups.index(group)

        del self.groups[idx]

    def replaceAOV(self, aov):
        """Replace an AOV in the file."""
        idx = self.aovs.index(aov)

        self.aovs[idx] = aov

    def replaceGroup(self, group):
        """Replace a group in the file."""
        idx = self.groups.index(group)

        self.groups[idx] = group


class AOVAssetSection(BaseAOVSource):

    def __init__(self, section):
        path = self.buildPath(section)

        self._section = section

        super(AOVAssetSection, self).__init__(path)

        definition_path = section.definition().libraryFilePath()

        if definition_path == "Embedded":
            self._read_only = False

        else:
            self._read_only = not os.access(definition_path, os.W_OK)

    def _loadData(self):
        results = self.section.contents()

        return json.loads(results)

    @staticmethod
    def buildPath(section):
        return "opdef:{}?{}".format(
            section.definition().nodeType().nameWithCategory(),
            section.name()
        )

    @property
    def exists(self):
        """Check if the operator type definition and section actually exist."""
        return self.section is not None

    @property
    def section(self):
        return self._section

    def write(self):
        """Write data to the source section."""
        data = self._getData()

        self.section.setContents(json.dumps(data, indent=4))


class AOVFileSource(BaseAOVSource):
    """Class to handle reading and writing AOV .json files."""

    def __init__(self, path):
        super(AOVFileSource, self).__init__(path)

        self._read_only = not os.access(path, os.W_OK)

    # =========================================================================
    # METHODS
    # =========================================================================

    def _loadData(self):
        with open(self.path) as handle:
            data = json.load(handle)

            return data

    def write(self, path=None):
        """Write the data to file."""
        data = self._getData()

        if path is None:
            path = self.path

        with open(path, 'w') as handle:
            json.dump(data, handle, indent=4)


class AOVGroupSource(BaseAOVSource):

    def __init__(self, group):

        path = "Group: {}".format(group.name)

        super(AOVGroupSource, self).__init__(path)

        self._group = group


    @property
    def group(self):
        return self._group
