"""Test the ht.pyfilter.operations.zdepth module."""

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
from ht.pyfilter.operations import zdepth


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def patch_logger():
    """Mock the log_filter_call logger and mantra import."""
    mock_mantra = MagicMock()

    modules = {
        "mantra": mock_mantra,
    }

    module_patcher = patch.dict("sys.modules", modules)
    module_patcher.start()

    patcher = patch("ht.pyfilter.operations.operation._logger", autospec=True)

    yield

    module_patcher.stop()
    patcher.stop()


# =============================================================================
# CLASSES
# =============================================================================

class Test_ZDepthPass(object):
    """Test the ht.pyfilter.operations.zdepth.ZDepthPass class.

    """

    def test___init__(self):
        mock_manager = MagicMock(spec=PyFilterManager)
        op = zdepth.ZDepthPass(mock_manager)

        assert op._data == {"set_pz": False}
        assert not op._active

    # Properties

    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_all_passes(self):
        op = zdepth.ZDepthPass(None)
        op._active = True
        assert op.active

        op = zdepth.ZDepthPass(None)
        op._active = False
        op.active = True
        assert op._active

    # Static Methods

    def test_build_arg_string(self):
        result = zdepth.ZDepthPass.build_arg_string()

        assert result == ""

        # Disable deep image path
        result = zdepth.ZDepthPass.build_arg_string(active=True)

        assert result == "--zdepth"

    def test_register_parser_args(self):
        mock_parser = MagicMock(spec=argparse.ArgumentParser)

        zdepth.ZDepthPass.register_parser_args(mock_parser)

        calls = [
            call("--zdepth", action="store_true")
        ]
        mock_parser.add_argument.assert_has_calls(calls)

    # Methods

    # filter_instance

    @patch("ht.pyfilter.operations.zdepth.set_property")
    @patch("ht.pyfilter.operations.zdepth.get_property")
    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_filter_instance__obj_matte(self, mock_get, mock_set, patch_logger):
        mock_get.side_effect = (True, False, "")

        op = zdepth.ZDepthPass(None)

        op.filter_instance()

        calls = [
            call("object:overridedetail", True),
            call("object:phantom", 1)
        ]

        mock_set.asset_has_calls(calls)

    @patch("ht.pyfilter.operations.zdepth.set_property")
    @patch("ht.pyfilter.operations.zdepth.get_property")
    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_filter_instance__obj_phantom(self, mock_get, mock_set, patch_logger):
        mock_get.side_effect = (False, True, "")

        op = zdepth.ZDepthPass(None)

        op.filter_instance()

        calls = [
            call("object:overridedetail", True),
            call("object:phantom", 1)
        ]

        mock_set.asset_has_calls(calls)

    @patch("ht.pyfilter.operations.zdepth.set_property")
    @patch("ht.pyfilter.operations.zdepth.get_property")
    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_filter_instance__surface_matte(self, mock_get, mock_set, patch_logger):
        mock_get.side_effect = (False, False, "matte")

        op = zdepth.ZDepthPass(None)

        op.filter_instance()

        calls = [
            call("object:overridedetail", True),
            call("object:phantom", 1)
        ]

        mock_set.asset_has_calls(calls)

    @patch("ht.pyfilter.operations.zdepth.set_property")
    @patch("ht.pyfilter.operations.zdepth.get_property")
    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_filter_instance__set_shader(self, mock_get, mock_set, patch_logger):
        mock_get.side_effect = (False, False, "")

        op = zdepth.ZDepthPass(None)

        op.filter_instance()

        calls = [
            call("object:overridedetail", True),
            call("object:surface", op.CONST_SHADER.split()),
            call("object:displace", None)
        ]

        mock_set.asset_has_calls(calls)

    # filter_plane

    @patch("ht.pyfilter.operations.zdepth.set_property")
    @patch("ht.pyfilter.operations.zdepth.get_property")
    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_filter_plane_Pz(self, mock_get, mock_set, patch_logger):
        mock_get.return_value = "Pz"

        op = zdepth.ZDepthPass(None)
        op._data = {"set_pz": False}

        op.filter_plane()

        assert op.data["set_pz"]

        mock_set.assert_not_called()

    @patch("ht.pyfilter.operations.zdepth.set_property")
    @patch("ht.pyfilter.operations.zdepth.get_property")
    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_filter_plane_Pz_already_set(self, mock_get, mock_set, patch_logger):
        mock_get.return_value = "Pz"

        op = zdepth.ZDepthPass(None)
        op._data = {"set_pz": True}

        op.filter_plane()

        mock_set.assert_called_with("plane:disable", True)

    @patch("ht.pyfilter.operations.zdepth.set_property")
    @patch("ht.pyfilter.operations.zdepth.get_property")
    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_filter_plane_no_pz_C(self, mock_get, mock_set, patch_logger):
        mock_get.return_value = "C"

        op = zdepth.ZDepthPass(None)
        op._data = {"set_pz": False}

        op.filter_plane()

        assert not op.data["set_pz"]

        mock_set.assert_not_called()

    @patch("ht.pyfilter.operations.zdepth.set_property")
    @patch("ht.pyfilter.operations.zdepth.get_property")
    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_filter_plane_no_pz_Of(self, mock_get, mock_set, patch_logger):
        mock_get.return_value = "Of"

        op = zdepth.ZDepthPass(None)
        op._data = {"set_pz": False}

        op.filter_plane()

        assert not op.data["set_pz"]

        mock_set.assert_called_with("plane:disable", True)

    @patch("ht.pyfilter.operations.zdepth.set_property")
    @patch("ht.pyfilter.operations.zdepth.get_property")
    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_filter_plane_not_set_misc_channel(self, mock_get, mock_set, patch_logger):
        mock_get.return_value = "channel1"

        op = zdepth.ZDepthPass(None)
        op._data = {"set_pz": False}

        op.filter_plane()

        assert op.data["set_pz"]

        calls = [
            call("plane:variable", "Pz"),
            call("plane:vextype", "float"),
            call("plane:channel", "Pz"),
            call("plane:pfilter", "minmax min"),
            call("plane:quantize", None),
        ]

        mock_set.assert_has_calls(calls)

    @patch("ht.pyfilter.operations.zdepth.set_property")
    @patch("ht.pyfilter.operations.zdepth.get_property")
    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_filter_plane_set_pz_misc(self, mock_get, mock_set, patch_logger):
        mock_get.return_value = "channel1"

        op = zdepth.ZDepthPass(None)
        op._data = {"set_pz": True}

        op.filter_plane()

        mock_set.assert_called_with("plane:disable", True)

    # process_parsed_args

    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_process_parsed_args(self):
        namespace = argparse.Namespace()
        namespace.zdepth = True

        op = zdepth.ZDepthPass(None)

        op._active = False

        op.process_parsed_args(namespace)

        assert op.active

    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_process_parsed_args__none(self):
        namespace = argparse.Namespace()
        namespace.zdepth = None

        op = zdepth.ZDepthPass(None)

        op._active = False

        op.process_parsed_args(namespace)

        assert not op.active

    # should_run

    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_should_run(self):
        op = zdepth.ZDepthPass(None)

        op._active = False
        assert not op.should_run()

        op._active = True
        assert op.should_run()
