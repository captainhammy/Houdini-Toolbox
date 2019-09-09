"""Test the ht.pyfilter.operations.ipoverrides module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import argparse

# Third Party Imports
from mock import MagicMock, call, patch

# Houdini Toolbox Imports
from ht.pyfilter.manager import PyFilterManager
from ht.pyfilter.operations import ipoverrides

# Houdini Imports
import hou


# =============================================================================
# CLASSES
# =============================================================================

class Test_IpOverrides(object):
    """Test the ht.pyfilter.operations.ipoverrides.IpOverride class.    """

    def test___init__(self):
        mock_manager = MagicMock(spec=PyFilterManager)
        op = ipoverrides.IpOverrides(mock_manager)

        assert op._data == {}
        assert op._manager == mock_manager

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

    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_bucket_size(self):
        op = ipoverrides.IpOverrides(None)
        op._bucket_size = 16
        assert op.bucket_size == 16

        op = ipoverrides.IpOverrides(None)
        op._bucket_size = 8
        op.bucket_size = 16
        assert op._bucket_size == 16

    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_disable_aovs(self):
        op = ipoverrides.IpOverrides(None)
        op._disable_aovs = True
        assert op.disable_aovs

        op = ipoverrides.IpOverrides(None)
        op._disable_aovs = False
        op.disable_aovs = True
        assert op._disable_aovs

    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_disable_blur(self):
        op = ipoverrides.IpOverrides(None)
        op._disable_blur = True
        assert op.disable_blur

        op = ipoverrides.IpOverrides(None)
        op._disable_blur = False
        op.disable_blur = True
        assert op._disable_blur

    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_disable_deep(self):
        op = ipoverrides.IpOverrides(None)
        op._disable_deep = True
        assert op.disable_deep

        op = ipoverrides.IpOverrides(None)
        op._disable_deep = False
        op.disable_deep = True
        assert op._disable_deep

    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_disable_displacement(self):
        op = ipoverrides.IpOverrides(None)
        op._disable_displacement = True
        assert op.disable_displacement

        op = ipoverrides.IpOverrides(None)
        op._disable_displacement = False
        op.disable_displacement = True
        assert op._disable_displacement

    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_disable_matte(self):
        op = ipoverrides.IpOverrides(None)
        op._disable_matte = True
        assert op.disable_matte

        op = ipoverrides.IpOverrides(None)
        op._disable_matte = False
        op.disable_matte = True
        assert op._disable_matte

    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_disable_subd(self):
        op = ipoverrides.IpOverrides(None)
        op._disable_subd = True
        assert op.disable_subd

        op = ipoverrides.IpOverrides(None)
        op._disable_subd = False
        op.disable_subd = True
        assert op._disable_subd

    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_res_scale(self):
        op = ipoverrides.IpOverrides(None)
        op._res_scale = 0.5
        assert op.res_scale == 0.5

        op = ipoverrides.IpOverrides(None)
        op._res_scale = 1
        op.res_scale = 0.5
        assert op._res_scale == 0.5

    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_sample_scale(self):
        op = ipoverrides.IpOverrides(None)
        op._sample_scale = 0.5
        assert op.sample_scale == 0.5

        op = ipoverrides.IpOverrides(None)
        op._sample_scale = 1
        op.sample_scale = 0.5
        assert op._sample_scale == 0.5

    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_transparent_samples(self):
        op = ipoverrides.IpOverrides(None)
        op._transparent_samples = 4
        assert op.transparent_samples == 4

        op = ipoverrides.IpOverrides(None)
        op._transparent_samples = 1
        op.transparent_samples = 4
        assert op._transparent_samples == 4

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

        assert result  == "--ip-sample-scale=0.5"

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

    def test_register_parser_args(self):
        """Test registering all the argument parser args."""

        mock_parser = MagicMock(spec=argparse.ArgumentParser)

        ipoverrides.IpOverrides.register_parser_args(mock_parser)

        calls = [
            call("--ip-res-scale", default=None, type=float, dest="ip_res_scale"),
            call("--ip-sample-scale", default=None, type=float, dest="ip_sample_scale"),
            call("--ip-disable-blur", action="store_true", dest="ip_disable_blur"),
            call("--ip-disable-aovs", action="store_true", dest="ip_disable_aovs"),
            call("--ip-disable-deep", action="store_true", dest="ip_disable_deep"),
            call("--ip-disable-displacement", action="store_true", dest="ip_disable_displacement"),
            call("--ip-disable-subd", action="store_true", dest="ip_disable_subd"),
            call("--ip-disable-tilecallback", action="store_true", dest="ip_disable_tilecallback"),
            call("--ip-disable-matte", action="store_true", dest="ip_disable_matte"),
            call("--ip-bucket-size", nargs="?", default=None, type=int, dest="ip_bucket_size", action="store"),
            call("--ip-transparent-samples", nargs="?", default=None, type=int, action="store", dest="ip_transparent_samples")
        ]
        mock_parser.add_argument.assert_has_calls(calls)

    # Methods

    # filter_camera

    @patch("ht.pyfilter.operations.ipoverrides._scale_resolution")
    @patch("ht.pyfilter.operations.ipoverrides.set_property")
    @patch("ht.pyfilter.operations.ipoverrides.get_property")
    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_filter_camera_res_scale(self, mock_get, mock_set, mock_scale, patch_operation_logger):
        op = ipoverrides.IpOverrides(None)
        op._res_scale = 0.5
        op._sample_scale = None
        op._bucket_size = None
        op._disable_blur = False
        op._disable_deep = False
        op._disable_tilecallback = False
        op._transparent_samples = None

        source_res = [1920, 1080]
        target_res = [960, 540]

        mock_get.return_value = source_res
        mock_scale.return_value = target_res

        op.filter_camera()

        mock_get.assert_called_with("image:resolution")
        mock_scale.assert_called_with(source_res, 0.5)
        mock_set.assert_called_with("image:resolution", target_res)

    @patch("ht.pyfilter.operations.ipoverrides._scale_samples")
    @patch("ht.pyfilter.operations.ipoverrides.set_property")
    @patch("ht.pyfilter.operations.ipoverrides.get_property")
    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_filter_camera_sample_scale(self, mock_get, mock_set, mock_scale, patch_operation_logger):
        op = ipoverrides.IpOverrides(None)
        op._res_scale = None
        op._sample_scale = 0.5
        op._bucket_size = None
        op._disable_blur = False
        op._disable_deep = False
        op._disable_tilecallback = False
        op._transparent_samples = None

        source_samples = [10, 10]
        target_samples = [5, 5]

        mock_get.return_value = source_samples
        mock_scale.return_value = target_samples

        op.filter_camera()

        mock_get.assert_called_with("image:samples")
        mock_scale.assert_called_with(source_samples, 0.5)
        mock_set.assert_called_with("image:samples", target_samples)

    @patch("ht.pyfilter.operations.ipoverrides.set_property")
    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_filter_camera_bucket_size(self, mock_set, patch_operation_logger):
        op = ipoverrides.IpOverrides(None)
        op._res_scale = None
        op._sample_scale = None
        op._bucket_size = 16
        op._disable_blur = False
        op._disable_deep = False
        op._disable_tilecallback = False
        op._transparent_samples = None

        op.filter_camera()

        mock_set.assert_called_with("image:bucket", 16)

    @patch("ht.pyfilter.operations.ipoverrides.set_property")
    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_filter_camera_disable_blur(self, mock_set, patch_operation_logger):
        op = ipoverrides.IpOverrides(None)
        op._res_scale = None
        op._sample_scale = None
        op._bucket_size = None
        op._disable_blur = True
        op._disable_deep = False
        op._disable_tilecallback = False
        op._transparent_samples = None

        op.filter_camera()

        mock_set.has_calls([call("renderer:blurquality", 0), call("renderer:rayblurquality", 0)])

    @patch("ht.pyfilter.operations.ipoverrides.set_property")
    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_filter_camera_disable_deep(self, mock_set, patch_operation_logger):
        op = ipoverrides.IpOverrides(None)
        op._res_scale = None
        op._sample_scale = None
        op._bucket_size = None
        op._disable_blur = False
        op._disable_deep = True
        op._disable_tilecallback = False
        op._transparent_samples = None

        op.filter_camera()

        mock_set.assert_called_with("image:deepresolver", [])

    @patch("ht.pyfilter.operations.ipoverrides.set_property")
    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_filter_camera_disable_tilecallback(self, mock_set, patch_operation_logger):
        op = ipoverrides.IpOverrides(None)
        op._res_scale = None
        op._sample_scale = None
        op._bucket_size = None
        op._disable_blur = False
        op._disable_deep = False
        op._disable_tilecallback = True
        op._transparent_samples = None

        op.filter_camera()

        mock_set.assert_called_with("render:tilecallback", "")

    @patch("ht.pyfilter.operations.ipoverrides.set_property")
    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_filter_camera_transparent_samples(self, mock_set, patch_operation_logger):
        op = ipoverrides.IpOverrides(None)
        op._res_scale = None
        op._sample_scale = None
        op._bucket_size = None
        op._disable_blur = False
        op._disable_deep = False
        op._disable_tilecallback = False
        op._transparent_samples = 3

        op.filter_camera()

        mock_set.assert_any_call("image:transparentsamples", 3)

    # filter_instance

    @patch("ht.pyfilter.operations.ipoverrides.set_property")
    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_filter_instance_noop(self, mock_set, patch_operation_logger):
        op = ipoverrides.IpOverrides(None)
        op._disable_displacement = False
        op._disable_subd = False
        op._disable_matte = False

        op.filter_instance()

        mock_set.assert_not_called()

    @patch("ht.pyfilter.operations.ipoverrides.set_property")
    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_filter_instance_disable_displacement(self, mock_set, patch_operation_logger):
        op = ipoverrides.IpOverrides(None)
        op._disable_displacement = True
        op._disable_subd = False
        op._disable_matte = False

        op.filter_instance()

        mock_set.assert_called_with("object:displace", [])

    @patch("ht.pyfilter.operations.ipoverrides.set_property")
    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_filter_instance_disable_subd(self, mock_set, patch_operation_logger):
        op = ipoverrides.IpOverrides(None)
        op._disable_displacement = False
        op._disable_subd = True
        op._disable_matte = False

        op.filter_instance()

        mock_set.assert_called_with("object:rendersubd", 0)

    @patch("ht.pyfilter.operations.ipoverrides.get_property")
    @patch("ht.pyfilter.operations.ipoverrides.set_property")
    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_filter_instance_disable_matte_matte_object(self, mock_set, mock_get, patch_operation_logger):
        op = ipoverrides.IpOverrides(None)
        op._disable_displacement = False
        op._disable_subd = False
        op._disable_matte = True

        values = {
            "object:matte": True,
            "object:phantom": False,
        }

        mock_get.side_effect = lambda name: values.get(name)

        op.filter_instance()

        mock_get.assert_called_with("object:matte")

        mock_set.assert_called_with("object:renderable", False)

    @patch("ht.pyfilter.operations.ipoverrides.get_property")
    @patch("ht.pyfilter.operations.ipoverrides.set_property")
    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_filter_instance_disable_matte_phantom_object(self, mock_set, mock_get, patch_operation_logger):
        op = ipoverrides.IpOverrides(None)
        op._disable_displacement = False
        op._disable_subd = False
        op._disable_matte = True

        values = {
            "object:matte": False,
            "object:phantom": True,
        }

        mock_get.side_effect = lambda name: values.get(name)

        op.filter_instance()

        mock_get.assert_has_calls([call("object:matte"), call("object:phantom")])
        mock_set.assert_called_with("object:renderable", False)

    @patch("ht.pyfilter.operations.ipoverrides.get_property")
    @patch("ht.pyfilter.operations.ipoverrides.set_property")
    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_filter_instance_disable_matte_surface_matte(self, mock_set, mock_get, patch_operation_logger):
        op = ipoverrides.IpOverrides(None)
        op._disable_displacement = False
        op._disable_subd = False
        op._disable_matte = True

        values = {
            "object:matte": False,
            "object:phantom": False,
            "object:surface": "opdef:/Shop/v_matte"
        }

        mock_get.side_effect = lambda name: values.get(name)

        op.filter_instance()

        mock_get.assert_has_calls([call("object:matte"), call("object:phantom"), call("object:surface")])
        mock_set.assert_called_with("object:renderable", False)

    @patch("ht.pyfilter.operations.ipoverrides.get_property")
    @patch("ht.pyfilter.operations.ipoverrides.set_property")
    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_filter_instance_disable_matte_noop(self, mock_set, mock_get, patch_operation_logger):
        op = ipoverrides.IpOverrides(None)
        op._disable_displacement = False
        op._disable_subd = False
        op._disable_matte = True

        values = {
            "object:matte": False,
            "object:phantom": False,
            "object:surface": "opdef:/Shop/v_thing"
        }

        mock_get.side_effect = lambda name: values.get(name)

        op.filter_instance()

        mock_get.assert_has_calls([call("object:matte"), call("object:phantom"), call("object:surface")])
        mock_set.assert_not_called()

    # filter_material

    @patch("ht.pyfilter.operations.ipoverrides.set_property")
    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_filter_material_disable_displacement(self, mock_set, patch_operation_logger):
        op = ipoverrides.IpOverrides(None)
        op._disable_displacement = True

        op.filter_material()

        mock_set.assert_called_with("object:displace", [])

    @patch("ht.pyfilter.operations.ipoverrides.set_property")
    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_filter_material_no_disable(self, mock_set, patch_operation_logger):
        op = ipoverrides.IpOverrides(None)
        op._disable_displacement = False

        op.filter_material()

        mock_set.assert_not_called()

    # filter_plane

    @patch("ht.pyfilter.operations.ipoverrides.set_property")
    @patch("ht.pyfilter.operations.ipoverrides.get_property")
    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_filter_plane_noop(self, mock_get, mock_set, patch_operation_logger):
        op = ipoverrides.IpOverrides(None)
        op._disable_aovs = False
        op.filter_plane()

        mock_get.assert_not_called()
        mock_set.assert_not_called()

    @patch("ht.pyfilter.operations.ipoverrides.set_property")
    @patch("ht.pyfilter.operations.ipoverrides.get_property")
    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_filter_plane_disable_aovs(self, mock_get, mock_set, patch_operation_logger):
        mock_get.return_value = "channel1"

        op = ipoverrides.IpOverrides(None)
        op._disable_aovs = True

        op.filter_plane()

        mock_set.assert_called_with("plane:disable", 1)

    @patch("ht.pyfilter.operations.ipoverrides.set_property")
    @patch("ht.pyfilter.operations.ipoverrides.get_property")
    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_filter_plane_disable_aovs_Cf(self, mock_get, mock_set, patch_operation_logger):
        mock_get.return_value = "Cf"

        op = ipoverrides.IpOverrides(None)
        op._disable_aovs = True

        op.filter_plane()

        mock_set.assert_called_with("plane:disable", 1)

    @patch("ht.pyfilter.operations.ipoverrides.set_property")
    @patch("ht.pyfilter.operations.ipoverrides.get_property")
    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_filter_plane_disable_aovs_Cf_Af(self, mock_get, mock_set, patch_operation_logger):
        mock_get.return_value = "Cf+Af"

        op = ipoverrides.IpOverrides(None)
        op._disable_aovs = True

        op.filter_plane()

        mock_set.assert_not_called()

    # process_parsed_args

    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_process_parsed_args(self):
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

        op = ipoverrides.IpOverrides(None)

        op._res_scale = None
        op._sample_scale = None
        op._bucket_size = None
        op._transparent_samples = None
        op._disable_aovs = False
        op._disable_blur = False
        op._disable_deep = False
        op._disable_displacement = False
        op._disable_matte = False
        op._disable_subd = False
        op._disable_tilecallback = False

        op.process_parsed_args(namespace)

        assert op.res_scale == 0.5
        assert op.sample_scale == 0.75
        assert op.disable_aovs
        assert op.disable_blur
        assert op.disable_deep
        assert op.disable_displacement
        assert op.disable_matte
        assert op.disable_subd
        assert op.disable_tilecallback
        assert op.bucket_size == 16
        assert op.transparent_samples == 3

    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_process_parsed_args__none(self):
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

        op = ipoverrides.IpOverrides(None)

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

        assert op.res_scale == 0.5
        assert op.sample_scale == 0.75
        assert op.bucket_size == 16
        assert op.transparent_samples == 3

    # should_run

    @patch("ht.pyfilter.operations.ipoverrides.get_property")
    @patch.object(ipoverrides.IpOverrides, "__init__", lambda x, y: None)
    def test_should_run(self, mock_get):
        op = ipoverrides.IpOverrides(None)

        op._res_scale = None
        op._sample_scale = None
        op._bucket_size = None
        op._transparent_samples = None
        op._disable_aovs = False
        op._disable_blur = False
        op._disable_deep = False
        op._disable_displacement = False
        op._disable_matte = False
        op._disable_subd = False
        op._disable_tilecallback = False

        assert not op.should_run()

        # Can't run if something is set but not ip.
        op.res_scale = 0.5
        assert not op.should_run()
        op.res_scale = None

        # Can't run if ip but nothing else is set.
        mock_get.return_value = "ip"
        assert not op.should_run()

        op.res_scale = 0.5
        assert op.should_run()
        op.res_scale = None

        op.sample_scale = 0.5
        assert op.should_run()
        op.sample_scale = None

        op.disable_blur = True
        assert op.should_run()
        op.disable_blur = False

        op.disable_aovs = True
        assert op.should_run()
        op.disable_aovs = False

        op.disable_displacement = True
        assert op.should_run()
        op.disable_displacement = False

        op.disable_matte = True
        assert op.should_run()
        op.disable_matte = False

        op.disable_subd = True
        assert op.should_run()
        op.disable_subd = False

        op.disable_tilecallback = True
        assert op.should_run()
        op.disable_tilecallback = False

        op.bucket_size = 16
        assert op.should_run()
        op.bucket_size = None

        op.transparent_samples = 2
        assert op.should_run()
        op.transparent_samples = None


def test__scale_resolution():
    """Test the ht.pyfilter.operations.ipoverrides._scale_resolution."""

    source = [1920, 1080]
    target = [1920, 1080]
    scale = 1.0

    result = ipoverrides._scale_resolution(source, scale)
    assert result == target

    source = [1920, 1080]
    target = [960, 540]
    scale = 0.5

    result = ipoverrides._scale_resolution(source, scale)
    assert result == target

    source = [1920, 1080]
    target = [639, 360]
    scale = 0.333

    result = ipoverrides._scale_resolution(source, scale)
    assert result == target


def test__scale_sample_value():
    """Test the ht.pyfilter.operations.ipoverrides._scale_sample_value."""

    source = [10, 10]
    target = [10, 10]
    scale = 1.0

    result = ipoverrides._scale_samples(source, scale)
    assert result == target

    source = [10, 10]
    target = [5, 5]
    scale = 0.5

    result = ipoverrides._scale_samples(source, scale)
    assert result == target

    source = [10, 10]
    target = [4, 4]
    scale = 0.333

    result = ipoverrides._scale_samples(source, scale)
    assert result == target


class Test_build_arg_string_from_node(object):
    """Test the ht.pyfilter.operations.ipoverrides.build_arg_string_from_node."""

    @patch("ht.pyfilter.operations.ipoverrides.IpOverrides.build_arg_string")
    def test(self, mock_build):
        mock_node = MagicMock()
        mock_node.evalParm.return_value = 0

        result = ipoverrides.build_arg_string_from_node(mock_node)
        assert result == ""

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

        result = ipoverrides.build_arg_string_from_node(mock_node)

        assert result ==  mock_build.return_value

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

    @patch("ht.pyfilter.operations.ipoverrides.IpOverrides.build_arg_string")
    def test_no_scales(self, mock_build):
        mock_node = MagicMock()
        mock_node.evalParm.return_value = 0

        result = ipoverrides.build_arg_string_from_node(mock_node)
        assert result == ""

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

        result = ipoverrides.build_arg_string_from_node(mock_node)

        assert result == mock_build.return_value

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
            disable_matte=parm_data["ip_disable_matte"]
        )


@patch("ht.pyfilter.operations.ipoverrides._scale_samples")
def test_build_pixel_sample_scale_display(mock_scale):
    """Test the ht.pyfilter.operations.ipoverrides.build_pixel_sample_scale_display."""
    source_samples = (6, 6)
    target_samples = (3, 3)
    scale = 0.5

    mock_node = MagicMock()
    mock_node.evalParmTuple.return_value = source_samples
    mock_node.evalParm.return_value = scale

    mock_scale.return_value = target_samples

    result = ipoverrides.build_pixel_sample_scale_display(mock_node)

    mock_node.evalParmTuple.assert_called_with("vm_samples")
    mock_node.evalParm.assert_called_with("ip_sample_scale")
    mock_scale.assert_called_with(source_samples, scale)
    assert result == "{}x{}".format(target_samples[0], target_samples[1])


class Test_build_resolution_scale_display(object):
    """Test the ht.pyfilter.operations.ipoverrides.build_resolution_scale_display."""

    def test_no_camera(self):
        mock_node = MagicMock(spec=hou.RopNode)
        mock_node.parm.return_value.evalAsNode.return_value = None

        result = ipoverrides.build_resolution_scale_display(mock_node)

        assert result == ""

        mock_node.parm.assert_called_with("camera")

    @patch("ht.pyfilter.operations.ipoverrides._scale_resolution")
    def test_no_override(self, mock_scale):
        mock_scale.return_value = (960, 540)

        mock_camera = MagicMock(spec=hou.ObjNode)
        mock_camera.evalParmTuple.return_value = (1920, 1080)

        parm_values = {
            "override_camerares": False,
            "ip_res_fraction": "0.5",
        }

        mock_node = MagicMock(spec=hou.RopNode)
        mock_node.parm.return_value.evalAsNode.return_value = mock_camera

        mock_node.evalParm.side_effect = lambda name: parm_values[name]

        result = ipoverrides.build_resolution_scale_display(mock_node)

        assert result == "960x540"

        mock_node.parm.assert_called_with("camera")

        mock_scale.assert_called_with((1920, 1080), 0.5)

    @patch("ht.pyfilter.operations.ipoverrides._scale_resolution")
    def test_override_specific(self, mock_scale):
        mock_scale.return_value = (250, 250)

        mock_camera = MagicMock(spec=hou.ObjNode)
        mock_camera.evalParmTuple.return_value = (1920, 1080)

        parm_values = {
            "override_camerares": 1,
            "ip_res_fraction": "0.25",
            "res_fraction": "specific",
        }

        mock_node = MagicMock(spec=hou.RopNode)
        mock_node.parm.return_value.evalAsNode.return_value = mock_camera
        mock_node.evalParmTuple.return_value = (1000, 1000)
        mock_node.evalParm.side_effect = lambda name: parm_values[name]

        result = ipoverrides.build_resolution_scale_display(mock_node)

        assert result == "250x250"

        mock_node.parm.assert_called_with("camera")

        mock_scale.assert_called_with((1000, 1000), 0.25)

    @patch("ht.pyfilter.operations.ipoverrides._scale_resolution")
    def test_override_scaled(self, mock_scale):
        mock_scale.side_effect = ((960, 540), (480, 270))

        mock_camera = MagicMock(spec=hou.ObjNode)
        mock_camera.evalParmTuple.return_value = (1920, 1080)

        parm_values = {
            "override_camerares": 1,
            "ip_res_fraction": "0.5",
            "res_fraction": "0.5",
        }

        mock_node = MagicMock(spec=hou.RopNode)
        mock_node.parm.return_value.evalAsNode.return_value = mock_camera
        mock_node.evalParmTuple.return_value = (1000, 1000)
        mock_node.evalParm.side_effect = lambda name: parm_values[name]

        result = ipoverrides.build_resolution_scale_display(mock_node)

        assert result == "480x270"

        mock_node.parm.assert_called_with("camera")

        calls = [
            call((1920, 1080), 0.5),
            call((960, 540), 0.5)

        ]
        mock_scale.assert_has_calls(calls)


@patch("ht.pyfilter.operations.ipoverrides.build_pyfilter_command")
@patch("ht.pyfilter.operations.ipoverrides.build_arg_string_from_node")
def test_build_pyfilter_command_from_node(mock_build_arg, mock_build_command):
    """Test the ht.pyfilter.operations.ipoverrides.build_pyfilter_command_from_node."""
    mock_node = MagicMock(spec=hou.RopNode)

    result = ipoverrides.build_pyfilter_command_from_node(mock_node)

    assert result == mock_build_command.return_value

    mock_build_arg.assert_called_with(mock_node)
    mock_build_command.assert_called_with(mock_build_arg.return_value.split.return_value)


def test_set_mantra_command():
    """Test the ht.pyfilter.operations.ipoverrides.set_mantra_command."""

    mock_node = MagicMock(spec=hou.RopNode)

    ipoverrides.set_mantra_command(mock_node)

    mock_node.parm.return_value.set.assert_called_with(
        "mantra `pythonexprs(\"__import__('ht.pyfilter.operations', globals(), locals(), ['ipoverrides']).ipoverrides.build_pyfilter_command_from_node(hou.pwd())\")`"
    )

    mock_node.parm.assert_called_with("soho_pipecmd")
