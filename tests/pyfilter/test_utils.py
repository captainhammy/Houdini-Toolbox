"""Test the ht.pyfilter.utils module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
from mock import MagicMock, patch
import unittest

# Houdini Toolbox Imports
from ht.pyfilter import utils

# Houdini Imports
import hou

reload(utils)

# =============================================================================
# CLASSES
# =============================================================================

class Test_build_pyfilter_command(unittest.TestCase):
    """Test ht.pyfilter.utils.build_pyfilter_command"""

    @patch("os.path.exists")
    @patch("ht.pyfilter.utils.logger")
    def test_no_found_script(self, mock_logger, mock_exists):
        def raise_error(*args, **kwargs):
            raise hou.OperationFailed()

        mock_hou = MagicMock()
        mock_hou.findFile.side_effect = raise_error
        mock_hou.OperationFailed = hou.OperationFailed

        modules = {"hou": mock_hou}

        with patch.dict("sys.modules", modules):
            result = utils.build_pyfilter_command()

        self.assertEqual(result, "")

        mock_logger.error.assert_called()

        mock_exists.assert_not_called()

    @patch("os.path.exists")
    def test_found_script_does_not_exists(self, mock_exists):
        mock_exists.return_value = False
        mock_hou = MagicMock()

        modules = {"hou": mock_hou}

        with patch.dict("sys.modules", modules):
            with self.assertRaises(OSError):
                utils.build_pyfilter_command()

        mock_exists.assert_called_with(mock_hou.findFile.return_value)

    @patch("os.path.exists")
    def test_found_script_no_args(self, mock_exists):
        mock_exists.return_value = True

        path = "/path/to/pyfilter.py"

        mock_hou = MagicMock()
        mock_hou.findFile.return_value = path

        modules = {"hou": mock_hou}

        with patch.dict("sys.modules", modules):
            result = utils.build_pyfilter_command()

        self.assertEqual(
            result,
            '-P "{} "'.format(path)
        )

    @patch("os.path.exists")
    def test_manual_path(self, mock_exists):
        mock_exists.return_value = True

        path = "/path/to/pyfilter.py"

        mock_hou = MagicMock()

        modules = {"hou": mock_hou}

        with patch.dict("sys.modules", modules):
            result = utils.build_pyfilter_command(pyfilter_path=path)

        self.assertEqual(
            result,
            '-P "{} "'.format(path)
        )

        mock_hou.findFile.assert_not_called()
        mock_exists.assert_called_with(path)

    @patch("os.path.exists")
    def test_manual_path_args(self, mock_exists):
        mock_exists.return_value = True

        path = "/path/to/pyfilter.py"

        mock_hou = MagicMock()

        modules = {"hou": mock_hou}

        args = ["-arg1=1", "-arg2"]

        with patch.dict("sys.modules", modules):
            result = utils.build_pyfilter_command(pyfilter_args=args, pyfilter_path=path)

        self.assertEqual(
            result,
            '-P "{} {}"'.format(path, " ".join(args))
        )

        mock_hou.findFile.assert_not_called()
        mock_exists.assert_called_with(path)

# =============================================================================

if __name__ == '__main__':
    unittest.main()
