

import coverage
import unittest

from mock import MagicMock, patch

from ht.pyfilter.operations import operation
from ht.pyfilter.manager import PyFilterManager

cov = coverage.Coverage(source=["ht.pyfilter.operations.operation"], branch=True)

cov.start()

reload(operation)

class TestOperation(unittest.TestCase):
    """Test the ht.pyfilter.operations.operation.PyFilterOperation object."""

    def test___init__(self):
        mock_manager = MagicMock(spec=PyFilterManager)
        op = operation.PyFilterOperation(mock_manager)

        self.assertEqual(op._data, {})
        self.assertEqual(op._manager, mock_manager)

    # Properties

    @patch.object(operation.PyFilterOperation, "__init__", lambda x, y: None)
    def test_data(self):
        data = {"key": "value"}

        op = operation.PyFilterOperation(None)
        op._data = data

        self.assertEqual(op.data, data)

    @patch.object(operation.PyFilterOperation, "__init__", lambda x, y: None)
    def test_manager(self):
        mock_manager = MagicMock(spec=PyFilterManager)

        op = operation.PyFilterOperation(None)
        op._manager = mock_manager

        self.assertEqual(op.manager, mock_manager)

    # Static Methods

    def test_build_arg_string(self):
        self.assertIsNone(operation.PyFilterOperation.build_arg_string())

    def test_register_parser_args(self):
        self.assertIsNone(operation.PyFilterOperation.register_parser_args(None))

    # Methods

    @patch.object(operation.PyFilterOperation, "__init__", lambda x, y: None)
    def test_process_parsed_args(self):
        op = operation.PyFilterOperation(None)

        self.assertIsNone(op.process_parsed_args(None))

    @patch.object(operation.PyFilterOperation, "__init__", lambda x, y: None)
    def test_should_run(self):
        op = operation.PyFilterOperation(None)

        self.assertTrue(op.should_run())

# =============================================================================

if __name__ == '__main__':
    try:
        # Run the tests.
        unittest.main()

    finally:
        cov.stop()
        cov.save()

        cov.html_report()
