"""This module contains an event to color nodes based on events."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.events.group import HoudiniEventGroup
from ht.events import NodeEvents

from ht.nodes.colors.manager import ColorManager

# =============================================================================
# CLASSES
# =============================================================================


class ColorNodeEvent(HoudiniEventGroup):
    """Event to color Houdini nodes based on events."""

    def __init__(self):
        super(ColorNodeEvent, self).__init__()

        self.event_map.update(
            {
                NodeEvents.OnCreated: (self.colorNodeOnCreation,),
                NodeEvents.OnNameChanged: (self.colorNodeByName,),
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

