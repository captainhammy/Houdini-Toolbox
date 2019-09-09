"""Test the ht.pyfilter.operations.logoutput module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Third Party Imports
from mock import MagicMock, call, patch
import pytest

# Houdini Toolbox Imports
from ht.pyfilter.operations import logoutput


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def patch_logger():
    """Mock the module logger."""
    with patch("ht.pyfilter.operations.logoutput._logger", autospec=True) as mock_logger:
        yield mock_logger


# =============================================================================
# CLASSES
# =============================================================================

class Test_LogOutput(object):
    """Test the ht.pyfilter.operations.logoutput.LogOutput object."""

    # Methods

    @patch.object(logoutput.LogOutput, "__init__", lambda x, y: None)
    def test_filter_error__level_0(self, patch_logger):
        level = 0

        mock_message1 = MagicMock(spec=str)
        mock_message2 = MagicMock(spec=str)

        mock_message = MagicMock(spec=str)
        mock_message.split.return_value = [mock_message1, mock_message2]

        mock_prefix = MagicMock(spec=str)

        op = logoutput.LogOutput(None)

        result = op.filter_error(level, mock_message, mock_prefix)

        assert result

        mock_message.split.assert_called_with('\n')

        patch_logger.error.assert_has_calls(
            [call(mock_message1), call(mock_message2)]
        )

    @patch.object(logoutput.LogOutput, "__init__", lambda x, y: None)
    def test_filter_error__prefix(self, patch_logger):
        level = 1

        mock_message = MagicMock(spec=str)
        mock_message.split.return_value = [mock_message]

        mock_prefix = MagicMock(spec=str)
        mock_prefix.__len__.return_value = 1

        op = logoutput.LogOutput(None)

        result = op.filter_error(level, mock_message, mock_prefix)

        assert result

        mock_message.split.assert_called_with('\n')

        patch_logger.warning.assert_called_with(mock_message)

    @patch.object(logoutput.LogOutput, "__init__", lambda x, y: None)
    def test_filter_error__level_1(self, patch_logger):
        level = 1

        mock_message = MagicMock(spec=str)
        mock_message.split.return_value = [mock_message]

        mock_prefix = MagicMock(spec=str)

        op = logoutput.LogOutput(None)

        result = op.filter_error(level, mock_message, mock_prefix)

        assert result

        mock_message.split.assert_called_with('\n')

        patch_logger.info.assert_called_with(mock_message)

    @patch.object(logoutput.LogOutput, "__init__", lambda x, y: None)
    def test_filter_error__debug(self, patch_logger):
        level = MagicMock(spec=int)

        mock_message = MagicMock(spec=str)
        mock_message.split.return_value = [mock_message]

        mock_prefix = MagicMock(spec=str)

        op = logoutput.LogOutput(None)

        result = op.filter_error(level, mock_message, mock_prefix)

        assert result

        mock_message.split.assert_called_with('\n')

        patch_logger.debug.assert_called_with(mock_message)
