"""Test the ht.pyfilter.operations.primaryimage module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import argparse
from mock import MagicMock, call, patch
import unittest

# Houdini Toolbox Imports
from ht.pyfilter.manager import PyFilterManager
from ht.pyfilter.operations import primaryimage

reload(primaryimage)

# =============================================================================
# CLASSES
# =============================================================================

class Test_SetPrimaryImage(unittest.TestCase):
    """Test the ht.pyfilter.operations.primaryimage.SetPrimaryImage object."""

    def setUp(self):
        super(Test_SetPrimaryImage, self).setUp()

        self.patcher = patch("ht.pyfilter.operations.operation._logger", autospec=True)
        self.patcher.start()

    def tearDown(self):
        super(Test_SetPrimaryImage, self).tearDown()
        self.patcher.stop()

    def test___init__(self):
        mock_manager = MagicMock(spec=PyFilterManager)

        op = primaryimage.SetPrimaryImage(mock_manager)

        self.assertEqual(op._data, {})
        self.assertEqual(op._manager, mock_manager)

        self.assertFalse(op._disable_primary_image)
        self.assertIsNone(op._primary_image_path)

    # Properties

    @patch.object(primaryimage.SetPrimaryImage, "__init__", lambda x, y: None)
    def test_disable_primary_image(self):
        op = primaryimage.SetPrimaryImage(None)
        op._disable_primary_image = True
        self.assertTrue(op.disable_primary_image)

        op._disable_primary_image = False
        op.disable_primary_image = True
        self.assertTrue(op._disable_primary_image)

    @patch.object(primaryimage.SetPrimaryImage, "__init__", lambda x, y: None)
    def test_manager(self):
        path = "/path/to/image.exr"

        op = primaryimage.SetPrimaryImage(None)
        op._primary_image_path = path
        self.assertEqual(op.primary_image_path, path)

        op._primary_image_path = None
        op.primary_image_path = path
        self.assertEqual(op._primary_image_path, path)

    # Static Methods

    # build_arg_string

    def test_build_arg_string__empty(self):
        result = primaryimage.SetPrimaryImage.build_arg_string()

        self.assertEqual(result, "")

    def test_build_arg_string__path(self):
        path = "/path/to/image.exr"

        result = primaryimage.SetPrimaryImage.build_arg_string(primary_image_path=path)

        self.assertEqual(result, "--primary-image-path={}".format(path))

    def test_build_arg_string__disable(self):
        result = primaryimage.SetPrimaryImage.build_arg_string(disable_primary_image=True)

        self.assertEqual(result, "--disable-primary-image")

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

    @patch("ht.pyfilter.operations.primaryimage._logger")
    @patch("ht.pyfilter.operations.primaryimage.set_property")
    @patch.object(primaryimage.SetPrimaryImage, "__init__", lambda x, y: None)
    def test_filterCamera__disable(self, mock_set, mock_logger):
        op = primaryimage.SetPrimaryImage(None)
        op._disable_primary_image = True

        op.filterCamera()

        mock_set.assert_called_with("image:filename", "null:")

    @patch("ht.pyfilter.operations.primaryimage._logger")
    @patch("ht.pyfilter.operations.primaryimage.set_property")
    @patch.object(primaryimage.SetPrimaryImage, "__init__", lambda x, y: None)
    def test_filterCamera__path(self, mock_set, mock_logger):
        path = "/path/to/images.exr"

        op = primaryimage.SetPrimaryImage(None)
        op._disable_primary_image = False
        op._primary_image_path = path

        op.filterCamera()

        mock_set.assert_called_with("image:filename", path)

    @patch("ht.pyfilter.operations.primaryimage._logger")
    @patch("ht.pyfilter.operations.primaryimage.set_property")
    @patch.object(primaryimage.SetPrimaryImage, "__init__", lambda x, y: None)
    def test_filterCamera__no_op(self, mock_set, mock_logger):
        path = "/path/to/images.exr"

        op = primaryimage.SetPrimaryImage(None)
        op._disable_primary_image = False
        op._primary_image_path = None

        op.filterCamera()

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

        self.assertFalse(op.disable_primary_image)

        self.assertIsNone(op.primary_image_path)

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

        self.assertTrue(op.disable_primary_image)

        self.assertEqual(op.primary_image_path, path)

    @patch.object(primaryimage.SetPrimaryImage, "__init__", lambda x, y: None)
    def test_should_run__no_op(self):
        op = primaryimage.SetPrimaryImage(None)
        op._disable_primary_image = False
        op._primary_image_path = None

        self.assertFalse(op.should_run())

    @patch.object(primaryimage.SetPrimaryImage, "__init__", lambda x, y: None)
    def test_should_run__disable(self):
        op = primaryimage.SetPrimaryImage(None)
        op._disable_primary_image = True
        op._primary_image_path = None

        self.assertTrue(op.should_run())

    @patch.object(primaryimage.SetPrimaryImage, "__init__", lambda x, y: None)
    def test_should_run__no_op(self):
        op = primaryimage.SetPrimaryImage(None)
        op._disable_primary_image = False
        op._primary_image_path = "/path/to/image.exr"

        self.assertTrue(op.should_run())

# =============================================================================

if __name__ == '__main__':
    unittest.main()
