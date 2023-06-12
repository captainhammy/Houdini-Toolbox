"""Test the houdini_toolbox.utils module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Third Party
import pytest

# Houdini Toolbox
from houdini_toolbox import utils

# Houdini
import hou

# =============================================================================
# TESTS
# =============================================================================


def test_restore_update_mode(mocker, mock_hou_ui):
    """Test houdini_toolbox.utils.restore_update_mode.

    Since we're using 'finally' we'll throw an exception inside the code to ensure
    that the mode gets restored.

    """
    mock_setting = mocker.patch("hou.updateModeSetting")

    mock_value = mocker.MagicMock(spec=hou.updateMode)

    with pytest.raises(RuntimeError), utils.restore_update_mode(mock_value):
        raise RuntimeError()

    mock_hou_ui.setUpdateMode.assert_has_calls(
        [mocker.call(mock_value), mocker.call(mock_setting.return_value)]
    )


class Test_timer:
    """Test houdini_toolbox.utils.timer."""

    def test_label(self, mocker):
        """Test passing a label."""
        mock_start = mocker.MagicMock(spec=float)
        mock_end = mocker.MagicMock(spec=float)

        mocker.patch("time.time", side_effect=(mock_start, mock_end))

        mock_logger = mocker.patch("houdini_toolbox.utils._logger")

        mock_label = mocker.MagicMock(spec=str)

        with pytest.raises(RuntimeError), utils.timer(mock_label):
            raise RuntimeError()

        mock_logger.info.assert_called_with(
            "%s - %s", mock_label, mock_end - mock_start
        )

    def test_no_label(self, mocker):
        """Test with no label."""
        mock_start = mocker.MagicMock(spec=float)
        mock_end = mocker.MagicMock(spec=float)

        mocker.patch("time.time", side_effect=(mock_start, mock_end))

        mock_logger = mocker.patch("houdini_toolbox.utils._logger")

        with pytest.raises(RuntimeError), utils.timer():
            raise RuntimeError()

        mock_logger.info.assert_called_with(mock_end - mock_start)
