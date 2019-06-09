"""Test the ht.pyfilter.operations.deepimage module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import argparse
from mock import MagicMock, PropertyMock, call, mock_open, patch
import unittest

# Houdini Toolbox Imports
from ht.pyfilter.manager import PyFilterManager
from ht.pyfilter.operations import setproperties

reload(setproperties)

# =============================================================================
# CLASSES
# =============================================================================

class Test_PropertySetterManager(unittest.TestCase):
    """Test the ht.pyfilter.operations.setproperties.PropertySetterManager class."""

    def test___init__(self):
        op = setproperties.PropertySetterManager()

        self.assertEqual(op._properties, {})

    # Properties

    @patch.object(setproperties.PropertySetterManager, "__init__", lambda x, y: None)
    def test_properties(self):
        value = MagicMock(spec=dict)

        op = setproperties.PropertySetterManager(None)
        op._properties = value

        self.assertEqual(op.properties, value)

    # Methods

    # _load_from_data

    @patch("ht.pyfilter.operations.setproperties._process_block")
    @patch("ht.pyfilter.operations.setproperties._process_rendertype_block")
    @patch.object(setproperties.PropertySetterManager, "properties", new_callable=PropertyMock)
    @patch.object(setproperties.PropertySetterManager, "__init__", lambda x, y: None)
    def test__load_from_data(self, mock_properties, mock_process_render, mock_process_block):
        mock_stage1 = MagicMock(spec=str)
        mock_stage2 = MagicMock(spec=str)

        mock_property1 = MagicMock(spec=str)
        mock_property1.startswith.return_value = True

        mock_property2 = MagicMock(spec=str)
        mock_property2.startswith.return_value = False

        mock_block1 = MagicMock(spec=dict)
        mock_block2 = MagicMock(spec=dict)

        data = {
            mock_stage1: {
                mock_property1: mock_block1
            },
            mock_stage2: {
                mock_property2: mock_block2
            }
        }

        properties = {}

        mock_properties.return_value = properties

        op = setproperties.PropertySetterManager(None)
        op._load_from_data(data)

        self.assertTrue(mock_stage1 in properties)
        self.assertTrue(mock_stage2 in properties)

        mock_process_render.assert_called_with(
            [], mock_stage1, mock_property1.split.return_value[1], mock_block1
        )

        mock_process_block.assert_called_with(
            [], mock_stage2, mock_property2, mock_block2
        )

    # load_from_file

    @patch("ht.pyfilter.operations.setproperties.json.load")
    @patch("ht.pyfilter.operations.setproperties.logger")
    @patch.object(setproperties.PropertySetterManager, "_load_from_data")
    @patch.object(setproperties.PropertySetterManager, "__init__", lambda x, y: None)
    def test_load_from_file(self, mock_from_data, mock_logger, mock_json_load):
        mock_path = MagicMock(spec=str)

        op = setproperties.PropertySetterManager(None)

        m = mock_open()

        with patch("__builtin__.open", m):
            op.load_from_file(mock_path)

        m.assert_called_with(mock_path)
        mock_json_load.assert_called_with(m.return_value)

        mock_from_data.assert_called_with(mock_json_load.return_value)

    # parse_from_string

    @patch("ht.pyfilter.operations.setproperties.json.loads")
    @patch.object(setproperties.PropertySetterManager, "_load_from_data")
    @patch.object(setproperties.PropertySetterManager, "__init__", lambda x, y: None)
    def test_parse_from_string(self, mock_from_data, mock_json_loads):
        mock_string = MagicMock(spec=str)

        op = setproperties.PropertySetterManager(None)

        op.parse_from_string(mock_string)

        mock_json_loads.assert_called_with(mock_string)

        mock_from_data.assert_called_with(mock_json_loads.return_value)

    # set_properties

    @patch.object(setproperties.PropertySetterManager, "properties", new_callable=PropertyMock)
    @patch.object(setproperties.PropertySetterManager, "__init__", lambda x, y: None)
    def test_set_properties__has_stage(self, mock_properties):
        mock_stage = MagicMock(spec=str)

        mock_property = MagicMock(spec=setproperties.PropertySetter)

        properties = {mock_stage: [mock_property]}
        mock_properties.return_value = properties

        op = setproperties.PropertySetterManager(None)
        op.set_properties(mock_stage)

        mock_property.set_property.assert_called()

    @patch.object(setproperties.PropertySetterManager, "properties", new_callable=PropertyMock)
    @patch.object(setproperties.PropertySetterManager, "__init__", lambda x, y: None)
    def test_set_properties__no_stage(self, mock_properties):
        mock_stage1 = MagicMock(spec=str)
        mock_stage2 = MagicMock(spec=str)

        mock_property = MagicMock(spec=setproperties.PropertySetter)

        properties = {mock_stage1: [mock_property]}
        mock_properties.return_value = properties

        op = setproperties.PropertySetterManager(None)
        op.set_properties(mock_stage2)

        mock_property.set_property.assert_not_called()


class Test_PropertySetter(unittest.TestCase):
    """Test the ht.pyfilter.operations.setproperties.PropertySetter class."""

    def setUp(self):
        super(Test_PropertySetter, self).setUp()

        self.mock_hou = MagicMock()

        modules = {"hou": self.mock_hou}

        self.patcher = patch.dict("sys.modules", modules)
        self.patcher.start()

    def tearDown(self):
        super(Test_PropertySetter, self).tearDown()

        self.patcher.stop()

    @patch.object(setproperties.PropertySetter, "find_file", new_callable=PropertyMock(return_value=False))
    def test___init___no_findfile(self, mock_find_file):
        mock_name = MagicMock(spec=str)

        mock_value = MagicMock()
        mock_rendertype = MagicMock(spec=str)

        block = {
            "value": mock_value,
            "rendertype": mock_rendertype
        }

        op = setproperties.PropertySetter(mock_name, block)

        self.assertEqual(op._name, mock_name)
        self.assertEqual(op._value, mock_value)
        self.assertFalse(op._find_file)
        self.assertEqual(op._rendertype, mock_rendertype)

    @patch.object(setproperties.PropertySetter, "find_file", new_callable=PropertyMock(return_value=True))
    def test___init___findfile(self, mock_find_file):
        mock_name = MagicMock(spec=str)

        mock_value = MagicMock()

        block = {
            "value": mock_value,
            "findfile": True
        }

        op = setproperties.PropertySetter(mock_name, block)

        self.assertEqual(op._name, mock_name)
        self.assertEqual(op._value, self.mock_hou.findFile.return_value)
        self.assertTrue(op._find_file)
        self.assertIsNone(op._rendertype)

        self.mock_hou.findFile.assert_called_with(mock_value)

    # Properties

    @patch.object(setproperties.PropertySetter, "__init__", lambda x, y, z: None)
    def test_find_file(self):
        value = MagicMock(spec=bool)

        op = setproperties.PropertySetter(None, None)

        op._find_file = value

        self.assertEqual(op.find_file, value)

    @patch.object(setproperties.PropertySetter, "__init__", lambda x, y, z: None)
    def test_name(self):
        value = MagicMock(spec=str)

        op = setproperties.PropertySetter(None, None)

        op._name = value

        self.assertEqual(op.name, value)

    @patch.object(setproperties.PropertySetter, "__init__", lambda x, y, z: None)
    def test_rendertype(self):
        value = MagicMock(spec=str)

        op = setproperties.PropertySetter(None, None)

        op._rendertype = value

        self.assertEqual(op.rendertype, value)

    @patch.object(setproperties.PropertySetter, "__init__", lambda x, y, z: None)
    def test_value(self):
        value = MagicMock()

        op = setproperties.PropertySetter(None, None)

        op._value = value

        self.assertEqual(op.value, value)

    # Methods

    # set_property

    @patch("ht.pyfilter.operations.setproperties.set_property")
    @patch("ht.pyfilter.operations.setproperties.logger")
    @patch("ht.pyfilter.operations.setproperties.get_property")
    @patch.object(setproperties.PropertySetter, "rendertype", new_callable=PropertyMock)
    @patch.object(setproperties.PropertySetter, "__init__", lambda x, y, z: None)
    def test_set_property__rendertype_no_match(self, mock_rendertype, mock_get, mock_logger, mock_set):

        self.mock_hou.patternMatch.return_value = False

        op = setproperties.PropertySetter(None, None)
        op.set_property()

        mock_get.assert_called_with("renderer:rendertype")
        self.mock_hou.patternMatch.assert_called_with(mock_rendertype.return_value, mock_get.return_value)

        mock_set.assert_not_called()

    @patch("ht.pyfilter.operations.setproperties.set_property")
    @patch("ht.pyfilter.operations.setproperties.logger")
    @patch("ht.pyfilter.operations.setproperties.get_property")
    @patch.object(setproperties.PropertySetter, "value", new_callable=PropertyMock)
    @patch.object(setproperties.PropertySetter, "name", new_callable=PropertyMock)
    @patch.object(setproperties.PropertySetter, "rendertype", new_callable=PropertyMock)
    @patch.object(setproperties.PropertySetter, "__init__", lambda x, y, z: None)
    def test_set_property__rendertype_match(self, mock_rendertype, mock_name, mock_value, mock_get, mock_logger, mock_set):
        self.mock_hou.patternMatch.return_value = True

        op = setproperties.PropertySetter(None, None)
        op.set_property()

        mock_get.assert_called_with("renderer:rendertype")
        self.mock_hou.patternMatch.assert_called_with(mock_rendertype.return_value, mock_get.return_value)

        mock_set.assert_called_with(mock_name.return_value, mock_value.return_value)

    @patch("ht.pyfilter.operations.setproperties.set_property")
    @patch("ht.pyfilter.operations.setproperties.logger")
    @patch("ht.pyfilter.operations.setproperties.get_property")
    @patch.object(setproperties.PropertySetter, "value", new_callable=PropertyMock)
    @patch.object(setproperties.PropertySetter, "name", new_callable=PropertyMock)
    @patch.object(setproperties.PropertySetter, "rendertype", new_callable=PropertyMock(return_value=None))
    @patch.object(setproperties.PropertySetter, "__init__", lambda x, y, z: None)
    def test_set_property__no_rendertype(self, mock_rendertype, mock_name, mock_value, mock_get, mock_logger, mock_set):
        self.mock_hou.patternMatch.return_value = True

        op = setproperties.PropertySetter(None, None)
        op.set_property()

        mock_get.assert_not_called()

        mock_set.assert_called_with(mock_name.return_value, mock_value.return_value)


class Test_MaskedPropertySetter(unittest.TestCase):
    """Test the ht.pyfilter.operations.setproperties.MaskedPropertySetter class."""

    def setUp(self):
        super(Test_MaskedPropertySetter, self).setUp()

        self.mock_hou = MagicMock()

        modules = {"hou": self.mock_hou}

        self.patcher = patch.dict("sys.modules", modules)
        self.patcher.start()

    def tearDown(self):
        super(Test_MaskedPropertySetter, self).tearDown()

        self.patcher.stop()

    @patch.object(setproperties.PropertySetter, "__init__")
    def test___init__(self, mock_super_init):
        mock_name = MagicMock(spec=str)
        mock_block = MagicMock(spec=str)
        mock_mask = MagicMock(spec=str)

        op = setproperties.MaskedPropertySetter(mock_name, mock_block, mock_mask)

        mock_super_init.assert_called_with(mock_name, mock_block)

        self.assertEqual(op._mask, mock_block["mask"])
        self.assertEqual(op._mask_property_name, mock_mask)

    # Properties

    @patch.object(setproperties.MaskedPropertySetter, "__init__", lambda x, y, z: None)
    def test_mask(self):
        value = MagicMock(spec=str)

        op = setproperties.MaskedPropertySetter(None, None)

        op._mask = value

        self.assertEqual(op.mask, value)

    @patch.object(setproperties.MaskedPropertySetter, "__init__", lambda x, y, z: None)
    def test_mask_property_name(self):
        value = MagicMock(spec=str)

        op = setproperties.MaskedPropertySetter(None, None)

        op._mask_property_name = value

        self.assertEqual(op.mask_property_name, value)

    # Methods

    # set_property

    @patch.object(setproperties.PropertySetter, "set_property")
    @patch("ht.pyfilter.operations.setproperties.get_property")
    @patch.object(setproperties.MaskedPropertySetter, "mask_property_name", new_callable=PropertyMock)
    @patch.object(setproperties.MaskedPropertySetter, "mask", new_callable=PropertyMock)
    @patch.object(setproperties.MaskedPropertySetter, "__init__", lambda x, y, z: None)
    def test_set_property__mask_no_match(self, mock_mask, mock_mask_name, mock_get, mock_super_set):
        self.mock_hou.patternMatch.return_value = False

        op = setproperties.MaskedPropertySetter(None, None)
        op.set_property()

        mock_get.assert_called_with(mock_mask_name.return_value)
        self.mock_hou.patternMatch.assert_called_with(mock_mask.return_value, mock_get.return_value)

        mock_super_set.assert_not_called()

    @patch.object(setproperties.PropertySetter, "set_property")
    @patch("ht.pyfilter.operations.setproperties.get_property")
    @patch.object(setproperties.MaskedPropertySetter, "mask_property_name", new_callable=PropertyMock)
    @patch.object(setproperties.MaskedPropertySetter, "mask", new_callable=PropertyMock)
    @patch.object(setproperties.MaskedPropertySetter, "__init__", lambda x, y, z: None)
    def test_set_property__mask_match(self, mock_mask, mock_mask_name, mock_get, mock_super_set):
        self.mock_hou.patternMatch.return_value = True

        op = setproperties.MaskedPropertySetter(None, None)
        op.set_property()

        mock_get.assert_called_with(mock_mask_name.return_value)
        self.mock_hou.patternMatch.assert_called_with(mock_mask.return_value, mock_get.return_value)

        mock_super_set.assert_called()

    @patch.object(setproperties.PropertySetter, "set_property")
    @patch("ht.pyfilter.operations.setproperties.get_property")
    @patch.object(setproperties.MaskedPropertySetter, "mask_property_name", new_callable=PropertyMock)
    @patch.object(setproperties.MaskedPropertySetter, "mask", new_callable=PropertyMock(return_value=None))
    @patch.object(setproperties.MaskedPropertySetter, "__init__", lambda x, y, z: None)
    def test_set_property__no_mask(self,mock_mask, mock_mask_name, mock_get, mock_super_set):
        op = setproperties.MaskedPropertySetter(None, None)
        op.set_property()

        mock_get.assert_not_called()

        mock_super_set.assert_called()


class Test_SetProperties(unittest.TestCase):
    """Test the ht.pyfilter.operations.setproperties.SetProperties class."""

    def setUp(self):
        super(Test_SetProperties, self).setUp()

        modules = {"mantra": MagicMock()}
        self.patcher = patch.dict("sys.modules", modules)
        self.patcher.start()

        self.log_patcher = patch("ht.pyfilter.operations.operation.logger", autospec=True)
        self.log_patcher.start()

    def tearDown(self):
        super(Test_SetProperties, self).tearDown()

        self.patcher.stop()
        self.log_patcher.stop()

    @patch("ht.pyfilter.operations.setproperties.PropertySetterManager", autospec=True)
    def test___init__(self, mock_prop_manager):
        mock_manager = MagicMock(spec=PyFilterManager)
        op = setproperties.SetProperties(mock_manager)

        self.assertEqual(op._data, {})
        self.assertEqual(op._manager, mock_manager)
        self.assertEqual(op._property_manager, mock_prop_manager.return_value)

    # Properties

    @patch.object(setproperties.SetProperties, "__init__", lambda x, y: None)
    def test_disable_primary_image(self):
        value = MagicMock(spec=setproperties.PropertySetterManager)

        op = setproperties.SetProperties(None)
        op._property_manager = value

        self.assertEqual(op.property_manager, value)

    # Static Methods

    # build_arg_string

    def test_build_arg_string__empty(self):
        result = setproperties.SetProperties.build_arg_string()

        self.assertEqual(result, "")

    @patch("ht.pyfilter.operations.setproperties.json.dumps")
    def test_build_arg_string__properties(self, mock_dumps):
        mock_properties = MagicMock(spec=dict)

        mock_result = MagicMock(spec=str)
        mock_dumps.return_value.replace.return_value = mock_result

        result = setproperties.SetProperties.build_arg_string(properties=mock_properties)

        self.assertEqual(result, '--properties="{}"'.format(mock_result))

        mock_dumps.assert_called_with(mock_properties)

        mock_dumps.return_value.replace.assert_called_with('"', '\\"')

    def test_build_arg_string__properties_file(self):
        mock_path = MagicMock(spec=str)

        result = setproperties.SetProperties.build_arg_string(properties_file=mock_path)

        self.assertEqual(result, "--properties-file={}".format(mock_path))

    # register_parser_args

    def test_register_parser_args(self):
        mock_parser = MagicMock(spec=argparse.ArgumentParser)

        setproperties.SetProperties.register_parser_args(mock_parser)

        calls = [
            call("--properties", nargs=1, action="store"),
            call("--properties-file", nargs="*", action="store", dest="properties_file"),
        ]
        mock_parser.add_argument.assert_has_calls(calls)

    # Methods

    @patch.object(setproperties.SetProperties, "property_manager", new_callable=PropertyMock)
    @patch.object(setproperties.SetProperties, "__init__", lambda x, y: None)
    def test_filterCamera(self, mock_set):
        mock_manager = MagicMock(spec=setproperties.PropertySetterManager)
        mock_set.return_value = mock_manager

        op = setproperties.SetProperties(None)

        op.filterCamera()

        mock_manager.set_properties.assert_called_with("camera")

    @patch.object(setproperties.SetProperties, "property_manager", new_callable=PropertyMock)
    @patch.object(setproperties.SetProperties, "__init__", lambda x, y: None)
    def test_filterInstance(self, mock_set):
        mock_manager = MagicMock(spec=setproperties.PropertySetterManager)
        mock_set.return_value = mock_manager

        op = setproperties.SetProperties(None)

        op.filterInstance()

        mock_manager.set_properties.assert_called_with("instance")

    @patch.object(setproperties.SetProperties, "property_manager", new_callable=PropertyMock)
    @patch.object(setproperties.SetProperties, "__init__", lambda x, y: None)
    def test_filterLight(self, mock_set):
        mock_manager = MagicMock(spec=setproperties.PropertySetterManager)
        mock_set.return_value = mock_manager

        op = setproperties.SetProperties(None)

        op.filterLight()

        mock_manager.set_properties.assert_called_with("light")

    # process_parsed_args

    @patch.object(setproperties.SetProperties, "property_manager", new_callable=PropertyMock)
    @patch.object(setproperties.SetProperties, "__init__", lambda x, y: None)
    def test_process_parsed_args__noop(self, mock_manager):
        mock_mgr = MagicMock(spec=setproperties.PropertySetterManager)

        mock_manager.return_value = mock_mgr

        mock_namespace = MagicMock(spec=argparse.Namespace)
        mock_namespace.properties = None
        mock_namespace.properties_file = None

        op = setproperties.SetProperties(None)

        op.process_parsed_args(mock_namespace)

        mock_mgr.parse_from_string.assert_not_called()
        mock_mgr.load_from_file.assert_not_called()

    @patch.object(setproperties.SetProperties, "property_manager", new_callable=PropertyMock)
    @patch.object(setproperties.SetProperties, "__init__", lambda x, y: None)
    def test_process_parsed_args__properties(self, mock_manager):
        mock_mgr = MagicMock(spec=setproperties.PropertySetterManager)

        mock_manager.return_value = mock_mgr

        mock_prop1 = MagicMock(spec=str)
        mock_prop2 = MagicMock(spec=str)

        mock_namespace = MagicMock(spec=argparse.Namespace)
        mock_namespace.properties = [mock_prop1, mock_prop2]
        mock_namespace.properties_file = None

        op = setproperties.SetProperties(None)

        op.process_parsed_args(mock_namespace)

        calls = [call(mock_prop1), call(mock_prop2)]

        mock_mgr.parse_from_string.assert_has_calls(calls)
        mock_mgr.load_from_file.assert_not_called()

    @patch.object(setproperties.SetProperties, "property_manager", new_callable=PropertyMock)
    @patch.object(setproperties.SetProperties, "__init__", lambda x, y: None)
    def test_process_parsed_args__properties_file(self, mock_manager):
        mock_mgr = MagicMock(spec=setproperties.PropertySetterManager)

        mock_manager.return_value = mock_mgr

        mock_file1 = MagicMock(spec=str)
        mock_file2 = MagicMock(spec=str)

        mock_namespace = MagicMock(spec=argparse.Namespace)
        mock_namespace.properties_file = [mock_file1, mock_file2]
        mock_namespace.properties = None

        op = setproperties.SetProperties(None)

        op.process_parsed_args(mock_namespace)

        calls = [call(mock_file1), call(mock_file2)]

        mock_mgr.parse_from_string.assert_not_called()
        mock_mgr.load_from_file.assert_has_calls(calls)

    # should_run

    @patch.object(setproperties.SetProperties, "property_manager", new_callable=PropertyMock)
    @patch.object(setproperties.SetProperties, "__init__", lambda x, y: None)
    def test_should_run__false(self, mock_manager):
        mock_properties = MagicMock(spec=dict)

        mock_mgr = MagicMock(spec=setproperties.PropertySetterManager)
        type(mock_mgr).properties = PropertyMock(return_value=mock_properties)

        mock_manager.return_value = mock_mgr

        op = setproperties.SetProperties(None)

        result = op.should_run()

        self.assertFalse(result)

    @patch.object(setproperties.SetProperties, "property_manager", new_callable=PropertyMock)
    @patch.object(setproperties.SetProperties, "__init__", lambda x, y: None)
    def test_should_run__true(self, mock_manager):
        mock_properties = {"key": "value"}

        mock_mgr = MagicMock(spec=setproperties.PropertySetterManager)
        type(mock_mgr).properties = PropertyMock(return_value=mock_properties)

        mock_manager.return_value = mock_mgr

        op = setproperties.SetProperties(None)

        result = op.should_run()

        self.assertTrue(result)


class Test__create_property_setter(unittest.TestCase):
    """Test the ht.pyfilter.operations.setproperties._create_property_setter."""

    @patch("ht.pyfilter.operations.setproperties.PropertySetter", autospec=True)
    def test_property(self, mock_setter):
        mock_name = MagicMock(spec=str)
        mock_block = MagicMock(spec=dict)
        mock_stage = MagicMock(spec=str)

        result = setproperties._create_property_setter(mock_name, mock_block, mock_stage)

        self.assertEqual(result, mock_setter.return_value)

        mock_setter.assert_called_with(mock_name, mock_block)

    @patch("ht.pyfilter.operations.setproperties.MaskedPropertySetter", autospec=True)
    def test_mask_plane(self, mock_setter):
        mock_name = MagicMock(spec=str)
        mock_block = MagicMock(spec=dict)
        mock_block.__contains__.return_value = True

        stage = "plane"

        result = setproperties._create_property_setter(mock_name, mock_block, stage)

        self.assertEqual(result, mock_setter.return_value)

        mock_block.__contains__.assert_called_with("mask")
        mock_setter.assert_called_with(mock_name, mock_block, "plane:variable")

    @patch("ht.pyfilter.operations.setproperties.MaskedPropertySetter", autospec=True)
    def test_mask_fog(self, mock_setter):
        mock_name = MagicMock(spec=str)
        mock_block = MagicMock(spec=dict)
        mock_block.__contains__.return_value = True

        stage = "fog"

        result = setproperties._create_property_setter(mock_name, mock_block, stage)

        self.assertEqual(result, mock_setter.return_value)

        mock_block.__contains__.assert_called_with("mask")
        mock_setter.assert_called_with(mock_name, mock_block, "object:name")

    @patch("ht.pyfilter.operations.setproperties.MaskedPropertySetter", autospec=True)
    def test_mask_light(self, mock_setter):
        mock_name = MagicMock(spec=str)
        mock_block = MagicMock(spec=dict)
        mock_block.__contains__.return_value = True

        stage = "light"

        result = setproperties._create_property_setter(mock_name, mock_block, stage)

        self.assertEqual(result, mock_setter.return_value)

        mock_block.__contains__.assert_called_with("mask")
        mock_setter.assert_called_with(mock_name, mock_block, "object:name")

    @patch("ht.pyfilter.operations.setproperties.MaskedPropertySetter", autospec=True)
    def test_mask_instance(self, mock_setter):
        mock_name = MagicMock(spec=str)
        mock_block = MagicMock(spec=dict)
        mock_block.__contains__.return_value = True

        stage = "instance"

        result = setproperties._create_property_setter(mock_name, mock_block, stage)

        self.assertEqual(result, mock_setter.return_value)

        mock_block.__contains__.assert_called_with("mask")
        mock_setter.assert_called_with(mock_name, mock_block, "object:name")

    @patch("ht.pyfilter.operations.setproperties.logger")
    @patch("ht.pyfilter.operations.setproperties.PropertySetter", autospec=True)
    def test_mask_unknown_stage(self, mock_setter, mock_logger):
        mock_name = MagicMock(spec=str)
        mock_block = MagicMock(spec=dict)
        mock_block.__contains__.return_value = True

        stage = MagicMock(spec=str)

        result = setproperties._create_property_setter(mock_name, mock_block, stage)

        self.assertEqual(result, mock_setter.return_value)

        mock_block.__contains__.assert_called_with("mask")
        mock_logger.warning.assert_called()
        mock_setter.assert_called_with(mock_name, mock_block)


class Test__process_block(unittest.TestCase):
    """Test the ht.pyfilter.operations.setproperties._process_block."""

    @patch("ht.pyfilter.operations.setproperties._create_property_setter")
    def test_dict(self, mock_create):
        properties = []
        mock_stage = MagicMock(spec=str)
        mock_name = MagicMock(spec=str)

        mock_block = MagicMock(spec=dict)

        setproperties._process_block(properties, mock_stage, mock_name, mock_block)

        self.assertEqual(properties, [mock_create.return_value])

        mock_create.assert_called_with(mock_name, mock_block, mock_stage)

    @patch("ht.pyfilter.operations.setproperties._create_property_setter")
    def test_list(self, mock_create):
        properties = []
        mock_stage = MagicMock(spec=str)
        mock_name = MagicMock(spec=str)

        mock_block = MagicMock(spec=dict)

        setproperties._process_block(properties, mock_stage, mock_name, [mock_block])

        self.assertEqual(properties, [mock_create.return_value])

        mock_create.assert_called_with(mock_name, mock_block, mock_stage)

    @patch("ht.pyfilter.operations.setproperties._create_property_setter")
    def test_noniterable(self, mock_create):
        properties = []
        mock_stage = MagicMock(spec=str)
        mock_name = MagicMock(spec=str)

        mock_block = MagicMock(spec=int)

        setproperties._process_block(properties, mock_stage, mock_name, mock_block)

        self.assertEqual(properties, [])

        mock_create.assert_not_called()


class Test__process_rendertype_block(unittest.TestCase):
    """Test the ht.pyfilter.operations.setproperties._process_rendertype_block."""

    @patch("ht.pyfilter.operations.setproperties._process_block")
    def test_dict(self, mock_process):
        mock_properties = MagicMock(spec=list)
        mock_stage = MagicMock(spec=str)
        mock_rendertype = MagicMock(spec=str)

        mock_name = MagicMock(spec=str)

        block = {}

        property_block = {
            mock_name: block
        }

        setproperties._process_rendertype_block(mock_properties, mock_stage, mock_rendertype, property_block)

        mock_process.assert_called_with(mock_properties, mock_stage, mock_name, {"rendertype": mock_rendertype})

    @patch("ht.pyfilter.operations.setproperties._process_block")
    def test_list(self, mock_process):
        mock_properties = MagicMock(spec=list)
        mock_stage = MagicMock(spec=str)
        mock_rendertype = MagicMock(spec=str)

        mock_name = MagicMock(spec=str)

        block = {}

        property_block = {
            mock_name: [block]
        }

        setproperties._process_rendertype_block(mock_properties, mock_stage, mock_rendertype, property_block)

        mock_process.assert_called_with(mock_properties, mock_stage, mock_name, [{"rendertype": mock_rendertype}])

    def test_error(self):
        mock_properties = MagicMock(spec=list)
        mock_stage = MagicMock(spec=str)
        mock_rendertype = MagicMock(spec=str)

        mock_name = MagicMock(spec=str)

        property_block = {
            mock_name: MagicMock()
        }

        with self.assertRaises(TypeError):
            setproperties._process_rendertype_block(mock_properties, mock_stage, mock_rendertype, property_block)


# =============================================================================

if __name__ == '__main__':
    unittest.main()
