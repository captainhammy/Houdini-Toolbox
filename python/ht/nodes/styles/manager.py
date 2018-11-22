"""This module contains a class and functions for managing and applying node
colors in Houdini.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import glob
import json
import os

# Houdini Toolbox Imports
from ht.nodes.styles.styles import StyleConstant, StyleEntry, ConstantEntry

# Houdini Imports
import hou

# =============================================================================
# CLASSES
# =============================================================================

class StyleManager(object):
    """Manage and apply Houdini node styles.

    """

    def __init__(self):
        self._constants = {}
        self._names = {}
        self._nodes = {}
        self._tools = {}

        # Build mappings for this object.
        self._buildMappings()

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __repr__(self):
        return "<StyleManager>"

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _buildConstantsFromData(self, all_data):
        for data in all_data:
            path = data["path"]

            # Process any constants first so they can be used by assignments.
            if "constants" in data:
                for name, entry in data["constants"].iteritems():
                    # Get the color from the info.

                    color, color_type = _buildColor(entry)
                    shape = _buildShape(entry)

                    # Store the constant under its name.
                    self.constants[name] = StyleConstant(
                        name,
                        color,
                        color_type,
                        shape,
                        path
                    )

    def _buildEntriesFromData(self, all_data):
        for data in all_data:
            path = data["path"]

            # Process each of the different types of color assignments.
            for assign_type in ("names", "nodes", "tools"):
                # Ensure the type exists in the data.
                if assign_type not in data:
                    continue

                # Get the mapping dictionary from the manager.
                color_type_map = getattr(self, assign_type)

                # Process each category in the data.
                for category_name, entries in data[assign_type].iteritems():
                    # Get a mapping list for the category name.
                    category_list = color_type_map.setdefault(
                        category_name,
                        {}
                    )

                    # Process each entry.  The entry name can be a node
                    # type name, Tab menu folder name, or manager/generator.
                    for entry in entries:
                        # Get the entry name.
                        entry_name = entry["name"]

                        if "constant" in entry:
                            constant_name = entry["constant"]

                            # Ensure the constant exists.  If not, raise an
                            # exception.
                            if constant_name not in self.constants:
                                raise ConstantDoesNotExistError(constant_name)

                            # Add a ConstantEntry to the list.
                            category_list[entry_name] = ConstantEntry(
                                entry_name,
                                constant_name,
                                path
                            )

                            continue

                        # Build the color from the raw data.
                        color, color_type = _buildColor(entry)

                        shape = _buildShape(entry)

                        # Add a ColorEntry to the list.
                        category_list[entry_name] = StyleEntry(
                            entry_name,
                            color,
                            color_type,
                            shape,
                            path
                        )

    def _buildMappings(self):
        """Build mappings from files."""
        files = _findFiles()

        all_data = []

        # Read all the target files in reverse.
        for path in reversed(files):
            # Open the target file.
            with open(path) as handle:
                # Load the json data and convert the data from unicde.
                data = json.load(handle)

            data["path"] = path
            all_data.append(data)

        self._buildConstantsFromData(all_data)

        self._buildEntriesFromData(all_data)

    def _getManagerGeneratorStyle(self, node_type):
        """Look for a color match based on the node type being a manager or
        generator type.

        """
        categories = (node_type.category().name(), "all")

        for category_name in categories:
            # Check if the category has any entries.
            if category_name in self.nodes:
                category_entries = self.nodes[category_name]

                # The node type is a manager.
                if node_type.isManager():
                    # Check for a manager entry under the category.
                    if "manager" in category_entries:
                        return self._resolveEntry(category_entries["manager"])

                # The node type is a generator.
                elif node_type.isGenerator():
                    # Check for a generator entry under the category.
                    if "generator" in category_entries:
                        return self._resolveEntry(category_entries["generator"])

        return None

    def _getNameEntry(self, node):
        """Look for a color match based on the node name."""
        # The node name.
        name = node.name()

        categories = (node.type().category().name(), "all")

        for category_name in categories:
            # Check for entries for the node type category.
            if category_name in self.names:
                # Check if the name matches any of the category entries.
                for color_entry in self.names[category_name].itervalues():
                    if hou.patternMatch(color_entry.name, name):
                        return self._resolveEntry(color_entry)

        return None

    def _getToolStyle(self, node_type):
        """Look for a color match based on the node type's Tab menu
        locations.

        """
        categories = (node_type.category().name(), "all")

        for category_name in categories:
            # Check for entries for the node type category.
            if category_name in self.tools:
                # Get any Tab menu locations the node type might show up in.
                menu_locations = _getToolMenuLocations(node_type)

                # Process the locations, looking for the first match.
                for location in menu_locations:
                    # Check if the node name is in the mapping.

                    # Check if the location matches any of the category entries.
                    for color_entry in self.tools[category_name].itervalues():
                        if hou.patternMatch(color_entry.name, location):
                            return self._resolveEntry(color_entry)

        return None

    def _getTypeStyle(self, node_type):
        """Look for a color match based on the node type's name."""
        type_name = node_type.nameComponents()[2]

        # Get the category name from the node and also check the 'all'
        # category.
        categories = (node_type.category().name(), "all")

        for category_name in categories:
            # Check if the category has any entries.
            if category_name in self.nodes:
                # Check if the node type name matches any of the category
                # entries.
                for style_entry in self.nodes[category_name].itervalues():
                    if hou.patternMatch(style_entry.name, type_name):
                        return self._resolveEntry(style_entry)

        return None

    def _resolveEntry(self, entry):
        """Resolve the entry to a color.

        The entry might a color or a constant so this will return the actual
        color.

        """
        # If the entry object is a ColorEntry then we can just return the
        # color.
        if isinstance(entry, StyleEntry):
            return entry

        # Otherwise it is a ConstantEntry so we have to resolve the constant
        # name and return its color.
        else:
            constant_name = entry.constant_name
            return self.constants[constant_name]

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def constants(self):
        """A dictionary of constant styles."""
        return self._constants

    @property
    def names(self):
        """A dictionary of node name styles."""
        return self._names

    @property
    def nodes(self):
        """A dictionary of node type name styles."""
        return self._nodes

    @property
    def tools(self):
        """A dictionary of tool menu location styles."""
        return self._tools

    # =========================================================================
    # STATIC METHODS
    # =========================================================================

    @staticmethod
    def from_session():
        """Find or create a StyleManager for the session."""
        if not hasattr(hou.session, "style_manager"):
            hou.session.style_manager = StyleManager()

        return hou.session.style_manager

    # =========================================================================
    # METHODS
    # =========================================================================

    def styleNode(self, node):
        """Color the node given its properties.

        This function will attempt to color the node by first matching its
        node type name, then the tab menu location and the whether or not it
        is a manager or generator type.

        """
        node_type = node.type()

        # Look for a match with the node type name.
        style = self._getTypeStyle(node_type)

        # Look for a match given the node's Tab menu entries.
        if style is None:
            style = self._getToolStyle(node_type)

        if style is None:
            # Check if the node is a manager or generator.
            if node_type.isManager() or node_type.isGenerator():
                style = self._getManagerGeneratorStyle(node_type)

        # If a color was found, set it.
        if style is not None:
            style.applyToNode(node)

    def styleNodeByName(self, node):
        """Color the node given its name."""
        # Look for a name entry for the node's type category.
        style = self._getNameEntry(node)

        # If a color was found, set the node to it.
        if style is not None:
            style.applyToNode(node)

    def reload(self):
        """Reload all color mappings."""
        self.constants.clear()
        self.names.clear()
        self.nodes.clear()
        self.tools.clear()

        self._buildMappings()

# =============================================================================
# EXCEPTIONS
# =============================================================================


class ConstantDoesNotExistError(Exception):
    """Exception raised when a color attempts to reference a non-existent
    constant.

    """

    pass


class InvalidColorTypeError(Exception):
    """Exception raised when a color is not a valid type defined in
    hou.colorType.

    """

    pass

# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

def _buildShape(data):
    shape = data.get("shape")

    return shape


def _buildColor(entry):
    """Build a hou.Color object from data."""
    data = entry.get("color")

    if data is None:
        return None, None

    value = data["value"]

    # Create an empty color value since we don't know the color format yet.
    color = hou.Color()

    # Try to get the associated hou.colorType object from the type.
    try:
        color_type = getattr(hou.colorType, data["type"])

    # Catch the AttributeError generated by invalid types and raise an
    # InvalidColorTypeError instead.
    except AttributeError:
        raise InvalidColorTypeError(data["type"])

    # Set the color value given the specified type.
    if color_type == hou.colorType.RGB:
        # We support defining RGB colors with just a single value for grey
        # shades.  If one is detected, create at tuple from it.
        if not isinstance(value, list):
            value = [value] * 3

        color.setRGB(value)

    elif color_type == hou.colorType.HSL:
        color.setHSL(value)

    elif color_type == hou.colorType.HSV:
        color.setHSV(value)

    elif color_type == hou.colorType.LAB:
        color.setLAB(value)

    elif color_type == hou.colorType.XYZ:
        color.setXYZ(value)

    return color, data["type"]


def _findFiles():
    """Find any .json files that should be read."""
    try:
        directories = hou.findDirectories("config/styles")

    except hou.OperationFailed:
        directories = []

    all_files = []

    for directory in directories:
        all_files.extend(glob.glob(os.path.join(directory, "*.json")))

    return all_files


def _getToolMenuLocations(node_type):
    """Get any Tab menu locations the tool for the node type lives in."""
    # Need to get all of Houdini's tools.
    tools = hou.shelves.tools()

    # Figure out what the tool name should be for the give node type
    # information.
    tool_name = hou.shelves.defaultToolName(
        node_type.category().name(),
        node_type.name()
    )

    # Check the tool name corresponds to a valid tool.
    if tool_name in tools:
        tool = tools[tool_name]

        # Return the menu locations.
        return tool.toolMenuLocations()

    return ()

