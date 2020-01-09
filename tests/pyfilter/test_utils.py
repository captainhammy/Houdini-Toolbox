"""Test the ht.pyfilter.utils module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Third Party Imports
import pytest

# Houdini Toolbox Imports
from ht.pyfilter import utils


# =============================================================================
# CLASSES
# =============================================================================

class Test_build_pyfilter_command(object):
    """Test ht.pyfilter.utils.build_pyfilter_command"""

    def test_no_found_script(self, mocker, patch_hou, mock_hou_exceptions):
        mock_logger = mocker.patch("ht.pyfilter.utils._logger")
        mock_exists = mocker.patch("os.path.exists")

        patch_hou.hou.findFile.side_effect = mock_hou_exceptions.OperationFailed

        result = utils.build_pyfilter_command()

        assert result == ""

        mock_logger.error.assert_called()

        mock_exists.assert_not_called()

    def test_found_script_does_not_exists(self, mocker, patch_hou):
        mock_exists = mocker.patch("os.path.exists", return_value=False)

        with pytest.raises(OSError):
            utils.build_pyfilter_command()

        mock_exists.assert_called_with(patch_hou.hou.findFile.return_value)

    def test_found_script_no_args(self, mocker, patch_hou):
        mock_exists = mocker.patch("os.path.exists", return_value=True)

        result = utils.build_pyfilter_command()

        assert result == '-P "{} "'.format(patch_hou.hou.findFile.return_value)

        mock_exists.assert_called_with(patch_hou.hou.findFile.return_value)

    def test_manual_path(self, mocker, patch_hou):
        mock_exists = mocker.patch("os.path.exists", return_value=True)

        mock_path = mocker.MagicMock()

        result = utils.build_pyfilter_command(pyfilter_path=mock_path)

        assert result == '-P "{} "'.format(mock_path)

        patch_hou.hou.findFile.assert_not_called()
        mock_exists.assert_called_with(mock_path)

    def test_manual_path_args(self, mocker, patch_hou):
        mock_exists = mocker.patch("os.path.exists", return_value=True)

        mock_path = mocker.MagicMock()

        args = ["-arg1=1", "-arg2"]

        result = utils.build_pyfilter_command(pyfilter_args=args, pyfilter_path=mock_path)

        assert result == '-P "{} {}"'.format(mock_path, " ".join(args))

        patch_hou.hou.findFile.assert_not_called()
        mock_exists.assert_called_with(mock_path)
