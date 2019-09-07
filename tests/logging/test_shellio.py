"""Tests for ht.logging.shellio module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import imp
import io
import logging

# Third Party Imports
from mock import MagicMock, call, patch
import pytest

# Houdini Toolbox Imports
import ht.logging.shellio

# Houdini Imports
import hou

# Reload the module to test to capture load evaluation since it has already
# been loaded.
imp.reload(ht.logging.shellio)


# =============================================================================
# CLASSES
# =============================================================================

class Test_PythonShellHandler(object):
    """Test ht.logging.shellio.PythonShellHandler object."""

    @patch.object(ht.logging.shellio.PythonShellHandler, "format")
    @patch.object(ht.logging.shellio.PythonShellHandler, "__init__", lambda x, y: None)
    def test_emit__shellio(self, mock_format):
        """Test when sys.stdout is an instance of hou.ShellIO."""
        mock_message = MagicMock(spec=str)

        mock_format.return_value = mock_message

        mock_record = MagicMock(spec=logging.LogRecord)
        inst = ht.logging.shellio.PythonShellHandler(None)

        with patch("sys.stdout", spec=hou.ShellIO) as mock_stream:
            inst.emit(mock_record)

        mock_format.assert_called_with(mock_record)

        calls = [call(mock_format.return_value), call('\n')]

        mock_stream.write.assert_has_calls(calls)
        mock_stream.flush.assert_called()

    @patch.object(ht.logging.shellio.PythonShellHandler, "format")
    @patch.object(ht.logging.shellio.PythonShellHandler, "__init__", lambda x, y: None)
    def test_emit__not_shellio(self, mock_format):
        """Test when sys.stdout is not an instance of hou.ShellIO."""
        mock_message = MagicMock(spec=str)

        mock_format.return_value = mock_message

        mock_record = MagicMock(spec=logging.LogRecord)
        inst = ht.logging.shellio.PythonShellHandler(None)

        with patch("sys.stdout", spec=io.StringIO) as mock_stream:
            inst.emit(mock_record)

        mock_format.assert_called_with(mock_record)

        calls = [call(mock_format.return_value), call('\n')]

        mock_stream.write.assert_not_called()

    @patch.object(ht.logging.shellio.PythonShellHandler, "format")
    @patch.object(ht.logging.shellio.PythonShellHandler, "__init__", lambda x, y: None)
    def test_emit__keyboardinterrupt(self, mock_format):
        """Test when KeyboardInterrupt is raised."""
        mock_format.side_effect = KeyboardInterrupt

        mock_record = MagicMock(spec=logging.LogRecord)
        inst = ht.logging.shellio.PythonShellHandler(None)

        with pytest.raises(KeyboardInterrupt):
            inst.emit(mock_record)

        mock_format.assert_called_with(mock_record)

    @patch.object(ht.logging.shellio.PythonShellHandler, "format")
    @patch.object(ht.logging.shellio.PythonShellHandler, "__init__", lambda x, y: None)
    def test_emit__systemexit(self, mock_format):
        """Test when SystemExit is raised."""
        mock_format.side_effect = SystemExit

        mock_record = MagicMock(spec=logging.LogRecord)
        inst = ht.logging.shellio.PythonShellHandler(None)

        with pytest.raises(SystemExit):
            inst.emit(mock_record)

        mock_format.assert_called_with(mock_record)

    @patch.object(ht.logging.shellio.PythonShellHandler, "handleError")
    @patch.object(ht.logging.shellio.PythonShellHandler, "format")
    @patch.object(ht.logging.shellio.PythonShellHandler, "__init__", lambda x, y: None)
    def test_emit__generic_exception(self, mock_format, mock_handle):
        """Test when an generic exception is raised."""
        mock_format.side_effect = Exception

        mock_record = MagicMock(spec=logging.LogRecord)
        inst = ht.logging.shellio.PythonShellHandler(None)

        inst.emit(mock_record)

        mock_format.assert_called_with(mock_record)
        mock_handle.assert_called_with(mock_record)
