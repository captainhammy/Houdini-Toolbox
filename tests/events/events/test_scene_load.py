"""Tests for ht.events.event.rop_render module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import imp

# Houdini Toolbox Imports
import ht.events.events.scene_load

from ht.events.item import HoudiniEventItem
from ht.events.types import SceneEvents

# Reload the module to test to capture load evaluation since it has already
# been loaded.
imp.reload(ht.events.events.scene_load)


# =============================================================================
# CLASSES
# =============================================================================


class Test_SceneLoadEvent(object):
    """Test ht.events.events.scene_load.SceneLoadEvent class."""

    def test___init__(self):
        event = ht.events.events.scene_load.SceneLoadEvent()

        expected_map = {
            SceneEvents.Load: HoudiniEventItem((event.clear_session_settings,))
        }

        assert event.event_map == expected_map

    # Methods

    def test_clear_session_settings(self, mocker):
        mocker.patch.object(
            ht.events.events.scene_load.SceneLoadEvent, "__init__", lambda x: None
        )
        mock_hscript = mocker.patch("ht.events.events.scene_load.hou.hscript")

        event = ht.events.events.scene_load.SceneLoadEvent()

        event.clear_session_settings({})

        mock_hscript.assert_called_with("set -u HOUDINI_ICON_CACHE_DIR")
