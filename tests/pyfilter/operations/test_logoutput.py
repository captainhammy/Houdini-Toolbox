"""Test the ht.pyfilter.operations.logoutput module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import argparse
import logging
from mock import MagicMock, PropertyMock, call, patch
import unittest

# Houdini Toolbox Imports
from ht.pyfilter.manager import PyFilterManager
from ht.pyfilter.operations import logoutput

reload(logoutput)

# =============================================================================
# CLASSES
# =============================================================================

class Test_LogOutput(unittest.TestCase):
    """Test the ht.pyfilter.operations.logoutput.LogOutput object."""

    def setUp(self):
        super(Test_LogOutput, self).setUp()

        self.patcher = patch("ht.pyfilter.operations.operation.logger", autospec=True)
        self.patcher.start()

    def tearDown(self):
        super(Test_LogOutput, self).tearDown()
        self.patcher.stop()

    @patch("ht.pyfilter.operations.logoutput.logging.getLogger")
    @patch.object(logoutput.PyFilterOperation, "__init__")
    def test___init__(self, mock_super_init, mock_get):
        mock_manager = MagicMock(spec=PyFilterManager)

        op = logoutput.LogOutput(mock_manager)

        mock_super_init.assert_called_with(mock_manager)

        self.assertEqual(op._logger, mock_get.return_value)

    # Properties

    @patch.object(logoutput.LogOutput, "__init__", lambda x, y: None)
    def test_logger(self):
        value = MagicMock(logging.Logger)

        op = logoutput.LogOutput(None)
        op._logger = value
        self.assertEqual(op.logger, value)

    # Methods

    @patch.object(logoutput.LogOutput, "logger", new_callable=PropertyMock)
    @patch.object(logoutput.LogOutput, "__init__", lambda x, y: None)
    def test_filterError__level_0(self, mock_logger):
        mock_log = MagicMock(spec=logging.Logger)
        mock_logger.return_value = mock_log

        level = 0

        mock_message1 = MagicMock(spec=str)
        mock_message2 = MagicMock(spec=str)

        mock_message = MagicMock(spec=str)
        mock_message.split.return_value = [mock_message1, mock_message2]

        mock_prefix = MagicMock(spec=str)

        op = logoutput.LogOutput(None)

        result = op.filterError(level, mock_message, mock_prefix)

        self.assertTrue(result)

        mock_message.split.assert_called_with('\n')

        mock_log.error.assert_has_calls(
            [call(mock_message1), call(mock_message2)]
        )

    @patch.object(logoutput.LogOutput, "logger", new_callable=PropertyMock)
    @patch.object(logoutput.LogOutput, "__init__", lambda x, y: None)
    def test_filterError__prefix(self, mock_logger):
        mock_log = MagicMock(spec=logging.Logger)
        mock_logger.return_value = mock_log

        level = 1

        mock_message = MagicMock(spec=str)
        mock_message.split.return_value = [mock_message]

        mock_prefix = MagicMock(spec=str)
        mock_prefix.__len__.return_value = 1

        op = logoutput.LogOutput(None)

        result = op.filterError(level, mock_message, mock_prefix)

        self.assertTrue(result)

        mock_message.split.assert_called_with('\n')

        mock_log.warning.assert_called_with(mock_message)

    @patch.object(logoutput.LogOutput, "logger", new_callable=PropertyMock)
    @patch.object(logoutput.LogOutput, "__init__", lambda x, y: None)
    def test_filterError__level_1(self, mock_logger):
        mock_log = MagicMock(spec=logging.Logger)
        mock_logger.return_value = mock_log

        level = 1

        mock_message = MagicMock(spec=str)
        mock_message.split.return_value = [mock_message]

        mock_prefix = MagicMock(spec=str)

        op = logoutput.LogOutput(None)

        result = op.filterError(level, mock_message, mock_prefix)

        self.assertTrue(result)

        mock_message.split.assert_called_with('\n')

        mock_log.info.assert_called_with(mock_message)

    @patch.object(logoutput.LogOutput, "logger", new_callable=PropertyMock)
    @patch.object(logoutput.LogOutput, "__init__", lambda x, y: None)
    def test_filterError__debug(self, mock_logger):
        mock_log = MagicMock(spec=logging.Logger)
        mock_logger.return_value = mock_log

        level = MagicMock(spec=int)

        mock_message = MagicMock(spec=str)
        mock_message.split.return_value = [mock_message]

        mock_prefix = MagicMock(spec=str)

        op = logoutput.LogOutput(None)

        result = op.filterError(level, mock_message, mock_prefix)

        self.assertTrue(result)

        mock_message.split.assert_called_with('\n')

        mock_log.debug.assert_called_with(mock_message)

# =============================================================================

if __name__ == '__main__':
    unittest.main()
