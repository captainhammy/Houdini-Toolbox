"""Tests for ht.nodes.styles.event module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
from mock import MagicMock, patch
import unittest

# Houdini Toolbox Imports
import ht.nodes.styles.event

from ht.events.item import HoudiniEventItem
from ht.events.types import NodeEvents

# Houdini Imports
import hou

reload(ht.nodes.styles.event)

# =============================================================================
# CLASSES
# =============================================================================

class Test_StyleNodeEvent(unittest.TestCase):
    """Test ht.nodes.styles.event.StyleNodeEvent class."""

    def test___init__(self):
        event = ht.nodes.styles.event.StyleNodeEvent()

        expected_map = {
            NodeEvents.OnCreated: HoudiniEventItem((event.style_node_on_creation,)),
            NodeEvents.OnNameChanged: HoudiniEventItem((event.style_node_by_name,)),
        }

        self.assertEqual(event.event_map, expected_map)

    # Methods

    # style_node_by_name

    @patch("ht.nodes.styles.event.MANAGER", autospec=True)
    @patch.object(ht.nodes.styles.event.StyleNodeEvent, "__init__", lambda x: None)
    def test_style_node_by_name(self, mock_manager):
        mock_node = MagicMock(spec=hou.Node)

        event = ht.nodes.styles.event.StyleNodeEvent()

        scriptargs = {"node": mock_node}

        event.style_node_by_name(scriptargs)

        mock_manager.style_node_by_name.assert_called_with(mock_node)

    # style_node_on_creation

    @patch("ht.nodes.styles.event.MANAGER", autospec=True)
    @patch.object(ht.nodes.styles.event.StyleNodeEvent, "__init__", lambda x: None)
    def test_style_node_on_creation(self, mock_manager):
        mock_node = MagicMock(spec=hou.Node)

        event = ht.nodes.styles.event.StyleNodeEvent()

        scriptargs = {"node": mock_node}

        event.style_node_on_creation(scriptargs)

        mock_manager.style_node.assert_called_with(mock_node)

# =============================================================================

if __name__ == '__main__':
    unittest.main()
