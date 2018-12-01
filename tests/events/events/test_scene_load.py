"""Tests for ht.events.event.rop_render module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
from mock import patch
import unittest

# Houdini Toolbox Imports
import ht.events.events.scene_load

from ht.events.item import HoudiniEventItem
from ht.events.types import SceneEvents

reload(ht.events.events.scene_load)

# =============================================================================
# CLASSES
# =============================================================================

class Test_SceneLoadEvent(unittest.TestCase):
    """Test ht.events.events.scene_load.SceneLoadEvent class."""

    def test___init__(self):
        event = ht.events.events.scene_load.SceneLoadEvent()

        expected_map = {
            SceneEvents.Load: HoudiniEventItem((event.clear_session_settings,)),
        }

        self.assertEqual(event.event_map, expected_map)

    # Methods

    @patch("ht.events.events.scene_load.hou.hscript")
    @patch.object(ht.events.events.scene_load.SceneLoadEvent, "__init__", lambda x: None)
    def test_clear_session_settings(self, mock_hscript):
        event = ht.events.events.scene_load.SceneLoadEvent()

        event.clear_session_settings({})

        mock_hscript.assert_called_with("set -u HOUDINI_ICON_CACHE_DIR")

# =============================================================================

if __name__ == '__main__':
    unittest.main()
