"""This module contains functions for managing and applying node styles in
Houdini.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.events import registerEventGroup
from ht.nodes.colors.event import StyleNodeEvent
from ht.nodes.colors.manager import StyleManager

# =============================================================================

# Register our event to handle automatic color setting.
registerEventGroup(StyleNodeEvent())

# Initialize the session style manager.
StyleManager.from_session()

