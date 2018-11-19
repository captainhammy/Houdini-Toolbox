"""Test the ht.pyfilter.operations.deepimage module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import argparse
import coverage
from mock import MagicMock, patch
import unittest

# Houdini Toolbox Imports
from ht.pyfilter.manager import PyFilterManager
from ht.pyfilter.operations import deepimage

# Houdini Imports
import hou

cov = coverage.coverage(data_suffix=True, source=["ht.pyfilter.operations.deepimage"], branch=True)
cov.start()

reload(deepimage)

# =============================================================================
# CLASSES
# =============================================================================

class Test_DeepImage(unittest.TestCase):
    """Test the houdini_submission.pyfilter.operations.deepimage.DeepImage class.

    """

    def setUp(self):
        super(Test_DeepImage, self).setUp()

        self.patcher = patch("ht.pyfilter.operations.operation.logger", autospec=True)
        self.patcher.start()

    def tearDown(self):
        super(Test_DeepImage, self).tearDown()
        self.patcher.stop()

    def test___init__(self):
        mock_manager = MagicMock(spec=PyFilterManager)
        op = deepimage.SetDeepImage(mock_manager)

        self.assertEqual(op._data, {})
        self.assertEqual(op._manager, mock_manager)

        self.assertFalse(op._all_passes, False)
        self.assertFalse(op._disable_deep_image, False)

        self.assertIsNone(op._resolver)
        self.assertIsNone(op._filename)
        self.assertIsNone(op._compositing)
        self.assertIsNone(op._deepcompression)
        self.assertIsNone(op._depth_planes)
        self.assertIsNone(op._mipmaps)
        self.assertIsNone(op._ofsize)
        self.assertIsNone(op._ofstorage)
        self.assertIsNone(op._pzstorage)
        self.assertIsNone(op._zbias)

    # Properties

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_all_passes(self):
        op = deepimage.SetDeepImage(None)
        op._all_passes = True
        self.assertTrue(op.all_passes)

        op = deepimage.SetDeepImage(None)
        op._all_passes = False
        op.all_passes = True
        self.assertTrue(op._all_passes)

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_compositing(self):
        op = deepimage.SetDeepImage(None)
        op._compositing = True
        self.assertTrue(op.compositing)

        op = deepimage.SetDeepImage(None)
        op._compositing = False
        op.compositing = True
        self.assertTrue(op._compositing)

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_deepcompression(self):
        op = deepimage.SetDeepImage(None)
        op._deepcompression = 4
        self.assertEqual(op.deepcompression, 4)

        op = deepimage.SetDeepImage(None)
        op._deepcompression = 3
        op.deepcompression = 4
        self.assertEqual(op._deepcompression, 4)

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_depth_planes(self):
        op = deepimage.SetDeepImage(None)
        op._depth_planes = "zfront,zback"
        self.assertEqual(op.depth_planes, "zfront,zback")

        op = deepimage.SetDeepImage(None)
        op._depth_planes = "foo"
        op.depth_planes = "zfront,zback"
        self.assertEqual(op._depth_planes, "zfront,zback")

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_disable_deep_image(self):
        op = deepimage.SetDeepImage(None)
        op._disable_deep_image = True
        self.assertTrue(op.disable_deep_image)

        op = deepimage.SetDeepImage(None)
        op._disable_deep_image = False
        op.disable_deep_image = True
        self.assertTrue(op._disable_deep_image)

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_filename(self):
        op = deepimage.SetDeepImage(None)
        op._filename = "/path/to/file.exr"
        self.assertEqual(op.filename, "/path/to/file.exr")

        op = deepimage.SetDeepImage(None)
        op._filename = "foo"
        op.filename = "/path/to/file.exr"
        self.assertEqual(op._filename, "/path/to/file.exr")

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_mipmaps(self):
        op = deepimage.SetDeepImage(None)
        op._mipmaps = True
        self.assertTrue(op.mipmaps)

        op = deepimage.SetDeepImage(None)
        op._mipmaps = False
        op.mipmaps = True
        self.assertTrue(op._mipmaps)

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_ofsize(self):
        op = deepimage.SetDeepImage(None)
        op._ofsize = 3
        self.assertEqual(op.ofsize, 3)

        op = deepimage.SetDeepImage(None)
        op._ofsize = 1
        op.ofsize = 3
        self.assertEqual(op._ofsize, 3)

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_ofstorage(self):
        op = deepimage.SetDeepImage(None)
        op._ofstorage = "real32"
        self.assertEqual(op.ofstorage, "real32")

        op = deepimage.SetDeepImage(None)
        op._ofstorage = "real16"
        op.ofstorage = "real32"
        self.assertEqual(op._ofstorage, "real32")

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_pzstorage(self):
        op = deepimage.SetDeepImage(None)
        op._pzstorage = "real32"
        self.assertEqual(op.pzstorage, "real32")

        op = deepimage.SetDeepImage(None)
        op._pzstorage = "real16"
        op.pzstorage = "real32"
        self.assertEqual(op._pzstorage, "real32")

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_resolver(self):
        op = deepimage.SetDeepImage(None)
        op._resolver = "shadow"
        self.assertEqual(op.resolver, "shadow")

        op = deepimage.SetDeepImage(None)
        op._resolver = "camera"
        op.resolver = "shadow"
        self.assertEqual(op._resolver, "shadow")

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_zbias(self):
        op = deepimage.SetDeepImage(None)
        op._zbias = 3
        self.assertEqual(op.zbias, 3)

        op = deepimage.SetDeepImage(None)
        op._zbias = 1
        op.zbias = 3
        self.assertEqual(op._zbias, 3)

    # Static Methods

    def test_build_arg_string(self):
        result = deepimage.SetDeepImage.build_arg_string()

        self.assertEquals(result, "")

        # Disable deep image path
        result = deepimage.SetDeepImage.build_arg_string(
            disable_deep_image=True
        )

        self.assertEquals(
            result,
            "--disable-deep-image"
        )

        # deep all passes
        result = deepimage.SetDeepImage.build_arg_string(
            deep_all_passes=True
        )

        self.assertEquals(
            result,
            "--deep-all-passes"
        )

        # Set deep image path
        result = deepimage.SetDeepImage.build_arg_string(
            deep_image_path="/path/to/deep.exr"
        )

        self.assertEquals(
            result,
            "--deep-image-path={}".format("/path/to/deep.exr")
        )

        # Set deep resolver
        result = deepimage.SetDeepImage.build_arg_string(
            resolver="shadow"
        )

        self.assertEquals(
            result,
            "--deep-resolver=shadow"
        )

        # Set compositing
        result = deepimage.SetDeepImage.build_arg_string(
            compositing=1
        )

        self.assertEquals(
            result,
            "--deep-compositing=1"
        )

        # Set compression
        result = deepimage.SetDeepImage.build_arg_string(
            compression=1
        )

        self.assertEquals(
            result,
            "--deep-compression=1"
        )

        # Set depth planes
        result = deepimage.SetDeepImage.build_arg_string(
            depth_planes="zfront,zback"
        )

        self.assertEquals(
            result,
            "--deep-depth-planes={}".format("zfront,zback")
        )

        result = deepimage.SetDeepImage.build_arg_string(
            depth_planes="zfront,zback".split(',')
        )

        self.assertEquals(
            result,
            "--deep-depth-planes={}".format("zfront,zback")
        )

        # Set mipmaps
        result = deepimage.SetDeepImage.build_arg_string(
            mipmaps=0
        )

        self.assertEquals(
            result,
            "--deep-mipmaps=0"
        )

        # Set ofsize
        result = deepimage.SetDeepImage.build_arg_string(
            ofsize=1
        )

        self.assertEquals(
            result,
            "--deep-ofsize=1"
        )

        # Set ofstorage
        result = deepimage.SetDeepImage.build_arg_string(
            ofstorage="real32"
        )

        self.assertEquals(
            result,
            "--deep-ofstorage=real32"
        )

        # Set pzstorage
        result = deepimage.SetDeepImage.build_arg_string(
            pzstorage="real16"
        )

        self.assertEquals(
            result,
            "--deep-pzstorage=real16"
        )

        # Set zbias
        result = deepimage.SetDeepImage.build_arg_string(
            zbias=1.2
        )

        self.assertEquals(
            result,
            "--deep-zbias=1.2"
        )

    def test_register_parser_args(self):
        parser = argparse.ArgumentParser()

        deepimage.SetDeepImage.register_parser_args(parser)

        arg_names = {
            "--deep-image-path",
            "--disable-deep-image",
            "--deep-all-passes",
            "--deep-resolver",
            "--deep-compositing",
            "--deep-compression",
            "--deep-depth-planes",
            "--deep-depth-planes",
            "--deep-mipmaps",
            "--deep-ofsize",
            "--deep-ofstorage",
            "--deep-pzstorage",
            "--deep-zbias"
        }

        registered_args = []

        for action in parser._optionals._actions:
            registered_args.extend(action.option_strings)

        registered_args = set(registered_args)

        msg = "Expected args not registered: {}".format(
            ", ".join(arg_names - registered_args)
        )

        self.assertTrue(
            arg_names.issubset(registered_args),
            msg=msg
        )

    # Methods

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test__modify_deep_args(self):
        # Test value propagation.
        deep_args = ["shadow"]
        op = deepimage.SetDeepImage(None)

        op._all_passes = False
        op._disable_deep_image = False
        op._resolver = None
        op._filename = None
        op._compositing = None
        op._deepcompression = None
        op._depth_planes = None
        op._mipmaps = None
        op._ofsize = None
        op._ofstorage = None
        op._pzstorage = None
        op._zbias = None

        op._modify_deep_args(deep_args)

        self.assertEquals(deep_args, ["shadow"])

        # Test adding a new value.
        deep_args = ["shadow"]
        op._filename = "/path/to/deep.exr"
        op._modify_deep_args(deep_args)

        self.assertEquals(deep_args, ["shadow", "filename", "/path/to/deep.exr"])

        # Test modifying existing value.
        deep_args = ["filename", "/foo/bar/frame.exr"]
        op._filename = "/path/to/deep.exr"
        op._modify_deep_args(deep_args)

        self.assertEquals(deep_args, ["filename", "/path/to/deep.exr"])

    @patch("ht.pyfilter.operations.deepimage.get_property")
    @patch("ht.pyfilter.operations.deepimage.logger")
    @patch.object(deepimage.SetDeepImage, "_modify_deep_args")
    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_filterCamera__not_beatuy(self, mock_modify, mock_logger, mock_get):
        mock_get.return_value = "shadow"

        op = deepimage.SetDeepImage(None)
        op._all_passes = False

        op.filterCamera()

        mock_logger.warning.assert_called_with("Not a beauty render, skipping deepresolver")

    @patch("ht.pyfilter.operations.deepimage.set_property")
    @patch("ht.pyfilter.operations.deepimage.get_property")
    @patch("ht.pyfilter.operations.deepimage.logger")
    @patch.object(deepimage.SetDeepImage, "_modify_deep_args")
    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_filterCamera__disable_deep_image(self, mock_modify, mock_logger, mock_get, mock_set):
        """Try to disable deep image export."""
        mock_get.return_value = "beauty"

        op = deepimage.SetDeepImage(None)
        op._all_passes = False
        op._disable_deep_image = True

        op.filterCamera()

        mock_set.assert_called_with("image:deepresolver", [])
        mock_logger.info.assert_called_with("Disabling deep resolver")

    @patch("ht.pyfilter.operations.deepimage.set_property")
    @patch("ht.pyfilter.operations.deepimage.get_property")
    @patch("ht.pyfilter.operations.deepimage.logger")
    @patch.object(deepimage.SetDeepImage, "_modify_deep_args")
    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_filterCamera__no_deep_args_no_resolver(self, mock_modify, mock_logger, mock_get, mock_set):
        """Try to set the resolver when there is no resolver already set and
        we don't provide enough data.

        """
        data = {
            "renderer:rendertype": "beauty",
            "image:deepresolver": []
        }

        mock_get.side_effect = lambda arg: data[arg]

        # No resolver type.
        op = deepimage.SetDeepImage(None)
        op._all_passes = False
        op._disable_deep_image = False
        op._filename = "/path/to/deep.exr"
        op._resolver = None

        op.filterCamera()

        mock_logger.error.assert_called_with("Cannot set deepresolver: deep output is not enabled")

    @patch("ht.pyfilter.operations.deepimage.set_property")
    @patch("ht.pyfilter.operations.deepimage.get_property")
    @patch("ht.pyfilter.operations.deepimage.logger")
    @patch.object(deepimage.SetDeepImage, "_modify_deep_args")
    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_filterCamera__no_deep_args_no_file(self, mock_modify, mock_logger, mock_get, mock_set):
        """Try to set the resolver when there is no resolver already set and
        we don't provide enough data.

        """
        data = {
            "renderer:rendertype": "beauty",
            "image:deepresolver": []
        }

        mock_get.side_effect = lambda arg: data[arg]

        # No resolver type.
        op = deepimage.SetDeepImage(None)
        op._all_passes = False
        op._disable_deep_image = False
        op._filename = None
        op._resolver = "shadow"

        op.filterCamera()

        mock_logger.error.assert_called_with("Cannot set deepresolver: deep output is not enabled")

    @patch("ht.pyfilter.operations.deepimage.set_property")
    @patch("ht.pyfilter.operations.deepimage.get_property")
    @patch("ht.pyfilter.operations.deepimage.logger")
    @patch.object(deepimage.SetDeepImage, "_modify_deep_args")
    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_filterCamera__no_deep_args_resolver_and_file(self, mock_modify, mock_logger, mock_get, mock_set):
        """Try to set the resolver when there is no resolver already set and
        we don't provide enough data.

        """
        data = {
            "renderer:rendertype": "beauty",
            "image:deepresolver": []
        }

        mock_get.side_effect = lambda arg: data[arg]

        # No resolver type.
        op = deepimage.SetDeepImage(None)
        op._all_passes = False
        op._disable_deep_image = False
        op._filename = "/path/to/deep.exr"
        op._resolver = "shadow"

        op.filterCamera()

        mock_modify.assert_called_with(["shadow"])

        mock_logger.debug.assert_called()

        mock_set.assert_called_with("image:deepresolver", ["shadow"])

    @patch("ht.pyfilter.operations.deepimage.set_property")
    @patch("ht.pyfilter.operations.deepimage.get_property")
    @patch("ht.pyfilter.operations.deepimage.logger")
    @patch.object(deepimage.SetDeepImage, "_modify_deep_args")
    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_filterCamera__deep_args(self, mock_modify, mock_logger, mock_get, mock_set):
        """Try to set the resolver when there is no resolver already set and
        we don't provide enough data.

        """
        data = {
            "renderer:rendertype": "beauty",
            "image:deepresolver": ["shadow", "filename", "/path/to/deep.exr"]
        }

        mock_get.side_effect = lambda arg: data[arg]

        # No resolver type.
        op = deepimage.SetDeepImage(None)
        op._all_passes = False
        op._disable_deep_image = False
        op._filename = None
        op._resolver = None

        op.filterCamera()

        mock_modify.assert_called_with(["shadow", "filename", "/path/to/deep.exr"])

        mock_logger.debug.assert_called()

        mock_set.assert_called_with("image:deepresolver", ["shadow", "filename", "/path/to/deep.exr"])

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_process_parsed_args(self):
        namespace = argparse.Namespace()
        namespace.disable_deep_image = True
        namespace.deep_all_passes = True
        namespace.deep_image_path = "/path/to/deep.exr"
        namespace.deep_resolver = "shadow"
        namespace.deep_compositing = 1
        namespace.deep_compression = 1
        namespace.deep_depth_planes = "zfront,zback"
        namespace.deep_mipmaps = 1
        namespace.deep_ofsize = 1
        namespace.deep_ofstorage = "real16"
        namespace.deep_pzstorage = "real32"
        namespace.deep_zbias = 0.5

        op = deepimage.SetDeepImage(None)

        op._all_passes = False
        op._disable_deep_image = False
        op._resolver = None
        op._filename = None
        op._compositing = None
        op._deepcompression = None
        op._depth_planes = None
        op._mipmaps = None
        op._ofsize = None
        op._ofstorage = None
        op._pzstorage = None
        op._zbias = None

        op.process_parsed_args(namespace)

        self.assertTrue(op.disable_deep_image)
        self.assertTrue(op.all_passes)
        self.assertEquals(op.filename, "/path/to/deep.exr")
        self.assertEquals(op.resolver, "shadow")
        self.assertEquals(op.compositing, 1)
        self.assertEquals(op.deepcompression, 1)
        self.assertEquals(op.depth_planes, "zfront,zback")
        self.assertEquals(op.mipmaps, 1)
        self.assertEquals(op.ofsize, 1)
        self.assertEquals(op.ofstorage, "real16")
        self.assertEquals(op.pzstorage, "real32")
        self.assertEquals(op.zbias, 0.5)

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_process_parsed_args__none(self):
        namespace = argparse.Namespace()
        namespace.disable_deep_image = False
        namespace.deep_all_passes = False
        namespace.deep_image_path = None
        namespace.deep_resolver = None
        namespace.deep_compositing = None
        namespace.deep_compression = None
        namespace.deep_depth_planes = None
        namespace.deep_mipmaps = None
        namespace.deep_ofsize = None
        namespace.deep_ofstorage = None
        namespace.deep_pzstorage = None
        namespace.deep_zbias = None

        op = deepimage.SetDeepImage(None)

        op._all_passes = True
        op._disable_deep_image = True
        op._resolver = "shadow"
        op._filename = "/path/to/deep.exr"
        op._compositing = 1
        op._deepcompression = 1
        op._depth_planes = "zfront,zback"
        op._mipmaps = 1
        op._ofsize = 1
        op._ofstorage = "real16"
        op._pzstorage = "real32"
        op._zbias = 0.5

        op.process_parsed_args(namespace)

        self.assertTrue(op.disable_deep_image)
        self.assertTrue(op.all_passes)
        self.assertEquals(op.filename, "/path/to/deep.exr")
        self.assertEquals(op.resolver, "shadow")
        self.assertEquals(op.compositing, 1)
        self.assertEquals(op.deepcompression, 1)
        self.assertEquals(op.depth_planes, "zfront,zback")
        self.assertEquals(op.mipmaps, 1)
        self.assertEquals(op.ofsize, 1)
        self.assertEquals(op.ofstorage, "real16")
        self.assertEquals(op.pzstorage, "real32")
        self.assertEquals(op.zbias, 0.5)

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_should_run(self):
        op = deepimage.SetDeepImage(None)

        op._disable_deep_image = False
        op._resolver = None
        op._filename = None
        op._compositing = None
        op._deepcompression = None
        op._depth_planes = None
        op._mipmaps = None
        op._ofsize = None
        op._ofstorage = None
        op._pzstorage = None
        op._zbias = None

        self.assertFalse(op.should_run())

        op.disable_deep_image = True
        self.assertTrue(op.should_run())
        op.disable_deep_image = False

        op.filename = "/path/to/deep.exr"
        self.assertTrue(op.should_run())
        op.filename = None

        op.resolver = "shadow"
        self.assertTrue(op.should_run())
        op.resolver = None

        op.compositing = 1
        self.assertTrue(op.should_run())
        op.compositing = None

        op.deepcompression = 1
        self.assertTrue(op.should_run())
        op.deepcompression = None

        op.depth_planes = "zback"
        self.assertTrue(op.should_run())
        op.depth_planes = None

        op.mipmaps = 0
        self.assertTrue(op.should_run())
        op.mipmaps = None

        op.ofsize = 1
        self.assertTrue(op.should_run())
        op.ofsize = None

        op.ofstorage = "real16"
        self.assertTrue(op.should_run())
        op.ofstorage = None

        op.pzstorage = "real16"
        self.assertTrue(op.should_run())
        op.pzstorage = None

        op.zbias = 0.1
        self.assertTrue(op.should_run())
        op.zbias = None

# =============================================================================

if __name__ == '__main__':
    # Run the tests.
    try:
        unittest.main()
    finally:
        cov.stop()
        cov.html_report()
        cov.save()
