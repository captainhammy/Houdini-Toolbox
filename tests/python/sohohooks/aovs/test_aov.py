"""Test the houdini_toolbox.sohohooks.aovs.aov module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
from contextlib import contextmanager

# Third Party
import pytest

# Houdini Toolbox
from houdini_toolbox.sohohooks.aovs import aov
from houdini_toolbox.sohohooks.aovs import constants as consts

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def init_aov(mocker):
    """Fixture to initialize an aov."""
    mocker.patch.object(aov.AOV, "__init__", lambda x, y: None)

    def _create():
        return aov.AOV(None)

    return _create


@pytest.fixture
def init_group(mocker):
    """Fixture to initialize an aov."""
    mocker.patch.object(aov.AOVGroup, "__init__", lambda x, y: None)

    def _create():
        return aov.AOVGroup(None)

    return _create


@contextmanager
def does_not_raise():
    """Dummy for testing"""
    yield


# =============================================================================
# TESTS
# =============================================================================


class Test_AOV:
    """Test houdini_toolbox.sohohooks.aovs.AOV object."""

    def test___init__(self, mocker):
        """Test object initialization."""
        mock_copy = mocker.patch("houdini_toolbox.sohohooks.aovs.aov.copy.copy")
        mock_update = mocker.patch.object(aov.AOV, "update_data")

        data = mocker.MagicMock(spec=dict)

        aov.AOV(data)

        mock_copy.assert_called_with(aov._DEFAULT_AOV_DATA)
        mock_update.assert_called_with(data)

    # Special Methods

    @pytest.mark.parametrize("equals", (None, True, False))
    def test___eq__(self, init_aov, mocker, equals):
        """Test object equality."""
        mock_variable_value = mocker.MagicMock(spec=str)

        mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov.AOV.variable",
            new_callable=mocker.PropertyMock(return_value=mock_variable_value),
        )

        inst1 = init_aov()

        # If equals is None then the other object won't be an AOV.
        if equals is None:
            inst2 = mocker.MagicMock()

            # Check for NotImplemented since the objects aren't of the same type.
            assert inst1.__eq__(inst2) == NotImplemented

        else:
            inst2 = mocker.MagicMock(spec=aov.AOV)

            # Ensure the variables are equal.
            if equals:
                type(inst2).variable = mock_variable_value

            else:
                type(inst2).variable = mocker.PropertyMock(spec=str)

            if equals:
                assert inst1 == inst2

            else:
                assert inst1 != inst2

            mock_variable_value.__eq__.assert_called_with(inst2.variable)

    @pytest.mark.parametrize("ge", (None, True, False))
    def test___ge___greater_than(self, init_aov, mocker, ge):
        """Test greater than or equal operator."""
        mock_variable_value = mocker.MagicMock(spec=str)
        mock_variable_value.__ge__.return_value = ge

        mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov.AOV.variable",
            new_callable=mocker.PropertyMock(return_value=mock_variable_value),
        )

        inst1 = init_aov()

        if ge is None:
            inst2 = mocker.MagicMock()
            assert inst1.__ge__(inst2) == NotImplemented

        else:
            inst2 = mocker.MagicMock(spec=aov.AOV)

            result = inst1 >= inst2

            if ge:
                assert result

            else:
                assert not result

            mock_variable_value.__ge__.assert_called_with(inst2.variable)

    @pytest.mark.parametrize("gt", (None, True, False))
    def test___gt__(self, init_aov, mocker, gt):
        """Test greater than operator."""
        mock_variable_value = mocker.MagicMock(spec=str)
        mock_variable_value.__gt__.return_value = gt

        mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov.AOV.variable",
            new_callable=mocker.PropertyMock(return_value=mock_variable_value),
        )

        inst1 = init_aov()

        if gt is None:
            inst2 = mocker.MagicMock()

            assert inst1.__gt__(inst2) == NotImplemented

        else:
            inst2 = mocker.MagicMock(spec=aov.AOV)

            result = inst1 > inst2

            if gt:
                assert result

            else:
                assert not result

            mock_variable_value.__gt__.assert_called_with(inst2.variable)

    def test___hash__(self, init_aov, mocker):
        """Test hashing an AOV."""
        mock_variable_value = mocker.MagicMock(spec=str)
        mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov.AOV.variable",
            new_callable=mocker.PropertyMock(return_value=mock_variable_value),
        )

        inst1 = init_aov()

        result = inst1.__hash__()

        assert result == hash(mock_variable_value)

        assert hash(inst1) == hash(mock_variable_value)

    @pytest.mark.parametrize("le", (None, True, False))
    def test___le__(self, init_aov, mocker, le):
        """Test less than or equal operator."""
        mock_variable_value = mocker.MagicMock(spec=str)
        mock_variable_value.__le__.return_value = le

        mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov.AOV.variable",
            new_callable=mocker.PropertyMock(return_value=mock_variable_value),
        )

        inst1 = init_aov()

        if le is None:
            inst2 = mocker.MagicMock()

            assert inst1.__le__(inst2) == NotImplemented
        else:
            inst2 = mocker.MagicMock(spec=aov.AOV)

            result = inst1 <= inst2

            if le:
                assert result

            else:
                assert not result

            mock_variable_value.__le__.assert_called_with(inst2.variable)

    @pytest.mark.parametrize("lt", (None, True, False))
    def test___lt__(self, init_aov, mocker, lt):
        """Test less than operator."""
        mock_variable_value = mocker.MagicMock(spec=str)
        mock_variable_value.__lt__.return_value = lt

        mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov.AOV.variable",
            new_callable=mocker.PropertyMock(return_value=mock_variable_value),
        )

        inst1 = init_aov()

        if lt is None:
            inst2 = mocker.MagicMock()

            assert inst1.__lt__(inst2) == NotImplemented
        else:
            inst2 = mocker.MagicMock(spec=aov.AOV)

            result = inst1 < inst2

            if lt:
                assert result

            else:
                assert not result

            mock_variable_value.__lt__.assert_called_with(inst2.variable)

    def test___ne__(self, init_aov, mocker):
        """Test the not equals operator."""
        mock_eq = mocker.patch.object(aov.AOV, "__eq__")

        inst1 = init_aov()
        inst2 = mocker.MagicMock(spec=aov.AOV)

        result = inst1.__ne__(inst2)

        assert result != mock_eq.return_value
        mock_eq.assert_called_with(inst2)

    def test___str__(self, init_aov, mocker):
        """Test conversion to string."""
        mock_variable = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov.AOV.variable",
            new_callable=mocker.PropertyMock(spec=str),
        )

        inst1 = init_aov()

        result = inst1.__str__()

        assert result == mock_variable

    # Non-Public Methods

    @pytest.mark.parametrize(
        "export_value",
        [
            consts.LIGHTEXPORT_PER_LIGHT_KEY,
            consts.LIGHTEXPORT_SINGLE_KEY,
            consts.LIGHTEXPORT_PER_CATEGORY_KEY,
            "foo",
            None,
        ],
    )
    def test__light_export_planes(self, init_aov, mocker, export_value):
        """Test AOV._light_export_planes."""
        mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov.AOV.lightexport",
            new_callable=mocker.PropertyMock(return_value=export_value),
        )
        mock_scope = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov.AOV.lightexport_scope",
            new_callable=mocker.PropertyMock,
        )
        mock_select = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov.AOV.lightexport_select",
            new_callable=mocker.PropertyMock,
        )
        mock_write_light = mocker.patch("houdini_toolbox.sohohooks.aovs.aov._write_light")
        mock_write_single = mocker.patch("houdini_toolbox.sohohooks.aovs.aov._write_single_channel")
        mock_write_per_category = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov._write_per_category"
        )
        mock_write_to_ifd = mocker.patch("houdini_toolbox.sohohooks.aovs.aov._write_data_to_ifd")

        inst = init_aov()

        mock_light1 = mocker.MagicMock()
        mock_light2 = mocker.MagicMock()

        lights = [mock_light1, mock_light2]

        mock_channel = mocker.MagicMock(spec=str)
        data = {consts.CHANNEL_KEY: mock_channel}
        mock_wrangler = mocker.MagicMock()

        mock_cam = mocker.MagicMock()
        mock_cam.objectList.return_value = lights
        mock_now = mocker.MagicMock(spec=float)

        if export_value == "foo":
            with pytest.raises(aov.InvalidAOVValueError):
                inst._light_export_planes(data, mock_wrangler, mock_cam, mock_now)

        else:
            inst._light_export_planes(data, mock_wrangler, mock_cam, mock_now)

            if export_value is not None:
                mock_cam.objectList.assert_called_with(
                    "objlist:light",
                    mock_now,
                    mock_scope.return_value,
                    mock_select.return_value,
                )

            if export_value == consts.LIGHTEXPORT_PER_LIGHT_KEY:
                mock_write_light.assert_has_calls(
                    [
                        mocker.call(
                            mock_light1,
                            mock_channel,
                            data,
                            mock_wrangler,
                            mock_cam,
                            mock_now,
                        ),
                        mocker.call(
                            mock_light2,
                            mock_channel,
                            data,
                            mock_wrangler,
                            mock_cam,
                            mock_now,
                        ),
                    ]
                )

            elif export_value == consts.LIGHTEXPORT_SINGLE_KEY:
                mock_write_single.assert_called_with(
                    lights, data, mock_wrangler, mock_cam, mock_now
                )

            elif export_value == consts.LIGHTEXPORT_PER_CATEGORY_KEY:
                mock_write_per_category.assert_called_with(
                    lights, mock_channel, data, mock_wrangler, mock_cam, mock_now
                )

            elif export_value is None:
                mock_write_to_ifd.assert_called_with(
                    data, mock_wrangler, mock_cam, mock_now
                )

    @pytest.mark.parametrize(
        "variable, vextype, raises",
        [
            (None, None, pytest.raises(aov.MissingVariableError)),
            ("variable", None, pytest.raises(aov.MissingVexTypeError)),
            ("variable", "vextype", does_not_raise()),
        ],
    )
    def test__verify_internal_data(self, init_aov, mocker, variable, vextype, raises):
        """Test verifying internal data."""
        mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov.AOV.variable",
            new_callable=mocker.PropertyMock(return_value=variable),
        )
        mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov.AOV.vextype",
            new_callable=mocker.PropertyMock(return_value=vextype),
        )

        inst = init_aov()

        with raises:
            inst._verify_internal_data()

    # properties

    def test_channel(self, init_aov, mocker):
        """Test the 'channel' property."""
        mock_value = mocker.MagicMock(spec=str)

        inst = init_aov()
        inst._data = {consts.CHANNEL_KEY: mock_value}

        assert inst.channel == mock_value

        inst.channel = None

        assert inst._data[consts.CHANNEL_KEY] is None

    def test_comment(self, init_aov, mocker):
        """Test the 'comment' property."""
        mock_value = mocker.MagicMock(spec=str)

        inst = init_aov()
        inst._data = {consts.COMMENT_KEY: mock_value}

        assert inst.comment == mock_value

        inst.comment = None

        assert inst._data[consts.COMMENT_KEY] is None

    def test_componentexport(self, init_aov, mocker):
        """Test the 'componentexport' property."""
        mock_value1 = mocker.MagicMock(spec=bool)

        inst = init_aov()
        inst._data = {consts.COMPONENTEXPORT_KEY: mock_value1}

        assert inst.componentexport == mock_value1

        mock_value2 = mocker.MagicMock(spec=bool)
        inst.componentexport = mock_value2

        assert inst._data[consts.COMPONENTEXPORT_KEY] == mock_value2

    def test_components(self, init_aov, mocker):
        """Test the 'components' property."""
        mock_value1 = mocker.MagicMock(spec=list)

        inst = init_aov()
        inst._data = {consts.COMPONENTS_KEY: mock_value1}

        assert inst.components == mock_value1

        mock_value2 = mocker.MagicMock(spec=list)
        inst.components = mock_value2

        assert inst._data[consts.COMPONENTS_KEY] == mock_value2

    def test_exclude_from_dcm(self, init_aov, mocker):
        """Test the 'exclude_from_dcm' property."""
        mock_value1 = mocker.MagicMock(spec=bool)

        inst = init_aov()
        inst._data = {consts.EXCLUDE_DCM_KEY: mock_value1}

        assert inst.exclude_from_dcm == mock_value1

        mock_value2 = mocker.MagicMock(spec=bool)
        inst.exclude_from_dcm = mock_value2

        assert inst._data[consts.EXCLUDE_DCM_KEY] == mock_value2

    def test_intrinsics(self, init_aov, mocker):
        """Test the 'intrinsics' property."""
        mock_value1 = mocker.MagicMock(spec=list)

        inst = init_aov()
        inst._data = {consts.INTRINSICS_KEY: mock_value1}

        assert inst.intrinsics == mock_value1

        mock_value2 = mocker.MagicMock(spec=list)
        inst.intrinsics = mock_value2

        assert inst._data[consts.INTRINSICS_KEY] == mock_value2

    def test_lightexport(self, init_aov, mocker):
        """Test the 'lightexport' property."""
        mock_value1 = mocker.MagicMock(spec=str)

        inst = init_aov()
        inst._data = {consts.LIGHTEXPORT_KEY: mock_value1}

        assert inst.lightexport == mock_value1

        mock_value2 = mocker.MagicMock(spec=str)
        inst.lightexport = mock_value2

        assert inst._data[consts.LIGHTEXPORT_KEY] == mock_value2

    def test_lightexport_select(self, init_aov, mocker):
        """Test the 'lightexport_select' property."""
        mock_value1 = mocker.MagicMock(spec=str)

        inst = init_aov()
        inst._data = {consts.LIGHTEXPORT_SELECT_KEY: mock_value1}

        assert inst.lightexport_select == mock_value1

        mock_value2 = mocker.MagicMock(spec=str)
        inst.lightexport_select = mock_value2

        assert inst._data[consts.LIGHTEXPORT_SELECT_KEY] == mock_value2

    def test_lightexport_scope(self, init_aov, mocker):
        """Test the 'lightexport_scope' property."""
        mock_value1 = mocker.MagicMock(spec=str)

        inst = init_aov()
        inst._data = {consts.LIGHTEXPORT_SCOPE_KEY: mock_value1}

        assert inst.lightexport_scope == mock_value1

        mock_value2 = mocker.MagicMock(spec=str)
        inst.lightexport_scope = mock_value2

        assert inst._data[consts.LIGHTEXPORT_SCOPE_KEY] == mock_value2

    def test_path(self, init_aov, mocker):
        """Test the 'path' property."""
        mock_value1 = mocker.MagicMock(spec=str)

        inst = init_aov()
        inst._data = {consts.PATH_KEY: mock_value1}

        assert inst.path == mock_value1

        mock_value2 = mocker.MagicMock(spec=str)
        inst.path = mock_value2

        assert inst._data[consts.PATH_KEY] == mock_value2

    def test_pfilter(self, init_aov, mocker):
        """Test the 'pfilter' property."""
        mock_value1 = mocker.MagicMock(spec=str)

        inst = init_aov()
        inst._data = {consts.PFILTER_KEY: mock_value1}

        assert inst.pfilter == mock_value1

        mock_value2 = mocker.MagicMock(spec=str)
        inst.pfilter = mock_value2

        assert inst._data[consts.PFILTER_KEY] == mock_value2

    def test_planefile(self, init_aov, mocker):
        """Test the 'planefile' property."""
        mock_value1 = mocker.MagicMock(spec=str)

        inst = init_aov()
        inst._data = {consts.PLANEFILE_KEY: mock_value1}

        assert inst.planefile == mock_value1

        mock_value2 = mocker.MagicMock(spec=str)
        inst.planefile = mock_value2

        assert inst._data[consts.PLANEFILE_KEY] == mock_value2

    def test_priority(self, init_aov, mocker):
        """Test the 'priority' property."""
        mock_value1 = mocker.MagicMock(spec=int)

        inst = init_aov()
        inst._data = {consts.PRIORITY_KEY: mock_value1}

        assert inst.priority == mock_value1

        mock_value2 = mocker.MagicMock(spec=int)
        inst.priority = mock_value2

        assert inst._data[consts.PRIORITY_KEY] == mock_value2

    def test_quantize(self, init_aov, mocker):
        """Test the 'quantize' property."""
        mock_value1 = mocker.MagicMock(spec=str)

        inst = init_aov()
        inst._data = {consts.QUANTIZE_KEY: mock_value1}

        assert inst.quantize == mock_value1

        mock_value2 = mocker.MagicMock(spec=str)
        inst.quantize = mock_value2

        assert inst._data[consts.QUANTIZE_KEY] == mock_value2

    def test_sfilter(self, init_aov, mocker):
        """Test the 'sfilter' property."""
        mock_value1 = mocker.MagicMock(spec=str)

        inst = init_aov()
        inst._data = {consts.SFILTER_KEY: mock_value1}

        assert inst.sfilter == mock_value1

        mock_value2 = mocker.MagicMock(spec=str)
        inst.sfilter = mock_value2

        assert inst._data[consts.SFILTER_KEY] == mock_value2

    def test_variable(self, init_aov, mocker):
        """Test the 'variable' property."""
        mock_value1 = mocker.MagicMock(spec=str)

        inst = init_aov()
        inst._data = {consts.VARIABLE_KEY: mock_value1}

        assert inst.variable == mock_value1

        mock_value2 = mocker.MagicMock(spec=str)
        inst.variable = mock_value2

        assert inst._data[consts.VARIABLE_KEY] == mock_value2

    def test_vextype(self, init_aov, mocker):
        """Test the 'vextype' property."""
        mock_value1 = mocker.MagicMock(spec=str)

        inst = init_aov()
        inst._data = {consts.VEXTYPE_KEY: mock_value1}

        assert inst.vextype == mock_value1

        mock_value2 = mocker.MagicMock(spec=str)
        inst.vextype = mock_value2

        assert inst._data[consts.VEXTYPE_KEY] == mock_value2

    # as_data

    def test_as_data__defaults(self, init_aov, mocker):
        """Test converting to a data dictionary with mostly defaults."""
        mocker.patch.object(aov.AOV, "variable", new_callable=mocker.PropertyMock)
        mocker.patch.object(aov.AOV, "vextype", new_callable=mocker.PropertyMock)
        mocker.patch.object(
            aov.AOV, "channel", new_callable=mocker.PropertyMock(return_value=None)
        )
        mocker.patch.object(
            aov.AOV, "quantize", new_callable=mocker.PropertyMock(return_value=None)
        )
        mocker.patch.object(
            aov.AOV, "sfilter", new_callable=mocker.PropertyMock(return_value=None)
        )
        mocker.patch.object(
            aov.AOV, "pfilter", new_callable=mocker.PropertyMock(return_value=None)
        )
        mocker.patch.object(
            aov.AOV,
            "exclude_from_dcm",
            new_callable=mocker.PropertyMock(return_value=None),
        )
        mocker.patch.object(
            aov.AOV,
            "componentexport",
            new_callable=mocker.PropertyMock(return_value=None),
        )
        mocker.patch.object(
            aov.AOV, "lightexport", new_callable=mocker.PropertyMock(return_value=None)
        )
        mocker.patch.object(
            aov.AOV, "intrinsics", new_callable=mocker.PropertyMock(return_value=[])
        )
        mocker.patch.object(
            aov.AOV, "comment", new_callable=mocker.PropertyMock(return_value="")
        )
        mocker.patch.object(
            aov.AOV, "priority", new_callable=mocker.PropertyMock(return_value=-1)
        )

        inst = init_aov()

        result = inst.as_data()

        assert result == {
            consts.VARIABLE_KEY: inst.variable,
            consts.VEXTYPE_KEY: inst.vextype,
        }

    def test_as_data__values_per_category_no_components(self, init_aov, mocker):
        """Test converting to a data dictionary with per category exports and no components."""
        mocker.patch.object(aov.AOV, "variable", new_callable=mocker.PropertyMock)
        mocker.patch.object(aov.AOV, "vextype", new_callable=mocker.PropertyMock)
        mocker.patch.object(aov.AOV, "channel", new_callable=mocker.PropertyMock)
        mocker.patch.object(aov.AOV, "quantize", new_callable=mocker.PropertyMock)
        mocker.patch.object(aov.AOV, "sfilter", new_callable=mocker.PropertyMock)
        mocker.patch.object(aov.AOV, "pfilter", new_callable=mocker.PropertyMock)
        mocker.patch.object(
            aov.AOV, "exclude_from_dcm", new_callable=mocker.PropertyMock
        )
        mocker.patch.object(
            aov.AOV, "componentexport", new_callable=mocker.PropertyMock
        )
        mocker.patch.object(
            aov.AOV, "components", new_callable=mocker.PropertyMock(return_value=[])
        )
        mocker.patch.object(
            aov.AOV,
            "lightexport",
            new_callable=mocker.PropertyMock(
                return_value=consts.LIGHTEXPORT_PER_CATEGORY_KEY
            ),
        )
        mocker.patch.object(aov.AOV, "intrinsics", new_callable=mocker.PropertyMock)
        mocker.patch.object(aov.AOV, "comment", new_callable=mocker.PropertyMock)
        mocker.patch.object(aov.AOV, "priority", new_callable=mocker.PropertyMock)

        inst = init_aov()
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
            consts.PRIORITY_KEY: inst.priority,
        }
        assert result == expected

    def test_as_data__values_exports_components(self, init_aov, mocker):
        """Test converting to a data dictionary with exports and components."""
        mocker.patch.object(aov.AOV, "variable", new_callable=mocker.PropertyMock)
        mocker.patch.object(aov.AOV, "vextype", new_callable=mocker.PropertyMock)
        mocker.patch.object(aov.AOV, "channel", new_callable=mocker.PropertyMock)
        mocker.patch.object(aov.AOV, "quantize", new_callable=mocker.PropertyMock)
        mocker.patch.object(aov.AOV, "sfilter", new_callable=mocker.PropertyMock)
        mocker.patch.object(aov.AOV, "pfilter", new_callable=mocker.PropertyMock)
        mocker.patch.object(
            aov.AOV, "exclude_from_dcm", new_callable=mocker.PropertyMock
        )
        mocker.patch.object(
            aov.AOV,
            "componentexport",
            new_callable=mocker.PropertyMock(return_value=True),
        )
        mocker.patch.object(aov.AOV, "components", new_callable=mocker.PropertyMock)
        mocker.patch.object(aov.AOV, "lightexport", new_callable=mocker.PropertyMock)
        mocker.patch.object(
            aov.AOV, "lightexport_scope", new_callable=mocker.PropertyMock
        )
        mocker.patch.object(
            aov.AOV, "lightexport_select", new_callable=mocker.PropertyMock
        )
        mocker.patch.object(aov.AOV, "intrinsics", new_callable=mocker.PropertyMock)
        mocker.patch.object(aov.AOV, "comment", new_callable=mocker.PropertyMock)
        mocker.patch.object(aov.AOV, "priority", new_callable=mocker.PropertyMock)

        inst = init_aov()

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
            consts.PRIORITY_KEY: inst.priority,
        }

        assert result == expected

    # update_data

    def test_update_data__unknown(self, init_aov, mocker):
        """Test updating data with an unknown key that won't be added to the data."""
        mocker.patch("houdini_toolbox.sohohooks.aovs.aov.ALLOWABLE_VALUES", return_value={})
        mock_verify = mocker.patch("houdini_toolbox.sohohooks.aovs.aov.AOV._verify_internal_data")

        inst = init_aov()
        inst._data = {}

        data = {"key": None}

        inst.update_data(data)

        assert inst._data == {}

        mock_verify.assert_called()

    def test_update_data__settable(self, init_aov, mocker):
        """Test updating data with a known value that will be updated"""
        mocker.patch("houdini_toolbox.sohohooks.aovs.aov.ALLOWABLE_VALUES", return_value={})
        mock_verify = mocker.patch("houdini_toolbox.sohohooks.aovs.aov.AOV._verify_internal_data")

        inst = init_aov()
        inst._data = {"key": None}

        data = {"key": "value"}

        inst.update_data(data)

        assert inst._data == {"key": "value"}

        mock_verify.assert_called()

    def test_update_data__allowable_valid(self, init_aov, mocker):
        """Test updating data with a valid checked value."""
        mock_verify = mocker.patch("houdini_toolbox.sohohooks.aovs.aov.AOV._verify_internal_data")

        inst = init_aov()
        inst._data = {"key": None}

        data = {"key": "value1"}

        allowable = {"key": ("value1", "value2")}

        mocker.patch.dict(aov.ALLOWABLE_VALUES, allowable, clear=True)

        inst.update_data(data)

        assert inst._data == {"key": "value1"}

        mock_verify.assert_called()

    def test_update_data__allowable_invalid(self, init_aov, mocker):
        """Test updating data with an invalid checked value."""
        mocker.patch("houdini_toolbox.sohohooks.aovs.aov.AOV._verify_internal_data")

        inst = init_aov()
        inst._data = {"key": None}

        data = {"key": "value3"}

        allowable = {"key": ("value1", "value2")}

        mocker.patch.dict(aov.ALLOWABLE_VALUES, allowable, clear=True)

        with pytest.raises(aov.InvalidAOVValueError):
            inst.update_data(data)

    # write_to_ifd

    def test_write_to_ifd__no_channel_no_comp(self, init_aov, mocker, patch_soho):
        """Test writing to an ifd with no specific channel name or component export."""
        mock_as_data = mocker.patch.object(aov.AOV, "as_data")
        mocker.patch.object(
            aov.AOV, "channel", new_callable=mocker.PropertyMock(return_value=None)
        )
        mock_variable = mocker.patch.object(
            aov.AOV, "variable", new_callable=mocker.PropertyMock
        )
        mocker.patch.object(
            aov.AOV,
            "componentexport",
            new_callable=mocker.PropertyMock(return_value=False),
        )
        mock_export = mocker.patch.object(aov.AOV, "_light_export_planes")

        mock_as_data.return_value = {"key": "value"}

        inst = init_aov()

        mock_wrangler = mocker.MagicMock()
        mock_cam = mocker.MagicMock()
        mock_now = mocker.MagicMock(spec=float)

        inst.write_to_ifd(mock_wrangler, mock_cam, mock_now)

        mock_export.assert_called_with(
            {"key": "value", consts.CHANNEL_KEY: mock_variable.return_value},
            mock_wrangler,
            mock_cam,
            mock_now,
        )

    def test_write_to_ifd__channel_no_comp(self, init_aov, mocker, patch_soho):
        """Test writing to an ifd with a specific channel name and no component export."""
        mock_as_data = mocker.patch.object(aov.AOV, "as_data")
        mock_channel = mocker.patch.object(
            aov.AOV, "channel", new_callable=mocker.PropertyMock
        )
        mocker.patch.object(
            aov.AOV,
            "componentexport",
            new_callable=mocker.PropertyMock(return_value=False),
        )
        mock_export = mocker.patch.object(aov.AOV, "_light_export_planes")

        mock_as_data.return_value = {"key": "value"}

        inst = init_aov()

        mock_wrangler = mocker.MagicMock()
        mock_cam = mocker.MagicMock()
        mock_now = mocker.MagicMock(spec=float)

        inst.write_to_ifd(mock_wrangler, mock_cam, mock_now)

        mock_export.assert_called_with(
            {"key": "value", consts.CHANNEL_KEY: mock_channel.return_value},
            mock_wrangler,
            mock_cam,
            mock_now,
        )

    def test_write_to_ifd__export_no_comp(self, init_aov, mocker, patch_soho):
        """Test writing to an ifd with component export but no specific components and none on the node."""
        mock_as_data = mocker.patch.object(aov.AOV, "as_data")
        mocker.patch.object(aov.AOV, "channel", new_callable=mocker.PropertyMock)
        mocker.patch.object(
            aov.AOV,
            "componentexport",
            new_callable=mocker.PropertyMock(return_value=True),
        )
        mocker.patch.object(
            aov.AOV, "components", new_callable=mocker.PropertyMock(return_value=[])
        )
        mock_export = mocker.patch.object(aov.AOV, "_light_export_planes")

        mock_as_data.return_value = {"key": "value"}

        inst = init_aov()

        mock_wrangler = mocker.MagicMock()
        mock_cam = mocker.MagicMock()
        mock_now = mocker.MagicMock(spec=float)

        mock_parm = mocker.MagicMock()
        patch_soho.soho.SohoParm.return_value = mock_parm

        mock_cam.wrangle.return_value = {}

        inst.write_to_ifd(mock_wrangler, mock_cam, mock_now)

        patch_soho.soho.SohoParm.assert_called_with(
            "vm_exportcomponents", "str", [""], skipdefault=False
        )

        mock_export.assert_not_called()

    def test_write_to_ifd__export_components_from_node(
        self, init_aov, mocker, patch_soho
    ):
        """Test writing to an ifd with component export and getting the components from the node.."""
        mock_as_data = mocker.patch.object(aov.AOV, "as_data")
        mocker.patch.object(
            aov.AOV, "channel", new_callable=mocker.PropertyMock(return_value="Pworld")
        )
        mocker.patch.object(
            aov.AOV,
            "componentexport",
            new_callable=mocker.PropertyMock(return_value=True),
        )
        mocker.patch.object(
            aov.AOV, "components", new_callable=mocker.PropertyMock(return_value=[])
        )
        mock_export = mocker.patch.object(aov.AOV, "_light_export_planes")

        mock_as_data.return_value = {"key": "value"}

        inst = init_aov()

        mock_wrangler = mocker.MagicMock()
        mock_cam = mocker.MagicMock()
        mock_now = mocker.MagicMock(spec=float)

        mock_parm = mocker.MagicMock()
        patch_soho.soho.SohoParm.return_value = mock_parm

        mock_result = mocker.MagicMock()
        mock_result.Value = ["comp1 comp2"]

        mock_cam.wrangle.return_value = {"vm_exportcomponents": mock_result}

        inst.write_to_ifd(mock_wrangler, mock_cam, mock_now)

        patch_soho.soho.SohoParm.assert_called_with(
            "vm_exportcomponents", "str", [""], skipdefault=False
        )

        calls = [
            mocker.call(
                {
                    "key": "value",
                    consts.CHANNEL_KEY: "Pworld_comp1",
                    consts.COMPONENT_KEY: "comp1",
                },
                mock_wrangler,
                mock_cam,
                mock_now,
            ),
            mocker.call(
                {
                    "key": "value",
                    consts.CHANNEL_KEY: "Pworld_comp2",
                    consts.COMPONENT_KEY: "comp2",
                },
                mock_wrangler,
                mock_cam,
                mock_now,
            ),
        ]

        mock_export.assert_has_calls(calls)

    def test_write_to_ifd__export_components(self, init_aov, mocker, patch_soho):
        """Test writing to an ifd with component export and specific components."""
        mock_as_data = mocker.patch.object(aov.AOV, "as_data")
        mocker.patch.object(
            aov.AOV, "channel", new_callable=mocker.PropertyMock(return_value="Pworld")
        )
        mocker.patch.object(
            aov.AOV,
            "componentexport",
            new_callable=mocker.PropertyMock(return_value=True),
        )
        mocker.patch.object(
            aov.AOV,
            "components",
            new_callable=mocker.PropertyMock(return_value=["comp3", "comp4"]),
        )
        mock_export = mocker.patch.object(aov.AOV, "_light_export_planes")

        mock_as_data.return_value = {"key": "value"}

        inst = init_aov()

        mock_wrangler = mocker.MagicMock()
        mock_cam = mocker.MagicMock()
        mock_now = mocker.MagicMock(spec=float)

        inst.write_to_ifd(mock_wrangler, mock_cam, mock_now)

        calls = [
            mocker.call(
                {
                    "key": "value",
                    consts.CHANNEL_KEY: "Pworld_comp3",
                    consts.COMPONENT_KEY: "comp3",
                },
                mock_wrangler,
                mock_cam,
                mock_now,
            ),
            mocker.call(
                {
                    "key": "value",
                    consts.CHANNEL_KEY: "Pworld_comp4",
                    consts.COMPONENT_KEY: "comp4",
                },
                mock_wrangler,
                mock_cam,
                mock_now,
            ),
        ]

        mock_export.assert_has_calls(calls)


class Test_AOVGroup:
    """Test houdini_toolbox.sohohooks.aovs.AOVGroup object."""

    def test___init__(self, mocker):
        """Test object initialization."""
        mock_name = mocker.MagicMock(spec=str)

        group = aov.AOVGroup(mock_name)

        assert group._aovs == []
        assert group._comment == ""
        assert group._icon is None
        assert group._includes == []
        assert group._name == mock_name
        assert group._path is None
        assert group._priority == -1

    # __eq__

    def test___eq___equal(self, init_group, mocker):
        """Test equality check when two objects are equal."""
        mock_name = mocker.MagicMock(spec=str)

        mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov.AOVGroup.name",
            new_callable=mocker.PropertyMock(return_value=mock_name),
        )

        group1 = init_group()

        group2 = mocker.MagicMock(spec=aov.AOVGroup)
        type(group2).name = mock_name

        assert group1 == group2

        mock_name.__eq__.assert_called_with(group2.name)

    def test___eq___not_equal(self, init_group, mocker):
        """Test equality check when two objects are not equal."""
        mock_name = mocker.MagicMock(spec=str)

        mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov.AOVGroup.name",
            new_callable=mocker.PropertyMock(return_value=mock_name),
        )

        group1 = init_group()

        group2 = mocker.MagicMock(spec=aov.AOVGroup)
        type(group2).name = mocker.PropertyMock(spec=str)

        assert group1 != group2

        mock_name.__eq__.assert_called_with(group2.name)

    def test___eq___non_group(self, init_group, mocker):
        """Test equality check when the other object is a different type."""
        mocker.patch("houdini_toolbox.sohohooks.aovs.aov.AOVGroup.name")

        group1 = init_group()

        group2 = mocker.MagicMock()

        assert group1.__eq__(group2) == NotImplemented

    # ge

    def test___ge___less_than(self, init_group, mocker):
        """Test >= when the object is < the other object."""
        mock_name = mocker.MagicMock(spec=str)
        mock_name.__ge__.return_value = False

        mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov.AOVGroup.name",
            new_callable=mocker.PropertyMock(return_value=mock_name),
        )

        group1 = init_group()

        group2 = mocker.MagicMock(spec=aov.AOVGroup)

        assert not group1 >= group2

        mock_name.__ge__.assert_called_with(group2.name)

    def test___ge___(self, init_group, mocker):
        """Test >= when the object is >= the other object."""
        mock_name = mocker.MagicMock(spec=str)
        mock_name.__ge__.return_value = True

        mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov.AOVGroup.name",
            new_callable=mocker.PropertyMock(return_value=mock_name),
        )

        group1 = init_group()

        group2 = mocker.MagicMock(spec=aov.AOVGroup)

        assert group1 >= group2

        mock_name.__ge__.assert_called_with(group2.name)

    def test___ge___non_group(self, init_group, mocker):
        """Test >= when the object is a different type."""
        group1 = init_group()
        group2 = mocker.MagicMock()

        assert group1.__ge__(group2) == NotImplemented

    # gt

    def test___gt___less_than(self, init_group, mocker):
        """Test > when the object is < the other object."""
        mock_name = mocker.MagicMock(spec=str)
        mock_name.__gt__.return_value = False

        mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov.AOVGroup.name",
            new_callable=mocker.PropertyMock(return_value=mock_name),
        )

        group1 = init_group()

        group2 = mocker.MagicMock(spec=aov.AOVGroup)

        assert not group1 > group2

        mock_name.__gt__.assert_called_with(group2.name)

    def test___gt__(self, init_group, mocker):
        """Test > when the object is > the other object."""
        mock_name = mocker.MagicMock(spec=str)
        mock_name.__gt__.return_value = True

        mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov.AOVGroup.name",
            new_callable=mocker.PropertyMock(return_value=mock_name),
        )

        group1 = init_group()

        group2 = mocker.MagicMock(spec=aov.AOVGroup)

        assert group1 > group2

        mock_name.__gt__.assert_called_with(group2.name)

    def test___gt___non_group(self, init_group, mocker):
        """Test > when the object is a different type."""
        group1 = init_group()
        group2 = mocker.MagicMock()

        assert group1.__gt__(group2) == NotImplemented

    # __hash__

    def test___hash__(self, init_group, mocker):
        """Test hashing the object."""
        mock_name = mocker.MagicMock(spec=str)
        mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov.AOVGroup.name",
            new_callable=mocker.PropertyMock(return_value=mock_name),
        )

        group1 = init_group()

        result = group1.__hash__()

        assert result == hash(mock_name)

        assert hash(group1) == hash(mock_name)

    # le

    def test___le__(self, init_group, mocker):
        """Test <= when the object is < the other object."""
        mock_name = mocker.MagicMock(spec=str)
        mock_name.__le__.return_value = True

        mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov.AOVGroup.name",
            new_callable=mocker.PropertyMock(return_value=mock_name),
        )

        group1 = init_group()

        group2 = mocker.MagicMock(spec=aov.AOVGroup)

        assert group1 <= group2

        mock_name.__le__.assert_called_with(group2.name)

    def test___le___greater_than(self, init_group, mocker):
        """Test <= when the object is > the other object."""
        mock_name = mocker.MagicMock(spec=str)
        mock_name.__le__.return_value = False

        mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov.AOVGroup.name",
            new_callable=mocker.PropertyMock(return_value=mock_name),
        )

        group1 = init_group()

        group2 = mocker.MagicMock(spec=aov.AOVGroup)

        assert not group1 <= group2

        mock_name.__le__.assert_called_with(group2.name)

    def test___le___non_group(self, init_group, mocker):
        """Test <= when the object is a different type."""
        group1 = init_group()
        group2 = mocker.MagicMock()

        assert group1.__le__(group2) == NotImplemented

    # lt

    def test___lt__(self, init_group, mocker):
        """Test < when the object is < the other object."""
        mock_name = mocker.MagicMock(spec=str)
        mock_name.__lt__.return_value = True

        mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov.AOVGroup.name",
            new_callable=mocker.PropertyMock(return_value=mock_name),
        )

        group1 = init_group()

        group2 = mocker.MagicMock(spec=aov.AOVGroup)

        assert group1 < group2

        mock_name.__lt__.assert_called_with(group2.name)

    def test___lt___greater_than(self, init_group, mocker):
        """Test <= when the object is >= the other object."""
        mock_name = mocker.MagicMock(spec=str)
        mock_name.__lt__.return_value = False

        mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov.AOVGroup.name",
            new_callable=mocker.PropertyMock(return_value=mock_name),
        )

        group1 = init_group()

        group2 = mocker.MagicMock(spec=aov.AOVGroup)

        assert not group1 < group2

        mock_name.__lt__.assert_called_with(group2.name)

    def test___lt___non_group(self, init_group, mocker):
        """Test < when the object is a different type."""
        group1 = init_group()
        group2 = mocker.MagicMock()

        assert group1.__lt__(group2) == NotImplemented

    # __ne__

    def test___ne__(self, init_group, mocker):
        """Test if the object is !=."""
        mock_eq = mocker.patch.object(aov.AOVGroup, "__eq__")

        group1 = init_group()
        group2 = mocker.MagicMock(spec=aov.AOVGroup)

        result = group1.__ne__(group2)

        assert result != mock_eq.return_value
        mock_eq.assert_called_with(group2)

    # Properties

    def test_aovs(self, init_group, mocker):
        """Test the 'aovs' property."""
        mock_aov = mocker.MagicMock(spec=aov.AOV)

        group = init_group()
        group._aovs = [mock_aov]

        assert group.aovs == [mock_aov]

    def test_comment(self, init_group, mocker):
        """Test the 'comment' property."""
        mock_value1 = mocker.MagicMock(spec=str)

        group = init_group()

        group._comment = mock_value1
        assert group.comment == mock_value1

        mock_value2 = mocker.MagicMock(spec=str)
        group.comment = mock_value2
        assert group._comment == mock_value2

    def test_icon(self, init_group, mocker):
        """Test the 'icon' property."""
        mock_value1 = mocker.MagicMock(spec=str)

        group = init_group()

        group._icon = mock_value1
        assert group.icon == mock_value1

        mock_value2 = mocker.MagicMock(spec=str)
        group.icon = mock_value2
        assert group._icon == mock_value2

    def test_includes(self, init_group, mocker):
        """Test the 'includes' property."""
        mock_value1 = mocker.MagicMock(spec=list)

        group = init_group()

        group._includes = mock_value1
        assert group.includes == mock_value1

    def test_name(self, init_group, mocker):
        """Test the 'name' property."""
        mock_value = mocker.MagicMock(spec=str)

        group = init_group()

        group._name = mock_value
        assert group.name == mock_value

    def test_path(self, init_group, mocker):
        """Test the 'path' property."""
        mock_value1 = mocker.MagicMock(spec=str)

        group = init_group()

        group._path = mock_value1
        assert group.path == mock_value1

        mock_value2 = mocker.MagicMock(spec=str)
        group.path = mock_value2
        assert group._path == mock_value2

    def test_priority(self, init_group, mocker):
        """Test the 'priority' property."""
        mock_value1 = mocker.MagicMock(spec=int)

        group = init_group()

        group._priority = mock_value1
        assert group.priority == mock_value1

        mock_value2 = mocker.MagicMock(spec=int)
        group.priority = mock_value2
        assert group._priority == mock_value2

    def test_clear(self, init_group, mocker):
        """Test clearing the aov list."""
        mock_aov = mocker.MagicMock(spec=aov.AOV)

        group = init_group()
        group._aovs = [mock_aov]

        group.clear()

        assert group._aovs == []

    # as_data

    def test_as_data__no_comment_or_priority(self, init_group, mocker):
        """Test 'as_data' with no comment or priority."""
        mock_includes = mocker.patch.object(
            aov.AOVGroup, "includes", new_callable=mocker.PropertyMock
        )
        mock_name = mocker.patch.object(
            aov.AOVGroup, "name", new_callable=mocker.PropertyMock
        )
        mock_aovs = mocker.patch.object(
            aov.AOVGroup, "aovs", new_callable=mocker.PropertyMock
        )
        mocker.patch.object(
            aov.AOVGroup, "comment", new_callable=mocker.PropertyMock(return_value="")
        )
        mocker.patch.object(
            aov.AOVGroup, "priority", new_callable=mocker.PropertyMock(return_value=-1)
        )

        mock_var_name1 = mocker.MagicMock(spec=str)
        mock_var_name2 = mocker.MagicMock(spec=str)

        mock_includes.return_value = [mock_var_name1, mock_var_name2]

        mock_aov1 = mocker.MagicMock(spec=aov.AOV)
        mock_aov2 = mocker.MagicMock(spec=aov.AOV)

        mock_aovs.return_value = [mock_aov1, mock_aov2]

        expected = {
            mock_name.return_value: {
                consts.GROUP_INCLUDE_KEY: [
                    mock_var_name1,
                    mock_var_name2,
                    mock_aov1.variable,
                    mock_aov2.variable,
                ]
            }
        }

        group = init_group()

        result = group.as_data()

        assert result == expected

    def test_as_data(self, init_group, mocker):
        """Test 'as_data' with a comment and priority."""
        mock_includes = mocker.patch.object(
            aov.AOVGroup, "includes", new_callable=mocker.PropertyMock
        )
        mock_name = mocker.patch.object(
            aov.AOVGroup, "name", new_callable=mocker.PropertyMock
        )
        mock_aovs = mocker.patch.object(
            aov.AOVGroup, "aovs", new_callable=mocker.PropertyMock
        )
        mock_comment = mocker.patch.object(
            aov.AOVGroup, "comment", new_callable=mocker.PropertyMock
        )
        mock_priority = mocker.patch.object(
            aov.AOVGroup, "priority", new_callable=mocker.PropertyMock
        )

        mock_var_name1 = mocker.MagicMock(spec=str)
        mock_var_name2 = mocker.MagicMock(spec=str)

        mock_includes.return_value = [mock_var_name1, mock_var_name2]

        mock_aov1 = mocker.MagicMock(spec=aov.AOV)
        mock_aov2 = mocker.MagicMock(spec=aov.AOV)
        mock_aovs.return_value = [mock_aov1, mock_aov2]

        expected = {
            mock_name.return_value: {
                consts.GROUP_INCLUDE_KEY: [
                    mock_var_name1,
                    mock_var_name2,
                    mock_aov1.variable,
                    mock_aov2.variable,
                ],
                consts.PRIORITY_KEY: mock_priority.return_value,
                consts.COMMENT_KEY: mock_comment.return_value,
            }
        }

        group = init_group()

        result = group.as_data()

        assert result == expected

    def test_write_to_ifd(self, init_group, mocker):
        """Test "write_to_ifd"."""
        mock_aovs = mocker.patch.object(
            aov.AOVGroup, "aovs", new_callable=mocker.PropertyMock
        )

        mock_aov1 = mocker.MagicMock(spec=aov.AOV)
        mock_aov2 = mocker.MagicMock(spec=aov.AOV)

        mock_wrangler = mocker.MagicMock()
        mock_cam = mocker.MagicMock()
        mock_now = mocker.MagicMock(spec=float)

        mock_aovs.return_value = [mock_aov1, mock_aov2]

        group = init_group()

        group.write_to_ifd(mock_wrangler, mock_cam, mock_now)

        mock_aov1.write_to_ifd.assert_called_with(mock_wrangler, mock_cam, mock_now)
        mock_aov2.write_to_ifd.assert_called_with(mock_wrangler, mock_cam, mock_now)


class Test_IntrinsicAOVGroup:
    """Test the houdini_toolbox.sohohooks.aovs.IntrinsicAOVGroup object."""

    def test___init__(self, mocker):
        """Test object initialization."""
        mock_super_init = mocker.patch("houdini_toolbox.sohohooks.aovs.aov.AOVGroup.__init__")

        mock_name = mocker.MagicMock(spec=str)

        result = aov.IntrinsicAOVGroup(mock_name)

        mock_super_init.assert_called_with(mock_name)
        assert result._comment == "Automatically generated"


class Test__build_category_map:
    """Test houdini_toolbox.sohohooks.aovs._build_category_map."""

    def test_no_parm(self, mocker):
        """Test when the light doesn't have a "categories" parameter."""
        mock_light1 = mocker.MagicMock()

        lights = (mock_light1,)

        mock_now = mocker.MagicMock(spec=float)

        result = aov._build_category_map(lights, mock_now)

        assert result == {}

        mock_light1.evalString.assert_called_with("categories", mock_now, [])

    def test_no_categories(self, mocker):
        """Test when the "categories" parameter is empty."""
        mock_light1 = mocker.MagicMock()

        mock_light1.evalString.side_effect = lambda name, t, value: value.append("")

        lights = (mock_light1,)

        mock_now = mocker.MagicMock(spec=float)

        result = aov._build_category_map(lights, mock_now)

        assert result == {None: [mock_light1]}

    def test_categories(self, mocker):
        """Test when the "categories" parameter is set."""
        mock_light1 = mocker.MagicMock()
        mock_light1.evalString.side_effect = lambda name, t, value: value.append(
            "cat1 cat2"
        )

        mock_light2 = mocker.MagicMock()
        mock_light2.evalString.side_effect = lambda name, t, value: value.append(
            "cat2,cat3"
        )

        lights = (mock_light1, mock_light2)

        mock_now = mocker.MagicMock(spec=float)

        result = aov._build_category_map(lights, mock_now)

        assert result == {
            "cat1": [mock_light1],
            "cat2": [mock_light1, mock_light2],
            "cat3": [mock_light2],
        }


def test__call_post_defplane(mocker, patch_soho):
    """Test houdini_toolbox.sohohooks.aovs._call_post_defplane."""
    mock_variable = mocker.MagicMock(spec=str)
    mock_vextype = mocker.MagicMock(spec=str)
    mock_planefile = mocker.MagicMock(spec=str)
    mock_lightexport = mocker.MagicMock(spec=str)

    data = {
        consts.VARIABLE_KEY: mock_variable,
        consts.VEXTYPE_KEY: mock_vextype,
        consts.PLANEFILE_KEY: mock_planefile,
        consts.LIGHTEXPORT_KEY: mock_lightexport,
    }

    mock_wrangler = mocker.MagicMock()
    mock_cam = mocker.MagicMock()
    mock_now = mocker.MagicMock(spec=float)

    aov._call_post_defplane(data, mock_wrangler, mock_cam, mock_now)

    patch_soho.IFDhooks.call.assert_called_with(
        "post_defplane",
        mock_variable,
        mock_vextype,
        -1,
        mock_wrangler,
        mock_cam,
        mock_now,
        mock_planefile,
        mock_lightexport,
    )


def test__call_pre_defplane(mocker, patch_soho):
    """Test houdini_toolbox.sohohooks.aovs._call_pre_defplane."""
    mock_variable = mocker.MagicMock(spec=str)
    mock_vextype = mocker.MagicMock(spec=str)
    mock_planefile = mocker.MagicMock(spec=str)
    mock_lightexport = mocker.MagicMock(spec=str)

    data = {
        consts.VARIABLE_KEY: mock_variable,
        consts.VEXTYPE_KEY: mock_vextype,
        consts.PLANEFILE_KEY: mock_planefile,
        consts.LIGHTEXPORT_KEY: mock_lightexport,
    }

    mock_wrangler = mocker.MagicMock()
    mock_cam = mocker.MagicMock()
    mock_now = mocker.MagicMock(spec=float)

    aov._call_pre_defplane(data, mock_wrangler, mock_cam, mock_now)

    patch_soho.IFDhooks.call.assert_called_with(
        "pre_defplane",
        mock_variable,
        mock_vextype,
        -1,
        mock_wrangler,
        mock_cam,
        mock_now,
        mock_planefile,
        mock_lightexport,
    )


class Test__write_data_to_ifd:
    """Test houdini_toolbox.sohohooks.aovs._write_data_to_ifd."""

    def test_pre_defplane(self, mocker, patch_soho):
        """Test when the "pre_defplane" hook return True."""
        mock_pre = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov._call_pre_defplane", return_value=True
        )

        data = {}
        mock_wrangler = mocker.MagicMock()
        mock_cam = mocker.MagicMock()
        mock_now = mocker.MagicMock(spec=float)

        aov._write_data_to_ifd(data, mock_wrangler, mock_cam, mock_now)

        mock_pre.assert_called_with(data, mock_wrangler, mock_cam, mock_now)

        patch_soho.IFDapi.ray_start.assert_not_called()

    def test_base_data(self, mocker, patch_soho):
        """Test with only the minimum keys to write."""
        mock_pre = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov._call_pre_defplane", return_value=False
        )
        mock_post = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov._call_post_defplane", return_value=False
        )

        mock_pre.return_value = False
        mock_post.return_value = False

        mock_variable = mocker.MagicMock(spec=str)
        mock_vextype = mocker.MagicMock(spec=str)
        mock_channel = mocker.MagicMock(spec=str)

        data = {
            consts.VARIABLE_KEY: mock_variable,
            consts.VEXTYPE_KEY: mock_vextype,
            consts.CHANNEL_KEY: mock_channel,
        }

        mock_wrangler = mocker.MagicMock()
        mock_cam = mocker.MagicMock()
        mock_now = mocker.MagicMock(spec=float)

        aov._write_data_to_ifd(data, mock_wrangler, mock_cam, mock_now)

        calls = [
            mocker.call("plane", "variable", [mock_variable]),
            mocker.call("plane", "vextype", [mock_vextype]),
            mocker.call("plane", "channel", [mock_channel]),
        ]

        patch_soho.IFDapi.ray_property.assert_has_calls(calls)

        mock_pre.assert_called_with(data, mock_wrangler, mock_cam, mock_now)
        mock_post.assert_called_with(data, mock_wrangler, mock_cam, mock_now)

    def test_full_data(self, mocker, patch_soho):
        """Test with all the keys to write."""
        mock_pre = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov._call_pre_defplane", return_value=False
        )
        mock_post = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov._call_post_defplane", return_value=False
        )

        mock_variable = mocker.MagicMock(spec=str)
        mock_vextype = mocker.MagicMock(spec=str)
        mock_channel = mocker.MagicMock(spec=str)
        mock_quantize = mocker.MagicMock(spec=str)
        mock_planefile = mocker.MagicMock(spec=str)
        mock_lightexport = mocker.MagicMock(spec=str)
        mock_pfilter = mocker.MagicMock(spec=str)
        mock_sfilter = mocker.MagicMock(spec=str)
        mock_component = mocker.MagicMock(spec=str)
        mock_exclude_from_dcm = mocker.MagicMock(spec=str)

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
            consts.EXCLUDE_DCM_KEY: mock_exclude_from_dcm,
        }
        mock_wrangler = mocker.MagicMock()
        mock_cam = mocker.MagicMock()
        mock_now = mocker.MagicMock(spec=float)

        aov._write_data_to_ifd(data, mock_wrangler, mock_cam, mock_now)

        calls = [
            mocker.call("plane", "variable", [mock_variable]),
            mocker.call("plane", "vextype", [mock_vextype]),
            mocker.call("plane", "channel", [mock_channel]),
            mocker.call("plane", "quantize", [mock_quantize]),
            mocker.call("plane", "planefile", [mock_planefile]),
            mocker.call("plane", "lightexport", [mock_lightexport]),
            mocker.call("plane", "pfilter", [mock_pfilter]),
            mocker.call("plane", "sfilter", [mock_sfilter]),
            mocker.call("plane", "component", [mock_component]),
            mocker.call("plane", "excludedcm", [True]),
        ]

        patch_soho.IFDapi.ray_property.assert_has_calls(calls)

        mock_pre.assert_called_with(data, mock_wrangler, mock_cam, mock_now)
        mock_post.assert_called_with(data, mock_wrangler, mock_cam, mock_now)

    def test_none_planefile(self, mocker, patch_soho):
        """Test when the plane_file is None."""
        mock_pre = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov._call_pre_defplane", return_value=False
        )
        mock_post = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov._call_post_defplane", return_value=False
        )

        mock_variable = mocker.MagicMock(spec=str)
        mock_vextype = mocker.MagicMock(spec=str)
        mock_channel = mocker.MagicMock(spec=str)

        data = {
            consts.VARIABLE_KEY: mock_variable,
            consts.VEXTYPE_KEY: mock_vextype,
            consts.CHANNEL_KEY: mock_channel,
            consts.PLANEFILE_KEY: None,
        }

        mock_wrangler = mocker.MagicMock()
        mock_cam = mocker.MagicMock()
        mock_now = mocker.MagicMock(spec=float)

        aov._write_data_to_ifd(data, mock_wrangler, mock_cam, mock_now)

        calls = [
            mocker.call("plane", "variable", [mock_variable]),
            mocker.call("plane", "vextype", [mock_vextype]),
            mocker.call("plane", "channel", [mock_channel]),
        ]

        patch_soho.IFDapi.ray_property.assert_has_calls(calls)

        mock_pre.assert_called_with(data, mock_wrangler, mock_cam, mock_now)
        mock_post.assert_called_with(data, mock_wrangler, mock_cam, mock_now)

    def test_post_defplane(self, mocker, patch_soho):
        """Test when the "post_defplane" hook returns True."""
        mock_pre = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov._call_pre_defplane", return_value=False
        )
        mock_post = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.aov._call_post_defplane", return_value=True
        )

        mock_variable = mocker.MagicMock(spec=str)
        mock_vextype = mocker.MagicMock(spec=str)
        mock_channel = mocker.MagicMock(spec=str)

        data = {
            consts.VARIABLE_KEY: mock_variable,
            consts.VEXTYPE_KEY: mock_vextype,
            consts.CHANNEL_KEY: mock_channel,
        }

        mock_wrangler = mocker.MagicMock()
        mock_cam = mocker.MagicMock()
        mock_now = mocker.MagicMock(spec=float)

        aov._write_data_to_ifd(data, mock_wrangler, mock_cam, mock_now)

        calls = [
            mocker.call("plane", "variable", [mock_variable]),
            mocker.call("plane", "vextype", [mock_vextype]),
            mocker.call("plane", "channel", [mock_channel]),
        ]

        patch_soho.IFDapi.ray_property.assert_has_calls(calls)

        mock_pre.assert_called_with(data, mock_wrangler, mock_cam, mock_now)
        mock_post.assert_called_with(data, mock_wrangler, mock_cam, mock_now)

        patch_soho.IFDapi.ray_end.assert_not_called()


class Test__write_light:
    """Test houdini_toolbox.sohohooks.aovs._write_light."""

    def test_suffix_prefix(self, mocker, patch_soho):
        """Test when adding a suffix and prefix."""
        mock_write = mocker.patch("houdini_toolbox.sohohooks.aovs.aov._write_data_to_ifd")

        mock_light = mocker.MagicMock()

        mock_prefix = mocker.MagicMock(spec=str)
        mock_suffix = mocker.MagicMock(spec=str)

        mock_light.getDefaultedString.return_value = [mock_suffix]

        def eval_string(name, now, prefix):  # pylint: disable=unused-argument
            """Fake string evaluation that appends a value."""
            prefix.append(mock_prefix)
            return True

        mock_light.evalString.side_effect = eval_string

        data = {}
        mock_base = mocker.MagicMock(spec=str)
        mock_wrangler = mocker.MagicMock()
        mock_cam = mocker.MagicMock()
        mock_now = mocker.MagicMock(spec=float)

        aov._write_light(mock_light, mock_base, data, mock_wrangler, mock_cam, mock_now)

        mock_write.assert_called_with(
            {
                consts.LIGHTEXPORT_KEY: mock_light.getName.return_value,
                consts.CHANNEL_KEY: f"{mock_prefix}_{mock_base}{mock_suffix}",
            },
            mock_wrangler,
            mock_cam,
            mock_now,
        )

    def test_no_suffix_path_prefix(self, mocker, patch_soho):
        """Test with no suffix and a path type prefix."""
        mock_write = mocker.patch("houdini_toolbox.sohohooks.aovs.aov._write_data_to_ifd")

        mock_name = mocker.MagicMock(spec=str)
        mock_light = mocker.MagicMock()
        mock_light.getName.return_value = mock_name

        mock_light.getDefaultedString.side_effect = lambda name, now, default: default

        mock_light.evalString.return_value = False

        data = {}
        mock_base = mocker.MagicMock(spec=str)
        mock_wrangler = mocker.MagicMock()
        mock_cam = mocker.MagicMock()
        mock_now = mocker.MagicMock(spec=float)

        aov._write_light(mock_light, mock_base, data, mock_wrangler, mock_cam, mock_now)

        mock_write.assert_called_with(
            {
                consts.LIGHTEXPORT_KEY: mock_light.getName.return_value,
                consts.CHANNEL_KEY: f"{mock_name.__getitem__.return_value.replace.return_value}_{mock_base}",
            },
            mock_wrangler,
            mock_cam,
            mock_now,
        )

        mock_name.__getitem__.assert_called_with(slice(1, None, None))
        mock_name.__getitem__.return_value.replace.assert_called_with("/", "_")

    def test_suffix_no_prefix(self, mocker, patch_soho):
        """Test with no prefix and a suffix."""
        mock_write = mocker.patch("houdini_toolbox.sohohooks.aovs.aov._write_data_to_ifd")

        mock_name = mocker.MagicMock(spec=str)

        mock_light = mocker.MagicMock()
        mock_light.getName.return_value = mock_name

        mock_default_suffix = mocker.MagicMock(spec=str)

        mock_light.getDefaultedString.return_value = mock_default_suffix

        mock_light.evalString.return_value = True

        data = {}
        mock_base = mocker.MagicMock(spec=str)
        mock_wrangler = mocker.MagicMock()
        mock_cam = mocker.MagicMock()
        mock_now = mocker.MagicMock(spec=float)

        aov._write_light(mock_light, mock_base, data, mock_wrangler, mock_cam, mock_now)

        mock_write.assert_called_with(
            {
                consts.LIGHTEXPORT_KEY: mock_name,
                consts.CHANNEL_KEY: f"{mock_base}{mock_default_suffix.__getitem__.return_value}",
            },
            mock_wrangler,
            mock_cam,
            mock_now,
        )

        mock_default_suffix.__getitem__.assert_called_with(0)

    def test_empty_suffix(self, mocker, patch_soho):
        """Test with no prefix and an empty suffix."""
        mock_write = mocker.patch("houdini_toolbox.sohohooks.aovs.aov._write_data_to_ifd")

        mock_name = mocker.MagicMock(spec=str)

        mock_light = mocker.MagicMock()
        mock_light.getName.return_value = mock_name

        mock_light.getDefaultedString.return_value = [""]

        mock_light.evalString.return_value = True

        data = {}
        mock_base = mocker.MagicMock(spec=str)
        mock_wrangler = mocker.MagicMock()
        mock_cam = mocker.MagicMock()
        mock_now = mocker.MagicMock(spec=float)

        aov._write_light(mock_light, mock_base, data, mock_wrangler, mock_cam, mock_now)

        patch_soho.soho.error.assert_called()

        mock_write.assert_called_with(
            {consts.LIGHTEXPORT_KEY: mock_name, consts.CHANNEL_KEY: mock_base},
            mock_wrangler,
            mock_cam,
            mock_now,
        )


class Test__write_per_category:
    """Test houdini_toolbox.sohohooks.aovs._write_per_category."""

    def test_no_category(self, mocker):
        """Test when the category is 'None'."""
        mock_build = mocker.patch("houdini_toolbox.sohohooks.aovs.aov._build_category_map")
        mock_write = mocker.patch("houdini_toolbox.sohohooks.aovs.aov._write_data_to_ifd")

        mock_light1 = mocker.MagicMock()
        mock_light1.getName.return_value = "light1"

        mock_light2 = mocker.MagicMock()
        mock_light2.getName.return_value = "light2"

        lights = (mock_light1, mock_light2)

        category_lights = lights

        mock_build.return_value = {None: category_lights}

        data = {}
        base_channel = "base"
        mock_wrangler = mocker.MagicMock()
        mock_cam = mocker.MagicMock()
        mock_now = mocker.MagicMock(spec=float)

        aov._write_per_category(
            lights, base_channel, data, mock_wrangler, mock_cam, mock_now
        )

        mock_write.assert_called_with(
            {consts.LIGHTEXPORT_KEY: "light1 light2", consts.CHANNEL_KEY: base_channel},
            mock_wrangler,
            mock_cam,
            mock_now,
        )

    def test_category(self, mocker):
        """Test with a non-None category."""
        mock_build = mocker.patch("houdini_toolbox.sohohooks.aovs.aov._build_category_map")
        mock_write = mocker.patch("houdini_toolbox.sohohooks.aovs.aov._write_data_to_ifd")

        mock_light1 = mocker.MagicMock()
        mock_light1.getName.return_value = "light1"

        mock_light2 = mocker.MagicMock()
        mock_light2.getName.return_value = "light2"

        lights = (mock_light1, mock_light2)

        category_lights = lights

        category = "test"

        mock_build.return_value = {category: category_lights}

        data = {}
        base_channel = "base"
        mock_wrangler = mocker.MagicMock()
        mock_cam = mocker.MagicMock()
        mock_now = mocker.MagicMock(spec=float)

        aov._write_per_category(
            lights, base_channel, data, mock_wrangler, mock_cam, mock_now
        )

        mock_write.assert_called_with(
            {
                consts.LIGHTEXPORT_KEY: "light1 light2",
                consts.CHANNEL_KEY: f"{category}_{base_channel}",
            },
            mock_wrangler,
            mock_cam,
            mock_now,
        )


class Test__write_single_channel:
    """Test houdini_toolbox.sohohooks.aovs._write_single_channel."""

    def test_lights(self, mocker):
        """Test writing multiple lights."""
        mock_write = mocker.patch("houdini_toolbox.sohohooks.aovs.aov._write_data_to_ifd")

        mock_light1 = mocker.MagicMock()
        mock_light1.getName.return_value = "light1"

        mock_light2 = mocker.MagicMock()
        mock_light2.getName.return_value = "light2"

        lights = (mock_light1, mock_light2)

        data = {}
        mock_wrangler = mocker.MagicMock()
        mock_cam = mocker.MagicMock()
        mock_now = mocker.MagicMock(spec=float)

        aov._write_single_channel(lights, data, mock_wrangler, mock_cam, mock_now)

        mock_write.assert_called_with(
            {consts.LIGHTEXPORT_KEY: "light1 light2"}, mock_wrangler, mock_cam, mock_now
        )

    def test_no_lights(self, mocker):
        """Test writing no lights."""
        mock_write = mocker.patch("houdini_toolbox.sohohooks.aovs.aov._write_data_to_ifd")

        lights = ()

        data = {}
        mock_wrangler = mocker.MagicMock()
        mock_cam = mocker.MagicMock()
        mock_now = mocker.MagicMock(spec=float)

        aov._write_single_channel(lights, data, mock_wrangler, mock_cam, mock_now)

        mock_write.assert_called_with(
            {consts.LIGHTEXPORT_KEY: "__nolights__"}, mock_wrangler, mock_cam, mock_now
        )
