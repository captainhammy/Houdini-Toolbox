"""Test the houdini_toolbox.pyfilter.operations.zdepth module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import argparse

# Third Party
import pytest

# Houdini Toolbox
from houdini_toolbox.pyfilter.manager import PyFilterManager
from houdini_toolbox.pyfilter.operations import zdepth

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def init_operation(mocker):
    """Fixture to initialize an operation."""
    mocker.patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)

    def _create():
        return zdepth.ZDepthPass(None)

    return _create


@pytest.fixture
def properties(mocker):
    """Fixture to handle mocking (get|set)_property calls."""

    _mock_get = mocker.patch("houdini_toolbox.pyfilter.operations.zdepth.get_property")
    _mock_set = mocker.patch("houdini_toolbox.pyfilter.operations.zdepth.set_property")

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


class Test_ZDepthPass:
    """Test the houdini_toolbox.pyfilter.operations.zdepth.ZDepthPass class."""

    def test___init__(self, mocker):
        """Test object initialization."""
        mock_manager = mocker.MagicMock(spec=PyFilterManager)

        op = zdepth.ZDepthPass(mock_manager)

        assert op._data == {"set_pz": False}
        assert not op._active

    # Properties

    def test_all_passes(self, init_operation, mocker):
        """Test the 'all_passes' property."""
        mock_value = mocker.MagicMock(spec=bool)

        op = init_operation()
        op._active = mock_value

        assert op.active == mock_value

    # Static Methods

    def test_build_arg_string(self):
        """Test arg string construction."""
        result = zdepth.ZDepthPass.build_arg_string()

        assert result == ""

        # Disable deep image path
        result = zdepth.ZDepthPass.build_arg_string(active=True)

        assert result == "--zdepth"

    def test_register_parser_args(self, mocker):
        """Test registering all the argument parser args."""
        mock_parser = mocker.MagicMock(spec=argparse.ArgumentParser)

        zdepth.ZDepthPass.register_parser_args(mock_parser)

        calls = [mocker.call("--zdepth", action="store_true")]
        mock_parser.add_argument.assert_has_calls(calls)

    # Methods

    # filter_instance

    def test_filter_instance__obj_matte(
        self, init_operation, properties, mocker, patch_soho
    ):
        """Test filtering when the object:matte property is set."""
        properties.mock_get.side_effect = (True, False, "")

        op = init_operation()

        op.filter_instance()

        calls = [
            mocker.call("object:overridedetail", True),
            mocker.call("object:phantom", 1),
        ]

        properties.mock_set.asset_has_calls(calls)

    def test_filter_instance__obj_phantom(
        self, init_operation, properties, mocker, patch_soho
    ):
        """Test filtering when the object:phantom property is set."""
        properties.mock_get.side_effect = (False, True, "")

        op = init_operation()

        op.filter_instance()

        calls = [
            mocker.call("object:overridedetail", True),
            mocker.call("object:phantom", 1),
        ]

        properties.mock_set.asset_has_calls(calls)

    def test_filter_instance__surface_matte(
        self, init_operation, properties, mocker, patch_soho
    ):
        """Test filtering when the object:surface points to a matte shader."""
        properties.mock_get.side_effect = (False, False, "matte")

        op = init_operation()

        op.filter_instance()

        calls = [
            mocker.call("object:overridedetail", True),
            mocker.call("object:phantom", 1),
        ]

        properties.mock_set.asset_has_calls(calls)

    def test_filter_instance__set_shader(
        self, init_operation, properties, mocker, patch_soho
    ):
        """Test setting the surface and displacement shaders to be constant."""
        properties.mock_get.side_effect = (False, False, "")

        op = init_operation()

        op.filter_instance()

        calls = [
            mocker.call("object:overridedetail", True),
            mocker.call("object:surface", op.CONST_SHADER.split()),
            mocker.call("object:displace", None),
        ]

        properties.mock_set.asset_has_calls(calls)

    # filter_plane

    def test_filter_plane__pz(self, init_operation, properties, patch_soho):
        """Test filtering the actual Pz plane."""
        properties.mock_get.return_value = "Pz"

        op = init_operation()
        op._data = {"set_pz": False}

        op.filter_plane()

        assert op.data["set_pz"]

        properties.mock_set.assert_not_called()

    def test_filter_plane__pz_already_set(self, init_operation, properties, patch_soho):
        """Test filtering Pz when Pz has already been manually set."""
        properties.mock_get.return_value = "Pz"

        op = init_operation()
        op._data = {"set_pz": True}

        op.filter_plane()

        properties.mock_set.assert_called_with("plane:disable", True)

    def test_filter_plane__no_pz_c(self, init_operation, properties, patch_soho):
        """Test filtering C when Pz has not already been set."""
        properties.mock_get.return_value = "C"

        op = init_operation()
        op._data = {"set_pz": False}

        op.filter_plane()

        assert not op.data["set_pz"]

        properties.mock_set.assert_not_called()

    def test_filter_plane__no_pz_of(self, init_operation, properties, patch_soho):
        """Test filtering Of when Pz has not already been set."""
        properties.mock_get.return_value = "Of"

        op = init_operation()
        op._data = {"set_pz": False}

        op.filter_plane()

        assert not op.data["set_pz"]

        properties.mock_set.assert_called_with("plane:disable", True)

    def test_filter_plane__not_set_misc_channel(
        self, init_operation, properties, mocker, patch_soho
    ):
        """Test filtering a non-special plane when Pz has not already been set."""
        properties.mock_get.return_value = "channel1"

        op = init_operation()
        op._data = {"set_pz": False}

        op.filter_plane()

        assert op.data["set_pz"]

        calls = [
            mocker.call("plane:variable", "Pz"),
            mocker.call("plane:vextype", "float"),
            mocker.call("plane:channel", "Pz"),
            mocker.call("plane:pfilter", "minmax min"),
            mocker.call("plane:quantize", None),
        ]

        properties.mock_set.assert_has_calls(calls)

    def test_filter_plane__set_pz_misc(self, init_operation, properties, patch_soho):
        """Test filtering a non-special plane when Pz has already been set."""
        properties.mock_get.return_value = "channel1"

        op = init_operation()
        op._data = {"set_pz": True}

        op.filter_plane()

        properties.mock_set.assert_called_with("plane:disable", True)

    # process_parsed_args

    def test_process_parsed_args(self, init_operation):
        """Test "process_parsed_args" when the args have been set."""
        namespace = argparse.Namespace()
        namespace.zdepth = True

        op = init_operation()

        op._active = False

        op.process_parsed_args(namespace)

        assert op.active

    def test_process_parsed_args__none(self, init_operation):
        """Test "process_parsed_args" when the args have not been set."""
        namespace = argparse.Namespace()
        namespace.zdepth = None

        op = init_operation()

        op._active = False

        op.process_parsed_args(namespace)

        assert not op.active

    # should_run

    def test_should_run(self, init_operation):
        """Test "should_run"."""
        op = init_operation()

        op._active = False
        assert not op.should_run()

        op._active = True
        assert op.should_run()
