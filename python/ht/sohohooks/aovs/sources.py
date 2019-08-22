"""This module contains classes and functions for high level interaction
with AOVs.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import abc
import json
import os

# Houdini-Toolbox Imports
from ht.sohohooks.aovs.aov import AOV, AOVGroup, GroupBasedAOV
from ht.sohohooks.aovs import constants as consts

# Houdini Imports
import hou


# =============================================================================
# CLASSES
# =============================================================================

class AOVSourceManager(object):
    """Manager class for aov sources."""

    def __init__(self):
        self._file_sources = {}
        self._group_sources = {}
        self._asset_section_sources = {}
        self._hip_source = AOVHipSource()
        self._unsaved_source = AOVUnsavedSource()

    @property
    def asset_section_sources(self):
        return self._asset_section_sources

    def get_file_source(self, file_path):
        """Get the source representing a file on disk."""
        # Check to see if we already have it.
        if file_path in self._file_sources:
            return self._file_sources[file_path]

        # Create and store a reference to the source.
        source = AOVFileSource(file_path)
        self._file_sources[file_path] = source

        return source

    def get_group_source(self, group):
        """Get the source representing a group."""
        # Check to see if we already have it.
        if group in self._group_sources:
            return self._group_sources[group]

        # Create and store a reference to the source.
        source = AOVGroupSource(group)
        self._group_sources[group] = source

        return source

    def get_asset_section_source(self, section):
        """Get the source representing a digital asset section."""
        # Check to see if we already have it.
        if section in self.asset_section_sources:
            return self.asset_section_sources[section]

        # Create and store a reference to the source
        source = AOVAssetSectionSource(section)
        self.asset_section_sources[section] = source

        return source

    @property
    def file_sources(self):
        return self._file_sources

    @property
    def group_sources(self):
        return self._group_sources

    @property
    def hip_source(self):
        """Get the source representing the hip file."""
        return self._hip_source

    @property
    def unsaved_source(self):
        """Get the source representing unsaved items."""
        return self._unsaved_source

    def remove_source(self, source):
        if isinstance(source, AOVHipSource):
            pass

        elif isinstance(source, AOVUnsavedSource):
            pass

        elif isinstance(source, AOVAssetSectionSource):
            del self.asset_section_sources[source.section]

        elif isinstance(source, AOVGroupSource):
            del self._group_sources[source.group]

        elif isinstance(source, AOVFileSource):
            del self._file_sources[source.path]


class BaseAOVSource(object):
    """The base class for AOV sources."""
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self._aovs = []
        self._data = {}
        self._groups = []

        self._read_only = False

        if self.exists:
            self._init_from_source()

    def __repr__(self):
        return "<{} {}>".format(
            self.__class__.__name__,
            self.name
        )

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _init_from_source(self):
        """Read data from the source and create the appropriate entities."""
        data = self._load_data()

        if consts.FILE_DEFINITIONS_KEY in data:
            self._create_aovs(data[consts.FILE_DEFINITIONS_KEY])

        if consts.FILE_GROUPS_KEY in data:
            self._create_groups(data[consts.FILE_GROUPS_KEY])

    # =========================================================================

    def _create_aovs(self, definitions):
        """Create AOVs based on definitions."""
        for definition in definitions:
            # Insert this file path into the data.
            definition[consts.SOURCE_KEY] = self

            # Construct a new AOV and add it to our list.
            aov = AOV(definition)
            self.aovs.append(aov)

    # =========================================================================

    def _create_groups(self, definitions):
        """Create AOVGroups based on definitions."""
        for name, group_data in definitions.items():
            # A list of AOV definitions contained inside the group.
            definitions = []

            # If there are definitions then we need to remove them from the
            # group's data.
            if consts.GROUP_DEFINITIONS_KEY in group_data:
                definitions = group_data.pop(consts.GROUP_DEFINITIONS_KEY)

            # Create the new group.
            group_data[consts.GROUP_NAME_KEY] = name
            group = AOVGroup(group_data)

            # Set the source as this object.
            group.source = self

            # Add the group to the list.
            self.groups.append(group)

            if definitions:
                group_source = AOVGroupSource(group)

                # Construct new group AOV definitions and add them to the
                # source/group.
                for definition_data in definitions:
                    definition_data[consts.SOURCE_KEY] = group_source
                    aov = GroupBasedAOV(definition_data, group)
                    group.aovs.append(aov)

    def _get_data(self):
        """The method will serialize the source into json data for writing."""
        data = {}

        if self.groups:
            group_definitions = data.setdefault(consts.FILE_GROUPS_KEY, {})

            for group in self.groups:
                group_definitions.update(group.getData())

        if self.aovs:
            definitions = data.setdefault(consts.FILE_DEFINITIONS_KEY, [])

            for aov in self.aovs:
                definitions.append(aov.getData())

        return data

    @abc.abstractmethod
    def _load_data(self):
        """Method to load data from the source."""
        pass

    @abc.abstractmethod
    def write(self):
        """Method to write the source."""
        pass

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def aovs(self):
        """List containing AOVs defined in this source."""
        return self._aovs

    # =========================================================================

    @property
    def groups(self):
        """List containing AOVGroups defined in this source."""
        return self._groups

    # =========================================================================

    @abc.abstractproperty
    def name(self):
        """The name of the source."""
        pass

    @abc.abstractproperty
    def exists(self):
        """Determine if the source actually exists."""
        pass

    @abc.abstractproperty
    def read_only(self):
        """Determine if the source is read only."""
        pass

    @abc.abstractproperty
    def path(self):
        """A representative path to where the source is."""
        pass

    # =========================================================================
    # METHODS
    # =========================================================================

    def add_aov(self, aov):
        """Add an AOV so the source."""
        self.aovs.append(aov)

        aov.source = self

    def add_group(self, group):
        """Add a group to the source."""
        self.groups.append(group)

        group.source = self

    # TODO: Is this a good idea?
    def can_create_source(self):
        return NotImplemented

    def clear(self):
        self._aovs = []
        self._data.clear()
        self._groups = []

    def contains_aov(self, aov):
        """Check if this source contains an AOV."""
        return aov in self.aovs

    def contains_group(self, group):
        """Check if this source contains a group."""
        return group in self.groups

    def delete_aov(self, aov):
        """Remove and delete an AOV from the source."""
        idx = self.aovs.index(aov)

        del self.aovs[idx]

    def delete_group(self, group):
        """Remove and delete a group from the source."""
        idx = self.groups.index(group)

        del self.groups[idx]

    def remove_aov(self, aov):
        """Remove an AOV from the source."""
        self.aovs.remove(aov)

    def remove_group(self, group):
        """Remove a group from the source."""
        self.groups.remove(group)

    def replace_aov(self, aov):
        """Replace an AOV in the source"""
        idx = self.aovs.index(aov)

        self.aovs[idx] = aov

    def replace_group(self, group):
        """Replace a group in the source."""
        idx = self.groups.index(group)

        self.groups[idx] = group

    def transfer_aov_ownership(self, aov, new_owner, write=True):
        """Transfer an AOV from this source to another source."""
        # Remove the AOV from our self and add it to the new owner.
        self.remove_aov(aov)
        new_owner.add_aov(aov)

        # Write the changes to the sources.
        if write:
            new_owner.write()

            self.write()

    def transfer_group_ownership(self, group, new_owner, write=True):
        """Transfer a group from this source to another source."""
        # Remove the group from our self and add it to the new owner.
        self.remove_group(group)
        new_owner.add_group(group)

        # Write the changes to the sources.
        if write:
            new_owner.write()

            self.write()


class AOVAssetSectionSource(BaseAOVSource):
    """This class represents AOVs and groups stored in Digital Asset sections."""

    # The name of the digital asset section definitions will be stored in.
    SECTION_NAME = "aovs.json"

    def __init__(self, section):
        # Store information about the operator type.  We do this so we don't have
        # to store an actual reference to the hou.HDASection object which can cause
        # problems. We do this before the superclass __init__ so that the requisite
        # data will be available on initialization.
        self._path = section.definition().libraryFilePath()
        self._category = section.definition().nodeType().category().name()
        self._type_name = section.definition().nodeType().name()

        super(AOVAssetSectionSource, self).__init__()

        # Build an opdef: style display name for our section.
        self._name = AOVAssetSectionSource.build_name(section)

    def _load_data(self):
        """Load the data from the section."""
        results = self.section.contents()

        return json.loads(results)

    @staticmethod
    def build_name(section):
        """Build a display name from the section."""
        return "opdef:{}?{}".format(
            section.definition().nodeType().nameWithCategory(),
            section.name()
        )

    @property
    def name(self):
        """The name of the source."""
        return self._name

    @property
    def path(self):
        """The path to the source otl file."""
        return self._path

    @property
    def read_only(self):
        """Check if the otl file is ready only."""
        # If the definition is embedded in the hip file then we can always
        # modify it.
        if self.path == "Embedded":
            return False

        # Check the write permissions of the file on disk.
        return not os.access(self.path, os.W_OK)

    @property
    def exists(self):
        """Check if the operator type definition and section actually exist."""
        return self.section is not None

    @property
    def section(self):
        """Get the representative hou.HDASection for the source."""
        category = hou.nodeTypeCategories()[self._category]
        definition = hou.hdaDefinition(category, self._type_name, self._path)
        return definition.sections()[self.SECTION_NAME]

    @staticmethod
    def create_section_from_node(node):
        """Initialize a new hou.HDASection for a given digital asset."""
        definition = node.type().definition()

        # Add a new section with empty json data.
        section = definition.addSection(AOVAssetSectionSource.SECTION_NAME, json.dumps({}))

        return section

    @staticmethod
    def get_aov_section(node):
        """Get the hou.HDASection representing AOV storage from a node."""
        return node.type().definition().sections()[AOVAssetSectionSource.SECTION_NAME]

    @staticmethod
    def has_aov_section(node):
        """Check to see if a node contains embedded AOV definitions."""
        definition = node.type().definition()
        return AOVAssetSectionSource.SECTION_NAME in definition.sections().keys()

    # def can_create_source(self):
    #     dir_path = os.path.dirname(self.path)
    #
    #     return os.access(dir_path, os.W_OK)

    def write(self):
        """Write data to the source section."""
        data = self._get_data()

        self.section.setContents(json.dumps(data, indent=4))


class AOVFileSource(BaseAOVSource):
    """Class to handle reading and writing AOV .json files."""

    def __init__(self, path):
        self._path = path

        super(AOVFileSource, self).__init__()

    def _load_data(self):
        """Load the data from the source file."""
        with open(self.path) as handle:
            data = json.load(handle)

            return data

    @property
    def exists(self):
        """Check if the source file exists."""
        return os.path.isfile(self.path)

    @property
    def name(self):
        """The name of the source."""
        return self.path

    @property
    def read_only(self):
        """Check if the json file is ready only."""
        return not os.access(self.path, os.W_OK)

    @property
    def path(self):
        """The path to the source file."""
        return self._path

    def can_create_source(self):
        dir_path = os.path.dirname(self.path)

        return os.access(dir_path, os.W_OK)

    def write(self, path=None):  # pylint: disable=parameters-differ
        """Write the data to file."""
        data = self._get_data()

        if path is None:
            path = self.path

        with open(path, 'w') as handle:
            json.dump(data, handle, indent=4)


class AOVHipSource(BaseAOVSource):
    """This class represents AOVs and groups stored in the current hip file."""

    USER_DATA_NAME = "aovs.json"

    @property
    def name(self):
        """The name of the source."""
        return "HipFile"

    @property
    def path(self):
        """THe path to the hip file."""
        return hou.hipFile.path()

    @property
    def read_only(self):
        """Check if the source is read only."""
        return False

    @property
    def exists(self):
        """Ensure the root node exists."""
        return self.root is not None

    def _load_data(self):
        """Load the data from the root node's user data dictionary."""
        user_data = self.root.userData(self.USER_DATA_NAME)

        if user_data is not None:
            return json.loads(user_data)

        return {}

    @property
    def root(self):
        """The root Houdini node ('/') where hip file definitions are stored."""
        return hou.node("/")

    def reload(self):
        """Reload the source."""
        self._init_from_source()

    def write(self): #, save_hip=True):
        """Write data to the hip file."""
        data = self._get_data()

        self.root.setUserData(self.USER_DATA_NAME, json.dumps(data, indent=4))

        # TODO: Should we save the file?  If so, we need to adjust the read_only check.
        # Save the hip file to seal the changes.
        # if save_hip:
        #    hou.hipFile.save()


class AOVUnsavedSource(BaseAOVSource):
    """This class represents AOVs and groups stored in the current Houdini session.

    Unless items in this source are moved to another source they will be destroyed
    when that session quits.

    """

    @property
    def name(self):
        """The name of the source."""
        return "Unsaved"

    @property
    def path(self):
        """The path to the source."""
        return "unsaved"

    @property
    def read_only(self):
        """It is always possible to write to Unsaved."""
        return False

    @property
    def exists(self):
        """This source always exists."""
        return True

    def _load_data(self):
        """This is a noop as there is never any data to load."""
        return {}

    def clear(self):
        self._init_from_source()

    def write(self):
        """This is a noop as there is never any place to write to."""
        pass


# TODO: Need to implement the add/remove/delete/etc methods on this source so that
# they modify the underlying group's source? Maybe, but probably not?
class AOVGroupSource(BaseAOVSource):
    """This class represents AOVs store inside a group."""

    def __init__(self, group):
        self._group = group

        super(AOVGroupSource, self).__init__()

    def _load_data(self):
        return {}

    @property
    def exists(self):
        """Check if the source group's source exists."""
        return self.group.source.exists

    @property
    def read_only(self):
        """Check if the source group's source is read only."""
        return self.group.source.read_only

    @property
    def name(self):
        """The name of the section."""
        return "Group: {}".format(self.group.name)

    @property
    def group(self):
        """The containing group"""
        return self._group

    @property
    def path(self):
        """The path to the source."""
        return "Group: {}".format(self.group.name)

    def write(self):
        """Write data to the source.

        This will cause the source group's source to be written.

        """
        self.group.source.write()
