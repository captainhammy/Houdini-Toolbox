"""This module contains an event to perform actions on scene load."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.events.block import HoudiniEventBlock
from ht.events.types import SceneEvents

from ht.sohohooks.aovs.sources import AOVHipSource

# Houdini Imports
import hou

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
            self.loadHipAOVs,
        ]

    # =========================================================================
    # METHODS
    # =========================================================================

    def clearSessionSettings(self, scriptargs):
        """Clear out potentially annoying/bad settings."""
        # Remove an icon cache directory variable if it exists.
        hou.hscript("set -u HOUDINI_ICON_CACHE_DIR")

    def loadHipAOVs(self, scriptargs):
        root = hou.node("/")

        if "aovs.json" in root.userDataDict():
            source = AOVHipSource()

            manager = hou.session.aov_manager
            manager.loadSource(source)

