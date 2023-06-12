"""This module contains functions for managing and applying node styles in
Houdini.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox
from houdini_toolbox.events import NodeEvents, register_function
from houdini_toolbox.nodes.styles.event import (
    style_node_by_name,
    style_node_on_creation,
)

# =============================================================================

# Register our events to handle automatic color setting.
register_function(style_node_on_creation, NodeEvents.OnCreated)
register_function(style_node_by_name, NodeEvents.OnNameChanged)
