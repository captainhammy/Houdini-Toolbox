"""Tests for ht.nodes.badges module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Third Party Imports
from mock import MagicMock, patch

# Houdini Toolbox Imports
from ht.nodes import badges

# Houdini Imports
import hou


# =============================================================================
# CLASSES
# =============================================================================

class Test_clear_generic_image_badge(object):
    """Test ht.nodes.badges.clear_generic_image_badge."""

    @patch("ht.nodes.badges._ht_generic_image_badge.get_generic_image_key")
    @patch("ht.nodes.badges.hou.undos.disabler")
    def test_no_data(self, mock_disabler, mock_data_name, raise_hou_operationfailed):
        mock_node = MagicMock(spec=hou.Node)

        mock_node.destroyUserData.side_effect = raise_hou_operationfailed

        badges.clear_generic_image_badge(mock_node)

        mock_disabler.assert_called()

        mock_node.destroyUserData.assert_called_with(mock_data_name.return_value)

    @patch("ht.nodes.badges._ht_generic_image_badge.get_generic_image_key")
    @patch("ht.nodes.badges.hou.undos.disabler")
    def test(self, mock_disabler, mock_data_name):
        mock_node = MagicMock(spec=hou.Node)

        badges.clear_generic_image_badge(mock_node)

        mock_disabler.assert_called()

        mock_node.destroyUserData.assert_called_with(mock_data_name.return_value)


class Test_clear_generic_text_badge(object):
    """Test ht.nodes.badges.clear_generic_text_badge."""

    @patch("ht.nodes.badges.clear_generic_text_badge_color")
    @patch("ht.nodes.badges._ht_generic_text_badge.get_generic_text_key")
    @patch("ht.nodes.badges.hou.undos.disabler")
    def test_no_data(self, mock_disabler, mock_data_name, mock_clear_color, raise_hou_operationfailed):
        mock_node = MagicMock(spec=hou.Node)

        mock_node.destroyUserData.side_effect = raise_hou_operationfailed

        badges.clear_generic_text_badge(mock_node)

        mock_disabler.assert_called()

        mock_node.destroyUserData.assert_called_with(mock_data_name.return_value)

        mock_clear_color.assert_called()

    @patch("ht.nodes.badges.clear_generic_text_badge_color")
    @patch("ht.nodes.badges._ht_generic_text_badge.get_generic_text_key")
    @patch("ht.nodes.badges.hou.undos.disabler")
    def test(self, mock_disabler, mock_data_name, mock_clear_color):
        mock_node = MagicMock(spec=hou.Node)

        badges.clear_generic_text_badge(mock_node)

        mock_disabler.assert_called()

        mock_node.destroyUserData.assert_called_with(mock_data_name.return_value)

        mock_clear_color.assert_called()


class Test_clear_generic_text_badge_color(object):
    """Test ht.nodes.badges.clear_generic_text_badge_color."""

    @patch("ht.nodes.badges._ht_generic_text_badge.get_generic_text_color_key")
    @patch("ht.nodes.badges.hou.undos.disabler")
    def test_no_data(self, mock_disabler, mock_data_name, raise_hou_operationfailed):
        mock_node = MagicMock(spec=hou.Node)

        mock_node.destroyUserData.side_effect = raise_hou_operationfailed

        badges.clear_generic_text_badge_color(mock_node)

        mock_disabler.assert_called()

        mock_node.destroyUserData.assert_called_with(mock_data_name.return_value)

    @patch("ht.nodes.badges._ht_generic_text_badge.get_generic_text_color_key")
    @patch("ht.nodes.badges.hou.undos.disabler")
    def test(self, mock_disabler, mock_data_name):
        mock_node = MagicMock(spec=hou.Node)

        badges.clear_generic_text_badge_color(mock_node)

        mock_disabler.assert_called()
        mock_node.destroyUserData.assert_called_with(mock_data_name.return_value)


class Test_set_generic_image_badge(object):
    """Test ht.nodes.badges.set_generic_image_badge."""

    @patch("ht.nodes.badges._ht_generic_image_badge.get_generic_image_key")
    @patch("ht.nodes.badges.hou.undos.disabler")
    def test(self, mock_disabler, mock_data_name):
        mock_node = MagicMock(spec=hou.Node)
        mock_value = MagicMock(spec=str)

        badges.set_generic_image_badge(mock_node, mock_value)

        mock_disabler.assert_called()

        mock_node.setUserData.assert_called_with(
            mock_data_name.return_value,
            mock_value
        )


class Test_set_generic_text_badge(object):
    """Test ht.nodes.badges.set_generic_text_badge."""

    @patch("ht.nodes.badges.set_generic_text_badge_color")
    @patch("ht.nodes.badges._ht_generic_text_badge.get_generic_text_key")
    @patch("ht.nodes.badges.hou.undos.disabler")
    def test_no_color(self, mock_disabler, mock_data_name, mock_set_color):
        mock_node = MagicMock(spec=hou.Node)
        mock_value = MagicMock(spec=str)

        badges.set_generic_text_badge(mock_node, mock_value)

        mock_disabler.assert_called()

        mock_node.setUserData.assert_called_with(
            mock_data_name.return_value,
            mock_value
        )

        mock_set_color.assert_not_called()

    @patch("ht.nodes.badges.set_generic_text_badge_color")
    @patch("ht.nodes.badges._ht_generic_text_badge.get_generic_text_key")
    @patch("ht.nodes.badges.hou.undos.disabler")
    def test_color(self, mock_disabler, mock_data_name, mock_set_color):
        mock_color = MagicMock(spec=hou.Color)
        mock_value = MagicMock(spec=str)
        mock_node = MagicMock(spec=hou.Node)

        badges.set_generic_text_badge(mock_node, mock_value, mock_color)

        mock_disabler.assert_called()

        mock_node.setUserData.assert_called_with(
            mock_data_name.return_value,
            mock_value
        )

        mock_set_color.assert_called_with(mock_node, mock_color)


class Test_set_generic_text_badge_color(object):
    """Test ht.nodes.badges.set_generic_text_badge_color."""

    @patch("ht.nodes.badges._ht_generic_text_badge.get_generic_text_color_key")
    @patch("ht.nodes.badges.hou.undos.disabler")
    def test_no_color(self, mock_disabler, mock_data_name):
        mock_node = MagicMock(spec=hou.Node)

        mock_color = MagicMock(spec=hou.Color)
        mock_color.rgb.return_value = (0.1, 0.2, 0.3)

        badges.set_generic_text_badge_color(mock_node, mock_color)

        mock_disabler.assert_called()

        mock_node.setUserData.assert_called_with(
            mock_data_name.return_value,
            "rgb 0.1 0.2 0.3"
        )
