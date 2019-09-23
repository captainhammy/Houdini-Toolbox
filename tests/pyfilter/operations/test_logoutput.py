"""Test the ht.pyfilter.operations.logoutput module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Third Party Imports
import pytest

# Houdini Toolbox Imports
from ht.pyfilter.operations import logoutput


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def init_operation(mocker):
    """Fixture to initialize an operation."""
    mocker.patch.object(logoutput.LogOutput, "__init__", lambda x, y: None)

    def _create():
        return logoutput.LogOutput(None)

    return _create


@pytest.fixture
def patch_logger(mocker):
    """Mock the fake 'mantra' module logger."""
    yield mocker.patch("ht.pyfilter.operations.logoutput._logger", autospec=True)


# =============================================================================
# CLASSES
# =============================================================================

class Test_LogOutput(object):
    """Test the ht.pyfilter.operations.logoutput.LogOutput object."""

    # Methods

    def test_filter_error__level_0(self, init_operation, patch_logger, mocker):
        """Filter an error with level=0."""
        level = 0

        mock_message1 = mocker.MagicMock(spec=str)
        mock_message2 = mocker.MagicMock(spec=str)

        mock_message = mocker.MagicMock(spec=str)
        mock_message.split.return_value = [mock_message1, mock_message2]

        mock_prefix = mocker.MagicMock(spec=str)

        op = init_operation()

        assert op.filter_error(level, mock_message, mock_prefix)

        mock_message.split.assert_called_with('\n')

        patch_logger.error.assert_has_calls(
            [mocker.call(mock_message1), mocker.call(mock_message2)]
        )

    def test_filter_error__prefix(self, init_operation, patch_logger, mocker):
        """Filter a warning due to a prefix."""
        level = mocker.MagicMock(spec=int)

        mock_message = mocker.MagicMock(spec=str)
        mock_message.split.return_value = [mock_message]

        mock_prefix = mocker.MagicMock(spec=str)
        mock_prefix.__len__.return_value = 1

        op = init_operation()

        assert op.filter_error(level, mock_message, mock_prefix)

        mock_message.split.assert_called_with('\n')

        patch_logger.warning.assert_called_with(mock_message)

    def test_filter_error__level_1(self, init_operation, patch_logger, mocker):
        """Filter an info message with level=1."""
        level = 1

        mock_message = mocker.MagicMock(spec=str)
        mock_message.split.return_value = [mock_message]

        mock_prefix = mocker.MagicMock(spec=str)

        op = init_operation()

        assert op.filter_error(level, mock_message, mock_prefix)

        mock_message.split.assert_called_with('\n')

        patch_logger.info.assert_called_with(mock_message)

    def test_filter_error__debug(self, init_operation, patch_logger, mocker):
        """Filter a debug message."""
        level = mocker.MagicMock(spec=int)

        mock_message = mocker.MagicMock(spec=str)
        mock_message.split.return_value = [mock_message]

        mock_prefix = mocker.MagicMock(spec=str)

        op = init_operation()

        assert op.filter_error(level, mock_message, mock_prefix)

        mock_message.split.assert_called_with('\n')

        patch_logger.debug.assert_called_with(mock_message)
