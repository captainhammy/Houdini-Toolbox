"""Test the ht.pyfilter.operations.settilecallback module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import argparse

# Third Party Imports
import pytest

# Houdini Toolbox Imports
from ht.pyfilter.manager import PyFilterManager
from ht.pyfilter.operations import settilecallback


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def init_operation(mocker):
    """Fixture to initialize an operation."""
    mocker.patch.object(settilecallback.SetTileCallback, "__init__", lambda x, y: None)

    def _create():
        return settilecallback.SetTileCallback(None)

    return _create


# =============================================================================
# CLASSES
# =============================================================================


class Test_SetTileCallback(object):
    """Test the ht.pyfilter.operations.settilecallback.SetTileCallback object."""

    def test___init__(self, mocker):
        """Test object initialization."""
        mock_super_init = mocker.patch.object(
            settilecallback.PyFilterOperation, "__init__"
        )

        mock_manager = mocker.MagicMock(spec=PyFilterManager)

        op = settilecallback.SetTileCallback(mock_manager)

        mock_super_init.assert_called_with(mock_manager)

        assert op._tilecallback is None

    # Properties

    def test_tilecallback(self, init_operation, mocker):
        """Test 'tilecallback' property."""
        mock_value = mocker.MagicMock(spec=str)

        op = init_operation()

        op._tilecallback = mock_value
        assert op.tilecallback == mock_value

    # Static Methods

    def test_build_arg_string(self, mocker):
        """Test arg string construction."""
        assert settilecallback.SetTileCallback.build_arg_string() == ""

        mock_path = mocker.MagicMock(spec=str)
        result = settilecallback.SetTileCallback.build_arg_string(path=mock_path)

        assert result == "--tile-callback={}".format(mock_path)

    def test_register_parser_args(self, mocker):
        """Test registering parser args."""
        mock_parser = mocker.MagicMock(spec=argparse.ArgumentParser)

        settilecallback.SetTileCallback.register_parser_args(mock_parser)

        calls = [mocker.call("--tile-callback", dest="tilecallback")]
        mock_parser.add_argument.assert_has_calls(calls)

    # Methods

    def test_filter_camera(self, init_operation, mocker, patch_operation_logger):
        """Test filter_camera."""
        mock_set = mocker.patch("ht.pyfilter.operations.settilecallback.set_property")

        mock_tilecallback = mocker.PropertyMock(spec=str)

        op = init_operation()
        type(op).tilecallback = mock_tilecallback

        op.filter_camera()

        mock_set.assert_called_with(
            "render:tilecallback", mock_tilecallback.return_value
        )

    def test_process_parsed_args__noop(self, init_operation, mocker):
        """Test processing the args when the tilecallback arg is None."""
        mock_namespace = mocker.MagicMock(spec=argparse.Namespace)
        mock_namespace.tilecallback = None

        op = init_operation()
        op._tilecallback = None

        op.process_parsed_args(mock_namespace)

        assert op._tilecallback is None

    def test_process_parsed_args(self, init_operation, mocker):
        """Test processing the args when the tilecallback arg is set to a value."""
        mock_path = mocker.MagicMock(spec=str)

        mock_namespace = mocker.MagicMock(spec=argparse.Namespace)
        mock_namespace.tilecallback = mock_path

        op = init_operation()
        op._tilecallback = None

        op.process_parsed_args(mock_namespace)

        assert op._tilecallback == mock_path

    # should_run

    def test_should_run__no_callback(self, init_operation, mocker):
        """Test if the operation should run when a path is not set."""
        mock_tilecallback = mocker.PropertyMock(return_value=None)

        op = init_operation()
        type(op).tilecallback = mock_tilecallback

        assert not op.should_run()

    def test_should_run__callbacl(self, init_operation, mocker):
        """Test if the operation should run when a path is set."""
        mock_path = mocker.MagicMock(spec=str)

        op = init_operation()
        type(op).tilecallback = mock_path

        assert op.should_run()
