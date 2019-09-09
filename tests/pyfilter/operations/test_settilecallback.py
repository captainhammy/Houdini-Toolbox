"""Test the ht.pyfilter.operations.settilecallback module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import argparse

# Third Party Imports
from mock import MagicMock, PropertyMock, call, patch

# Houdini Toolbox Imports
from ht.pyfilter.manager import PyFilterManager
from ht.pyfilter.operations import settilecallback


# =============================================================================
# CLASSES
# =============================================================================

class Test_SetTileCallback(object):
    """Test the ht.pyfilter.operations.settilecallback.SetTileCallback object."""

    # =========================================================================

    @patch.object(settilecallback.PyFilterOperation, "__init__")
    def test___init__(self, mock_super_init):
        """Test constructor."""
        mock_manager = MagicMock(spec=PyFilterManager)

        op = settilecallback.SetTileCallback(mock_manager)

        mock_super_init.assert_called_with(mock_manager)

        assert op._tilecallback is None

    # Properties

    @patch.object(settilecallback.SetTileCallback, "__init__", lambda x, y: None)
    def test_tilecallback(self):
        """Test 'tilecallback' property."""
        op = settilecallback.SetTileCallback(None)

        mock_value = MagicMock(spec=str)
        op._tilecallback = mock_value
        assert op.tilecallback == mock_value

    # Static Methods

    # build_arg_string

    def test_build_arg_string__empty(self):
        """Test passing no path."""
        result = settilecallback.SetTileCallback.build_arg_string()

        assert result == ""

    def test_build_arg_string__path(self):
        """Test passing a tile callback path."""
        mock_path = MagicMock(spec=str)

        result = settilecallback.SetTileCallback.build_arg_string(path=mock_path)

        assert result == "--tile-callback={}".format(mock_path)

    # register_parser_args

    def test_register_parser_args(self):
        """Test registering parser args."""
        mock_parser = MagicMock(spec=argparse.ArgumentParser)

        settilecallback.SetTileCallback.register_parser_args(mock_parser)

        calls = [call("--tile-callback", dest="tilecallback")]
        mock_parser.add_argument.assert_has_calls(calls)

    # Methods

    # filter_camera

    @patch("ht.pyfilter.operations.settilecallback.set_property")
    @patch.object(settilecallback.SetTileCallback, "tilecallback", new_callable=PropertyMock)
    @patch.object(settilecallback.SetTileCallback, "__init__", lambda x, y: None)
    def test_filter_camera(self, mock_tilecallback, mock_set, patch_operation_logger):
        """Test filter_camera."""
        op = settilecallback.SetTileCallback(None)

        op.filter_camera()

        mock_set.assert_called_with("render:tilecallback", mock_tilecallback.return_value)

    # process_parsed_args

    @patch.object(settilecallback.SetTileCallback, "__init__", lambda x, y: None)
    def test_process_parsed_args_noop(self):
        """Test processing the args when the tilecallback arg is None."""
        mock_namespace = MagicMock(spec=argparse.Namespace)
        mock_namespace.tilecallback = None

        op = settilecallback.SetTileCallback(None)
        op._tilecallback = None

        op.process_parsed_args(mock_namespace)

        assert op._tilecallback is None

    @patch.object(settilecallback.SetTileCallback, "__init__", lambda x, y: None)
    def test_process_parsed_args(self):
        """Test processing the args when the tilecallback arg is set to a value."""
        mock_path = MagicMock(spec=str)

        mock_namespace = MagicMock(spec=argparse.Namespace)
        mock_namespace.tilecallback = mock_path

        op = settilecallback.SetTileCallback(None)
        op._tilecallback = None

        op.process_parsed_args(mock_namespace)

        assert op._tilecallback == mock_path

    # should_run

    @patch.object(settilecallback.SetTileCallback, "__init__", lambda x, y: None)
    def test_should_run__no_op(self):
        """Test if the operation should run when a path is not set."""
        op = settilecallback.SetTileCallback(None)
        op._tilecallback = None

        assert not op.should_run()

    @patch.object(settilecallback.SetTileCallback, "__init__", lambda x, y: None)
    def test_should_run(self):
        """Test if the operation should run when a path is set."""
        mock_path = MagicMock(spec=str)

        op = settilecallback.SetTileCallback(None)
        op._tilecallback = mock_path

        assert op.should_run()
