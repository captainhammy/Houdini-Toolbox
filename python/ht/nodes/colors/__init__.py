"""This module contains a class and functions for managing and applying node
colors in Houdini.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.nodes.colors.manager import ColorManager

# Houdini Imports
import hou

# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

def _findSessionColorManager():
    """Look at hou.session for a ColorManager stored as a 'colorManager'
    attribute.  If the manager exists, return it.

    """
    manager = None

    # Check to see if the manager exists.  If so, retrieve it.
    if hasattr(hou.session, "color_manager"):
        manager = hou.session.color_manager

    return manager

# =============================================================================
# FUNCTIONS
# =============================================================================

def colorNode(node):
    """Color the node given its properties.

    This function will attempt to color the node by first matching its
    node type name, then the tab menu location and the whether or not it
    is a manager or generator type.

    """
    # Try to find the session color manager.
    manager = _findSessionColorManager()

    # If one exists, use it to try to color the node.
    if manager is not None:
        manager.colorNode(node)


def colorNodeByName(node):
    """Color the node given its name."""
    # Try to find the session color manager.
    manager = _findSessionColorManager()

    # If one exists, use it to try to color the node.
    if manager is not None:
        manager.colorNodeByName(node)


def createSessionColorManager():
    """Create a new ColorManager object and store it in
    hou.session.color_manager.

    """
    manager = ColorManager()
    hou.session.color_manager = manager

