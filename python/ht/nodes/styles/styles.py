"""Classes representing color entries and mappings."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import re

# =============================================================================
# CLASSES
# =============================================================================


class StyleConstant(object):
    """This class represents a named constant style.

    :param name: The constant's name.
    :type name: str
    :param color: The constant's color.
    :type color: hou.Color
    :param color_type: The color type.
    :type color_type: str
    :param shape: The constant's shape.
    :type shape: str
    :param file_path: The path to the definition file.
    :type file_path: str
    :return:

    """

    def __init__(self, name, color, color_type, shape, file_path=None):
        self._color = color
        self._color_type = color_type
        self._shape = shape
        self._file_path = file_path
        self._name = name

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __eq__(self, rule):
        # For our purposes we only care if the names match.
        return self.name == rule.name

    def __repr__(self):
        return "<StyleConstant {} ({})>".format(self.name, self.color)

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def color(self):
        """hou.Color: The mapped color."""
        return self._color

    @color.setter
    def color(self, color):
        self._color = color

    # =========================================================================

    @property
    def color_type(self):
        """str: The mapped color type."""
        return self._color_type

    @color_type.setter
    def color_type(self, color_type):
        self._color_type = color_type

    # =========================================================================

    @property
    def file_path(self):
        """str: Path the definition was from."""
        return self._file_path

    # =========================================================================

    @property
    def name(self):
        """str: The name the color is mapped to."""
        return self._name

    # =========================================================================

    @property
    def shape(self):
        """str: The mapped shape."""
        return self._shape

    @shape.setter
    def shape(self, shape):
        self._shape = shape

    # =========================================================================
    # METHODS
    # =========================================================================

    def apply_to_node(self, node):
        """Apply styling to a node.

        :param node: Node to apply to
        :type node: hou.Node
        :return:

        """
        if self.color is not None:
            node.setColor(self.color)

        if self.shape is not None:
            node.setUserData("nodeshape", self.shape)


class StyleRule(object):
    """This class represents a color application bound to a name.

    :param name: The rules's name.
    :type name: str
    :param color: The rules's color.
    :type color: hou.Color
    :param color_type: The rules's color type.
    :type color_type: str
    :param shape: The rules's shape.
    :type shape: str
    :param file_path: The path to the definition file.
    :type file_path: str
    :return:

    """

    def __init__(self, name, color, color_type, shape, file_path=None):
        self._color = color
        self._color_type = color_type
        self._shape = shape
        self._file_path = file_path
        self._name = name

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __eq__(self, entry):
        # For our purposes we only care if the names match.
        return self.name == entry.name

    def __repr__(self):
        return "<StyleRule {} ({})>".format(self.name, self.color)

    def __str__(self):
        value = self._get_typed_color_value()

        strs = [re.sub("\\.*0+$", "", "{:0.3f}".format(val)) for val in value]

        return "(" + ", ".join(strs) + ")"

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _get_typed_color_value(self):
        """Get the appropriately typed color values.

        :return: The color value in the correct type.
        :rtype: tuple(float)

        """
        to_func = getattr(self.color, self.color_type.lower())

        return to_func()

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def color(self):
        """hou.Color: The mapped color."""
        return self._color

    @property
    def color_type(self):
        """str: The mapped color type."""
        return self._color_type

    @property
    def shape(self):
        """str: The mapped shape name."""
        return self._shape

    @property
    def file_path(self):
        """str: Path the definition was from."""
        return self._file_path

    @property
    def name(self):
        """str: The name the style is mapped to."""
        return self._name

    # =========================================================================
    # METHODS
    # =========================================================================

    def apply_to_node(self, node):
        """Apply styling to a node.

        :param node: Node to apply to
        :type node: hou.Node
        :return:
        """

        if self.color is not None:
            node.setColor(self.color)

        if self.shape is not None:
            node.setUserData("nodeshape", self.shape)


class ConstantRule(object):
    """This class represents a style application bound to a named constant.

    :param name: The rules's name.
    :type name: str
    :param constant_name: The constant name.
    :type constant_name: str
    :param file_path: The path to the definition file.
    :type file_path: str
    :return:

    """

    def __init__(self, name, constant_name, file_path=None):
        self._constant_name = constant_name
        self._file_path = file_path
        self._name = name

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __eq__(self, entry):
        # For our purposes we only care if the names match.
        return self.name == entry.name

    def __repr__(self):
        return "<ConstantRule {} ({})>".format(self.name, self.constant_name)

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def constant_name(self):
        """str: The mapped constant."""
        return self._constant_name

    @property
    def file_path(self):
        """str: Path the definition was from."""
        return self._file_path

    @property
    def name(self):
        """str: The name the style is mapped to."""
        return self._name
