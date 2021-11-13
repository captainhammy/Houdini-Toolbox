"""Test the houdini_toolbox.pyfilter.operations.deepimage module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import argparse

# Third Party
import pytest

# Houdini Toolbox
from houdini_toolbox.pyfilter.manager import PyFilterManager
from houdini_toolbox.pyfilter.operations import deepimage

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def init_operation(mocker):
    """Fixture to initialize an operation."""
    mocker.patch.object(deepimage.SetDeepImage, "__init__", lambda x, y: None)

    def _create():
        return deepimage.SetDeepImage(None)

    return _create


@pytest.fixture
def patch_logger(mocker):
    """Fixture to handle mocking the module logger calls."""

    return mocker.patch("houdini_toolbox.pyfilter.operations.deepimage._logger")


@pytest.fixture
def properties(mocker):
    """Fixture to handle mocking (get|set)_property calls."""

    _mock_get = mocker.patch("houdini_toolbox.pyfilter.operations.deepimage.get_property")
    _mock_set = mocker.patch("houdini_toolbox.pyfilter.operations.deepimage.set_property")

    class Properties:
        """Fake class for accessing and setting properties."""

        @property
        def mock_get(self):
            """Access get_property."""
            return _mock_get

        @property
        def mock_set(self):
            """Access set_property."""
            return _mock_set

    return Properties()


# =============================================================================
# TESTS
# =============================================================================


class Test_DeepImage:
    """Test the houdini_toolbox.pyfilter.operations.deepimage.DeepImage class."""

    def test___init__(self, mocker):
        """Test object initialization."""
        mock_super_init = mocker.patch.object(deepimage.PyFilterOperation, "__init__")

        mock_manager = mocker.MagicMock(spec=PyFilterManager)

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

    def test_all_passes(self, init_operation, mocker):
        """Test the 'all_passes' property."""
        mock_value = mocker.MagicMock(spec=bool)

        op = init_operation()
        op._all_passes = mock_value

        assert op.all_passes == mock_value

    def test_compositing(self, init_operation, mocker):
        """Test the 'compositing' property."""
        mock_value = mocker.MagicMock(spec=int)

        op = init_operation()
        op._compositing = mock_value

        assert op.compositing == mock_value

    def test_deepcompression(self, init_operation, mocker):
        """Test the 'deepcompression' property."""
        mock_value = mocker.MagicMock(spec=int)

        op = init_operation()
        op._deepcompression = mock_value

        assert op.deepcompression == mock_value

    def test_depth_planes(self, init_operation, mocker):
        """Test the 'depth_planes' property."""
        mock_value = mocker.MagicMock(spec=str)

        op = init_operation()
        op._depth_planes = mock_value

        assert op.depth_planes == mock_value

    def test_disable_deep_image(self, init_operation, mocker):
        """Test the 'disable_deep_image' property."""
        mock_value = mocker.MagicMock(spec=bool)

        op = init_operation()
        op._disable_deep_image = mock_value

        assert op.disable_deep_image == mock_value

    def test_filename(self, init_operation, mocker):
        """Test the 'filename' property."""
        mock_value = mocker.MagicMock(spec=str)

        op = init_operation()
        op._filename = mock_value

        assert op.filename == mock_value

    def test_mipmaps(self, init_operation, mocker):
        """Test the 'mipmaps' property."""
        mock_value = mocker.MagicMock(spec=int)

        op = init_operation()
        op._mipmaps = mock_value

        assert op.mipmaps == mock_value

    def test_ofsize(self, init_operation, mocker):
        """Test the 'ofsize' property."""
        mock_value = mocker.MagicMock(spec=int)

        op = init_operation()
        op._ofsize = mock_value

        assert op.ofsize == mock_value

    def test_ofstorage(self, init_operation, mocker):
        """Test the 'ofstorage' property."""
        mock_value = mocker.MagicMock(spec=str)

        op = init_operation()
        op._ofstorage = mock_value

        assert op.ofstorage == mock_value

    def test_pzstorage(self, init_operation, mocker):
        """Test the 'pzstorage' property."""
        mock_value = mocker.MagicMock(spec=str)

        op = init_operation()
        op._pzstorage = mock_value

        assert op.pzstorage == mock_value

    def test_resolver(self, init_operation, mocker):
        """Test the 'resolver' property."""
        mock_value = mocker.MagicMock(spec=str)

        op = init_operation()
        op._resolver = mock_value

        assert op.resolver == mock_value

    def test_zbias(self, init_operation, mocker):
        """Test the 'zbias' property."""
        mock_value = mocker.MagicMock(spec=int)

        op = init_operation()
        op._zbias = mock_value

        assert op.zbias == mock_value

    # Static Methods

    def test_build_arg_string(self, mocker):
        """Test building arg strings."""
        assert deepimage.SetDeepImage.build_arg_string() == ""

        # Disable deep image path
        result = deepimage.SetDeepImage.build_arg_string(disable_deep_image=True)

        assert result == "--disable-deep-image"

        # deep all passes
        result = deepimage.SetDeepImage.build_arg_string(deep_all_passes=True)

        assert result == "--deep-all-passes"

        # Set deep image path
        mock_path = mocker.MagicMock(spec=str)

        result = deepimage.SetDeepImage.build_arg_string(deep_image_path=mock_path)

        assert result == f"--deep-image-path={mock_path}"

        # Set deep resolver
        mock_resolver = mocker.MagicMock(spec=str)

        result = deepimage.SetDeepImage.build_arg_string(resolver=mock_resolver)

        assert result == f"--deep-resolver={mock_resolver}"

        # Set compositing
        mock_compositing = mocker.MagicMock(spec=int)

        result = deepimage.SetDeepImage.build_arg_string(compositing=mock_compositing)

        assert result == f"--deep-compositing={mock_compositing}"

        # Set compression
        mock_compression = mocker.MagicMock(spec=int)

        result = deepimage.SetDeepImage.build_arg_string(compression=mock_compression)

        assert result == f"--deep-compression={mock_compression}"

        # Set depth planes
        mock_planes = mocker.MagicMock(spec=str)

        result = deepimage.SetDeepImage.build_arg_string(depth_planes=mock_planes)

        assert result == f"--deep-depth-planes={mock_planes}"

        # Test depth planes with string list.
        result = deepimage.SetDeepImage.build_arg_string(
            depth_planes="zfront,zback".split(",")
        )

        assert result == "--deep-depth-planes=zfront,zback"

        # Set mipmaps
        mock_mips = mocker.MagicMock(spec=int)

        result = deepimage.SetDeepImage.build_arg_string(mipmaps=mock_mips)

        assert result == f"--deep-mipmaps={mock_mips}"

        # Set ofsize
        mock_ofsize = mocker.MagicMock(spec=int)

        result = deepimage.SetDeepImage.build_arg_string(ofsize=mock_ofsize)

        assert result == f"--deep-ofsize={mock_ofsize}"

        # Set ofstorage
        mock_ofstorage = mocker.MagicMock(spec=str)

        result = deepimage.SetDeepImage.build_arg_string(ofstorage=mock_ofstorage)

        assert result == f"--deep-ofstorage={mock_ofstorage}"

        # Set pzstorage
        mock_pzstorage = mocker.MagicMock(spec=str)

        result = deepimage.SetDeepImage.build_arg_string(pzstorage=mock_pzstorage)

        assert result == f"--deep-pzstorage={mock_pzstorage}"

        # Set zbias
        mock_zbias = mocker.MagicMock(spec=str)

        result = deepimage.SetDeepImage.build_arg_string(zbias=mock_zbias)

        assert result == f"--deep-zbias={mock_zbias}"

    def test_register_parser_args(self, mocker):
        """Test registering parser args."""
        mock_parser = mocker.MagicMock(spec=argparse.ArgumentParser)

        deepimage.SetDeepImage.register_parser_args(mock_parser)

        calls = [
            mocker.call("--deep-image-path", dest="deep_image_path"),
            mocker.call(
                "--deep-all-passes", action="store_true", dest="deep_all_passes"
            ),
            mocker.call(
                "--disable-deep-image", action="store_true", dest="disable_deep_image"
            ),
            mocker.call(
                "--deep-resolver", choices=("camera", "shadow"), dest="deep_resolver"
            ),
            mocker.call("--deep-compression", type=int, dest="deep_compression"),
            mocker.call("--deep-compositing", type=int, dest="deep_compositing"),
            mocker.call("--deep-depth-planes", dest="deep_depth_planes"),
            mocker.call(
                "--deep-mipmaps", type=int, choices=(0, 1), dest="deep_mipmaps"
            ),
            mocker.call("--deep-ofsize", type=int, choices=(1, 3), dest="deep_ofsize"),
            mocker.call(
                "--deep-ofstorage",
                choices=("real16", "real32", "real64"),
                dest="deep_ofstorage",
            ),
            mocker.call(
                "--deep-pzstorage",
                choices=("real16", "real32", "real64"),
                dest="deep_pzstorage",
            ),
            mocker.call("--deep-zbias", type=float, dest="deep_zbias"),
        ]
        mock_parser.add_argument.assert_has_calls(calls)

    # Methods

    # _modify_deep_args

    def test__modify_deep_args(self, init_operation):
        """Test modifying deep args."""
        # Test value propagation.
        deep_args = ["shadow"]
        op = init_operation()

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

    def test_filter_camera__not_beauty(self, patch_logger, init_operation, properties):
        """Test for non-beauty renders."""
        properties.mock_get.return_value = "shadow"

        op = init_operation()
        op._all_passes = False

        op.filter_camera()

        patch_logger.warning.assert_called_with(
            "Not a beauty render, skipping deepresolver"
        )

    def test_filter_camera__disable_deep_image(
        self, patch_logger, init_operation, properties
    ):
        """Try to disable deep image export."""
        properties.mock_get.return_value = "beauty"

        op = init_operation()
        op._all_passes = False
        op._disable_deep_image = True

        op.filter_camera()

        properties.mock_set.assert_called_with("image:deepresolver", [])
        patch_logger.info.assert_called_with("Disabling deep resolver")

    def test_filter_camera__no_deep_args_no_resolver(
        self, patch_logger, init_operation, properties
    ):
        """Try to set the resolver when there is no resolver already set and
        we don't provide enough data.

        """
        data = {"renderer:rendertype": "beauty", "image:deepresolver": []}

        properties.mock_get.side_effect = lambda arg: data[arg]

        # No resolver type.
        op = init_operation()
        op._all_passes = False
        op._disable_deep_image = False
        op._filename = "/path/to/deep.exr"
        op._resolver = None

        op.filter_camera()

        patch_logger.error.assert_called_with(
            "Cannot set deepresolver: deep output is not enabled"
        )

    def test_filter_camera__no_deep_args_no_file(
        self, patch_logger, init_operation, properties
    ):
        """Try to set the resolver when there is no resolver already set and
        we don't provide enough data.

        """
        data = {"renderer:rendertype": "beauty", "image:deepresolver": []}

        properties.mock_get.side_effect = lambda arg: data[arg]

        # No resolver type.
        op = init_operation()
        op._all_passes = False
        op._disable_deep_image = False
        op._filename = None
        op._resolver = "shadow"

        op.filter_camera()

        patch_logger.error.assert_called_with(
            "Cannot set deepresolver: deep output is not enabled"
        )

    def test_filter_camera__no_deep_args_resolver_and_file(
        self, patch_logger, init_operation, properties, mocker
    ):
        """Try to set the resolver when there is no resolver already set and
        we don't provide enough data.

        """
        mock_modify = mocker.patch.object(deepimage.SetDeepImage, "_modify_deep_args")

        data = {"renderer:rendertype": "beauty", "image:deepresolver": []}

        properties.mock_get.side_effect = lambda arg: data[arg]

        # No resolver type.
        op = init_operation()
        op._all_passes = False
        op._disable_deep_image = False
        op._filename = "/path/to/deep.exr"
        op._resolver = "shadow"

        op.filter_camera()

        mock_modify.assert_called_with(["shadow"])

        patch_logger.debug.assert_called()

        properties.mock_set.assert_called_with("image:deepresolver", ["shadow"])

    def test_filter_camera__deep_args(
        self, patch_logger, init_operation, properties, mocker
    ):
        """Try to set the resolver when there is no resolver already set and
        we don't provide enough data.

        """
        mock_modify = mocker.patch.object(deepimage.SetDeepImage, "_modify_deep_args")

        data = {
            "renderer:rendertype": "beauty",
            "image:deepresolver": ["shadow", "filename", "/path/to/deep.exr"],
        }

        properties.mock_get.side_effect = lambda arg: data[arg]

        # No resolver type.
        op = init_operation()
        op._all_passes = False
        op._disable_deep_image = False
        op._filename = None
        op._resolver = None

        op.filter_camera()

        mock_modify.assert_called_with(["shadow", "filename", "/path/to/deep.exr"])

        patch_logger.debug.assert_called()

        properties.mock_set.assert_called_with(
            "image:deepresolver", ["shadow", "filename", "/path/to/deep.exr"]
        )

    # process_parsed_args

    def test_process_parsed_args(self, init_operation):
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

        op = init_operation()

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

    def test_process_parsed_args__noop(self, init_operation):
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

        op = init_operation()

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

    def test_should_run(self, init_operation):
        """Test if the operation should run."""
        op = init_operation()

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

        op._disable_deep_image = True
        assert op.should_run()
        op._disable_deep_image = False

        op._filename = "/path/to/deep.exr"
        assert op.should_run()
        op._filename = None

        op._resolver = "shadow"
        assert op.should_run()
        op._resolver = None

        op._compositing = 1
        assert op.should_run()
        op._compositing = None

        op._deepcompression = 1
        assert op.should_run()
        op._deepcompression = None

        op._depth_planes = "zback"
        assert op.should_run()
        op._depth_planes = None

        op._mipmaps = 0
        assert op.should_run()
        op._mipmaps = None

        op._ofsize = 1
        assert op.should_run()
        op._ofsize = None

        op._ofstorage = "real16"
        assert op.should_run()
        op._ofstorage = None

        op._pzstorage = "real16"
        assert op.should_run()
        op._pzstorage = None

        op._zbias = 0.1
        assert op.should_run()
        op._zbias = None
