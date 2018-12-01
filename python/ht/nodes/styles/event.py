"""This module contains an event to style nodes based on events."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.events.group import HoudiniEventGroup
from ht.events.item import HoudiniEventItem
from ht.events import NodeEvents

from ht.nodes.styles.manager import MANAGER

# =============================================================================
# CLASSES
# =============================================================================

class StyleNodeEvent(HoudiniEventGroup):
    """Event to style Houdini nodes based on events."""

    def __init__(self):
        super(StyleNodeEvent, self).__init__()

        self.event_map.update(
            {
                NodeEvents.OnCreated: HoudiniEventItem((self.style_node_on_creation,)),
                NodeEvents.OnNameChanged: HoudiniEventItem((self.style_node_by_name,)),
            }
        )
    # =========================================================================
    # METHODS
    # =========================================================================

    def style_node_by_name(self, scriptargs):
        """Style a node based on a name.

        :param scriptargs: Data passed by event runner.
        :type scriptargs: dict
        :return:

        """
        node = scriptargs["node"]

        MANAGER.style_node_by_name(node)

    def style_node_on_creation(self, scriptargs):
        """Style a node on creation."

        :param scriptargs: Data passed by event runner.
        :type scriptargs: dict
        :return:

        """
        node = scriptargs["node"]

        MANAGER.style_node(node)
