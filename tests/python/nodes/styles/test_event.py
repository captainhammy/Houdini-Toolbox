"""Tests for houdini_toolbox.nodes.styles.event module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox
import houdini_toolbox.nodes.styles.event

# Houdini
import hou

# =============================================================================
# TESTS
# =============================================================================


def test_style_node_by_name(mocker):
    """Test styling a node by name."""
    mock_manager = mocker.patch("houdini_toolbox.nodes.styles.event.STYLE_MANAGER", autospec=True)

    mock_node = mocker.MagicMock(spec=hou.Node)

    scriptargs = {"node": mock_node}

    houdini_toolbox.nodes.styles.event.style_node_by_name(scriptargs)

    mock_manager.style_node_by_name.assert_called_with(mock_node)


def test_style_node_on_creation(mocker):
    """Test styling a node on creation."""
    mock_manager = mocker.patch("houdini_toolbox.nodes.styles.event.STYLE_MANAGER", autospec=True)

    mock_node = mocker.MagicMock(spec=hou.Node)

    scriptargs = {"node": mock_node}

    houdini_toolbox.nodes.styles.event.style_node_on_creation(scriptargs)

    mock_manager.style_node.assert_called_with(mock_node)
