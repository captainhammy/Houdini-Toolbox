"""Tests for houdini_toolbox.nodes.badges module."""
# flake8: noqa
# =============================================================================
# IMPORTS
# =============================================================================

# Third Party
import pytest

# Houdini
import hou

badges = pytest.importorskip("houdini_toolbox.nodes.badges")


# =============================================================================
# TESTS
# =============================================================================


class Test_clear_generic_image_badge:
    """Test houdini_toolbox.nodes.badges.clear_generic_image_badge."""

    def test_no_data(self, mocker):
        """Test when there is no user data to remove."""
        mock_disabler = mocker.patch("hou.undos.disabler")
        mock_data_name = mocker.patch(
            "houdini_toolbox.nodes.badges._ht_generic_image_badge.get_generic_image_key"
        )

        mock_node = mocker.MagicMock(spec=hou.Node)

        mock_node.destroyUserData.side_effect = hou.OperationFailed

        badges.clear_generic_image_badge(mock_node)

        mock_disabler.assert_called()

        mock_node.destroyUserData.assert_called_with(mock_data_name.return_value)

    def test(self, mocker):
        """Test when there is user data to remove."""
        mock_disabler = mocker.patch("hou.undos.disabler")
        mock_data_name = mocker.patch(
            "houdini_toolbox.nodes.badges._ht_generic_image_badge.get_generic_image_key"
        )

        mock_node = mocker.MagicMock(spec=hou.Node)

        badges.clear_generic_image_badge(mock_node)

        mock_disabler.assert_called()

        mock_node.destroyUserData.assert_called_with(mock_data_name.return_value)


class Test_clear_generic_text_badge:
    """Test houdini_toolbox.nodes.badges.clear_generic_text_badge."""

    def test_no_data(self, mocker):
        """Test when there is no user data to remove."""
        mock_disabler = mocker.patch("hou.undos.disabler")
        mock_data_name = mocker.patch(
            "houdini_toolbox.nodes.badges._ht_generic_text_badge.get_generic_text_key"
        )
        mock_clear_color = mocker.patch(
            "houdini_toolbox.nodes.badges.clear_generic_text_badge_color"
        )

        mock_node = mocker.MagicMock(spec=hou.Node)

        mock_node.destroyUserData.side_effect = hou.OperationFailed

        badges.clear_generic_text_badge(mock_node)

        mock_disabler.assert_called()

        mock_node.destroyUserData.assert_called_with(mock_data_name.return_value)

        mock_clear_color.assert_called()

    def test(self, mocker):
        """Test when there is user data to remove."""
        mock_disabler = mocker.patch("hou.undos.disabler")
        mock_data_name = mocker.patch(
            "houdini_toolbox.nodes.badges._ht_generic_text_badge.get_generic_text_key"
        )
        mock_clear_color = mocker.patch(
            "houdini_toolbox.nodes.badges.clear_generic_text_badge_color"
        )

        mock_node = mocker.MagicMock(spec=hou.Node)

        badges.clear_generic_text_badge(mock_node)

        mock_disabler.assert_called()

        mock_node.destroyUserData.assert_called_with(mock_data_name.return_value)

        mock_clear_color.assert_called()


class Test_clear_generic_text_badge_color:
    """Test houdini_toolbox.nodes.badges.clear_generic_text_badge_color."""

    def test_no_data(self, mocker):
        """Test when there is no user data to remove."""
        mock_disabler = mocker.patch("hou.undos.disabler")
        mock_data_name = mocker.patch(
            "houdini_toolbox.nodes.badges._ht_generic_text_badge.get_generic_text_color_key"
        )

        mock_node = mocker.MagicMock(spec=hou.Node)

        mock_node.destroyUserData.side_effect = hou.OperationFailed

        badges.clear_generic_text_badge_color(mock_node)

        mock_disabler.assert_called()

        mock_node.destroyUserData.assert_called_with(mock_data_name.return_value)

    def test(self, mocker):
        """Test when there is user data to remove."""
        mock_disabler = mocker.patch("hou.undos.disabler")
        mock_data_name = mocker.patch(
            "houdini_toolbox.nodes.badges._ht_generic_text_badge.get_generic_text_color_key"
        )

        mock_node = mocker.MagicMock(spec=hou.Node)

        badges.clear_generic_text_badge_color(mock_node)

        mock_disabler.assert_called()
        mock_node.destroyUserData.assert_called_with(mock_data_name.return_value)


def test_set_generic_image_badge(mocker):
    """Test houdini_toolbox.nodes.badges.set_generic_image_badge."""
    mock_disabler = mocker.patch("hou.undos.disabler")
    mock_data_name = mocker.patch(
        "houdini_toolbox.nodes.badges._ht_generic_image_badge.get_generic_image_key"
    )

    mock_node = mocker.MagicMock(spec=hou.Node)
    mock_value = mocker.MagicMock(spec=str)

    badges.set_generic_image_badge(mock_node, mock_value)

    mock_disabler.assert_called()

    mock_node.setUserData.assert_called_with(mock_data_name.return_value, mock_value)


class Test_set_generic_text_badge:
    """Test houdini_toolbox.nodes.badges.set_generic_text_badge."""

    def test_no_color(self, mocker):
        """Test not passing a color."""
        mock_disabler = mocker.patch("hou.undos.disabler")
        mock_data_name = mocker.patch(
            "houdini_toolbox.nodes.badges._ht_generic_text_badge.get_generic_text_key"
        )
        mock_set_color = mocker.patch(
            "houdini_toolbox.nodes.badges.set_generic_text_badge_color"
        )

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_value = mocker.MagicMock(spec=str)

        badges.set_generic_text_badge(mock_node, mock_value)

        mock_disabler.assert_called()

        mock_node.setUserData.assert_called_with(
            mock_data_name.return_value, mock_value
        )

        mock_set_color.assert_not_called()

    def test_color(self, mocker):
        """Test passing a color."""
        mock_disabler = mocker.patch("hou.undos.disabler")
        mock_data_name = mocker.patch(
            "houdini_toolbox.nodes.badges._ht_generic_text_badge.get_generic_text_key"
        )
        mock_set_color = mocker.patch(
            "houdini_toolbox.nodes.badges.set_generic_text_badge_color"
        )

        mock_color = mocker.MagicMock(spec=hou.Color)
        mock_value = mocker.MagicMock(spec=str)
        mock_node = mocker.MagicMock(spec=hou.Node)

        badges.set_generic_text_badge(mock_node, mock_value, mock_color)

        mock_disabler.assert_called()

        mock_node.setUserData.assert_called_with(
            mock_data_name.return_value, mock_value
        )

        mock_set_color.assert_called_with(mock_node, mock_color)


def test_set_generic_text_badge_color(mocker):
    """Test houdini_toolbox.nodes.badges.set_generic_text_badge_color."""
    mock_disabler = mocker.patch("hou.undos.disabler")
    mock_data_name = mocker.patch(
        "houdini_toolbox.nodes.badges._ht_generic_text_badge.get_generic_text_color_key"
    )

    mock_node = mocker.MagicMock(spec=hou.Node)

    mock_color = mocker.MagicMock(spec=hou.Color)
    mock_color.rgb.return_value = (0.1, 0.2, 0.3)

    badges.set_generic_text_badge_color(mock_node, mock_color)

    mock_disabler.assert_called()

    mock_node.setUserData.assert_called_with(
        mock_data_name.return_value, "rgb 0.1 0.2 0.3"
    )
