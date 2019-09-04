"""This module contains functions for managing and applying node styles in
Houdini.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.events import register_event_group
from ht.nodes.styles.event import StyleNodeEvent
import ht.nodes.styles.manager


# =============================================================================

# Register our event to handle automatic color setting.
register_event_group(StyleNodeEvent())
