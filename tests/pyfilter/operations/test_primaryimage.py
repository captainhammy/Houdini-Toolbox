"""Test the ht.pyfilter.operations.primaryimage module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import argparse

# Third Party Imports
import pytest

# Houdini Toolbox Imports
from ht.pyfilter.manager import PyFilterManager
from ht.pyfilter.operations import primaryimage


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def init_operation(mocker):
    """Fixture to initialize an operation."""
    mocker.patch.object(primaryimage.SetPrimaryImage, "__init__", lambda x, y: None)

    def _create():
        return primaryimage.SetPrimaryImage(None)

    return _create


# =============================================================================
# TESTS
# =============================================================================


class Test_SetPrimaryImage(object):
    """Test the ht.pyfilter.operations.primaryimage.SetPrimaryImage object."""

    def test___init__(self, mocker):
        """Test object initialization."""
        mock_super_init = mocker.patch.object(
            primaryimage.PyFilterOperation, "__init__"
        )

        mock_manager = mocker.MagicMock(spec=PyFilterManager)

        op = primaryimage.SetPrimaryImage(mock_manager)

        mock_super_init.assert_called_with(mock_manager)

        assert not op._disable_primary_image
        assert op._primary_image_path is None

    # Properties

    def test_disable_primary_image(self, init_operation, mocker):
        """Test the 'disable_primary_image' property."""
        mock_value = mocker.MagicMock(spec=bool)

        op = init_operation()
        op._disable_primary_image = mock_value

        assert op.disable_primary_image == mock_value

    def test_primary_image_path(self, init_operation, mocker):
        """Test the 'primary_image_path' property."""
        mock_value = mocker.MagicMock(spec=str)

        op = init_operation()
        op._primary_image_path = mock_value

        assert op.primary_image_path == mock_value

    # Static Methods

    def test_build_arg_string(self, mocker):
        """Test arg string construction."""
        result = primaryimage.SetPrimaryImage.build_arg_string()
        assert result == ""

        mock_value = mocker.MagicMock(spec=str)

        result = primaryimage.SetPrimaryImage.build_arg_string(
            primary_image_path=mock_value
        )
        assert result == "--primary-image-path={}".format(mock_value)

        result = primaryimage.SetPrimaryImage.build_arg_string(
            disable_primary_image=True
        )
        assert result == "--disable-primary-image"

    def test_register_parser_args(self, mocker):
        """Test registering all the argument parser args."""
        mock_parser = mocker.MagicMock(spec=argparse.ArgumentParser)

        primaryimage.SetPrimaryImage.register_parser_args(mock_parser)

        calls = [
            mocker.call("--primary-image-path", dest="primary_image_path"),
            mocker.call(
                "--disable-primary-image",
                action="store_true",
                dest="disable_primary_image",
            ),
        ]
        mock_parser.add_argument.assert_has_calls(calls)

    # Methods

    # filter_camera

    def test_filter_camera__no_op(self, init_operation, patch_operation_logger, mocker):
        """Test 'filter_camera' when doing nothing."""
        mock_set = mocker.patch("ht.pyfilter.operations.primaryimage.set_property")

        op = init_operation()
        op._disable_primary_image = False
        op._primary_image_path = None

        op.filter_camera()

        mock_set.assert_not_called()

    def test_filter_camera__disable(
        self, init_operation, patch_operation_logger, mocker
    ):
        """Test 'filter_camera' when disabling the image."""
        mock_set = mocker.patch("ht.pyfilter.operations.primaryimage.set_property")
        mock_logger = mocker.patch(
            "ht.pyfilter.operations.primaryimage._logger", autospec=True
        )

        op = init_operation()
        op._disable_primary_image = True

        op.filter_camera()

        mock_logger.info.assert_called()
        mock_set.assert_called_with("image:filename", "null:")

    def test_filter_camera__path(self, init_operation, patch_operation_logger, mocker):
        """Test 'filter_camera' when setting the image path."""
        mock_set = mocker.patch("ht.pyfilter.operations.primaryimage.set_property")

        mock_path = mocker.MagicMock(spec=str)

        op = init_operation()
        op._disable_primary_image = False
        op._primary_image_path = mock_path

        op.filter_camera()

        mock_set.assert_called_with("image:filename", mock_path)

    # process_parsed_args

    def test_process_parsed_args__noop(self, init_operation, mocker):
        """Test processing parsed args when no args are set."""
        mock_namespace = mocker.MagicMock(spec=argparse.Namespace)
        mock_namespace.disable_primary_image = False
        mock_namespace.primary_image_path = None

        op = init_operation()
        op._disable_primary_image = False
        op._primary_image_path = None

        op.process_parsed_args(mock_namespace)

        assert not op.disable_primary_image

        assert op.primary_image_path is None

    def test_process_parsed_args__all(self, init_operation, mocker):
        """Test processing parsed args when all args are set."""
        mock_path = mocker.MagicMock(spec=str)

        mock_namespace = mocker.MagicMock(spec=argparse.Namespace)
        mock_namespace.disable_primary_image = True
        mock_namespace.primary_image_path = mock_path

        op = init_operation()
        op._disable_primary_image = False
        op._primary_image_path = None

        op.process_parsed_args(mock_namespace)

        assert op.disable_primary_image

        assert op.primary_image_path == mock_path

    # should_run

    def test_should_run__no_op(self, init_operation):
        """Test if the operation should run with no args set."""
        op = init_operation()
        op._disable_primary_image = False
        op._primary_image_path = None

        assert not op.should_run()

    def test_should_run__disable(self, init_operation):
        """Test if the operation should run when disable image is set."""
        op = init_operation()
        op._disable_primary_image = True
        op._primary_image_path = None

        assert op.should_run()

    def test_should_run__set_path(self, init_operation, mocker):
        """Test if the operation should run when setting an image path."""
        op = init_operation()
        op._disable_primary_image = False
        op._primary_image_path = mocker.MagicMock(spec=str)

        assert op.should_run()
