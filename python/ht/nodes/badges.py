"""Utilities for custom node badges."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
from typing import Optional

# Third Party
import _ht_generic_image_badge
import _ht_generic_text_badge

# Houdini
import hou

# ==============================================================================
# FUNCTIONS
# ==============================================================================


def clear_generic_image_badge(node: hou.Node):
    """Clear the generic image badge from the node.

    :param node: The node to clear the badge from.
    :return:

    """
    with hou.undos.disabler():
        # Try to remove the user data from the node.
        try:
            node.destroyUserData(_ht_generic_image_badge.get_generic_image_key())

        # Will fail if it doesn't exist, so just ignore.
        except hou.OperationFailed:
            pass


def clear_generic_text_badge(node: hou.Node):
    """Clear the generic text badge from the node.

    :param node: The node to clear the badge from.
    :return:

    """
    with hou.undos.disabler():
        # Try to remove the user data from the node.
        try:
            node.destroyUserData(_ht_generic_text_badge.get_generic_text_key())

        # Will fail if it doesn't exist, so just ignore.
        except hou.OperationFailed:
            pass

        # If we're clearing the text then clear any coloring too.
        clear_generic_text_badge_color(node)


def clear_generic_text_badge_color(node: hou.Node):
    """Clear the generic text badge coloring from the node.

    :param node: The node to clear badge coloring from.
    :return:

    """
    with hou.undos.disabler():
        # Try to remove the user data from the node.
        try:
            node.destroyUserData(_ht_generic_text_badge.get_generic_text_color_key())

        # Will fail if it doesn't exist, so just ignore.
        except hou.OperationFailed:
            pass


def set_generic_image_badge(node: hou.Node, image: str):
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
):
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


def set_generic_text_badge_color(node: hou.Node, color: hou.Color):
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
            "rgb {} {} {}".format(*rgb_value),
        )
