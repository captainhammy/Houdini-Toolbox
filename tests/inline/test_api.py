"""This script is a unit test suite for the inline.py module.

It can be executed directly from the command line, or directly using python or
Hython.

If run with regular Python it will attempt to import the hou module.  You must
have the Houdini environments sourced.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import ctypes
from mock import MagicMock, call, patch
import unittest

# Houdini Toolbox Imports
from ht.inline import api

# Houdini Imports
import hou

# =============================================================================
# CLASSES
# =============================================================================

# TODO: Test global dicts

# Non-Public Functions

class Test__assert_prim_vertex_index(unittest.TestCase):
    """Test ht.inline.api._assert_prim_vertex_index."""

    def test_less_than_0(self):
        mock_prim = MagicMock(spec=hou.Prim)

        with self.assertRaises(IndexError):
            api._assert_prim_vertex_index(mock_prim, -1)

    @patch("ht.inline.api.num_prim_vertices")
    def test_equal(self, mock_num_verts):
        mock_num_verts.return_value = 5

        mock_prim = MagicMock(spec=hou.Prim)

        with self.assertRaises(IndexError):
            api._assert_prim_vertex_index(mock_prim, 5)

    @patch("ht.inline.api.num_prim_vertices")
    def test_greater_than(self, mock_num_verts):
        mock_num_verts.return_value = 5

        mock_prim = MagicMock(spec=hou.Prim)

        with self.assertRaises(IndexError):
            api._assert_prim_vertex_index(mock_prim, 6)

    @patch("ht.inline.api.num_prim_vertices")
    def test_valid(self, mock_num_verts):
        mock_num_verts.return_value = 5

        mock_prim = MagicMock(spec=hou.Prim)

        api._assert_prim_vertex_index(mock_prim, 4)


class Test__build_c_double_array(unittest.TestCase):
    """Test ht.inline.api._build_c_double_array."""

    def test(self):
        values = [float(val) for val in range(5)]
        values.reverse()

        result = api._build_c_double_array(values)

        self.assertEqual(list(result), values)

        expected_type = type((ctypes.c_double * len(values))())
        self.assertTrue(isinstance(result, expected_type))


class Test__build_c_int_array(unittest.TestCase):
    """Test ht.inline.api._build_c_int_array."""

    def test(self):
        values = range(5)
        values.reverse()

        result = api._build_c_int_array(values)

        self.assertEqual(list(result), values)

        expected_type = type((ctypes.c_int * len(values))())
        self.assertTrue(isinstance(result, expected_type))


class Test__build_c_string_array(unittest.TestCase):
    """Test ht.inline.api._build_c_string_array."""

    def test(self):
        values = ["foo", "bar", "test"]

        result = api._build_c_string_array(values)

        self.assertEqual(list(result), values)

        expected_type = type((ctypes.c_char_p * len(values))())
        self.assertTrue(isinstance(result, expected_type))


class Test__clean_string_values(unittest.TestCase):
    """Test ht.inline.api._clean_string_values."""

    def test(self):
        mock_str1 = MagicMock(spec=str)
        mock_str1.__len__.return_value = 1

        mock_str2 = MagicMock(spec=str)
        mock_str2.__len__.return_value = 0

        mock_str3 = MagicMock(spec=str)
        mock_str3.__len__.return_value = 2

        values = [mock_str1, mock_str2, mock_str3]

        result = api._clean_string_values(values)

        self.assertEqual(result, tuple([mock_str1, mock_str3]))


class Test__find_attrib(unittest.TestCase):
    """Test ht.inline.api._find_attrib."""

    def test_vertex(self):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)

        result = api._find_attrib(mock_geometry, hou.attribType.Vertex, mock_name)

        self.assertEqual(result, mock_geometry.findVertexAttrib.return_value)

        mock_geometry.findVertexAttrib.assert_called_with(mock_name)

    def test_point(self):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)

        result = api._find_attrib(mock_geometry, hou.attribType.Point, mock_name)

        self.assertEqual(result, mock_geometry.findPointAttrib.return_value)

        mock_geometry.findPointAttrib.assert_called_with(mock_name)

    def test_prim(self):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)

        result = api._find_attrib(mock_geometry, hou.attribType.Prim, mock_name)

        self.assertEqual(result, mock_geometry.findPrimAttrib.return_value)

        mock_geometry.findPrimAttrib.assert_called_with(mock_name)

    def test_global(self):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)

        result = api._find_attrib(mock_geometry, hou.attribType.Global, mock_name)

        self.assertEqual(result, mock_geometry.findGlobalAttrib.return_value)

        mock_geometry.findGlobalAttrib.assert_called_with(mock_name)

    def test_invalid(self):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)

        with self.assertRaises(ValueError):
            api._find_attrib(mock_geometry, None, mock_name)


class Test__find_group(unittest.TestCase):
    """Test ht.inline.api._find_group."""

    def test_point(self):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)

        result = api._find_group(mock_geometry, 0, mock_name)

        self.assertEqual(result, mock_geometry.findPointGroup.return_value)

        mock_geometry.findPointGroup.assert_called_with(mock_name)

    def test_prim(self):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)

        result = api._find_group(mock_geometry, 1, mock_name)

        self.assertEqual(result, mock_geometry.findPrimGroup.return_value)

        mock_geometry.findPrimGroup.assert_called_with(mock_name)

    def test_edge(self):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)

        result = api._find_group(mock_geometry, 2, mock_name)

        self.assertEqual(result, mock_geometry.findEdgeGroup.return_value)

        mock_geometry.findEdgeGroup.assert_called_with(mock_name)

    def test_invalid(self):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)

        with self.assertRaises(ValueError):
            api._find_group(mock_geometry, None, mock_name)


class Test__geo_details_match(unittest.TestCase):
    """Test ht.inline.api._geo_details_match."""

    def test_match(self):
        mock_geometry1 = MagicMock(spec=hou.Geometry)
        mock_geometry2 = MagicMock(spec=hou.Geometry)

        mock_geometry1._guDetailHandle.return_value._asVoidPointer.return_value = 1
        mock_geometry2._guDetailHandle.return_value._asVoidPointer.return_value = 1

        self.assertTrue(api._geo_details_match(mock_geometry1, mock_geometry2))

        mock_geometry1._guDetailHandle.return_value.destroy.assert_called()
        mock_geometry2._guDetailHandle.return_value.destroy.assert_called()

    def test_no_match(self):
        mock_geometry1 = MagicMock(spec=hou.Geometry)
        mock_geometry2 = MagicMock(spec=hou.Geometry)

        mock_geometry1._guDetailHandle.return_value._asVoidPointer.return_value = 0
        mock_geometry2._guDetailHandle.return_value._asVoidPointer.return_value = 1

        self.assertFalse(api._geo_details_match(mock_geometry1, mock_geometry2))

        mock_geometry1._guDetailHandle.return_value.destroy.assert_called()
        mock_geometry2._guDetailHandle.return_value.destroy.assert_called()


class Test__get_attrib_owner(unittest.TestCase):
    """Test ht.inline.api._get_attrib_owner."""

    def test_in_map(self):
        mock_data_type = MagicMock(spec=hou.attribType)
        mock_dict = MagicMock(spec=dict)

        with patch("ht.inline.api._ATTRIB_TYPE_MAP", mock_dict):
            result = api._get_attrib_owner(mock_data_type)

            self.assertEqual(result, mock_dict.__getitem__.return_value)

            mock_dict.__getitem__.assert_called_with(mock_data_type)

    def test_invalid(self):
        mock_data_type = MagicMock(spec=hou.attribType)

        with patch("ht.inline.api._ATTRIB_TYPE_MAP", {}):
            with self.assertRaises(ValueError):
                api._get_attrib_owner(mock_data_type)


class Test__get_attrib_owner_from_geometry_entity_type(unittest.TestCase):
    """Test ht.inline.api._get_attrib_owner_from_geometry_entity_type."""

    def test_in_map(self):
        mock_entity_type = MagicMock()
        mock_owner_value = MagicMock(spec=int)

        data = {
            mock_entity_type: mock_owner_value
        }

        with patch("ht.inline.api._GEOMETRY_ATTRIB_MAP", data):
            result = api._get_attrib_owner_from_geometry_entity_type(mock_entity_type)

            self.assertEqual(result, mock_owner_value)

    def test_subclass_in_map(self):
        mock_entity_type = hou.Polygon
        mock_parent_type = hou.Prim

        mock_owner_value = MagicMock(spec=int)

        data = {
            mock_parent_type: mock_owner_value
        }

        with patch("ht.inline.api._GEOMETRY_ATTRIB_MAP", data):
            result = api._get_attrib_owner_from_geometry_entity_type(mock_entity_type)

            self.assertEqual(result, mock_owner_value)

    def test_invalid_type(self):
        mock_owner_value = MagicMock(spec=int)

        data = {
            MagicMock: mock_owner_value
        }

        with patch("ht.inline.api._GEOMETRY_ATTRIB_MAP", data):
            with self.assertRaises(ValueError):
                api._get_attrib_owner_from_geometry_entity_type(hou.Vector2)


class Test__get_attrib_owner_from_geometry_type(unittest.TestCase):
    """Test ht.inline.api._get_attrib_owner_from_geometry_type."""

    def test_in_map(self):
        mock_geometry_type = MagicMock(spec=hou.geometryType)
        mock_owner_value = MagicMock(spec=int)

        data = {mock_geometry_type: mock_owner_value}

        with patch("ht.inline.api._GEOMETRY_TYPE_MAP", data):
            result = api._get_attrib_owner_from_geometry_type(mock_geometry_type)

            self.assertEqual(result, mock_owner_value)

    def test_invalid_type(self):
        mock_geometry_type = MagicMock(spec=hou.geometryType)

        data = {}

        with patch("ht.inline.api._GEOMETRY_TYPE_MAP", data):
            with self.assertRaises(ValueError):
                api._get_attrib_owner_from_geometry_type(mock_geometry_type)


class Test__get_attrib_storage(unittest.TestCase):
    """Test ht.inline.api._get_attrib_storage."""

    def test(self):
        mock_data_type = MagicMock(spec=hou.attribData)
        mock_dict = MagicMock(spec=dict)

        with patch("ht.inline.api._ATTRIB_STORAGE_MAP", mock_dict):
            result = api._get_attrib_storage(mock_data_type)

            self.assertEqual(result, mock_dict.__getitem__.return_value)

            mock_dict.__getitem__.assert_called_with(mock_data_type)

    def test_invalid(self):

        mock_data_type = MagicMock(spec=hou.attribData)

        with patch("ht.inline.api._ATTRIB_STORAGE_MAP", {}):
            with self.assertRaises(ValueError):
                api._get_attrib_storage(mock_data_type)


class Test__get_group_attrib_owner(unittest.TestCase):
    """Test ht.inline.api._get_group_attrib_owner."""

    def test(self):
        mock_data_type = MagicMock()
        mock_dict = MagicMock(spec=dict)

        with patch("ht.inline.api._GROUP_ATTRIB_MAP", mock_dict):
            result = api._get_group_attrib_owner(mock_data_type)

            self.assertEqual(result, mock_dict.__getitem__.return_value)

            mock_dict.__getitem__.assert_called_with(type(mock_data_type))

    def test_invalid(self):
        mock_data_type = MagicMock()

        with patch("ht.inline.api._GROUP_ATTRIB_MAP", {}):
            with self.assertRaises(ValueError):
                api._get_group_attrib_owner(mock_data_type)


class Test__get_group_type(unittest.TestCase):
    """Test ht.inline.api._get_group_type."""

    def test(self):
        mock_data_type = MagicMock()
        mock_dict = MagicMock(spec=dict)

        with patch("ht.inline.api._GROUP_TYPE_MAP", mock_dict):
            result = api._get_group_type(mock_data_type)

            self.assertEqual(result, mock_dict.__getitem__.return_value)

            mock_dict.__getitem__.assert_called_with(type(mock_data_type))

    def test_invalid(self):
        mock_data_type = MagicMock()

        with patch("ht.inline.api._GROUP_TYPE_MAP", {}):
            with self.assertRaises(ValueError):
                api._get_group_type(mock_data_type)


class Test__get_nodes_from_paths(unittest.TestCase):
    """Test ht.inline.api._get_nodes_from_paths."""

    @patch("ht.inline.api.hou.node")
    def test(self, mock_hou_node):
        mock_path1 = MagicMock(spec=str)

        mock_path2 = MagicMock(spec=str)
        mock_path2.__len__.return_value = 1

        mock_path3 = MagicMock(spec=str)
        mock_path3.__len__.return_value = 1

        result = api._get_nodes_from_paths([mock_path1, mock_path2, mock_path3])

        self.assertEqual(result, (mock_hou_node.return_value, mock_hou_node.return_value))

        mock_hou_node.assert_has_calls(
            [call(mock_path2), call(mock_path3)]
        )


class Test__get_points_from_list(unittest.TestCase):
    """Test ht.inline.api._get_points_from_list."""

    def test_empty(self):
        mock_geometry = MagicMock(spec=hou.Geometry)

        result = api._get_points_from_list(mock_geometry, [])

        self.assertEqual(result, ())

    def test(self):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_int1 = MagicMock(spec=int)
        mock_int2 = MagicMock(spec=int)

        result = api._get_points_from_list(mock_geometry, [mock_int1, mock_int2])

        self.assertEqual(result, mock_geometry.globPoints.return_value)

        mock_geometry.globPoints.assert_called_with("{} {}".format(mock_int1, mock_int2))


class Test__get_prims_from_list(unittest.TestCase):
    """Test ht.inline.api._get_prims_from_list."""

    def test_empty(self):
        mock_geometry = MagicMock(spec=hou.Geometry)

        result = api._get_prims_from_list(mock_geometry, [])

        self.assertEqual(result, ())

    def test(self):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_int1 = MagicMock(spec=int)
        mock_int2 = MagicMock(spec=int)

        result = api._get_prims_from_list(mock_geometry, [mock_int1, mock_int2])

        self.assertEqual(result, mock_geometry.globPrims.return_value)

        mock_geometry.globPrims.assert_called_with("{} {}".format(mock_int1, mock_int2))

# Functions

class Test_is_rendering(unittest.TestCase):
    """Test ht.inline.api.is_rendering."""

    @patch("ht.inline.api._cpp_methods.isRendering")
    def test(self, mock_rendering):
        result = api.is_rendering()

        self.assertEqual(result, mock_rendering.return_value)


class Test_get_global_variable_names(unittest.TestCase):
    """Test ht.inline.api.get_global_variable_names."""

    @patch("ht.inline.api._clean_string_values")
    @patch("ht.inline.api._cpp_methods.getGlobalVariableNames")
    def test_default_arg(self, mock_get_globals, mock_clean):
        result = api.get_global_variable_names()

        self.assertEqual(result, mock_clean.return_value)

        mock_get_globals.assert_called_with(False)
        mock_clean.assert_called_with(mock_get_globals.return_value)

    @patch("ht.inline.api._clean_string_values")
    @patch("ht.inline.api._cpp_methods.getGlobalVariableNames")
    def test(self, mock_get_globals, mock_clean):
        mock_dirty = MagicMock(spec=bool)

        result = api.get_global_variable_names(mock_dirty)

        self.assertEqual(result, mock_clean.return_value)

        mock_get_globals.assert_called_with(mock_dirty)
        mock_clean.assert_called_with(mock_get_globals.return_value)


class Test_get_variable_names(unittest.TestCase):
    """Test ht.inline.api.get_variable_names."""

    @patch("ht.inline.api._clean_string_values")
    @patch("ht.inline.api._cpp_methods.getVariableNames")
    def test_default_arg(self, mock_get_globals, mock_clean):
        result = api.get_variable_names()

        self.assertEqual(result, mock_clean.return_value)

        mock_get_globals.assert_called_with(False)
        mock_clean.assert_called_with(mock_get_globals.return_value)

    @patch("ht.inline.api._clean_string_values")
    @patch("ht.inline.api._cpp_methods.getVariableNames")
    def test(self, mock_get_globals, mock_clean):
        mock_dirty = MagicMock(spec=bool)

        result = api.get_variable_names(mock_dirty)

        self.assertEqual(result, mock_clean.return_value)

        mock_get_globals.assert_called_with(mock_dirty)
        mock_clean.assert_called_with(mock_get_globals.return_value)


class Test_get_variable_value(unittest.TestCase):
    """Test ht.inline.api.get_variable_value."""

    @patch("ht.inline.api._cpp_methods.getVariableValue")
    @patch("ht.inline.api.get_variable_names", return_value=())
    def test_not_in_list(self, mock_get_names, mock_get_var):
        mock_name = MagicMock(spec=str)

        result = api.get_variable_value(mock_name)

        self.assertIsNone(result)

        mock_get_var.assert_not_called()

    @patch("ht.inline.api.ast.literal_eval")
    @patch("ht.inline.api._cpp_methods.getVariableValue")
    @patch("ht.inline.api.get_variable_names")
    def test_syntax_error(self, mock_get_names, mock_get_var, mock_eval):
        mock_name = MagicMock(spec=str)

        mock_get_names.return_value = (mock_name, )

        mock_eval.side_effect = SyntaxError

        result = api.get_variable_value(mock_name)

        self.assertEqual(result, mock_get_var.return_value)

        mock_get_var.assert_called_with(mock_name)
        mock_eval.assert_called_with(mock_get_var.return_value)

    @patch("ht.inline.api.ast.literal_eval")
    @patch("ht.inline.api._cpp_methods.getVariableValue")
    @patch("ht.inline.api.get_variable_names")
    def test_value_error(self, mock_get_names, mock_get_var, mock_eval):
        mock_name = MagicMock(spec=str)

        mock_get_names.return_value = (mock_name, )

        mock_eval.side_effect = ValueError

        result = api.get_variable_value(mock_name)

        self.assertEqual(result, mock_get_var.return_value)

        mock_get_var.assert_called_with(mock_name)
        mock_eval.assert_called_with(mock_get_var.return_value)

    @patch("ht.inline.api.ast.literal_eval")
    @patch("ht.inline.api._cpp_methods.getVariableValue")
    @patch("ht.inline.api.get_variable_names")
    def test(self, mock_get_names, mock_get_var, mock_eval):
        mock_name = MagicMock(spec=str)

        mock_get_names.return_value = (mock_name, )

        result = api.get_variable_value(mock_name)

        self.assertEqual(result, mock_eval.return_value)

        mock_get_var.assert_called_with(mock_name)
        mock_eval.assert_called_with(mock_get_var.return_value)


class Test_set_variable(unittest.TestCase):
    """Test ht.inline.api.set_variable."""

    @patch("ht.inline.api._cpp_methods.setVariable")
    def test_default_arg(self, mock_set):
        mock_name = MagicMock(spec=str)
        mock_value = MagicMock()

        api.set_variable(mock_name, mock_value)

        mock_set.assert_called_with(mock_name, str(mock_value), False)

    @patch("ht.inline.api._cpp_methods.setVariable")
    def test(self, mock_set):
        mock_name = MagicMock(spec=str)
        mock_value = MagicMock()
        mock_global = MagicMock(spec=bool)

        api.set_variable(mock_name, mock_value, mock_global)

        mock_set.assert_called_with(mock_name, str(mock_value), mock_global)


class Test_unset_variable(unittest.TestCase):
    """Test ht.inline.api.unset_variable."""

    @patch("ht.inline.api._cpp_methods.unsetVariable")
    def test(self, mock_unset):
        mock_name = MagicMock(spec=str)

        api.unset_variable(mock_name)

        mock_unset.assert_called_with(mock_name)


class Test_emit_var_change(unittest.TestCase):
    """Test ht.inline.api.emit_var_change."""

    @patch("ht.inline.api._cpp_methods.emitVarChange")
    def test(self, mock_varchange):
        api.emit_var_change()

        mock_varchange.assert_called()


class Test_expand_range(unittest.TestCase):
    """Test ht.inline.api.expand_range."""

    @patch("ht.inline.api._cpp_methods.expandRange")
    def test(self, mock_expand):
        mock_pattern = MagicMock(spec=str)

        result = api.expand_range(mock_pattern)

        self.assertEqual(result, tuple(mock_expand.return_value))

        mock_expand.assert_called_with(mock_pattern)


class Test_is_geometry_read_only(unittest.TestCase):
    """Test ht.inline.api.is_geometry_read_only."""

    def test(self):
        mock_handle = MagicMock(spec=hou._GUDetailHandle)

        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_geometry._guDetailHandle.return_value = mock_handle

        result = api.is_geometry_read_only(mock_geometry)

        self.assertEqual(result, mock_handle.isReadOnly.return_value)

        mock_handle.destroy.assert_called()


class Test_num_points(unittest.TestCase):
    """Test ht.inline.api.num_points."""

    def test(self):
        mock_geometry = MagicMock(spec=hou.Geometry)

        result = api.num_points(mock_geometry)

        self.assertEqual(result, mock_geometry.intrinsicValue.return_value)
        mock_geometry.intrinsicValue.assert_called_with("pointcount")


class Test_num_prims(unittest.TestCase):
    """Test ht.inline.api.num_prims."""

    def test(self):
        mock_geometry = MagicMock(spec=hou.Geometry)

        result = api.num_prims(mock_geometry)

        self.assertEqual(result, mock_geometry.intrinsicValue.return_value)
        mock_geometry.intrinsicValue.assert_called_with("primitivecount")


class Test_num_vertices(unittest.TestCase):
    """Test ht.inline.api.num_vertices."""

    def test(self):
        mock_geometry = MagicMock(spec=hou.Geometry)

        result = api.num_vertices(mock_geometry)

        self.assertEqual(result, mock_geometry.intrinsicValue.return_value)
        mock_geometry.intrinsicValue.assert_called_with("vertexcount")


class Test_num_prim_vertices(unittest.TestCase):
    """Test ht.inline.api.num_prim_vertices."""

    def test(self):
        mock_prim = MagicMock(spec=hou.Prim)

        result = api.num_prim_vertices(mock_prim)

        self.assertEqual(result, mock_prim.intrinsicValue.return_value)
        mock_prim.intrinsicValue.assert_called_with("vertexcount")


class Test_pack_geometry(unittest.TestCase):
    """Test ht.inline.api.pack_geometry."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_geo_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_source = MagicMock(spec=hou.Geometry)

        with self.assertRaises(hou.GeometryPermissionError):
            api.pack_geometry(mock_geometry, mock_source)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.is_geometry_read_only", side_effect=(False, True))
    def test_source_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_source = MagicMock(spec=hou.Geometry)

        with self.assertRaises(hou.GeometryPermissionError):
            api.pack_geometry(mock_geometry, mock_source)

        mock_read_only.assert_has_calls(
            [call(mock_geometry), call(mock_source)]
        )

    @patch("ht.inline.api._cpp_methods.packGeometry")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_pack):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_source = MagicMock(spec=hou.Geometry)

        result = api.pack_geometry(mock_geometry, mock_source)
        self.assertEqual(result, mock_geometry.iterPrims.return_value.__getitem__.return_value)

        mock_geometry.iterPrims.return_value.__getitem__.assert_called_with(-1)

        mock_read_only.assert_has_calls(
            [call(mock_geometry), call(mock_source)]
        )

        mock_pack.assert_called_with(mock_source, mock_geometry)


class Test_sort_geometry_by_attribute(unittest.TestCase):
    """Test ht.inline.api.sort_geometry_by_attribute."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_attribute = MagicMock(spec=hou.Attrib)
        mock_index = MagicMock(spec=int)

        with self.assertRaises(hou.GeometryPermissionError):
            api.sort_geometry_by_attribute(mock_geometry, mock_attribute, mock_index)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_index_out_of_range(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_attribute = MagicMock(spec=hou.Attrib)
        mock_attribute.size.return_value = 5

        with self.assertRaises(IndexError):
            api.sort_geometry_by_attribute(mock_geometry, mock_attribute, 10)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_global_attrib(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_attribute = MagicMock(spec=hou.Attrib)
        mock_attribute.size.return_value = 5
        mock_attribute.type.return_value = hou.attribType.Global

        with self.assertRaises(ValueError):
            api.sort_geometry_by_attribute(mock_geometry, mock_attribute, 1)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api._cpp_methods.sortGeometryByAttribute")
    @patch("ht.inline.api._get_attrib_owner")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_default_arg(self, mock_read_only, mock_get_owner, mock_sort):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_attrib_type = MagicMock()

        mock_attribute = MagicMock(spec=hou.Attrib)
        mock_attribute.size.return_value = 5
        mock_attribute.type.return_value = mock_attrib_type

        api.sort_geometry_by_attribute(mock_geometry, mock_attribute, 1)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(mock_attrib_type)

        mock_sort.assert_called_with(
            mock_geometry,
            mock_get_owner.return_value,
            mock_attribute.name.return_value,
            1,
            False
        )

    @patch("ht.inline.api._cpp_methods.sortGeometryByAttribute")
    @patch("ht.inline.api._get_attrib_owner")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_get_owner, mock_sort):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_attrib_type = MagicMock()

        mock_attribute = MagicMock(spec=hou.Attrib)
        mock_attribute.size.return_value = 5
        mock_attribute.type.return_value = mock_attrib_type

        mock_reverse = MagicMock(spec=bool)

        api.sort_geometry_by_attribute(mock_geometry, mock_attribute, 1, mock_reverse)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(mock_attrib_type)

        mock_sort.assert_called_with(
            mock_geometry,
            mock_get_owner.return_value,
            mock_attribute.name.return_value,
            1,
            mock_reverse
        )


class Test_sort_geometry_along_axis(unittest.TestCase):
    """Test ht.inline.api.sort_geometry_along_axis."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_geometry_type = MagicMock(spec=hou.geometryType)
        mock_axis = MagicMock(spec=int)

        with self.assertRaises(hou.GeometryPermissionError):
            api.sort_geometry_along_axis(mock_geometry, mock_geometry_type, mock_axis)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_index_out_of_range(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_geometry_type = MagicMock(spec=hou.geometryType)

        with self.assertRaises(ValueError):
            api.sort_geometry_along_axis(mock_geometry, mock_geometry_type, 4)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_invalid_type(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geo_type = hou.geometryType.Edges
        index = 1

        with self.assertRaises(ValueError):
            api.sort_geometry_along_axis(mock_geometry,geo_type, index)

    @patch("ht.inline.api._cpp_methods.sortGeometryAlongAxis")
    @patch("ht.inline.api._get_attrib_owner_from_geometry_type")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_points(self, mock_read_only, mock_get_owner, mock_sort):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geo_type = hou.geometryType.Points
        index = 1

        api.sort_geometry_along_axis(mock_geometry,geo_type, index)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geo_type)

        mock_sort.assert_called_with(mock_geometry, mock_get_owner.return_value, index)

    @patch("ht.inline.api._cpp_methods.sortGeometryAlongAxis")
    @patch("ht.inline.api._get_attrib_owner_from_geometry_type")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_prims(self, mock_read_only, mock_get_owner, mock_sort):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geo_type = hou.geometryType.Primitives
        index = 1

        api.sort_geometry_along_axis(mock_geometry,geo_type, index)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geo_type)

        mock_sort.assert_called_with(mock_geometry, mock_get_owner.return_value, index)


class Test_sort_geometry_by_values(unittest.TestCase):
    """Test ht.inline.api.sort_geometry_by_values."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_geometry_type = MagicMock(spec=hou.geometryType)
        mock_values = MagicMock(spec=list)

        with self.assertRaises(hou.GeometryPermissionError):
            api.sort_geometry_by_values(mock_geometry, mock_geometry_type, mock_values)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.num_points", return_value=5)
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_points_mismatch(self, mock_read_only, mock_num_points):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Points

        mock_values = MagicMock(spec=list)
        mock_values.__len__.return_value = 4

        with self.assertRaises(hou.OperationFailed):
            api.sort_geometry_by_values(mock_geometry, geometry_type, mock_values)

        mock_read_only.assert_called_with(mock_geometry)

        mock_num_points.assert_called_with(mock_geometry)

    @patch("ht.inline.api._cpp_methods.sortGeometryByValues")
    @patch("ht.inline.api._build_c_double_array")
    @patch("ht.inline.api._get_attrib_owner_from_geometry_type")
    @patch("ht.inline.api.num_points")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_points(self, mock_read_only, mock_num_points, mock_get_owner, mock_build, mock_sort):
        size = 5

        mock_num_points.return_value = size

        mock_geometry = MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Points

        mock_values = MagicMock(spec=list)
        mock_values.__len__.return_value = size

        api.sort_geometry_by_values(mock_geometry, geometry_type, mock_values)

        mock_read_only.assert_called_with(mock_geometry)

        mock_num_points.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geometry_type)

        mock_build.assert_called_with(mock_values)

        mock_sort.assert_called_with(mock_geometry, mock_get_owner.return_value, mock_build.return_value)

    @patch("ht.inline.api.num_prims", return_value=5)
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_prims_mismatch(self, mock_read_only, mock_num_prims):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Primitives

        mock_values = MagicMock(spec=list)
        mock_values.__len__.return_value = 4

        with self.assertRaises(hou.OperationFailed):
            api.sort_geometry_by_values(mock_geometry, geometry_type, mock_values)

        mock_read_only.assert_called_with(mock_geometry)

        mock_num_prims.assert_called_with(mock_geometry)

    @patch("ht.inline.api._cpp_methods.sortGeometryByValues")
    @patch("ht.inline.api._build_c_double_array")
    @patch("ht.inline.api._get_attrib_owner_from_geometry_type")
    @patch("ht.inline.api.num_prims")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_prims(self, mock_read_only, mock_num_prims, mock_get_owner, mock_build, mock_sort):
        size = 5

        mock_num_prims.return_value = size

        mock_geometry = MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Primitives

        mock_values = MagicMock(spec=list)
        mock_values.__len__.return_value = size

        api.sort_geometry_by_values(mock_geometry, geometry_type, mock_values)

        mock_read_only.assert_called_with(mock_geometry)

        mock_num_prims.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geometry_type)

        mock_build.assert_called_with(mock_values)

        mock_sort.assert_called_with(mock_geometry, mock_get_owner.return_value, mock_build.return_value)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_invalid(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Edges

        mock_values = MagicMock(spec=list)

        with self.assertRaises(ValueError):
            api.sort_geometry_by_values(mock_geometry, geometry_type, mock_values)

        mock_read_only.assert_called_with(mock_geometry)


class Test_sort_geometry_randomly(unittest.TestCase):
    """Test ht.inline.api.sort_geometry_randomly."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geometry_type = MagicMock(spec=hou.geometryType)
        mock_seed = MagicMock(spec=int)

        with self.assertRaises(hou.GeometryPermissionError):
            api.sort_geometry_randomly(mock_geometry, geometry_type, mock_seed)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_invalid_seed_type(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geometry_type = MagicMock(spec=hou.geometryType)
        mock_seed = MagicMock(spec=str)

        with self.assertRaises(TypeError):
            api.sort_geometry_randomly(mock_geometry, geometry_type, mock_seed)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_invalid_geometry_type(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Edges

        mock_seed = MagicMock(spec=int)

        with self.assertRaises(ValueError):
            api.sort_geometry_randomly(mock_geometry, geometry_type, mock_seed)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api._cpp_methods.sortGeometryRandomly")
    @patch("ht.inline.api._get_attrib_owner_from_geometry_type")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_points_int(self, mock_read_only, mock_get_owner, mock_sort):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Points
        mock_seed = MagicMock(spec=int)

        api.sort_geometry_randomly(mock_geometry, geometry_type, mock_seed)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geometry_type)

        mock_sort.assert_called_with(mock_geometry, mock_get_owner.return_value, mock_seed)

    @patch("ht.inline.api._cpp_methods.sortGeometryRandomly")
    @patch("ht.inline.api._get_attrib_owner_from_geometry_type")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_prims_float(self, mock_read_only, mock_get_owner, mock_sort):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Primitives
        mock_seed = MagicMock(spec=float)

        api.sort_geometry_randomly(mock_geometry, geometry_type, mock_seed)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geometry_type)

        mock_sort.assert_called_with(mock_geometry, mock_get_owner.return_value, mock_seed)


class Test_shift_geometry_elements(unittest.TestCase):
    """Test ht.inline.api.shift_geometry_elements."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geometry_type = MagicMock(spec=hou.geometryType)
        mock_offset = MagicMock(spec=int)

        with self.assertRaises(hou.GeometryPermissionError):
            api.shift_geometry_elements(mock_geometry, geometry_type, mock_offset)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_invalid_offset_type(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geometry_type = MagicMock(spec=hou.geometryType)
        mock_offset = MagicMock(spec=float)

        with self.assertRaises(TypeError):
            api.shift_geometry_elements(mock_geometry, geometry_type, mock_offset)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_invalid_geometry_type(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Edges
        mock_offset = MagicMock(spec=int)

        with self.assertRaises(ValueError):
            api.shift_geometry_elements(mock_geometry, geometry_type, mock_offset)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api._cpp_methods.shiftGeometry")
    @patch("ht.inline.api._get_attrib_owner_from_geometry_type")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_points(self, mock_read_only, mock_get_owner, mock_shift):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Points
        mock_offset = MagicMock(spec=int)

        api.shift_geometry_elements(mock_geometry, geometry_type, mock_offset)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geometry_type)

        mock_shift.assert_called_with(mock_geometry, mock_get_owner.return_value, mock_offset)

    @patch("ht.inline.api._cpp_methods.shiftGeometry")
    @patch("ht.inline.api._get_attrib_owner_from_geometry_type")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_prims(self, mock_read_only, mock_get_owner, mock_shift):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Primitives
        mock_offset = MagicMock(spec=int)

        api.shift_geometry_elements(mock_geometry, geometry_type, mock_offset)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geometry_type)

        mock_shift.assert_called_with(mock_geometry, mock_get_owner.return_value, mock_offset)


class Test_reverse_sort_geometry(unittest.TestCase):
    """Test ht.inline.api.reverse_sort_geometry."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geometry_type = MagicMock(spec=hou.geometryType)

        with self.assertRaises(hou.GeometryPermissionError):
            api.reverse_sort_geometry(mock_geometry, geometry_type)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_invalid_geometry_type(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Edges

        with self.assertRaises(ValueError):
            api.reverse_sort_geometry(mock_geometry, geometry_type)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api._cpp_methods.reverseSortGeometry")
    @patch("ht.inline.api._get_attrib_owner_from_geometry_type")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_points(self, mock_read_only, mock_get_owner, mock_reverse):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Points

        api.reverse_sort_geometry(mock_geometry, geometry_type)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geometry_type)

        mock_reverse.assert_called_with(mock_geometry, mock_get_owner.return_value)

    @patch("ht.inline.api._cpp_methods.reverseSortGeometry")
    @patch("ht.inline.api._get_attrib_owner_from_geometry_type")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_prims(self, mock_read_only, mock_get_owner, mock_reverse):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Primitives

        api.reverse_sort_geometry(mock_geometry, geometry_type)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geometry_type)

        mock_reverse.assert_called_with(mock_geometry, mock_get_owner.return_value)


class Test_sort_geometry_by_proximity_to_position(unittest.TestCase):
    """Test ht.inline.api.sort_geometry_by_proximity_to_position."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geometry_type = MagicMock(spec=hou.geometryType)
        mock_pos = MagicMock(spec=hou.Vector3)

        with self.assertRaises(hou.GeometryPermissionError):
            api.sort_geometry_by_proximity_to_position(mock_geometry, geometry_type, mock_pos)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_invalid_geometry_type(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Edges
        mock_pos = MagicMock(spec=hou.Vector3)

        with self.assertRaises(ValueError):
            api.sort_geometry_by_proximity_to_position(mock_geometry, geometry_type, mock_pos)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api._cpp_methods.sortGeometryByProximity")
    @patch("ht.inline.api._get_attrib_owner_from_geometry_type")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_points(self, mock_read_only, mock_get_owner, mock_proximity):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Points
        mock_pos = MagicMock(spec=hou.Vector3)

        api.sort_geometry_by_proximity_to_position(mock_geometry, geometry_type, mock_pos)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geometry_type)

        mock_proximity.assert_called_with(mock_geometry, mock_get_owner.return_value, mock_pos)

    @patch("ht.inline.api._cpp_methods.sortGeometryByProximity")
    @patch("ht.inline.api._get_attrib_owner_from_geometry_type")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_prims(self, mock_read_only, mock_get_owner, mock_proximity):
        mock_geometry = MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Primitives
        mock_pos = MagicMock(spec=hou.Vector3)

        api.sort_geometry_by_proximity_to_position(mock_geometry, geometry_type, mock_pos)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geometry_type)

        mock_proximity.assert_called_with(mock_geometry, mock_get_owner.return_value, mock_pos)


class Test_sort_geometry_by_vertex_order(unittest.TestCase):
    """Test ht.inline.api.sort_geometry_by_vertex_order."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        with self.assertRaises(hou.GeometryPermissionError):
            api.sort_geometry_by_vertex_order(mock_geometry)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api._cpp_methods.sortGeometryByVertexOrder")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_invalid_geometry_type(self, mock_read_only, mock_sort):
        mock_geometry = MagicMock(spec=hou.Geometry)

        api.sort_geometry_by_vertex_order(mock_geometry)

        mock_read_only.assert_called_with(mock_geometry)
        mock_sort.assert_called_with(mock_geometry)


class Test_sort_geometry_by_expression(unittest.TestCase):
    """Test ht.inline.api.sort_geometry_by_expression."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_geometry_type = MagicMock(spec=hou.geometryType.Points)
        mock_expression = MagicMock(spec=str)

        with self.assertRaises(hou.GeometryPermissionError):
            api.sort_geometry_by_expression(mock_geometry, mock_geometry_type, mock_expression)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.sort_geometry_by_values")
    @patch("ht.inline.api.hou.hscriptExpression")
    @patch("ht.inline.api.hou.pwd")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_points(self, mock_read_only, mock_pwd, mock_hscript, mock_sort):
        mock_pt1 = MagicMock(spec=hou.Point)
        mock_pt2 = MagicMock(spec=hou.Point)

        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_geometry.points.return_value = (mock_pt1, mock_pt2)

        geometry_type = hou.geometryType.Points
        mock_expression = MagicMock(spec=str)

        mock_sopnode = MagicMock(spec=hou.SopNode)
        mock_pwd.return_value = mock_sopnode

        api.sort_geometry_by_expression(mock_geometry, geometry_type, mock_expression)

        mock_read_only.assert_called_with(mock_geometry)

        mock_sopnode.setCurPoint.assert_has_calls(
            [call(mock_pt1), call(mock_pt2)]
        )

        mock_hscript.assert_called_with(mock_expression)
        self.assertEqual(mock_hscript.call_count, 2)

        mock_sort.assert_called_with(mock_geometry, geometry_type, [mock_hscript.return_value, mock_hscript.return_value])

    @patch("ht.inline.api.sort_geometry_by_values")
    @patch("ht.inline.api.hou.hscriptExpression")
    @patch("ht.inline.api.hou.pwd")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_prims(self, mock_read_only, mock_pwd, mock_hscript, mock_sort):
        mock_pr1 = MagicMock(spec=hou.Prim)
        mock_pr2 = MagicMock(spec=hou.Prim)

        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_geometry.prims.return_value = (mock_pr1, mock_pr2)

        geometry_type = hou.geometryType.Primitives
        mock_expression = MagicMock(spec=str)

        mock_sopnode = MagicMock(spec=hou.SopNode)
        mock_pwd.return_value = mock_sopnode

        api.sort_geometry_by_expression(mock_geometry, geometry_type, mock_expression)

        mock_read_only.assert_called_with(mock_geometry)

        mock_sopnode.setCurPrim.assert_has_calls(
            [call(mock_pr1), call(mock_pr2)]
        )

        mock_hscript.assert_called_with(mock_expression)
        self.assertEqual(mock_hscript.call_count, 2)

        mock_sort.assert_called_with(mock_geometry, geometry_type, [mock_hscript.return_value, mock_hscript.return_value])

    @patch("ht.inline.api.hou.pwd")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_invalid_type(self, mock_read_only, mock_pwd):
        mock_geometry = MagicMock(spec=hou.Geometry)

        geometry_type = hou.geometryType.Edges
        mock_expression = MagicMock(spec=str)

        mock_sopnode = MagicMock(spec=hou.SopNode)
        mock_pwd.return_value = mock_sopnode

        with self.assertRaises(ValueError):
            api.sort_geometry_by_expression(mock_geometry, geometry_type, mock_expression)

        mock_read_only.assert_called_with(mock_geometry)


class Test_create_point_at_position(unittest.TestCase):
    """Test ht.inline.api.create_point_at_position."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_pos = MagicMock(spec=hou.Vector3)

        with self.assertRaises(hou.GeometryPermissionError):
            api.create_point_at_position(mock_geometry, mock_pos)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api._cpp_methods.createPointAtPosition")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_create):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_pos = MagicMock(spec=hou.Vector3)

        result = api.create_point_at_position(mock_geometry, mock_pos)

        self.assertEqual(result, mock_geometry.iterPoints.return_value.__getitem__.return_value)

        mock_read_only.assert_called_with(mock_geometry)

        mock_create.assert_called_with(mock_geometry, mock_pos)

        mock_geometry.iterPoints.return_value.__getitem__.assert_called_with(-1)


class Test_create_n_points(unittest.TestCase):
    """Test ht.inline.api.create_n_points."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_npoints = MagicMock(spec=int)

        with self.assertRaises(hou.GeometryPermissionError):
            api.create_n_points(mock_geometry, mock_npoints)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_n_0(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        npoints = 0

        with self.assertRaises(ValueError):
            api.create_n_points(mock_geometry, npoints)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_n_negative(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        npoints = -1

        with self.assertRaises(ValueError):
            api.create_n_points(mock_geometry, npoints)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api._cpp_methods.createNPoints")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_create):
        mock_geometry = MagicMock(spec=hou.Geometry)
        npoints = 10

        result = api.create_n_points(mock_geometry, npoints)

        self.assertEqual(result, tuple(mock_geometry.points.return_value.__getitem__.return_value))

        mock_read_only.assert_called_with(mock_geometry)

        mock_create.assert_called_with(mock_geometry, npoints)

        mock_geometry.points.return_value.__getitem__.assert_called_with(slice(-npoints, None, None))


class Test_merge_point_group(unittest.TestCase):
    """Test ht.inline.api.merge_point_group."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_group = MagicMock(spec=hou.PointGroup)

        with self.assertRaises(hou.GeometryPermissionError):
            api.merge_point_group(mock_geometry, mock_group)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_not_point_group(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_group = MagicMock(spec=hou.PrimGroup)

        with self.assertRaises(ValueError):
            api.merge_point_group(mock_geometry, mock_group)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api._cpp_methods.mergePointGroup")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_merge):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_group = MagicMock(spec=hou.PointGroup)

        api.merge_point_group(mock_geometry, mock_group)

        mock_read_only.assert_called_with(mock_geometry)
        mock_merge.assert_called_with(mock_geometry, mock_group.geometry.return_value, mock_group.name.return_value)


class Test_merge_points(unittest.TestCase):
    """Test ht.inline.api.merge_points."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_points = MagicMock(spec=list)

        with self.assertRaises(hou.GeometryPermissionError):
            api.merge_points(mock_geometry, mock_points)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api._cpp_methods.mergePoints")
    @patch("ht.inline.api._build_c_int_array")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_build, mock_merge):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_pt1 = MagicMock(spec=hou.Point)
        mock_pt2 = MagicMock(spec=hou.Point)

        points = [mock_pt1, mock_pt2]

        api.merge_points(mock_geometry, points)

        mock_read_only.assert_called_with(mock_geometry)

        mock_build.assert_called_with([mock_pt1.number.return_value, mock_pt2.number.return_value])

        mock_merge.assert_called_with(mock_geometry, mock_pt1.geometry.return_value, mock_build.return_value, len(mock_build.return_value))


class Test_merge_prim_group(unittest.TestCase):
    """Test ht.inline.api.merge_prim_group."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_group = MagicMock(spec=hou.PrimGroup)

        with self.assertRaises(hou.GeometryPermissionError):
            api.merge_prim_group(mock_geometry, mock_group)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_not_prim_group(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_group = MagicMock(spec=hou.PointGroup)

        with self.assertRaises(ValueError):
            api.merge_prim_group(mock_geometry, mock_group)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api._cpp_methods.mergePrimGroup")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_merge):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_group = MagicMock(spec=hou.PrimGroup)

        api.merge_prim_group(mock_geometry, mock_group)

        mock_read_only.assert_called_with(mock_geometry)
        mock_merge.assert_called_with(mock_geometry, mock_group.geometry.return_value, mock_group.name.return_value)


class Test_merge_prims(unittest.TestCase):
    """Test ht.inline.api.merge_prims."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_prims = MagicMock(spec=list)

        with self.assertRaises(hou.GeometryPermissionError):
            api.merge_prims(mock_geometry, mock_prims)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api._cpp_methods.mergePrims")
    @patch("ht.inline.api._build_c_int_array")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_build, mock_merge):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_pr1 = MagicMock(spec=hou.Point)
        mock_pr2 = MagicMock(spec=hou.Point)

        points = [mock_pr1, mock_pr2]

        api.merge_prims(mock_geometry, points)

        mock_read_only.assert_called_with(mock_geometry)

        mock_build.assert_called_with([mock_pr1.number.return_value, mock_pr2.number.return_value])

        mock_merge.assert_called_with(mock_geometry, mock_pr1.geometry.return_value, mock_build.return_value, len(mock_build.return_value))


class Test_copy_attribute_values(unittest.TestCase):
    """Test ht.inline.api.copy_attribute_values."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_vertex_read_only(self, mock_read_only):
        mock_source = MagicMock(spec=hou.Vertex)
        mock_attribs = MagicMock(spec=list)

        mock_target = MagicMock(spec=hou.Vertex)

        mock_target_geo = MagicMock(spec=hou.Geometry)
        mock_target.geometry.return_value = mock_target_geo

        with self.assertRaises(hou.GeometryPermissionError):
            api.copy_attribute_values(mock_source, mock_attribs, mock_target)

        mock_target.linearNumber.assert_called()
        mock_read_only.assert_called_with(mock_target_geo)

    @patch("ht.inline.api._cpp_methods.copyAttributeValues")
    @patch("ht.inline.api._get_attrib_owner")
    @patch("ht.inline.api._build_c_string_array")
    @patch("ht.inline.api._get_attrib_owner_from_geometry_entity_type")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_vertex(self, mock_read_only, mock_owner_from_type, mock_build, mock_get_owner, mock_copy):

        mock_source_node = MagicMock(spec=hou.SopNode)

        mock_source_geo = MagicMock(spec=hou.Geometry)
        mock_source_geo.sopNode.return_value = mock_source_node

        mock_source = MagicMock(spec=hou.Vertex)
        mock_source.geometry.return_value = mock_source_geo

        mock_attrib1 = MagicMock(spec=hou.Attrib)
        mock_attrib1.geometry.return_value = MagicMock()

        mock_attrib2 = MagicMock(spec=hou.Attrib)
        mock_attrib2.geometry.return_value.sopNode.return_value = mock_source_node

        mock_attrib3 = MagicMock(spec=hou.Attrib)
        mock_attrib3.geometry.return_value.sopNode.return_value = mock_source_node

        attribs = [mock_attrib1, mock_attrib2, mock_attrib3]

        mock_target_geo = MagicMock(spec=hou.Geometry)

        mock_target = MagicMock(spec=hou.Vertex)
        mock_target.geometry.return_value = mock_target_geo

        mock_target_owner = MagicMock(spec=int)
        mock_source_owner = MagicMock(spec=int)

        mock_get_owner.side_effect = (mock_source_owner, mock_source_owner, MagicMock(spec=int))

        mock_owner_from_type.side_effect = (mock_target_owner, mock_source_owner)

        api.copy_attribute_values(mock_source, attribs, mock_target)

        mock_target.linearNumber.assert_called()
        mock_read_only.assert_called_with(mock_target_geo)

        mock_owner_from_type.assert_has_calls(
            [call(type(mock_target)), call(type(mock_source))]
        )

        mock_get_owner.assert_has_calls(
            [call(mock_attrib1.type.return_value), call(mock_attrib2.type.return_value), call(mock_attrib3.type.return_value)]
        )

        mock_build.assert_called_with([mock_attrib2.name.return_value])

        mock_copy.assert_called_with(
            mock_target_geo,
            mock_target_owner,
            mock_target.linearNumber.return_value,
            mock_source.geometry.return_value,
            mock_source_owner,
            mock_source.linearNumber.return_value,
            mock_build.return_value,
            len(mock_build.return_value)
        )

    @patch("ht.inline.api._cpp_methods.copyAttributeValues")
    @patch("ht.inline.api._get_attrib_owner")
    @patch("ht.inline.api._build_c_string_array")
    @patch("ht.inline.api._get_attrib_owner_from_geometry_entity_type")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_point(self, mock_read_only, mock_owner_from_type, mock_build, mock_get_owner, mock_copy):

        mock_source_node = MagicMock(spec=hou.SopNode)

        mock_source_geo = MagicMock(spec=hou.Geometry)
        mock_source_geo.sopNode.return_value = mock_source_node

        mock_source = MagicMock(spec=hou.Point)
        mock_source.geometry.return_value = mock_source_geo

        mock_attrib1 = MagicMock(spec=hou.Attrib)
        mock_attrib1.geometry.return_value = MagicMock()

        mock_attrib2 = MagicMock(spec=hou.Attrib)
        mock_attrib2.geometry.return_value.sopNode.return_value = mock_source_node

        mock_attrib3 = MagicMock(spec=hou.Attrib)
        mock_attrib3.geometry.return_value.sopNode.return_value = mock_source_node

        attribs = [mock_attrib1, mock_attrib2, mock_attrib3]

        mock_target_geo = MagicMock(spec=hou.Geometry)

        mock_target = MagicMock(spec=hou.Point)
        mock_target.geometry.return_value = mock_target_geo

        mock_target_owner = MagicMock(spec=int)
        mock_source_owner = MagicMock(spec=int)

        mock_get_owner.side_effect = (mock_source_owner, mock_source_owner, MagicMock(spec=int))

        mock_owner_from_type.side_effect = (mock_target_owner, mock_source_owner)

        api.copy_attribute_values(mock_source, attribs, mock_target)

        mock_target.number.assert_called()
        mock_read_only.assert_called_with(mock_target_geo)

        mock_owner_from_type.assert_has_calls(
            [call(type(mock_target)), call(type(mock_source))]
        )

        mock_get_owner.assert_has_calls(
            [call(mock_attrib1.type.return_value), call(mock_attrib2.type.return_value), call(mock_attrib3.type.return_value)]
        )

        mock_build.assert_called_with([mock_attrib2.name.return_value])

        mock_copy.assert_called_with(
            mock_target_geo,
            mock_target_owner,
            mock_target.number.return_value,
            mock_source.geometry.return_value,
            mock_source_owner,
            mock_source.number.return_value,
            mock_build.return_value,
            len(mock_build.return_value)
        )

    @patch("ht.inline.api._cpp_methods.copyAttributeValues")
    @patch("ht.inline.api._get_attrib_owner")
    @patch("ht.inline.api._build_c_string_array")
    @patch("ht.inline.api._get_attrib_owner_from_geometry_entity_type")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_geometry(self, mock_read_only, mock_owner_from_type, mock_build, mock_get_owner, mock_copy):

        mock_source_node = MagicMock(spec=hou.SopNode)

        mock_source = MagicMock(spec=hou.Geometry)
        mock_source.sopNode.return_value = mock_source_node

        mock_attrib1 = MagicMock(spec=hou.Attrib)
        mock_attrib1.geometry.return_value = MagicMock()

        mock_attrib2 = MagicMock(spec=hou.Attrib)
        mock_attrib2.geometry.return_value.sopNode.return_value = mock_source_node

        mock_attrib3 = MagicMock(spec=hou.Attrib)
        mock_attrib3.geometry.return_value.sopNode.return_value = mock_source_node

        attribs = [mock_attrib1, mock_attrib2, mock_attrib3]

        mock_target = MagicMock(spec=hou.Geometry)

        mock_target_owner = MagicMock(spec=int)
        mock_source_owner = MagicMock(spec=int)

        mock_get_owner.side_effect = (mock_source_owner, mock_source_owner, MagicMock(spec=int))

        mock_owner_from_type.side_effect = (mock_target_owner, mock_source_owner)

        api.copy_attribute_values(mock_source, attribs, mock_target)

        mock_read_only.assert_called_with(mock_target)

        mock_owner_from_type.assert_has_calls(
            [call(type(mock_target)), call(type(mock_source))]
        )

        mock_get_owner.assert_has_calls(
            [call(mock_attrib1.type.return_value), call(mock_attrib2.type.return_value), call(mock_attrib3.type.return_value)]
        )

        mock_build.assert_called_with([mock_attrib2.name.return_value])

        mock_copy.assert_called_with(
            mock_target,
            mock_target_owner,
            0,
            mock_source,
            mock_source_owner,
            0,
            mock_build.return_value,
            len(mock_build.return_value)
        )

class Test_copy_point_attribute_values(unittest.TestCase):
    """Test ht.inline.api.copy_point_attribute_values."""

    @patch("ht.inline.api.copy_attribute_values")
    def test(self, mock_copy):
        mock_target_point = MagicMock(spec=hou.Point)
        mock_source_point = MagicMock(spec=hou.Point)
        mock_attributes = MagicMock(spec=str)

        api.copy_point_attribute_values(mock_target_point, mock_source_point, mock_attributes)

        mock_copy.assert_called_with(mock_source_point, mock_attributes, mock_target_point)


class Test_copy_prim_attribute_values(unittest.TestCase):
    """Test ht.inline.api.copy_prim_attribute_values."""

    @patch("ht.inline.api.copy_attribute_values")
    def test(self, mock_copy):
        mock_target_prim = MagicMock(spec=hou.Prim)
        mock_source_prim = MagicMock(spec=hou.Prim)
        mock_attributes = MagicMock(spec=str)

        api.copy_prim_attribute_values(mock_target_prim, mock_source_prim, mock_attributes)

        mock_copy.assert_called_with(mock_source_prim, mock_attributes, mock_target_prim)


class Test_point_adjacent_polygons(unittest.TestCase):
    """Test ht.inline.api.point_adjacent_polygons."""

    @patch("ht.inline.api._get_prims_from_list")
    @patch("ht.inline.api._cpp_methods.pointAdjacentPolygons")
    def test(self, mock_adjacent, mock_get):
        mock_prim = MagicMock(spec=hou.Prim)

        result = api.point_adjacent_polygons(mock_prim)

        self.assertEqual(result, mock_get.return_value)

        mock_adjacent.assert_called_with(mock_prim.geometry.return_value, mock_prim.number.return_value)
        mock_get.assert_called_with(mock_prim.geometry.return_value, mock_adjacent.return_value)


class Test_edge_adjacent_polygons(unittest.TestCase):
    """Test ht.inline.api.edge_adjacent_polygons."""

    @patch("ht.inline.api._get_prims_from_list")
    @patch("ht.inline.api._cpp_methods.edgeAdjacentPolygons")
    def test(self, mock_adjacent, mock_get):
        mock_prim = MagicMock(spec=hou.Prim)

        result = api.edge_adjacent_polygons(mock_prim)

        self.assertEqual(result, mock_get.return_value)

        mock_adjacent.assert_called_with(mock_prim.geometry.return_value, mock_prim.number.return_value)
        mock_get.assert_called_with(mock_prim.geometry.return_value, mock_adjacent.return_value)


class Test_connected_points(unittest.TestCase):
    """Test ht.inline.api.connected_points."""

    @patch("ht.inline.api._get_points_from_list")
    @patch("ht.inline.api._cpp_methods.connectedPoints")
    def test(self, mock_connected, mock_get):
        mock_point = MagicMock(spec=hou.Point)

        result = api.connected_points(mock_point)

        self.assertEqual(result, mock_get.return_value)

        mock_connected.assert_called_with(mock_point.geometry.return_value, mock_point.number.return_value)
        mock_get.assert_called_with(mock_point.geometry.return_value, mock_connected.return_value)


class Test_connected_prims(unittest.TestCase):
    """Test ht.inline.api.connected_prims."""

    @patch("ht.inline.api._get_prims_from_list")
    @patch("ht.inline.api._cpp_methods.connectedPrims")
    def test(self, mock_connected, mock_get):
        mock_point = MagicMock(spec=hou.Point)

        result = api.connected_prims(mock_point)

        self.assertEqual(result, mock_get.return_value)

        mock_connected.assert_called_with(mock_point.geometry.return_value, mock_point.number.return_value)
        mock_get.assert_called_with(mock_point.geometry.return_value, mock_connected.return_value)


class Test_referencing_vertices(unittest.TestCase):
    """Test ht.inline.api.referencing_vertices."""

    @patch("ht.inline.api._cpp_methods.referencingVertices")
    def test(self, mock_referencing):
        mock_point = MagicMock(spec=hou.Prim)

        mock_result = MagicMock()
        mock_result.prims = range(3)
        mock_result.indices = reversed(range(3))

        mock_referencing.return_value = mock_result

        result = api.referencing_vertices(mock_point)

        self.assertEqual(result, mock_point.geometry.return_value.globVertices.return_value)

        mock_referencing.assert_called_with(mock_point.geometry.return_value, mock_point.number.return_value)

        mock_point.geometry.return_value.globVertices.assert_called_with("0v2 1v1 2v0")


class Test_string_table_indices(unittest.TestCase):
    """Test ht.inline.api.string_table_indices."""

    def test_not_string(self):
        mock_attrib = MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.Float

        with self.assertRaises(ValueError):
            api.string_table_indices(mock_attrib)

    @patch("ht.inline.api._cpp_methods.getStringTableIndices")
    @patch("ht.inline.api._get_attrib_owner")
    def test(self, mock_owner, mock_get):
        mock_attrib = MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.String

        result = api.string_table_indices(mock_attrib)

        self.assertEqual(result, tuple(mock_get.return_value))

        mock_owner.assert_called_with(mock_attrib.type.return_value)
        mock_get.assert_called_with(mock_attrib.geometry.return_value, mock_owner.return_value, mock_attrib.name.return_value)


class Test_vertex_string_attrib_values(unittest.TestCase):
    """Test ht.inline.api.vertex_string_attrib_values."""

    def test_invalid_attribute(self):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_geometry.findVertexAttrib.return_value = None

        mock_name = MagicMock(spec=str)

        with self.assertRaises(hou.OperationFailed):
            api.vertex_string_attrib_values(mock_geometry, mock_name)

        mock_geometry.findVertexAttrib.assert_called_with(mock_name)

    def test_not_string(self):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)

        mock_attrib = MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.Float

        mock_geometry.findVertexAttrib.return_value = mock_attrib

        with self.assertRaises(ValueError):
            api.vertex_string_attrib_values(mock_geometry, mock_name)

        mock_geometry.findVertexAttrib.assert_called_with(mock_name)

    @patch("ht.inline.api._cpp_methods.vertexStringAttribValues")
    def test(self, mock_get):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)

        mock_attrib = MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.String

        mock_geometry.findVertexAttrib.return_value = mock_attrib

        result = api.vertex_string_attrib_values(mock_geometry, mock_name)

        self.assertEqual(result, mock_get.return_value)

        mock_geometry.findVertexAttrib.assert_called_with(mock_name)
        mock_get.assert_called_with(mock_geometry, mock_name)


class Test_set_vertex_string_attrib_values(unittest.TestCase):
    """Test ht.inline.api.set_vertex_string_attrib_values."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)
        mock_values = MagicMock(spec=list)

        with self.assertRaises(hou.GeometryPermissionError):
            api.set_vertex_string_attrib_values(mock_geometry, mock_name, mock_values)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_invalid_attribute(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_geometry.findVertexAttrib.return_value = None

        mock_name = MagicMock(spec=str)
        mock_values = MagicMock(spec=list)

        with self.assertRaises(hou.OperationFailed):
            api.set_vertex_string_attrib_values(mock_geometry, mock_name, mock_values)

        mock_geometry.findVertexAttrib.assert_called_with(mock_name)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_not_string(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)
        mock_values = MagicMock(spec=list)

        mock_attrib = MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.Float

        mock_geometry.findVertexAttrib.return_value = mock_attrib

        with self.assertRaises(ValueError):
            api.set_vertex_string_attrib_values(mock_geometry, mock_name, mock_values)

        mock_geometry.findVertexAttrib.assert_called_with(mock_name)

    @patch("ht.inline.api.num_vertices")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_no_size_match(self, mock_read_only, mock_num):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)
        mock_values = MagicMock(spec=list)

        mock_attrib = MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.String

        mock_geometry.findVertexAttrib.return_value = mock_attrib

        with self.assertRaises(ValueError):
            api.set_vertex_string_attrib_values(mock_geometry, mock_name, mock_values)

        mock_geometry.findVertexAttrib.assert_called_with(mock_name)
        mock_num.assert_called_with(mock_geometry)

    @patch("ht.inline.api._cpp_methods.setVertexStringAttribValues")
    @patch("ht.inline.api._build_c_string_array")
    @patch("ht.inline.api.num_vertices")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_num, mock_build, mock_set):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)

        size = 5
        mock_values = MagicMock(spec=list)
        mock_values.__len__.return_value = size
        mock_num.return_value = size

        mock_attrib = MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.String

        mock_geometry.findVertexAttrib.return_value = mock_attrib

        api.set_vertex_string_attrib_values(mock_geometry, mock_name, mock_values)

        mock_geometry.findVertexAttrib.assert_called_with(mock_name)
        mock_num.assert_called_with(mock_geometry)

        mock_build.assert_called_with(mock_values)

        mock_set.assert_called_with(mock_geometry, mock_name, mock_build.return_value, len(mock_build.return_value))


class Test_set_shared_point_string_attrib(unittest.TestCase):
    """Test ht.inline.api.set_shared_point_string_attrib."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)
        mock_value = MagicMock(spec=str)

        with self.assertRaises(hou.GeometryPermissionError):
            api.set_shared_point_string_attrib(mock_geometry, mock_name, mock_value)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_invalid_attribute(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)
        mock_value = MagicMock(spec=str)

        mock_geometry.findPointAttrib.return_value = None

        with self.assertRaises(ValueError):
            api.set_shared_point_string_attrib(mock_geometry, mock_name, mock_value)

        mock_geometry.findPointAttrib.assert_called_with(mock_name)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_not_string(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)
        mock_value = MagicMock(spec=str)

        mock_attrib = MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.Float

        mock_geometry.findPointAttrib.return_value = mock_attrib

        with self.assertRaises(ValueError):
            api.set_shared_point_string_attrib(mock_geometry, mock_name, mock_value)

        mock_geometry.findPointAttrib.assert_called_with(mock_name)

    @patch("ht.inline.api._cpp_methods.setSharedStringAttrib")
    @patch("ht.inline.api._get_attrib_owner")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_default(self, mock_read_only, mock_owner, mock_set):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)
        mock_value = MagicMock(spec=str)

        mock_attrib = MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.String

        mock_geometry.findPointAttrib.return_value = mock_attrib

        api.set_shared_point_string_attrib(mock_geometry, mock_name, mock_value)

        mock_geometry.findPointAttrib.assert_called_with(mock_name)

        mock_owner.assert_called_with(mock_attrib.type.return_value)
        mock_set.assert_called_with(mock_geometry, mock_owner.return_value, mock_name, mock_value, 0)

    @patch("ht.inline.api._cpp_methods.setSharedStringAttrib")
    @patch("ht.inline.api._get_attrib_owner")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_group(self, mock_read_only, mock_owner, mock_set):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)
        mock_value = MagicMock(spec=str)
        mock_group = MagicMock(spec=hou.PointGroup)

        mock_attrib = MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.String

        mock_geometry.findPointAttrib.return_value = mock_attrib

        api.set_shared_point_string_attrib(mock_geometry, mock_name, mock_value, mock_group)

        mock_geometry.findPointAttrib.assert_called_with(mock_name)

        mock_owner.assert_called_with(mock_attrib.type.return_value)
        mock_set.assert_called_with(mock_geometry, mock_owner.return_value, mock_name, mock_value, mock_group.name.return_value)


class Test_set_shared_prim_string_attrib(unittest.TestCase):
    """Test ht.inline.api.set_shared_prim_string_attrib."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)
        mock_value = MagicMock(spec=str)

        with self.assertRaises(hou.GeometryPermissionError):
            api.set_shared_prim_string_attrib(mock_geometry, mock_name, mock_value)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_invalid_attribute(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)
        mock_value = MagicMock(spec=str)

        mock_geometry.findPrimAttrib.return_value = None

        with self.assertRaises(ValueError):
            api.set_shared_prim_string_attrib(mock_geometry, mock_name, mock_value)

        mock_geometry.findPrimAttrib.assert_called_with(mock_name)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_not_string(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)
        mock_value = MagicMock(spec=str)

        mock_attrib = MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.Float

        mock_geometry.findPrimAttrib.return_value = mock_attrib

        with self.assertRaises(ValueError):
            api.set_shared_prim_string_attrib(mock_geometry, mock_name, mock_value)

        mock_geometry.findPrimAttrib.assert_called_with(mock_name)

    @patch("ht.inline.api._cpp_methods.setSharedStringAttrib")
    @patch("ht.inline.api._get_attrib_owner")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_default(self, mock_read_only, mock_owner, mock_set):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)
        mock_value = MagicMock(spec=str)

        mock_attrib = MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.String

        mock_geometry.findPrimAttrib.return_value = mock_attrib

        api.set_shared_prim_string_attrib(mock_geometry, mock_name, mock_value)

        mock_geometry.findPrimAttrib.assert_called_with(mock_name)

        mock_owner.assert_called_with(mock_attrib.type.return_value)
        mock_set.assert_called_with(mock_geometry, mock_owner.return_value, mock_name, mock_value, 0)

    @patch("ht.inline.api._cpp_methods.setSharedStringAttrib")
    @patch("ht.inline.api._get_attrib_owner")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_group(self, mock_read_only, mock_owner, mock_set):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)
        mock_value = MagicMock(spec=str)
        mock_group = MagicMock(spec=hou.PointGroup)

        mock_attrib = MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.String

        mock_geometry.findPrimAttrib.return_value = mock_attrib

        api.set_shared_prim_string_attrib(mock_geometry, mock_name, mock_value, mock_group)

        mock_geometry.findPrimAttrib.assert_called_with(mock_name)

        mock_owner.assert_called_with(mock_attrib.type.return_value)
        mock_set.assert_called_with(mock_geometry, mock_owner.return_value, mock_name, mock_value, mock_group.name.return_value)


class Test_face_has_edge(unittest.TestCase):
    """Test ht.inline.api.face_has_edge."""

    @patch("ht.inline.api._cpp_methods.faceHasEdge")
    def test(self, mock_has):
        mock_face = MagicMock(spec=hou.Face)
        mock_pt1 = MagicMock(spec=hou.Point)
        mock_pt2 = MagicMock(spec=hou.Point)

        result = api.face_has_edge(mock_face, mock_pt1, mock_pt2)

        self.assertEqual(result, mock_has.return_value)

        mock_has.assert_called_with(
            mock_face.geometry.return_value,
            mock_face.number.return_value,
            mock_pt1.number.return_value,
            mock_pt2.number.return_value
        )


class Test_shared_edges(unittest.TestCase):
    """Test ht.inline.api.shared_edges."""

    @patch("ht.inline.api.face_has_edge")
    @patch("ht.inline.api.connected_points")
    def test(self, mock_connected, mock_has):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_point1 = MagicMock(spec=hou.Point)
        mock_point1.number.return_value = 1

        mock_vertex1 = MagicMock(spec=hou.Vertex)
        mock_vertex1.point.return_value = mock_point1

        mock_point2 = MagicMock(spec=hou.Point)
        mock_point2.number.return_value = 2

        mock_vertex2 = MagicMock(spec=hou.Vertex)
        mock_vertex2.point.return_value = mock_point2

        mock_point3 = MagicMock(spec=hou.Point)
        mock_point3.number.return_value = 3

        mock_vertex3 = MagicMock(spec=hou.Vertex)
        mock_vertex3.point.return_value = mock_point3

        mock_face1 = MagicMock(spec=hou.Face)
        mock_face1.geometry.return_value = mock_geometry
        mock_face1.vertices.return_value = (mock_vertex1, mock_vertex2, mock_vertex3)

        mock_connected.side_effect = (
            (mock_point2, mock_point3),
            (mock_point3, mock_point1),
            (mock_point1, mock_point2),
        )

        mock_face2 = MagicMock(spec=hou.Face)

        # pt 2 and 3 are connected, so we need to have positives when iterating over both.
        # Duplicate edges are removed via the set.
        mock_has.side_effect = (False, False, True, True, False, False, True, True)

        result = api.shared_edges(mock_face1, mock_face2)

        self.assertEqual(result, (mock_geometry.findEdge.return_value, ))

        mock_geometry.findEdge.assert_called_with(mock_point2, mock_point3)


class Test_insert_vertex(unittest.TestCase):
    """Test ht.inline.api.insert_vertex."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_face = MagicMock(spec=hou.Face)
        mock_face.geometry.return_value = mock_geometry

        mock_point = MagicMock(spec=hou.Point)
        mock_index = MagicMock(spec=int)

        with self.assertRaises(hou.GeometryPermissionError):
            api.insert_vertex(mock_face, mock_point, mock_index)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api._cpp_methods.insertVertex")
    @patch("ht.inline.api._assert_prim_vertex_index")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_assert, mock_insert):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_face = MagicMock(spec=hou.Face)
        mock_face.geometry.return_value = mock_geometry

        mock_point = MagicMock(spec=hou.Point)
        mock_index = MagicMock(spec=int)

        result = api.insert_vertex(mock_face, mock_point, mock_index)

        self.assertEqual(result, mock_face.vertex.return_value)

        mock_read_only.assert_called_with(mock_geometry)

        mock_assert.assert_called_with(mock_face, mock_index)

        mock_insert.assert_called_with(mock_geometry, mock_face.number.return_value, mock_point.number.return_value, mock_index)

        mock_face.vertex.assert_called_with(mock_index)


class Test_delete_vertex_from_face(unittest.TestCase):
    """Test ht.inline.api.delete_vertex_from_face."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_face = MagicMock(spec=hou.Face)
        mock_face.geometry.return_value = mock_geometry

        mock_index = MagicMock(spec=int)

        with self.assertRaises(hou.GeometryPermissionError):
            api.delete_vertex_from_face(mock_face, mock_index)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api._cpp_methods.deleteVertexFromFace")
    @patch("ht.inline.api._assert_prim_vertex_index")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_assert, mock_delete):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_face = MagicMock(spec=hou.Face)
        mock_face.geometry.return_value = mock_geometry

        mock_index = MagicMock(spec=int)

        api.delete_vertex_from_face(mock_face, mock_index)

        mock_read_only.assert_called_with(mock_geometry)

        mock_assert.assert_called_with(mock_face, mock_index)

        mock_delete.assert_called_with(mock_geometry, mock_face.number.return_value, mock_index)


class Test_set_face_vertex_point(unittest.TestCase):
    """Test ht.inline.api.set_face_vertex_point."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_face = MagicMock(spec=hou.Face)
        mock_face.geometry.return_value = mock_geometry

        mock_point = MagicMock(spec=hou.Point)
        mock_index = MagicMock(spec=int)

        with self.assertRaises(hou.GeometryPermissionError):
            api.set_face_vertex_point(mock_face, mock_point, mock_index)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api._cpp_methods.setFaceVertexPoint")
    @patch("ht.inline.api._assert_prim_vertex_index")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_assert, mock_set):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_face = MagicMock(spec=hou.Face)
        mock_face.geometry.return_value = mock_geometry

        mock_point = MagicMock(spec=hou.Point)
        mock_index = MagicMock(spec=int)

        api.set_face_vertex_point(mock_face, mock_index, mock_point)

        mock_read_only.assert_called_with(mock_geometry)

        mock_assert.assert_called_with(mock_face, mock_index)

        mock_set.assert_called_with(mock_geometry, mock_face.number.return_value, mock_index, mock_point.number.return_value)


class Test_primitive_bary_center(unittest.TestCase):
    """Test ht.inline.api.primitive_bary_center."""

    @patch("ht.inline.api.hou.Vector3", autospec=True)
    @patch("ht.inline.api._cpp_methods.primitiveBaryCenter")
    def test(self, mock_center, mock_hou_vec):
        mock_prim = MagicMock(spec=hou.Prim)

        mock_result = MagicMock()
        mock_center.return_value = mock_result

        result = api.primitive_bary_center(mock_prim)
        self.assertEqual(result, mock_hou_vec.return_value)

        mock_center.assert_called_with(mock_prim.geometry.return_value, mock_prim.number.return_value)

        mock_hou_vec.assert_called_with(mock_result.x, mock_result.y, mock_result.z)


class Test_primitive_area(unittest.TestCase):
    """Test ht.inline.api.primitive_area."""

    def test(self):
        mock_prim = MagicMock(spec=hou.Prim)

        result = api.primitive_area(mock_prim)
        self.assertEqual(result, mock_prim.intrinsicValue.return_value)

        mock_prim.intrinsicValue.assert_called_with("measuredarea")


class Test_primitive_perimeter(unittest.TestCase):
    """Test ht.inline.api.primitive_perimeter."""

    def test(self):
        mock_prim = MagicMock(spec=hou.Prim)

        result = api.primitive_perimeter(mock_prim)
        self.assertEqual(result, mock_prim.intrinsicValue.return_value)

        mock_prim.intrinsicValue.assert_called_with("measuredperimeter")


class Test_primitive_volume(unittest.TestCase):
    """Test ht.inline.api.primitive_volume."""

    def test(self):
        mock_prim = MagicMock(spec=hou.Prim)

        result = api.primitive_volume(mock_prim)
        self.assertEqual(result, mock_prim.intrinsicValue.return_value)

        mock_prim.intrinsicValue.assert_called_with("measuredvolume")


class Test_reverse_prim(unittest.TestCase):
    """Test ht.inline.api.reverse_prim."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_prim = MagicMock(spec=hou.Prim)
        mock_prim.geometry.return_value = mock_geometry

        with self.assertRaises(hou.GeometryPermissionError):
            api.reverse_prim(mock_prim)

    @patch("ht.inline.api._cpp_methods.reversePrimitive")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_reverse):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_prim = MagicMock(spec=hou.Prim)
        mock_prim.geometry.return_value = mock_geometry

        api.reverse_prim(mock_prim)

        mock_reverse.assert_called_with(mock_geometry, mock_prim.number.return_value)


class Test_make_primitive_points_unique(unittest.TestCase):
    """Test ht.inline.api.make_primitive_points_unique."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_prim = MagicMock(spec=hou.Prim)
        mock_prim.geometry.return_value = mock_geometry

        with self.assertRaises(hou.GeometryPermissionError):
            api.make_primitive_points_unique(mock_prim)

    @patch("ht.inline.api._cpp_methods.makePrimitiveUnique")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_unique):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_prim = MagicMock(spec=hou.Prim)
        mock_prim.geometry.return_value = mock_geometry

        api.make_primitive_points_unique(mock_prim)

        mock_unique.assert_called_with(mock_geometry, mock_prim.number.return_value)


class Test_primitive_bounding_box(unittest.TestCase):
    """Test ht.inline.api.primitive_bounding_box."""

    @patch("ht.inline.api.hou.BoundingBox")
    def test(self, mock_bounding):
        mock_value = MagicMock()

        mock_prim = MagicMock(spec=hou.Prim)
        mock_prim.intrinsicValue.return_value = mock_value

        result = api.primitive_bounding_box(mock_prim)

        self.assertEqual(result, mock_bounding.return_value)

        mock_prim.intrinsicValue.assert_called_with("bounds")

        mock_bounding.assert_called_with(
            mock_value.__getitem__.return_value,
            mock_value.__getitem__.return_value,
            mock_value.__getitem__.return_value,
            mock_value.__getitem__.return_value,
            mock_value.__getitem__.return_value,
            mock_value.__getitem__.return_value,
        )

        mock_value.__getitem__.assert_has_calls(
            [call(0),call(2),call(4),call(1),call(3),call(5)]
        )


class Test_compute_point_normals(unittest.TestCase):
    """Test ht.inline.api.compute_point_normals."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        with self.assertRaises(hou.GeometryPermissionError):
            api.compute_point_normals(mock_geometry)

    @patch("ht.inline.api._cpp_methods.computePointNormals")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_compute):
        mock_geometry = MagicMock(spec=hou.Geometry)

        api.compute_point_normals(mock_geometry)

        mock_compute.assert_called_with(mock_geometry)


class Test_add_point_normal_attribute(unittest.TestCase):
    """Test ht.inline.api.add_point_normal_attribute."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        with self.assertRaises(hou.GeometryPermissionError):
            api.add_point_normal_attribute(mock_geometry)

    @patch("ht.inline.api._cpp_methods.addNormalAttribute", return_value=False)
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_failure(self, mock_read_only, mock_add):
        mock_geometry = MagicMock(spec=hou.Geometry)

        with self.assertRaises(hou.OperationFailed):
            api.add_point_normal_attribute(mock_geometry)

        mock_add.assert_called_with(mock_geometry)

    @patch("ht.inline.api._cpp_methods.addNormalAttribute", return_value=True)
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_add):
        mock_geometry = MagicMock(spec=hou.Geometry)

        result = api.add_point_normal_attribute(mock_geometry)

        self.assertEqual(result, mock_geometry.findPointAttrib.return_value)

        mock_add.assert_called_with(mock_geometry)

        mock_geometry.findPointAttrib.assert_called_with("N")


class Test_add_point_velocity_attribute(unittest.TestCase):
    """Test ht.inline.api.add_point_velocity_attribute."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        with self.assertRaises(hou.GeometryPermissionError):
            api.add_point_velocity_attribute(mock_geometry)

    @patch("ht.inline.api._cpp_methods.addVelocityAttribute", return_value=False)
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_failure(self, mock_read_only, mock_add):
        mock_geometry = MagicMock(spec=hou.Geometry)

        with self.assertRaises(hou.OperationFailed):
            api.add_point_velocity_attribute(mock_geometry)

        mock_add.assert_called_with(mock_geometry)

    @patch("ht.inline.api._cpp_methods.addVelocityAttribute", return_value=True)
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_add):
        mock_geometry = MagicMock(spec=hou.Geometry)

        result = api.add_point_velocity_attribute(mock_geometry)

        self.assertEqual(result, mock_geometry.findPointAttrib.return_value)

        mock_add.assert_called_with(mock_geometry)

        mock_geometry.findPointAttrib.assert_called_with("v")


class Test_add_color_attribute(unittest.TestCase):
    """Test ht.inline.api.add_color_attribute."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_attrib_type = MagicMock(spec=hou.attribType)

        with self.assertRaises(hou.GeometryPermissionError):
            api.add_color_attribute(mock_geometry, mock_attrib_type)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_global(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        with self.assertRaises(ValueError):
            api.add_color_attribute(mock_geometry, hou.attribType.Global)

    @patch("ht.inline.api._cpp_methods.addDiffuseAttribute", return_value=False)
    @patch("ht.inline.api._get_attrib_owner",)
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_failure(self, mock_read_only, mock_owner, mock_add):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_attrib_type = MagicMock(spec=hou.attribType)

        with self.assertRaises(hou.OperationFailed):
            api.add_color_attribute(mock_geometry, mock_attrib_type)

        mock_owner.assert_called_with(mock_attrib_type)

        mock_add.assert_called_with(mock_geometry, mock_owner.return_value)

    @patch("ht.inline.api._find_attrib")
    @patch("ht.inline.api._cpp_methods.addDiffuseAttribute", return_value=True)
    @patch("ht.inline.api._get_attrib_owner",)
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_owner, mock_add, mock_find):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_attrib_type = MagicMock(spec=hou.attribType)

        result = api.add_color_attribute(mock_geometry, mock_attrib_type)

        self.assertEqual(result, mock_find.return_value)

        mock_owner.assert_called_with(mock_attrib_type)

        mock_add.assert_called_with(mock_geometry, mock_owner.return_value)

        mock_find.assert_called_with(mock_geometry, mock_attrib_type, "Cd")


class Test_convex_polygons(unittest.TestCase):
    """Test ht.inline.api.convex_polygons."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        with self.assertRaises(hou.GeometryPermissionError):
            api.convex_polygons(mock_geometry)

    @patch("ht.inline.api._cpp_methods.convexPolygons")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_default_arg(self, mock_read_only, mock_convex):
        mock_geometry = MagicMock(spec=hou.Geometry)

        api.convex_polygons(mock_geometry)

        mock_convex.assert_called_with(mock_geometry, 3)

    @patch("ht.inline.api._cpp_methods.convexPolygons")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_convex):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_max_points = MagicMock(spec=int)

        api.convex_polygons(mock_geometry, mock_max_points)

        mock_convex.assert_called_with(mock_geometry, mock_max_points)


class Test_clip_geometry(unittest.TestCase):
    """Test ht.inline.api.clip_geometry."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_origin = MagicMock(spec=hou.Vector3)
        mock_normal = MagicMock(spec=hou.Vector3)

        with self.assertRaises(hou.GeometryPermissionError):
            api.clip_geometry(mock_geometry, mock_origin, mock_normal)

    @patch("ht.inline.api._cpp_methods.clipGeometry")
    @patch("ht.inline.api.hou.hmath.buildTranslate")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_group_below(self, mock_read_only, mock_build, mock_clip):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_origin = MagicMock(spec=hou.Vector3)
        mock_normal = MagicMock(spec=hou.Vector3)
        mock_dist = MagicMock(spec=int)
        mock_group = MagicMock(spec=hou.PrimGroup)

        api.clip_geometry(mock_geometry, mock_origin, mock_normal, dist=mock_dist, below=True, group=mock_group)

        mock_origin.__add__.assert_called_with(mock_normal.__mul__.return_value)

        mock_normal.__mul__.assert_has_calls([call(mock_dist), call(-1)])

        mock_build.assert_called_with(mock_origin.__add__.return_value)

        mock_clip.assert_called_with(mock_geometry, mock_build.return_value, mock_normal.__mul__.return_value.normalized. return_value, 0, mock_group.name.return_value)

    @patch("ht.inline.api._cpp_methods.clipGeometry")
    @patch("ht.inline.api.hou.hmath.buildTranslate")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_default_args(self, mock_read_only, mock_build, mock_clip):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_origin = MagicMock(spec=hou.Vector3)
        mock_normal = MagicMock(spec=hou.Vector3)

        api.clip_geometry(mock_geometry, mock_origin, mock_normal)

        mock_origin.__add__.assert_not_called()

        mock_build.assert_called_with(mock_origin)

        mock_clip.assert_called_with(mock_geometry, mock_build.return_value, mock_normal.normalized.return_value, 0, "")


class Test_destroy_empty_groups(unittest.TestCase):
    """Test ht.inline.api.destroy_empty_groups."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_attrib_type = MagicMock(spec=hou.attribType)

        with self.assertRaises(hou.GeometryPermissionError):
            api.destroy_empty_groups(mock_geometry, mock_attrib_type)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_global(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        with self.assertRaises(ValueError):
            api.destroy_empty_groups(mock_geometry, hou.attribType.Global)

    @patch("ht.inline.api._cpp_methods.destroyEmptyGroups")
    @patch("ht.inline.api._get_attrib_owner",)
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_owner, mock_destroy):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_attrib_type = MagicMock(spec=hou.attribType)

        api.destroy_empty_groups(mock_geometry, mock_attrib_type)

        mock_owner.assert_called_with(mock_attrib_type)
        mock_destroy.assert_called_with(mock_geometry, mock_owner.return_value)


class Test_destroy_unused_points(unittest.TestCase):
    """Test ht.inline.api.destroy_unused_points."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        with self.assertRaises(hou.GeometryPermissionError):
            api.destroy_unused_points(mock_geometry)

    @patch("ht.inline.api._cpp_methods.destroyUnusedPoints")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_group(self, mock_read_only, mock_destroy):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_group = MagicMock(spec=hou.PointGroup)

        api.destroy_unused_points(mock_geometry, mock_group)

        mock_destroy.assert_called_with(mock_geometry, mock_group.name.return_value)

    @patch("ht.inline.api._cpp_methods.destroyUnusedPoints")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_no_group(self, mock_read_only, mock_destroy):
        mock_geometry = MagicMock(spec=hou.Geometry)

        api.destroy_unused_points(mock_geometry)

        mock_destroy.assert_called_with(mock_geometry, 0)


class Test_consolidate_points(unittest.TestCase):
    """Test ht.inline.api.consolidate_points."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        with self.assertRaises(hou.GeometryPermissionError):
            api.consolidate_points(mock_geometry)

    @patch("ht.inline.api._cpp_methods.consolidatePoints")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_group_distance(self, mock_read_only, mock_consolidate):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_distance = MagicMock(spec=float)
        mock_group = MagicMock(spec=hou.PointGroup)

        api.consolidate_points(mock_geometry, mock_distance, mock_group)

        mock_consolidate.assert_called_with(mock_geometry, mock_distance, mock_group.name.return_value)

    @patch("ht.inline.api._cpp_methods.consolidatePoints")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_no_group(self, mock_read_only, mock_consolidate):
        mock_geometry = MagicMock(spec=hou.Geometry)

        api.consolidate_points(mock_geometry)

        mock_consolidate.assert_called_with(mock_geometry, 0.001, 0)


class Test_unique_points(unittest.TestCase):
    """Test ht.inline.api.unique_points."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        with self.assertRaises(hou.GeometryPermissionError):
            api.unique_points(mock_geometry)

    @patch("ht.inline.api._cpp_methods.uniquePoints")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_group(self, mock_read_only, mock_unique):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_group = MagicMock(spec=hou.PointGroup)

        api.unique_points(mock_geometry, mock_group)

        mock_unique.assert_called_with(mock_geometry, mock_group.name.return_value)

    @patch("ht.inline.api._cpp_methods.uniquePoints")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_no_group(self, mock_read_only, mock_unique):
        mock_geometry = MagicMock(spec=hou.Geometry)

        api.unique_points(mock_geometry)

        mock_unique.assert_called_with(mock_geometry, 0)


class Test_rename_group(unittest.TestCase):
    """Test ht.inline.api.rename_group."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group = MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_new_name = MagicMock(spec=str)

        with self.assertRaises(hou.GeometryPermissionError):
            api.rename_group(mock_group, mock_new_name)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_same_name(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group = MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_new_name = mock_group.name.return_value

        with self.assertRaises(hou.OperationFailed):
            api.rename_group(mock_group, mock_new_name)

    @patch("ht.inline.api._find_group")
    @patch("ht.inline.api._cpp_methods.renameGroup", return_value=True)
    @patch("ht.inline.api._get_group_type")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_get_type, mock_rename, mock_find):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group = MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_new_name = MagicMock(spec=str)

        result = api.rename_group(mock_group, mock_new_name)

        self.assertEqual(result, mock_find.return_value)

        mock_get_type.assert_called_with(mock_group)

        mock_rename.assert_called_with(
            mock_geometry, mock_group.name.return_value, mock_new_name, mock_get_type.return_value
        )

        mock_find.assert_called_with(mock_geometry, mock_get_type.return_value, mock_new_name)

    @patch("ht.inline.api._find_group")
    @patch("ht.inline.api._cpp_methods.renameGroup", return_value=False)
    @patch("ht.inline.api._get_group_type")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_failure(self, mock_read_only, mock_get_type, mock_rename, mock_find):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group = MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_new_name = MagicMock(spec=str)

        result = api.rename_group(mock_group, mock_new_name)

        self.assertIsNone(result)

        mock_get_type.assert_called_with(mock_group)

        mock_rename.assert_called_with(
            mock_geometry, mock_group.name.return_value, mock_new_name, mock_get_type.return_value
        )

        mock_find.assert_not_called()


class Test_group_bounding_box(unittest.TestCase):
    """Test ht.inline.api.group_bounding_box."""

    @patch("ht.inline.api.hou.BoundingBox")
    @patch("ht.inline.api._cpp_methods.groupBoundingBox")
    @patch("ht.inline.api._get_group_type")
    def test(self, mock_get_type, mock_group_bbox, mock_bbox):
        mock_group = MagicMock(spec=hou.PointGroup)

        result = api.group_bounding_box(mock_group)
        self.assertEqual(result, mock_bbox.return_value)

        mock_get_type.assert_called_with(mock_group)

        mock_group_bbox.assert_called_with(mock_group.geometry.return_value, mock_get_type.return_value, mock_group.name.return_value)

        mock_bbox.assert_called_with(*mock_group_bbox.return_value)


class Test_group_size(unittest.TestCase):
    """Test ht.inline.api.group_size."""

    @patch("ht.inline.api._cpp_methods.groupSize")
    @patch("ht.inline.api._get_group_type")
    def test(self, mock_get_type, mock_size):
        mock_group = MagicMock(spec=hou.PointGroup)

        result = api.group_size(mock_group)
        self.assertEqual(result, mock_size.return_value)

        mock_get_type.assert_called_with(mock_group)

        mock_size.assert_called_with(mock_group.geometry.return_value, mock_group.name.return_value, mock_get_type.return_value)


class Test_toggle_point_in_group(unittest.TestCase):
    """Test ht.inline.api.toggle_point_in_group."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group = MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_point = MagicMock(spec=hou.Point)

        with self.assertRaises(hou.GeometryPermissionError):
            api.toggle_point_in_group(mock_group, mock_point)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api._cpp_methods.toggleGroupMembership")
    @patch("ht.inline.api._get_group_type")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_get_type, mock_toggle):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group = MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_point = MagicMock(spec=hou.Point)

        api.toggle_point_in_group(mock_group, mock_point)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_type.assert_called_with(mock_group)

        mock_toggle.assert_called_with(
            mock_geometry,
            mock_group.name.return_value,
            mock_get_type.return_value,
            mock_point.number.return_value
        )


class Test_toggle_prim_in_group(unittest.TestCase):
    """Test ht.inline.api.toggle_point_in_group."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group = MagicMock(spec=hou.PrimGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_prim = MagicMock(spec=hou.Prim)

        with self.assertRaises(hou.GeometryPermissionError):
            api.toggle_prim_in_group(mock_group, mock_prim)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api._cpp_methods.toggleGroupMembership")
    @patch("ht.inline.api._get_group_type")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_get_type, mock_toggle):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group = MagicMock(spec=hou.PrimGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_prim = MagicMock(spec=hou.Prim)

        api.toggle_prim_in_group(mock_group, mock_prim)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_type.assert_called_with(mock_group)

        mock_toggle.assert_called_with(
            mock_geometry,
            mock_group.name.return_value,
            mock_get_type.return_value,
            mock_prim.number.return_value
        )


class Test_toggle_group_entries(unittest.TestCase):
    """Test ht.inline.api.toggle_group_entries."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group = MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        with self.assertRaises(hou.GeometryPermissionError):
            api.toggle_group_entries(mock_group)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api._cpp_methods.toggleGroupEntries")
    @patch("ht.inline.api._get_group_type")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_get_type, mock_toggle):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group = MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        api.toggle_group_entries(mock_group)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_type.assert_called_with(mock_group)

        mock_toggle.assert_called_with(
            mock_geometry,
            mock_group.name.return_value,
            mock_get_type.return_value,
        )


class Test_copy_group(unittest.TestCase):
    """Test ht.inline.api.copy_group."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group = MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_new_name = MagicMock(spec=str)

        with self.assertRaises(hou.GeometryPermissionError):
            api.copy_group(mock_group, mock_new_name)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_same_name(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group = MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_new_name = mock_group.name.return_value

        with self.assertRaises(hou.OperationFailed):
            api.copy_group(mock_group, mock_new_name)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api._find_group")
    @patch("ht.inline.api._get_group_type")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_existing(self, mock_read_only, mock_get_type, mock_find):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group = MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_new_name = MagicMock(spec=str)

        with self.assertRaises(hou.OperationFailed):
            api.copy_group(mock_group, mock_new_name)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_type.assert_called_with(mock_group)

        mock_find.assert_called_with(mock_geometry, mock_get_type.return_value, mock_new_name)

    @patch("ht.inline.api._cpp_methods.copyGroup")
    @patch("ht.inline.api._get_group_attrib_owner")
    @patch("ht.inline.api._find_group")
    @patch("ht.inline.api._get_group_type")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_get_type, mock_find, mock_get_owner, mock_copy):
        mock_new_group = MagicMock(spec=hou.PointGroup)

        mock_find.side_effect = (None, mock_new_group)

        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group = MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_new_name = MagicMock(spec=str)

        result = api.copy_group(mock_group, mock_new_name)
        self.assertEqual(result, mock_new_group)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_type.assert_called_with(mock_group)

        mock_find.assert_has_calls(
            [
                call(mock_geometry, mock_get_type.return_value, mock_new_name),
                call(mock_geometry, mock_get_type.return_value, mock_new_name)
            ]
        )

        mock_get_owner.assert_called_with(mock_group)

        mock_copy.assert_called_with(mock_geometry, mock_get_owner.return_value, mock_group.name.return_value, mock_new_name)


class Test_groups_share_elements(unittest.TestCase):
    """Test ht.inline.api.groups_share_elements."""

    @patch("ht.inline.api._geo_details_match", return_value=False)
    def test_different_details(self, mock_match):
        mock_geometry1 = MagicMock(spec=hou.Geometry)

        mock_group1 = MagicMock(spec=hou.PointGroup)
        mock_group1.geometry.return_value = mock_geometry1

        mock_geometry2 = MagicMock(spec=hou.Geometry)

        mock_group2 = MagicMock(spec=hou.PointGroup)
        mock_group2.geometry.return_value = mock_geometry2

        with self.assertRaises(ValueError):
            api.groups_share_elements(mock_group1, mock_group2)

        mock_match.assert_called_with(mock_geometry1, mock_geometry2)

    @patch("ht.inline.api._get_group_type")
    @patch("ht.inline.api._geo_details_match", return_value=True)
    def test_different_group_types(self, mock_match, mock_get_type):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group1 = MagicMock(spec=hou.PointGroup)
        mock_group1.geometry.return_value = mock_geometry

        mock_group2 = MagicMock(spec=hou.PointGroup)
        mock_group2.geometry.return_value = mock_geometry

        mock_get_type.side_effect = (MagicMock(spec=int), MagicMock(spec=int))

        with self.assertRaises(TypeError):
            api.groups_share_elements(mock_group1, mock_group2)

        mock_match.assert_called_with(mock_geometry, mock_geometry)

        mock_get_type.assert_has_calls(
            [call(mock_group1), call(mock_group2)]
        )

    @patch("ht.inline.api._cpp_methods.groupsShareElements")
    @patch("ht.inline.api._get_group_type")
    @patch("ht.inline.api._geo_details_match", return_value=True)
    def test(self, mock_match, mock_get_type, mock_contains):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group1 = MagicMock(spec=hou.PointGroup)
        mock_group1.geometry.return_value = mock_geometry

        mock_group2 = MagicMock(spec=hou.PointGroup)
        mock_group2.geometry.return_value = mock_geometry

        result = api.groups_share_elements(mock_group1, mock_group2)

        self.assertEqual(result, mock_contains.return_value)

        mock_match.assert_called_with(mock_geometry, mock_geometry)

        mock_get_type.assert_has_calls(
            [call(mock_group1), call(mock_group2)]
        )

        mock_contains.assert_called_with(
            mock_geometry, mock_group1.name.return_value, mock_group2.name.return_value, mock_get_type.return_value
        )


class Test_convert_prim_to_point_group(unittest.TestCase):
    """Test ht.inline.api.convert_prim_to_point_group."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group = MagicMock(spec=hou.PrimGroup)
        mock_group.geometry.return_value = mock_geometry

        with self.assertRaises(hou.GeometryPermissionError):
            api.convert_prim_to_point_group(mock_group)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_name_already_exists(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group = MagicMock(spec=hou.PrimGroup)
        mock_group.geometry.return_value = mock_geometry

        with self.assertRaises(hou.OperationFailed):
            api.convert_prim_to_point_group(mock_group)

        mock_read_only.assert_called_with(mock_geometry)

        mock_geometry.findPointGroup.assert_called_with(mock_group.name.return_value)

    @patch("ht.inline.api._cpp_methods.primToPointGroup")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_same_name(self, mock_read_only, mock_to_point):
        mock_new_group = MagicMock(spec=hou.PointGroup)

        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_geometry.findPointGroup.side_effect = (None, mock_new_group)

        mock_group = MagicMock(spec=hou.PrimGroup)
        mock_group.geometry.return_value = mock_geometry

        result = api.convert_prim_to_point_group(mock_group)
        self.assertEqual(result, mock_new_group)

        mock_read_only.assert_called_with(mock_geometry)

        mock_geometry.findPointGroup.assert_has_calls(
            [call(mock_group.name.return_value), call(mock_group.name.return_value)]
        )

        mock_to_point.assert_called_with(
            mock_geometry,
            mock_group.name.return_value,
            mock_group.name.return_value,
            True
        )

    @patch("ht.inline.api._cpp_methods.primToPointGroup")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_new_name_no_destroy(self, mock_read_only, mock_to_point):
        mock_new_group = MagicMock(spec=hou.PointGroup)

        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_geometry.findPointGroup.side_effect = (None, mock_new_group)

        mock_group = MagicMock(spec=hou.PrimGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_new_name = MagicMock(spec=str)

        result = api.convert_prim_to_point_group(mock_group, mock_new_name, False)
        self.assertEqual(result, mock_new_group)

        mock_read_only.assert_called_with(mock_geometry)

        mock_geometry.findPointGroup.assert_has_calls(
            [call(mock_new_name), call(mock_new_name)]
        )

        mock_to_point.assert_called_with(
            mock_geometry,
            mock_group.name.return_value,
            mock_new_name,
            False
        )


class Test_convert_point_to_prim_group(unittest.TestCase):
    """Test ht.inline.api.convert_point_to_prim_group."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group = MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        with self.assertRaises(hou.GeometryPermissionError):
            api.convert_point_to_prim_group(mock_group)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_name_already_exists(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group = MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        with self.assertRaises(hou.OperationFailed):
            api.convert_point_to_prim_group(mock_group)

        mock_read_only.assert_called_with(mock_geometry)

        mock_geometry.findPrimGroup.assert_called_with(mock_group.name.return_value)

    @patch("ht.inline.api._cpp_methods.pointToPrimGroup")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_same_name(self, mock_read_only, mock_to_point):
        mock_new_group = MagicMock(spec=hou.PrimGroup)

        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_geometry.findPrimGroup.side_effect = (None, mock_new_group)

        mock_group = MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        result = api.convert_point_to_prim_group(mock_group)
        self.assertEqual(result, mock_new_group)

        mock_read_only.assert_called_with(mock_geometry)

        mock_geometry.findPrimGroup.assert_has_calls(
            [call(mock_group.name.return_value), call(mock_group.name.return_value)]
        )

        mock_to_point.assert_called_with(
            mock_geometry,
            mock_group.name.return_value,
            mock_group.name.return_value,
            True
        )

    @patch("ht.inline.api._cpp_methods.pointToPrimGroup")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_new_name_no_destroy(self, mock_read_only, mock_to_point):
        mock_new_group = MagicMock(spec=hou.PrimGroup)

        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_geometry.findPrimGroup.side_effect = (None, mock_new_group)

        mock_group = MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_new_name = MagicMock(spec=str)

        result = api.convert_point_to_prim_group(mock_group, mock_new_name, False)
        self.assertEqual(result, mock_new_group)

        mock_read_only.assert_called_with(mock_geometry)

        mock_geometry.findPrimGroup.assert_has_calls(
            [call(mock_new_name), call(mock_new_name)]
        )

        mock_to_point.assert_called_with(
            mock_geometry,
            mock_group.name.return_value,
            mock_new_name,
            False
        )


class Test_geometry_has_ungrouped_points(unittest.TestCase):
    """Test ht.inline.api.geometry_has_ungrouped_points."""

    @patch("ht.inline.api._cpp_methods.hasUngroupedPoints")
    def test(self, mock_has):
        mock_geometry = MagicMock(spec=hou.Geometry)

        result = api.geometry_has_ungrouped_points(mock_geometry)
        self.assertEqual(result, mock_has.return_value)

        mock_has.assert_called_with(mock_geometry)


class Test_group_ungrouped_points(unittest.TestCase):
    """Test ht.inline.api.group_ungrouped_points."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group_name = MagicMock(spec=str)

        with self.assertRaises(hou.GeometryPermissionError):
            api.group_ungrouped_points(mock_geometry, mock_group_name)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_empty_name(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        with self.assertRaises(ValueError):
            api.group_ungrouped_points(mock_geometry, "")

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_group_exists(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group_name = MagicMock(spec=str)
        mock_group_name.__len__.return_value = 1

        with self.assertRaises(hou.OperationFailed):
            api.group_ungrouped_points(mock_geometry, mock_group_name)

        mock_read_only.assert_called_with(mock_geometry)

        mock_geometry.findPointGroup.assert_called_with(mock_group_name)

    @patch("ht.inline.api._cpp_methods.groupUngroupedPoints")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_group_points):
        mock_new_group = MagicMock(spec=hou.PointGroup)

        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_geometry.findPointGroup.side_effect = (None, mock_new_group)

        mock_group_name = MagicMock(spec=str)
        mock_group_name.__len__.return_value = 1

        result = api.group_ungrouped_points(mock_geometry, mock_group_name)
        self.assertEqual(result, mock_new_group)

        mock_read_only.assert_called_with(mock_geometry)

        mock_geometry.findPointGroup.assert_has_calls(
            [call(mock_group_name), call(mock_group_name)]
        )

        mock_group_points.assert_called_with(mock_geometry, mock_group_name)


class Test_geometry_has_ungrouped_prims(unittest.TestCase):
    """Test ht.inline.api.geometry_has_ungrouped_prims."""

    @patch("ht.inline.api._cpp_methods.hasUngroupedPrims")
    def test(self, mock_has):
        mock_geometry = MagicMock(spec=hou.Geometry)

        result = api.geometry_has_ungrouped_prims(mock_geometry)
        self.assertEqual(result, mock_has.return_value)

        mock_has.assert_called_with(mock_geometry)


class Test_group_ungrouped_prims(unittest.TestCase):
    """Test ht.inline.api.group_ungrouped_prims."""

    @patch("ht.inline.api.is_geometry_read_only", return_value=True)
    def test_read_only(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group_name = MagicMock(spec=str)

        with self.assertRaises(hou.GeometryPermissionError):
            api.group_ungrouped_prims(mock_geometry, mock_group_name)

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_empty_name(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        with self.assertRaises(ValueError):
            api.group_ungrouped_prims(mock_geometry, "")

        mock_read_only.assert_called_with(mock_geometry)

    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test_group_exists(self, mock_read_only):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_group_name = MagicMock(spec=str)
        mock_group_name.__len__.return_value = 1

        with self.assertRaises(hou.OperationFailed):
            api.group_ungrouped_prims(mock_geometry, mock_group_name)

        mock_read_only.assert_called_with(mock_geometry)

        mock_geometry.findPrimGroup.assert_called_with(mock_group_name)

    @patch("ht.inline.api._cpp_methods.groupUngroupedPrims")
    @patch("ht.inline.api.is_geometry_read_only", return_value=False)
    def test(self, mock_read_only, mock_group_prims):
        mock_new_group = MagicMock(spec=hou.PrimGroup)

        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_geometry.findPrimGroup.side_effect = (None, mock_new_group)

        mock_group_name = MagicMock(spec=str)
        mock_group_name.__len__.return_value = 1

        result = api.group_ungrouped_prims(mock_geometry, mock_group_name)
        self.assertEqual(result, mock_new_group)

        mock_read_only.assert_called_with(mock_geometry)

        mock_geometry.findPrimGroup.assert_has_calls(
            [call(mock_group_name), call(mock_group_name)]
        )

        mock_group_prims.assert_called_with(mock_geometry, mock_group_name)



class Test_bounding_box_is_inside(unittest.TestCase):
    """Test ht.inline.api.bounding_box_is_inside."""

    @patch("ht.inline.api._cpp_methods.boundingBoxisInside")
    def test(self, mock_is_inside):
        mock_box1 = MagicMock(spec=hou.BoundingBox)
        mock_box2 = MagicMock(spec=hou.BoundingBox)

        result = api.bounding_box_is_inside(mock_box1, mock_box2)
        self.assertEqual(result, mock_is_inside.return_value)

        mock_is_inside.assert_called_with(mock_box1, mock_box2)


class Test_bounding_boxes_intersect(unittest.TestCase):
    """Test ht.inline.api.bounding_boxes_intersect."""

    @patch("ht.inline.api._cpp_methods.boundingBoxesIntersect")
    def test(self, mock_intersects):
        mock_box1 = MagicMock(spec=hou.BoundingBox)
        mock_box2 = MagicMock(spec=hou.BoundingBox)

        result = api.bounding_boxes_intersect(mock_box1, mock_box2)
        self.assertEqual(result, mock_intersects.return_value)

        mock_intersects.assert_called_with(mock_box1, mock_box2)


class Test_compute_bounding_box_intersection(unittest.TestCase):
    """Test ht.inline.api.compute_bounding_box_intersection."""

    @patch("ht.inline.api._cpp_methods.computeBoundingBoxIntersection")
    def test(self, mock_compute):
        mock_box1 = MagicMock(spec=hou.BoundingBox)
        mock_box2 = MagicMock(spec=hou.BoundingBox)

        result = api.compute_bounding_box_intersection(mock_box1, mock_box2)
        self.assertEqual(result, mock_compute.return_value)

        mock_compute.assert_called_with(mock_box1, mock_box2)


class Test_expand_bounding_box(unittest.TestCase):
    """Test ht.inline.api.expand_bounding_box."""

    @patch("ht.inline.api._cpp_methods.expandBoundingBoxBounds")
    def test(self, mock_expand):
        mock_box = MagicMock(spec=hou.BoundingBox)

        mock_delta_x = MagicMock(spec=float)
        mock_delta_y = MagicMock(spec=float)
        mock_delta_z = MagicMock(spec=float)

        api.expand_bounding_box(mock_box, mock_delta_x, mock_delta_y, mock_delta_z)

        mock_expand.assert_called_with(mock_box, mock_delta_x, mock_delta_y, mock_delta_z)


class Test_add_to_bounding_box_min(unittest.TestCase):
    """Test ht.inline.api.add_to_bounding_box_min."""

    @patch("ht.inline.api._cpp_methods.addToBoundingBoxMin")
    def test(self, mock_add):
        mock_box = MagicMock(spec=hou.BoundingBox)

        mock_vec = MagicMock(spec=hou.Vector3)

        api.add_to_bounding_box_min(mock_box, mock_vec)

        mock_add.assert_called_with(mock_box, mock_vec)


class Test_add_to_bounding_box_max(unittest.TestCase):
    """Test ht.inline.api.add_to_bounding_box_max."""

    @patch("ht.inline.api._cpp_methods.addToBoundingBoxMax")
    def test(self, mock_add):
        mock_box = MagicMock(spec=hou.BoundingBox)

        mock_vec = MagicMock(spec=hou.Vector3)

        api.add_to_bounding_box_max(mock_box, mock_vec)

        mock_add.assert_called_with(mock_box, mock_vec)


class Test_bounding_box_area(unittest.TestCase):
    """Test ht.inline.api.bounding_box_area."""

    @patch("ht.inline.api._cpp_methods.boundingBoxArea")
    def test(self, mock_area):
        mock_box = MagicMock(spec=hou.BoundingBox)

        result = api.bounding_box_area(mock_box)
        self.assertEqual(result, mock_area.return_value)

        mock_area.assert_called_with(mock_box)


class Test_bounding_box_volume(unittest.TestCase):
    """Test ht.inline.api.bounding_box_volume."""

    @patch("ht.inline.api._cpp_methods.boundingBoxVolume")
    def test(self, mock_volume):
        mock_box = MagicMock(spec=hou.BoundingBox)

        result = api.bounding_box_volume(mock_box)
        self.assertEqual(result, mock_volume.return_value)

        mock_volume.assert_called_with(mock_box)


class Test_is_parm_tuple_vector(unittest.TestCase):
    """Test ht.inline.api.is_parm_tuple_vector."""

    def test_not_vector(self):
        mock_parm_tuple = MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple.parmTemplate.return_value.namingScheme.return_value = hou.parmNamingScheme.RGBA

        self.assertFalse(api.is_parm_tuple_vector(mock_parm_tuple))

    def test_is_vector(self):
        mock_parm_tuple = MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple.parmTemplate.return_value.namingScheme.return_value = hou.parmNamingScheme.XYZW

        self.assertTrue(api.is_parm_tuple_vector(mock_parm_tuple))


class Test_eval_parm_tuple_as_vector(unittest.TestCase):
    """Test ht.inline.api.eval_parm_tuple_as_vector."""

    @patch("ht.inline.api.is_parm_tuple_vector", return_value=False)
    def test_not_vector(self, mock_is_vector):
        mock_parm_tuple = MagicMock(spec=hou.ParmTuple)

        with self.assertRaises(ValueError):
            api.eval_parm_tuple_as_vector(mock_parm_tuple)

        mock_is_vector.assert_called_with(mock_parm_tuple)

    @patch("ht.inline.api.hou.Vector2", autospec=True)
    @patch("ht.inline.api.is_parm_tuple_vector", return_value=True)
    def test_vector2(self, mock_is_vector, mock_hou_vec2):
        mock_value = MagicMock(spec=tuple)
        mock_value.__len__.return_value = 2

        mock_parm_tuple = MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple.eval.return_value = mock_value

        result = api.eval_parm_tuple_as_vector(mock_parm_tuple)
        self.assertEqual(result, mock_hou_vec2.return_value)

        mock_is_vector.assert_called_with(mock_parm_tuple)

        mock_hou_vec2.assert_called_with(mock_value)

    @patch("ht.inline.api.hou.Vector3", autospec=True)
    @patch("ht.inline.api.is_parm_tuple_vector", return_value=True)
    def test_vector3(self, mock_is_vector, mock_hou_vec3):
        mock_value = MagicMock(spec=tuple)
        mock_value.__len__.return_value = 3

        mock_parm_tuple = MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple.eval.return_value = mock_value

        result = api.eval_parm_tuple_as_vector(mock_parm_tuple)
        self.assertEqual(result, mock_hou_vec3.return_value)

        mock_is_vector.assert_called_with(mock_parm_tuple)

        mock_hou_vec3.assert_called_with(mock_value)

    @patch("ht.inline.api.hou.Vector4", autospec=True)
    @patch("ht.inline.api.is_parm_tuple_vector", return_value=True)
    def test_vector4(self, mock_is_vector, mock_hou_vec4):
        mock_value = MagicMock(spec=tuple)
        mock_value.__len__.return_value = 4

        mock_parm_tuple = MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple.eval.return_value = mock_value

        result = api.eval_parm_tuple_as_vector(mock_parm_tuple)
        self.assertEqual(result, mock_hou_vec4.return_value)

        mock_is_vector.assert_called_with(mock_parm_tuple)

        mock_hou_vec4.assert_called_with(mock_value)


class Test_is_parm_tuple_color(unittest.TestCase):
    """Test ht.inline.api.is_parm_tuple_color."""

    def test_not_color(self):
        mock_parm_tuple = MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple.parmTemplate.return_value.look.return_value = hou.parmLook.Angle

        self.assertFalse(api.is_parm_tuple_color(mock_parm_tuple))

    def test_is_color(self):
        mock_parm_tuple = MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple.parmTemplate.return_value.look.return_value = hou.parmLook.ColorSquare

        self.assertTrue(api.is_parm_tuple_color(mock_parm_tuple))


class Test_eval_parm_tuple_as_color(unittest.TestCase):
    """Test ht.inline.api.eval_parm_tuple_as_color."""

    @patch("ht.inline.api.is_parm_tuple_color", return_value=False)
    def test_not_color(self, mock_is_color):
        mock_parm_tuple = MagicMock(spec=hou.ParmTuple)

        with self.assertRaises(ValueError):
            api.eval_parm_tuple_as_color(mock_parm_tuple)

        mock_is_color.assert_called_with(mock_parm_tuple)

    @patch("ht.inline.api.hou.Color", autospec=True)
    @patch("ht.inline.api.is_parm_tuple_color", return_value=True)
    def test_color(self, mock_is_color, mock_hou_color):
        mock_parm_tuple = MagicMock(spec=hou.ParmTuple)

        result = api.eval_parm_tuple_as_color(mock_parm_tuple)
        self.assertEqual(result, mock_hou_color.return_value)

        mock_is_color.assert_called_with(mock_parm_tuple)

        mock_hou_color.assert_called_with(mock_parm_tuple.eval.return_value)


class Test_eval_parm_as_strip(unittest.TestCase):
    """Test ht.inline.api.eval_parm_as_strip."""

    def test_not_menu(self):
        mock_template = MagicMock(spec=hou.ParmTemplate)

        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.parmTemplate.return_value = mock_template

        with self.assertRaises(TypeError):
            api.eval_parm_as_strip(mock_parm)

    def test_toggle_menu(self):
        mock_template = MagicMock(spec=hou.MenuParmTemplate)
        mock_template.menuItems.return_value.__len__.return_value = 5
        mock_template.menuType.return_value = hou.menuType.StringToggle

        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = 13
        mock_parm.parmTemplate.return_value = mock_template

        result = api.eval_parm_as_strip(mock_parm)
        self.assertEqual(result, (True, False, True, True, False))


    def test_replace_menu(self):
        mock_template = MagicMock(spec=hou.MenuParmTemplate)
        mock_template.menuItems.return_value.__len__.return_value = 5
        mock_template.menuType.return_value = hou.menuType.StringReplace

        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = 3
        mock_parm.parmTemplate.return_value = mock_template

        result = api.eval_parm_as_strip(mock_parm)
        self.assertEqual(result, (False, False, False, True, False))


class Test_eval_parm_strip_as_string(unittest.TestCase):
    """Test ht.inline.api.eval_parm_strip_as_string."""

    @patch("ht.inline.api.eval_parm_as_strip")
    def test(self, mock_eval):
        mock_eval.return_value = (False, True, True, False, True)

        mock_item1 = MagicMock(spec=str)
        mock_item2 = MagicMock(spec=str)
        mock_item3 = MagicMock(spec=str)
        mock_item4 = MagicMock(spec=str)
        mock_item5 = MagicMock(spec=str)

        mock_template = MagicMock(spec=hou.MenuParmTemplate)
        mock_template.menuItems.return_value = (mock_item1, mock_item2, mock_item3, mock_item4, mock_item5)

        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.parmTemplate.return_value = mock_template

        result = api.eval_parm_strip_as_string(mock_parm)

        self.assertEqual(result, (mock_item2, mock_item3, mock_item5))

        mock_eval.assert_called_with(mock_parm)


class Test_is_parm_multiparm(unittest.TestCase):
    """Test ht.inline.api.is_parm_multiparm."""

    def test_folder_is_multiparm(self):
        mock_folder_type = MagicMock(spec=hou.folderType)

        mock_template = MagicMock(spec=hou.FolderParmTemplate)
        mock_template.folderType.return_value = mock_folder_type

        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.parmTemplate.return_value = mock_template

        mock_types = (mock_folder_type, )

        with patch("ht.inline.api._MULTIPARM_FOLDER_TYPES", mock_types):
            self.assertTrue(api.is_parm_multiparm(mock_parm))

    def test_folder_not_multiparm(self):
        mock_folder_type = MagicMock(spec=hou.folderType)

        mock_template = MagicMock(spec=hou.FolderParmTemplate)
        mock_template.folderType.return_value = mock_folder_type

        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.parmTemplate.return_value = mock_template

        mock_types = ()

        with patch("ht.inline.api._MULTIPARM_FOLDER_TYPES", mock_types):
            self.assertFalse(api.is_parm_multiparm(mock_parm))

    def test_not_folder(self):
        mock_template = MagicMock(spec=hou.ParmTemplate)

        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.parmTemplate.return_value = mock_template

        self.assertFalse(api.is_parm_multiparm(mock_parm))


class Test_get_multiparm_instances_per_item(unittest.TestCase):
    """Test ht.inline.api.get_multiparm_instances_per_item."""

    @patch("ht.inline.api.is_parm_multiparm", return_value=False)
    def test_not_multiparm(self, mock_is_multiparm):
        mock_parm = MagicMock(spec=hou.Parm)

        with self.assertRaises(ValueError):
            api.get_multiparm_instances_per_item(mock_parm)

    @patch("ht.inline.api._cpp_methods.getMultiParmInstancesPerItem")
    @patch("ht.inline.api.is_parm_multiparm", return_value=True)
    def test_parm(self, mock_is_multiparm, mock_get):
        mock_parm_tuple = MagicMock(spec=hou.ParmTuple)

        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.tuple.return_value = mock_parm_tuple

        result = api.get_multiparm_instances_per_item(mock_parm)
        self.assertEqual(result, mock_get.return_value)

        mock_get.assert_called_with(mock_parm_tuple.node.return_value, mock_parm_tuple.name.return_value)

    @patch("ht.inline.api._cpp_methods.getMultiParmInstancesPerItem")
    @patch("ht.inline.api.is_parm_multiparm", return_value=True)
    def test_parm_tuple(self, mock_is_multiparm, mock_get):
        mock_parm_tuple = MagicMock(spec=hou.ParmTuple)

        result = api.get_multiparm_instances_per_item(mock_parm_tuple)
        self.assertEqual(result, mock_get.return_value)

        mock_get.assert_called_with(mock_parm_tuple.node.return_value, mock_parm_tuple.name.return_value)


class Test_get_multiparm_start_offset(unittest.TestCase):
    """Test ht.inline.api.get_multiparm_start_offset."""

    @patch("ht.inline.api.is_parm_multiparm", return_value=False)
    def test_not_multiparm(self, mock_is_multiparm):
        mock_parm = MagicMock(spec=hou.Parm)

        with self.assertRaises(ValueError):
            api.get_multiparm_start_offset(mock_parm)

    @patch("ht.inline.api.is_parm_multiparm", return_value=True)
    def test_default(self, mock_is_multiparm):
        mock_template = MagicMock(spec=hou.ParmTemplate)
        mock_template.tags.return_value = {}

        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.parmTemplate.return_value = mock_template

        result = api.get_multiparm_start_offset(mock_parm)
        self.assertEqual(result, 1)

    @patch("ht.inline.api.is_parm_multiparm", return_value=True)
    def test_specific(self, mock_is_multiparm):
        mock_template = MagicMock(spec=hou.ParmTemplate)
        mock_template.tags.return_value = {"multistartoffset": "3"}

        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.parmTemplate.return_value = mock_template

        result = api.get_multiparm_start_offset(mock_parm)
        self.assertEqual(result, 3)


class Test_get_multiparm_instance_index(unittest.TestCase):
    """Test ht.inline.api.get_multiparm_instance_index."""

    def test_not_multiparm(self):
        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.isMultiParmInstance.return_value = False

        with self.assertRaises(ValueError):
            api.get_multiparm_instance_index(mock_parm)

    @patch("ht.inline.api._cpp_methods.getMultiParmInstanceIndex")
    def test_parm(self, mock_get):
        mock_parm_tuple = MagicMock(spec=hou.ParmTuple)

        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.isMultiParmInstance.return_value = True
        mock_parm.tuple.return_value = mock_parm_tuple

        result = api.get_multiparm_instance_index(mock_parm)
        self.assertEqual(result, tuple(mock_get.return_value))

        mock_get.assert_called_with(mock_parm_tuple.node.return_value, mock_parm_tuple.name.return_value)

    @patch("ht.inline.api._cpp_methods.getMultiParmInstanceIndex")
    def test_parm_tuple(self, mock_get):
        mock_parm_tuple = MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple.isMultiParmInstance.return_value = True

        result = api.get_multiparm_instance_index(mock_parm_tuple)
        self.assertEqual(result, tuple(mock_get.return_value))

        mock_get.assert_called_with(mock_parm_tuple.node.return_value, mock_parm_tuple.name.return_value)


class Test_get_multiparm_instances(unittest.TestCase):
    """Test ht.inline.api.get_multiparm_instances."""

    @patch("ht.inline.api.is_parm_multiparm", return_value=False)
    def test_not_multiparm(self, mock_is_multiparm):
        mock_parm = MagicMock(spec=hou.Parm)

        with self.assertRaises(ValueError):
            api.get_multiparm_instances(mock_parm)

    @patch("ht.inline.api._cpp_methods.getMultiParmInstances")
    @patch("ht.inline.api.is_parm_multiparm", return_value=True)
    def test_parm(self, mock_is_multiparm, mock_get):
        mock_node = MagicMock(spec=hou.Node)

        mock_parm_tuple = MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple.node.return_value = mock_node

        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.tuple.return_value = mock_parm_tuple

        mock_name1 = MagicMock(spec=str)
        mock_name1.__len__.return_value = 1

        mock_name2 = MagicMock(spec=str)
        mock_name2.__len__.return_value = 0

        mock_name3 = MagicMock(spec=str)
        mock_name3.__len__.return_value = 1

        mock_name4 = MagicMock(spec=str)
        mock_name4.__len__.return_value = 0

        mock_name5 = MagicMock(spec=str)
        mock_name5.__len__.return_value = 1

        mock_get.return_value = (
            (mock_name1, mock_name2, mock_name3),
            (mock_name4, mock_name5),
        )

        mock_tuple1 = MagicMock(spec=hou.ParmTuple)
        mock_tuple1.__len__.return_value = 2

        mock_tuple3 = MagicMock(spec=hou.ParmTuple)
        mock_tuple3.__len__.return_value = 1

        mock_tuple5 = MagicMock(spec=hou.ParmTuple)
        mock_tuple5.__len__.return_value = 2

        mock_node.parmTuple.side_effect = (mock_tuple1, mock_tuple3, mock_tuple5)

        expected = (
            (mock_tuple1, mock_tuple3.__getitem__.return_value),
            (mock_tuple5, )
        )

        result = api.get_multiparm_instances(mock_parm)
        self.assertEqual(result, expected)

        mock_get.assert_called_with(mock_node, mock_parm_tuple.name.return_value)

    @patch("ht.inline.api._cpp_methods.getMultiParmInstances")
    @patch("ht.inline.api.is_parm_multiparm", return_value=True)
    def test_parm_tuple(self, mock_is_multiparm, mock_get):
        mock_node = MagicMock(spec=hou.Node)

        mock_parm_tuple = MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple.node.return_value = mock_node

        mock_name1 = MagicMock(spec=str)
        mock_name1.__len__.return_value = 1

        mock_name2 = MagicMock(spec=str)
        mock_name2.__len__.return_value = 0

        mock_name3 = MagicMock(spec=str)
        mock_name3.__len__.return_value = 1

        mock_name4 = MagicMock(spec=str)
        mock_name4.__len__.return_value = 0

        mock_name5 = MagicMock(spec=str)
        mock_name5.__len__.return_value = 1

        mock_get.return_value = (
            (mock_name1, mock_name2, mock_name3),
            (mock_name4, mock_name5),
        )

        mock_tuple1 = MagicMock(spec=hou.ParmTuple)
        mock_tuple1.__len__.return_value = 2

        mock_tuple3 = MagicMock(spec=hou.ParmTuple)
        mock_tuple3.__len__.return_value = 1

        mock_tuple5 = MagicMock(spec=hou.ParmTuple)
        mock_tuple5.__len__.return_value = 2

        mock_node.parmTuple.side_effect = (mock_tuple1, mock_tuple3, mock_tuple5)

        expected = (
            (mock_tuple1, mock_tuple3.__getitem__.return_value),
            (mock_tuple5, )
        )

        result = api.get_multiparm_instances(mock_parm_tuple)
        self.assertEqual(result, expected)

        mock_get.assert_called_with(mock_node, mock_parm_tuple.name.return_value)


class Test_get_multiparm_instance_values(unittest.TestCase):
    """Test ht.inline.api.get_multiparm_instance_values."""

    @patch("ht.inline.api.is_parm_multiparm", return_value=False)
    def test_not_multiparm(self, mock_is_multiparm):
        mock_parm = MagicMock(spec=hou.Parm)

        with self.assertRaises(ValueError):
            api.get_multiparm_instance_values(mock_parm)

    @patch("ht.inline.api.get_multiparm_instances")
    @patch("ht.inline.api.is_parm_multiparm", return_value=True)
    def test_parm(self, mock_is_multiparm, mock_get):
        mock_parm_tuple = MagicMock(spec=hou.ParmTuple)

        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.tuple.return_value = mock_parm_tuple

        mock_tuple1 = MagicMock(spec=hou.ParmTuple)
        mock_tuple2 = MagicMock(spec=hou.ParmTuple)

        mock_parm1 = MagicMock(spec=hou.Parm)

        mock_get.return_value = ((mock_tuple1, mock_parm1), (mock_tuple2, ))

        expected = (
            (mock_tuple1.eval.return_value, mock_parm1.eval.return_value),
            (mock_tuple2.eval.return_value, ),
        )

        result = api.get_multiparm_instance_values(mock_parm)
        self.assertEqual(result, expected)

        mock_get.assert_called_with(mock_parm_tuple)

    @patch("ht.inline.api.get_multiparm_instances")
    @patch("ht.inline.api.is_parm_multiparm", return_value=True)
    def test_parm_tuple(self, mock_is_multiparm, mock_get):
        mock_parm_tuple = MagicMock(spec=hou.ParmTuple)

        mock_tuple1 = MagicMock(spec=hou.ParmTuple)
        mock_tuple2 = MagicMock(spec=hou.ParmTuple)

        mock_parm1 = MagicMock(spec=hou.Parm)

        mock_get.return_value = ((mock_tuple1, mock_parm1), (mock_tuple2, ))

        expected = (
            (mock_tuple1.eval.return_value, mock_parm1.eval.return_value),
            (mock_tuple2.eval.return_value, ),
        )

        result = api.get_multiparm_instance_values(mock_parm_tuple)
        self.assertEqual(result, expected)

        mock_get.assert_called_with(mock_parm_tuple)


class Test_eval_multiparm_instance(unittest.TestCase):
    """Test ht.inline.api.eval_multiparm_instance."""

    def test_invalid_number_signs(self):
        mock_node = MagicMock(spec=hou.Node)

        mock_name = MagicMock(spec=str)
        mock_name.count.return_value = 2

        mock_index = MagicMock(spec=int)

        with self.assertRaises(ValueError):
            api.eval_multiparm_instance(mock_node, mock_name, mock_index)

        mock_name.count.assert_called_with('#')

    def test_invalid_parm_name(self):
        mock_ptg = MagicMock(spec=hou.ParmTemplateGroup)
        mock_ptg.find.return_value = None

        mock_node = MagicMock(spec=hou.Node)
        mock_node.parmTemplateGroup.return_value = mock_ptg

        mock_name = MagicMock(spec=str)
        mock_name.count.return_value = 1

        mock_index = MagicMock(spec=int)

        with self.assertRaises(ValueError):
            api.eval_multiparm_instance(mock_node, mock_name, mock_index)

        mock_name.count.assert_called_with('#')

    @patch("ht.inline.api.is_parm_multiparm", return_value=False)
    def test_not_multiparm(self, mock_is_multiparm):
        mock_parm = MagicMock(spec=hou.Parm)

        mock_template = MagicMock(spec=hou.ParmTemplate)

        mock_folder_template = MagicMock(spec=hou.FolderParmTemplate)

        mock_ptg = MagicMock(spec=hou.ParmTemplateGroup)
        mock_ptg.containingFolder.return_value = mock_folder_template
        mock_ptg.find.return_value = mock_template

        mock_node = MagicMock(spec=hou.Node)
        mock_node.parmTemplateGroup.return_value = mock_ptg
        mock_node.parm.return_value = mock_parm

        mock_name = MagicMock(spec=str)
        mock_name.count.return_value = 1

        mock_index = MagicMock(spec=int)

        with self.assertRaises(ValueError):
            api.eval_multiparm_instance(mock_node, mock_name, mock_index)

        mock_name.count.assert_called_with('#')

        mock_ptg.containingFolder.assert_called_with(mock_name)
        mock_node.parm.assert_called_with(mock_folder_template.name.return_value)

        mock_is_multiparm.assert_called_with(mock_parm)

    @patch("ht.inline.api.is_parm_multiparm", return_value=True)
    def test_invalid_index(self, mock_is_multiparm):
        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = MagicMock(spec=int)

        mock_template = MagicMock(spec=hou.ParmTemplate)

        mock_folder_template = MagicMock(spec=hou.FolderParmTemplate)

        mock_ptg = MagicMock(spec=hou.ParmTemplateGroup)
        mock_ptg.containingFolder.return_value = mock_folder_template
        mock_ptg.find.return_value = mock_template

        mock_node = MagicMock(spec=hou.Node)
        mock_node.parmTemplateGroup.return_value = mock_ptg
        mock_node.parm.return_value = mock_parm

        mock_name = MagicMock(spec=str)
        mock_name.count.return_value = 1

        mock_index = MagicMock()
        mock_index.__ge__.return_value = True

        with self.assertRaises(IndexError):
            api.eval_multiparm_instance(mock_node, mock_name, mock_index)

        mock_name.count.assert_called_with('#')

        mock_ptg.containingFolder.assert_called_with(mock_name)
        mock_node.parm.assert_called_with(mock_folder_template.name.return_value)

        mock_is_multiparm.assert_called_with(mock_parm)

        mock_index.__ge__.assert_called_with(mock_parm.eval.return_value)

    @patch("ht.inline.api._cpp_methods.eval_multiparm_instance_float")
    @patch("ht.inline.api.get_multiparm_start_offset")
    @patch("ht.inline.api.is_parm_multiparm", return_value=True)
    def test_float_single_component(self, mock_is_multiparm, mock_get, mock_eval):
        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = MagicMock(spec=int)

        mock_template = MagicMock(spec=hou.ParmTemplate)
        mock_template.dataType.return_value = hou.parmData.Float
        mock_template.numComponents.return_value = 1

        mock_folder_template = MagicMock(spec=hou.FolderParmTemplate)

        mock_ptg = MagicMock(spec=hou.ParmTemplateGroup)
        mock_ptg.containingFolder.return_value = mock_folder_template
        mock_ptg.find.return_value = mock_template

        mock_node = MagicMock(spec=hou.Node)
        mock_node.parmTemplateGroup.return_value = mock_ptg
        mock_node.parm.return_value = mock_parm

        mock_name = MagicMock(spec=str)
        mock_name.count.return_value = 1

        mock_index = MagicMock()
        mock_index.__ge__.return_value = False

        result = api.eval_multiparm_instance(mock_node, mock_name, mock_index)
        self.assertEqual(result, mock_eval.return_value)

        mock_name.count.assert_called_with('#')

        mock_ptg.containingFolder.assert_called_with(mock_name)
        mock_node.parm.assert_called_with(mock_folder_template.name.return_value)

        mock_is_multiparm.assert_called_with(mock_parm)

        mock_index.__ge__.assert_called_with(mock_parm.eval.return_value)

        mock_get.assert_called_with(mock_parm)

        mock_eval.assert_called_with(mock_node, mock_name, 0, mock_index, mock_get.return_value)

    @patch("ht.inline.api._cpp_methods.eval_multiparm_instance_int")
    @patch("ht.inline.api.get_multiparm_start_offset")
    @patch("ht.inline.api.is_parm_multiparm", return_value=True)
    def test_int_multiple_components(self, mock_is_multiparm, mock_get, mock_eval):
        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = MagicMock(spec=int)

        mock_template = MagicMock(spec=hou.ParmTemplate)
        mock_template.dataType.return_value = hou.parmData.Int
        mock_template.numComponents.return_value = 2

        mock_folder_template = MagicMock(spec=hou.FolderParmTemplate)

        mock_ptg = MagicMock(spec=hou.ParmTemplateGroup)
        mock_ptg.containingFolder.return_value = mock_folder_template
        mock_ptg.find.return_value = mock_template

        mock_node = MagicMock(spec=hou.Node)
        mock_node.parmTemplateGroup.return_value = mock_ptg
        mock_node.parm.return_value = mock_parm

        mock_name = MagicMock(spec=str)
        mock_name.count.return_value = 1

        mock_index = MagicMock()
        mock_index.__ge__.return_value = False

        result = api.eval_multiparm_instance(mock_node, mock_name, mock_index)
        self.assertEqual(result, (mock_eval.return_value, mock_eval.return_value))

        mock_name.count.assert_called_with('#')

        mock_ptg.containingFolder.assert_called_with(mock_name)
        mock_node.parm.assert_called_with(mock_folder_template.name.return_value)

        mock_is_multiparm.assert_called_with(mock_parm)

        mock_index.__ge__.assert_called_with(mock_parm.eval.return_value)

        mock_get.assert_called_with(mock_parm)

        mock_eval.assert_has_calls(
            [
                call(mock_node, mock_name, 0, mock_index, mock_get.return_value),
                call(mock_node, mock_name, 1, mock_index, mock_get.return_value),
            ]
        )

    @patch("ht.inline.api._cpp_methods.eval_multiparm_instance_string")
    @patch("ht.inline.api.get_multiparm_start_offset")
    @patch("ht.inline.api.is_parm_multiparm", return_value=True)
    def test_string_multiple_components(self, mock_is_multiparm, mock_get, mock_eval):
        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = MagicMock(spec=int)

        mock_template = MagicMock(spec=hou.ParmTemplate)
        mock_template.dataType.return_value = hou.parmData.String
        mock_template.numComponents.return_value = 3

        mock_folder_template = MagicMock(spec=hou.FolderParmTemplate)

        mock_ptg = MagicMock(spec=hou.ParmTemplateGroup)
        mock_ptg.containingFolder.return_value = mock_folder_template
        mock_ptg.find.return_value = mock_template

        mock_node = MagicMock(spec=hou.Node)
        mock_node.parmTemplateGroup.return_value = mock_ptg
        mock_node.parm.return_value = mock_parm

        mock_name = MagicMock(spec=str)
        mock_name.count.return_value = 1

        mock_index = MagicMock()
        mock_index.__ge__.return_value = False

        result = api.eval_multiparm_instance(mock_node, mock_name, mock_index)
        self.assertEqual(result, (mock_eval.return_value, mock_eval.return_value, mock_eval.return_value))

        mock_name.count.assert_called_with('#')

        mock_ptg.containingFolder.assert_called_with(mock_name)
        mock_node.parm.assert_called_with(mock_folder_template.name.return_value)

        mock_is_multiparm.assert_called_with(mock_parm)

        mock_index.__ge__.assert_called_with(mock_parm.eval.return_value)

        mock_get.assert_called_with(mock_parm)

        mock_eval.assert_has_calls(
            [
                call(mock_node, mock_name, 0, mock_index, mock_get.return_value),
                call(mock_node, mock_name, 1, mock_index, mock_get.return_value),
                call(mock_node, mock_name, 2, mock_index, mock_get.return_value)
            ]
        )

    @patch("ht.inline.api._cpp_methods.eval_multiparm_instance_string")
    @patch("ht.inline.api.get_multiparm_start_offset")
    @patch("ht.inline.api.is_parm_multiparm", return_value=True)
    def test_invalid_type(self, mock_is_multiparm, mock_get, mock_eval):
        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = MagicMock(spec=int)

        mock_template = MagicMock(spec=hou.ParmTemplate)
        mock_template.dataType.return_value = hou.parmData.Data
        mock_template.numComponents.return_value = 3

        mock_folder_template = MagicMock(spec=hou.FolderParmTemplate)

        mock_ptg = MagicMock(spec=hou.ParmTemplateGroup)
        mock_ptg.containingFolder.return_value = mock_folder_template
        mock_ptg.find.return_value = mock_template

        mock_node = MagicMock(spec=hou.Node)
        mock_node.parmTemplateGroup.return_value = mock_ptg
        mock_node.parm.return_value = mock_parm

        mock_name = MagicMock(spec=str)
        mock_name.count.return_value = 1

        mock_index = MagicMock()
        mock_index.__ge__.return_value = False

        with self.assertRaises(TypeError):
            api.eval_multiparm_instance(mock_node, mock_name, mock_index)

        mock_name.count.assert_called_with('#')

        mock_ptg.containingFolder.assert_called_with(mock_name)
        mock_node.parm.assert_called_with(mock_folder_template.name.return_value)

        mock_is_multiparm.assert_called_with(mock_parm)

        mock_index.__ge__.assert_called_with(mock_parm.eval.return_value)

        mock_get.assert_called_with(mock_parm)


class Test_disconnect_all_inputs(unittest.TestCase):
    """Test ht.inline.api.disconnect_all_inputs."""

    @patch("ht.inline.api.hou.undos.group")
    def test(self, mock_undos):
        mock_connection1 = MagicMock(spec=hou.NodeConnection)
        mock_connection2 = MagicMock(spec=hou.NodeConnection)

        mock_node = MagicMock(spec=hou.Node)
        mock_node.inputConnections.return_value = (mock_connection1, mock_connection2)

        api.disconnect_all_inputs(mock_node)

        mock_undos.assert_called()

        mock_node.setInput.assert_has_calls(
            [call(mock_connection2.inputIndex.return_value, None), call(mock_connection1.inputIndex.return_value, None)]
        )


class Test_disconnect_all_outputs(unittest.TestCase):
    """Test ht.inline.api.disconnect_all_outputs."""

    @patch("ht.inline.api.hou.undos.group")
    def test(self, mock_undos):
        mock_connection1 = MagicMock(spec=hou.NodeConnection)
        mock_connection2 = MagicMock(spec=hou.NodeConnection)

        mock_node = MagicMock(spec=hou.Node)
        mock_node.outputConnections.return_value = (mock_connection1, mock_connection2)

        api.disconnect_all_outputs(mock_node)

        mock_undos.assert_called()

        mock_connection1.outputNode.return_value.setInput.assert_called_with(mock_connection1.inputIndex.return_value, None)
        mock_connection2.outputNode.return_value.setInput.assert_called_with(mock_connection2.inputIndex.return_value, None)


class Test_get_node_message_nodes(unittest.TestCase):
    """Test ht.inline.api.get_node_message_nodes."""

    def test(self):
        mock_section = MagicMock(spec=hou.HDASection)

        mock_definition = MagicMock(spec=hou.HDADefinition)
        mock_definition.sections.return_value = {"MessageNodes": mock_section}

        mock_node = MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = mock_definition

        result = api.get_node_message_nodes(mock_node)
        self.assertEqual(result, mock_node.glob.return_value)

        mock_node.glob.assert_called_with(mock_section.contents.return_value)

    def test_no_section(self):
        mock_definition = MagicMock(spec=hou.HDADefinition)
        mock_definition.sections.return_value = {}

        mock_node = MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = mock_definition

        result = api.get_node_message_nodes(mock_node)
        self.assertEqual(result, ())

    def test_not_hda(self):
        mock_node = MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = None

        result = api.get_node_message_nodes(mock_node)
        self.assertEqual(result, ())


class Test_get_node_editable_nodes(unittest.TestCase):
    """Test ht.inline.api.get_node_editable_nodes."""

    def test(self):
        mock_section = MagicMock(spec=hou.HDASection)

        mock_definition = MagicMock(spec=hou.HDADefinition)
        mock_definition.sections.return_value = {"EditableNodes": mock_section}

        mock_node = MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = mock_definition

        result = api.get_node_editable_nodes(mock_node)
        self.assertEqual(result, mock_node.glob.return_value)

        mock_node.glob.assert_called_with(mock_section.contents.return_value)

    def test_no_section(self):
        mock_definition = MagicMock(spec=hou.HDADefinition)
        mock_definition.sections.return_value = {}

        mock_node = MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = mock_definition

        result = api.get_node_editable_nodes(mock_node)
        self.assertEqual(result, ())

    def test_not_hda(self):
        mock_node = MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = None

        result = api.get_node_editable_nodes(mock_node)
        self.assertEqual(result, ())


class Test_get_node_dive_target(unittest.TestCase):
    """Test ht.inline.api.get_node_dive_target."""

    def test(self):
        mock_section = MagicMock(spec=hou.HDASection)

        mock_definition = MagicMock(spec=hou.HDADefinition)
        mock_definition.sections.return_value = {"DiveTarget": mock_section}

        mock_node = MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = mock_definition

        result = api.get_node_dive_target(mock_node)
        self.assertEqual(result, mock_node.node.return_value)

        mock_node.node.assert_called_with(mock_section.contents.return_value)

    def test_no_section(self):
        mock_definition = MagicMock(spec=hou.HDADefinition)
        mock_definition.sections.return_value = {}

        mock_node = MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = mock_definition

        result = api.get_node_dive_target(mock_node)
        self.assertIsNone(result)

    def test_not_hda(self):
        mock_node = MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = None

        result = api.get_node_dive_target(mock_node)
        self.assertIsNone(result)


class Test_get_node_representative_node(unittest.TestCase):
    """Test ht.inline.api.get_node_representative_node."""

    def test(self):
        mock_path = MagicMock(spec=str)
        mock_path.__len__.return_value = 1

        mock_definition = MagicMock(spec=hou.HDADefinition)
        mock_definition.representativeNodePath.return_value = mock_path

        mock_node = MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = mock_definition

        result = api.get_node_representative_node(mock_node)
        self.assertEqual(result, mock_node.node.return_value)

        mock_node.node.assert_called_with(mock_path)

    def test_empty_path(self):
        mock_path = MagicMock(spec=str)
        mock_path.__len__.return_value = 0

        mock_definition = MagicMock(spec=hou.HDADefinition)
        mock_definition.representativeNodePath.return_value = mock_path

        mock_node = MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = mock_definition

        result = api.get_node_representative_node(mock_node)
        self.assertIsNone(result)

        mock_node.node.assert_not_called()

    def test_not_hda(self):
        mock_node = MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = None

        result = api.get_node_representative_node(mock_node)
        self.assertIsNone(result)


class Test_node_is_contained_by(unittest.TestCase):
    """Test ht.inline.api.node_is_contained_by."""

    def test_is_parent(self):
        mock_containing = MagicMock(spec=hou.Node)

        mock_node = MagicMock(spec=hou.Node)
        mock_node.parent.return_value = mock_containing

        self.assertTrue(api.node_is_contained_by(mock_node, mock_containing))

    def test_parent_parent(self):
        mock_containing = MagicMock(spec=hou.Node)

        mock_parent = MagicMock(spec=hou.Node)
        mock_parent.parent.return_value = mock_containing

        mock_node = MagicMock(spec=hou.Node)
        mock_node.parent.return_value = mock_parent

        self.assertTrue(api.node_is_contained_by(mock_node, mock_containing))

    def test_not_contained(self):
        mock_containing = MagicMock(spec=hou.Node)

        mock_parent = MagicMock(spec=hou.Node)
        mock_parent.parent.return_value = None

        mock_node = MagicMock(spec=hou.Node)
        mock_node.parent.return_value = mock_parent

        self.assertFalse(api.node_is_contained_by(mock_node, mock_containing))


class Test_node_author_name(unittest.TestCase):
    """Test ht.inline.api.node_author_name."""

    @patch("ht.inline.api._cpp_methods.getNodeAuthor")
    def test(self, mock_get_author):
        mock_node = MagicMock(spec=hou.Node)

        result = api.node_author_name(mock_node)

        self.assertEqual(result, mock_get_author.return_value.split.return_value.__getitem__.return_value)

        mock_get_author.return_value.split.assert_called_with('@')
        mock_get_author.return_value.split.return_value.__getitem__.assert_called_with(0)


class Test_set_node_type_icon(unittest.TestCase):
    """Test ht.inline.api.set_node_type_icon."""

    @patch("ht.inline.api._cpp_methods.setNodeTypeIcon")
    def test(self, mock_set_icon):
        mock_type = MagicMock(spec=hou.NodeType)
        mock_icon = MagicMock(spec=str)

        api.set_node_type_icon(mock_type, mock_icon)
        mock_set_icon.assert_called_with(mock_type, mock_icon)


class Test_set_node_type_default_icon(unittest.TestCase):
    """Test ht.inline.api.set_node_type_default_icon."""

    @patch("ht.inline.api._cpp_methods.setNodeTypeDefaultIcon")
    def test(self, mock_set_icon):
        mock_type = MagicMock(spec=hou.NodeType)

        api.set_node_type_default_icon(mock_type)
        mock_set_icon.assert_called_with(mock_type)


class Test_is_node_type_python(unittest.TestCase):
    """Test ht.inline.api.is_node_type_python."""

    @patch("ht.inline.api._cpp_methods.isNodeTypePythonType")
    def test(self, mock_is_python):
        mock_type = MagicMock(spec=hou.NodeType)

        api.is_node_type_python(mock_type)
        mock_is_python.assert_called_with(mock_type)


class Test_is_node_type_subnet(unittest.TestCase):
    """Test ht.inline.api.is_node_type_subnet."""

    @patch("ht.inline.api._cpp_methods.isNodeTypeSubnetType")
    def test(self, mock_is_subnet):
        mock_type = MagicMock(spec=hou.NodeType)

        api.is_node_type_subnet(mock_type)
        mock_is_subnet.assert_called_with(mock_type)


class Test_vector_component_along(unittest.TestCase):
    """Test ht.inline.api.vector_component_along."""

    def test(self):
        mock_vec1 = MagicMock(spec=hou.Vector3)
        mock_vec2 = MagicMock(spec=hou.Vector3)

        result = api.vector_component_along(mock_vec1, mock_vec2)
        self.assertEqual(result, mock_vec1.dot.return_value)

        mock_vec1.dot.assert_called_with(mock_vec2.normalized.return_value)


class Test_vector_project_along(unittest.TestCase):
    """Test ht.inline.api.vector_project_along."""

    def test_zero(self):
        mock_vec1 = MagicMock(spec=hou.Vector3)
        vec2 = hou.Vector3()

        with self.assertRaises(ValueError):
            api.vector_project_along(mock_vec1, vec2)

    @patch("ht.inline.api.vector_component_along")
    def test(self, mock_along):
        mock_vec1 = MagicMock(spec=hou.Vector3)
        mock_vec2 = MagicMock(spec=hou.Vector3)

        result = api.vector_project_along(mock_vec1, mock_vec2)
        self.assertEqual(result, mock_vec2.normalized.return_value * mock_along.return_value)

        mock_along.assert_called_with(mock_vec1, mock_vec2)


class Test_vector_contains_nans(unittest.TestCase):
    """Test ht.inline.api.vector_contains_nans."""

    @patch("ht.inline.api.math.isnan")
    def test_contains(self, mock_is_nan):
        mock_value1 = MagicMock(spec=float)
        mock_value2 = MagicMock(spec=float)
        mock_value3 = MagicMock(spec=float)

        values = (mock_value1, mock_value2, mock_value3)

        mock_vec = MagicMock(spec=hou.Vector3)
        mock_vec.__getitem__.side_effect = values

        mock_is_nan.side_effect = (False, True, False)

        self.assertTrue(api.vector_contains_nans(mock_vec))

        mock_is_nan.assert_has_calls([call(mock_value1), call(mock_value2)])

    @patch("ht.inline.api.math.isnan")
    def test_does_not_contain(self, mock_is_nan):
        mock_value1 = MagicMock(spec=float)
        mock_value2 = MagicMock(spec=float)
        mock_value3 = MagicMock(spec=float)

        values = (mock_value1, mock_value2, mock_value3)

        mock_vec = MagicMock(spec=hou.Vector3)
        mock_vec.__getitem__.side_effect = values

        mock_is_nan.side_effect = (False, False, False)

        self.assertFalse(api.vector_contains_nans(mock_vec))

        mock_is_nan.assert_has_calls([call(mock_value1), call(mock_value2), call(mock_value3)])


class Test_vector_compute_dual(unittest.TestCase):
    """Test ht.inline.api.vector_compute_dual."""

    @patch("ht.inline.api._cpp_methods.vector3GetDual")
    @patch("ht.inline.api.hou.Matrix3", autospec=True)
    def test_contains(self, mock_mat, mock_get):
        mock_vec = MagicMock(spec=hou.Vector3)

        result = api.vector_compute_dual(mock_vec)
        self.assertEqual(result, mock_mat.return_value)

        mock_get.assert_called_with(mock_vec, mock_mat.return_value)


class Test_is_identity_matrix(unittest.TestCase):
    """Test ht.inline.api.is_identity_matrix."""

    def test_mat3_identity(self):
        mock_mat = MagicMock(spec=hou.Matrix3)

        with patch("ht.inline.api.hou.Matrix3.__new__", autospec=True) as mock_mat3:
            mock_mat3.return_value = mock_mat
            self.assertTrue(api.is_identity_matrix(mock_mat))

        mock_mat3.return_value.setToIdentity.assert_called()

    def test_mat3_not_identity(self):
        mock_mat = MagicMock(spec=hou.Matrix3)

        with patch("ht.inline.api.hou.Matrix3.__new__", autospec=True) as mock_mat3:
            self.assertFalse(api.is_identity_matrix(mock_mat))

        mock_mat3.return_value.setToIdentity.assert_called()

    @patch("ht.inline.api.hou.hmath.identityTransform")
    def test_mat4_identity(self, mock_ident):
        mock_mat = MagicMock(spec=hou.Matrix4)

        mock_ident.return_value = mock_mat

        self.assertTrue(api.is_identity_matrix(mock_mat))

    @patch("ht.inline.api.hou.hmath.identityTransform")
    def test_mat4_not_identity(self, mock_ident):
        mock_mat = MagicMock(spec=hou.Matrix4)

        self.assertFalse(api.is_identity_matrix(mock_mat))


class Test_set_matrix_translates(unittest.TestCase):
    """Test ht.inline.api.set_matrix_translates."""

    def test(self):
        mock_mat = MagicMock(spec=hou.Matrix4)
        mock_values = MagicMock(spec=tuple)

        api.set_matrix_translates(mock_mat, mock_values)

        mock_mat.setAt.assert_has_calls(
            [
                call(3, 0, mock_values.__getitem__.return_value),
                call(3, 1, mock_values.__getitem__.return_value),
                call(3, 2, mock_values.__getitem__.return_value),
            ]
        )

        mock_values.__getitem__.assert_has_calls(
            [call(0), call(1), call(2)]
        )


class Test_build_lookat_matrix(unittest.TestCase):
    """Test ht.inline.api.build_lookat_matrix."""

    @patch("ht.inline.api._cpp_methods.buildLookatMatrix")
    @patch("ht.inline.api.hou.Matrix3", autospec=True)
    def test(self, mock_mat3, mock_build):
        mock_from_vec = MagicMock(spec=hou.Vector3)
        mock_to_vec = MagicMock(spec=hou.Vector3)
        mock_up_vec = MagicMock(spec=hou.Vector3)

        result = api.build_lookat_matrix(mock_from_vec, mock_to_vec, mock_up_vec)
        self.assertEqual(result, mock_mat3.return_value)

        mock_build.assert_called_with(mock_mat3.return_value, mock_from_vec, mock_to_vec, mock_up_vec)


class Test_build_instance_matrix(unittest.TestCase):
    """Test ht.inline.api.build_instance_matrix."""

    @patch("ht.inline.api.hou.hmath.buildTranslate")
    @patch("ht.inline.api.hou.Matrix4", autospec=True)
    @patch("ht.inline.api.hou.hmath.buildScale")
    @patch("ht.inline.api.hou.Vector3", autospec=True)
    def test_orient(self, mock_vec3, mock_build_scale, mock_mat4, mock_build_trans):
        mock_pos = MagicMock(spec=hou.Vector3)
        mock_dir = MagicMock(spec=hou.Vector3)
        mock_pscale = MagicMock(spec=float)
        mock_scale = MagicMock(spec=hou.Vector3)
        mock_up_vector = MagicMock(spec=hou.Vector3)
        mock_rot = MagicMock(spec=hou.Quaternion)
        mock_trans = MagicMock(spec=hou.Vector3)
        mock_pivot = MagicMock(spec=hou.Vector3)
        mock_orient = MagicMock(spec=hou.Quaternion)

        result = api.build_instance_matrix(
            mock_pos, mock_dir, mock_pscale, mock_scale, mock_up_vector, mock_rot,
            mock_trans, mock_pivot, mock_orient
        )

        self.assertEqual(
            result,
            mock_build_trans.return_value * mock_build_scale.return_value * mock_mat4.return_value * mock_mat4.return_value * mock_build_trans.return_value
        )

        mock_scale.__mul__.assert_called_with(mock_pscale)
        mock_build_scale.assert_called_with(mock_scale.__mul__.return_value)

        mock_build_trans.assert_has_calls(
            [call(mock_pivot), call(mock_pos + mock_trans)]
        )

        mock_mat4.assert_has_calls(
            [call(mock_rot.extractRotationMatrix3.return_value), call(mock_orient.extractRotationMatrix3.return_value)]
        )

    @patch("ht.inline.api.build_lookat_matrix")
    @patch("ht.inline.api.hou.hmath.buildTranslate")
    @patch("ht.inline.api.hou.Matrix4", autospec=True)
    @patch("ht.inline.api.hou.hmath.buildScale")
    @patch("ht.inline.api.hou.Vector3", autospec=True)
    def test_up_vector(self, mock_vec3, mock_build_scale, mock_mat4, mock_build_trans, mock_build_lookat):
        mock_pos = MagicMock(spec=hou.Vector3)
        mock_dir = MagicMock(spec=hou.Vector3)
        mock_pscale = MagicMock(spec=float)
        mock_scale = MagicMock(spec=hou.Vector3)
        mock_up_vector = MagicMock(spec=hou.Vector3)
        mock_rot = MagicMock(spec=hou.Quaternion)
        mock_trans = MagicMock(spec=hou.Vector3)
        mock_pivot = MagicMock(spec=hou.Vector3)

        result = api.build_instance_matrix(
            mock_pos, mock_dir, mock_pscale, mock_scale, mock_up_vector, mock_rot,
            mock_trans, mock_pivot, None
        )

        self.assertEqual(
            result,
            mock_build_trans.return_value * mock_build_scale.return_value * mock_mat4.return_value * mock_mat4.return_value * mock_build_trans.return_value
        )

        mock_scale.__mul__.assert_called_with(mock_pscale)
        mock_build_scale.assert_called_with(mock_scale.__mul__.return_value)

        mock_build_trans.assert_has_calls(
            [call(mock_pivot), call(mock_pos + mock_trans)]
        )

        mock_mat4.assert_has_calls(
            [call(mock_rot.extractRotationMatrix3.return_value), call(mock_build_lookat.return_value)]
        )

        mock_build_lookat.assert_called_with(mock_dir, mock_vec3.return_value, mock_up_vector)

    @patch("ht.inline.api.hou.hmath.buildTranslate")
    @patch("ht.inline.api.hou.Matrix4", autospec=True)
    @patch("ht.inline.api.hou.hmath.buildScale")
    @patch("ht.inline.api.hou.Vector3", autospec=True)
    def test_up_vector_is_zero_vec(self, mock_vec3, mock_build_scale, mock_mat4, mock_build_trans):
        mock_pos = MagicMock(spec=hou.Vector3)
        mock_dir = MagicMock(spec=hou.Vector3)
        mock_pscale = MagicMock(spec=float)
        mock_scale = MagicMock(spec=hou.Vector3)
        mock_up_vector = mock_vec3.return_value
        mock_rot = MagicMock(spec=hou.Quaternion)
        mock_trans = MagicMock(spec=hou.Vector3)
        mock_pivot = MagicMock(spec=hou.Vector3)

        result = api.build_instance_matrix(
            mock_pos, mock_dir, mock_pscale, mock_scale, mock_up_vector, mock_rot,
            mock_trans, mock_pivot, None
        )

        self.assertEqual(
            result,
            mock_build_trans.return_value * mock_build_scale.return_value * mock_vec3.return_value.matrixToRotateTo.return_value * mock_mat4.return_value * mock_build_trans.return_value
        )

        mock_scale.__mul__.assert_called_with(mock_pscale)
        mock_build_scale.assert_called_with(mock_scale.__mul__.return_value)

        mock_build_trans.assert_has_calls(
            [call(mock_pivot), call(mock_pos + mock_trans)]
        )

        mock_mat4.assert_has_calls(
            [call(mock_rot.extractRotationMatrix3.return_value)]
        )

        mock_vec3.return_value.matrixToRotateTo.assert_called_with(mock_dir)


class Test_is_node_digital_asset(unittest.TestCase):
    """Test ht.inline.api.is_node_digital_asset."""

    def test_true(self):
        mock_node = MagicMock(spec=hou.Node)

        self.assertTrue(api.is_node_digital_asset(mock_node))

    def test_false(self):
        mock_node = MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = None

        self.assertFalse(api.is_node_digital_asset(mock_node))


class Test_asset_file_meta_source(unittest.TestCase):
    """Test ht.inline.api.asset_file_meta_source."""

    @patch("ht.inline.api.hou.hda.loadedFiles", return_value=())
    def test_not_installed(self, mock_loaded):
        mock_path = MagicMock(spec=str)

        self.assertIsNone(api.asset_file_meta_source(mock_path))

    @patch("ht.inline.api._cpp_methods.getMetaSourceForPath")
    @patch("ht.inline.api.hou.hda.loadedFiles")
    def test(self, mock_loaded, mock_get):
        mock_path = MagicMock(spec=str)

        mock_loaded.return_value = (mock_path, )

        result = api.asset_file_meta_source(mock_path)
        self.assertEqual(result, mock_get.return_value)

        mock_get.assert_called_with(mock_path)


class Test_get_definition_meta_source(unittest.TestCase):
    """Test ht.inline.api.get_definition_meta_source."""

    @patch("ht.inline.api.asset_file_meta_source")
    def test(self, mock_source):
        mock_definition = MagicMock(spec=hou.HDADefinition)

        result = api.get_definition_meta_source(mock_definition)
        self.assertEqual(result, mock_source.return_value)

        mock_source.assert_called_with(mock_definition.libraryFilePath.return_value)


class Test_remove_meta_source(unittest.TestCase):
    """Test ht.inline.api.remove_meta_source."""

    @patch("ht.inline.api._cpp_methods.removeMetaSource")
    def test(self, mock_remove):
        mock_source_name = MagicMock(spec=str)

        result = api.remove_meta_source(mock_source_name)
        self.assertEqual(result, mock_remove.return_value)

        mock_remove.assert_called_with(mock_source_name)


class Test_libraries_in_meta_source(unittest.TestCase):
    """Test ht.inline.api.libraries_in_meta_source."""

    @patch("ht.inline.api._clean_string_values")
    @patch("ht.inline.api._cpp_methods.getLibrariesInMetaSource")
    def test(self, mock_get, mock_clean):
        mock_source_name = MagicMock(spec=str)

        result = api.libraries_in_meta_source(mock_source_name)
        self.assertEqual(result, mock_clean.return_value)

        mock_clean.assert_called_with(mock_get.return_value)


class Test_is_dummy_definition(unittest.TestCase):
    """Test ht.inline.api.is_dummy_definition."""

    @patch("ht.inline.api._cpp_methods.isDummyDefinition")
    def test(self, mock_is_dummy):
        mock_definition = MagicMock(spec=hou.HDADefinition)

        result = api.is_dummy_definition(mock_definition)
        self.assertEqual(result, mock_is_dummy.return_value)

        mock_is_dummy.assert_called_with(
            mock_definition.libraryFilePath.return_value,
            mock_definition.nodeTypeCategory.return_value.name.return_value,
            mock_definition.nodeTypeName.return_value,
        )

# =============================================================================

if __name__ == '__main__':
    unittest.main()
