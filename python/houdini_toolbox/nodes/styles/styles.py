"""Classes representing color entries and mappings."""

# =============================================================================
# IMPORTS
# =============================================================================

from __future__ import annotations

# Standard Library
import re
from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    import hou

# =============================================================================
# CLASSES
# =============================================================================


class StyleConstant:
    """This class represents a named constant style.

    :param name: The constant's name.
    :param color: The constant's color.
    :param color_type: The color type.
    :param shape: The constant's shape.
    :param file_path: The path to the definition file.
    :return:

    """

    def __init__(
        self,
        name: str,
        color: hou.Color,
        color_type: str,
        shape: Optional[str] = None,
        file_path: Optional[str] = None,
    ):
        self._color = color
        self._color_type = color_type
        self._shape = shape
        self._file_path = file_path
        self._name = name

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __eq__(self, other):
        if not isinstance(other, StyleConstant):
            return NotImplemented

        # For our purposes we only care if the names match.
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __ne__(self, other):
        if not isinstance(other, StyleConstant):
            return NotImplemented

        return not self.__eq__(other)

    def __repr__(self):
        return f"<StyleConstant {self.name} ({self.color})>"

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def color(self) -> hou.Color:
        """The mapped color."""
        return self._color

    # -------------------------------------------------------------------------

    @property
    def color_type(self) -> str:
        """The mapped color type."""
        return self._color_type

    # -------------------------------------------------------------------------

    @property
    def file_path(self) -> Optional[str]:
        """Path the definition was from."""
        return self._file_path

    # -------------------------------------------------------------------------

    @property
    def name(self) -> str:
        """The name the color is mapped to."""
        return self._name

    # -------------------------------------------------------------------------

    @property
    def shape(self) -> Optional[str]:
        """The mapped shape."""
        return self._shape

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def apply_to_node(self, node: hou.Node):
        """Apply styling to a node.

        :param node: Node to apply to
        :return:

        """
        if self.color is not None:
            node.setColor(self.color)

        if self.shape is not None:
            node.setUserData("nodeshape", self.shape)


class StyleRule:
    """This class represents a color application bound to a name.

    :param name: The rule's name.
    :param color: The rule's color.
    :param color_type: The rule's color type.
    :param shape: The rule's shape.
    :param file_path: The path to the definition file.
    :return:

    """

    def __init__(
        self,
        name: str,
        color: hou.Color,
        color_type: str,
        shape: Optional[str] = None,
        file_path: Optional[str] = None,
    ):
        self._color = color
        self._color_type = color_type
        self._shape = shape
        self._file_path = file_path
        self._name = name

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __eq__(self, other):
        if not isinstance(other, StyleRule):
            return NotImplemented

        # For our purposes we only care if the names match.
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __ne__(self, other):
        if not isinstance(other, StyleRule):
            return NotImplemented

        return not self.__eq__(other)

    def __repr__(self):
        return f"<StyleRule {self.name} ({self.color})>"

    def __str__(self):
        value = self._get_typed_color_value()

        components = [re.sub("\\.*0+$", "", f"{val:0.3f}") for val in value]

        return "(" + ", ".join(components) + ")"

    # -------------------------------------------------------------------------
    # NON-PUBLIC METHODS
    # -------------------------------------------------------------------------

    def _get_typed_color_value(self) -> Tuple[float]:
        """Get the appropriately typed color values.

        :return: The color value in the correct type.

        """
        to_func = getattr(self.color, self.color_type.lower())

        return to_func()

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def color(self) -> hou.Color:
        """The mapped color."""
        return self._color

    @property
    def color_type(self) -> str:
        """The mapped color type."""
        return self._color_type

    @property
    def shape(self) -> Optional[str]:
        """The mapped shape name."""
        return self._shape

    @property
    def file_path(self) -> Optional[str]:
        """Path the definition was from."""
        return self._file_path

    @property
    def name(self) -> str:
        """The name the style is mapped to."""
        return self._name

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def apply_to_node(self, node: hou.Node):
        """Apply styling to a node.

        :param node: Node to apply to
        :return:
        """

        if self.color is not None:
            node.setColor(self.color)

        if self.shape is not None:
            node.setUserData("nodeshape", self.shape)


class ConstantRule:
    """This class represents a style application bound to a named constant.

    :param name: The rule's name.
    :param constant_name: The constant name.
    :param file_path: The path to the definition file.
    :return:

    """

    def __init__(self, name: str, constant_name: str, file_path: Optional[str] = None):
        self._constant_name = constant_name
        self._file_path = file_path
        self._name = name

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __eq__(self, other):
        if not isinstance(other, ConstantRule):
            return NotImplemented

        # For our purposes we only care if the names match.
        return self.name == other.name

    def __hash__(self):
        return hash((self.constant_name, self.name))

    def __ne__(self, other):
        if not isinstance(other, ConstantRule):
            return NotImplemented

        return not self.__eq__(other)

    def __repr__(self):
        return f"<ConstantRule {self.name} ({self.constant_name})>"

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def constant_name(self) -> str:
        """The mapped constant."""
        return self._constant_name

    @property
    def file_path(self) -> Optional[str]:
        """Path the definition was from."""
        return self._file_path

    @property
    def name(self) -> str:
        """The name the style is mapped to."""
        return self._name
