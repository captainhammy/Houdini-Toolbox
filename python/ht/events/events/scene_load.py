"""This module contains an event to perform actions on scene load."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Imports
import hou
# Houdini Toolbox Imports
from ht.events.block import HoudiniEventBlock
from ht.events.types import SceneEvents


# =============================================================================
# CLASSES
# =============================================================================

class SceneLoadEvent(HoudiniEventBlock):
    """Event to run on scene load (456)."""

    _EVENT_NAME = SceneEvents.Load

    def __init__(self):
        super(SceneLoadEvent, self).__init__()

        self._order = [
            self.clearSessionSettings,
        ]

    # =========================================================================
    # METHODS
    # =========================================================================

    def clearSessionSettings(self, scriptargs):
        """Clear out potentially annoying/bad settings."""
        # Remove an icon cache directory variable if it exists.
        hou.hscript("set -u HOUDINI_ICON_CACHE_DIR")
