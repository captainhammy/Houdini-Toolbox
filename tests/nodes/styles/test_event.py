"""Tests for ht.nodes.styles.event module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
import ht.nodes.styles.event
from ht.events.item import HoudiniEventItem
from ht.events.types import NodeEvents

# Houdini Imports
import hou


# =============================================================================
# TESTS
# =============================================================================


class Test_StyleNodeEvent:
    """Test ht.nodes.styles.event.StyleNodeEvent class."""

    def test___init__(self):
        """Test object initialization."""
        event = ht.nodes.styles.event.StyleNodeEvent()

        expected_map = {
            NodeEvents.OnCreated: HoudiniEventItem((event.style_node_on_creation,)),
            NodeEvents.OnNameChanged: HoudiniEventItem((event.style_node_by_name,)),
        }

        assert event.event_map == expected_map

    # Methods

    def test_style_node_by_name(self, mocker):
        """Test styling a node by name."""
        mocker.patch.object(
            ht.nodes.styles.event.StyleNodeEvent, "__init__", lambda x: None
        )
        mock_manager = mocker.patch("ht.nodes.styles.event.STYLE_MANAGER", autospec=True)

        mock_node = mocker.MagicMock(spec=hou.Node)

        event = ht.nodes.styles.event.StyleNodeEvent()

        scriptargs = {"node": mock_node}

        event.style_node_by_name(scriptargs)

        mock_manager.style_node_by_name.assert_called_with(mock_node)

    def test_style_node_on_creation(self, mocker):
        """Test styling a node on creation."""
        mocker.patch.object(
            ht.nodes.styles.event.StyleNodeEvent, "__init__", lambda x: None
        )
        mock_manager = mocker.patch("ht.nodes.styles.event.STYLE_MANAGER", autospec=True)

        mock_node = mocker.MagicMock(spec=hou.Node)

        event = ht.nodes.styles.event.StyleNodeEvent()

        scriptargs = {"node": mock_node}

        event.style_node_on_creation(scriptargs)

        mock_manager.style_node.assert_called_with(mock_node)
