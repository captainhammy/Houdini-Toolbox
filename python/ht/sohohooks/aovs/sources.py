
import abc

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
        self._hip_source = None
        self._unsaved_source = None

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

    def getHipSource(self):
        if self._hip_source is None:
            self._hip_source = AOVHipSource()

        return self._hip_source

    def getUnsavedSource(self):
        if self._unsaved_source is None:
            self._unsaved_source = AOVUnsavedSource()

        return self._unsaved_source


class BaseAOVSource(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self._aovs = []
        self._data = {}
        self._groups = []

        self._read_only = False

        if self.exists:
            self._initFromSource()

    def __repr__(self):
        return "<{} {}>".format(
            self.__class__.__name__,
            self.name
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
                group_source = AOVGroupSource(group)

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

    @abc.abstractmethod
    def _loadData(self):
        pass

    @abc.abstractmethod
    def write(self):
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

    @abc.abstractproperty
    def name(self):
        pass

    @abc.abstractproperty
    def exists(self):
        """Check if the file actually exists."""
        pass

    @abc.abstractproperty
    def read_only(self):
        pass

    @abc.abstractproperty
    def path(self):
        pass

    # =========================================================================
    # METHODS
    # =========================================================================

    def addAOV(self, aov):
        """Add an AOV for writing."""
        self.aovs.append(aov)

        aov.source = self

    def addGroup(self, group):
        """Add An AOVGroup for writing."""
        self.groups.append(group)

        group.source = self

    def containsAOV(self, aov):
        """Check if this file contains an AOV with the same variable name."""
        return aov in self.aovs

    def containsGroup(self, group):
        """Check if this file contains a group with the same name."""
        return group in self.groups

    def deleteAOV(self, aov):
        """Remove and delete an AOV from the file."""
        idx = self.aovs.index(aov)

        del self.aovs[idx]


    def deleteGroup(self, group):
        """Remove and delete a group from the file."""
        idx = self.groups.index(group)

        del self.groups[idx]

    def removeAOV(self, aov):
        self.aovs.remove(aov)

    def removeGroup(self, group):
        self.groups.remove(group)

    def replaceAOV(self, aov):
        """Replace an AOV in the file."""
        idx = self.aovs.index(aov)

        self.aovs[idx] = aov

    def replaceGroup(self, group):
        """Replace a group in the file."""
        idx = self.groups.index(group)

        self.groups[idx] = group

    def transferAOVOwnership(self, aov, new_owner, write=True):
        self.removeAOV(aov)

        new_owner.addAOV(aov)

        if write:
            new_owner.write()

            self.write()

    def transferGroupOwnership(self, group, new_owner, write=True):
        self.removeGroup(group)

        new_owner.addGroup(group)

        if write:
            new_owner.write()

            self.write()


class AOVAssetSection(BaseAOVSource):

    def __init__(self, section):
        self._path = section.definition().libraryFilePath()
        self._category = section.definition().nodeType().category().name()
        self._type_name = section.definition().nodeType().name()

        super(AOVAssetSection, self).__init__()

        self._name = AOVAssetSection.buildName(section)

    def _loadData(self):
        results = self.section.contents()

        return json.loads(results)

    @staticmethod
    def buildName(section):
        return "opdef:{}?{}".format(
            section.definition().nodeType().nameWithCategory(),
            section.name()
        )

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    @property
    def read_only(self):
        if self.path == "Embedded":
            return False

        else:
            return not os.access(self.path, os.W_OK)

    @property
    def exists(self):
        """Check if the operator type definition and section actually exist."""
        return self.section is not None

    @property
    def section(self):
        category = hou.nodeTypeCategories()[self._category]
        definition = hou.hdaDefinition(category, self._type_name, self._path)
        return definition.sections()["aovs.json"]

    @staticmethod
    def createSectionFromNode(node):
        definition = node.type().definition()
        section = definition.addSection("aovs.json", json.dumps({}))
        return section

    @staticmethod
    def getAOVSection(node):
        return node.type().definition().sections()["aovs.json"]

    @staticmethod
    def hasAOVSection(node):
        definition = node.type().definition()
        return "aovs.json" in definition.sections().keys()

    def write(self):
        """Write data to the source section."""
        data = self._getData()

        self.section.setContents(json.dumps(data, indent=4))


class AOVFileSource(BaseAOVSource):
    """Class to handle reading and writing AOV .json files."""

    def __init__(self, path):
        self._path = path

        super(AOVFileSource, self).__init__()

    def _loadData(self):
        with open(self.path) as handle:
            data = json.load(handle)

            return data

    @property
    def exists(self):
        return os.path.isfile(self.path)

    @property
    def name(self):
        return self.path

    @property
    def read_only(self):
        return not os.access(self.path, os.W_OK)

    @property
    def path(self):
        return self._path

    def write(self, path=None):
        """Write the data to file."""
        data = self._getData()

        if path is None:
            path = self.path

        with open(path, 'w') as handle:
            json.dump(data, handle, indent=4)


class AOVHipSource(BaseAOVSource):

    def __init__(self):
        super(AOVHipSource, self).__init__()

    @property
    def name(self):
        return "HipFile"

    @property
    def path(self):
        return hou.hipFile.path()

    @property
    def read_only(self):
        return False

    @property
    def exists(self):
        return self.root is not None

    def _loadData(self):
        user_data = self.root.userData("aovs.json")

        if user_data is not None:
            return json.loads(user_data)

        return None

    @property
    def root(self):
        return hou.node("/")

    def write(self):
        """Write data to the source section."""
        data = self._getData()

        self.node.setUserData("aovs.json", json.dumps(data, indent=4))


class AOVUnsavedSource(BaseAOVSource):

    def __init__(self):
        super(AOVUnsavedSource, self).__init__()

    @property
    def name(self):
        return "Unsaved"

    @property
    def path(self):
        return "unsaved"

    @property
    def read_only(self):
        return False

    @property
    def exists(self):
        return True

    def _loadData(self):
        return None

    def write(self):
        pass


class AOVGroupSource(BaseAOVSource):

    def __init__(self, group):
        self._group = group

        super(AOVGroupSource, self).__init__()

        self._read_only = group.source.read_only

    def _loadData(self):
        return {}

    @property
    def exists(self):
        return self.group.source.exists

    @property
    def read_only(self):
        return self._read_only

    @property
    def name(self):
        return "Group: {}".format(self.group.name)

    @property
    def group(self):
        return self._group

    @property
    def path(self):
        return "Group: {}".format(self.group.name)

    def write(self):
        """Write data to the source section."""
        self.group.source.write()

