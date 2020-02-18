"""Test ht.inline.utils module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import ctypes

# Third Party Imports
import pytest

# Houdini Toolbox Imports
from ht.inline import utils

# Houdini Imports
import hou


# =============================================================================
# TESTS
# =============================================================================


def test_build_c_double_array():
    """Test ht.inline.utils.build_c_double_array."""
    values = [float(val) for val in range(5)]
    values.reverse()

    result = utils.build_c_double_array(values)

    assert list(result) == values

    expected_type = type((ctypes.c_double * len(values))())
    assert isinstance(result, expected_type)


def test_build_c_int_array():
    """Test ht.inline.utils.build_c_int_array."""
    values = range(5)
    values.reverse()

    result = utils.build_c_int_array(values)

    assert list(result) == values

    expected_type = type((ctypes.c_int * len(values))())
    assert isinstance(result, expected_type)


def test_build_c_string_array():
    """Test ht.inline.utils.build_c_string_array."""

    values = ["foo", "bar", "test"]

    result = utils.build_c_string_array(values)

    assert list(result) == values

    expected_type = type((ctypes.c_char_p * len(values))())
    assert isinstance(result, expected_type)


def test_clean_string_values(mocker):
    """Test ht.inline.utils.clean_string_values."""

    mock_str1 = mocker.MagicMock(spec=str)
    mock_str1.__len__.return_value = 1

    mock_str2 = mocker.MagicMock(spec=str)
    mock_str2.__len__.return_value = 0

    mock_str3 = mocker.MagicMock(spec=str)
    mock_str3.__len__.return_value = 2

    values = [mock_str1, mock_str2, mock_str3]

    result = utils.clean_string_values(values)

    assert result == tuple([mock_str1, mock_str3])


class Test_find_attrib(object):
    """Test ht.inline.utils.find_attrib."""

    def test_vertex(self, mocker):
        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)

        result = utils.find_attrib(mock_geometry, hou.attribType.Vertex, mock_name)

        assert result == mock_geometry.findVertexAttrib.return_value

        mock_geometry.findVertexAttrib.assert_called_with(mock_name)

    def test_point(self, mocker):
        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)

        result = utils.find_attrib(mock_geometry, hou.attribType.Point, mock_name)

        assert result == mock_geometry.findPointAttrib.return_value

        mock_geometry.findPointAttrib.assert_called_with(mock_name)

    def test_prim(self, mocker):
        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)

        result = utils.find_attrib(mock_geometry, hou.attribType.Prim, mock_name)

        assert result == mock_geometry.findPrimAttrib.return_value

        mock_geometry.findPrimAttrib.assert_called_with(mock_name)

    def test_global(self, mocker):
        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)

        result = utils.find_attrib(mock_geometry, hou.attribType.Global, mock_name)

        assert result == mock_geometry.findGlobalAttrib.return_value

        mock_geometry.findGlobalAttrib.assert_called_with(mock_name)

    def test_invalid(self, mocker):
        """Test an invalid attribute type."""
        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)

        with pytest.raises(ValueError):
            utils.find_attrib(mock_geometry, None, mock_name)


class Test_find_group(object):
    """Test ht.inline.utils.find_group."""

    def test_point(self, mocker):
        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)

        result = utils.find_group(mock_geometry, 0, mock_name)

        assert result == mock_geometry.findPointGroup.return_value

        mock_geometry.findPointGroup.assert_called_with(mock_name)

    def test_prim(self, mocker):
        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)

        result = utils.find_group(mock_geometry, 1, mock_name)

        assert result == mock_geometry.findPrimGroup.return_value

        mock_geometry.findPrimGroup.assert_called_with(mock_name)

    def test_edge(self, mocker):
        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)

        result = utils.find_group(mock_geometry, 2, mock_name)

        assert result == mock_geometry.findEdgeGroup.return_value

        mock_geometry.findEdgeGroup.assert_called_with(mock_name)

    def test_invalid(self, mocker):
        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)

        with pytest.raises(ValueError):
            utils.find_group(mock_geometry, None, mock_name)


class Test_geo_details_match(object):
    """Test ht.inline.utils.geo_details_match."""

    def test_match(self, mocker):
        mock_geometry1 = mocker.MagicMock(spec=hou.Geometry)
        mock_geometry2 = mocker.MagicMock(spec=hou.Geometry)

        mock_geometry1._guDetailHandle.return_value._asVoidPointer.return_value = 1
        mock_geometry2._guDetailHandle.return_value._asVoidPointer.return_value = 1

        assert utils.geo_details_match(mock_geometry1, mock_geometry2)

        mock_geometry1._guDetailHandle.return_value.destroy.assert_called()
        mock_geometry2._guDetailHandle.return_value.destroy.assert_called()

    def test_no_match(self, mocker):
        mock_geometry1 = mocker.MagicMock(spec=hou.Geometry)
        mock_geometry2 = mocker.MagicMock(spec=hou.Geometry)

        mock_geometry1._guDetailHandle.return_value._asVoidPointer.return_value = 0
        mock_geometry2._guDetailHandle.return_value._asVoidPointer.return_value = 1

        assert not utils.geo_details_match(mock_geometry1, mock_geometry2)

        mock_geometry1._guDetailHandle.return_value.destroy.assert_called()
        mock_geometry2._guDetailHandle.return_value.destroy.assert_called()


class Test_get_attrib_owner(object):
    """Test ht.inline.utils.get_attrib_owner."""

    def test_in_map(self, mocker):
        mock_data_type = mocker.MagicMock(spec=hou.attribType)
        mock_dict = mocker.MagicMock(spec=dict)

        mocker.patch("ht.inline.utils._ATTRIB_TYPE_MAP", mock_dict)

        result = utils.get_attrib_owner(mock_data_type)

        assert result == mock_dict.__getitem__.return_value

        mock_dict.__getitem__.assert_called_with(mock_data_type)

    def test_invalid(self, mocker):
        mock_data_type = mocker.MagicMock(spec=hou.attribType)

        mocker.patch("ht.inline.utils._ATTRIB_TYPE_MAP", {})

        with pytest.raises(ValueError):
            utils.get_attrib_owner(mock_data_type)


class Test_get_attrib_owner_from_geometry_entity_type(object):
    """Test ht.inline.utils.get_attrib_owner_from_geometry_entity_type."""

    def test_in_map(self, mocker):
        mock_entity_type = mocker.MagicMock()
        mock_owner_value = mocker.MagicMock(spec=int)

        data = {mock_entity_type: mock_owner_value}

        mocker.patch("ht.inline.utils._GEOMETRY_ATTRIB_MAP", data)

        result = utils.get_attrib_owner_from_geometry_entity_type(mock_entity_type)

        assert result == mock_owner_value

    def test_subclass_in_map(self, mocker):
        mock_entity_type = hou.Polygon
        mock_parent_type = hou.Prim

        mock_owner_value = mocker.MagicMock(spec=int)

        data = {mock_parent_type: mock_owner_value}

        mocker.patch("ht.inline.utils._GEOMETRY_ATTRIB_MAP", data)

        result = utils.get_attrib_owner_from_geometry_entity_type(mock_entity_type)

        assert result == mock_owner_value

    def test_invalid_type(self, mocker):
        mock_owner_value = mocker.MagicMock(spec=int)

        data = {mocker.MagicMock: mock_owner_value}

        mocker.patch("ht.inline.utils._GEOMETRY_ATTRIB_MAP", data)

        with pytest.raises(ValueError):
            utils.get_attrib_owner_from_geometry_entity_type(hou.Vector2)


class Test_get_attrib_owner_from_geometry_type(object):
    """Test ht.inline.utils.get_attrib_owner_from_geometry_type."""

    def test_in_map(self, mocker):
        mock_geometry_type = mocker.MagicMock(spec=hou.geometryType)
        mock_owner_value = mocker.MagicMock(spec=int)

        data = {mock_geometry_type: mock_owner_value}

        mocker.patch("ht.inline.utils._GEOMETRY_TYPE_MAP", data)

        result = utils.get_attrib_owner_from_geometry_type(mock_geometry_type)

        assert result == mock_owner_value

    def test_invalid_type(self, mocker):
        mock_geometry_type = mocker.MagicMock(spec=hou.geometryType)

        data = {}

        mocker.patch("ht.inline.utils._GEOMETRY_TYPE_MAP", data)

        with pytest.raises(ValueError):
            utils.get_attrib_owner_from_geometry_type(mock_geometry_type)


class Test_get_attrib_storage(object):
    """Test ht.inline.utils.get_attrib_storage."""

    def test(self, mocker):
        mock_data_type = mocker.MagicMock(spec=hou.attribData)
        mock_dict = mocker.MagicMock(spec=dict)

        mocker.patch("ht.inline.utils._ATTRIB_STORAGE_MAP", mock_dict)

        result = utils.get_attrib_storage(mock_data_type)

        assert result == mock_dict.__getitem__.return_value

        mock_dict.__getitem__.assert_called_with(mock_data_type)

    def test_invalid(self, mocker):
        mock_data_type = mocker.MagicMock(spec=hou.attribData)

        mocker.patch("ht.inline.utils._ATTRIB_STORAGE_MAP", {})

        with pytest.raises(ValueError):
            utils.get_attrib_storage(mock_data_type)


class Test_get_group_attrib_owner(object):
    """Test ht.inline.utils.get_group_attrib_owner."""

    def test(self, mocker):
        mock_data_type = mocker.MagicMock()
        mock_dict = mocker.MagicMock(spec=dict)

        mocker.patch("ht.inline.utils._GROUP_ATTRIB_MAP", mock_dict)

        result = utils.get_group_attrib_owner(mock_data_type)

        assert result == mock_dict.__getitem__.return_value

        mock_dict.__getitem__.assert_called_with(type(mock_data_type))

    def test_invalid(self, mocker):
        mock_data_type = mocker.MagicMock()

        mocker.patch("ht.inline.utils._GROUP_ATTRIB_MAP", {})

        with pytest.raises(ValueError):
            utils.get_group_attrib_owner(mock_data_type)


class Test_get_group_type(object):
    """Test ht.inline.utils.get_group_type."""

    def test(self, mocker):
        mock_data_type = mocker.MagicMock()
        mock_dict = mocker.MagicMock(spec=dict)

        mocker.patch("ht.inline.utils._GROUP_TYPE_MAP", mock_dict)

        result = utils.get_group_type(mock_data_type)

        assert result == mock_dict.__getitem__.return_value

        mock_dict.__getitem__.assert_called_with(type(mock_data_type))

    def test_invalid(self, mocker):
        mock_data_type = mocker.MagicMock()

        mocker.patch("ht.inline.utils._GROUP_TYPE_MAP", {})

        with pytest.raises(ValueError):
            utils.get_group_type(mock_data_type)


def test_get_nodes_from_paths(mocker):
    """Test ht.inline.utils.get_nodes_from_paths."""
    mock_hou_node = mocker.patch("ht.inline.utils.hou.node")

    mock_path1 = mocker.MagicMock(spec=str)

    mock_path2 = mocker.MagicMock(spec=str)
    mock_path2.__len__.return_value = 1

    mock_path3 = mocker.MagicMock(spec=str)
    mock_path3.__len__.return_value = 1

    result = utils.get_nodes_from_paths([mock_path1, mock_path2, mock_path3])

    assert result == (mock_hou_node.return_value, mock_hou_node.return_value)

    mock_hou_node.assert_has_calls([mocker.call(mock_path2), mocker.call(mock_path3)])


class Test_get_points_from_list(object):
    """Test ht.inline.utils.get_points_from_list."""

    def test_empty(self, mocker):
        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        result = utils.get_points_from_list(mock_geometry, [])

        assert result == ()

    def test(self, mocker):
        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_int1 = mocker.MagicMock(spec=int)
        mock_int2 = mocker.MagicMock(spec=int)

        result = utils.get_points_from_list(mock_geometry, [mock_int1, mock_int2])

        assert result == mock_geometry.globPoints.return_value

        mock_geometry.globPoints.assert_called_with(
            "{} {}".format(mock_int1, mock_int2)
        )


class Test_get_prims_from_list(object):
    """Test ht.inline.utils.get_prims_from_list."""

    def test_empty(self, mocker):
        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        result = utils.get_prims_from_list(mock_geometry, [])

        assert result == ()

    def test(self, mocker):
        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_int1 = mocker.MagicMock(spec=int)
        mock_int2 = mocker.MagicMock(spec=int)

        result = utils.get_prims_from_list(mock_geometry, [mock_int1, mock_int2])

        assert result == mock_geometry.globPrims.return_value

        mock_geometry.globPrims.assert_called_with("{} {}".format(mock_int1, mock_int2))
