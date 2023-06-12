"""Utilities for custom node badges."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import contextlib
from typing import Optional

# Houdini Toolbox
from houdini_toolbox.nodes import (  # type: ignore # pylint: disable=no-name-in-module
    _ht_generic_image_badge,
    _ht_generic_text_badge,
)

# Houdini
import hou

# ==============================================================================
# FUNCTIONS
# ==============================================================================


def clear_generic_image_badge(node: hou.Node) -> None:
    """Clear the generic image badge from the node.

    :param node: The node to clear the badge from.
    :return:

    """
    # Try to remove the user data from the node. If the data doesn't exist
    # it will fail, but we can just ignore that.
    with hou.undos.disabler(), contextlib.suppress(hou.OperationFailed):
        node.destroyUserData(_ht_generic_image_badge.get_generic_image_key())


def clear_generic_text_badge(node: hou.Node) -> None:
    """Clear the generic text badge from the node.

    :param node: The node to clear the badge from.
    :return:

    """
    # Try to remove the user data from the node. If the data doesn't exist
    # it will fail, but we can just ignore that.
    with hou.undos.disabler():
        with contextlib.suppress(hou.OperationFailed):
            # Try to remove the user data from the node.
            node.destroyUserData(_ht_generic_text_badge.get_generic_text_key())

        # If we're clearing the text then clear any coloring too.
        clear_generic_text_badge_color(node)


def clear_generic_text_badge_color(node: hou.Node) -> None:
    """Clear the generic text badge coloring from the node.

    :param node: The node to clear badge coloring from.
    :return:

    """
    # Try to remove the user data from the node. If the data doesn't exist
    # it will fail, but we can just ignore that.
    with hou.undos.disabler(), contextlib.suppress(hou.OperationFailed):
        node.destroyUserData(_ht_generic_text_badge.get_generic_text_color_key())


def set_generic_image_badge(node: hou.Node, image: str) -> None:
    """Set the node's generic image badge.

    :param node: The node to set the badge for.
    :param image: The image to set.
    :return:

    """
    with hou.undos.disabler():
        # Set the user data.
        node.setUserData(_ht_generic_image_badge.get_generic_image_key(), image)


def set_generic_text_badge(
    node: hou.Node, value: str, color: Optional[hou.Color] = None
) -> None:
    """Set the node's generic text badge.

    :param node: The node to set the badge for.
    :param value: The badge value.
    :param color: An optional text color.
    :return:

    """
    with hou.undos.disabler():
        # Set the user data.
        node.setUserData(_ht_generic_text_badge.get_generic_text_key(), value)

        if color is not None:
            set_generic_text_badge_color(node, color)


def set_generic_text_badge_color(node: hou.Node, color: hou.Color) -> None:
    """Set the node's generic text badge color.

    :param node: The node to set the badge for.
    :param color: The text color.
    :return:

    """
    # Get the color RGB values.
    rgb_value = color.rgb()

    with hou.undos.disabler():
        # Set the user data with a valid text -> color string.
        node.setUserData(
            _ht_generic_text_badge.get_generic_text_color_key(),
            f"rgb {rgb_value[0]} {rgb_value[1]} {rgb_value[2]}",
        )
