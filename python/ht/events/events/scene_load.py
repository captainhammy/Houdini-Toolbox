"""This module contains a class to color nodes based on events."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.events.event import HoudiniEvent

# Houdini Imports
import hou

# =============================================================================
# CLASSES
# =============================================================================

class SceneLoadEvent(HoudiniEvent):
    """Event to run on scene load (456)."""

    def __init__(self):
        super(SceneLoadEvent, self).__init__()

        self.event_map.update(
            {
                "456": (self.clearSessionSettings,),
            }
        )

    # =========================================================================
    # METHODS
    # =========================================================================

    def clearSessionSettings(self, scriptargs):
        """Clear out potentially annoying/bad settings."""
	# Remove an icon cache directory variable if it exists.
	hou.hscript("set -u HOUDINI_ICON_CACHE_DIR")

	hou.hscript("opdefaultcolor -c")
	hou.hscript("opdefaultshape -c")

