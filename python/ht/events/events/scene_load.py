"""This module contains an event to perform actions on scene load."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.events.group import HoudiniEventGroup
from ht.events.item import HoudiniEventItem
from ht.events.types import SceneEvents

# Houdini Imports
import hou


# =============================================================================
# CLASSES
# =============================================================================


class SceneLoadEvent(HoudiniEventGroup):
    """Event to run on scene load (456)."""

    def __init__(self):
        super().__init__()

        load_item = HoudiniEventItem((self.clear_session_settings,))

        self.event_map.update({SceneEvents.Load: load_item})

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def clear_session_settings(
        self, scriptargs: dict
    ):  # pylint: disable=no-self-use,unused-argument
        """Clear out potentially annoying/bad settings.

        :param scriptargs: Event data.
        :return:

        """
        # Remove an icon cache directory variable if it exists.
        hou.hscript("set -u HOUDINI_ICON_CACHE_DIR")
