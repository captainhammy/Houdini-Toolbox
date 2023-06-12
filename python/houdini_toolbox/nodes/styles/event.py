"""This module contains an event to style nodes based on events."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox
from houdini_toolbox.nodes.styles.manager import STYLE_MANAGER

# =============================================================================
# FUNCTIONS
# =============================================================================


def style_node_by_name(scriptargs: dict) -> None:
    """Style a node based on a name.

    :param scriptargs: Data passed by event runner.
    :return:

    """
    node = scriptargs["node"]

    STYLE_MANAGER.style_node_by_name(node)


def style_node_on_creation(scriptargs: dict) -> None:
    """Style a node on creation."

    :param scriptargs: Data passed by event runner.
    :return:

    """
    node = scriptargs["node"]

    STYLE_MANAGER.style_node(node)
