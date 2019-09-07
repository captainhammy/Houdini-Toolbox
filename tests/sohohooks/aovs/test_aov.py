"""Test the ht.sohohooks.aovs.aov module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import imp

# Third Party Imports
from mock import MagicMock, PropertyMock, call, patch
import pytest

# Houdini Toolbox Imports
from ht.sohohooks.aovs import aov

# Houdini Toolbox Imports
from ht.sohohooks.aovs import constants as consts

# Reload the module to test to capture load evaluation since it has already
# been loaded.
imp.reload(aov)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def patch_soho():
    """Mock importing of soho modules."""
    mock_IFDhooks = MagicMock()
    mock_api = MagicMock()
    mock_soho = MagicMock()

    modules = {
        "IFDapi": mock_api,
        "IFDhooks": mock_IFDhooks,
        "soho": mock_soho,
    }

    patcher = patch.dict("sys.modules", modules)
    patcher.start()

    yield mock_soho, mock_api, mock_IFDhooks

    patcher.stop()


# =============================================================================
# CLASSES
# =============================================================================

class Test_AOV(object):
    """Test ht.sohohooks.aovs.AOV object."""

    # __init__

    @patch.object(aov.AOV, "_update_data")
    @patch("ht.sohohooks.aovs.aov.copy.copy")
    def test___init__(self, mock_copy, mock_update):
        data = MagicMock(spec=dict)

        aov.AOV(data)

        mock_copy.assert_called_with(aov._DEFAULT_AOV_DATA)
        mock_update.assert_called_with(data)

    # __eq__

    @patch("ht.sohohooks.aovs.aov.AOV.variable", new_callable=PropertyMock(return_value="P"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___eq___equal(self, mock_variable):
        inst1 = aov.AOV(None)

        inst2 = MagicMock(spec=aov.AOV)
        type(inst2).variable = PropertyMock(return_value="P")

        result = inst1.__eq__(inst2)

        assert result

    @patch("ht.sohohooks.aovs.aov.AOV.variable", new_callable=PropertyMock(return_value="N"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___eq___not_equal(self, mock_variable):
        inst1 = aov.AOV(None)

        inst2 = MagicMock(spec=aov.AOV)
        type(inst2).variable = PropertyMock(return_value="P")

        result = inst1.__eq__(inst2)

        assert not result

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___eq___non_aov(self):
        inst1 = aov.AOV(None)
        inst2 = MagicMock()

        result = inst1.__eq__(inst2)

        assert result == NotImplemented

    # __ge__

    @patch("ht.sohohooks.aovs.aov.AOV.variable", new_callable=PropertyMock(return_value="O"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___ge___less_than(self, mock_variable):
        inst1 = aov.AOV(None)

        inst2 = MagicMock(spec=aov.AOV)
        type(inst2).variable = PropertyMock(return_value="P")

        result = inst1.__ge__(inst2)

        assert not result

    @patch("ht.sohohooks.aovs.aov.AOV.variable", new_callable=PropertyMock(return_value="P"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___ge___equal(self, mock_variable):
        inst1 = aov.AOV(None)

        inst2 = MagicMock(spec=aov.AOV)
        type(inst2).variable = PropertyMock(return_value="P")

        result = inst1.__ge__(inst2)

        assert result

    @patch("ht.sohohooks.aovs.aov.AOV.variable", new_callable=PropertyMock(return_value="Q"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___ge___greater_than(self, mock_variable):
        inst1 = aov.AOV(None)

        inst2 = MagicMock(spec=aov.AOV)
        type(inst2).variable = PropertyMock(return_value="P")

        result = inst1.__ge__(inst2)

        assert result

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___ge___non_aov(self):
        inst1 = aov.AOV(None)
        inst2 = MagicMock()

        result = inst1.__ge__(inst2)

        assert result == NotImplemented

    # __gt__

    @patch("ht.sohohooks.aovs.aov.AOV.variable", new_callable=PropertyMock(return_value="O"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___gt___less_than(self, mock_variable):
        inst1 = aov.AOV(None)

        inst2 = MagicMock(spec=aov.AOV)
        type(inst2).variable = PropertyMock(return_value="P")

        result = inst1.__gt__(inst2)

        assert not result

    @patch("ht.sohohooks.aovs.aov.AOV.variable", new_callable=PropertyMock(return_value="P"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___gt___equal(self, mock_variable):
        inst1 = aov.AOV(None)

        inst2 = MagicMock(spec=aov.AOV)
        type(inst2).variable = PropertyMock(return_value="P")

        result = inst1.__gt__(inst2)

        assert not result

    @patch("ht.sohohooks.aovs.aov.AOV.variable", new_callable=PropertyMock(return_value="Q"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___gt___greater_than(self, mock_variable):
        inst1 = aov.AOV(None)

        inst2 = MagicMock(spec=aov.AOV)
        type(inst2).variable = PropertyMock(return_value="P")

        result = inst1.__gt__(inst2)

        assert result

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___gt___non_aov(self):
        inst1 = aov.AOV(None)
        inst2 = MagicMock()

        result = inst1.__gt__(inst2)

        assert result == NotImplemented

    # __le__

    @patch("ht.sohohooks.aovs.aov.AOV.variable", new_callable=PropertyMock(return_value="O"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___le___less_than(self, mock_variable):
        inst1 = aov.AOV(None)

        inst2 = MagicMock(spec=aov.AOV)
        type(inst2).variable = PropertyMock(return_value="P")

        result = inst1.__le__(inst2)

        assert result

    @patch("ht.sohohooks.aovs.aov.AOV.variable", new_callable=PropertyMock(return_value="P"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___le___equal(self, mock_variable):
        inst1 = aov.AOV(None)

        inst2 = MagicMock(spec=aov.AOV)
        type(inst2).variable = PropertyMock(return_value="P")

        result = inst1.__le__(inst2)

        assert result

    @patch("ht.sohohooks.aovs.aov.AOV.variable", new_callable=PropertyMock(return_value="Q"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___le___greater_than(self, mock_variable):
        inst1 = aov.AOV(None)

        inst2 = MagicMock(spec=aov.AOV)
        type(inst2).variable = PropertyMock(return_value="P")

        result = inst1.__le__(inst2)

        assert not result

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___le___non_aov(self):
        inst1 = aov.AOV(None)
        inst2 = MagicMock()

        result = inst1.__le__(inst2)

        assert result == NotImplemented

    # __lt__

    @patch("ht.sohohooks.aovs.aov.AOV.variable", new_callable=PropertyMock(return_value="O"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___lt___less_than(self, mock_variable):
        inst1 = aov.AOV(None)

        inst2 = MagicMock(spec=aov.AOV)
        type(inst2).variable = PropertyMock(return_value="P")

        result = inst1.__lt__(inst2)

        assert result

    @patch("ht.sohohooks.aovs.aov.AOV.variable", new_callable=PropertyMock(return_value="P"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___lt___equal(self, mock_variable):
        inst1 = aov.AOV(None)

        inst2 = MagicMock(spec=aov.AOV)
        type(inst2).variable = PropertyMock(return_value="P")

        result = inst1.__lt__(inst2)

        assert not result

    @patch("ht.sohohooks.aovs.aov.AOV.variable", new_callable=PropertyMock(return_value="Q"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___lt___greater_than(self, mock_variable):
        inst1 = aov.AOV(None)

        inst2 = MagicMock(spec=aov.AOV)
        type(inst2).variable = PropertyMock(return_value="P")

        result = inst1.__lt__(inst2)

        assert not result

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___lt___non_aov(self):
        inst1 = aov.AOV(None)
        inst2 = MagicMock()

        result = inst1.__lt__(inst2)

        assert result == NotImplemented

    # __hash__

    @patch("ht.sohohooks.aovs.aov.AOV.variable", new_callable=PropertyMock(return_value="N"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___hash__(self, mock_variable):
        inst1 = aov.AOV(None)

        result = inst1.__hash__()

        assert result == hash("N")

        assert hash(inst1) == hash("N")

    # __ne__

    @patch.object(aov.AOV, "__eq__")
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___ne___(self, mock_eq):
        inst1 = aov.AOV(None)

        inst2 = MagicMock(spec=aov.AOV)

        result = inst1.__ne__(inst2)

        assert result != mock_eq.return_value
        mock_eq.assert_called_with(inst2)

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___ne___non_aov(self):
        inst1 = aov.AOV(None)
        inst2 = MagicMock()

        result = inst1.__ne__(inst2)

        assert result == NotImplemented

    # __str__

    @patch("ht.sohohooks.aovs.aov.AOV.variable", new_callable=PropertyMock(return_value="N"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___str__(self, mock_variable):
        inst1 = aov.AOV(None)

        result = inst1.__str__()

        assert str(inst1) == "N"

        assert result == "N"

    # _light_export_planes

    @patch("ht.sohohooks.aovs.aov._write_data_to_ifd")
    @patch("ht.sohohooks.aovs.aov.AOV.lightexport", new_callable=PropertyMock(return_value=None))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__light_export_planes__no_lightexport(self, mock_lightexport, mock_write):
        inst = aov.AOV(None)

        data = MagicMock(spec=dict)
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        mock_now = MagicMock(spec=float)

        inst._light_export_planes(data, mock_wrangler, mock_cam, mock_now)

        mock_write.assert_called_with(data, mock_wrangler, mock_cam, mock_now)

    @patch("ht.sohohooks.aovs.aov._write_light")
    @patch("ht.sohohooks.aovs.aov.AOV.lightexport_select", new_callable=PropertyMock)
    @patch("ht.sohohooks.aovs.aov.AOV.lightexport_scope", new_callable=PropertyMock)
    @patch("ht.sohohooks.aovs.aov.AOV.lightexport", new_callable=PropertyMock(return_value=consts.LIGHTEXPORT_PER_LIGHT_KEY))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__light_export_planes__per_light(self, mock_lightexport, mock_scope, mock_select, mock_write):
        inst = aov.AOV(None)

        mock_light1 = MagicMock()
        mock_light2 = MagicMock()

        lights = [mock_light1, mock_light2]

        mock_channel = MagicMock(spec=str)
        data = {consts.CHANNEL_KEY: mock_channel}
        mock_wrangler = MagicMock()

        mock_cam = MagicMock()
        mock_cam.objectList.return_value = lights
        mock_now = MagicMock(spec=float)

        inst._light_export_planes(data, mock_wrangler, mock_cam, mock_now)

        mock_cam.objectList.assert_called_with("objlist:light", mock_now, mock_scope.return_value, mock_select.return_value)

        calls = [
            call(mock_light1, mock_channel, data, mock_wrangler, mock_cam, mock_now),
            call(mock_light2, mock_channel, data, mock_wrangler, mock_cam, mock_now)
        ]

        mock_write.assert_has_calls(calls)

    @patch("ht.sohohooks.aovs.aov._write_single_channel")
    @patch("ht.sohohooks.aovs.aov.AOV.lightexport_select", new_callable=PropertyMock)
    @patch("ht.sohohooks.aovs.aov.AOV.lightexport_scope", new_callable=PropertyMock)
    @patch("ht.sohohooks.aovs.aov.AOV.lightexport", new_callable=PropertyMock(return_value=consts.LIGHTEXPORT_SINGLE_KEY))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__light_export_planes__single(self, mock_lightexport, mock_scope, mock_select, mock_write):
        inst = aov.AOV(None)

        mock_light1 = MagicMock()
        mock_light2 = MagicMock()

        lights = [mock_light1, mock_light2]

        mock_channel = MagicMock(spec="str")
        data = {consts.CHANNEL_KEY: mock_channel}
        mock_wrangler = MagicMock()

        mock_cam = MagicMock()
        mock_cam.objectList.return_value = lights
        mock_now = MagicMock(spec=float)

        inst._light_export_planes(data, mock_wrangler, mock_cam, mock_now)

        mock_cam.objectList.assert_called_with("objlist:light", mock_now, mock_scope.return_value, mock_select.return_value)

        mock_write.assert_called_with(lights, data, mock_wrangler, mock_cam, mock_now)

    @patch("ht.sohohooks.aovs.aov._write_per_category")
    @patch("ht.sohohooks.aovs.aov.AOV.lightexport_select", new_callable=PropertyMock)
    @patch("ht.sohohooks.aovs.aov.AOV.lightexport_scope", new_callable=PropertyMock)
    @patch("ht.sohohooks.aovs.aov.AOV.lightexport", new_callable=PropertyMock(return_value=consts.LIGHTEXPORT_PER_CATEGORY_KEY))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__light_export_planes__per_category(self, mock_lightexport, mock_scope, mock_select, mock_write):
        inst = aov.AOV(None)

        mock_light1 = MagicMock()
        mock_light2 = MagicMock()

        lights = [mock_light1, mock_light2]

        mock_channel = MagicMock(spec="str")
        data = {consts.CHANNEL_KEY: mock_channel}
        mock_wrangler = MagicMock()

        mock_cam = MagicMock()
        mock_cam.objectList.return_value = lights
        mock_now = MagicMock(spec=float)

        inst._light_export_planes(data, mock_wrangler, mock_cam, mock_now)

        mock_cam.objectList.assert_called_with("objlist:light", mock_now, mock_scope.return_value, mock_select.return_value)

        mock_write.assert_called_with(lights, mock_channel, data, mock_wrangler, mock_cam, mock_now)

    @patch("ht.sohohooks.aovs.aov.AOV.lightexport_select", new_callable=PropertyMock)
    @patch("ht.sohohooks.aovs.aov.AOV.lightexport_scope", new_callable=PropertyMock)
    @patch("ht.sohohooks.aovs.aov.AOV.lightexport", new_callable=PropertyMock(return_value="bad_value"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__light_export_planes__bad_value(self, mock_lightexport, mock_scope, mock_select):
        inst = aov.AOV(None)

        mock_light1 = MagicMock()
        mock_light2 = MagicMock()

        lights = [mock_light1, mock_light2]

        mock_channel = MagicMock(spec="str")
        data = {consts.CHANNEL_KEY: mock_channel}
        mock_wrangler = MagicMock()

        mock_cam = MagicMock()
        mock_cam.objectList.return_value = lights
        mock_now = MagicMock(spec=float)

        with pytest.raises(aov.InvalidAOVValueError):
            inst._light_export_planes(data, mock_wrangler, mock_cam, mock_now)

        mock_cam.objectList.assert_called_with("objlist:light", mock_now, mock_scope.return_value, mock_select.return_value)

    # _update_data

    @patch("ht.sohohooks.aovs.aov.AOV._verify_internal_data")
    @patch("ht.sohohooks.aovs.aov.ALLOWABLE_VALUES", return_value={})
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__update_data__unknown(self, mock_allowable, mock_verify):
        inst = aov.AOV(None)
        inst._data = {}

        data = {"key": None}

        inst._update_data(data)

        assert inst._data == {}

        mock_verify.assert_called()

    @patch("ht.sohohooks.aovs.aov.AOV._verify_internal_data")
    @patch("ht.sohohooks.aovs.aov.ALLOWABLE_VALUES", return_value={})
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__update_data__settable(self, mock_allowable, mock_verify):
        inst = aov.AOV(None)
        inst._data = {"key": None}

        data = {"key": "value"}

        inst._update_data(data)

        assert inst._data == {"key": "value"}

        mock_verify.assert_called()

    @patch("ht.sohohooks.aovs.aov.AOV._verify_internal_data")
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__update_data__allowable_valid(self, mock_verify):
        inst = aov.AOV(None)
        inst._data = {"key": None}

        data = {"key": "value1"}

        allowable = {
            "key": ("value1", "value2")
        }

        with patch.dict(aov.ALLOWABLE_VALUES, allowable, clear=True):
            inst._update_data(data)

        assert inst._data == {"key": "value1"}

        mock_verify.assert_called()

    @patch("ht.sohohooks.aovs.aov.AOV._verify_internal_data")
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__update_data__allowable_invalid(self, mock_verify):
        inst = aov.AOV(None)
        inst._data = {"key": None}

        data = {"key": "value3"}

        allowable = {
            "key": ("value1", "value2")
        }

        with patch.dict(aov.ALLOWABLE_VALUES, allowable, clear=True):
            with pytest.raises(aov.InvalidAOVValueError):
                inst._update_data(data)

    # _verify_internal_data

    @patch("ht.sohohooks.aovs.aov.AOV.variable", new_callable=PropertyMock)
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__verify_internal_data__no_variable(self, mock_variable):
        mock_variable.return_value = None

        inst = aov.AOV(None)

        with pytest.raises(aov.MissingVariableError):
            inst._verify_internal_data()

    @patch("ht.sohohooks.aovs.aov.AOV.vextype", new_callable=PropertyMock)
    @patch("ht.sohohooks.aovs.aov.AOV.variable", new_callable=PropertyMock)
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__verify_internal_data__no_vextype(self, mock_variable, mock_vextype):
        mock_variable.return_value = MagicMock(spec=str)
        mock_vextype.return_value = None

        inst = aov.AOV(None)

        with pytest.raises(aov.MissingVexTypeError):
            inst._verify_internal_data()

    @patch("ht.sohohooks.aovs.aov.AOV.vextype", new_callable=PropertyMock)
    @patch("ht.sohohooks.aovs.aov.AOV.variable", new_callable=PropertyMock)
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__verify_internal_data__valid(self, mock_variable, mock_vextype):
        mock_variable.return_value = MagicMock(spec=str)
        mock_vextype.return_value = MagicMock(spec=str)

        inst = aov.AOV(None)

        inst._verify_internal_data()

    # properties

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_channel(self):
        mock_value = MagicMock(spec=str)

        inst = aov.AOV(None)
        inst._data = {consts.CHANNEL_KEY: mock_value}

        assert inst.channel == mock_value

        inst.channel = None

        assert inst._data[consts.CHANNEL_KEY] is None

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_comment(self):
        mock_value = MagicMock(spec=str)

        inst = aov.AOV(None)
        inst._data = {consts.COMMENT_KEY: mock_value}

        assert inst.comment == mock_value

        inst.comment = None

        assert inst._data[consts.COMMENT_KEY] is None

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_componentexport(self):
        mock_value1 = MagicMock(spec=bool)

        inst = aov.AOV(None)
        inst._data = {consts.COMPONENTEXPORT_KEY: mock_value1}

        assert inst.componentexport == mock_value1

        mock_value2 = MagicMock(spec=bool)
        inst.componentexport = mock_value2

        assert inst._data[consts.COMPONENTEXPORT_KEY] == mock_value2

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_components(self):
        mock_value1 = MagicMock(spec=list)

        inst = aov.AOV(None)
        inst._data = {consts.COMPONENTS_KEY: mock_value1}

        assert inst.components == mock_value1

        mock_value2 = MagicMock(spec=list)
        inst.components = mock_value2

        assert inst._data[consts.COMPONENTS_KEY] == mock_value2

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_exclude_from_dcm(self):
        mock_value1 = MagicMock(spec=bool)

        inst = aov.AOV(None)
        inst._data = {consts.EXCLUDE_DCM_KEY: mock_value1}

        assert inst.exclude_from_dcm == mock_value1

        mock_value2 = MagicMock(spec=bool)
        inst.exclude_from_dcm = mock_value2

        assert inst._data[consts.EXCLUDE_DCM_KEY] == mock_value2

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_intrinsics(self):
        mock_value1 = MagicMock(spec=list)

        inst = aov.AOV(None)
        inst._data = {consts.INTRINSICS_KEY: mock_value1}

        assert inst.intrinsics == mock_value1

        mock_value2 = MagicMock(spec=list)
        inst.intrinsics = mock_value2

        assert inst._data[consts.INTRINSICS_KEY] == mock_value2

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_lightexport(self):
        mock_value1 = MagicMock(spec=str)

        inst = aov.AOV(None)
        inst._data = {consts.LIGHTEXPORT_KEY: mock_value1}

        assert inst.lightexport == mock_value1

        mock_value2 = MagicMock(spec=str)
        inst.lightexport = mock_value2

        assert inst._data[consts.LIGHTEXPORT_KEY] == mock_value2

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_lightexport_select(self):
        mock_value1 = MagicMock(spec=str)

        inst = aov.AOV(None)
        inst._data = {consts.LIGHTEXPORT_SELECT_KEY: mock_value1}

        assert inst.lightexport_select == mock_value1

        mock_value2 = MagicMock(spec=str)
        inst.lightexport_select = mock_value2

        assert inst._data[consts.LIGHTEXPORT_SELECT_KEY] == mock_value2

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_lightexport_scope(self):
        mock_value1 = MagicMock(spec=str)

        inst = aov.AOV(None)
        inst._data = {consts.LIGHTEXPORT_SCOPE_KEY: mock_value1}

        assert inst.lightexport_scope == mock_value1

        mock_value2 = MagicMock(spec=str)
        inst.lightexport_scope = mock_value2

        assert inst._data[consts.LIGHTEXPORT_SCOPE_KEY] == mock_value2

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_path(self):
        mock_value1 = MagicMock(spec=str)

        inst = aov.AOV(None)
        inst._data = {consts.PATH_KEY: mock_value1}

        assert inst.path == mock_value1

        mock_value2 = MagicMock(spec=str)
        inst.path = mock_value2

        assert inst._data[consts.PATH_KEY] == mock_value2

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_pfilter(self):
        mock_value1 = MagicMock(spec=str)

        inst = aov.AOV(None)
        inst._data = {consts.PFILTER_KEY: mock_value1}

        assert inst.pfilter == mock_value1

        mock_value2 = MagicMock(spec=str)
        inst.pfilter = mock_value2

        assert inst._data[consts.PFILTER_KEY] == mock_value2

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_planefile(self):
        mock_value1 = MagicMock(spec=str)

        inst = aov.AOV(None)
        inst._data = {consts.PLANEFILE_KEY: mock_value1}

        assert inst.planefile == mock_value1

        mock_value2 = MagicMock(spec=str)
        inst.planefile = mock_value2

        assert inst._data[consts.PLANEFILE_KEY] == mock_value2

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_priority(self):
        mock_value1 = MagicMock(spec=int)

        inst = aov.AOV(None)
        inst._data = {consts.PRIORITY_KEY: mock_value1}

        assert inst.priority == mock_value1

        mock_value2 = MagicMock(spec=int)
        inst.priority = mock_value2

        assert inst._data[consts.PRIORITY_KEY] == mock_value2

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_quantize(self):
        mock_value1 = MagicMock(spec=str)

        inst = aov.AOV(None)
        inst._data = {consts.QUANTIZE_KEY: mock_value1}

        assert inst.quantize == mock_value1

        mock_value2 = MagicMock(spec=str)
        inst.quantize = mock_value2

        assert inst._data[consts.QUANTIZE_KEY] == mock_value2

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_sfilter(self):
        mock_value1 = MagicMock(spec=str)

        inst = aov.AOV(None)
        inst._data = {consts.SFILTER_KEY: mock_value1}

        assert inst.sfilter == mock_value1

        mock_value2 = MagicMock(spec=str)
        inst.sfilter = mock_value2

        assert inst._data[consts.SFILTER_KEY] == mock_value2

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_variable(self):
        mock_value1 = MagicMock(spec=str)

        inst = aov.AOV(None)
        inst._data = {consts.VARIABLE_KEY: mock_value1}

        assert inst.variable == mock_value1

        mock_value2 = MagicMock(spec=str)
        inst.variable = mock_value2

        assert inst._data[consts.VARIABLE_KEY] == mock_value2

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_vextype(self):
        mock_value1 = MagicMock(spec=str)

        inst = aov.AOV(None)
        inst._data = {consts.VEXTYPE_KEY: mock_value1}

        assert inst.vextype == mock_value1

        mock_value2 = MagicMock(spec=str)
        inst.vextype = mock_value2

        assert inst._data[consts.VEXTYPE_KEY] == mock_value2

    # _as_data

    @patch.object(aov.AOV, "priority", new_callable=PropertyMock(return_value=-1))
    @patch.object(aov.AOV, "comment", new_callable=PropertyMock(return_value=""))
    @patch.object(aov.AOV, "intrinsics", new_callable=PropertyMock(return_value=[]))
    @patch.object(aov.AOV, "lightexport", new_callable=PropertyMock(return_value=None))
    @patch.object(aov.AOV, "componentexport", new_callable=PropertyMock(return_value=None))
    @patch.object(aov.AOV, "exclude_from_dcm", new_callable=PropertyMock(return_value=None))
    @patch.object(aov.AOV, "pfilter", new_callable=PropertyMock(return_value=None))
    @patch.object(aov.AOV, "sfilter", new_callable=PropertyMock(return_value=None))
    @patch.object(aov.AOV, "quantize", new_callable=PropertyMock(return_value=None))
    @patch.object(aov.AOV, "channel", new_callable=PropertyMock(return_value=None))
    @patch.object(aov.AOV, "vextype", new_callable=PropertyMock)
    @patch.object(aov.AOV, "variable", new_callable=PropertyMock)
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_as_data__defaults(self, *args, **kwargs):
        inst = aov.AOV(None)

        result = inst.as_data()

        assert result == {consts.VARIABLE_KEY: inst.variable, consts.VEXTYPE_KEY: inst.vextype}

    @patch.object(aov.AOV, "priority", new_callable=PropertyMock)
    @patch.object(aov.AOV, "comment", new_callable=PropertyMock)
    @patch.object(aov.AOV, "intrinsics", new_callable=PropertyMock)
    @patch.object(aov.AOV, "lightexport", new_callable=PropertyMock(return_value=consts.LIGHTEXPORT_PER_CATEGORY_KEY))
    @patch.object(aov.AOV, "components", new_callable=PropertyMock(return_value=[]))
    @patch.object(aov.AOV, "componentexport", new_callable=PropertyMock)
    @patch.object(aov.AOV, "exclude_from_dcm", new_callable=PropertyMock)
    @patch.object(aov.AOV, "pfilter", new_callable=PropertyMock)
    @patch.object(aov.AOV, "sfilter", new_callable=PropertyMock)
    @patch.object(aov.AOV, "quantize", new_callable=PropertyMock)
    @patch.object(aov.AOV, "channel", new_callable=PropertyMock)
    @patch.object(aov.AOV, "vextype", new_callable=PropertyMock)
    @patch.object(aov.AOV, "variable", new_callable=PropertyMock)
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_as_data__values_per_category_no_components(self, *args, **kwargs):
        inst = aov.AOV(None)
        result = inst.as_data()

        expected = {
            consts.VARIABLE_KEY: inst.variable,
            consts.VEXTYPE_KEY: inst.vextype,
            consts.CHANNEL_KEY: inst.channel,
            consts.QUANTIZE_KEY: inst.quantize,
            consts.SFILTER_KEY: inst.sfilter,
            consts.PFILTER_KEY: inst.pfilter,
            consts.EXCLUDE_DCM_KEY: inst.exclude_from_dcm,
            consts.COMPONENTEXPORT_KEY: inst.componentexport,
            consts.LIGHTEXPORT_KEY: inst.lightexport,
            consts.INTRINSICS_KEY: inst.intrinsics,
            consts.COMMENT_KEY: inst.comment,
            consts.PRIORITY_KEY: inst.priority
        }
        assert result == expected

    @patch.object(aov.AOV, "priority", new_callable=PropertyMock)
    @patch.object(aov.AOV, "comment", new_callable=PropertyMock)
    @patch.object(aov.AOV, "intrinsics", new_callable=PropertyMock)
    @patch.object(aov.AOV, "lightexport_select", new_callable=PropertyMock)
    @patch.object(aov.AOV, "lightexport_scope", new_callable=PropertyMock)
    @patch.object(aov.AOV, "lightexport", new_callable=PropertyMock)
    @patch.object(aov.AOV, "components", new_callable=PropertyMock)
    @patch.object(aov.AOV, "componentexport", new_callable=PropertyMock(return_value=True))
    @patch.object(aov.AOV, "exclude_from_dcm", new_callable=PropertyMock)
    @patch.object(aov.AOV, "pfilter", new_callable=PropertyMock)
    @patch.object(aov.AOV, "sfilter", new_callable=PropertyMock)
    @patch.object(aov.AOV, "quantize", new_callable=PropertyMock)
    @patch.object(aov.AOV, "channel", new_callable=PropertyMock)
    @patch.object(aov.AOV, "vextype", new_callable=PropertyMock)
    @patch.object(aov.AOV, "variable", new_callable=PropertyMock)
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_as_data__values_exports_components(self, *args, **kwargs):
        inst = aov.AOV(None)

        result = inst.as_data()

        expected = {
            consts.VARIABLE_KEY: inst.variable,
            consts.VEXTYPE_KEY: inst.vextype,
            consts.CHANNEL_KEY: inst.channel,
            consts.QUANTIZE_KEY: inst.quantize,
            consts.SFILTER_KEY: inst.sfilter,
            consts.PFILTER_KEY: inst.pfilter,
            consts.EXCLUDE_DCM_KEY: inst.exclude_from_dcm,
            consts.COMPONENTEXPORT_KEY: inst.componentexport,
            consts.COMPONENTS_KEY: inst.components,
            consts.LIGHTEXPORT_KEY: inst.lightexport,
            consts.LIGHTEXPORT_SCOPE_KEY: inst.lightexport_scope,
            consts.LIGHTEXPORT_SELECT_KEY: inst.lightexport_select,
            consts.INTRINSICS_KEY: inst.intrinsics,
            consts.COMMENT_KEY: inst.comment,
            consts.PRIORITY_KEY: inst.priority
        }

        assert result == expected

    # write_to_ifd

    @patch.object(aov.AOV, "_light_export_planes")
    @patch.object(aov.AOV, "componentexport", new_callable=PropertyMock(return_value=False))
    @patch.object(aov.AOV, "variable", new_callable=PropertyMock)
    @patch.object(aov.AOV, "channel", new_callable=PropertyMock(return_value=None))
    @patch.object(aov.AOV, "as_data")
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_write_to_ifd__no_channel_no_comp(self, mock_as_data, mock_channel, mock_variable, mock_component, mock_export, patch_soho):
        mock_as_data.return_value = {"key": "value"}

        inst = aov.AOV(None)

        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        mock_now = MagicMock(spec=float)

        inst.write_to_ifd(mock_wrangler, mock_cam, mock_now)

        mock_export.assert_called_with(
            {"key": "value", consts.CHANNEL_KEY: mock_variable.return_value},
            mock_wrangler,
            mock_cam,
            mock_now
        )

    @patch.object(aov.AOV, "_light_export_planes")
    @patch.object(aov.AOV, "componentexport", new_callable=PropertyMock(return_value=False))
    @patch.object(aov.AOV, "channel", new_callable=PropertyMock)
    @patch.object(aov.AOV, "as_data")
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_write_to_ifd__channel_no_comp(self, mock_as_data, mock_channel, mock_component, mock_export, patch_soho):
        mock_as_data.return_value = {"key": "value"}

        inst = aov.AOV(None)

        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        mock_now = MagicMock(spec=float)

        inst.write_to_ifd(mock_wrangler, mock_cam, mock_now)

        mock_export.assert_called_with(
            {"key": "value", consts.CHANNEL_KEY: mock_channel.return_value},
            mock_wrangler,
            mock_cam,
            mock_now
        )

    @patch.object(aov.AOV, "_light_export_planes")
    @patch.object(aov.AOV, "components", new_callable=PropertyMock(return_value=[]))
    @patch.object(aov.AOV, "componentexport", new_callable=PropertyMock(return_value=True))
    @patch.object(aov.AOV, "channel", new_callable=PropertyMock)
    @patch.object(aov.AOV, "as_data")
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_write_to_ifd__export_no_comp(self, mock_as_data, mock_channel, mock_compexport, mock_components, mock_export, patch_soho):
        mock_as_data.return_value = {"key": "value"}

        inst = aov.AOV(None)

        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        mock_now = MagicMock(spec=float)

        mock_parm = MagicMock()
        patch_soho[0].SohoParm.return_value = mock_parm

        mock_cam.wrangle.return_value = {}

        inst.write_to_ifd(mock_wrangler, mock_cam, mock_now)

        patch_soho[0].SohoParm.assert_called_with("vm_exportcomponents", "str", [''], skipdefault=False)

        mock_export.assert_not_called()

    @patch.object(aov.AOV, "_light_export_planes")
    @patch.object(aov.AOV, "components", new_callable=PropertyMock(return_value=[]))
    @patch.object(aov.AOV, "componentexport", new_callable=PropertyMock(return_value=True))
    @patch.object(aov.AOV, "channel", new_callable=PropertyMock(return_value="Pworld"))
    @patch.object(aov.AOV, "as_data")
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_write_to_ifd__export_components_from_node(self, mock_as_data, mock_channel, mock_compexport, mock_components, mock_export, patch_soho):
        mock_as_data.return_value = {"key": "value"}

        inst = aov.AOV(None)

        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        mock_now = MagicMock(spec=float)

        mock_parm = MagicMock()
        patch_soho[0].SohoParm.return_value = mock_parm

        mock_result = MagicMock()
        mock_result.Value = ["comp1 comp2"]

        mock_cam.wrangle.return_value = {
            "vm_exportcomponents": mock_result
        }

        inst.write_to_ifd(mock_wrangler, mock_cam, mock_now)

        patch_soho[0].SohoParm.assert_called_with("vm_exportcomponents", "str", [''], skipdefault=False)

        calls = [
            call({"key": "value", consts.CHANNEL_KEY: "Pworld_comp1", consts.COMPONENT_KEY: "comp1"}, mock_wrangler, mock_cam, mock_now),
            call({"key": "value", consts.CHANNEL_KEY: "Pworld_comp2", consts.COMPONENT_KEY: "comp2"}, mock_wrangler, mock_cam, mock_now)
        ]

        mock_export.assert_has_calls(calls)

    @patch.object(aov.AOV, "_light_export_planes")
    @patch.object(aov.AOV, "components", new_callable=PropertyMock(return_value=["comp3", "comp4"]))
    @patch.object(aov.AOV, "componentexport", new_callable=PropertyMock(return_value=True))
    @patch.object(aov.AOV, "channel", new_callable=PropertyMock(return_value="Pworld"))
    @patch.object(aov.AOV, "as_data")
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_write_to_ifd__export_components(self, mock_as_data, mock_channel, mock_compexport, mock_components, mock_export, patch_soho):
        mock_as_data.return_value = {"key": "value"}

        inst = aov.AOV(None)

        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        mock_now = MagicMock(spec=float)

        inst.write_to_ifd(mock_wrangler, mock_cam, mock_now)

        calls = [
            call({"key": "value", consts.CHANNEL_KEY: "Pworld_comp3", consts.COMPONENT_KEY: "comp3"}, mock_wrangler, mock_cam, mock_now),
            call({"key": "value", consts.CHANNEL_KEY: "Pworld_comp4", consts.COMPONENT_KEY: "comp4"}, mock_wrangler, mock_cam, mock_now)
        ]

        mock_export.assert_has_calls(calls)


class Test_AOVGroup(object):
    """Test ht.sohohooks.aovs.AOVGroup object."""

    # __init__

    def test___init__(self):
        mock_name = MagicMock(spec=str)

        group = aov.AOVGroup(mock_name)

        assert group._aovs == []
        assert group._comment == ""
        assert group._icon is None
        assert group._includes == []
        assert group._name == mock_name
        assert group._path is None
        assert group._priority == -1

    # __eq__

    @patch("ht.sohohooks.aovs.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___eq___equal(self, mock_name):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock(spec=aov.AOVGroup)
        type(group2).name = PropertyMock(return_value="name")

        result = group1.__eq__(group2)

        assert result

    @patch("ht.sohohooks.aovs.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name1"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___eq___not_equal(self, mock_name):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock(spec=aov.AOVGroup)
        type(group2).name = PropertyMock(return_value="name2")

        result = group1.__eq__(group2)

        assert not result

    @patch("ht.sohohooks.aovs.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name1"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___eq___non_group(self, mock_name):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock()

        result = group1.__eq__(group2)

        assert result == NotImplemented

    # ge

    @patch("ht.sohohooks.aovs.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name1"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___ge___less_than(self, mock_name):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock(spec=aov.AOVGroup)
        type(group2).name = PropertyMock(return_value="name2")

        result = group1.__ge__(group2)

        assert not result

    @patch("ht.sohohooks.aovs.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name1"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___ge___equal(self, mock_name):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock(spec=aov.AOVGroup)
        type(group2).name = PropertyMock(return_value="name1")

        result = group1.__ge__(group2)

        assert result

    @patch("ht.sohohooks.aovs.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name3"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___ge___greater_than(self, mock_name):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock(spec=aov.AOVGroup)
        type(group2).name = PropertyMock(return_value="name2")

        result = group1.__ge__(group2)

        assert result

    @patch("ht.sohohooks.aovs.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name1"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___ge___non_group(self, mock_name):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock()

        result = group1.__ge__(group2)
        assert result == NotImplemented

    # gt

    @patch("ht.sohohooks.aovs.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name1"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___gt___less_than(self, mock_name):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock(spec=aov.AOVGroup)
        type(group2).name = PropertyMock(return_value="name2")

        result = group1.__gt__(group2)

        assert not result

    @patch("ht.sohohooks.aovs.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name1"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___gt___equal(self, mock_name):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock(spec=aov.AOVGroup)
        type(group2).name = PropertyMock(return_value="name1")

        result = group1.__gt__(group2)

        assert not result

    @patch("ht.sohohooks.aovs.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name3"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___gt___greater_than(self, mock_name):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock(spec=aov.AOVGroup)
        type(group2).name = PropertyMock(return_value="name2")

        result = group1.__gt__(group2)

        assert result

    @patch("ht.sohohooks.aovs.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name1"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___gt___non_group(self, mock_name):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock()

        result = group1.__gt__(group2)
        assert result == NotImplemented

    # __hash__

    @patch("ht.sohohooks.aovs.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name1"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___hash__(self, mock_variable):
        group1 = aov.AOVGroup(None)

        result = group1.__hash__()

        assert result == hash("name1")

        assert hash(group1) == hash("name1")

    # le

    @patch("ht.sohohooks.aovs.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name1"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___le___less_than(self, mock_name):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock(spec=aov.AOVGroup)
        type(group2).name = PropertyMock(return_value="name2")

        result = group1.__le__(group2)

        assert result

    @patch("ht.sohohooks.aovs.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name1"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___le___equal(self, mock_name):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock(spec=aov.AOVGroup)
        type(group2).name = PropertyMock(return_value="name1")

        result = group1.__le__(group2)

        assert result

    @patch("ht.sohohooks.aovs.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name3"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___le___greater_than(self, mock_name):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock(spec=aov.AOVGroup)
        type(group2).name = PropertyMock(return_value="name2")

        result = group1.__le__(group2)

        assert not result

    @patch("ht.sohohooks.aovs.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name1"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___le___non_group(self, mock_name):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock()

        result = group1.__le__(group2)

        assert result == NotImplemented

    # lt

    @patch("ht.sohohooks.aovs.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name1"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___lt___less_than(self, mock_name):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock(spec=aov.AOVGroup)
        type(group2).name = PropertyMock(return_value="name2")

        result = group1.__lt__(group2)

        assert result

    @patch("ht.sohohooks.aovs.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name1"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___lt___equal(self, mock_name):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock(spec=aov.AOVGroup)
        type(group2).name = PropertyMock(return_value="name1")

        result = group1.__lt__(group2)

        assert not result

    @patch("ht.sohohooks.aovs.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name3"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___lt___greater_than(self, mock_name):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock(spec=aov.AOVGroup)
        type(group2).name = PropertyMock(return_value="name2")

        result = group1.__lt__(group2)

        assert not result

    @patch("ht.sohohooks.aovs.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name1"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___lt___non_group(self, mock_name):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock()

        result = group1.__lt__(group2)

        assert result == NotImplemented

    # __ne__

    @patch.object(aov.AOVGroup, "__eq__")
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___ne___not_equal(self, mock_eq):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock(spec=aov.AOVGroup)

        result = group1.__ne__(group2)

        assert result != mock_eq.return_value
        mock_eq.assert_called_with(group2)

    @patch("ht.sohohooks.aovs.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name1"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___ne___non_group(self, mock_name):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock()

        result = group1.__ne__(group2)

        assert result == NotImplemented

    # Properties

    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test_aovs(self):
        mock_aov = MagicMock(spec=aov.AOV)

        group = aov.AOVGroup(None)
        group._aovs = [mock_aov]

        assert group.aovs == [mock_aov]

        with pytest.raises(AttributeError):
            group.aovs = []

    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test_comment(self):
        mock_value1 = MagicMock(spec=str)

        group = aov.AOVGroup(None)

        group._comment = mock_value1
        assert group.comment == mock_value1

        mock_value2 = MagicMock(spec=str)
        group.comment = mock_value2
        assert group._comment == mock_value2

    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test_icon(self):
        mock_value1 = MagicMock(spec=str)

        group = aov.AOVGroup(None)

        group._icon = mock_value1
        assert group.icon == mock_value1

        mock_value2 = MagicMock(spec=str)
        group.icon = mock_value2
        assert group._icon == mock_value2

    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test_includes(self):
        mock_value1 = MagicMock(spec=list)

        group = aov.AOVGroup(None)

        group._includes = mock_value1
        assert group.includes == mock_value1

        with pytest.raises(AttributeError):
            group.includes = mock_value1

    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test_name(self):
        mock_value = MagicMock(spec=str)

        group = aov.AOVGroup(None)

        group._name = mock_value
        assert group.name == mock_value

        with pytest.raises(AttributeError):
            group.name = mock_value

    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test_path(self):
        mock_value1 = MagicMock(spec=str)

        group = aov.AOVGroup(None)

        group._path = mock_value1
        assert group.path == mock_value1

        mock_value2 = MagicMock(spec=str)
        group.path = mock_value2
        assert group._path == mock_value2

    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test_priority(self):
        mock_value1 = MagicMock(spec=int)

        group = aov.AOVGroup(None)

        group._priority = mock_value1
        assert group.priority == mock_value1

        mock_value2 = MagicMock(spec=int)
        group.priority = mock_value2
        assert group._priority == mock_value2

    # clear

    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test_clear(self):
        mock_aov = MagicMock(spec=aov.AOV)

        group = aov.AOVGroup(None)
        group._aovs = [mock_aov]

        group.clear()

        assert group._aovs == []

    # as_data

    @patch.object(aov.AOVGroup, "priority", new_callable=PropertyMock(return_value=-1))
    @patch.object(aov.AOVGroup, "comment", new_callable=PropertyMock(return_value=""))
    @patch.object(aov.AOVGroup, "aovs", new_callable=PropertyMock)
    @patch.object(aov.AOVGroup, "name", new_callable=PropertyMock)
    @patch.object(aov.AOVGroup, "includes", new_callable=PropertyMock)
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test_as_data__no_comment_or_priority(self, mock_includes, mock_name, mock_aovs, mock_comment, mock_priority):
        mock_var_name1 = MagicMock(spec=str)
        mock_var_name2 = MagicMock(spec=str)

        mock_includes.return_value = [mock_var_name1, mock_var_name2]

        mock_aov1 = MagicMock(spec=aov.AOV)
        mock_aov2 = MagicMock(spec=aov.AOV)

        mock_aovs.return_value = [mock_aov1, mock_aov2]

        expected = {
            mock_name.return_value: {
                consts.GROUP_INCLUDE_KEY: [mock_var_name1, mock_var_name2, mock_aov1.variable, mock_aov2.variable],

            }
        }

        group = aov.AOVGroup(None)

        result = group.as_data()

        assert result == expected

    @patch.object(aov.AOVGroup, "priority", new_callable=PropertyMock)
    @patch.object(aov.AOVGroup, "comment", new_callable=PropertyMock)
    @patch.object(aov.AOVGroup, "aovs", new_callable=PropertyMock)
    @patch.object(aov.AOVGroup, "name", new_callable=PropertyMock)
    @patch.object(aov.AOVGroup, "includes", new_callable=PropertyMock)
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test_as_data(self, mock_includes, mock_name, mock_aovs, mock_comment, mock_priority):
        mock_var_name1 = MagicMock(spec=str)
        mock_var_name2 = MagicMock(spec=str)

        mock_includes.return_value = [mock_var_name1, mock_var_name2]

        mock_aov1 = MagicMock(spec=aov.AOV)
        mock_aov2 = MagicMock(spec=aov.AOV)
        mock_aovs.return_value = [mock_aov1, mock_aov2]

        expected = {
            mock_name.return_value: {
                consts.GROUP_INCLUDE_KEY: [mock_var_name1, mock_var_name2, mock_aov1.variable, mock_aov2.variable],
                consts.PRIORITY_KEY: mock_priority.return_value,
                consts.COMMENT_KEY: mock_comment.return_value

            }
        }

        group = aov.AOVGroup(None)

        result = group.as_data()

        assert result == expected

    @patch.object(aov.AOVGroup, "aovs", new_callable=PropertyMock)
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test_write_to_ifd(self, mock_aovs):
        mock_aov1 = MagicMock(spec=aov.AOV)
        mock_aov2 = MagicMock(spec=aov.AOV)

        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        mock_now = MagicMock(spec=float)

        mock_aovs.return_value = [mock_aov1, mock_aov2]

        group = aov.AOVGroup(None)

        group.write_to_ifd(mock_wrangler, mock_cam, mock_now)

        mock_aov1.write_to_ifd.assert_called_with(mock_wrangler, mock_cam, mock_now)
        mock_aov2.write_to_ifd.assert_called_with(mock_wrangler, mock_cam, mock_now)


class Test_IntrinsicAOVGroup(object):

    @patch("ht.sohohooks.aovs.aov.AOVGroup.__init__")
    def test___init__(self, mock_super_init):
        mock_name = MagicMock(spec=str)

        result = aov.IntrinsicAOVGroup(mock_name)

        mock_super_init.assert_called_with(mock_name)
        assert result._comment == "Automatically generated"


class Test__build_category_map(object):

    def test_no_parm(self):
        mock_light1 = MagicMock()

        lights = (mock_light1, )

        mock_now = MagicMock(spec=float)

        result = aov._build_category_map(lights, mock_now)

        assert result == {}

        mock_light1.evalString.assert_called_with("categories", mock_now, [])

    def test_no_categories(self):
        mock_light1 = MagicMock()

        mock_light1.evalString.side_effect = lambda name, t, value: value.append("")

        lights = (mock_light1, )

        mock_now = MagicMock(spec=float)

        result = aov._build_category_map(lights, mock_now)

        assert result == {None: [mock_light1]}

    def test_categories(self):
        mock_light1 = MagicMock()
        mock_light1.evalString.side_effect = lambda name, t, value: value.append("cat1 cat2")

        mock_light2 = MagicMock()
        mock_light2.evalString.side_effect = lambda name, t, value: value.append("cat2,cat3")

        lights = (mock_light1, mock_light2)

        mock_now = MagicMock(spec=float)

        result = aov._build_category_map(lights, mock_now)

        assert result == {"cat1": [mock_light1], "cat2": [mock_light1, mock_light2], "cat3": [mock_light2]}


class Test__call_post_defplane(object):

    def test(self, patch_soho):
        mock_variable = MagicMock(spec=str)
        mock_vextype = MagicMock(spec=str)
        mock_planefile = MagicMock(spec=str)
        mock_lightexport = MagicMock(spec=str)

        data = {
            consts.VARIABLE_KEY: mock_variable,
            consts.VEXTYPE_KEY: mock_vextype,
            consts.PLANEFILE_KEY: mock_planefile,
            consts.LIGHTEXPORT_KEY: mock_lightexport
        }

        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        mock_now = MagicMock(spec=float)

        aov._call_post_defplane(
            data,
            mock_wrangler,
            mock_cam,
            mock_now
        )

        patch_soho[2].call.assert_called_with(
            "post_defplane",
            mock_variable,
            mock_vextype,
            -1,
            mock_wrangler,
            mock_cam,
            mock_now,
            mock_planefile,
            mock_lightexport
        )


class Test__call_pre_defplane(object):

    def test(self, patch_soho):
        mock_variable = MagicMock(spec=str)
        mock_vextype = MagicMock(spec=str)
        mock_planefile = MagicMock(spec=str)
        mock_lightexport = MagicMock(spec=str)

        data = {
            consts.VARIABLE_KEY: mock_variable,
            consts.VEXTYPE_KEY: mock_vextype,
            consts.PLANEFILE_KEY: mock_planefile,
            consts.LIGHTEXPORT_KEY: mock_lightexport
        }

        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        mock_now = MagicMock(spec=float)

        aov._call_pre_defplane(
            data,
            mock_wrangler,
            mock_cam,
            mock_now
        )

        patch_soho[2].call.assert_called_with(
            "pre_defplane",
            mock_variable,
            mock_vextype,
            -1,
            mock_wrangler,
            mock_cam,
            mock_now,
            mock_planefile,
            mock_lightexport
        )


class Test__write_data_to_ifd(object):

    @patch("ht.sohohooks.aovs.aov._call_pre_defplane")
    def test_pre_defplane(self, mock_pre, patch_soho):
        mock_pre.return_value = True

        data = {}
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        mock_now = MagicMock(spec=float)

        aov._write_data_to_ifd(data, mock_wrangler, mock_cam, mock_now)

        mock_pre.assert_called_with(data, mock_wrangler, mock_cam, mock_now)

        patch_soho[1].ray_start.assert_not_called()

    @patch("ht.sohohooks.aovs.aov._call_post_defplane")
    @patch("ht.sohohooks.aovs.aov._call_pre_defplane")
    def test_base_data(self, mock_pre, mock_post, patch_soho):
        mock_pre.return_value = False
        mock_post.return_value = False

        mock_variable = MagicMock(spec=str)
        mock_vextype = MagicMock(spec=str)
        mock_channel = MagicMock(spec=str)

        data = {
            consts.VARIABLE_KEY: mock_variable,
            consts.VEXTYPE_KEY: mock_vextype,
            consts.CHANNEL_KEY: mock_channel,
        }

        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        mock_now = MagicMock(spec=float)

        aov._write_data_to_ifd(data, mock_wrangler, mock_cam, mock_now)

        calls = [
            call("plane", "variable", [mock_variable]),
            call("plane", "vextype", [mock_vextype]),
            call("plane", "channel", [mock_channel]),

        ]

        patch_soho[1].ray_property.assert_has_calls(calls)

        mock_pre.assert_called_with(data, mock_wrangler, mock_cam, mock_now)
        mock_post.assert_called_with(data, mock_wrangler, mock_cam, mock_now)

    @patch("ht.sohohooks.aovs.aov._call_post_defplane")
    @patch("ht.sohohooks.aovs.aov._call_pre_defplane")
    def test_full_data(self, mock_pre, mock_post, patch_soho):
        mock_pre.return_value = False
        mock_post.return_value = False

        mock_variable = MagicMock(spec=str)
        mock_vextype = MagicMock(spec=str)
        mock_channel = MagicMock(spec=str)
        mock_quantize = MagicMock(spec=str)
        mock_planefile = MagicMock(spec=str)
        mock_lightexport = MagicMock(spec=str)
        mock_pfilter = MagicMock(spec=str)
        mock_sfilter = MagicMock(spec=str)
        mock_component = MagicMock(spec=str)
        mock_exclude_from_dcm = MagicMock(spec=str)

        data = {
            consts.VARIABLE_KEY: mock_variable,
            consts.VEXTYPE_KEY: mock_vextype,
            consts.CHANNEL_KEY: mock_channel,
            consts.QUANTIZE_KEY: mock_quantize,
            consts.PLANEFILE_KEY: mock_planefile,
            consts.LIGHTEXPORT_KEY: mock_lightexport,
            consts.PFILTER_KEY: mock_pfilter,
            consts.SFILTER_KEY: mock_sfilter,
            consts.COMPONENT_KEY: mock_component,
            consts.EXCLUDE_DCM_KEY: mock_exclude_from_dcm
        }
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        mock_now = MagicMock(spec=float)

        aov._write_data_to_ifd(data, mock_wrangler, mock_cam, mock_now)

        calls = [
            call("plane", "variable", [mock_variable]),
            call("plane", "vextype", [mock_vextype]),
            call("plane", "channel", [mock_channel]),
            call("plane", "quantize", [mock_quantize]),
            call("plane", "planefile", [mock_planefile]),
            call("plane", "lightexport", [mock_lightexport]),
            call("plane", "pfilter", [mock_pfilter]),
            call("plane", "sfilter", [mock_sfilter]),
            call("plane", "component", [mock_component]),
            call("plane", "excludedcm", [True]),
        ]

        patch_soho[1].ray_property.assert_has_calls(calls)

        mock_pre.assert_called_with(data, mock_wrangler, mock_cam, mock_now)
        mock_post.assert_called_with(data, mock_wrangler, mock_cam, mock_now)

    @patch("ht.sohohooks.aovs.aov._call_post_defplane")
    @patch("ht.sohohooks.aovs.aov._call_pre_defplane")
    def test_None_planefile(self, mock_pre, mock_post, patch_soho):
        mock_pre.return_value = False
        mock_post.return_value = False

        mock_variable = MagicMock(spec=str)
        mock_vextype = MagicMock(spec=str)
        mock_channel = MagicMock(spec=str)

        data = {
            consts.VARIABLE_KEY: mock_variable,
            consts.VEXTYPE_KEY: mock_vextype,
            consts.CHANNEL_KEY: mock_channel,
            consts.PLANEFILE_KEY: None,
        }

        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        mock_now = MagicMock(spec=float)

        aov._write_data_to_ifd(data, mock_wrangler, mock_cam, mock_now)

        calls = [
            call("plane", "variable", [mock_variable]),
            call("plane", "vextype", [mock_vextype]),
            call("plane", "channel", [mock_channel]),
        ]

        patch_soho[1].ray_property.assert_has_calls(calls)

        mock_pre.assert_called_with(data, mock_wrangler, mock_cam, mock_now)
        mock_post.assert_called_with(data, mock_wrangler, mock_cam, mock_now)

    @patch("ht.sohohooks.aovs.aov._call_post_defplane")
    @patch("ht.sohohooks.aovs.aov._call_pre_defplane")
    def test_post_defplane(self, mock_pre, mock_post, patch_soho):
        mock_pre.return_value = False
        mock_post.return_value = True

        mock_variable = MagicMock(spec=str)
        mock_vextype = MagicMock(spec=str)
        mock_channel = MagicMock(spec=str)

        data = {
            consts.VARIABLE_KEY: mock_variable,
            consts.VEXTYPE_KEY: mock_vextype,
            consts.CHANNEL_KEY: mock_channel,
        }

        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        mock_now = MagicMock(spec=float)

        aov._write_data_to_ifd(data, mock_wrangler, mock_cam, mock_now)

        calls = [
            call("plane", "variable", [mock_variable]),
            call("plane", "vextype", [mock_vextype]),
            call("plane", "channel", [mock_channel]),
        ]

        patch_soho[1].ray_property.assert_has_calls(calls)

        mock_pre.assert_called_with(data, mock_wrangler, mock_cam, mock_now)
        mock_post.assert_called_with(data, mock_wrangler, mock_cam, mock_now)

        patch_soho[1].ray_end.assert_not_called()


class Test__write_light(object):

    @patch("ht.sohohooks.aovs.aov._write_data_to_ifd")
    def test_suffix_prefix(self, mock_write, patch_soho):
        mock_light = MagicMock()
        mock_light.getName.return_value = "light1"

        mock_light.getDefaultedString.return_value = ["suffix"]

        def evalString(name, mock_now, prefix):
            prefix.append("prefix")
            return True

        mock_light.evalString.side_effect = evalString

        data = {}
        base_channel = "base"
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        mock_now = MagicMock(spec=float)

        aov._write_light(mock_light, base_channel, data, mock_wrangler, mock_cam, mock_now)

        mock_write.assert_called_with(
            {
                consts.LIGHTEXPORT_KEY: "light1",
                consts.CHANNEL_KEY: "prefix_basesuffix"
            },
            mock_wrangler,
            mock_cam,
            mock_now
        )

    @patch("ht.sohohooks.aovs.aov._write_data_to_ifd")
    def test_no_suffix_path_prefix(self, mock_write, patch_soho):
        mock_light = MagicMock()
        mock_light.getName.return_value = "/obj/light1"

        def getDefaulted(name, mock_now, default):
            return default

        mock_light.getDefaultedString.side_effect = getDefaulted

        mock_light.evalString.return_value = False

        data = {}
        base_channel = "base"
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        mock_now = MagicMock(spec=float)

        aov._write_light(mock_light, base_channel, data, mock_wrangler, mock_cam, mock_now)

        mock_write.assert_called_with(
            {
                consts.LIGHTEXPORT_KEY: "/obj/light1",
                consts.CHANNEL_KEY: "obj_light1_base"
            },
            mock_wrangler,
            mock_cam,
            mock_now
        )

    @patch("ht.sohohooks.aovs.aov._write_data_to_ifd")
    def test_suffix_no_prefix(self, mock_write, patch_soho):
        mock_light = MagicMock()
        mock_light.getName.return_value = "/obj/light1"

        mock_light.getDefaultedString.return_value = ["suffix"]

        mock_light.evalString.return_value = True

        data = {}
        base_channel = "base"
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        mock_now = MagicMock(spec=float)

        aov._write_light(mock_light, base_channel, data, mock_wrangler, mock_cam, mock_now)

        mock_write.assert_called_with(
            {
                consts.LIGHTEXPORT_KEY: "/obj/light1",
                consts.CHANNEL_KEY: "basesuffix"
            },
            mock_wrangler,
            mock_cam,
            mock_now
        )

    @patch("ht.sohohooks.aovs.aov._write_data_to_ifd")
    def test_empty_suffix(self, mock_write, patch_soho):
        mock_light = MagicMock()
        mock_light.getName.return_value = "/obj/light1"

        mock_light.getDefaultedString.return_value = ['']

        mock_light.evalString.return_value = True

        data = {}
        base_channel = "base"
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        mock_now = MagicMock(spec=float)

        aov._write_light(mock_light, base_channel, data, mock_wrangler, mock_cam, mock_now)

        patch_soho[0].error.assert_called()

        mock_write.assert_called_with(
            {
                consts.LIGHTEXPORT_KEY: "/obj/light1",
                consts.CHANNEL_KEY: "base"
            },
            mock_wrangler,
            mock_cam,
            mock_now
        )


class Test__write_per_category(object):

    @patch("ht.sohohooks.aovs.aov._write_data_to_ifd")
    @patch("ht.sohohooks.aovs.aov._build_category_map")
    def test_no_category(self, mock_build, mock_write):
        mock_light1 = MagicMock()
        mock_light1.getName.return_value = "light1"

        mock_light2 = MagicMock()
        mock_light2.getName.return_value = "light2"

        lights = (mock_light1, mock_light2)

        category_lights = lights

        mock_build.return_value = {None: category_lights}

        data = {}
        base_channel = "base"
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        mock_now = MagicMock(spec=float)

        aov._write_per_category(lights, base_channel, data, mock_wrangler, mock_cam, mock_now)

        mock_write.assert_called_with(
            {
                consts.LIGHTEXPORT_KEY: "light1 light2",
                consts.CHANNEL_KEY: base_channel
            },
            mock_wrangler,
            mock_cam,
            mock_now
        )

    @patch("ht.sohohooks.aovs.aov._write_data_to_ifd")
    @patch("ht.sohohooks.aovs.aov._build_category_map")
    def test_category(self, mock_build, mock_write):
        mock_light1 = MagicMock()
        mock_light1.getName.return_value = "light1"

        mock_light2 = MagicMock()
        mock_light2.getName.return_value = "light2"

        lights = (mock_light1, mock_light2)

        category_lights = lights

        category = "test"

        mock_build.return_value = {category: category_lights}

        data = {}
        base_channel = "base"
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        mock_now = MagicMock(spec=float)

        aov._write_per_category(lights, base_channel, data, mock_wrangler, mock_cam, mock_now)

        mock_write.assert_called_with(
            {
                consts.LIGHTEXPORT_KEY: "light1 light2",
                consts.CHANNEL_KEY: "{}_{}".format(category, base_channel)
            },
            mock_wrangler,
            mock_cam,
            mock_now
        )


class Test__write_single_channel(object):

    @patch("ht.sohohooks.aovs.aov._write_data_to_ifd")
    def test_lights(self, mock_write):
        mock_light1 = MagicMock()
        mock_light1.getName.return_value = "light1"

        mock_light2 = MagicMock()
        mock_light2.getName.return_value = "light2"

        lights = (mock_light1, mock_light2)

        data = {}
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        mock_now = MagicMock(spec=float)

        aov._write_single_channel(lights, data, mock_wrangler, mock_cam, mock_now)

        mock_write.assert_called_with(
            {consts.LIGHTEXPORT_KEY: "light1 light2"},
            mock_wrangler,
            mock_cam,
            mock_now
        )

    @patch("ht.sohohooks.aovs.aov._write_data_to_ifd")
    def test_no_lights(self, mock_write):
        lights = ()

        data = {}
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        mock_now = MagicMock(spec=float)

        aov._write_single_channel(lights, data, mock_wrangler, mock_cam, mock_now)

        mock_write.assert_called_with(
            {consts.LIGHTEXPORT_KEY: "__nolights__"},
            mock_wrangler,
            mock_cam,
            mock_now
        )
