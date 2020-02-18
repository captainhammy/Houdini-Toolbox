"""Test the ht.pyfilter.utils module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Third Party Imports
import pytest

# Houdini Toolbox Imports
from ht.pyfilter import utils

# Houdini Imports
import hou

# =============================================================================
# TESTS
# =============================================================================


class Test_build_pyfilter_command(object):
    """Test ht.pyfilter.utils.build_pyfilter_command"""

    def test_no_found_script(self, mocker, fix_hou_exceptions):
        mock_find = mocker.patch("hou.findFile", side_effect=hou.OperationFailed)
        mock_logger = mocker.patch("ht.pyfilter.utils._logger")
        mock_isfile = mocker.patch("os.path.isfile")

        result = utils.build_pyfilter_command()

        assert result == ""

        mock_find.assert_called_with("pyfilter/ht-pyfilter.py")

        mock_logger.error.assert_called()

        mock_isfile.assert_not_called()

    def test_found_script_does_not_exists(self, mocker):
        mock_find = mocker.patch("hou.findFile")
        mock_isfile = mocker.patch("os.path.isfile", return_value=False)

        with pytest.raises(OSError):
            utils.build_pyfilter_command()

        mock_isfile.assert_called_with(mock_find.return_value)

    def test_found_script_no_args(self, mocker):
        mock_find = mocker.patch("hou.findFile")
        mock_isfile = mocker.patch("os.path.isfile", return_value=True)

        result = utils.build_pyfilter_command()

        assert result == '-P "{} "'.format(mock_find.return_value)

        mock_isfile.assert_called_with(mock_find.return_value)

    def test_manual_path(self, mocker):
        mock_find = mocker.patch("hou.findFile")
        mock_isfile = mocker.patch("os.path.isfile", return_value=True)

        mock_path = mocker.MagicMock()

        result = utils.build_pyfilter_command(pyfilter_path=mock_path)

        assert result == '-P "{} "'.format(mock_path)

        mock_find.return_value.assert_not_called()
        mock_isfile.assert_called_with(mock_path)

    def test_manual_path_args(self, mocker):
        mock_find = mocker.patch("hou.findFile")
        mock_isfile = mocker.patch("os.path.isfile", return_value=True)

        mock_path = mocker.MagicMock()

        args = ["-arg1=1", "-arg2"]

        result = utils.build_pyfilter_command(
            pyfilter_args=args, pyfilter_path=mock_path
        )

        assert result == '-P "{} {}"'.format(mock_path, " ".join(args))

        mock_find.return_value.assert_not_called()
        mock_isfile.assert_called_with(mock_path)
