"""Test ht.inline.utils module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import ctypes
from mock import MagicMock, call, patch
import unittest

# Houdini Toolbox Imports
from ht.inline import utils

# Houdini Imports
import hou

# =============================================================================
# CLASSES
# =============================================================================

class Test_build_c_double_array(unittest.TestCase):
    """Test ht.inline.utils.build_c_double_array."""

    def test(self):
        values = [float(val) for val in range(5)]
        values.reverse()

        result = utils.build_c_double_array(values)

        self.assertEqual(list(result), values)

        expected_type = type((ctypes.c_double * len(values))())
        self.assertTrue(isinstance(result, expected_type))


class Test_build_c_int_array(unittest.TestCase):
    """Test ht.inline.utils.build_c_int_array."""

    def test(self):
        values = range(5)
        values.reverse()

        result = utils.build_c_int_array(values)

        self.assertEqual(list(result), values)

        expected_type = type((ctypes.c_int * len(values))())
        self.assertTrue(isinstance(result, expected_type))


class Test_build_c_string_array(unittest.TestCase):
    """Test ht.inline.utils.build_c_string_array."""

    def test(self):
        values = ["foo", "bar", "test"]

        result = utils.build_c_string_array(values)

        self.assertEqual(list(result), values)

        expected_type = type((ctypes.c_char_p * len(values))())
        self.assertTrue(isinstance(result, expected_type))


class Test_clean_string_values(unittest.TestCase):
    """Test ht.inline.utils.clean_string_values."""

    def test(self):
        mock_str1 = MagicMock(spec=str)
        mock_str1.__len__.return_value = 1

        mock_str2 = MagicMock(spec=str)
        mock_str2.__len__.return_value = 0

        mock_str3 = MagicMock(spec=str)
        mock_str3.__len__.return_value = 2

        values = [mock_str1, mock_str2, mock_str3]

        result = utils.clean_string_values(values)

        self.assertEqual(result, tuple([mock_str1, mock_str3]))


class Test_find_attrib(unittest.TestCase):
    """Test ht.inline.utils.find_attrib."""

    def test_vertex(self):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)

        result = utils.find_attrib(mock_geometry, hou.attribType.Vertex, mock_name)

        self.assertEqual(result, mock_geometry.findVertexAttrib.return_value)

        mock_geometry.findVertexAttrib.assert_called_with(mock_name)

    def test_point(self):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)

        result = utils.find_attrib(mock_geometry, hou.attribType.Point, mock_name)

        self.assertEqual(result, mock_geometry.findPointAttrib.return_value)

        mock_geometry.findPointAttrib.assert_called_with(mock_name)

    def test_prim(self):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)

        result = utils.find_attrib(mock_geometry, hou.attribType.Prim, mock_name)

        self.assertEqual(result, mock_geometry.findPrimAttrib.return_value)

        mock_geometry.findPrimAttrib.assert_called_with(mock_name)

    def test_global(self):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)

        result = utils.find_attrib(mock_geometry, hou.attribType.Global, mock_name)

        self.assertEqual(result, mock_geometry.findGlobalAttrib.return_value)

        mock_geometry.findGlobalAttrib.assert_called_with(mock_name)

    def test_invalid(self):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)

        with self.assertRaises(ValueError):
            utils.find_attrib(mock_geometry, None, mock_name)


class Test_find_group(unittest.TestCase):
    """Test ht.inline.utils.find_group."""

    def test_point(self):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)

        result = utils.find_group(mock_geometry, 0, mock_name)

        self.assertEqual(result, mock_geometry.findPointGroup.return_value)

        mock_geometry.findPointGroup.assert_called_with(mock_name)

    def test_prim(self):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)

        result = utils.find_group(mock_geometry, 1, mock_name)

        self.assertEqual(result, mock_geometry.findPrimGroup.return_value)

        mock_geometry.findPrimGroup.assert_called_with(mock_name)

    def test_edge(self):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)

        result = utils.find_group(mock_geometry, 2, mock_name)

        self.assertEqual(result, mock_geometry.findEdgeGroup.return_value)

        mock_geometry.findEdgeGroup.assert_called_with(mock_name)

    def test_invalid(self):
        mock_geometry = MagicMock(spec=hou.Geometry)
        mock_name = MagicMock(spec=str)

        with self.assertRaises(ValueError):
            utils.find_group(mock_geometry, None, mock_name)


class Test_geo_details_match(unittest.TestCase):
    """Test ht.inline.utils.geo_details_match."""

    def test_match(self):
        mock_geometry1 = MagicMock(spec=hou.Geometry)
        mock_geometry2 = MagicMock(spec=hou.Geometry)

        mock_geometry1._guDetailHandle.return_value._asVoidPointer.return_value = 1
        mock_geometry2._guDetailHandle.return_value._asVoidPointer.return_value = 1

        self.assertTrue(utils.geo_details_match(mock_geometry1, mock_geometry2))

        mock_geometry1._guDetailHandle.return_value.destroy.assert_called()
        mock_geometry2._guDetailHandle.return_value.destroy.assert_called()

    def test_no_match(self):
        mock_geometry1 = MagicMock(spec=hou.Geometry)
        mock_geometry2 = MagicMock(spec=hou.Geometry)

        mock_geometry1._guDetailHandle.return_value._asVoidPointer.return_value = 0
        mock_geometry2._guDetailHandle.return_value._asVoidPointer.return_value = 1

        self.assertFalse(utils.geo_details_match(mock_geometry1, mock_geometry2))

        mock_geometry1._guDetailHandle.return_value.destroy.assert_called()
        mock_geometry2._guDetailHandle.return_value.destroy.assert_called()


class Test_get_attrib_owner(unittest.TestCase):
    """Test ht.inline.utils.get_attrib_owner."""

    def test_in_map(self):
        mock_data_type = MagicMock(spec=hou.attribType)
        mock_dict = MagicMock(spec=dict)

        with patch("ht.inline.utils._ATTRIB_TYPE_MAP", mock_dict):
            result = utils.get_attrib_owner(mock_data_type)

            self.assertEqual(result, mock_dict.__getitem__.return_value)

            mock_dict.__getitem__.assert_called_with(mock_data_type)

    def test_invalid(self):
        mock_data_type = MagicMock(spec=hou.attribType)

        with patch("ht.inline.utils._ATTRIB_TYPE_MAP", {}):
            with self.assertRaises(ValueError):
                utils.get_attrib_owner(mock_data_type)


class Test_get_attrib_owner_from_geometry_entity_type(unittest.TestCase):
    """Test ht.inline.utils.get_attrib_owner_from_geometry_entity_type."""

    def test_in_map(self):
        mock_entity_type = MagicMock()
        mock_owner_value = MagicMock(spec=int)

        data = {
            mock_entity_type: mock_owner_value
        }

        with patch("ht.inline.utils._GEOMETRY_ATTRIB_MAP", data):
            result = utils.get_attrib_owner_from_geometry_entity_type(mock_entity_type)

            self.assertEqual(result, mock_owner_value)

    def test_subclass_in_map(self):
        mock_entity_type = hou.Polygon
        mock_parent_type = hou.Prim

        mock_owner_value = MagicMock(spec=int)

        data = {
            mock_parent_type: mock_owner_value
        }

        with patch("ht.inline.utils._GEOMETRY_ATTRIB_MAP", data):
            result = utils.get_attrib_owner_from_geometry_entity_type(mock_entity_type)

            self.assertEqual(result, mock_owner_value)

    def test_invalid_type(self):
        mock_owner_value = MagicMock(spec=int)

        data = {
            MagicMock: mock_owner_value
        }

        with patch("ht.inline.utils._GEOMETRY_ATTRIB_MAP", data):
            with self.assertRaises(ValueError):
                utils.get_attrib_owner_from_geometry_entity_type(hou.Vector2)


class Test_get_attrib_owner_from_geometry_type(unittest.TestCase):
    """Test ht.inline.utils.get_attrib_owner_from_geometry_type."""

    def test_in_map(self):
        mock_geometry_type = MagicMock(spec=hou.geometryType)
        mock_owner_value = MagicMock(spec=int)

        data = {mock_geometry_type: mock_owner_value}

        with patch("ht.inline.utils._GEOMETRY_TYPE_MAP", data):
            result = utils.get_attrib_owner_from_geometry_type(mock_geometry_type)

            self.assertEqual(result, mock_owner_value)

    def test_invalid_type(self):
        mock_geometry_type = MagicMock(spec=hou.geometryType)

        data = {}

        with patch("ht.inline.utils._GEOMETRY_TYPE_MAP", data):
            with self.assertRaises(ValueError):
                utils.get_attrib_owner_from_geometry_type(mock_geometry_type)


class Test_get_attrib_storage(unittest.TestCase):
    """Test ht.inline.utils.get_attrib_storage."""

    def test(self):
        mock_data_type = MagicMock(spec=hou.attribData)
        mock_dict = MagicMock(spec=dict)

        with patch("ht.inline.utils._ATTRIB_STORAGE_MAP", mock_dict):
            result = utils.get_attrib_storage(mock_data_type)

            self.assertEqual(result, mock_dict.__getitem__.return_value)

            mock_dict.__getitem__.assert_called_with(mock_data_type)

    def test_invalid(self):

        mock_data_type = MagicMock(spec=hou.attribData)

        with patch("ht.inline.utils._ATTRIB_STORAGE_MAP", {}):
            with self.assertRaises(ValueError):
                utils.get_attrib_storage(mock_data_type)


class Test_get_group_attrib_owner(unittest.TestCase):
    """Test ht.inline.utils.get_group_attrib_owner."""

    def test(self):
        mock_data_type = MagicMock()
        mock_dict = MagicMock(spec=dict)

        with patch("ht.inline.utils._GROUP_ATTRIB_MAP", mock_dict):
            result = utils.get_group_attrib_owner(mock_data_type)

            self.assertEqual(result, mock_dict.__getitem__.return_value)

            mock_dict.__getitem__.assert_called_with(type(mock_data_type))

    def test_invalid(self):
        mock_data_type = MagicMock()

        with patch("ht.inline.utils._GROUP_ATTRIB_MAP", {}):
            with self.assertRaises(ValueError):
                utils.get_group_attrib_owner(mock_data_type)


class Test_get_group_type(unittest.TestCase):
    """Test ht.inline.utils.get_group_type."""

    def test(self):
        mock_data_type = MagicMock()
        mock_dict = MagicMock(spec=dict)

        with patch("ht.inline.utils._GROUP_TYPE_MAP", mock_dict):
            result = utils.get_group_type(mock_data_type)

            self.assertEqual(result, mock_dict.__getitem__.return_value)

            mock_dict.__getitem__.assert_called_with(type(mock_data_type))

    def test_invalid(self):
        mock_data_type = MagicMock()

        with patch("ht.inline.utils._GROUP_TYPE_MAP", {}):
            with self.assertRaises(ValueError):
                utils.get_group_type(mock_data_type)


class Test_get_nodes_from_paths(unittest.TestCase):
    """Test ht.inline.utils.get_nodes_from_paths."""

    @patch("ht.inline.utils.hou.node")
    def test(self, mock_hou_node):
        mock_path1 = MagicMock(spec=str)

        mock_path2 = MagicMock(spec=str)
        mock_path2.__len__.return_value = 1

        mock_path3 = MagicMock(spec=str)
        mock_path3.__len__.return_value = 1

        result = utils.get_nodes_from_paths([mock_path1, mock_path2, mock_path3])

        self.assertEqual(result, (mock_hou_node.return_value, mock_hou_node.return_value))

        mock_hou_node.assert_has_calls(
            [call(mock_path2), call(mock_path3)]
        )


class Test_get_points_from_list(unittest.TestCase):
    """Test ht.inline.utils.get_points_from_list."""

    def test_empty(self):
        mock_geometry = MagicMock(spec=hou.Geometry)

        result = utils.get_points_from_list(mock_geometry, [])

        self.assertEqual(result, ())

    def test(self):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_int1 = MagicMock(spec=int)
        mock_int2 = MagicMock(spec=int)

        result = utils.get_points_from_list(mock_geometry, [mock_int1, mock_int2])

        self.assertEqual(result, mock_geometry.globPoints.return_value)

        mock_geometry.globPoints.assert_called_with("{} {}".format(mock_int1, mock_int2))


class Test_get_prims_from_list(unittest.TestCase):
    """Test ht.inline.utils.get_prims_from_list."""

    def test_empty(self):
        mock_geometry = MagicMock(spec=hou.Geometry)

        result = utils.get_prims_from_list(mock_geometry, [])

        self.assertEqual(result, ())

    def test(self):
        mock_geometry = MagicMock(spec=hou.Geometry)

        mock_int1 = MagicMock(spec=int)
        mock_int2 = MagicMock(spec=int)

        result = utils.get_prims_from_list(mock_geometry, [mock_int1, mock_int2])

        self.assertEqual(result, mock_geometry.globPrims.return_value)

        mock_geometry.globPrims.assert_called_with("{} {}".format(mock_int1, mock_int2))


# =============================================================================

if __name__ == '__main__':
    unittest.main()

