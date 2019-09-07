"""Test the ht.pyfilter.operations.operation module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import imp

# Third Party Imports
from mock import MagicMock, patch
import pytest

# Houdini Toolbox Imports
from ht.pyfilter.manager import PyFilterManager
from ht.pyfilter.operations import operation

# Reload the module to test to capture load evaluation since it has already
# been loaded.
imp.reload(operation)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def patch_logger():
    """Mock the log_filter_call logger."""
    patcher = patch("ht.pyfilter.operations.operation._logger", autospec=True)

    yield

    patcher.stop()


# =============================================================================
# CLASSES
# =============================================================================

class Test_PyFilterOperation(object):
    """Test the ht.pyfilter.operations.operation.PyFilterOperation object."""

    # def setUp(self):
    #     super(Test_PyFilterOperation, self).setUp()
    #
    #     self.patcher = patch("ht.pyfilter.operations.operation._logger", autospec=True)
    #     self.patcher.start()
    #
    # def tearDown(self):
    #     super(Test_PyFilterOperation, self).tearDown()
    #     self.patcher.stop()

    def test___init__(self, patch_logger):
        mock_manager = MagicMock(spec=PyFilterManager)
        op = operation.PyFilterOperation(mock_manager)

        assert op._data == {}
        assert op._manager == mock_manager

    # Properties

    @patch.object(operation.PyFilterOperation, "__init__", lambda x, y: None)
    def test_data(self, patch_logger):
        data = {"key": "value"}

        op = operation.PyFilterOperation(None)
        op._data = data

        assert op.data == data

    @patch.object(operation.PyFilterOperation, "__init__", lambda x, y: None)
    def test_manager(self, patch_logger):
        mock_manager = MagicMock(spec=PyFilterManager)

        op = operation.PyFilterOperation(None)
        op._manager = mock_manager

        assert op.manager == mock_manager

    # Static Methods

    def test_build_arg_string(self, patch_logger):
        assert operation.PyFilterOperation.build_arg_string() is None

    def test_register_parser_args(self, patch_logger):
        assert operation.PyFilterOperation.register_parser_args(None) is None

    # Methods

    @patch.object(operation.PyFilterOperation, "__init__", lambda x, y: None)
    def test_process_parsed_args(self, patch_logger):
        op = operation.PyFilterOperation(None)

        assert op.process_parsed_args(None) is None

    @patch.object(operation.PyFilterOperation, "__init__", lambda x, y: None)
    def test_should_run(self, patch_logger):
        op = operation.PyFilterOperation(None)

        assert op.should_run()
