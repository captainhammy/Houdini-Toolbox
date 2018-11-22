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
    """This class represents a named constant style."""

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
        return "<StyleConstant {} ({})>".format(
            self.name,
            self.color
        )

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def color(self):
        """The mapped color."""
        return self._color

    @color.setter
    def color(self, color):
        self._color = color

    # =========================================================================

    @property
    def color_type(self):
        """The mapped color type."""
        return self._color_type

    @color_type.setter
    def color_type(self, color_type):
        self._color_type = color_type

    # =========================================================================

    @property
    def shape(self):
        """The mapped shape."""
        return self._shape

    @shape.setter
    def shape(self, shape):
        self._shape = shape

    # =========================================================================

    @property
    def file_path(self):
        """Path the definition was from."""
        return self._file_path

    # =========================================================================

    @property
    def name(self):
        """The name the color is mapped to."""
        return self._name

    # =========================================================================
    # METHODS
    # =========================================================================

    def applyToNode(self, node):
        if self.color is not None:
            node.setColor(self.color)

        if self.shape is not None:
            node.setUserData("nodeshape", self.shape)


class StyleEntry(object):
    """This class represents a color application bound to a name.

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
        return "<StyleEntry {} ({})>".format(
            self.name,
            self.color
        )

    def __str__(self):
        value = self._getTypedColorValue()

        strs = [re.sub("\.*0+$", "", "{:0.3f}".format(val)) for val in value]

        return "(" + ", ".join(strs) + ")"

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _getTypedColorValue(self):
        to_func = getattr(self.color, self.color_type.lower())

        return to_func()

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def color(self):
        """The mapped color."""
        return self._color

    @property
    def color_type(self):
        """The mapped color type."""
        return self._color_type

    @property
    def shape(self):
        """The mapped shape name."""
        return self._shape

    @property
    def file_path(self):
        """Path the definition was from."""
        return self._file_path

    @property
    def name(self):
        """The name the style is mapped to."""
        return self._name

    # =========================================================================
    # METHODS
    # =========================================================================

    def applyToNode(self, node):
        if self.color is not None:
            node.setColor(self.color)

        if self.shape is not None:
            node.setUserData("nodeshape", self.shape)


class ConstantEntry(object):
    """This class represents a style application bound to a named constant.

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
        return "<ConstantEntry {} ({})>".format(
            self.name,
            self.constant_name
        )

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def constant_name(self):
        """The mapped constant."""
        return self._constant_name

    @property
    def file_path(self):
        """Path the definition was from."""
        return self._file_path

    @property
    def name(self):
        """The name the style is mapped to."""
        return self._name

