"""Test the ht.pyfilter.operations.operation module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import argparse

# Third Party Imports
import pytest

# Houdini Toolbox Imports
from ht.pyfilter.manager import PyFilterManager
from ht.pyfilter.operations import operation


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def init_operation(mocker):
    """Fixture to initialize an operation."""
    mocker.patch.object(operation.PyFilterOperation, "__init__", lambda x, y: None)

    def _create():
        return operation.PyFilterOperation(None)

    return _create


# =============================================================================
# TESTS
# =============================================================================


class Test_PyFilterOperation:
    """Test the ht.pyfilter.operations.operation.PyFilterOperation object."""

    def test___init__(self, mocker):
        """Test object initialization."""
        mock_manager = mocker.MagicMock(spec=PyFilterManager)

        op = operation.PyFilterOperation(mock_manager)

        assert op._data == {}
        assert op._manager == mock_manager

    # Properties

    def test_data(self, init_operation, mocker):
        """Test the 'data' property."""
        mock_value = mocker.MagicMock(spec=dict)

        op = init_operation()
        op._data = mock_value

        assert op.data == mock_value

    def test_manager(self, init_operation, mocker):
        """Test the 'manager' property."""
        mock_manager = mocker.MagicMock(spec=PyFilterManager)

        op = init_operation()
        op._manager = mock_manager

        assert op.manager == mock_manager

    # Static Methods

    def test_build_arg_string(self):
        """Test arg string construction."""
        assert operation.PyFilterOperation.build_arg_string() is None

    def test_register_parser_args(self, mocker):
        """Test registering all the argument parser args."""
        mock_parser = mocker.MagicMock(spec=argparse.ArgumentParser)

        assert operation.PyFilterOperation.register_parser_args(mock_parser) is None

    # Methods

    def test_process_parsed_args(self, init_operation):
        """Test processing parsed args."""
        namespace = argparse.Namespace()

        op = init_operation()

        assert op.process_parsed_args(namespace) is None

    def test_should_run(self, init_operation):
        """Test whether or not the operation should run."""
        op = init_operation()

        assert op.should_run()
