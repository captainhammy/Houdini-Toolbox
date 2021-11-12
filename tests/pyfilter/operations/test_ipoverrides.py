"""Test the ht.pyfilter.operations.ipoverrides module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import argparse
import copy

# Third Party
import pytest

# Houdini Toolbox
from ht.pyfilter.manager import PyFilterManager
from ht.pyfilter.operations import ipoverrides

# Houdini
import hou

_DEFAULTS = {
    "bucket_size": None,
    "disable_aovs": False,
    "disable_blur": False,
    "disable_deep": False,
    "disable_displacement": False,
    "disable_matte": False,
    "disable_subd": False,
    "disable_tilecallback": False,
    "res_scale": None,
    "sample_scale": None,
    "transparent_samples": None,
}


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def init_operation(mocker):
    """Fixture to initialize an operation."""
    mocker.patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)

    def _create(
        prop_map: dict = None, as_properties: bool = False
    ) -> ipoverrides.IpOverrides:
        """Function which instantiates the operation.

        :param prop_map: Map of property name:values to set.
        :param as_properties: Whether or not to set the values as properties
        :return: An basic instantiated IpOverrides object.

        """
        op = ipoverrides.IpOverrides(None)

        if prop_map is None:
            prop_map = {}

        values = copy.deepcopy(_DEFAULTS)

        values.update(prop_map)

        for key, value in list(values.items()):
            if as_properties:
                if isinstance(value, type):
                    prop = mocker.PropertyMock(spec=value)

                else:
                    prop = mocker.PropertyMock(return_value=value)

                setattr(type(op), key, prop)

            else:
                setattr(op, f"_{key}", value)

        return op

    return _create


@pytest.fixture
def properties(mocker):
    """Fixture to handle mocking (get|set)_property calls."""

    _mock_get = mocker.patch("ht.pyfilter.operations.ipoverrides.get_property")
    _mock_set = mocker.patch("ht.pyfilter.operations.ipoverrides.set_property")

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


class Test_IpOverrides:
    """Test the ht.pyfilter.operations.ipoverrides.IpOverride class."""

    def test___init__(self, mocker):
        """Test object initialization."""
        mock_super_init = mocker.patch.object(ipoverrides.PyFilterOperation, "__init__")

        mock_manager = mocker.MagicMock(spec=PyFilterManager)

        op = ipoverrides.IpOverrides(mock_manager)

        mock_super_init.assert_called_with(mock_manager)

        assert op._bucket_size is None
        assert not op._disable_aovs
        assert not op._disable_blur
        assert not op._disable_deep
        assert not op._disable_displacement
        assert not op._disable_matte
        assert not op._disable_subd
        assert op._res_scale is None
        assert op._sample_scale is None
        assert op._transparent_samples is None

    # Properties

    def test_bucket_size(self, init_operation, mocker):
        """Test the 'bucket_size' property."""
        mock_value = mocker.MagicMock(spec=int)

        op = init_operation({"bucket_size": mock_value})
        assert op.bucket_size == mock_value

    def test_disable_aovs(self, init_operation, mocker):
        """Test the 'disable_aovs' property."""
        mock_value = mocker.MagicMock(spec=bool)

        op = init_operation({"disable_aovs": mock_value})
        assert op.disable_aovs == mock_value

    def test_disable_blur(self, init_operation, mocker):
        """Test the 'disable_blur' property."""
        mock_value = mocker.MagicMock(spec=bool)

        op = init_operation({"disable_blur": mock_value})
        assert op.disable_blur == mock_value

    def test_disable_deep(self, init_operation, mocker):
        """Test the 'disable_deep' property."""
        mock_value = mocker.MagicMock(spec=bool)

        op = init_operation({"disable_deep": mock_value})

        assert op.disable_deep == mock_value

    def test_disable_displacement(self, init_operation, mocker):
        """Test the 'disable_displacement' property."""
        mock_value = mocker.MagicMock(spec=bool)

        op = init_operation({"disable_displacement": mock_value})

        assert op.disable_displacement == mock_value

    def test_disable_matte(self, init_operation, mocker):
        """Test the 'disable_matte' property."""
        mock_value = mocker.MagicMock(spec=bool)

        op = init_operation({"disable_matte": mock_value})
        assert op.disable_matte == mock_value

    def test_disable_subd(self, init_operation, mocker):
        """Test the 'disable_subd' property."""
        mock_value = mocker.MagicMock(spec=bool)

        op = init_operation({"disable_subd": mock_value})

        assert op.disable_subd == mock_value

    def test_disable_tilecallback(self, init_operation, mocker):
        """Test the 'disable_tilecallback' property."""
        mock_value = mocker.MagicMock(spec=bool)

        op = init_operation({"disable_tilecallback": mock_value})

        assert op.disable_tilecallback == mock_value

    def test_res_scale(self, init_operation, mocker):
        """Test the 'res_scale' property."""
        mock_value = mocker.MagicMock(spec=float)

        op = init_operation({"res_scale": mock_value})
        assert op.res_scale == mock_value

    def test_sample_scale(self, init_operation, mocker):
        """Test the 'sample_scale' property."""
        mock_value = mocker.MagicMock(spec=float)

        op = init_operation({"sample_scale": mock_value})

        assert op.sample_scale == mock_value

    def test_transparent_samples(self, init_operation, mocker):
        """Test the 'transparent_samples' property."""
        mock_value = mocker.MagicMock(spec=int)

        op = init_operation({"transparent_samples": mock_value})
        assert op.transparent_samples == mock_value

    # Static Methods

    def test_build_arg_string(self):
        """Test arg string construction."""
        result = ipoverrides.IpOverrides.build_arg_string()

        assert result == ""

        # Res scale
        result = ipoverrides.IpOverrides.build_arg_string(res_scale=0.5)

        assert result == "--ip-res-scale=0.5"

        # Sample scale
        result = ipoverrides.IpOverrides.build_arg_string(sample_scale=0.5)

        assert result == "--ip-sample-scale=0.5"

        # Disable blur
        result = ipoverrides.IpOverrides.build_arg_string(disable_blur=True)

        assert result == "--ip-disable-blur"

        # Disable aovs
        result = ipoverrides.IpOverrides.build_arg_string(disable_aovs=True)

        assert result == "--ip-disable-aovs"

        # Disable deeps
        result = ipoverrides.IpOverrides.build_arg_string(disable_deep=True)

        assert result == "--ip-disable-deep"

        # Disable displacements
        result = ipoverrides.IpOverrides.build_arg_string(disable_displacement=True)

        assert result == "--ip-disable-displacement"

        # Disable matte and phantom objects
        result = ipoverrides.IpOverrides.build_arg_string(disable_matte=True)

        assert result == "--ip-disable-matte"

        # Disable subdivision surfaces
        result = ipoverrides.IpOverrides.build_arg_string(disable_subd=True)

        assert result == "--ip-disable-subd"

        # Disable tilecallback
        result = ipoverrides.IpOverrides.build_arg_string(disable_tilecallback=True)

        assert result == "--ip-disable-tilecallback"

        # Set the bucket size
        result = ipoverrides.IpOverrides.build_arg_string(bucket_size=16)

        assert result == "--ip-bucket-size=16"

        # Set the stochastic samples
        result = ipoverrides.IpOverrides.build_arg_string(transparent_samples=3)

        assert result == "--ip-transparent-samples=3"

    def test_register_parser_args(self, mocker):
        """Test registering all the argument parser args."""
        mock_parser = mocker.MagicMock(spec=argparse.ArgumentParser)

        ipoverrides.IpOverrides.register_parser_args(mock_parser)

        calls = [
            mocker.call(
                "--ip-res-scale", default=None, type=float, dest="ip_res_scale"
            ),
            mocker.call(
                "--ip-sample-scale", default=None, type=float, dest="ip_sample_scale"
            ),
            mocker.call(
                "--ip-disable-blur", action="store_true", dest="ip_disable_blur"
            ),
            mocker.call(
                "--ip-disable-aovs", action="store_true", dest="ip_disable_aovs"
            ),
            mocker.call(
                "--ip-disable-deep", action="store_true", dest="ip_disable_deep"
            ),
            mocker.call(
                "--ip-disable-displacement",
                action="store_true",
                dest="ip_disable_displacement",
            ),
            mocker.call(
                "--ip-disable-subd", action="store_true", dest="ip_disable_subd"
            ),
            mocker.call(
                "--ip-disable-tilecallback",
                action="store_true",
                dest="ip_disable_tilecallback",
            ),
            mocker.call(
                "--ip-disable-matte", action="store_true", dest="ip_disable_matte"
            ),
            mocker.call(
                "--ip-bucket-size",
                nargs="?",
                default=None,
                type=int,
                action="store",
                dest="ip_bucket_size",
            ),
            mocker.call(
                "--ip-transparent-samples",
                nargs="?",
                default=None,
                type=int,
                action="store",
                dest="ip_transparent_samples",
            ),
        ]
        mock_parser.add_argument.assert_has_calls(calls)

    # Methods

    # filter_camera

    def test_filter_camera__res_scale(
        self, patch_operation_logger, init_operation, properties, mocker
    ):
        """Test 'filter_camera' when scaling the resolution."""
        mock_scale = mocker.patch(
            "ht.pyfilter.operations.ipoverrides._scale_resolution"
        )

        op = init_operation({"res_scale": int}, as_properties=True)

        op.filter_camera()

        properties.mock_get.assert_called_with("image:resolution")
        mock_scale.assert_called_with(properties.mock_get.return_value, op.res_scale)
        properties.mock_set.assert_called_with(
            "image:resolution", mock_scale.return_value
        )

    def test_filter_camera__sample_scale(
        self, init_operation, properties, patch_operation_logger, mocker
    ):
        """Test 'filter_camera' when scaling the samples."""
        mock_scale = mocker.patch("ht.pyfilter.operations.ipoverrides._scale_samples")

        op = init_operation({"sample_scale": float}, as_properties=True)

        op.filter_camera()

        properties.mock_get.assert_called_with("image:samples")

        mock_scale.assert_called_with(properties.mock_get.return_value, op.sample_scale)

        properties.mock_set.assert_called_with("image:samples", mock_scale.return_value)

    def test_filter_camera__bucket_size(
        self, init_operation, properties, patch_operation_logger
    ):
        """Test 'filter_camera' when setting the bucket size."""
        op = init_operation({"bucket_size": int}, as_properties=True)

        op.filter_camera()

        properties.mock_set.assert_called_with("image:bucket", op.bucket_size)

    def test_filter_camera__disable_blur(
        self, init_operation, properties, patch_operation_logger, mocker
    ):
        """Test 'filter_camera' when disabling motion blur."""
        op = init_operation({"disable_blur": True}, as_properties=True)

        op.filter_camera()

        properties.mock_set.has_calls(
            [
                mocker.call("renderer:blurquality", 0),
                mocker.call("renderer:rayblurquality", 0),
            ]
        )

    def test_filter_camera__disable_deep(
        self, init_operation, properties, patch_operation_logger
    ):
        """Test 'filter_camera' when disabling motion deep images."""
        op = init_operation({"disable_deep": True}, as_properties=True)

        op.filter_camera()

        properties.mock_set.assert_called_with("image:deepresolver", [])

    def test_filter_camera__disable_tilecallback(
        self, init_operation, properties, patch_operation_logger
    ):
        """Test 'filter_camera' when disabling the tile callback."""
        op = init_operation({"disable_tilecallback": True}, as_properties=True)

        op.filter_camera()

        properties.mock_set.assert_called_with("render:tilecallback", "")

    def test_filter_camera__transparent_samples(
        self, init_operation, properties, patch_operation_logger
    ):
        """Test 'filter_camera' when setting the transparent samples."""
        op = init_operation({"transparent_samples": int}, as_properties=True)

        op.filter_camera()

        properties.mock_set.assert_any_call(
            "image:transparentsamples", op.transparent_samples
        )

    # filter_instance

    def test_filter_instance__disable_displacement(
        self, init_operation, patch_operation_logger, properties
    ):
        """Test 'filter_instance' when disabling displacements."""
        op = init_operation({"disable_displacement": True}, as_properties=True)

        op.filter_instance()

        properties.mock_set.assert_called_with("object:displace", [])

    def test_filter_instance__disable_subd(
        self, init_operation, properties, patch_operation_logger
    ):
        """Test 'filter_instance' when disabling subd's."""
        op = init_operation({"disable_subd": True}, as_properties=True)

        op.filter_instance()

        properties.mock_set.assert_called_with("object:rendersubd", 0)

    def test_filter_instance__disable_matte_matte_object(
        self, init_operation, properties, patch_operation_logger
    ):
        """Test 'filter_instance' when disabling matte on an object which
        is rendering as a matte object.

        """
        op = init_operation({"disable_matte": True}, as_properties=True)

        values = {"object:matte": True, "object:phantom": False}

        properties.mock_get.side_effect = values.get

        op.filter_instance()

        properties.mock_get.assert_called_with("object:matte")
        properties.mock_set.assert_called_with("object:renderable", False)

    def test_filter_instance__disable_matte_phantom_object(
        self, init_operation, properties, patch_operation_logger, mocker
    ):
        """Test 'filter_instance' when disabling matte on an object which
        is rendering as a phantom object.

        """
        op = init_operation({"disable_matte": True}, as_properties=True)

        values = {"object:matte": False, "object:phantom": True}

        properties.mock_get.side_effect = values.get

        op.filter_instance()

        properties.mock_get.assert_has_calls(
            [mocker.call("object:matte"), mocker.call("object:phantom")]
        )
        properties.mock_set.assert_called_with("object:renderable", False)

    def test_filter_instance__disable_matte_surface_matte(
        self, init_operation, properties, patch_operation_logger, mocker
    ):
        """Test 'filter_instance' when disabling matte on an object which
        is has a matte shader applied.

        """
        op = init_operation({"disable_matte": True}, as_properties=True)

        values = {
            "object:matte": False,
            "object:phantom": False,
            "object:surface": "opdef:/Shop/v_matte",
        }

        properties.mock_get.side_effect = values.get

        op.filter_instance()

        properties.mock_get.assert_has_calls(
            [
                mocker.call("object:matte"),
                mocker.call("object:phantom"),
                mocker.call("object:surface"),
            ]
        )
        properties.mock_set.assert_called_with("object:renderable", False)

    def test_filter_instance__disable_matte_noop(
        self, init_operation, properties, patch_operation_logger, mocker
    ):
        """Test 'filter_instance' when disabling matte when the object is
        not a matte.

        """
        op = init_operation({"disable_matte": True}, as_properties=True)

        values = {
            "object:matte": False,
            "object:phantom": False,
            "object:surface": "opdef:/Shop/v_thing",
        }

        properties.mock_get.side_effect = values.get

        op.filter_instance()

        properties.mock_get.assert_has_calls(
            [
                mocker.call("object:matte"),
                mocker.call("object:phantom"),
                mocker.call("object:surface"),
            ]
        )
        properties.mock_set.assert_not_called()

    # filter_material

    def test_filter_material__disable_displacement(
        self, init_operation, properties, patch_operation_logger
    ):
        """Test 'filter_material' when disabling displacement."""
        op = init_operation({"disable_displacement": True}, as_properties=True)

        op.filter_material()

        properties.mock_set.assert_called_with("object:displace", [])

    def test_filter_material__no_disable(
        self, init_operation, properties, patch_operation_logger
    ):
        """Test 'filter_material' when not disabling displacement."""
        op = init_operation({"disable_displacement": False}, as_properties=True)

        op.filter_material()

        properties.mock_set.assert_not_called()

    # filter_plane

    def test_filter_plane__noop(
        self, init_operation, properties, patch_operation_logger
    ):
        """Test 'filter_plane' when not disabling."""
        op = init_operation()

        op.filter_plane()

        properties.mock_get.assert_not_called()
        properties.mock_set.assert_not_called()

    def test_filter_plane__disable_aovs(
        self, init_operation, properties, patch_operation_logger, mocker
    ):
        """Test 'filter_plane' when disabling a plane which can be disabled."""
        properties.mock_get.return_value = mocker.MagicMock(spec=str)

        op = init_operation({"disable_aovs": True}, as_properties=True)

        op.filter_plane()

        properties.mock_set.assert_called_with("plane:disable", 1)

    def test_filter_plane__disable_aovs_cf(
        self, init_operation, properties, patch_operation_logger
    ):
        """Test 'filter_plane' when disabling just a 'Cf' plane."""
        properties.mock_get.return_value = "Cf"

        op = init_operation({"disable_aovs": True}, as_properties=True)

        op.filter_plane()

        properties.mock_set.assert_called_with("plane:disable", 1)

    def test_filter_plane__disable_aovs_cf_af(
        self, init_operation, properties, patch_operation_logger
    ):
        """Test 'filter_plane' when disabling just a 'Cf+Af' plane."""
        properties.mock_get.return_value = "Cf+Af"

        op = init_operation({"disable_aovs": True}, as_properties=True)

        op.filter_plane()

        properties.mock_set.assert_not_called()

    # process_parsed_args

    def test_process_parsed_args(self, init_operation):
        """Test processing parsed args when all args are set."""
        namespace = argparse.Namespace()
        namespace.ip_res_scale = 0.5
        namespace.ip_sample_scale = 0.75
        namespace.ip_disable_aovs = True
        namespace.ip_disable_blur = True
        namespace.ip_disable_deep = True
        namespace.ip_disable_displacement = True
        namespace.ip_disable_matte = True
        namespace.ip_disable_subd = True
        namespace.ip_bucket_size = 16
        namespace.ip_transparent_samples = 3
        namespace.ip_disable_tilecallback = True

        op = init_operation()

        op.process_parsed_args(namespace)

        assert op._res_scale == 0.5
        assert op._sample_scale == 0.75
        assert op._disable_aovs
        assert op._disable_blur
        assert op._disable_deep
        assert op._disable_displacement
        assert op._disable_matte
        assert op._disable_subd
        assert op._disable_tilecallback
        assert op._bucket_size == 16
        assert op._transparent_samples == 3

    def test_process_parsed_args__noop(self, init_operation):
        """Test processing parsed args when no args are set."""
        namespace = argparse.Namespace()
        namespace.ip_res_scale = None
        namespace.ip_sample_scale = None
        namespace.ip_bucket_size = None
        namespace.ip_transparent_samples = None
        namespace.ip_disable_aovs = False
        namespace.ip_disable_blur = False
        namespace.ip_disable_deep = False
        namespace.ip_disable_displacement = False
        namespace.ip_disable_matte = False
        namespace.ip_disable_subd = False
        namespace.ip_disable_tilecallback = False

        op = init_operation()

        op._res_scale = 0.5
        op._sample_scale = 0.75
        op._bucket_size = 16
        op._transparent_samples = 3
        op._disable_aovs = False
        op._disable_blur = False
        op._disable_deep = False
        op._disable_displacement = False
        op._disable_matte = False
        op._disable_subd = False
        op._disable_tilecallback = False

        op.process_parsed_args(namespace)

        assert op._res_scale == 0.5
        assert op._sample_scale == 0.75
        assert op._bucket_size == 16
        assert op._transparent_samples == 3

    # should_run

    def test_should_run(self, init_operation, properties):
        """Test whether or not the operation should run."""
        op = init_operation({"res_scale": float}, as_properties=True)

        # Not ip, so it can't run.
        assert not op.should_run()

        # Need to mimic rendering to ip.
        properties.mock_get.return_value = "ip"

        op = init_operation(as_properties=True)

        # Can't run if ip but nothing else is set.
        assert not op.should_run()

        # Values to check
        data = dict(
            bucket_size=int,
            disable_aovs=True,
            disable_blur=True,
            disable_deep=True,
            disable_displacement=True,
            disable_matte=True,
            disable_subd=True,
            disable_tilecallback=True,
            res_scale=float,
            sample_scale=float,
            transparent_samples=int,
        )

        # Create an operation with each property set and ip set.
        for key, value in list(data.items()):
            op = init_operation({key: value}, as_properties=True)

            assert op.should_run()


@pytest.mark.parametrize(
    "resolution,scale,expected",
    [
        ((1920, 1080), 1.0, [1920, 1080]),
        ((1920, 1080), 0.5, [960, 540]),
        ((1920, 1080), 0.333, [639, 360]),
    ],
)
def test__scale_resolution(resolution, scale, expected):
    """Test the ht.pyfilter.operations.ipoverrides._scale_resolution."""
    assert ipoverrides._scale_resolution(resolution, scale) == expected


@pytest.mark.parametrize(
    "samples,scale,expected",
    [((10, 10), 1.0, [10, 10]), ((10, 10), 0.5, [5, 5]), ((10, 10), 0.333, [4, 4])],
)
def test__scale_sample_value(samples, scale, expected):
    """Test the ht.pyfilter.operations.ipoverrides._scale_sample_value."""
    assert ipoverrides._scale_samples(samples, scale) == expected


class Test_build_arg_string_from_node:
    """Test the ht.pyfilter.operations.ipoverrides.build_arg_string_from_node."""

    def test(self, mocker):
        """Test with scaling."""
        mock_build = mocker.patch(
            "ht.pyfilter.operations.ipoverrides.IpOverrides.build_arg_string"
        )

        mock_node = mocker.MagicMock()
        mock_node.evalParm.return_value = 0

        assert ipoverrides.build_arg_string_from_node(mock_node) == ""

        parm_data = {
            "enable_ip_override": 1,
            "ip_override_camerares": 1,
            "ip_res_fraction": 0.5,
            "ip_transparent": 1,
            "ip_transparent_samples": 3,
            "ip_sample_scale": 0.5,
            "ip_disable_blur": 1,
            "ip_disable_aovs": 1,
            "ip_disable_deep": 1,
            "ip_disable_displacement": 1,
            "ip_disable_matte": 1,
            "ip_disable_subd": 1,
            "ip_disable_tilecallback": 1,
            "ip_bucket_size": 16,
        }

        mock_node.evalParm.side_effect = lambda name: parm_data[name]

        assert (
            ipoverrides.build_arg_string_from_node(mock_node) == mock_build.return_value
        )

        mock_build.assert_called_with(
            res_scale=parm_data["ip_res_fraction"],
            sample_scale=parm_data["ip_sample_scale"],
            disable_blur=parm_data["ip_disable_blur"],
            disable_aovs=parm_data["ip_disable_aovs"],
            disable_deep=parm_data["ip_disable_deep"],
            disable_displacement=parm_data["ip_disable_displacement"],
            disable_matte=parm_data["ip_disable_matte"],
            disable_subd=parm_data["ip_disable_subd"],
            disable_tilecallback=parm_data["ip_disable_tilecallback"],
            bucket_size=parm_data["ip_bucket_size"],
            transparent_samples=parm_data["ip_transparent_samples"],
        )

    def test_no_scales(self, mocker):
        """Test with no scaling."""
        mock_build = mocker.patch(
            "ht.pyfilter.operations.ipoverrides.IpOverrides.build_arg_string"
        )

        mock_node = mocker.MagicMock()
        mock_node.evalParm.return_value = 0

        assert ipoverrides.build_arg_string_from_node(mock_node) == ""

        parm_data = {
            "enable_ip_override": 1,
            "ip_override_camerares": 0,
            "ip_transparent": 0,
            "ip_sample_scale": 0.5,
            "ip_disable_blur": 1,
            "ip_disable_aovs": 1,
            "ip_disable_deep": 1,
            "ip_disable_displacement": 1,
            "ip_disable_matte": 1,
            "ip_disable_subd": 1,
            "ip_disable_tilecallback": 1,
            "ip_bucket_size": 16,
        }

        mock_node.evalParm.side_effect = lambda name: parm_data[name]

        assert (
            ipoverrides.build_arg_string_from_node(mock_node) == mock_build.return_value
        )

        mock_build.assert_called_with(
            res_scale=None,
            sample_scale=parm_data["ip_sample_scale"],
            disable_blur=parm_data["ip_disable_blur"],
            disable_aovs=parm_data["ip_disable_aovs"],
            disable_deep=parm_data["ip_disable_deep"],
            disable_displacement=parm_data["ip_disable_displacement"],
            disable_subd=parm_data["ip_disable_subd"],
            disable_tilecallback=parm_data["ip_disable_tilecallback"],
            bucket_size=parm_data["ip_bucket_size"],
            transparent_samples=None,
            disable_matte=parm_data["ip_disable_matte"],
        )


def test_build_pixel_sample_scale_display(mocker):
    """Test the ht.pyfilter.operations.ipoverrides.build_pixel_sample_scale_display."""
    mock_scale = mocker.patch("ht.pyfilter.operations.ipoverrides._scale_samples")

    source_samples = (6, 6)
    target_samples = (3, 3)
    scale = 0.5

    mock_node = mocker.MagicMock()
    mock_node.evalParmTuple.return_value = source_samples
    mock_node.evalParm.return_value = scale

    mock_scale.return_value = target_samples

    result = ipoverrides.build_pixel_sample_scale_display(mock_node)

    mock_node.evalParmTuple.assert_called_with("vm_samples")
    mock_node.evalParm.assert_called_with("ip_sample_scale")
    mock_scale.assert_called_with(source_samples, scale)
    assert result == f"{target_samples[0]}x{target_samples[1]}"


class Test_build_resolution_scale_display:
    """Test the ht.pyfilter.operations.ipoverrides.build_resolution_scale_display."""

    def test_no_camera(self, mocker):
        """Test when there is no target camera."""
        mock_node = mocker.MagicMock(spec=hou.RopNode)
        mock_node.parm.return_value.evalAsNode.return_value = None

        result = ipoverrides.build_resolution_scale_display(mock_node)

        assert result == ""

        mock_node.parm.assert_called_with("camera")

    def test_no_override(self, mocker):
        """Test when there is no override being applied on the Mantra ROP."""
        mock_scale = mocker.patch(
            "ht.pyfilter.operations.ipoverrides._scale_resolution"
        )

        mock_scale.return_value = (960, 540)

        mock_camera = mocker.MagicMock(spec=hou.ObjNode)
        mock_camera.evalParmTuple.return_value = (1920, 1080)

        parm_values = {"override_camerares": False, "ip_res_fraction": "0.5"}

        mock_node = mocker.MagicMock(spec=hou.RopNode)
        mock_node.parm.return_value.evalAsNode.return_value = mock_camera

        mock_node.evalParm.side_effect = lambda name: parm_values[name]

        result = ipoverrides.build_resolution_scale_display(mock_node)

        assert result == "960x540"

        mock_node.parm.assert_called_with("camera")

        mock_scale.assert_called_with((1920, 1080), 0.5)

    def test_override_specific(self, mocker):
        """Test when there is a specific resolution override being applied on the Mantra ROP."""
        mock_scale = mocker.patch(
            "ht.pyfilter.operations.ipoverrides._scale_resolution"
        )
        mock_scale.return_value = (250, 250)

        mock_camera = mocker.MagicMock(spec=hou.ObjNode)
        mock_camera.evalParmTuple.return_value = (1920, 1080)

        parm_values = {
            "override_camerares": 1,
            "ip_res_fraction": "0.25",
            "res_fraction": "specific",
        }

        mock_node = mocker.MagicMock(spec=hou.RopNode)
        mock_node.parm.return_value.evalAsNode.return_value = mock_camera
        mock_node.evalParmTuple.return_value = (1000, 1000)
        mock_node.evalParm.side_effect = lambda name: parm_values[name]

        result = ipoverrides.build_resolution_scale_display(mock_node)

        assert result == "250x250"

        mock_node.parm.assert_called_with("camera")

        mock_scale.assert_called_with((1000, 1000), 0.25)

    def test_override_scaled(self, mocker):
        """Test when there is a resolution scale override being applied on the Mantra ROP."""
        mock_scale = mocker.patch(
            "ht.pyfilter.operations.ipoverrides._scale_resolution"
        )
        mock_scale.side_effect = ((960, 540), (480, 270))

        mock_camera = mocker.MagicMock(spec=hou.ObjNode)
        mock_camera.evalParmTuple.return_value = (1920, 1080)

        parm_values = {
            "override_camerares": 1,
            "ip_res_fraction": "0.5",
            "res_fraction": "0.5",
        }

        mock_node = mocker.MagicMock(spec=hou.RopNode)
        mock_node.parm.return_value.evalAsNode.return_value = mock_camera
        mock_node.evalParmTuple.return_value = (1000, 1000)
        mock_node.evalParm.side_effect = lambda name: parm_values[name]

        result = ipoverrides.build_resolution_scale_display(mock_node)

        assert result == "480x270"

        mock_node.parm.assert_called_with("camera")

        calls = [mocker.call((1920, 1080), 0.5), mocker.call((960, 540), 0.5)]
        mock_scale.assert_has_calls(calls)


def test_build_pyfilter_command_from_node(mocker):
    """Test the ht.pyfilter.operations.ipoverrides.build_pyfilter_command_from_node."""
    mock_build_arg = mocker.patch(
        "ht.pyfilter.operations.ipoverrides.build_arg_string_from_node"
    )
    mock_build_command = mocker.patch(
        "ht.pyfilter.operations.ipoverrides.build_pyfilter_command"
    )

    mock_node = mocker.MagicMock(spec=hou.RopNode)

    assert (
        ipoverrides.build_pyfilter_command_from_node(mock_node)
        == mock_build_command.return_value
    )

    mock_build_arg.assert_called_with(mock_node)
    mock_build_command.assert_called_with(
        mock_build_arg.return_value.split.return_value
    )


def test_set_mantra_command(mocker):
    """Test the ht.pyfilter.operations.ipoverrides.set_mantra_command."""

    mock_node = mocker.MagicMock(spec=hou.RopNode)

    ipoverrides.set_mantra_command(mock_node)

    mock_node.parm.return_value.set.assert_called_with(
        "mantra `pythonexprs(\"__import__('ht.pyfilter.operations', globals(), locals(), ['ipoverrides']).ipoverrides.build_pyfilter_command_from_node(hou.pwd())\")`"
    )

    mock_node.parm.assert_called_with("soho_pipecmd")
