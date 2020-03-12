"""Tests for ht.events.event.rop_render module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
import ht.events.events.scene_load
from ht.events.item import HoudiniEventItem
from ht.events.types import SceneEvents


# =============================================================================
# TESTS
# =============================================================================


class Test_SceneLoadEvent(object):
    """Test ht.events.events.scene_load.SceneLoadEvent class."""

    def test___init__(self, mocker):
        """Test object initialization."""
        mock_super_init = mocker.patch.object(ht.events.scene_load.HoudiniEventGroup, "__init__")

        event_map = {}
        mocker.patch.object(ht.events.events.scene_load.SceneLoadEvent, "event_map", event_map)

        event = ht.events.events.scene_load.SceneLoadEvent()

        mock_super_init.asset_called()

        expected_map = {
            SceneEvents.Load: HoudiniEventItem((event.clear_session_settings,))
        }

        assert event_map == expected_map

    def test_clear_session_settings(self, mocker):
        """Test clearing session settings."""
        mocker.patch.object(
            ht.events.events.scene_load.SceneLoadEvent, "__init__", lambda x: None
        )
        mock_hscript = mocker.patch("hou.hscript")

        event = ht.events.events.scene_load.SceneLoadEvent()

        event.clear_session_settings({})

        mock_hscript.assert_called_with("set -u HOUDINI_ICON_CACHE_DIR")
