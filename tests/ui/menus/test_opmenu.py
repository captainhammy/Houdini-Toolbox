"""Tests for ht.ui.menus.opmenu module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Third Party Imports
from mock import MagicMock, patch

# Houdini Toolbox Imports
import ht.ui.menus.opmenu

# Houdini Imports
import hou


# =============================================================================
# CLASSES
# =============================================================================

def test_create_absolute_reference_copy():
    """Test ht.ui.menus.opmenu.create_absolute_reference_copy."""

    mock_node = MagicMock(spec=hou.Node)

    scriptargs = {
        "node": mock_node
    }

    ht.ui.menus.opmenu.create_absolute_reference_copy(scriptargs)

    mock_node.parent.return_value.copyItems.assert_called_with(
        [mock_node],
        channel_reference_originals=True,
        relative_references=False
    )


@patch("ht.ui.menus.opmenu.copy_item")
def test_save_item_to_file(mock_copy):
    """Test ht.ui.menus.opmenu.save_item_to_file."""
    mock_node = MagicMock(spec=hou.Node)

    scriptargs = {
        "node": mock_node
    }

    ht.ui.menus.opmenu.save_item_to_file(scriptargs)

    mock_copy.assert_called_with(mock_node)
