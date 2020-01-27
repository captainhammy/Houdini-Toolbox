"""Test the ht.pyfilter.operations.setproperties module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import argparse

# Third Party Library Imports
import pytest

# Houdini Toolbox Imports
from ht.pyfilter.manager import PyFilterManager
from ht.pyfilter.operations import setproperties


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def init_manager(mocker):
    """Fixture to initialize the manager class."""
    mocker.patch.object(
        setproperties.PropertySetterManager, "__init__", lambda x, y: None
    )

    def _create():
        return setproperties.PropertySetterManager(None)

    return _create


@pytest.fixture
def init_masked_setter(mocker):
    """Fixture to initialize the setter class."""
    mocker.patch.object(
        setproperties.MaskedPropertySetter, "__init__", lambda x, y, z, w: None
    )

    def _create():
        return setproperties.MaskedPropertySetter(None, None, None)

    return _create


@pytest.fixture
def init_operation(mocker):
    """Fixture to initialize an operation."""
    mocker.patch.object(setproperties.SetProperties, "__init__", lambda x, y: None)

    def _create():
        return setproperties.SetProperties(None)

    return _create


@pytest.fixture
def init_setter(mocker):
    """Fixture to initialize the masked setter class."""
    mocker.patch.object(setproperties.PropertySetter, "__init__", lambda x, y: None)

    def _create():
        return setproperties.PropertySetter(None)

    return _create


@pytest.fixture
def properties(mocker):
    """Fixture to handle mocking (get|set)_property calls."""

    _mock_get = mocker.patch("ht.pyfilter.operations.setproperties.get_property")
    _mock_set = mocker.patch("ht.pyfilter.operations.setproperties.set_property")

    class Properties(object):
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
# CLASSES
# =============================================================================


class Test_PropertySetterManager(object):
    """Test the ht.pyfilter.operations.setproperties.PropertySetterManager class."""

    def test___init__(self):
        """Test object initialization."""
        op = setproperties.PropertySetterManager()

        assert op._properties == {}

    # Properties

    def test_properties(self, init_manager, mocker):
        value = mocker.MagicMock(spec=dict)

        op = init_manager()
        op._properties = value

        assert op.properties == value

    # Methods

    def test__load_from_data(self, init_manager, mocker):
        mock_process_render = mocker.patch(
            "ht.pyfilter.operations.setproperties._process_rendertype_block"
        )
        mock_process_block = mocker.patch(
            "ht.pyfilter.operations.setproperties._process_block"
        )

        mock_stage1 = mocker.MagicMock(spec=str)
        mock_stage2 = mocker.MagicMock(spec=str)

        mock_property1 = mocker.MagicMock(spec=str)
        mock_property1.startswith.return_value = True

        mock_property2 = mocker.MagicMock(spec=str)
        mock_property2.startswith.return_value = False

        mock_block1 = mocker.MagicMock(spec=dict)
        mock_block2 = mocker.MagicMock(spec=dict)

        data = {
            mock_stage1: {mock_property1: mock_block1},
            mock_stage2: {mock_property2: mock_block2},
        }

        properties = {}

        mock_properties = mocker.PropertyMock()
        mock_properties.return_value = properties

        op = init_manager()
        type(op).properties = mock_properties

        op._load_from_data(data)

        assert mock_stage1 in properties
        assert mock_stage2 in properties

        mock_process_render.assert_called_with(
            [], mock_stage1, mock_property1.split.return_value[1], mock_block1
        )

        mock_process_block.assert_called_with(
            [], mock_stage2, mock_property2, mock_block2
        )

    # load_from_file

    def test_load_from_file(self, init_manager, mocker):
        mock_from_data = mocker.patch.object(
            setproperties.PropertySetterManager, "_load_from_data"
        )
        mock_json_load = mocker.patch("ht.pyfilter.operations.setproperties.json.load")

        mock_path = mocker.MagicMock(spec=str)

        op = init_manager()

        mock_handle = mocker.mock_open()
        mocker.patch("__builtin__.open", mock_handle)

        op.load_from_file(mock_path)

        mock_handle.assert_called_with(mock_path)
        mock_json_load.assert_called_with(mock_handle.return_value)

        mock_from_data.assert_called_with(mock_json_load.return_value)

    def test_parse_from_string(self, init_manager, mocker):
        mock_from_data = mocker.patch.object(
            setproperties.PropertySetterManager, "_load_from_data"
        )
        mock_json_loads = mocker.patch(
            "ht.pyfilter.operations.setproperties.json.loads"
        )

        mock_string = mocker.MagicMock(spec=str)

        op = init_manager()

        op.parse_from_string(mock_string)

        mock_json_loads.assert_called_with(mock_string)

        mock_from_data.assert_called_with(mock_json_loads.return_value)

    # set_properties

    def test_set_properties__has_stage(self, init_manager, mocker):
        mock_properties = mocker.patch.object(
            setproperties.PropertySetterManager,
            "properties",
            new_callable=mocker.PropertyMock,
        )

        mock_stage = mocker.MagicMock(spec=str)
        mock_property = mocker.MagicMock(spec=setproperties.PropertySetter)

        properties = {mock_stage: [mock_property]}

        mock_properties.return_value = properties

        op = init_manager()
        op.set_properties(mock_stage)

        mock_property.set_property.assert_called()

    def test_set_properties__no_stage(self, init_manager, mocker):
        mock_properties = mocker.patch.object(
            setproperties.PropertySetterManager,
            "properties",
            new_callable=mocker.PropertyMock,
        )

        mock_stage1 = mocker.MagicMock(spec=str)
        mock_stage2 = mocker.MagicMock(spec=str)

        mock_property = mocker.MagicMock(spec=setproperties.PropertySetter)

        properties = {mock_stage1: [mock_property]}
        mock_properties.return_value = properties

        op = init_manager()
        op.set_properties(mock_stage2)

        mock_property.set_property.assert_not_called()


class Test_PropertySetter(object):
    """Test the ht.pyfilter.operations.setproperties.PropertySetter class."""

    def test___init___no_findfile(self, mocker):
        """Test object initialization without finding a file."""
        mocker.patch.object(
            setproperties.PropertySetter,
            "find_file",
            new_callable=mocker.PropertyMock(return_value=False),
        )

        mock_name = mocker.MagicMock(spec=str)

        mock_value = mocker.MagicMock()
        mock_rendertype = mocker.MagicMock(spec=str)

        block = {"value": mock_value, "rendertype": mock_rendertype}

        op = setproperties.PropertySetter(mock_name, block)

        assert op._name == mock_name
        assert op._value == mock_value
        assert not op._find_file
        assert op._rendertype == mock_rendertype

    def test___init___findfile(self, patch_hou, mocker):
        """Test object initialization with finding a file."""
        mocker.patch.object(
            setproperties.PropertySetter,
            "find_file",
            new_callable=mocker.PropertyMock(return_value=True),
        )

        mock_name = mocker.MagicMock(spec=str)

        mock_value = mocker.MagicMock()

        block = {"value": mock_value, "findfile": True}

        op = setproperties.PropertySetter(mock_name, block)

        assert op._name == mock_name
        assert op._value == patch_hou.hou.findFile.return_value
        assert op._find_file
        assert op._rendertype is None

        patch_hou.hou.findFile.assert_called_with(mock_value)

    # Properties

    def test_find_file(self, init_setter, mocker):
        value = mocker.MagicMock(spec=bool)

        op = init_setter()
        op._find_file = value

        assert op.find_file == value

    def test_name(self, init_setter, mocker):
        value = mocker.MagicMock(spec=str)

        op = init_setter()
        op._name = value

        assert op.name == value

    def test_rendertype(self, init_setter, mocker):
        value = mocker.MagicMock(spec=str)

        op = init_setter()
        op._rendertype = value

        assert op.rendertype == value

    def test_value(self, init_setter, mocker):
        value = mocker.MagicMock()

        op = init_setter()
        op._value = value

        assert op.value == value

    # Methods

    # set_property

    def test_set_property__rendertype_no_match(
        self, init_setter, properties, mocker, patch_hou
    ):
        mock_rendertype = mocker.patch.object(
            setproperties.PropertySetter, "rendertype", new_callable=mocker.PropertyMock
        )

        patch_hou.hou.patternMatch.return_value = False

        op = init_setter()
        op.set_property()

        properties.mock_get.assert_called_with("renderer:rendertype")
        patch_hou.hou.patternMatch.assert_called_with(
            mock_rendertype.return_value, properties.mock_get.return_value
        )

        properties.mock_set.assert_not_called()

    def test_set_property__rendertype_match(
        self, init_setter, properties, mocker, patch_hou
    ):
        mock_rendertype = mocker.patch.object(
            setproperties.PropertySetter, "rendertype", new_callable=mocker.PropertyMock
        )
        mock_name = mocker.patch.object(
            setproperties.PropertySetter, "name", new_callable=mocker.PropertyMock
        )
        mock_value = mocker.patch.object(
            setproperties.PropertySetter, "value", new_callable=mocker.PropertyMock
        )

        patch_hou.hou.patternMatch.return_value = True

        op = init_setter()
        op.set_property()

        properties.mock_get.assert_called_with("renderer:rendertype")
        patch_hou.hou.patternMatch.assert_called_with(
            mock_rendertype.return_value, properties.mock_get.return_value
        )

        properties.mock_set.assert_called_with(
            mock_name.return_value, mock_value.return_value
        )

    def test_set_property__no_rendertype(
        self, init_setter, properties, mocker, patch_hou
    ):
        mocker.patch.object(
            setproperties.PropertySetter,
            "rendertype",
            new_callable=mocker.PropertyMock(return_value=None),
        )
        mock_name = mocker.patch.object(
            setproperties.PropertySetter, "name", new_callable=mocker.PropertyMock
        )
        mock_value = mocker.patch.object(
            setproperties.PropertySetter, "value", new_callable=mocker.PropertyMock
        )

        patch_hou.hou.patternMatch.return_value = True

        op = init_setter()
        op.set_property()

        properties.mock_get.assert_not_called()

        properties.mock_set.assert_called_with(
            mock_name.return_value, mock_value.return_value
        )


class Test_MaskedPropertySetter(object):
    """Test the ht.pyfilter.operations.setproperties.MaskedPropertySetter class."""

    def test___init__(self, mocker):
        mock_super_init = mocker.patch.object(setproperties.PropertySetter, "__init__")

        mock_name = mocker.MagicMock(spec=str)
        mock_block = mocker.MagicMock(spec=str)
        mock_mask = mocker.MagicMock(spec=str)

        op = setproperties.MaskedPropertySetter(mock_name, mock_block, mock_mask)

        mock_super_init.assert_called_with(mock_name, mock_block)

        assert op._mask == mock_block["mask"]
        assert op._mask_property_name == mock_mask

    # Properties

    def test_mask(self, init_masked_setter, mocker):
        value = mocker.MagicMock(spec=str)

        op = init_masked_setter()
        op._mask = value

        assert op.mask == value

    def test_mask_property_name(self, init_masked_setter, mocker):
        value = mocker.MagicMock(spec=str)

        op = init_masked_setter()
        op._mask_property_name = value

        assert op.mask_property_name == value

    # Methods

    # set_property

    def test_set_property__mask_no_match(self, init_masked_setter, mocker, patch_hou):
        mock_super_set = mocker.patch.object(
            setproperties.PropertySetter, "set_property"
        )
        mock_mask = mocker.patch.object(
            setproperties.MaskedPropertySetter, "mask", new_callable=mocker.PropertyMock
        )
        mock_mask_name = mocker.patch.object(
            setproperties.MaskedPropertySetter,
            "mask_property_name",
            new_callable=mocker.PropertyMock,
        )

        mock_get = mocker.patch("ht.pyfilter.operations.setproperties.get_property")

        patch_hou.hou.patternMatch.return_value = False

        op = init_masked_setter()
        op.set_property()

        mock_get.assert_called_with(mock_mask_name.return_value)
        patch_hou.hou.patternMatch.assert_called_with(
            mock_mask.return_value, mock_get.return_value
        )

        mock_super_set.assert_not_called()

    def test_set_property__mask_match(self, init_masked_setter, mocker, patch_hou):
        mock_super_set = mocker.patch.object(
            setproperties.PropertySetter, "set_property"
        )
        mock_mask = mocker.patch.object(
            setproperties.MaskedPropertySetter, "mask", new_callable=mocker.PropertyMock
        )
        mock_mask_name = mocker.patch.object(
            setproperties.MaskedPropertySetter,
            "mask_property_name",
            new_callable=mocker.PropertyMock,
        )

        mock_get = mocker.patch("ht.pyfilter.operations.setproperties.get_property")

        patch_hou.hou.patternMatch.return_value = True

        op = init_masked_setter()
        op.set_property()

        mock_get.assert_called_with(mock_mask_name.return_value)
        patch_hou.hou.patternMatch.assert_called_with(
            mock_mask.return_value, mock_get.return_value
        )

        mock_super_set.assert_called()

    def test_set_property__no_mask(self, init_masked_setter, mocker):
        mock_super_set = mocker.patch.object(
            setproperties.PropertySetter, "set_property"
        )
        mocker.patch.object(
            setproperties.MaskedPropertySetter,
            "mask",
            new_callable=mocker.PropertyMock(return_value=None),
        )

        mock_get = mocker.patch("ht.pyfilter.operations.setproperties.get_property")

        op = init_masked_setter()

        op.set_property()

        mock_get.assert_not_called()

        mock_super_set.assert_called()


class Test_SetProperties(object):
    """Test the ht.pyfilter.operations.setproperties.SetProperties class."""

    def test___init__(self, mocker):
        """Test object initialization."""
        mock_super_init = mocker.patch.object(
            setproperties.PyFilterOperation, "__init__"
        )

        mock_prop_manager = mocker.patch(
            "ht.pyfilter.operations.setproperties.PropertySetterManager", autospec=True
        )

        mock_manager = mocker.MagicMock(spec=PyFilterManager)
        op = setproperties.SetProperties(mock_manager)

        mock_super_init.assert_called_with(mock_manager)
        assert op._property_manager == mock_prop_manager.return_value

    # Properties

    def test_property_manager(self, init_operation, mocker):
        """Test the 'property_manager' property."""
        mock_value = mocker.MagicMock(spec=setproperties.PropertySetterManager)

        op = init_operation()
        op._property_manager = mock_value

        assert op.property_manager == mock_value

    # Static Methods

    # build_arg_string

    def test_build_arg_string(self, mocker):
        """Test arg string construction."""
        assert setproperties.SetProperties.build_arg_string() == ""

        # Test properties flag.
        mock_dumps = mocker.patch("ht.pyfilter.operations.setproperties.json.dumps")

        mock_properties = mocker.MagicMock(spec=dict)
        mock_result = mocker.MagicMock(spec=str)
        mock_dumps.return_value.replace.return_value = mock_result

        result = setproperties.SetProperties.build_arg_string(
            properties=mock_properties
        )

        assert result == '--properties="{}"'.format(mock_result)

        mock_dumps.assert_called_with(mock_properties)
        mock_dumps.return_value.replace.assert_called_with('"', '\\"')

        # Test properties-file flag.
        mock_path = mocker.MagicMock(spec=str)

        result = setproperties.SetProperties.build_arg_string(properties_file=mock_path)

        assert result == "--properties-file={}".format(mock_path)

    # register_parser_args

    def test_register_parser_args(self, mocker):
        mock_parser = mocker.MagicMock(spec=argparse.ArgumentParser)

        setproperties.SetProperties.register_parser_args(mock_parser)

        calls = [
            mocker.call("--properties", nargs=1, action="store"),
            mocker.call(
                "--properties-file", nargs="*", action="store", dest="properties_file"
            ),
        ]
        mock_parser.add_argument.assert_has_calls(calls)

    # Methods

    def test_filter_camera(self, init_operation, mocker):
        mock_prop_manager = mocker.patch.object(
            setproperties.SetProperties,
            "property_manager",
            new_callable=mocker.PropertyMock,
        )

        mock_manager = mocker.MagicMock(spec=setproperties.PropertySetterManager)
        mock_prop_manager.return_value = mock_manager

        op = init_operation()

        op.filter_camera()

        mock_manager.set_properties.assert_called_with("camera")

    def test_filter_instance(self, init_operation, mocker, patch_soho):
        mock_prop_manager = mocker.patch.object(
            setproperties.SetProperties,
            "property_manager",
            new_callable=mocker.PropertyMock,
        )

        mock_manager = mocker.MagicMock(spec=setproperties.PropertySetterManager)
        mock_prop_manager.return_value = mock_manager

        op = init_operation()

        op.filter_instance()

        mock_manager.set_properties.assert_called_with("instance")

    def test_filter_light(self, init_operation, mocker, patch_soho):
        mock_prop_manager = mocker.patch.object(
            setproperties.SetProperties,
            "property_manager",
            new_callable=mocker.PropertyMock,
        )

        mock_manager = mocker.MagicMock(spec=setproperties.PropertySetterManager)
        mock_prop_manager.return_value = mock_manager

        op = init_operation()

        op.filter_light()

        mock_manager.set_properties.assert_called_with("light")

    # process_parsed_args

    def test_process_parsed_args__noop(self, init_operation, mocker):
        mock_prop_manager = mocker.patch.object(
            setproperties.SetProperties,
            "property_manager",
            new_callable=mocker.PropertyMock,
        )

        mock_mgr = mocker.MagicMock(spec=setproperties.PropertySetterManager)

        mock_prop_manager.return_value = mock_mgr

        mock_namespace = mocker.MagicMock(spec=argparse.Namespace)
        mock_namespace.properties = None
        mock_namespace.properties_file = None

        op = init_operation()

        op.process_parsed_args(mock_namespace)

        mock_mgr.parse_from_string.assert_not_called()
        mock_mgr.load_from_file.assert_not_called()

    def test_process_parsed_args__properties(self, init_operation, mocker):
        mock_prop_manager = mocker.patch.object(
            setproperties.SetProperties,
            "property_manager",
            new_callable=mocker.PropertyMock,
        )

        mock_mgr = mocker.MagicMock(spec=setproperties.PropertySetterManager)

        mock_prop_manager.return_value = mock_mgr

        mock_prop1 = mocker.MagicMock(spec=str)
        mock_prop2 = mocker.MagicMock(spec=str)

        mock_namespace = mocker.MagicMock(spec=argparse.Namespace)
        mock_namespace.properties = [mock_prop1, mock_prop2]
        mock_namespace.properties_file = None

        op = init_operation()

        op.process_parsed_args(mock_namespace)

        calls = [mocker.call(mock_prop1), mocker.call(mock_prop2)]

        mock_mgr.parse_from_string.assert_has_calls(calls)
        mock_mgr.load_from_file.assert_not_called()

    def test_process_parsed_args__properties_file(self, init_operation, mocker):
        mock_prop_manager = mocker.patch.object(
            setproperties.SetProperties,
            "property_manager",
            new_callable=mocker.PropertyMock,
        )

        mock_mgr = mocker.MagicMock(spec=setproperties.PropertySetterManager)

        mock_prop_manager.return_value = mock_mgr

        mock_file1 = mocker.MagicMock(spec=str)
        mock_file2 = mocker.MagicMock(spec=str)

        mock_namespace = mocker.MagicMock(spec=argparse.Namespace)
        mock_namespace.properties_file = [mock_file1, mock_file2]
        mock_namespace.properties = None

        op = init_operation()

        op.process_parsed_args(mock_namespace)

        calls = [mocker.call(mock_file1), mocker.call(mock_file2)]

        mock_mgr.parse_from_string.assert_not_called()
        mock_mgr.load_from_file.assert_has_calls(calls)

    # should_run

    def test_should_run__false(self, init_operation, mocker):
        mock_prop_manager = mocker.patch.object(
            setproperties.SetProperties,
            "property_manager",
            new_callable=mocker.PropertyMock,
        )

        mock_properties = mocker.MagicMock(spec=dict)

        mock_mgr = mocker.MagicMock(spec=setproperties.PropertySetterManager)
        type(mock_mgr).properties = mocker.PropertyMock(return_value=mock_properties)

        mock_prop_manager.return_value = mock_mgr

        op = init_operation()

        result = op.should_run()

        assert not result

    def test_should_run__true(self, init_operation, mocker):
        mock_prop_manager = mocker.patch.object(
            setproperties.SetProperties,
            "property_manager",
            new_callable=mocker.PropertyMock,
        )

        mock_properties = {"key": "value"}

        mock_mgr = mocker.MagicMock(spec=setproperties.PropertySetterManager)
        type(mock_mgr).properties = mocker.PropertyMock(return_value=mock_properties)

        mock_prop_manager.return_value = mock_mgr

        op = init_operation()

        result = op.should_run()

        assert result


class Test__create_property_setter(object):
    """Test the ht.pyfilter.operations.setproperties._create_property_setter."""

    def test_property(self, mocker):
        mock_setter = mocker.patch(
            "ht.pyfilter.operations.setproperties.PropertySetter", autospec=True
        )

        mock_name = mocker.MagicMock(spec=str)
        mock_block = mocker.MagicMock(spec=dict)
        mock_stage = mocker.MagicMock(spec=str)

        result = setproperties._create_property_setter(
            mock_name, mock_block, mock_stage
        )

        assert result == mock_setter.return_value

        mock_setter.assert_called_with(mock_name, mock_block)

    def test_mask_plane(self, mocker):
        mock_setter = mocker.patch(
            "ht.pyfilter.operations.setproperties.MaskedPropertySetter", autospec=True
        )

        mock_name = mocker.MagicMock(spec=str)
        mock_block = mocker.MagicMock(spec=dict)
        mock_block.__contains__.return_value = True

        stage = "plane"

        result = setproperties._create_property_setter(mock_name, mock_block, stage)

        assert result == mock_setter.return_value

        mock_block.__contains__.assert_called_with("mask")
        mock_setter.assert_called_with(mock_name, mock_block, "plane:variable")

    def test_mask_fog(self, mocker):
        mock_setter = mocker.patch(
            "ht.pyfilter.operations.setproperties.MaskedPropertySetter", autospec=True
        )

        mock_name = mocker.MagicMock(spec=str)
        mock_block = mocker.MagicMock(spec=dict)
        mock_block.__contains__.return_value = True

        stage = "fog"

        result = setproperties._create_property_setter(mock_name, mock_block, stage)

        assert result == mock_setter.return_value

        mock_block.__contains__.assert_called_with("mask")
        mock_setter.assert_called_with(mock_name, mock_block, "object:name")

    def test_mask_light(self, mocker):
        mock_setter = mocker.patch(
            "ht.pyfilter.operations.setproperties.MaskedPropertySetter", autospec=True
        )

        mock_name = mocker.MagicMock(spec=str)
        mock_block = mocker.MagicMock(spec=dict)
        mock_block.__contains__.return_value = True

        stage = "light"

        result = setproperties._create_property_setter(mock_name, mock_block, stage)

        assert result == mock_setter.return_value

        mock_block.__contains__.assert_called_with("mask")
        mock_setter.assert_called_with(mock_name, mock_block, "object:name")

    def test_mask_instance(self, mocker):
        mock_setter = mocker.patch(
            "ht.pyfilter.operations.setproperties.MaskedPropertySetter", autospec=True
        )

        mock_name = mocker.MagicMock(spec=str)
        mock_block = mocker.MagicMock(spec=dict)
        mock_block.__contains__.return_value = True

        stage = "instance"

        result = setproperties._create_property_setter(mock_name, mock_block, stage)

        assert result == mock_setter.return_value

        mock_block.__contains__.assert_called_with("mask")
        mock_setter.assert_called_with(mock_name, mock_block, "object:name")

    def test_mask_unknown_stage(self, mocker):
        mock_setter = mocker.patch(
            "ht.pyfilter.operations.setproperties.PropertySetter", autospec=True
        )
        mock_logger = mocker.patch("ht.pyfilter.operations.setproperties._logger")

        mock_name = mocker.MagicMock(spec=str)
        mock_block = mocker.MagicMock(spec=dict)
        mock_block.__contains__.return_value = True

        stage = mocker.MagicMock(spec=str)

        result = setproperties._create_property_setter(mock_name, mock_block, stage)

        assert result == mock_setter.return_value

        mock_block.__contains__.assert_called_with("mask")
        mock_logger.warning.assert_called()
        mock_setter.assert_called_with(mock_name, mock_block)


class Test__process_block(object):
    """Test the ht.pyfilter.operations.setproperties._process_block."""

    def test_dict(self, mocker):
        mock_create = mocker.patch(
            "ht.pyfilter.operations.setproperties._create_property_setter"
        )

        properties = []
        mock_stage = mocker.MagicMock(spec=str)
        mock_name = mocker.MagicMock(spec=str)

        mock_block = mocker.MagicMock(spec=dict)

        setproperties._process_block(properties, mock_stage, mock_name, mock_block)

        assert properties == [mock_create.return_value]

        mock_create.assert_called_with(mock_name, mock_block, mock_stage)

    def test_list(self, mocker):
        mock_create = mocker.patch(
            "ht.pyfilter.operations.setproperties._create_property_setter"
        )

        properties = []
        mock_stage = mocker.MagicMock(spec=str)
        mock_name = mocker.MagicMock(spec=str)

        mock_block = mocker.MagicMock(spec=dict)

        setproperties._process_block(properties, mock_stage, mock_name, [mock_block])

        assert properties == [mock_create.return_value]

        mock_create.assert_called_with(mock_name, mock_block, mock_stage)

    def test_noniterable(self, mocker):
        mock_create = mocker.patch(
            "ht.pyfilter.operations.setproperties._create_property_setter"
        )

        properties = []
        mock_stage = mocker.MagicMock(spec=str)
        mock_name = mocker.MagicMock(spec=str)

        mock_block = mocker.MagicMock(spec=int)

        setproperties._process_block(properties, mock_stage, mock_name, mock_block)

        assert properties == []

        mock_create.assert_not_called()


class Test__process_rendertype_block(object):
    """Test the ht.pyfilter.operations.setproperties._process_rendertype_block."""

    def test_dict(self, mocker):
        mock_process = mocker.patch(
            "ht.pyfilter.operations.setproperties._process_block"
        )

        mock_properties = mocker.MagicMock(spec=list)
        mock_stage = mocker.MagicMock(spec=str)
        mock_rendertype = mocker.MagicMock(spec=str)

        mock_name = mocker.MagicMock(spec=str)

        block = {}

        property_block = {mock_name: block}

        setproperties._process_rendertype_block(
            mock_properties, mock_stage, mock_rendertype, property_block
        )

        mock_process.assert_called_with(
            mock_properties, mock_stage, mock_name, {"rendertype": mock_rendertype}
        )

    def test_list(self, mocker):
        mock_process = mocker.patch(
            "ht.pyfilter.operations.setproperties._process_block"
        )

        mock_properties = mocker.MagicMock(spec=list)
        mock_stage = mocker.MagicMock(spec=str)
        mock_rendertype = mocker.MagicMock(spec=str)

        mock_name = mocker.MagicMock(spec=str)

        block = {}

        property_block = {mock_name: [block]}

        setproperties._process_rendertype_block(
            mock_properties, mock_stage, mock_rendertype, property_block
        )

        mock_process.assert_called_with(
            mock_properties, mock_stage, mock_name, [{"rendertype": mock_rendertype}]
        )

    def test_error(self, mocker):
        mock_properties = mocker.MagicMock(spec=list)
        mock_stage = mocker.MagicMock(spec=str)
        mock_rendertype = mocker.MagicMock(spec=str)

        mock_name = mocker.MagicMock(spec=str)

        property_block = {mock_name: mocker.MagicMock()}

        with pytest.raises(TypeError):
            setproperties._process_rendertype_block(
                mock_properties, mock_stage, mock_rendertype, property_block
            )
