"""Test the ht.pyfilter.operations.deepimage module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import argparse

# Third Party Imports
from mock import MagicMock, call, patch

# Houdini Toolbox Imports
from ht.pyfilter.manager import PyFilterManager
from ht.pyfilter.operations import deepimage


# =============================================================================
# CLASSES
# =============================================================================

class Test_DeepImage(object):
    """Test the ht.pyfilter.operations.deepimage.DeepImage class.

    """

    @patch.object(deepimage.PyFilterOperation, "__init__")
    def test___init__(self, mock_super_init):
        """Test constructor."""
        mock_manager = MagicMock(spec=PyFilterManager)
        op = deepimage.SetDeepImage(mock_manager)

        mock_super_init.assert_called_with(mock_manager)

        assert not op._all_passes
        assert not op._disable_deep_image

        assert op._resolver is None
        assert op._filename is None
        assert op._compositing is None
        assert op._deepcompression is None
        assert op._depth_planes is None
        assert op._mipmaps is None
        assert op._ofsize is None
        assert op._ofstorage is None
        assert op._pzstorage is None
        assert op._zbias is None

    # Properties

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_all_passes(self):
        """Test 'all_passes' property."""
        op = deepimage.SetDeepImage(None)

        mock_value1 = MagicMock(spec=bool)
        op._all_passes = mock_value1
        assert op.all_passes == mock_value1

        mock_value2 = MagicMock(spec=bool)
        op.all_passes = mock_value2
        assert op._all_passes == mock_value2

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_compositing(self):
        """Test 'compositing' property."""
        op = deepimage.SetDeepImage(None)

        mock_value1 = MagicMock(spec=int)
        op._compositing = mock_value1
        assert op.compositing == mock_value1

        mock_value2 = MagicMock(spec=int)
        op.compositing = mock_value2
        assert op._compositing == mock_value2

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_deepcompression(self):
        """Test 'deepcompression' property."""
        op = deepimage.SetDeepImage(None)

        mock_value1 = MagicMock(spec=int)
        op._deepcompression = mock_value1
        assert op.deepcompression == mock_value1

        mock_value2 = MagicMock(spec=int)
        op.deepcompression = mock_value2
        assert op._deepcompression == mock_value2

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_depth_planes(self):
        """Test 'depth_planes' property."""
        op = deepimage.SetDeepImage(None)

        mock_value1 = MagicMock(spec=str)
        op._depth_planes = mock_value1
        assert op.depth_planes == mock_value1

        mock_value2 = MagicMock(spec=str)
        op.depth_planes = mock_value2
        assert op._depth_planes == mock_value2

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_disable_deep_image(self):
        """Test 'disable_deep_image' property."""
        op = deepimage.SetDeepImage(None)

        mock_value1 = MagicMock(spec=bool)
        op._disable_deep_image = mock_value1
        assert op.disable_deep_image == mock_value1

        mock_value2 = MagicMock(spec=bool)
        op.disable_deep_image = mock_value2
        assert op._disable_deep_image == mock_value2

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_filename(self):
        """Test 'filename' property."""
        op = deepimage.SetDeepImage(None)

        mock_value1 = MagicMock(spec=str)
        op._filename = mock_value1
        assert op.filename == mock_value1

        mock_value2 = MagicMock(spec=str)
        op.filename = mock_value2
        assert op._filename == mock_value2

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_mipmaps(self):
        """Test 'mipmaps' property."""
        op = deepimage.SetDeepImage(None)

        mock_value1 = MagicMock(spec=int)
        op._mipmaps = mock_value1
        assert op.mipmaps == mock_value1

        mock_value2 = MagicMock(spec=int)
        op.mipmaps = mock_value2
        assert op._mipmaps == mock_value2

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_ofsize(self):
        """Test 'ofsize' property."""
        op = deepimage.SetDeepImage(None)

        mock_value1 = MagicMock(spec=int)
        op._ofsize = mock_value1
        assert op.ofsize == mock_value1

        mock_value2 = MagicMock(spec=int)
        op.ofsize = mock_value2
        assert op._ofsize == mock_value2

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_ofstorage(self):
        """Test 'ofstorage' property."""
        op = deepimage.SetDeepImage(None)

        mock_value1 = MagicMock(spec=str)
        op._ofstorage = mock_value1
        assert op.ofstorage == mock_value1

        mock_value2 = MagicMock(spec=str)
        op.ofstorage = mock_value2
        assert op._ofstorage == mock_value2

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_pzstorage(self):
        """Test 'pzstorage' property."""
        op = deepimage.SetDeepImage(None)

        mock_value1 = MagicMock(spec=str)
        op._pzstorage = mock_value1
        assert op.pzstorage == mock_value1

        mock_value2 = MagicMock(spec=str)
        op.pzstorage = mock_value2
        assert op._pzstorage == mock_value2

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_resolver(self):
        """Test 'resolver' property."""
        op = deepimage.SetDeepImage(None)

        mock_value1 = MagicMock(spec=str)
        op._resolver = mock_value1
        assert op.resolver == mock_value1

        mock_value2 = MagicMock(spec=str)
        op.resolver = mock_value2
        assert op._resolver == mock_value2

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_zbias(self):
        """Test 'zbias' property."""
        op = deepimage.SetDeepImage(None)

        mock_value1 = MagicMock(spec=int)
        op._zbias = mock_value1
        assert op.zbias == mock_value1

        mock_value2 = MagicMock(spec=int)
        op.zbias = mock_value2
        assert op._zbias == mock_value2

    # Static Methods

    # build_arg_string

    def test_build_arg_string(self):
        """Test building arg strings."""
        result = deepimage.SetDeepImage.build_arg_string()

        assert result == ""

        # Disable deep image path
        result = deepimage.SetDeepImage.build_arg_string(disable_deep_image=True)

        assert result == "--disable-deep-image"

        # deep all passes
        result = deepimage.SetDeepImage.build_arg_string(deep_all_passes=True)

        assert result == "--deep-all-passes"

        # Set deep image path
        mock_path = MagicMock(spec=str)

        result = deepimage.SetDeepImage.build_arg_string(deep_image_path=mock_path)

        assert result == "--deep-image-path={}".format(mock_path)

        # Set deep resolver
        mock_resolver = MagicMock(spec=str)

        result = deepimage.SetDeepImage.build_arg_string(resolver=mock_resolver)

        assert result == "--deep-resolver={}".format(mock_resolver)

        # Set compositing
        mock_compositing = MagicMock(spec=int)

        result = deepimage.SetDeepImage.build_arg_string(compositing=mock_compositing)

        assert result == "--deep-compositing={}".format(mock_compositing)

        # Set compression
        mock_compression = MagicMock(spec=int)

        result = deepimage.SetDeepImage.build_arg_string(compression=mock_compression)

        assert result == "--deep-compression={}".format(mock_compression)

        # Set depth planes
        mock_planes = MagicMock(spec=str)

        result = deepimage.SetDeepImage.build_arg_string(depth_planes=mock_planes)

        assert result == "--deep-depth-planes={}".format(mock_planes)

        # Test depth planes with string list.
        result = deepimage.SetDeepImage.build_arg_string(depth_planes="zfront,zback".split(','))

        assert result == "--deep-depth-planes={}".format("zfront,zback")

        # Set mipmaps
        mock_mips = MagicMock(spec=int)

        result = deepimage.SetDeepImage.build_arg_string(mipmaps=mock_mips)

        assert result == "--deep-mipmaps={}".format(mock_mips)

        # Set ofsize
        mock_ofsize = MagicMock(spec=int)

        result = deepimage.SetDeepImage.build_arg_string(ofsize=mock_ofsize)

        assert result == "--deep-ofsize={}".format(mock_ofsize)

        # Set ofstorage
        mock_ofstorage = MagicMock(spec=str)

        result = deepimage.SetDeepImage.build_arg_string(ofstorage=mock_ofstorage)

        assert result == "--deep-ofstorage={}".format(mock_ofstorage)

        # Set pzstorage
        mock_pzstorage = MagicMock(spec=str)

        result = deepimage.SetDeepImage.build_arg_string(pzstorage=mock_pzstorage)

        assert result == "--deep-pzstorage={}".format(mock_pzstorage)

        # Set zbias
        mock_zbias = MagicMock(spec=str)

        result = deepimage.SetDeepImage.build_arg_string(zbias=mock_zbias)

        assert result == "--deep-zbias={}".format(mock_zbias)

    # register_parser_args

    def test_register_parser_args(self):
        """Test registering parser args."""
        mock_parser = MagicMock(spec=argparse.ArgumentParser)

        deepimage.SetDeepImage.register_parser_args(mock_parser)

        calls = [
            call("--deep-image-path", dest="deep_image_path"),
            call("--deep-all-passes", action="store_true", dest="deep_all_passes"),
            call("--disable-deep-image", action="store_true", dest="disable_deep_image"),
            call("--deep-resolver", choices=("camera", "shadow"), dest="deep_resolver"),
            call("--deep-compression", type=int, dest="deep_compression"),
            call("--deep-compositing", type=int, dest="deep_compositing"),
            call("--deep-depth-planes", dest="deep_depth_planes"),
            call("--deep-mipmaps", type=int, choices=(0, 1), dest="deep_mipmaps"),
            call("--deep-ofsize", type=int, choices=(1, 3), dest="deep_ofsize"),
            call("--deep-ofstorage", choices=("real16", "real32", "real64"), dest="deep_ofstorage"),
            call("--deep-pzstorage", choices=("real16", "real32", "real64"), dest="deep_pzstorage"),
            call("--deep-zbias", type=float, dest="deep_zbias"),

        ]
        mock_parser.add_argument.assert_has_calls(calls)

    # Methods

    # _modify_deep_args

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test__modify_deep_args(self):
        """Test modifying deep args."""
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

        assert deep_args == ["shadow"]

        # Test adding a new value.
        deep_args = ["shadow"]
        op._filename = "/path/to/deep.exr"
        op._modify_deep_args(deep_args)

        assert deep_args == ["shadow", "filename", "/path/to/deep.exr"]

        # Test modifying existing value.
        deep_args = ["filename", "/foo/bar/frame.exr"]
        op._filename = "/path/to/deep.exr"
        op._modify_deep_args(deep_args)

        assert deep_args == ["filename", "/path/to/deep.exr"]

    # filter_camera

    @patch("ht.pyfilter.operations.deepimage.get_property")
    @patch("ht.pyfilter.operations.deepimage._logger")
    @patch.object(deepimage.SetDeepImage, "_modify_deep_args")
    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_filter_camera__not_beauty(self, mock_modify, mock_logger, mock_get, patch_operation_logger):
        """Test for non-beauty renders."""
        mock_get.return_value = "shadow"

        op = deepimage.SetDeepImage(None)
        op._all_passes = False

        op.filter_camera()

        mock_logger.warning.assert_called_with("Not a beauty render, skipping deepresolver")

    @patch("ht.pyfilter.operations.deepimage.set_property")
    @patch("ht.pyfilter.operations.deepimage.get_property")
    @patch("ht.pyfilter.operations.deepimage._logger")
    @patch.object(deepimage.SetDeepImage, "_modify_deep_args")
    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_filter_camera__disable_deep_image(self, mock_modify, mock_logger, mock_get, mock_set, patch_operation_logger):
        """Try to disable deep image export."""
        mock_get.return_value = "beauty"

        op = deepimage.SetDeepImage(None)
        op._all_passes = False
        op._disable_deep_image = True

        op.filter_camera()

        mock_set.assert_called_with("image:deepresolver", [])
        mock_logger.info.assert_called_with("Disabling deep resolver")

    @patch("ht.pyfilter.operations.deepimage.set_property")
    @patch("ht.pyfilter.operations.deepimage.get_property")
    @patch("ht.pyfilter.operations.deepimage._logger")
    @patch.object(deepimage.SetDeepImage, "_modify_deep_args")
    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_filter_camera__no_deep_args_no_resolver(self, mock_modify, mock_logger, mock_get, mock_set, patch_operation_logger):
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

        op.filter_camera()

        mock_logger.error.assert_called_with("Cannot set deepresolver: deep output is not enabled")

    @patch("ht.pyfilter.operations.deepimage.set_property")
    @patch("ht.pyfilter.operations.deepimage.get_property")
    @patch("ht.pyfilter.operations.deepimage._logger")
    @patch.object(deepimage.SetDeepImage, "_modify_deep_args")
    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_filter_camera__no_deep_args_no_file(self, mock_modify, mock_logger, mock_get, mock_set, patch_operation_logger):
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

        op.filter_camera()

        mock_logger.error.assert_called_with("Cannot set deepresolver: deep output is not enabled")

    @patch("ht.pyfilter.operations.deepimage.set_property")
    @patch("ht.pyfilter.operations.deepimage.get_property")
    @patch("ht.pyfilter.operations.deepimage._logger")
    @patch.object(deepimage.SetDeepImage, "_modify_deep_args")
    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_filter_camera__no_deep_args_resolver_and_file(self, mock_modify, mock_logger, mock_get, mock_set, patch_operation_logger):
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

        op.filter_camera()

        mock_modify.assert_called_with(["shadow"])

        mock_logger.debug.assert_called()

        mock_set.assert_called_with("image:deepresolver", ["shadow"])

    @patch("ht.pyfilter.operations.deepimage.set_property")
    @patch("ht.pyfilter.operations.deepimage.get_property")
    @patch("ht.pyfilter.operations.deepimage._logger")
    @patch.object(deepimage.SetDeepImage, "_modify_deep_args")
    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_filter_camera__deep_args(self, mock_modify, mock_logger, mock_get, mock_set, patch_operation_logger):
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

        op.filter_camera()

        mock_modify.assert_called_with(["shadow", "filename", "/path/to/deep.exr"])

        mock_logger.debug.assert_called()

        mock_set.assert_called_with("image:deepresolver", ["shadow", "filename", "/path/to/deep.exr"])

    # process_parsed_args

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_process_parsed_args(self):
        """Test processing the args."""
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

        assert op.disable_deep_image
        assert op.all_passes
        assert op.filename == "/path/to/deep.exr"
        assert op.resolver == "shadow"
        assert op.compositing == 1
        assert op.deepcompression == 1
        assert op.depth_planes == "zfront,zback"
        assert op.mipmaps == 1
        assert op.ofsize == 1
        assert op.ofstorage == "real16"
        assert op.pzstorage == "real32"
        assert op.zbias == 0.5

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_process_parsed_args__none(self):
        """Test processing the args when they are all default."""
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

        assert op.disable_deep_image
        assert op.all_passes
        assert op.filename == "/path/to/deep.exr"
        assert op.resolver == "shadow"
        assert op.compositing == 1
        assert op.deepcompression == 1
        assert op.depth_planes == "zfront,zback"
        assert op.mipmaps == 1
        assert op.ofsize == 1
        assert op.ofstorage == "real16"
        assert op.pzstorage == "real32"
        assert op.zbias == 0.5

    # should_run

    @patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)
    def test_should_run(self):
        """Test if the operation should run."""
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

        assert not op.should_run()

        op.disable_deep_image = True
        assert op.should_run()
        op.disable_deep_image = False

        op.filename = "/path/to/deep.exr"
        assert op.should_run()
        op.filename = None

        op.resolver = "shadow"
        assert op.should_run()
        op.resolver = None

        op.compositing = 1
        assert op.should_run()
        op.compositing = None

        op.deepcompression = 1
        assert op.should_run()
        op.deepcompression = None

        op.depth_planes = "zback"
        assert op.should_run()
        op.depth_planes = None

        op.mipmaps = 0
        assert op.should_run()
        op.mipmaps = None

        op.ofsize = 1
        assert op.should_run()
        op.ofsize = None

        op.ofstorage = "real16"
        assert op.should_run()
        op.ofstorage = None

        op.pzstorage = "real16"
        assert op.should_run()
        op.pzstorage = None

        op.zbias = 0.1
        assert op.should_run()
        op.zbias = None

