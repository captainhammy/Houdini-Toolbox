"""Test the ht.pyfilter.operations.logoutput module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Third Party Imports
from mock import MagicMock, call, patch

# Houdini Toolbox Imports
from ht.pyfilter.operations import logoutput


# =============================================================================
# CLASSES
# =============================================================================

class Test_LogOutput(object):
    """Test the ht.pyfilter.operations.logoutput.LogOutput object."""

    # Methods

    @patch("ht.pyfilter.operations.logoutput._logger", autospec=True)
    @patch.object(logoutput.LogOutput, "__init__", lambda x, y: None)
    def test_filter_error__level_0(self, mock_logger):
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

        mock_logger.error.assert_has_calls(
            [call(mock_message1), call(mock_message2)]
        )

    @patch("ht.pyfilter.operations.logoutput._logger", autospec=True)
    @patch.object(logoutput.LogOutput, "__init__", lambda x, y: None)
    def test_filter_error__prefix(self, mock_logger):
        level = 1

        mock_message = MagicMock(spec=str)
        mock_message.split.return_value = [mock_message]

        mock_prefix = MagicMock(spec=str)
        mock_prefix.__len__.return_value = 1

        op = logoutput.LogOutput(None)

        result = op.filter_error(level, mock_message, mock_prefix)

        assert result

        mock_message.split.assert_called_with('\n')

        mock_logger.warning.assert_called_with(mock_message)

    @patch("ht.pyfilter.operations.logoutput._logger", autospec=True)
    @patch.object(logoutput.LogOutput, "__init__", lambda x, y: None)
    def test_filter_error__level_1(self, mock_logger):
        level = 1

        mock_message = MagicMock(spec=str)
        mock_message.split.return_value = [mock_message]

        mock_prefix = MagicMock(spec=str)

        op = logoutput.LogOutput(None)

        result = op.filter_error(level, mock_message, mock_prefix)

        assert result

        mock_message.split.assert_called_with('\n')

        mock_logger.info.assert_called_with(mock_message)

    @patch("ht.pyfilter.operations.logoutput._logger", autospec=True)
    @patch.object(logoutput.LogOutput, "__init__", lambda x, y: None)
    def test_filter_error__debug(self, mock_logger):
        level = MagicMock(spec=int)

        mock_message = MagicMock(spec=str)
        mock_message.split.return_value = [mock_message]

        mock_prefix = MagicMock(spec=str)

        op = logoutput.LogOutput(None)

        result = op.filter_error(level, mock_message, mock_prefix)

        assert result

        mock_message.split.assert_called_with('\n')

        mock_logger.debug.assert_called_with(mock_message)
