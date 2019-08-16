"""Tests for ht.nodes.badges module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
from mock import MagicMock, patch
import unittest

# Houdini Toolbox Imports
from ht.nodes import badges

# Houdini Imports
import hou


# =============================================================================
# CLASSES
# =============================================================================

class Test_clear_generic_text_badge(unittest.TestCase):
    """Test ht.nodes.badges.clear_generic_text_badge."""

    @patch("ht.nodes.badges.clear_generic_text_badge_color")
    @patch("ht.nodes.badges._ht_generic_text_badge.get_generic_text_key")
    @patch("ht.nodes.badges.hou.undos.disabler")
    def test_no_data(self, mock_disabler, mock_data_name, mock_clear_color):
        mock_node = MagicMock(spec=hou.Node)

        def raise_error(*args, **kwargs):
            raise hou.OperationFailed()

        mock_node.destroyUserData.side_effect = raise_error

        badges.clear_generic_text_badge(mock_node)

        self.assertEqual(mock_disabler.call_count, 1)
        mock_node.destroyUserData.assert_called_with(mock_data_name.return_value)
        self.assertEqual(mock_clear_color.call_count, 1)

    @patch("ht.nodes.badges.clear_generic_text_badge_color")
    @patch("ht.nodes.badges._ht_generic_text_badge.get_generic_text_key")
    @patch("ht.nodes.badges.hou.undos.disabler")
    def test(self, mock_disabler, mock_data_name, mock_clear_color):
        mock_node = MagicMock(spec=hou.Node)

        badges.clear_generic_text_badge(mock_node)

        self.assertEqual(mock_disabler.call_count, 1)
        mock_node.destroyUserData.assert_called_with(mock_data_name.return_value)
        self.assertEqual(mock_clear_color.call_count, 1)


class Test_clear_generic_text_badge_color(unittest.TestCase):
    """Test ht.nodes.badges.clear_generic_text_badge_color."""

    @patch("ht.nodes.badges._ht_generic_text_badge.get_generic_text_color_key")
    @patch("ht.nodes.badges.hou.undos.disabler")
    def test_no_data(self, mock_disabler, mock_data_name):
        mock_node = MagicMock(spec=hou.Node)

        def raise_error(*args, **kwargs):
            raise hou.OperationFailed()

        mock_node.destroyUserData.side_effect = raise_error

        badges.clear_generic_text_badge_color(mock_node)

        self.assertEqual(mock_disabler.call_count, 1)
        mock_node.destroyUserData.assert_called_with(mock_data_name.return_value)

    @patch("ht.nodes.badges._ht_generic_text_badge.get_generic_text_color_key")
    @patch("ht.nodes.badges.hou.undos.disabler")
    def test(self, mock_disabler, mock_data_name):
        mock_node = MagicMock(spec=hou.Node)

        badges.clear_generic_text_badge_color(mock_node)

        self.assertEqual(mock_disabler.call_count, 1)
        mock_node.destroyUserData.assert_called_with(mock_data_name.return_value)


class Test_set_generic_text_badge(unittest.TestCase):
    """Test ht.nodes.badges.set_generic_text_badge."""

    @patch("ht.nodes.badges.set_generic_text_badge_color")
    @patch("ht.nodes.badges._ht_generic_text_badge.get_generic_text_key")
    @patch("ht.nodes.badges.hou.undos.disabler")
    def test_no_color(self, mock_disabler, mock_data_name, mock_set_color):
        mock_node = MagicMock(spec=hou.Node)

        badges.set_generic_text_badge(mock_node, "some value")

        self.assertEqual(mock_disabler.call_count, 1)
        mock_node.setUserData.assert_called_with(
            mock_data_name.return_value,
            "some value"
        )

        self.assertEqual(mock_set_color.call_count, 0)

    @patch("ht.nodes.badges.set_generic_text_badge_color")
    @patch("ht.nodes.badges._ht_generic_text_badge.get_generic_text_key")
    @patch("ht.nodes.badges.hou.undos.disabler")
    def test_color(self, mock_disabler, mock_data_name, mock_set_color):
        mock_color = MagicMock(spec=hou.Color)

        mock_node = MagicMock(spec=hou.Node)

        badges.set_generic_text_badge(mock_node, "some value", mock_color)

        self.assertEqual(mock_disabler.call_count, 1)
        mock_node.setUserData.assert_called_with(
            mock_data_name.return_value,
            "some value"
        )

        mock_set_color.assert_called_with(mock_node, mock_color)


class Test_set_generic_text_badge_color(unittest.TestCase):
    """Test ht.nodes.badges.set_generic_text_badge_color."""

    @patch("ht.nodes.badges._ht_generic_text_badge.get_generic_text_color_key")
    @patch("ht.nodes.badges.hou.undos.disabler")
    def test_no_color(self, mock_disabler, mock_data_name):
        mock_node = MagicMock(spec=hou.Node)

        mock_color = MagicMock(spec=hou.Color)
        mock_color.rgb.return_value = (0.1, 0.2, 0.3)

        badges.set_generic_text_badge_color(mock_node, mock_color)

        self.assertEqual(mock_disabler.call_count, 1)
        mock_node.setUserData.assert_called_with(
            mock_data_name.return_value,
            "rgb 0.1 0.2 0.3"
        )

# =============================================================================

if __name__ == '__main__':
    unittest.main()
