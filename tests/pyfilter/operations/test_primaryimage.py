"""Test the ht.pyfilter.operations.primaryimage module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import argparse

# Third Party Imports
from mock import MagicMock, call, patch
import pytest

# Houdini Toolbox Imports
from ht.pyfilter.manager import PyFilterManager
from ht.pyfilter.operations import primaryimage


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

class Test_SetPrimaryImage(object):
    """Test the ht.pyfilter.operations.primaryimage.SetPrimaryImage object."""

    def test___init__(self):
        mock_manager = MagicMock(spec=PyFilterManager)

        op = primaryimage.SetPrimaryImage(mock_manager)

        assert op._data == {}
        assert op._manager == mock_manager

        assert not op._disable_primary_image
        assert op._primary_image_path is None

    # Properties

    @patch.object(primaryimage.SetPrimaryImage, "__init__", lambda x, y: None)
    def test_disable_primary_image(self):
        op = primaryimage.SetPrimaryImage(None)
        op._disable_primary_image = True
        assert op.disable_primary_image

        op._disable_primary_image = False
        op.disable_primary_image = True
        assert op._disable_primary_image

    @patch.object(primaryimage.SetPrimaryImage, "__init__", lambda x, y: None)
    def test_primary_image_path(self):
        path = "/path/to/image.exr"

        op = primaryimage.SetPrimaryImage(None)
        op._primary_image_path = path
        assert op.primary_image_path == path

        op._primary_image_path = None
        op.primary_image_path = path
        assert op._primary_image_path == path

    # Static Methods

    # build_arg_string

    def test_build_arg_string__empty(self):
        result = primaryimage.SetPrimaryImage.build_arg_string()

        assert result == ""

    def test_build_arg_string__path(self):
        path = "/path/to/image.exr"

        result = primaryimage.SetPrimaryImage.build_arg_string(primary_image_path=path)

        assert result == "--primary-image-path={}".format(path)

    def test_build_arg_string__disable(self):
        result = primaryimage.SetPrimaryImage.build_arg_string(disable_primary_image=True)

        assert result == "--disable-primary-image"

    # register_parser_args

    def test_register_parser_args(self):
        mock_parser = MagicMock(spec=argparse.ArgumentParser)

        primaryimage.SetPrimaryImage.register_parser_args(mock_parser)

        calls = [
            call("--primary-image-path", dest="primary_image_path"),
            call("--disable-primary-image", action="store_true", dest="disable_primary_image")
        ]
        mock_parser.add_argument.assert_has_calls(calls)

    # Methods

    # filter_camera

    @patch("ht.pyfilter.operations.primaryimage._logger")
    @patch("ht.pyfilter.operations.primaryimage.set_property")
    @patch.object(primaryimage.SetPrimaryImage, "__init__", lambda x, y: None)
    def test_filter_camera__disable(self, mock_set, mock_logger, patch_logger):
        op = primaryimage.SetPrimaryImage(None)
        op._disable_primary_image = True

        op.filter_camera()

        mock_set.assert_called_with("image:filename", "null:")

    @patch("ht.pyfilter.operations.primaryimage._logger")
    @patch("ht.pyfilter.operations.primaryimage.set_property")
    @patch.object(primaryimage.SetPrimaryImage, "__init__", lambda x, y: None)
    def test_filter_camera__path(self, mock_set, mock_logger, patch_logger):
        path = "/path/to/images.exr"

        op = primaryimage.SetPrimaryImage(None)
        op._disable_primary_image = False
        op._primary_image_path = path

        op.filter_camera()

        mock_set.assert_called_with("image:filename", path)

    @patch("ht.pyfilter.operations.primaryimage._logger")
    @patch("ht.pyfilter.operations.primaryimage.set_property")
    @patch.object(primaryimage.SetPrimaryImage, "__init__", lambda x, y: None)
    def test_filter_camera__no_op(self, mock_set, mock_logger, patch_logger):
        path = "/path/to/images.exr"

        op = primaryimage.SetPrimaryImage(None)
        op._disable_primary_image = False
        op._primary_image_path = None

        op.filter_camera()

        mock_set.assert_not_called()

    # process_parsed_args

    @patch.object(primaryimage.SetPrimaryImage, "__init__", lambda x, y: None)
    def test_process_parsed_args_noop(self):
        path = "/path/to/image.exr"
        mock_namespace = MagicMock(spec=argparse.Namespace)
        mock_namespace.disable_primary_image = False
        mock_namespace.primary_image_path = None

        op = primaryimage.SetPrimaryImage(None)
        op._disable_primary_image = False
        op._primary_image_path = None

        op.process_parsed_args(mock_namespace)

        assert not op.disable_primary_image

        assert op.primary_image_path is None

    @patch.object(primaryimage.SetPrimaryImage, "__init__", lambda x, y: None)
    def test_process_parsed_args(self):
        path = "/path/to/image.exr"
        mock_namespace = MagicMock(spec=argparse.Namespace)
        mock_namespace.disable_primary_image = True
        mock_namespace.primary_image_path = path

        op = primaryimage.SetPrimaryImage(None)
        op._disable_primary_image = False
        op._primary_image_path = None

        op.process_parsed_args(mock_namespace)

        assert op.disable_primary_image

        assert op.primary_image_path == path

    @patch.object(primaryimage.SetPrimaryImage, "__init__", lambda x, y: None)
    def test_should_run__no_op(self):
        op = primaryimage.SetPrimaryImage(None)
        op._disable_primary_image = False
        op._primary_image_path = None

        assert not op.should_run()

    @patch.object(primaryimage.SetPrimaryImage, "__init__", lambda x, y: None)
    def test_should_run__disable(self):
        op = primaryimage.SetPrimaryImage(None)
        op._disable_primary_image = True
        op._primary_image_path = None

        assert op.should_run()

    @patch.object(primaryimage.SetPrimaryImage, "__init__", lambda x, y: None)
    def test_should_run__no_op(self):
        op = primaryimage.SetPrimaryImage(None)
        op._disable_primary_image = False
        op._primary_image_path = "/path/to/image.exr"

        assert op.should_run()
