"""This module contains a class to color nodes based on events."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.events.event import HoudiniEvent

from ht.nodes.colors.manager import ColorManager

# =============================================================================
# CLASSES
# =============================================================================

class ColorNodeEvent(HoudiniEvent):
    """Event to color Houdini nodes based on events."""

    def __init__(self):
        super(ColorNodeEvent, self).__init__()

        self.event_map.update(
            {
                "OnCreated": (self.colorNodeOnCreation,),
                "OnNameChanged": (self.colorNodeByName,),
            }
        )

    # =========================================================================
    # METHODS
    # =========================================================================

    def colorNodeByName(self, scriptargs):
        """Color a node based on a name."""
        node = scriptargs["node"]

        manager = ColorManager.getSessionManager()
        manager.colorNodeByName(node)

    def colorNodeOnCreation(self, scriptargs):
        """Color a node on creation."""
        node = scriptargs["node"]

        manager = ColorManager.getSessionManager()
        manager.colorNode(node)

