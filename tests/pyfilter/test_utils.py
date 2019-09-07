"""Test the ht.pyfilter.utils module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Third Party Imports
from mock import MagicMock, patch
import pytest

# Houdini Toolbox Imports
from ht.pyfilter import utils

# Houdini Imports
import hou


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def patch_hou():
    """Mock importing of the hou module."""
    mock_hou = MagicMock()
    mock_hou.OperationFailed = hou.OperationFailed

    modules = {
        "hou": mock_hou,
    }

    patcher = patch.dict("sys.modules", modules)
    patcher.start()

    yield mock_hou

    patcher.stop()


# =============================================================================
# CLASSES
# =============================================================================

class Test_build_pyfilter_command(object):
    """Test ht.pyfilter.utils.build_pyfilter_command"""

    @patch("os.path.exists")
    @patch("ht.pyfilter.utils._logger")
    def test_no_found_script(self, mock_logger, mock_exists, patch_hou):
        def raise_error(*args, **kwargs):
            raise hou.OperationFailed()

        patch_hou.findFile.side_effect = raise_error

        result = utils.build_pyfilter_command()

        assert result == ""

        mock_logger.error.assert_called()

        mock_exists.assert_not_called()

    @patch("os.path.exists")
    def test_found_script_does_not_exists(self, mock_exists, patch_hou):
        mock_exists.return_value = False

        with pytest.raises(OSError):
            utils.build_pyfilter_command()

        mock_exists.assert_called_with(patch_hou.findFile.return_value)

    @patch("os.path.exists")
    def test_found_script_no_args(self, mock_exists, patch_hou):
        mock_exists.return_value = True

        result = utils.build_pyfilter_command()

        assert result == '-P "{} "'.format(patch_hou.findFile.return_value)

    @patch("os.path.exists")
    def test_manual_path(self, mock_exists, patch_hou):
        mock_exists.return_value = True

        mock_path = MagicMock()

        result = utils.build_pyfilter_command(pyfilter_path=mock_path)

        assert result == '-P "{} "'.format(mock_path)

        patch_hou.findFile.assert_not_called()
        mock_exists.assert_called_with(mock_path)

    @patch("os.path.exists")
    def test_manual_path_args(self, mock_exists, patch_hou):
        mock_exists.return_value = True

        mock_path = MagicMock()

        args = ["-arg1=1", "-arg2"]

        result = utils.build_pyfilter_command(pyfilter_args=args, pyfilter_path=mock_path)

        assert result == '-P "{} {}"'.format(mock_path, " ".join(args))

        patch_hou.findFile.assert_not_called()
        mock_exists.assert_called_with(mock_path)
