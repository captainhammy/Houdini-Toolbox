"""Tests for ht.ui.menus.opmenu module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
from mock import MagicMock, patch
import unittest

# Houdini Toolbox Imports
import ht.ui.menus.opmenu

# Houdini Imports
import hou

reload(ht.ui.menus.opmenu)

# =============================================================================
# CLASSES
# =============================================================================

class Test_create_absolute_reference_copy(unittest.TestCase):
    """Test ht.ui.menus.opmenu.create_absolute_reference_copy."""

    def test(self):
        """Test creating an absolute reference copy."""
        mock_node = MagicMock(spec=hou.Node)

        scriptargs = {
            "node": mock_node
        }

        mock_ui = MagicMock()

        hou.ui = mock_ui

        ht.ui.menus.opmenu.create_absolute_reference_copy(scriptargs)

        mock_node.parent.return_value.copyItems.assert_called_with([mock_node], channel_reference_originals=True, relative_references=False)

        del hou.ui


class Test_save_item_to_file(unittest.TestCase):
    """Test ht.ui.menus.opmenu.save_item_to_file."""

    @patch("ht.ui.menus.opmenu.copy_item")
    def test(self, mock_copy):
        """Test saving an item to a file."""
        mock_node = MagicMock(spec=hou.Node)

        scriptargs = {
            "node": mock_node
        }

        ht.ui.menus.opmenu.save_item_to_file(scriptargs)

        mock_copy.assert_called_with(mock_node)

# =============================================================================

if __name__ == '__main__':
    unittest.main()
