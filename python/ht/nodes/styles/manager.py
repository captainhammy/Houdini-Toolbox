"""This module contains a class and functions for managing and applying node
colors in Houdini.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
from __future__ import annotations
import glob
import json
import os
from typing import List, Optional, Tuple, Union

# Houdini Toolbox Imports
from ht.nodes.styles.styles import ConstantRule, StyleConstant, StyleRule
from ht.nodes.styles import constants

# Houdini Imports
import hou


# =============================================================================
# CLASSES
# =============================================================================


class StyleManager:
    """Manage and apply Houdini node styles."""

    def __init__(self):
        self._constants = {}
        self._name_rules = {}
        self._node_type_rules = {}
        self._tool_rules = {}

        # Build mappings for this object.
        self._build()

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __repr__(self):
        return "<StyleManager>"

    # -------------------------------------------------------------------------
    # NON-PUBLIC METHODS
    # -------------------------------------------------------------------------

    def _build(self):
        """Build styling data from files.

        :return:

        """
        files = _find_files()

        all_data = []

        # Read all the target files in reverse.
        for path in reversed(files):
            # Open the target file and load the data.
            with open(path) as handle:
                data = json.load(handle)

            data[constants.PATH_KEY] = path
            all_data.append(data)

        self._build_constants_from_data(all_data)

        self._build_rules_from_data(all_data)

    def _build_constants_from_data(self, all_data: List):
        """Build style constants from data..

        :param all_data: Base data definitions
        :return:

        """
        for data in all_data:
            path = data[constants.PATH_KEY]

            # Process any constants first so they can be used by assignments.
            if constants.CONSTANT_DEFINITION_KEY in data:
                for name, entry in list(
                    data[constants.CONSTANT_DEFINITION_KEY].items()
                ):
                    # Get the color from the info.

                    color, color_type = _build_color(entry)
                    shape = _build_shape(entry)

                    # Store the constant under its name.
                    self.constants[name] = StyleConstant(
                        name, color, color_type, shape, path
                    )

    def _build_rules_from_data(self, all_data: List):
        """Build style rules from data.

        :param all_data: Base data definitions
        :return:

        """
        for data in all_data:
            if constants.RULES_KEY in data:
                rules_data = data[constants.RULES_KEY]

                path = data[constants.PATH_KEY]

                for rule_type, rule_data in list(rules_data.items()):
                    # Get the mapping dictionary from the manager.
                    rule_type_map = getattr(self, rule_type)

                    # Process each category in the data.
                    for category_name, rules in list(rule_data.items()):
                        # Get a mapping list for the category name.
                        category_map = rule_type_map.setdefault(category_name, {})

                        _build_category_rules(rules, category_map, path, self.constants)

    def _get_manager_generator_style(self, node_type: hou.NodeType) -> Optional[Union[StyleConstant, StyleRule]]:
        """Look for a style match based on the node type being a manager or
        generator type.

        :param node_type: A manager/generator node type
        :return: An applicable styling object.

        """
        categories = (node_type.category().name(), constants.ALL_CATEGORY_KEY)

        for category_name in categories:
            # Check if the category has any rules.
            if category_name in self.node_type_rules:
                category_rules = self.node_type_rules[category_name]

                # The node type is a manager.
                if node_type.isManager():
                    # Check for a manager rule under the category.
                    if constants.MANAGER_TYPE_KEY in category_rules:
                        return self._resolve_rule(
                            category_rules[constants.MANAGER_TYPE_KEY]
                        )

                # The node type is a generator.
                elif node_type.isGenerator():
                    # Check for a generator rule under the category.
                    if constants.GENERATOR_TYPE_KEY in category_rules:
                        return self._resolve_rule(
                            category_rules[constants.GENERATOR_TYPE_KEY]
                        )

                else:
                    raise ValueError(
                        "{} is not a manager or a generator type".format(
                            node_type.nameWithCategory()
                        )
                    )

        return None

    def _get_name_style(self, node: hou.Node) -> Optional[Union[StyleConstant, StyleRule]]:
        """Look for a style match based on the node name.

        :param node: Node to style by name.
        :return: An applicable styling object.

        """
        # The node name.
        name = node.name()

        categories = (node.type().category().name(), constants.ALL_CATEGORY_KEY)

        for category_name in categories:
            # Check for rules for the node type category.
            if category_name in self.name_rules:
                # Check if the name matches any of the category rules.
                for rule in list(self.name_rules[category_name].values()):
                    if hou.patternMatch(rule.name, name):
                        return self._resolve_rule(rule)

        return None

    def _get_node_type_style(self, node_type: hou.NodeType) -> Optional[Union[StyleConstant, StyleRule]]:
        """Look for a style match based on the node type's name.

        :param node_type: Node type to style by name
        :return: An applicable styling object.

        """
        type_name = node_type.nameComponents()[2]

        # Get the category name from the node and also check the 'all'
        # category.
        categories = (node_type.category().name(), constants.ALL_CATEGORY_KEY)

        for category_name in categories:
            # Check if the category has any rules.
            if category_name in self.node_type_rules:
                # Check if the node type name matches any of the category
                # rules.
                for rule in list(self.node_type_rules[category_name].values()):
                    if hou.patternMatch(rule.name, type_name):
                        return self._resolve_rule(rule)

        return None

    def _get_tool_style(self, node_type: hou.NodeType) -> Optional[Union[StyleConstant, StyleRule]]:
        """Look for a color match based on the node type's Tab menu
        locations.

        :param node_type: Node type to style by tab menu location
        :return: An applicable styling object.

        """
        categories = (node_type.category().name(), constants.ALL_CATEGORY_KEY)
        # Get any Tab menu locations the node type might show up in.
        menu_locations = _get_tool_menu_locations(node_type)

        for category_name in categories:
            # Check for rules for the node type category.
            if category_name in self.tool_rules:
                # Process the locations, looking for the first match.
                for location in menu_locations:
                    # Check if the location matches any of the category rules.
                    for rule in list(self.tool_rules[category_name].values()):
                        if hou.patternMatch(rule.name, location):
                            return self._resolve_rule(rule)

        return None

    def _resolve_rule(self, rule: Union[ConstantRule, StyleRule]) -> Union[StyleConstant, StyleRule]:
        """Resolve the entry to a color.

        The entry might a style or a constant so this will return the actual
        style.

        :param rule: A rule object to resolve.
        :return: A resolved rule.

        """
        # If the entry object is a ColorEntry then we can just return the
        # color.
        if isinstance(rule, StyleRule):
            return rule

        # Otherwise it is a ConstantRule so we have to resolve the constant
        # name and return its color.
        constant_name = rule.constant_name
        return self.constants[constant_name]

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def constants(self) -> dict:
        """A dictionary of constant styles."""
        return self._constants

    @property
    def name_rules(self) -> dict:
        """A dictionary of node name styles."""
        return self._name_rules

    @property
    def node_type_rules(self) -> dict:
        """A dictionary of node type name styles."""
        return self._node_type_rules

    @property
    def tool_rules(self) -> dict:
        """A dictionary of tool menu location styles."""
        return self._tool_rules

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def style_node(self, node: hou.Node):
        """Style the node given its properties.

        This function will attempt to style the node by first matching its
        node type name, then the tab menu location and the whether or not it
        is a manager or generator type.

        :param node: A node to style
        :return:

        """

        node_type = node.type()

        # Look for a match with the node type name.
        style = self._get_node_type_style(node_type)

        # Look for a match given the node's Tab menu entries.
        if style is None:
            style = self._get_tool_style(node_type)

        if style is None:
            # Check if the node is a manager or generator.
            if node_type.isManager() or node_type.isGenerator():
                style = self._get_manager_generator_style(node_type)

        # If a color was found, set it.
        if style is not None:
            style.apply_to_node(node)

    def style_node_by_name(self, node: hou.Node):
        """Style the node given its name.

        :param node: A node to style
        :return:

        """
        # Look for a name entry for the node's type category.
        style = self._get_name_style(node)

        # If a color was found, set the node to it.
        if style is not None:
            style.apply_to_node(node)

    def reload(self):
        """Reload all color mappings.

        :return:

        """
        self.constants.clear()
        self.name_rules.clear()
        self.node_type_rules.clear()
        self.tool_rules.clear()

        self._build()


# =============================================================================
# EXCEPTIONS
# =============================================================================


class ConstantDoesNotExistError(Exception):
    """Exception raised when a color attempts to reference a non-existent
    constant.

    """


class InvalidColorTypeError(Exception):
    """Exception raised when a color is not a valid type defined in
    hou.colorType.

    """


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _build_category_rules(rules: List[dict], category_map: dict, path: str, constant_map: dict):
    """Build constant and style rules.

    :param rules: Rule data
    :param category_map: Mapping of rules for a category.
    :param path: The source file path.
    :param constant_map: Dictionary of known constants.
    :return:

    """
    # Process each rule.  The rule name can be a node
    # type name, Tab menu folder name, or manager/generator.
    for rule_data in rules:
        # Get the rule name.
        rule_name = rule_data[constants.RULE_NAME_KEY]

        # Handle constants.
        if constants.RULE_CONSTANT_KEY in rule_data:
            constant_name = rule_data[constants.RULE_CONSTANT_KEY]

            # Ensure the constant exists.  If not, raise an
            # exception.
            if constant_name not in constant_map:
                raise ConstantDoesNotExistError(constant_name)

            rule = ConstantRule(rule_name, constant_name, path)

        # Handle styles.
        else:
            # Build the style data from the raw data.
            color, color_type = _build_color(rule_data)
            shape = _build_shape(rule_data)

            # Add a StyleRule to the list.
            rule = StyleRule(rule_name, color, color_type, shape, path)

        # Add the rule to the map.
        category_map[rule_name] = rule


def _build_color(rule: dict) -> Union[Tuple[hou.Color, str], Tuple[None, None]]:
    """Build a hou.Color object from data.

    :param rule: Style information
    :return: Color information

    """
    data = rule.get(constants.RULE_COLOR_KEY)

    if data is None:
        return None, None

    # Try to get the associated hou.colorType object from the type.
    try:
        color_type = getattr(hou.colorType, data[constants.RULE_COLOR_TYPE_KEY])

    # Catch the AttributeError generated by invalid types and raise an
    # InvalidColorTypeError instead.
    except AttributeError as exc:
        raise InvalidColorTypeError(data[constants.RULE_COLOR_TYPE_KEY]) from exc

    value = data[constants.RULE_COLOR_VALUE_KEY]

    # Create an empty color value since we don't know the color format yet.
    color = hou.Color()

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

    # XYZ
    else:
        color.setXYZ(value)

    return color, data[constants.RULE_COLOR_TYPE_KEY]


def _build_shape(rule: dict) -> str:
    """Build shape information.

    :param rule: Style information
    :return: Shape name

    """
    shape = rule.get(constants.RULE_SHAPE_KEY)

    return shape


def _find_files() -> Tuple[str]:
    """Find any .json files that should be read.

    :return: Any found style files.

    """
    try:
        directories = hou.findDirectories("config/styles")

    except hou.OperationFailed:
        directories = []

    all_files = []

    for directory in directories:
        all_files.extend(glob.glob(os.path.join(directory, "*.json")))

    return tuple(str(f) for f in all_files)


def _get_tool_menu_locations(node_type: hou.NodeType) -> Tuple[str]:
    """Get any Tab menu locations the tool for the node type lives in.

    :param node_type: A node type to get Tab menu locations for
    :return: Any Tab menu locations the node type's tool appears under

    """
    # Need to get all of Houdini's tools.
    tools = hou.shelves.tools()

    # Figure out what the tool name should be for the give node type
    # information.
    tool_name = hou.shelves.defaultToolName(
        node_type.category().name(), node_type.name()
    )

    # Check the tool name corresponds to a valid tool.
    if tool_name in tools:
        tool = tools[tool_name]

        # Return the menu locations.
        return tool.toolMenuLocations()

    return tuple()


# =============================================================================

MANAGER = StyleManager()
