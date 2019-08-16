"""Utilities for custom node badges."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
import _ht_generic_text_badge

# Houdini Imports
import hou


# ==============================================================================
# FUNCTIONS
# ==============================================================================

def clear_generic_text_badge(node):
    """Clear the generic text badge from the node.

    :param node: The node to clear the badge from.
    :type node: hou.Node
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


def clear_generic_text_badge_color(node):
    """Clear the generic text badge coloring from the node.

    :param node: The node to clear badge coloring from.
    :type node: hou.Node
    :return:

    """
    with hou.undos.disabler():
        # Try to remove the user data from the node.
        try:
            node.destroyUserData(_ht_generic_text_badge.get_generic_text_color_key())

        # Will fail if it doesn't exist, so just ignore.
        except hou.OperationFailed:
            pass


def set_generic_text_badge(node, value, color=None):
    """Set the node's generic text badge.

    :param node: The node to set the badge for.
    :type node: hou.Node
    :param value: The badge value.
    :type value: str
    :param color: An optional text color.
    :type color: hou.Color
    :return:

    """
    with hou.undos.disabler():
        # Set the user data.
        node.setUserData(
            _ht_generic_text_badge.get_generic_text_key(),
            value
        )

        if color is not None:
            set_generic_text_badge_color(node, color)


def set_generic_text_badge_color(node, color):
    """Set the node's generic text badge color.

    :param node: The node to set the badge for.
    :type node: hou.Node
    :param color: The text color.
    :type color: hou.Color
    :return:

    """
    # Get the color RGB values.
    rgb_value = color.rgb()

    with hou.undos.disabler():
        # Set the user data with a valid text -> color string.
        node.setUserData(
            _ht_generic_text_badge.get_generic_text_color_key(),
            "rgb {} {} {}".format(*rgb_value)
        )
