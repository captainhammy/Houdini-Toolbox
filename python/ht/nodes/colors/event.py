"""This module contains an event to color nodes based on events."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.events.group import HoudiniEventGroup
from ht.events import NodeEvents

from ht.nodes.colors.manager import StyleManager

# =============================================================================
# CLASSES
# =============================================================================


class StyleNodeEvent(HoudiniEventGroup):
    """Event to style Houdini nodes based on events."""

    def __init__(self):
        super(StyleNodeEvent, self).__init__()

        self.event_map.update(
            {
                NodeEvents.OnCreated: (self.styleNodeOnCreation,),
                NodeEvents.OnNameChanged: (self.styleNodeByName,),
            }
        )

    # =========================================================================
    # METHODS
    # =========================================================================

    def styleNodeByName(self, scriptargs):
        """Style a node based on a name."""
        node = scriptargs["node"]

        manager = StyleManager.from_session()
        manager.colorNodeByName(node)

    def styleNodeOnCreation(self, scriptargs):
        """Style a node on creation."""
        node = scriptargs["node"]

        manager = StyleManager.from_session()
        manager.styleNode(node)

