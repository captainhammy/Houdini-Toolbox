"""Test ht.inline.api module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
from builtins import str
from builtins import range
from builtins import object
import sys

# Third Party Imports
import pytest

if sys.version_info.major == 3:
    pytest.skip("Skipping", allow_module_level=True)

# Houdini Toolbox Imports
from ht.inline import api

# Houdini Imports
import hou


# =============================================================================
# TESTS
# =============================================================================

# TODO: Test global dicts

# Non-Public Functions


class Test__assert_prim_vertex_index(object):
    """Test ht.inline.api._assert_prim_vertex_index."""

    def test_less_than_0(self, mocker):
        mock_prim = mocker.MagicMock(spec=hou.Prim)

        with pytest.raises(IndexError):
            api._assert_prim_vertex_index(mock_prim, -1)

    def test_equal(self, mocker):
        mocker.patch("ht.inline.api.num_prim_vertices", return_value=5)

        mock_prim = mocker.MagicMock(spec=hou.Prim)

        with pytest.raises(IndexError):
            api._assert_prim_vertex_index(mock_prim, 5)

    def test_greater_than(self, mocker):
        mocker.patch("ht.inline.api.num_prim_vertices", return_value=5)

        mock_prim = mocker.MagicMock(spec=hou.Prim)

        with pytest.raises(IndexError):
            api._assert_prim_vertex_index(mock_prim, 6)

    def test_valid(self, mocker):
        mocker.patch("ht.inline.api.num_prim_vertices", return_value=5)

        mock_prim = mocker.MagicMock(spec=hou.Prim)

        api._assert_prim_vertex_index(mock_prim, 4)


# Functions


class Test_clear_caches(object):
    """Test ht.inline.api.clear_caches."""

    def test_default_none(self, mocker):
        """Test with the default arg of None."""
        mock_clear = mocker.patch("ht.inline.api._cpp_methods.clearCacheByName")

        api.clear_caches()

        mock_clear.assert_called_with("")

    def test_args(self, mocker):
        """Test with the default arg of None."""
        mock_clear = mocker.patch("ht.inline.api._cpp_methods.clearCacheByName")

        mock_name1 = mocker.MagicMock(spec=str)
        mock_name2 = mocker.MagicMock(spec=str)

        api.clear_caches([mock_name1, mock_name2])

        mock_clear.assert_has_calls([mocker.call(mock_name1), mocker.call(mock_name2)])


def test_is_rendering(mocker):
    """Test ht.inline.api.is_rendering."""
    mock_rendering = mocker.patch("ht.inline.api._cpp_methods.isRendering")

    result = api.is_rendering()

    assert result == mock_rendering.return_value


class Test_get_global_variable_names(object):
    """Test ht.inline.api.get_global_variable_names."""

    def test_default_arg(self, mocker):
        mock_get_globals = mocker.patch(
            "ht.inline.api._cpp_methods.getGlobalVariableNames"
        )
        mock_clean = mocker.patch("ht.inline.utils.clean_string_values")

        result = api.get_global_variable_names()

        assert result == mock_clean.return_value

        mock_get_globals.assert_called_with(False)
        mock_clean.assert_called_with(mock_get_globals.return_value)

    def test(self, mocker):
        mock_get_globals = mocker.patch(
            "ht.inline.api._cpp_methods.getGlobalVariableNames"
        )
        mock_clean = mocker.patch("ht.inline.utils.clean_string_values")

        mock_dirty = mocker.MagicMock(spec=bool)

        result = api.get_global_variable_names(mock_dirty)

        assert result == mock_clean.return_value

        mock_get_globals.assert_called_with(mock_dirty)
        mock_clean.assert_called_with(mock_get_globals.return_value)


class Test_get_variable_names(object):
    """Test ht.inline.api.get_variable_names."""

    def test_default_arg(self, mocker):
        mock_get_globals = mocker.patch("ht.inline.api._cpp_methods.getVariableNames")
        mock_clean = mocker.patch("ht.inline.utils.clean_string_values")

        result = api.get_variable_names()

        assert result == mock_clean.return_value

        mock_get_globals.assert_called_with(False)
        mock_clean.assert_called_with(mock_get_globals.return_value)

    def test(self, mocker):
        mock_get_globals = mocker.patch("ht.inline.api._cpp_methods.getVariableNames")
        mock_clean = mocker.patch("ht.inline.utils.clean_string_values")

        mock_dirty = mocker.MagicMock(spec=bool)

        result = api.get_variable_names(mock_dirty)

        assert result == mock_clean.return_value

        mock_get_globals.assert_called_with(mock_dirty)
        mock_clean.assert_called_with(mock_get_globals.return_value)


class Test_get_variable_value(object):
    """Test ht.inline.api.get_variable_value."""

    def test_not_in_list(self, mocker):
        mocker.patch("ht.inline.api.get_variable_names", return_value=())
        mock_get_var = mocker.patch("ht.inline.api._cpp_methods.getVariableValue")

        mock_name = mocker.MagicMock(spec=str)

        result = api.get_variable_value(mock_name)

        assert result is None

        mock_get_var.assert_not_called()

    def test_syntax_error(self, mocker):
        mock_name = mocker.MagicMock(spec=str)

        mocker.patch("ht.inline.api.get_variable_names", return_value=(mock_name,))
        mock_get_var = mocker.patch("ht.inline.api._cpp_methods.getVariableValue")
        mock_eval = mocker.patch("ht.inline.api.ast.literal_eval")

        mock_eval.side_effect = SyntaxError

        result = api.get_variable_value(mock_name)

        assert result == mock_get_var.return_value

        mock_get_var.assert_called_with(mock_name)
        mock_eval.assert_called_with(mock_get_var.return_value)

    def test_value_error(self, mocker):
        mock_name = mocker.MagicMock(spec=str)

        mocker.patch("ht.inline.api.get_variable_names", return_value=(mock_name,))
        mock_get_var = mocker.patch("ht.inline.api._cpp_methods.getVariableValue")
        mock_eval = mocker.patch("ht.inline.api.ast.literal_eval")

        mock_eval.side_effect = ValueError

        result = api.get_variable_value(mock_name)

        assert result == mock_get_var.return_value

        mock_get_var.assert_called_with(mock_name)
        mock_eval.assert_called_with(mock_get_var.return_value)

    def test(self, mocker):
        mock_name = mocker.MagicMock(spec=str)

        mocker.patch("ht.inline.api.get_variable_names", return_value=(mock_name,))
        mock_get_var = mocker.patch("ht.inline.api._cpp_methods.getVariableValue")
        mock_eval = mocker.patch("ht.inline.api.ast.literal_eval")

        result = api.get_variable_value(mock_name)

        assert result == mock_eval.return_value

        mock_get_var.assert_called_with(mock_name)
        mock_eval.assert_called_with(mock_get_var.return_value)


class Test_set_variable(object):
    """Test ht.inline.api.set_variable."""

    def test_default_arg(self, mocker):
        mock_set = mocker.patch("ht.inline.api._cpp_methods.setVariable")

        mock_name = mocker.MagicMock(spec=str)
        mock_value = mocker.MagicMock()

        api.set_variable(mock_name, mock_value)

        mock_set.assert_called_with(mock_name, str(mock_value).encode("utf-8"), False)

    def test(self, mocker):
        mock_set = mocker.patch("ht.inline.api._cpp_methods.setVariable")

        mock_name = mocker.MagicMock(spec=str)
        mock_value = mocker.MagicMock()
        mock_global = mocker.MagicMock(spec=bool)

        api.set_variable(mock_name, mock_value, mock_global)

        mock_set.assert_called_with(mock_name, str(mock_value).encode("utf-8"), mock_global)


def test_unset_variable(mocker):
    """Test ht.inline.api.unset_variable."""
    mock_unset = mocker.patch("ht.inline.api._cpp_methods.unsetVariable")

    mock_name = mocker.MagicMock(spec=str)

    api.unset_variable(mock_name)

    mock_unset.assert_called_with(mock_name)


def test_emit_var_change(mocker):
    """Test ht.inline.api.emit_var_change."""
    mock_varchange = mocker.patch("ht.inline.api._cpp_methods.emitVarChange")

    api.emit_var_change()

    mock_varchange.assert_called()


def test_expand_range(mocker):
    """Test ht.inline.api.expand_range."""
    mock_expand = mocker.patch("ht.inline.api._cpp_methods.expandRange")

    mock_pattern = mocker.MagicMock(spec=str)

    result = api.expand_range(mock_pattern)

    assert result == tuple(mock_expand.return_value)

    mock_expand.assert_called_with(mock_pattern)


def test_is_geometry_read_only(mocker):
    """Test ht.inline.api.is_geometry_read_only."""
    mock_handle = mocker.MagicMock(spec=hou._GUDetailHandle)

    mock_geometry = mocker.MagicMock(spec=hou.Geometry)
    mock_geometry._guDetailHandle.return_value = mock_handle

    result = api.is_geometry_read_only(mock_geometry)

    assert result == mock_handle.isReadOnly.return_value

    mock_handle.destroy.assert_called()


def test_num_points(mocker):
    """Test ht.inline.api.num_points."""
    mock_geometry = mocker.MagicMock(spec=hou.Geometry)

    result = api.num_points(mock_geometry)

    assert result == mock_geometry.intrinsicValue.return_value
    mock_geometry.intrinsicValue.assert_called_with("pointcount")


def test_num_prims(mocker):
    """Test ht.inline.api.num_prims."""
    mock_geometry = mocker.MagicMock(spec=hou.Geometry)

    result = api.num_prims(mock_geometry)

    assert result == mock_geometry.intrinsicValue.return_value
    mock_geometry.intrinsicValue.assert_called_with("primitivecount")


def test_num_vertices(mocker):
    """Test ht.inline.api.num_vertices."""
    mock_geometry = mocker.MagicMock(spec=hou.Geometry)

    result = api.num_vertices(mock_geometry)

    assert result == mock_geometry.intrinsicValue.return_value
    mock_geometry.intrinsicValue.assert_called_with("vertexcount")


def test_num_prim_vertices(mocker):
    """Test ht.inline.api.num_prim_vertices."""
    mock_prim = mocker.MagicMock(spec=hou.Prim)

    result = api.num_prim_vertices(mock_prim)

    assert result == mock_prim.intrinsicValue.return_value
    mock_prim.intrinsicValue.assert_called_with("vertexcount")


class Test_pack_geometry(object):
    """Test ht.inline.api.pack_geometry."""

    def test_geo_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_source = mocker.MagicMock(spec=hou.Geometry)

        with pytest.raises(hou.GeometryPermissionError):
            api.pack_geometry(mock_geometry, mock_source)

        mock_read_only.assert_called_with(mock_geometry)

    def test_source_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", side_effect=(False, True)
        )
        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_source = mocker.MagicMock(spec=hou.Geometry)

        with pytest.raises(hou.GeometryPermissionError):
            api.pack_geometry(mock_geometry, mock_source)

        mock_read_only.assert_has_calls(
            [mocker.call(mock_geometry), mocker.call(mock_source)]
        )

    def test(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_pack = mocker.patch("ht.inline.api._cpp_methods.packGeometry")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_source = mocker.MagicMock(spec=hou.Geometry)

        result = api.pack_geometry(mock_geometry, mock_source)

        assert result == mock_geometry.iterPrims.return_value.__getitem__.return_value

        mock_geometry.iterPrims.return_value.__getitem__.assert_called_with(-1)

        mock_read_only.assert_has_calls(
            [mocker.call(mock_geometry), mocker.call(mock_source)]
        )

        mock_pack.assert_called_with(mock_source, mock_geometry)


class Test_sort_geometry_by_attribute(object):
    """Test ht.inline.api.sort_geometry_by_attribute."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_attribute = mocker.MagicMock(spec=hou.Attrib)
        mock_index = mocker.MagicMock(spec=int)

        with pytest.raises(hou.GeometryPermissionError):
            api.sort_geometry_by_attribute(mock_geometry, mock_attribute, mock_index)

        mock_read_only.assert_called_with(mock_geometry)

    def test_index_out_of_range(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_attribute = mocker.MagicMock(spec=hou.Attrib)
        mock_attribute.size.return_value = 5

        with pytest.raises(IndexError):
            api.sort_geometry_by_attribute(mock_geometry, mock_attribute, 10)

        mock_read_only.assert_called_with(mock_geometry)

    def test_global_attrib(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_attribute = mocker.MagicMock(spec=hou.Attrib)
        mock_attribute.size.return_value = 5
        mock_attribute.type.return_value = hou.attribType.Global

        with pytest.raises(ValueError):
            api.sort_geometry_by_attribute(mock_geometry, mock_attribute, 1)

        mock_read_only.assert_called_with(mock_geometry)

    def test_default_arg(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_get_owner = mocker.patch("ht.inline.utils.get_attrib_owner")
        mock_sort = mocker.patch("ht.inline.api._cpp_methods.sortGeometryByAttribute")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_attrib_type = mocker.MagicMock()

        mock_attribute = mocker.MagicMock(spec=hou.Attrib)
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
            False,
        )

    def test(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_get_owner = mocker.patch("ht.inline.utils.get_attrib_owner")
        mock_sort = mocker.patch("ht.inline.api._cpp_methods.sortGeometryByAttribute")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_attrib_type = mocker.MagicMock()

        mock_attribute = mocker.MagicMock(spec=hou.Attrib)
        mock_attribute.size.return_value = 5
        mock_attribute.type.return_value = mock_attrib_type

        mock_reverse = mocker.MagicMock(spec=bool)

        api.sort_geometry_by_attribute(mock_geometry, mock_attribute, 1, mock_reverse)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(mock_attrib_type)

        mock_sort.assert_called_with(
            mock_geometry,
            mock_get_owner.return_value,
            mock_attribute.name.return_value,
            1,
            mock_reverse,
        )


class Test_sort_geometry_along_axis(object):
    """Test ht.inline.api.sort_geometry_along_axis."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_geometry_type = mocker.MagicMock(spec=hou.geometryType)
        mock_axis = mocker.MagicMock(spec=int)

        with pytest.raises(hou.GeometryPermissionError):
            api.sort_geometry_along_axis(mock_geometry, mock_geometry_type, mock_axis)

        mock_read_only.assert_called_with(mock_geometry)

    def test_index_out_of_range(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_geometry_type = mocker.MagicMock(spec=hou.geometryType)

        with pytest.raises(ValueError):
            api.sort_geometry_along_axis(mock_geometry, mock_geometry_type, 4)

        mock_read_only.assert_called_with(mock_geometry)

    def test_invalid_type(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geo_type = hou.geometryType.Edges
        index = 1

        with pytest.raises(ValueError):
            api.sort_geometry_along_axis(mock_geometry, geo_type, index)

        mock_read_only.assert_called_with(mock_geometry)

    def test_points(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_get_owner = mocker.patch(
            "ht.inline.utils.get_attrib_owner_from_geometry_type"
        )
        mock_sort = mocker.patch("ht.inline.api._cpp_methods.sortGeometryAlongAxis")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geo_type = hou.geometryType.Points
        index = 1

        api.sort_geometry_along_axis(mock_geometry, geo_type, index)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geo_type)

        mock_sort.assert_called_with(mock_geometry, mock_get_owner.return_value, index)

    def test_prims(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_get_owner = mocker.patch(
            "ht.inline.utils.get_attrib_owner_from_geometry_type"
        )
        mock_sort = mocker.patch("ht.inline.api._cpp_methods.sortGeometryAlongAxis")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geo_type = hou.geometryType.Primitives
        index = 1

        api.sort_geometry_along_axis(mock_geometry, geo_type, index)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geo_type)

        mock_sort.assert_called_with(mock_geometry, mock_get_owner.return_value, index)


class Test_sort_geometry_by_values(object):
    """Test ht.inline.api.sort_geometry_by_values."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_geometry_type = mocker.MagicMock(spec=hou.geometryType)
        mock_values = mocker.MagicMock(spec=list)

        with pytest.raises(hou.GeometryPermissionError):
            api.sort_geometry_by_values(mock_geometry, mock_geometry_type, mock_values)

        mock_read_only.assert_called_with(mock_geometry)

    def test_points_mismatch(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_num_points = mocker.patch("ht.inline.api.num_points")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Points

        mock_values = mocker.MagicMock(spec=list)

        with pytest.raises(hou.OperationFailed):
            api.sort_geometry_by_values(mock_geometry, geometry_type, mock_values)

        mock_read_only.assert_called_with(mock_geometry)

        mock_num_points.assert_called_with(mock_geometry)

    def test_points(self, mocker, fix_hou_exceptions):
        num_pt = 3

        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_num_points = mocker.patch("ht.inline.api.num_points", return_value=num_pt)
        mock_get_owner = mocker.patch(
            "ht.inline.utils.get_attrib_owner_from_geometry_type"
        )
        mock_build = mocker.patch("ht.inline.utils.build_c_double_array")
        mock_sort = mocker.patch("ht.inline.api._cpp_methods.sortGeometryByValues")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Points

        mock_values = mocker.MagicMock(spec=list)

        mock_values.__len__.return_value = num_pt

        api.sort_geometry_by_values(mock_geometry, geometry_type, mock_values)

        mock_read_only.assert_called_with(mock_geometry)

        mock_num_points.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geometry_type)

        mock_build.assert_called_with(mock_values)

        mock_sort.assert_called_with(
            mock_geometry, mock_get_owner.return_value, mock_build.return_value
        )

    def test_prims_mismatch(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_num_prims = mocker.patch("ht.inline.api.num_prims")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Primitives

        mock_values = mocker.MagicMock(spec=list)

        with pytest.raises(hou.OperationFailed):
            api.sort_geometry_by_values(mock_geometry, geometry_type, mock_values)

        mock_read_only.assert_called_with(mock_geometry)

        mock_num_prims.assert_called_with(mock_geometry)

    def test_prims(self, mocker, fix_hou_exceptions):
        num_pr = 3

        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_num_prims = mocker.patch("ht.inline.api.num_prims", return_value=num_pr)
        mock_get_owner = mocker.patch(
            "ht.inline.utils.get_attrib_owner_from_geometry_type"
        )
        mock_build = mocker.patch("ht.inline.utils.build_c_double_array")
        mock_sort = mocker.patch("ht.inline.api._cpp_methods.sortGeometryByValues")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Primitives

        mock_values = mocker.MagicMock(spec=list)
        mock_values.__len__.return_value = num_pr

        api.sort_geometry_by_values(mock_geometry, geometry_type, mock_values)

        mock_read_only.assert_called_with(mock_geometry)

        mock_num_prims.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geometry_type)

        mock_build.assert_called_with(mock_values)

        mock_sort.assert_called_with(
            mock_geometry, mock_get_owner.return_value, mock_build.return_value
        )

    def test_invalid(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Edges

        mock_values = mocker.MagicMock(spec=list)

        with pytest.raises(ValueError):
            api.sort_geometry_by_values(mock_geometry, geometry_type, mock_values)

        mock_read_only.assert_called_with(mock_geometry)


class Test_sort_geometry_randomly(object):
    """Test ht.inline.api.sort_geometry_randomly."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geometry_type = mocker.MagicMock(spec=hou.geometryType)
        mock_seed = mocker.MagicMock(spec=int)

        with pytest.raises(hou.GeometryPermissionError):
            api.sort_geometry_randomly(mock_geometry, geometry_type, mock_seed)

        mock_read_only.assert_called_with(mock_geometry)

    def test_invalid_seed_type(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geometry_type = mocker.MagicMock(spec=hou.geometryType)
        mock_seed = mocker.MagicMock(spec=str)

        with pytest.raises(TypeError):
            api.sort_geometry_randomly(mock_geometry, geometry_type, mock_seed)

        mock_read_only.assert_called_with(mock_geometry)

    def test_invalid_geometry_type(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Edges

        mock_seed = mocker.MagicMock(spec=int)

        with pytest.raises(ValueError):
            api.sort_geometry_randomly(mock_geometry, geometry_type, mock_seed)

        mock_read_only.assert_called_with(mock_geometry)

    def test_points_int(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_get_owner = mocker.patch(
            "ht.inline.utils.get_attrib_owner_from_geometry_type"
        )
        mock_sort = mocker.patch("ht.inline.api._cpp_methods.sortGeometryRandomly")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Points
        mock_seed = mocker.MagicMock(spec=int)

        api.sort_geometry_randomly(mock_geometry, geometry_type, mock_seed)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geometry_type)

        mock_sort.assert_called_with(
            mock_geometry, mock_get_owner.return_value, mock_seed
        )

    def test_prims_float(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_get_owner = mocker.patch(
            "ht.inline.utils.get_attrib_owner_from_geometry_type"
        )
        mock_sort = mocker.patch("ht.inline.api._cpp_methods.sortGeometryRandomly")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Primitives
        mock_seed = mocker.MagicMock(spec=float)

        api.sort_geometry_randomly(mock_geometry, geometry_type, mock_seed)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geometry_type)

        mock_sort.assert_called_with(
            mock_geometry, mock_get_owner.return_value, mock_seed
        )


class Test_shift_geometry_elements(object):
    """Test ht.inline.api.shift_geometry_elements."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geometry_type = mocker.MagicMock(spec=hou.geometryType)
        mock_offset = mocker.MagicMock(spec=int)

        with pytest.raises(hou.GeometryPermissionError):
            api.shift_geometry_elements(mock_geometry, geometry_type, mock_offset)

        mock_read_only.assert_called_with(mock_geometry)

    def test_invalid_offset_type(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geometry_type = mocker.MagicMock(spec=hou.geometryType)
        mock_offset = mocker.MagicMock(spec=float)

        with pytest.raises(TypeError):
            api.shift_geometry_elements(mock_geometry, geometry_type, mock_offset)

        mock_read_only.assert_called_with(mock_geometry)

    def test_invalid_geometry_type(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Edges
        mock_offset = mocker.MagicMock(spec=int)

        with pytest.raises(ValueError):
            api.shift_geometry_elements(mock_geometry, geometry_type, mock_offset)

        mock_read_only.assert_called_with(mock_geometry)

    def test_points(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_get_owner = mocker.patch(
            "ht.inline.utils.get_attrib_owner_from_geometry_type"
        )
        mock_shift = mocker.patch("ht.inline.api._cpp_methods.shiftGeometry")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Points
        mock_offset = mocker.MagicMock(spec=int)

        api.shift_geometry_elements(mock_geometry, geometry_type, mock_offset)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geometry_type)

        mock_shift.assert_called_with(
            mock_geometry, mock_get_owner.return_value, mock_offset
        )

    def test_prims(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_get_owner = mocker.patch(
            "ht.inline.utils.get_attrib_owner_from_geometry_type"
        )
        mock_shift = mocker.patch("ht.inline.api._cpp_methods.shiftGeometry")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Primitives
        mock_offset = mocker.MagicMock(spec=int)

        api.shift_geometry_elements(mock_geometry, geometry_type, mock_offset)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geometry_type)

        mock_shift.assert_called_with(
            mock_geometry, mock_get_owner.return_value, mock_offset
        )


class Test_reverse_sort_geometry(object):
    """Test ht.inline.api.reverse_sort_geometry."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geometry_type = mocker.MagicMock(spec=hou.geometryType)

        with pytest.raises(hou.GeometryPermissionError):
            api.reverse_sort_geometry(mock_geometry, geometry_type)

        mock_read_only.assert_called_with(mock_geometry)

    def test_invalid_geometry_type(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Edges

        with pytest.raises(ValueError):
            api.reverse_sort_geometry(mock_geometry, geometry_type)

        mock_read_only.assert_called_with(mock_geometry)

    def test_points(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_get_owner = mocker.patch(
            "ht.inline.utils.get_attrib_owner_from_geometry_type"
        )
        mock_reverse = mocker.patch("ht.inline.api._cpp_methods.reverseSortGeometry")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Points

        api.reverse_sort_geometry(mock_geometry, geometry_type)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geometry_type)

        mock_reverse.assert_called_with(mock_geometry, mock_get_owner.return_value)

    def test_prims(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_get_owner = mocker.patch(
            "ht.inline.utils.get_attrib_owner_from_geometry_type"
        )
        mock_reverse = mocker.patch("ht.inline.api._cpp_methods.reverseSortGeometry")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Primitives

        api.reverse_sort_geometry(mock_geometry, geometry_type)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geometry_type)

        mock_reverse.assert_called_with(mock_geometry, mock_get_owner.return_value)


class Test_sort_geometry_by_proximity_to_position(object):
    """Test ht.inline.api.sort_geometry_by_proximity_to_position."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geometry_type = mocker.MagicMock(spec=hou.geometryType)
        mock_pos = mocker.MagicMock(spec=hou.Vector3)

        with pytest.raises(hou.GeometryPermissionError):
            api.sort_geometry_by_proximity_to_position(
                mock_geometry, geometry_type, mock_pos
            )

        mock_read_only.assert_called_with(mock_geometry)

    def test_invalid_geometry_type(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Edges
        mock_pos = mocker.MagicMock(spec=hou.Vector3)

        with pytest.raises(ValueError):
            api.sort_geometry_by_proximity_to_position(
                mock_geometry, geometry_type, mock_pos
            )

        mock_read_only.assert_called_with(mock_geometry)

    def test_points(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_get_owner = mocker.patch(
            "ht.inline.utils.get_attrib_owner_from_geometry_type"
        )
        mock_proximity = mocker.patch(
            "ht.inline.api._cpp_methods.sortGeometryByProximity"
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Points
        mock_pos = mocker.MagicMock(spec=hou.Vector3)

        api.sort_geometry_by_proximity_to_position(
            mock_geometry, geometry_type, mock_pos
        )

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geometry_type)

        mock_proximity.assert_called_with(
            mock_geometry, mock_get_owner.return_value, mock_pos
        )

    def test_prims(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_get_owner = mocker.patch(
            "ht.inline.utils.get_attrib_owner_from_geometry_type"
        )
        mock_proximity = mocker.patch(
            "ht.inline.api._cpp_methods.sortGeometryByProximity"
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        geometry_type = hou.geometryType.Primitives
        mock_pos = mocker.MagicMock(spec=hou.Vector3)

        api.sort_geometry_by_proximity_to_position(
            mock_geometry, geometry_type, mock_pos
        )

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_owner.assert_called_with(geometry_type)

        mock_proximity.assert_called_with(
            mock_geometry, mock_get_owner.return_value, mock_pos
        )


class Test_sort_geometry_by_vertex_order(object):
    """Test ht.inline.api.sort_geometry_by_vertex_order."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        with pytest.raises(hou.GeometryPermissionError):
            api.sort_geometry_by_vertex_order(mock_geometry)

        mock_read_only.assert_called_with(mock_geometry)

    def test_invalid_geometry_type(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_sort = mocker.patch("ht.inline.api._cpp_methods.sortGeometryByVertexOrder")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        api.sort_geometry_by_vertex_order(mock_geometry)

        mock_read_only.assert_called_with(mock_geometry)
        mock_sort.assert_called_with(mock_geometry)


class Test_sort_geometry_by_expression(object):
    """Test ht.inline.api.sort_geometry_by_expression."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_geometry_type = mocker.MagicMock(spec=hou.geometryType.Points)
        mock_expression = mocker.MagicMock(spec=str)

        with pytest.raises(hou.GeometryPermissionError):
            api.sort_geometry_by_expression(
                mock_geometry, mock_geometry_type, mock_expression
            )

        mock_read_only.assert_called_with(mock_geometry)

    def test_points(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_pwd = mocker.patch("ht.inline.api.hou.pwd")
        mock_hscript = mocker.patch("ht.inline.api.hou.hscriptExpression")
        mock_sort = mocker.patch("ht.inline.api.sort_geometry_by_values")

        mock_pt1 = mocker.MagicMock(spec=hou.Point)
        mock_pt2 = mocker.MagicMock(spec=hou.Point)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_geometry.points.return_value = (mock_pt1, mock_pt2)

        geometry_type = hou.geometryType.Points
        mock_expression = mocker.MagicMock(spec=str)

        mock_sopnode = mocker.MagicMock(spec=hou.SopNode)
        mock_pwd.return_value = mock_sopnode

        api.sort_geometry_by_expression(mock_geometry, geometry_type, mock_expression)

        mock_read_only.assert_called_with(mock_geometry)

        mock_sopnode.setCurPoint.assert_has_calls(
            [mocker.call(mock_pt1), mocker.call(mock_pt2)]
        )

        mock_hscript.assert_called_with(mock_expression)
        assert mock_hscript.call_count == 2

        mock_sort.assert_called_with(
            mock_geometry,
            geometry_type,
            [mock_hscript.return_value, mock_hscript.return_value],
        )

    def test_prims(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_pwd = mocker.patch("ht.inline.api.hou.pwd")
        mock_hscript = mocker.patch("ht.inline.api.hou.hscriptExpression")
        mock_sort = mocker.patch("ht.inline.api.sort_geometry_by_values")

        mock_pr1 = mocker.MagicMock(spec=hou.Prim)
        mock_pr2 = mocker.MagicMock(spec=hou.Prim)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_geometry.prims.return_value = (mock_pr1, mock_pr2)

        geometry_type = hou.geometryType.Primitives
        mock_expression = mocker.MagicMock(spec=str)

        mock_sopnode = mocker.MagicMock(spec=hou.SopNode)
        mock_pwd.return_value = mock_sopnode

        api.sort_geometry_by_expression(mock_geometry, geometry_type, mock_expression)

        mock_read_only.assert_called_with(mock_geometry)

        mock_sopnode.setCurPrim.assert_has_calls(
            [mocker.call(mock_pr1), mocker.call(mock_pr2)]
        )

        mock_hscript.assert_called_with(mock_expression)
        assert mock_hscript.call_count == 2

        mock_sort.assert_called_with(
            mock_geometry,
            geometry_type,
            [mock_hscript.return_value, mock_hscript.return_value],
        )

    def test_invalid_type(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_pwd = mocker.patch("ht.inline.api.hou.pwd")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        geometry_type = hou.geometryType.Edges
        mock_expression = mocker.MagicMock(spec=str)

        mock_sopnode = mocker.MagicMock(spec=hou.SopNode)
        mock_pwd.return_value = mock_sopnode

        with pytest.raises(ValueError):
            api.sort_geometry_by_expression(
                mock_geometry, geometry_type, mock_expression
            )

        mock_read_only.assert_called_with(mock_geometry)


class Test_create_point_at_position(object):
    """Test ht.inline.api.create_point_at_position."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_pos = mocker.MagicMock(spec=hou.Vector3)

        with pytest.raises(hou.GeometryPermissionError):
            api.create_point_at_position(mock_geometry, mock_pos)

        mock_read_only.assert_called_with(mock_geometry)

    def test(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_create = mocker.patch("ht.inline.api._cpp_methods.createPointAtPosition")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_pos = mocker.MagicMock(spec=hou.Vector3)

        result = api.create_point_at_position(mock_geometry, mock_pos)

        assert result == mock_geometry.iterPoints.return_value.__getitem__.return_value

        mock_read_only.assert_called_with(mock_geometry)

        mock_create.assert_called_with(mock_geometry, mock_pos)

        mock_geometry.iterPoints.return_value.__getitem__.assert_called_with(-1)


class Test_create_n_points(object):
    """Test ht.inline.api.create_n_points."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_npoints = mocker.MagicMock(spec=int)

        with pytest.raises(hou.GeometryPermissionError):
            api.create_n_points(mock_geometry, mock_npoints)

        mock_read_only.assert_called_with(mock_geometry)

    def test_n_0(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        npoints = 0

        with pytest.raises(ValueError):
            api.create_n_points(mock_geometry, npoints)

        mock_read_only.assert_called_with(mock_geometry)

    def test_n_negative(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        npoints = -1

        with pytest.raises(ValueError):
            api.create_n_points(mock_geometry, npoints)

        mock_read_only.assert_called_with(mock_geometry)

    def test(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_create = mocker.patch("ht.inline.api._cpp_methods.createNPoints")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        npoints = 10

        result = api.create_n_points(mock_geometry, npoints)

        assert result == tuple(
            mock_geometry.points.return_value.__getitem__.return_value
        )

        mock_read_only.assert_called_with(mock_geometry)

        mock_create.assert_called_with(mock_geometry, npoints)

        mock_geometry.points.return_value.__getitem__.assert_called_with(
            slice(-npoints, None, None)
        )


class Test_merge_point_group(object):
    """Test ht.inline.api.merge_point_group."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_group = mocker.MagicMock(spec=hou.PointGroup)

        with pytest.raises(hou.GeometryPermissionError):
            api.merge_point_group(mock_geometry, mock_group)

        mock_read_only.assert_called_with(mock_geometry)

    def test_not_point_group(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_group = mocker.MagicMock(spec=hou.PrimGroup)

        with pytest.raises(ValueError):
            api.merge_point_group(mock_geometry, mock_group)

        mock_read_only.assert_called_with(mock_geometry)

    def test(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_merge = mocker.patch("ht.inline.api._cpp_methods.mergePointGroup")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_group = mocker.MagicMock(spec=hou.PointGroup)

        api.merge_point_group(mock_geometry, mock_group)

        mock_read_only.assert_called_with(mock_geometry)
        mock_merge.assert_called_with(
            mock_geometry,
            mock_group.geometry.return_value,
            mock_group.name.return_value,
        )


class Test_merge_points(object):
    """Test ht.inline.api.merge_points."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_points = mocker.MagicMock(spec=list)

        with pytest.raises(hou.GeometryPermissionError):
            api.merge_points(mock_geometry, mock_points)

        mock_read_only.assert_called_with(mock_geometry)

    def test(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_build = mocker.patch("ht.inline.utils.build_c_int_array")
        mock_merge = mocker.patch("ht.inline.api._cpp_methods.mergePoints")
        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_pt1 = mocker.MagicMock(spec=hou.Point)
        mock_pt2 = mocker.MagicMock(spec=hou.Point)

        points = [mock_pt1, mock_pt2]

        api.merge_points(mock_geometry, points)

        mock_read_only.assert_called_with(mock_geometry)

        mock_build.assert_called_with(
            [mock_pt1.number.return_value, mock_pt2.number.return_value]
        )

        mock_merge.assert_called_with(
            mock_geometry,
            mock_pt1.geometry.return_value,
            mock_build.return_value,
            len(mock_build.return_value),
        )


class Test_merge_prim_group(object):
    """Test ht.inline.api.merge_prim_group."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_group = mocker.MagicMock(spec=hou.PrimGroup)

        with pytest.raises(hou.GeometryPermissionError):
            api.merge_prim_group(mock_geometry, mock_group)

        mock_read_only.assert_called_with(mock_geometry)

    def test_not_prim_group(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_group = mocker.MagicMock(spec=hou.PointGroup)

        with pytest.raises(ValueError):
            api.merge_prim_group(mock_geometry, mock_group)

        mock_read_only.assert_called_with(mock_geometry)

    def test(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_merge = mocker.patch("ht.inline.api._cpp_methods.mergePrimGroup")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_group = mocker.MagicMock(spec=hou.PrimGroup)

        api.merge_prim_group(mock_geometry, mock_group)

        mock_read_only.assert_called_with(mock_geometry)
        mock_merge.assert_called_with(
            mock_geometry,
            mock_group.geometry.return_value,
            mock_group.name.return_value,
        )


class Test_merge_prims(object):
    """Test ht.inline.api.merge_prims."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_prims = mocker.MagicMock(spec=list)

        with pytest.raises(hou.GeometryPermissionError):
            api.merge_prims(mock_geometry, mock_prims)

        mock_read_only.assert_called_with(mock_geometry)

    def test(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_build = mocker.patch("ht.inline.utils.build_c_int_array")
        mock_merge = mocker.patch("ht.inline.api._cpp_methods.mergePrims")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_pr1 = mocker.MagicMock(spec=hou.Point)
        mock_pr2 = mocker.MagicMock(spec=hou.Point)

        points = [mock_pr1, mock_pr2]

        api.merge_prims(mock_geometry, points)

        mock_read_only.assert_called_with(mock_geometry)

        mock_build.assert_called_with(
            [mock_pr1.number.return_value, mock_pr2.number.return_value]
        )

        mock_merge.assert_called_with(
            mock_geometry,
            mock_pr1.geometry.return_value,
            mock_build.return_value,
            len(mock_build.return_value),
        )


class Test_copy_attribute_values(object):
    """Test ht.inline.api.copy_attribute_values."""

    def test_vertex_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_source = mocker.MagicMock(spec=hou.Vertex)
        mock_attribs = mocker.MagicMock(spec=list)

        mock_target = mocker.MagicMock(spec=hou.Vertex)

        mock_target_geo = mocker.MagicMock(spec=hou.Geometry)
        mock_target.geometry.return_value = mock_target_geo

        with pytest.raises(hou.GeometryPermissionError):
            api.copy_attribute_values(mock_source, mock_attribs, mock_target)

        mock_target.linearNumber.assert_called()
        mock_read_only.assert_called_with(mock_target_geo)

    def test_vertex(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_owner_from_type = mocker.patch(
            "ht.inline.utils.get_attrib_owner_from_geometry_entity_type"
        )
        mock_build = mocker.patch("ht.inline.utils.build_c_string_array")
        mock_get_owner = mocker.patch("ht.inline.utils.get_attrib_owner")
        mock_copy = mocker.patch("ht.inline.api._cpp_methods.copyAttributeValues")

        mock_source_node = mocker.MagicMock(spec=hou.SopNode)

        mock_source_geo = mocker.MagicMock(spec=hou.Geometry)
        mock_source_geo.sopNode.return_value = mock_source_node

        mock_source = mocker.MagicMock(spec=hou.Vertex)
        mock_source.geometry.return_value = mock_source_geo

        mock_attrib1 = mocker.MagicMock(spec=hou.Attrib)
        mock_attrib1.geometry.return_value = mocker.MagicMock()

        mock_attrib2 = mocker.MagicMock(spec=hou.Attrib)
        mock_attrib2.geometry.return_value.sopNode.return_value = mock_source_node

        mock_attrib3 = mocker.MagicMock(spec=hou.Attrib)
        mock_attrib3.geometry.return_value.sopNode.return_value = mock_source_node

        attribs = [mock_attrib1, mock_attrib2, mock_attrib3]

        mock_target_geo = mocker.MagicMock(spec=hou.Geometry)

        mock_target = mocker.MagicMock(spec=hou.Vertex)
        mock_target.geometry.return_value = mock_target_geo

        mock_target_owner = mocker.MagicMock(spec=int)
        mock_source_owner = mocker.MagicMock(spec=int)

        mock_get_owner.side_effect = (
            mock_source_owner,
            mock_source_owner,
            mocker.MagicMock(spec=int),
        )

        mock_owner_from_type.side_effect = (mock_target_owner, mock_source_owner)

        api.copy_attribute_values(mock_source, attribs, mock_target)

        mock_target.linearNumber.assert_called()
        mock_read_only.assert_called_with(mock_target_geo)

        mock_owner_from_type.assert_has_calls(
            [mocker.call(type(mock_target)), mocker.call(type(mock_source))]
        )

        mock_get_owner.assert_has_calls(
            [
                mocker.call(mock_attrib1.type.return_value),
                mocker.call(mock_attrib2.type.return_value),
                mocker.call(mock_attrib3.type.return_value),
            ]
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
            len(mock_build.return_value),
        )

    def test_point(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_owner_from_type = mocker.patch(
            "ht.inline.utils.get_attrib_owner_from_geometry_entity_type"
        )
        mock_build = mocker.patch("ht.inline.utils.build_c_string_array")
        mock_get_owner = mocker.patch("ht.inline.utils.get_attrib_owner")
        mock_copy = mocker.patch("ht.inline.api._cpp_methods.copyAttributeValues")

        mock_source_node = mocker.MagicMock(spec=hou.SopNode)

        mock_source_geo = mocker.MagicMock(spec=hou.Geometry)
        mock_source_geo.sopNode.return_value = mock_source_node

        mock_source = mocker.MagicMock(spec=hou.Point)
        mock_source.geometry.return_value = mock_source_geo

        mock_attrib1 = mocker.MagicMock(spec=hou.Attrib)
        mock_attrib1.geometry.return_value = mocker.MagicMock()

        mock_attrib2 = mocker.MagicMock(spec=hou.Attrib)
        mock_attrib2.geometry.return_value.sopNode.return_value = mock_source_node

        mock_attrib3 = mocker.MagicMock(spec=hou.Attrib)
        mock_attrib3.geometry.return_value.sopNode.return_value = mock_source_node

        attribs = [mock_attrib1, mock_attrib2, mock_attrib3]

        mock_target_geo = mocker.MagicMock(spec=hou.Geometry)

        mock_target = mocker.MagicMock(spec=hou.Point)
        mock_target.geometry.return_value = mock_target_geo

        mock_target_owner = mocker.MagicMock(spec=int)
        mock_source_owner = mocker.MagicMock(spec=int)

        mock_get_owner.side_effect = (
            mock_source_owner,
            mock_source_owner,
            mocker.MagicMock(spec=int),
        )

        mock_owner_from_type.side_effect = (mock_target_owner, mock_source_owner)

        api.copy_attribute_values(mock_source, attribs, mock_target)

        mock_target.number.assert_called()
        mock_read_only.assert_called_with(mock_target_geo)

        mock_owner_from_type.assert_has_calls(
            [mocker.call(type(mock_target)), mocker.call(type(mock_source))]
        )

        mock_get_owner.assert_has_calls(
            [
                mocker.call(mock_attrib1.type.return_value),
                mocker.call(mock_attrib2.type.return_value),
                mocker.call(mock_attrib3.type.return_value),
            ]
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
            len(mock_build.return_value),
        )

    def test_geometry(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_owner_from_type = mocker.patch(
            "ht.inline.utils.get_attrib_owner_from_geometry_entity_type"
        )
        mock_build = mocker.patch("ht.inline.utils.build_c_string_array")
        mock_get_owner = mocker.patch("ht.inline.utils.get_attrib_owner")
        mock_copy = mocker.patch("ht.inline.api._cpp_methods.copyAttributeValues")

        mock_source_node = mocker.MagicMock(spec=hou.SopNode)

        mock_source = mocker.MagicMock(spec=hou.Geometry)
        mock_source.sopNode.return_value = mock_source_node

        mock_attrib1 = mocker.MagicMock(spec=hou.Attrib)
        mock_attrib1.geometry.return_value = mocker.MagicMock()

        mock_attrib2 = mocker.MagicMock(spec=hou.Attrib)
        mock_attrib2.geometry.return_value.sopNode.return_value = mock_source_node

        mock_attrib3 = mocker.MagicMock(spec=hou.Attrib)
        mock_attrib3.geometry.return_value.sopNode.return_value = mock_source_node

        attribs = [mock_attrib1, mock_attrib2, mock_attrib3]

        mock_target = mocker.MagicMock(spec=hou.Geometry)

        mock_target_owner = mocker.MagicMock(spec=int)
        mock_source_owner = mocker.MagicMock(spec=int)

        mock_get_owner.side_effect = (
            mock_source_owner,
            mock_source_owner,
            mocker.MagicMock(spec=int),
        )

        mock_owner_from_type.side_effect = (mock_target_owner, mock_source_owner)

        api.copy_attribute_values(mock_source, attribs, mock_target)

        mock_read_only.assert_called_with(mock_target)

        mock_owner_from_type.assert_has_calls(
            [mocker.call(type(mock_target)), mocker.call(type(mock_source))]
        )

        mock_get_owner.assert_has_calls(
            [
                mocker.call(mock_attrib1.type.return_value),
                mocker.call(mock_attrib2.type.return_value),
                mocker.call(mock_attrib3.type.return_value),
            ]
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
            len(mock_build.return_value),
        )


def test_point_adjacent_polygons(mocker):
    """Test ht.inline.api.point_adjacent_polygons."""
    mock_adjacent = mocker.patch("ht.inline.api._cpp_methods.pointAdjacentPolygons")
    mock_get = mocker.patch("ht.inline.api.utils.get_prims_from_list")

    mock_prim = mocker.MagicMock(spec=hou.Prim)

    result = api.point_adjacent_polygons(mock_prim)

    assert result == mock_get.return_value

    mock_adjacent.assert_called_with(
        mock_prim.geometry.return_value, mock_prim.number.return_value
    )
    mock_get.assert_called_with(
        mock_prim.geometry.return_value, mock_adjacent.return_value
    )


def test_edge_adjacent_polygons(mocker):
    """Test ht.inline.api.edge_adjacent_polygons."""
    mock_adjacent = mocker.patch("ht.inline.api._cpp_methods.edgeAdjacentPolygons")
    mock_get = mocker.patch("ht.inline.api.utils.get_prims_from_list")

    mock_prim = mocker.MagicMock(spec=hou.Prim)

    result = api.edge_adjacent_polygons(mock_prim)

    assert result == mock_get.return_value

    mock_adjacent.assert_called_with(
        mock_prim.geometry.return_value, mock_prim.number.return_value
    )
    mock_get.assert_called_with(
        mock_prim.geometry.return_value, mock_adjacent.return_value
    )


def test_connected_points(mocker):
    """Test ht.inline.api.connected_points."""
    mock_connected = mocker.patch("ht.inline.api._cpp_methods.connectedPoints")
    mock_get = mocker.patch("ht.inline.api.utils.get_points_from_list")

    mock_point = mocker.MagicMock(spec=hou.Point)

    result = api.connected_points(mock_point)

    assert result == mock_get.return_value

    mock_connected.assert_called_with(
        mock_point.geometry.return_value, mock_point.number.return_value
    )
    mock_get.assert_called_with(
        mock_point.geometry.return_value, mock_connected.return_value
    )


def test_connected_prims(mocker):
    """Test ht.inline.api.connected_prims."""
    mock_connected = mocker.patch("ht.inline.api._cpp_methods.connectedPrims")
    mock_get = mocker.patch("ht.inline.api.utils.get_prims_from_list")

    mock_point = mocker.MagicMock(spec=hou.Point)

    result = api.connected_prims(mock_point)

    assert result == mock_get.return_value

    mock_connected.assert_called_with(
        mock_point.geometry.return_value, mock_point.number.return_value
    )
    mock_get.assert_called_with(
        mock_point.geometry.return_value, mock_connected.return_value
    )


def test_referencing_vertices(mocker):
    """Test ht.inline.api.referencing_vertices."""
    mock_referencing = mocker.patch("ht.inline.api._cpp_methods.referencingVertices")

    mock_point = mocker.MagicMock(spec=hou.Prim)

    mock_result = mocker.MagicMock()
    mock_result.prims = list(range(3))
    mock_result.indices = reversed(list(range(3)))

    mock_referencing.return_value = mock_result

    result = api.referencing_vertices(mock_point)

    assert result == mock_point.geometry.return_value.globVertices.return_value

    mock_referencing.assert_called_with(
        mock_point.geometry.return_value, mock_point.number.return_value
    )

    mock_point.geometry.return_value.globVertices.assert_called_with("0v2 1v1 2v0")


class Test_string_table_indices(object):
    """Test ht.inline.api.string_table_indices."""

    def test_not_string(self, mocker):
        mock_attrib = mocker.MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.Float

        with pytest.raises(ValueError):
            api.string_table_indices(mock_attrib)

    def test(self, mocker):
        mock_owner = mocker.patch("ht.inline.utils.get_attrib_owner")
        mock_get = mocker.patch("ht.inline.api._cpp_methods.getStringTableIndices")

        mock_attrib = mocker.MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.String

        result = api.string_table_indices(mock_attrib)

        assert result == tuple(mock_get.return_value)

        mock_owner.assert_called_with(mock_attrib.type.return_value)
        mock_get.assert_called_with(
            mock_attrib.geometry.return_value,
            mock_owner.return_value,
            mock_attrib.name.return_value,
        )


class Test_vertex_string_attrib_values(object):
    """Test ht.inline.api.vertex_string_attrib_values."""

    def test_invalid_attribute(self, mocker, fix_hou_exceptions):
        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_geometry.findVertexAttrib.return_value = None

        mock_name = mocker.MagicMock(spec=str)

        with pytest.raises(hou.OperationFailed):
            api.vertex_string_attrib_values(mock_geometry, mock_name)

        mock_geometry.findVertexAttrib.assert_called_with(mock_name)

    def test_not_string(self, mocker, fix_hou_exceptions):
        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)

        mock_attrib = mocker.MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.Float

        mock_geometry.findVertexAttrib.return_value = mock_attrib

        with pytest.raises(ValueError):
            api.vertex_string_attrib_values(mock_geometry, mock_name)

        mock_geometry.findVertexAttrib.assert_called_with(mock_name)

    def test(self, mocker, fix_hou_exceptions):
        mock_get = mocker.patch("ht.inline.api._cpp_methods.vertexStringAttribValues")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)

        mock_attrib = mocker.MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.String

        mock_geometry.findVertexAttrib.return_value = mock_attrib

        result = api.vertex_string_attrib_values(mock_geometry, mock_name)

        assert result == mock_get.return_value

        mock_geometry.findVertexAttrib.assert_called_with(mock_name)
        mock_get.assert_called_with(mock_geometry, mock_name)


class Test_set_vertex_string_attrib_values(object):
    """Test ht.inline.api.set_vertex_string_attrib_values."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=True)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)
        mock_values = mocker.MagicMock(spec=list)

        with pytest.raises(hou.GeometryPermissionError):
            api.set_vertex_string_attrib_values(mock_geometry, mock_name, mock_values)

    def test_invalid_attribute(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_geometry.findVertexAttrib.return_value = None

        mock_name = mocker.MagicMock(spec=str)
        mock_values = mocker.MagicMock(spec=list)

        with pytest.raises(hou.OperationFailed):
            api.set_vertex_string_attrib_values(mock_geometry, mock_name, mock_values)

        mock_geometry.findVertexAttrib.assert_called_with(mock_name)

    def test_not_string(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)
        mock_values = mocker.MagicMock(spec=list)

        mock_attrib = mocker.MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.Float

        mock_geometry.findVertexAttrib.return_value = mock_attrib

        with pytest.raises(ValueError):
            api.set_vertex_string_attrib_values(mock_geometry, mock_name, mock_values)

        mock_geometry.findVertexAttrib.assert_called_with(mock_name)

    def test_no_size_match(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_num = mocker.patch("ht.inline.api.num_vertices")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)
        mock_values = mocker.MagicMock(spec=list)

        mock_attrib = mocker.MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.String

        mock_geometry.findVertexAttrib.return_value = mock_attrib

        with pytest.raises(ValueError):
            api.set_vertex_string_attrib_values(mock_geometry, mock_name, mock_values)

        mock_geometry.findVertexAttrib.assert_called_with(mock_name)
        mock_num.assert_called_with(mock_geometry)

    def test(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_num = mocker.patch("ht.inline.api.num_vertices")
        mock_build = mocker.patch("ht.inline.utils.build_c_string_array")
        mock_set = mocker.patch(
            "ht.inline.api._cpp_methods.setVertexStringAttribValues"
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)

        size = 5
        mock_values = mocker.MagicMock(spec=list)
        mock_values.__len__.return_value = size
        mock_num.return_value = size

        mock_attrib = mocker.MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.String

        mock_geometry.findVertexAttrib.return_value = mock_attrib

        api.set_vertex_string_attrib_values(mock_geometry, mock_name, mock_values)

        mock_geometry.findVertexAttrib.assert_called_with(mock_name)
        mock_num.assert_called_with(mock_geometry)

        mock_build.assert_called_with(mock_values)

        mock_set.assert_called_with(
            mock_geometry,
            mock_name,
            mock_build.return_value,
            len(mock_build.return_value),
        )


class Test_set_shared_point_string_attrib(object):
    """Test ht.inline.api.set_shared_point_string_attrib."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=True)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)
        mock_value = mocker.MagicMock(spec=str)

        with pytest.raises(hou.GeometryPermissionError):
            api.set_shared_point_string_attrib(mock_geometry, mock_name, mock_value)

    def test_invalid_attribute(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)
        mock_value = mocker.MagicMock(spec=str)

        mock_geometry.findPointAttrib.return_value = None

        with pytest.raises(ValueError):
            api.set_shared_point_string_attrib(mock_geometry, mock_name, mock_value)

        mock_geometry.findPointAttrib.assert_called_with(mock_name)

    def test_not_string(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)
        mock_value = mocker.MagicMock(spec=str)

        mock_attrib = mocker.MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.Float

        mock_geometry.findPointAttrib.return_value = mock_attrib

        with pytest.raises(ValueError):
            api.set_shared_point_string_attrib(mock_geometry, mock_name, mock_value)

        mock_geometry.findPointAttrib.assert_called_with(mock_name)

    def test_default(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_owner = mocker.patch("ht.inline.utils.get_attrib_owner")
        mock_set = mocker.patch("ht.inline.api._cpp_methods.setSharedStringAttrib")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)
        mock_value = mocker.MagicMock(spec=str)

        mock_attrib = mocker.MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.String

        mock_geometry.findPointAttrib.return_value = mock_attrib

        api.set_shared_point_string_attrib(mock_geometry, mock_name, mock_value)

        mock_geometry.findPointAttrib.assert_called_with(mock_name)

        mock_owner.assert_called_with(mock_attrib.type.return_value)
        mock_set.assert_called_with(
            mock_geometry, mock_owner.return_value, mock_name, mock_value, 0
        )

    def test_group(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_owner = mocker.patch("ht.inline.utils.get_attrib_owner")
        mock_set = mocker.patch("ht.inline.api._cpp_methods.setSharedStringAttrib")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)
        mock_value = mocker.MagicMock(spec=str)
        mock_group = mocker.MagicMock(spec=hou.PointGroup)

        mock_attrib = mocker.MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.String

        mock_geometry.findPointAttrib.return_value = mock_attrib

        api.set_shared_point_string_attrib(
            mock_geometry, mock_name, mock_value, mock_group
        )

        mock_geometry.findPointAttrib.assert_called_with(mock_name)

        mock_owner.assert_called_with(mock_attrib.type.return_value)
        mock_set.assert_called_with(
            mock_geometry,
            mock_owner.return_value,
            mock_name,
            mock_value,
            mock_group.name.return_value,
        )


class Test_set_shared_prim_string_attrib(object):
    """Test ht.inline.api.set_shared_prim_string_attrib."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=True)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)
        mock_value = mocker.MagicMock(spec=str)

        with pytest.raises(hou.GeometryPermissionError):
            api.set_shared_prim_string_attrib(mock_geometry, mock_name, mock_value)

    def test_invalid_attribute(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)
        mock_value = mocker.MagicMock(spec=str)

        mock_geometry.findPrimAttrib.return_value = None

        with pytest.raises(ValueError):
            api.set_shared_prim_string_attrib(mock_geometry, mock_name, mock_value)

        mock_geometry.findPrimAttrib.assert_called_with(mock_name)

    def test_not_string(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)
        mock_value = mocker.MagicMock(spec=str)

        mock_attrib = mocker.MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.Float

        mock_geometry.findPrimAttrib.return_value = mock_attrib

        with pytest.raises(ValueError):
            api.set_shared_prim_string_attrib(mock_geometry, mock_name, mock_value)

        mock_geometry.findPrimAttrib.assert_called_with(mock_name)

    def test_default(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_owner = mocker.patch("ht.inline.utils.get_attrib_owner")
        mock_set = mocker.patch("ht.inline.api._cpp_methods.setSharedStringAttrib")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)
        mock_value = mocker.MagicMock(spec=str)

        mock_attrib = mocker.MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.String

        mock_geometry.findPrimAttrib.return_value = mock_attrib

        api.set_shared_prim_string_attrib(mock_geometry, mock_name, mock_value)

        mock_geometry.findPrimAttrib.assert_called_with(mock_name)

        mock_owner.assert_called_with(mock_attrib.type.return_value)
        mock_set.assert_called_with(
            mock_geometry, mock_owner.return_value, mock_name, mock_value, 0
        )

    def test_group(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_owner = mocker.patch("ht.inline.utils.get_attrib_owner")
        mock_set = mocker.patch("ht.inline.api._cpp_methods.setSharedStringAttrib")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_name = mocker.MagicMock(spec=str)
        mock_value = mocker.MagicMock(spec=str)
        mock_group = mocker.MagicMock(spec=hou.PointGroup)

        mock_attrib = mocker.MagicMock(spec=hou.Attrib)
        mock_attrib.dataType.return_value = hou.attribData.String

        mock_geometry.findPrimAttrib.return_value = mock_attrib

        api.set_shared_prim_string_attrib(
            mock_geometry, mock_name, mock_value, mock_group
        )

        mock_geometry.findPrimAttrib.assert_called_with(mock_name)

        mock_owner.assert_called_with(mock_attrib.type.return_value)
        mock_set.assert_called_with(
            mock_geometry,
            mock_owner.return_value,
            mock_name,
            mock_value,
            mock_group.name.return_value,
        )


def test_face_has_edge(mocker):
    """Test ht.inline.api.face_has_edge."""
    mock_has = mocker.patch("ht.inline.api._cpp_methods.faceHasEdge")

    mock_face = mocker.MagicMock(spec=hou.Face)
    mock_pt1 = mocker.MagicMock(spec=hou.Point)
    mock_pt2 = mocker.MagicMock(spec=hou.Point)

    result = api.face_has_edge(mock_face, mock_pt1, mock_pt2)

    assert result == mock_has.return_value

    mock_has.assert_called_with(
        mock_face.geometry.return_value,
        mock_face.number.return_value,
        mock_pt1.number.return_value,
        mock_pt2.number.return_value,
    )


def test_shared_edges(mocker):
    """Test ht.inline.api.shared_edges."""
    mock_connected = mocker.patch("ht.inline.api.connected_points")
    mock_has = mocker.patch("ht.inline.api.face_has_edge")

    mock_geometry = mocker.MagicMock(spec=hou.Geometry)

    mock_point1 = mocker.MagicMock(spec=hou.Point)
    mock_point1.number.return_value = 1

    mock_vertex1 = mocker.MagicMock(spec=hou.Vertex)
    mock_vertex1.point.return_value = mock_point1

    mock_point2 = mocker.MagicMock(spec=hou.Point)
    mock_point2.number.return_value = 2

    mock_vertex2 = mocker.MagicMock(spec=hou.Vertex)
    mock_vertex2.point.return_value = mock_point2

    mock_point3 = mocker.MagicMock(spec=hou.Point)
    mock_point3.number.return_value = 3

    mock_vertex3 = mocker.MagicMock(spec=hou.Vertex)
    mock_vertex3.point.return_value = mock_point3

    mock_face1 = mocker.MagicMock(spec=hou.Face)
    mock_face1.geometry.return_value = mock_geometry
    mock_face1.vertices.return_value = (mock_vertex1, mock_vertex2, mock_vertex3)

    mock_connected.side_effect = (
        (mock_point2, mock_point3),
        (mock_point3, mock_point1),
        (mock_point1, mock_point2),
    )

    mock_face2 = mocker.MagicMock(spec=hou.Face)

    # pt 2 and 3 are connected, so we need to have positives when iterating over both.
    # Duplicate edges are removed via the set.
    mock_has.side_effect = (False, False, True, True, False, False, True, True)

    result = api.shared_edges(mock_face1, mock_face2)

    assert result == (mock_geometry.findEdge.return_value,)

    mock_geometry.findEdge.assert_called_with(mock_point2, mock_point3)


class Test_insert_vertex(object):
    """Test ht.inline.api.insert_vertex."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_face = mocker.MagicMock(spec=hou.Face)
        mock_face.geometry.return_value = mock_geometry

        mock_point = mocker.MagicMock(spec=hou.Point)
        mock_index = mocker.MagicMock(spec=int)

        with pytest.raises(hou.GeometryPermissionError):
            api.insert_vertex(mock_face, mock_point, mock_index)

        mock_read_only.assert_called_with(mock_geometry)

    def test(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_assert = mocker.patch("ht.inline.api._assert_prim_vertex_index")
        mock_insert = mocker.patch("ht.inline.api._cpp_methods.insertVertex")
        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_face = mocker.MagicMock(spec=hou.Face)
        mock_face.geometry.return_value = mock_geometry

        mock_point = mocker.MagicMock(spec=hou.Point)
        mock_index = mocker.MagicMock(spec=int)

        result = api.insert_vertex(mock_face, mock_point, mock_index)

        assert result == mock_face.vertex.return_value

        mock_read_only.assert_called_with(mock_geometry)

        mock_assert.assert_called_with(mock_face, mock_index)

        mock_insert.assert_called_with(
            mock_geometry,
            mock_face.number.return_value,
            mock_point.number.return_value,
            mock_index,
        )

        mock_face.vertex.assert_called_with(mock_index)


class Test_delete_vertex_from_face(object):
    """Test ht.inline.api.delete_vertex_from_face."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )
        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_face = mocker.MagicMock(spec=hou.Face)
        mock_face.geometry.return_value = mock_geometry

        mock_index = mocker.MagicMock(spec=int)

        with pytest.raises(hou.GeometryPermissionError):
            api.delete_vertex_from_face(mock_face, mock_index)

        mock_read_only.assert_called_with(mock_geometry)

    def test(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_assert = mocker.patch("ht.inline.api._assert_prim_vertex_index")
        mock_delete = mocker.patch("ht.inline.api._cpp_methods.deleteVertexFromFace")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_face = mocker.MagicMock(spec=hou.Face)
        mock_face.geometry.return_value = mock_geometry

        mock_index = mocker.MagicMock(spec=int)

        api.delete_vertex_from_face(mock_face, mock_index)

        mock_read_only.assert_called_with(mock_geometry)

        mock_assert.assert_called_with(mock_face, mock_index)

        mock_delete.assert_called_with(
            mock_geometry, mock_face.number.return_value, mock_index
        )


class Test_set_face_vertex_point(object):
    """Test ht.inline.api.set_face_vertex_point."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_face = mocker.MagicMock(spec=hou.Face)
        mock_face.geometry.return_value = mock_geometry

        mock_point = mocker.MagicMock(spec=hou.Point)
        mock_index = mocker.MagicMock(spec=int)

        with pytest.raises(hou.GeometryPermissionError):
            api.set_face_vertex_point(mock_face, mock_point, mock_index)

        mock_read_only.assert_called_with(mock_geometry)

    def test(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_assert = mocker.patch("ht.inline.api._assert_prim_vertex_index")
        mock_set = mocker.patch("ht.inline.api._cpp_methods.setFaceVertexPoint")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_face = mocker.MagicMock(spec=hou.Face)
        mock_face.geometry.return_value = mock_geometry

        mock_point = mocker.MagicMock(spec=hou.Point)
        mock_index = mocker.MagicMock(spec=int)

        api.set_face_vertex_point(mock_face, mock_index, mock_point)

        mock_read_only.assert_called_with(mock_geometry)

        mock_assert.assert_called_with(mock_face, mock_index)

        mock_set.assert_called_with(
            mock_geometry,
            mock_face.number.return_value,
            mock_index,
            mock_point.number.return_value,
        )


def test_primitive_bary_center(mocker):
    """Test ht.inline.api.primitive_bary_center."""
    mock_center = mocker.patch("ht.inline.api._cpp_methods.primitiveBaryCenter")
    mock_hou_vec = mocker.patch("ht.inline.api.hou.Vector3", autospec=True)

    mock_prim = mocker.MagicMock(spec=hou.Prim)

    mock_result = mocker.MagicMock()
    mock_center.return_value = mock_result

    result = api.primitive_bary_center(mock_prim)
    assert result == mock_hou_vec.return_value

    mock_center.assert_called_with(
        mock_prim.geometry.return_value, mock_prim.number.return_value
    )

    mock_hou_vec.assert_called_with(mock_result.x, mock_result.y, mock_result.z)


def test_primitive_area(mocker):
    """Test ht.inline.api.primitive_area."""
    mock_prim = mocker.MagicMock(spec=hou.Prim)

    result = api.primitive_area(mock_prim)
    assert result == mock_prim.intrinsicValue.return_value

    mock_prim.intrinsicValue.assert_called_with("measuredarea")


def test_primitive_perimeter(mocker):
    """Test ht.inline.api.primitive_perimeter."""
    mock_prim = mocker.MagicMock(spec=hou.Prim)

    result = api.primitive_perimeter(mock_prim)
    assert result == mock_prim.intrinsicValue.return_value

    mock_prim.intrinsicValue.assert_called_with("measuredperimeter")


def test_primitive_volume(mocker):
    """Test ht.inline.api.primitive_volume."""

    mock_prim = mocker.MagicMock(spec=hou.Prim)

    result = api.primitive_volume(mock_prim)
    assert result == mock_prim.intrinsicValue.return_value

    mock_prim.intrinsicValue.assert_called_with("measuredvolume")


class Test_reverse_prim(object):
    """Test ht.inline.api.reverse_prim."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_prim = mocker.MagicMock(spec=hou.Prim)
        mock_prim.geometry.return_value = mock_geometry

        with pytest.raises(hou.GeometryPermissionError):
            api.reverse_prim(mock_prim)

        mock_read_only.assert_called_with(mock_geometry)

    def test(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_reverse = mocker.patch("ht.inline.api._cpp_methods.reversePrimitive")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_prim = mocker.MagicMock(spec=hou.Prim)
        mock_prim.geometry.return_value = mock_geometry

        api.reverse_prim(mock_prim)

        mock_read_only.assert_called_with(mock_geometry)

        mock_reverse.assert_called_with(mock_geometry, mock_prim.number.return_value)


class Test_make_primitive_points_unique(object):
    """Test ht.inline.api.make_primitive_points_unique."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )
        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_prim = mocker.MagicMock(spec=hou.Prim)
        mock_prim.geometry.return_value = mock_geometry

        with pytest.raises(hou.GeometryPermissionError):
            api.make_primitive_points_unique(mock_prim)

        mock_read_only.assert_called_with(mock_geometry)

    def test(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_unique = mocker.patch("ht.inline.api._cpp_methods.makePrimitiveUnique")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_prim = mocker.MagicMock(spec=hou.Prim)
        mock_prim.geometry.return_value = mock_geometry

        api.make_primitive_points_unique(mock_prim)

        mock_read_only.assert_called_with(mock_geometry)

        mock_unique.assert_called_with(mock_geometry, mock_prim.number.return_value)


class Test_check_minimum_polygon_vertex_count(object):
    """Test ht.inline.api.check_minimum_polygon_vertex_count."""

    def test_default(self, mocker):
        mock_check = mocker.patch(
            "ht.inline.api._cpp_methods.check_minimum_polygon_vertex_count"
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_minimum = mocker.MagicMock(spec=int)

        result = api.check_minimum_polygon_vertex_count(mock_geometry, mock_minimum)
        assert result == mock_check.return_value
        mock_check.assert_called_with(mock_geometry, mock_minimum, True)

    def test(self, mocker):
        mock_check = mocker.patch(
            "ht.inline.api._cpp_methods.check_minimum_polygon_vertex_count"
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_minimum = mocker.MagicMock(spec=int)
        mock_ignore = mocker.MagicMock(spec=bool)

        result = api.check_minimum_polygon_vertex_count(
            mock_geometry, mock_minimum, ignore_open=mock_ignore
        )
        assert result == mock_check.return_value

        mock_check.assert_called_with(mock_geometry, mock_minimum, mock_ignore)


def test_primitive_bounding_box(mocker):
    """Test ht.inline.api.primitive_bounding_box."""
    mock_bounding = mocker.patch("ht.inline.api.hou.BoundingBox")

    mock_value = mocker.MagicMock()

    mock_prim = mocker.MagicMock(spec=hou.Prim)
    mock_prim.intrinsicValue.return_value = mock_value

    result = api.primitive_bounding_box(mock_prim)

    assert result == mock_bounding.return_value

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
        [
            mocker.call(0),
            mocker.call(2),
            mocker.call(4),
            mocker.call(1),
            mocker.call(3),
            mocker.call(5),
        ]
    )


class Test_compute_point_normals(object):
    """Test ht.inline.api.compute_point_normals."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=True)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        with pytest.raises(hou.GeometryPermissionError):
            api.compute_point_normals(mock_geometry)

    def test(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_compute = mocker.patch("ht.inline.api._cpp_methods.computePointNormals")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        api.compute_point_normals(mock_geometry)

        mock_compute.assert_called_with(mock_geometry)


class Test_add_point_normal_attribute(object):
    """Test ht.inline.api.add_point_normal_attribute."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=True)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        with pytest.raises(hou.GeometryPermissionError):
            api.add_point_normal_attribute(mock_geometry)

    def test_failure(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_add = mocker.patch(
            "ht.inline.api._cpp_methods.addNormalAttribute", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        with pytest.raises(hou.OperationFailed):
            api.add_point_normal_attribute(mock_geometry)

        mock_add.assert_called_with(mock_geometry)

    def test(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_add = mocker.patch(
            "ht.inline.api._cpp_methods.addNormalAttribute", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        result = api.add_point_normal_attribute(mock_geometry)

        assert result == mock_geometry.findPointAttrib.return_value

        mock_add.assert_called_with(mock_geometry)

        mock_geometry.findPointAttrib.assert_called_with("N")


class Test_add_point_velocity_attribute(object):
    """Test ht.inline.api.add_point_velocity_attribute."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=True)
        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        with pytest.raises(hou.GeometryPermissionError):
            api.add_point_velocity_attribute(mock_geometry)

    def test_failure(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_add = mocker.patch(
            "ht.inline.api._cpp_methods.addVelocityAttribute", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        with pytest.raises(hou.OperationFailed):
            api.add_point_velocity_attribute(mock_geometry)

        mock_add.assert_called_with(mock_geometry)

    def test(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_add = mocker.patch(
            "ht.inline.api._cpp_methods.addVelocityAttribute", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        result = api.add_point_velocity_attribute(mock_geometry)

        assert result == mock_geometry.findPointAttrib.return_value

        mock_add.assert_called_with(mock_geometry)

        mock_geometry.findPointAttrib.assert_called_with("v")


class Test_add_color_attribute(object):
    """Test ht.inline.api.add_color_attribute."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=True)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_attrib_type = mocker.MagicMock(spec=hou.attribType)

        with pytest.raises(hou.GeometryPermissionError):
            api.add_color_attribute(mock_geometry, mock_attrib_type)

    def test_global(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        with pytest.raises(ValueError):
            api.add_color_attribute(mock_geometry, hou.attribType.Global)

    def test_failure(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_owner = mocker.patch("ht.inline.utils.get_attrib_owner")
        mock_add = mocker.patch(
            "ht.inline.api._cpp_methods.addDiffuseAttribute", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_attrib_type = mocker.MagicMock(spec=hou.attribType)

        with pytest.raises(hou.OperationFailed):
            api.add_color_attribute(mock_geometry, mock_attrib_type)

        mock_owner.assert_called_with(mock_attrib_type)

        mock_add.assert_called_with(mock_geometry, mock_owner.return_value)

    def test(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_owner = mocker.patch("ht.inline.utils.get_attrib_owner")
        mock_add = mocker.patch(
            "ht.inline.api._cpp_methods.addDiffuseAttribute", return_value=True
        )
        mock_find = mocker.patch("ht.inline.api.utils.find_attrib")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_attrib_type = mocker.MagicMock(spec=hou.attribType)

        result = api.add_color_attribute(mock_geometry, mock_attrib_type)

        assert result == mock_find.return_value

        mock_owner.assert_called_with(mock_attrib_type)

        mock_add.assert_called_with(mock_geometry, mock_owner.return_value)

        mock_find.assert_called_with(mock_geometry, mock_attrib_type, "Cd")


class Test_convex_polygons(object):
    """Test ht.inline.api.convex_polygons."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=True)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        with pytest.raises(hou.GeometryPermissionError):
            api.convex_polygons(mock_geometry)

    def test_default_arg(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_convex = mocker.patch("ht.inline.api._cpp_methods.convexPolygons")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        api.convex_polygons(mock_geometry)

        mock_convex.assert_called_with(mock_geometry, 3)

    def test(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_convex = mocker.patch("ht.inline.api._cpp_methods.convexPolygons")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_max_points = mocker.MagicMock(spec=int)

        api.convex_polygons(mock_geometry, mock_max_points)

        mock_convex.assert_called_with(mock_geometry, mock_max_points)


class Test_clip_geometry(object):
    """Test ht.inline.api.clip_geometry."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=True)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_origin = mocker.MagicMock(spec=hou.Vector3)
        mock_normal = mocker.MagicMock(spec=hou.Vector3)

        with pytest.raises(hou.GeometryPermissionError):
            api.clip_geometry(mock_geometry, mock_origin, mock_normal)

    def test_group_below(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_build = mocker.patch("ht.inline.api.hou.hmath.buildTranslate")
        mock_clip = mocker.patch("ht.inline.api._cpp_methods.clipGeometry")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_origin = mocker.MagicMock(spec=hou.Vector3)
        mock_normal = mocker.MagicMock(spec=hou.Vector3)
        mock_dist = mocker.MagicMock(spec=int)
        mock_group = mocker.MagicMock(spec=hou.PrimGroup)

        api.clip_geometry(
            mock_geometry,
            mock_origin,
            mock_normal,
            dist=mock_dist,
            below=True,
            group=mock_group,
        )

        mock_origin.__add__.assert_called_with(mock_normal.__mul__.return_value)

        mock_normal.__mul__.assert_has_calls([mocker.call(mock_dist), mocker.call(-1)])

        mock_build.assert_called_with(mock_origin.__add__.return_value)

        mock_clip.assert_called_with(
            mock_geometry,
            mock_build.return_value,
            mock_normal.__mul__.return_value.normalized.return_value,
            0,
            mock_group.name.return_value,
        )

    def test_default_args(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_build = mocker.patch("ht.inline.api.hou.hmath.buildTranslate")
        mock_clip = mocker.patch("ht.inline.api._cpp_methods.clipGeometry")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_origin = mocker.MagicMock(spec=hou.Vector3)
        mock_normal = mocker.MagicMock(spec=hou.Vector3)

        api.clip_geometry(mock_geometry, mock_origin, mock_normal)

        mock_origin.__add__.assert_not_called()

        mock_build.assert_called_with(mock_origin)

        mock_clip.assert_called_with(
            mock_geometry,
            mock_build.return_value,
            mock_normal.normalized.return_value,
            0,
            "",
        )


class Test_destroy_empty_groups(object):
    """Test ht.inline.api.destroy_empty_groups."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=True)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_attrib_type = mocker.MagicMock(spec=hou.attribType)

        with pytest.raises(hou.GeometryPermissionError):
            api.destroy_empty_groups(mock_geometry, mock_attrib_type)

    def test_global(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        with pytest.raises(ValueError):
            api.destroy_empty_groups(mock_geometry, hou.attribType.Global)

    def test(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_owner = mocker.patch("ht.inline.utils.get_attrib_owner")
        mock_destroy = mocker.patch("ht.inline.api._cpp_methods.destroyEmptyGroups")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_attrib_type = mocker.MagicMock(spec=hou.attribType)

        api.destroy_empty_groups(mock_geometry, mock_attrib_type)

        mock_owner.assert_called_with(mock_attrib_type)
        mock_destroy.assert_called_with(mock_geometry, mock_owner.return_value)


class Test_destroy_unused_points(object):
    """Test ht.inline.api.destroy_unused_points."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=True)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        with pytest.raises(hou.GeometryPermissionError):
            api.destroy_unused_points(mock_geometry)

    def test_group(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_destroy = mocker.patch("ht.inline.api._cpp_methods.destroyUnusedPoints")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_group = mocker.MagicMock(spec=hou.PointGroup)

        api.destroy_unused_points(mock_geometry, mock_group)

        mock_destroy.assert_called_with(mock_geometry, mock_group.name.return_value)

    def test_no_group(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_destroy = mocker.patch("ht.inline.api._cpp_methods.destroyUnusedPoints")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        api.destroy_unused_points(mock_geometry)

        mock_destroy.assert_called_with(mock_geometry, 0)


class Test_consolidate_points(object):
    """Test ht.inline.api.consolidate_points."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=True)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        with pytest.raises(hou.GeometryPermissionError):
            api.consolidate_points(mock_geometry)

    def test_group_distance(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_consolidate = mocker.patch("ht.inline.api._cpp_methods.consolidatePoints")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_distance = mocker.MagicMock(spec=float)
        mock_group = mocker.MagicMock(spec=hou.PointGroup)

        api.consolidate_points(mock_geometry, mock_distance, mock_group)

        mock_consolidate.assert_called_with(
            mock_geometry, mock_distance, mock_group.name.return_value
        )

    def test_no_group(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_consolidate = mocker.patch("ht.inline.api._cpp_methods.consolidatePoints")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        api.consolidate_points(mock_geometry)

        mock_consolidate.assert_called_with(mock_geometry, 0.001, 0)


class Test_unique_points(object):
    """Test ht.inline.api.unique_points."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=True)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        with pytest.raises(hou.GeometryPermissionError):
            api.unique_points(mock_geometry)

    def test_group(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_unique = mocker.patch("ht.inline.api._cpp_methods.uniquePoints")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_group = mocker.MagicMock(spec=hou.PointGroup)

        api.unique_points(mock_geometry, mock_group)

        mock_unique.assert_called_with(mock_geometry, mock_group.name.return_value)

    def test_no_group(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_unique = mocker.patch("ht.inline.api._cpp_methods.uniquePoints")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        api.unique_points(mock_geometry)

        mock_unique.assert_called_with(mock_geometry, 0)


class Test_rename_group(object):
    """Test ht.inline.api.rename_group."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=True)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group = mocker.MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_new_name = mocker.MagicMock(spec=str)

        with pytest.raises(hou.GeometryPermissionError):
            api.rename_group(mock_group, mock_new_name)

    def test_same_name(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group = mocker.MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_new_name = mock_group.name.return_value

        with pytest.raises(hou.OperationFailed):
            api.rename_group(mock_group, mock_new_name)

    def test(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_get_type = mocker.patch("ht.inline.api.utils.get_group_type")
        mock_rename = mocker.patch(
            "ht.inline.api._cpp_methods.renameGroup", return_value=True
        )
        mock_find = mocker.patch("ht.inline.api.utils.find_group")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group = mocker.MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_new_name = mocker.MagicMock(spec=str)

        result = api.rename_group(mock_group, mock_new_name)

        assert result == mock_find.return_value

        mock_get_type.assert_called_with(mock_group)

        mock_rename.assert_called_with(
            mock_geometry,
            mock_group.name.return_value,
            mock_new_name,
            mock_get_type.return_value,
        )

        mock_find.assert_called_with(
            mock_geometry, mock_get_type.return_value, mock_new_name
        )

    def test_failure(self, mocker, fix_hou_exceptions):
        mocker.patch("ht.inline.api.is_geometry_read_only", return_value=False)
        mock_get_type = mocker.patch("ht.inline.api.utils.get_group_type")
        mock_rename = mocker.patch(
            "ht.inline.api._cpp_methods.renameGroup", return_value=False
        )
        mock_find = mocker.patch("ht.inline.api.utils.find_group")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group = mocker.MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_new_name = mocker.MagicMock(spec=str)

        result = api.rename_group(mock_group, mock_new_name)

        assert result is None

        mock_get_type.assert_called_with(mock_group)

        mock_rename.assert_called_with(
            mock_geometry,
            mock_group.name.return_value,
            mock_new_name,
            mock_get_type.return_value,
        )

        mock_find.assert_not_called()


def test_group_bounding_box(mocker):
    """Test ht.inline.api.group_bounding_box."""
    mock_get_type = mocker.patch("ht.inline.api.utils.get_group_type")
    mock_group_bbox = mocker.patch("ht.inline.api._cpp_methods.groupBoundingBox")
    mock_bbox = mocker.patch("ht.inline.api.hou.BoundingBox")

    mock_group = mocker.MagicMock(spec=hou.PointGroup)

    result = api.group_bounding_box(mock_group)
    assert result == mock_bbox.return_value

    mock_get_type.assert_called_with(mock_group)

    mock_group_bbox.assert_called_with(
        mock_group.geometry.return_value,
        mock_get_type.return_value,
        mock_group.name.return_value,
    )

    mock_bbox.assert_called_with(*mock_group_bbox.return_value)


def test_group_size(mocker):
    """Test ht.inline.api.group_size."""
    mock_get_type = mocker.patch("ht.inline.api.utils.get_group_type")
    mock_size = mocker.patch("ht.inline.api._cpp_methods.groupSize")

    mock_group = mocker.MagicMock(spec=hou.PointGroup)

    result = api.group_size(mock_group)
    assert result == mock_size.return_value

    mock_get_type.assert_called_with(mock_group)

    mock_size.assert_called_with(
        mock_group.geometry.return_value,
        mock_group.name.return_value,
        mock_get_type.return_value,
    )


class Test_toggle_point_in_group(object):
    """Test ht.inline.api.toggle_point_in_group."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group = mocker.MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_point = mocker.MagicMock(spec=hou.Point)

        with pytest.raises(hou.GeometryPermissionError):
            api.toggle_point_in_group(mock_group, mock_point)

        mock_read_only.assert_called_with(mock_geometry)

    def test(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_get_type = mocker.patch("ht.inline.api.utils.get_group_type")
        mock_toggle = mocker.patch("ht.inline.api._cpp_methods.toggleGroupMembership")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group = mocker.MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_point = mocker.MagicMock(spec=hou.Point)

        api.toggle_point_in_group(mock_group, mock_point)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_type.assert_called_with(mock_group)

        mock_toggle.assert_called_with(
            mock_geometry,
            mock_group.name.return_value,
            mock_get_type.return_value,
            mock_point.number.return_value,
        )


class Test_toggle_prim_in_group(object):
    """Test ht.inline.api.toggle_point_in_group."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group = mocker.MagicMock(spec=hou.PrimGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_prim = mocker.MagicMock(spec=hou.Prim)

        with pytest.raises(hou.GeometryPermissionError):
            api.toggle_prim_in_group(mock_group, mock_prim)

        mock_read_only.assert_called_with(mock_geometry)

    def test(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_get_type = mocker.patch("ht.inline.api.utils.get_group_type")
        mock_toggle = mocker.patch("ht.inline.api._cpp_methods.toggleGroupMembership")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group = mocker.MagicMock(spec=hou.PrimGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_prim = mocker.MagicMock(spec=hou.Prim)

        api.toggle_prim_in_group(mock_group, mock_prim)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_type.assert_called_with(mock_group)

        mock_toggle.assert_called_with(
            mock_geometry,
            mock_group.name.return_value,
            mock_get_type.return_value,
            mock_prim.number.return_value,
        )


class Test_toggle_group_entries(object):
    """Test ht.inline.api.toggle_group_entries."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group = mocker.MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        with pytest.raises(hou.GeometryPermissionError):
            api.toggle_group_entries(mock_group)

        mock_read_only.assert_called_with(mock_geometry)

    def test(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_get_type = mocker.patch("ht.inline.api.utils.get_group_type")
        mock_toggle = mocker.patch("ht.inline.api._cpp_methods.toggleGroupEntries")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group = mocker.MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        api.toggle_group_entries(mock_group)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_type.assert_called_with(mock_group)

        mock_toggle.assert_called_with(
            mock_geometry, mock_group.name.return_value, mock_get_type.return_value
        )


class Test_copy_group(object):
    """Test ht.inline.api.copy_group."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group = mocker.MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_new_name = mocker.MagicMock(spec=str)

        with pytest.raises(hou.GeometryPermissionError):
            api.copy_group(mock_group, mock_new_name)

        mock_read_only.assert_called_with(mock_geometry)

    def test_same_name(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group = mocker.MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_new_name = mock_group.name.return_value

        with pytest.raises(hou.OperationFailed):
            api.copy_group(mock_group, mock_new_name)

        mock_read_only.assert_called_with(mock_geometry)

    def test_existing(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_get_type = mocker.patch("ht.inline.api.utils.get_group_type")
        mock_find = mocker.patch("ht.inline.api.utils.find_group")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group = mocker.MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_new_name = mocker.MagicMock(spec=str)

        with pytest.raises(hou.OperationFailed):
            api.copy_group(mock_group, mock_new_name)

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_type.assert_called_with(mock_group)

        mock_find.assert_called_with(
            mock_geometry, mock_get_type.return_value, mock_new_name
        )

    def test(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_get_type = mocker.patch("ht.inline.api.utils.get_group_type")
        mock_find = mocker.patch("ht.inline.api.utils.find_group")
        mock_get_owner = mocker.patch("ht.inline.api.utils.get_group_attrib_owner")
        mock_copy = mocker.patch("ht.inline.api._cpp_methods.copyGroup")

        mock_new_group = mocker.MagicMock(spec=hou.PointGroup)

        mock_find.side_effect = (None, mock_new_group)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group = mocker.MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_new_name = mocker.MagicMock(spec=str)

        result = api.copy_group(mock_group, mock_new_name)
        assert result == mock_new_group

        mock_read_only.assert_called_with(mock_geometry)

        mock_get_type.assert_called_with(mock_group)

        mock_find.assert_has_calls(
            [
                mocker.call(mock_geometry, mock_get_type.return_value, mock_new_name),
                mocker.call(mock_geometry, mock_get_type.return_value, mock_new_name),
            ]
        )

        mock_get_owner.assert_called_with(mock_group)

        mock_copy.assert_called_with(
            mock_geometry,
            mock_get_owner.return_value,
            mock_group.name.return_value,
            mock_new_name,
        )


class Test_groups_share_elements(object):
    """Test ht.inline.api.groups_share_elements."""

    def test_different_details(self, mocker):
        mock_match = mocker.patch(
            "ht.inline.api.utils.geo_details_match", return_value=False
        )

        mock_geometry1 = mocker.MagicMock(spec=hou.Geometry)

        mock_group1 = mocker.MagicMock(spec=hou.PointGroup)
        mock_group1.geometry.return_value = mock_geometry1

        mock_geometry2 = mocker.MagicMock(spec=hou.Geometry)

        mock_group2 = mocker.MagicMock(spec=hou.PointGroup)
        mock_group2.geometry.return_value = mock_geometry2

        with pytest.raises(ValueError):
            api.groups_share_elements(mock_group1, mock_group2)

        mock_match.assert_called_with(mock_geometry1, mock_geometry2)

    def test_different_group_types(self, mocker):
        mock_match = mocker.patch(
            "ht.inline.api.utils.geo_details_match", return_value=True
        )
        mock_get_type = mocker.patch("ht.inline.api.utils.get_group_type")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group1 = mocker.MagicMock(spec=hou.PointGroup)
        mock_group1.geometry.return_value = mock_geometry

        mock_group2 = mocker.MagicMock(spec=hou.PointGroup)
        mock_group2.geometry.return_value = mock_geometry

        mock_get_type.side_effect = (
            mocker.MagicMock(spec=int),
            mocker.MagicMock(spec=int),
        )

        with pytest.raises(TypeError):
            api.groups_share_elements(mock_group1, mock_group2)

        mock_match.assert_called_with(mock_geometry, mock_geometry)

        mock_get_type.assert_has_calls(
            [mocker.call(mock_group1), mocker.call(mock_group2)]
        )

    def test(self, mocker):
        mock_match = mocker.patch(
            "ht.inline.api.utils.geo_details_match", return_value=True
        )
        mock_get_type = mocker.patch("ht.inline.api.utils.get_group_type")
        mock_contains = mocker.patch("ht.inline.api._cpp_methods.groupsShareElements")

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group1 = mocker.MagicMock(spec=hou.PointGroup)
        mock_group1.geometry.return_value = mock_geometry

        mock_group2 = mocker.MagicMock(spec=hou.PointGroup)
        mock_group2.geometry.return_value = mock_geometry

        result = api.groups_share_elements(mock_group1, mock_group2)

        assert result == mock_contains.return_value

        mock_match.assert_called_with(mock_geometry, mock_geometry)

        mock_get_type.assert_has_calls(
            [mocker.call(mock_group1), mocker.call(mock_group2)]
        )

        mock_contains.assert_called_with(
            mock_geometry,
            mock_group1.name.return_value,
            mock_group2.name.return_value,
            mock_get_type.return_value,
        )


class Test_convert_prim_to_point_group(object):
    """Test ht.inline.api.convert_prim_to_point_group."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group = mocker.MagicMock(spec=hou.PrimGroup)
        mock_group.geometry.return_value = mock_geometry

        with pytest.raises(hou.GeometryPermissionError):
            api.convert_prim_to_point_group(mock_group)

        mock_read_only.assert_called_with(mock_geometry)

    def test_name_already_exists(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group = mocker.MagicMock(spec=hou.PrimGroup)
        mock_group.geometry.return_value = mock_geometry

        with pytest.raises(hou.OperationFailed):
            api.convert_prim_to_point_group(mock_group)

        mock_read_only.assert_called_with(mock_geometry)

        mock_geometry.findPointGroup.assert_called_with(mock_group.name.return_value)

    def test_same_name(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_to_point = mocker.patch("ht.inline.api._cpp_methods.primToPointGroup")

        mock_new_group = mocker.MagicMock(spec=hou.PointGroup)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_geometry.findPointGroup.side_effect = (None, mock_new_group)

        mock_group = mocker.MagicMock(spec=hou.PrimGroup)
        mock_group.geometry.return_value = mock_geometry

        result = api.convert_prim_to_point_group(mock_group)
        assert result == mock_new_group

        mock_read_only.assert_called_with(mock_geometry)

        mock_geometry.findPointGroup.assert_has_calls(
            [
                mocker.call(mock_group.name.return_value),
                mocker.call(mock_group.name.return_value),
            ]
        )

        mock_to_point.assert_called_with(
            mock_geometry,
            mock_group.name.return_value,
            mock_group.name.return_value,
            True,
        )

    def test_new_name_no_destroy(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_to_point = mocker.patch("ht.inline.api._cpp_methods.primToPointGroup")

        mock_new_group = mocker.MagicMock(spec=hou.PointGroup)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_geometry.findPointGroup.side_effect = (None, mock_new_group)

        mock_group = mocker.MagicMock(spec=hou.PrimGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_new_name = mocker.MagicMock(spec=str)

        result = api.convert_prim_to_point_group(mock_group, mock_new_name, False)
        assert result == mock_new_group

        mock_read_only.assert_called_with(mock_geometry)

        mock_geometry.findPointGroup.assert_has_calls(
            [mocker.call(mock_new_name), mocker.call(mock_new_name)]
        )

        mock_to_point.assert_called_with(
            mock_geometry, mock_group.name.return_value, mock_new_name, False
        )


class Test_convert_point_to_prim_group(object):
    """Test ht.inline.api.convert_point_to_prim_group."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group = mocker.MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        with pytest.raises(hou.GeometryPermissionError):
            api.convert_point_to_prim_group(mock_group)

        mock_read_only.assert_called_with(mock_geometry)

    def test_name_already_exists(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group = mocker.MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        with pytest.raises(hou.OperationFailed):
            api.convert_point_to_prim_group(mock_group)

        mock_read_only.assert_called_with(mock_geometry)

        mock_geometry.findPrimGroup.assert_called_with(mock_group.name.return_value)

    def test_same_name(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_to_point = mocker.patch("ht.inline.api._cpp_methods.pointToPrimGroup")

        mock_new_group = mocker.MagicMock(spec=hou.PrimGroup)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_geometry.findPrimGroup.side_effect = (None, mock_new_group)

        mock_group = mocker.MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        result = api.convert_point_to_prim_group(mock_group)
        assert result == mock_new_group

        mock_read_only.assert_called_with(mock_geometry)

        mock_geometry.findPrimGroup.assert_has_calls(
            [
                mocker.call(mock_group.name.return_value),
                mocker.call(mock_group.name.return_value),
            ]
        )

        mock_to_point.assert_called_with(
            mock_geometry,
            mock_group.name.return_value,
            mock_group.name.return_value,
            True,
        )

    def test_new_name_no_destroy(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_to_point = mocker.patch("ht.inline.api._cpp_methods.pointToPrimGroup")

        mock_new_group = mocker.MagicMock(spec=hou.PrimGroup)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_geometry.findPrimGroup.side_effect = (None, mock_new_group)

        mock_group = mocker.MagicMock(spec=hou.PointGroup)
        mock_group.geometry.return_value = mock_geometry

        mock_new_name = mocker.MagicMock(spec=str)

        result = api.convert_point_to_prim_group(mock_group, mock_new_name, False)
        assert result == mock_new_group

        mock_read_only.assert_called_with(mock_geometry)

        mock_geometry.findPrimGroup.assert_has_calls(
            [mocker.call(mock_new_name), mocker.call(mock_new_name)]
        )

        mock_to_point.assert_called_with(
            mock_geometry, mock_group.name.return_value, mock_new_name, False
        )


def test_geometry_has_ungrouped_points(mocker):
    """Test ht.inline.api.geometry_has_ungrouped_points."""

    mock_has = mocker.patch("ht.inline.api._cpp_methods.hasUngroupedPoints")

    mock_geometry = mocker.MagicMock(spec=hou.Geometry)

    result = api.geometry_has_ungrouped_points(mock_geometry)
    assert result == mock_has.return_value

    mock_has.assert_called_with(mock_geometry)


class Test_group_ungrouped_points(object):
    """Test ht.inline.api.group_ungrouped_points."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group_name = mocker.MagicMock(spec=str)

        with pytest.raises(hou.GeometryPermissionError):
            api.group_ungrouped_points(mock_geometry, mock_group_name)

        mock_read_only.assert_called_with(mock_geometry)

    def test_empty_name(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        with pytest.raises(ValueError):
            api.group_ungrouped_points(mock_geometry, "")

        mock_read_only.assert_called_with(mock_geometry)

    def test_group_exists(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group_name = mocker.MagicMock(spec=str)
        mock_group_name.__len__.return_value = 1

        with pytest.raises(hou.OperationFailed):
            api.group_ungrouped_points(mock_geometry, mock_group_name)

        mock_read_only.assert_called_with(mock_geometry)

        mock_geometry.findPointGroup.assert_called_with(mock_group_name)

    def test(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_group_points = mocker.patch(
            "ht.inline.api._cpp_methods.groupUngroupedPoints"
        )

        mock_new_group = mocker.MagicMock(spec=hou.PointGroup)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_geometry.findPointGroup.side_effect = (None, mock_new_group)

        mock_group_name = mocker.MagicMock(spec=str)
        mock_group_name.__len__.return_value = 1

        result = api.group_ungrouped_points(mock_geometry, mock_group_name)
        assert result == mock_new_group

        mock_read_only.assert_called_with(mock_geometry)

        mock_geometry.findPointGroup.assert_has_calls(
            [mocker.call(mock_group_name), mocker.call(mock_group_name)]
        )

        mock_group_points.assert_called_with(mock_geometry, mock_group_name)


def test_geometry_has_ungrouped_prims(mocker):
    """Test ht.inline.api.geometry_has_ungrouped_prims."""
    mock_has = mocker.patch("ht.inline.api._cpp_methods.hasUngroupedPrims")

    mock_geometry = mocker.MagicMock(spec=hou.Geometry)

    result = api.geometry_has_ungrouped_prims(mock_geometry)
    assert result == mock_has.return_value

    mock_has.assert_called_with(mock_geometry)


class Test_group_ungrouped_prims(object):
    """Test ht.inline.api.group_ungrouped_prims."""

    def test_read_only(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=True
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group_name = mocker.MagicMock(spec=str)

        with pytest.raises(hou.GeometryPermissionError):
            api.group_ungrouped_prims(mock_geometry, mock_group_name)

        mock_read_only.assert_called_with(mock_geometry)

    def test_empty_name(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        with pytest.raises(ValueError):
            api.group_ungrouped_prims(mock_geometry, "")

        mock_read_only.assert_called_with(mock_geometry)

    def test_group_exists(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)

        mock_group_name = mocker.MagicMock(spec=str)
        mock_group_name.__len__.return_value = 1

        with pytest.raises(hou.OperationFailed):
            api.group_ungrouped_prims(mock_geometry, mock_group_name)

        mock_read_only.assert_called_with(mock_geometry)

        mock_geometry.findPrimGroup.assert_called_with(mock_group_name)

    def test(self, mocker, fix_hou_exceptions):
        mock_read_only = mocker.patch(
            "ht.inline.api.is_geometry_read_only", return_value=False
        )
        mock_group_prims = mocker.patch(
            "ht.inline.api._cpp_methods.groupUngroupedPrims"
        )

        mock_new_group = mocker.MagicMock(spec=hou.PrimGroup)

        mock_geometry = mocker.MagicMock(spec=hou.Geometry)
        mock_geometry.findPrimGroup.side_effect = (None, mock_new_group)

        mock_group_name = mocker.MagicMock(spec=str)
        mock_group_name.__len__.return_value = 1

        result = api.group_ungrouped_prims(mock_geometry, mock_group_name)
        assert result == mock_new_group

        mock_read_only.assert_called_with(mock_geometry)

        mock_geometry.findPrimGroup.assert_has_calls(
            [mocker.call(mock_group_name), mocker.call(mock_group_name)]
        )

        mock_group_prims.assert_called_with(mock_geometry, mock_group_name)


def test_bounding_box_is_inside(mocker):
    """Test ht.inline.api.bounding_box_is_inside."""
    mock_is_inside = mocker.patch("ht.inline.api._cpp_methods.boundingBoxisInside")

    mock_box1 = mocker.MagicMock(spec=hou.BoundingBox)
    mock_box2 = mocker.MagicMock(spec=hou.BoundingBox)

    result = api.bounding_box_is_inside(mock_box1, mock_box2)
    assert result == mock_is_inside.return_value

    mock_is_inside.assert_called_with(mock_box1, mock_box2)


def test_bounding_boxes_intersect(mocker):
    """Test ht.inline.api.bounding_boxes_intersect."""
    mock_intersects = mocker.patch("ht.inline.api._cpp_methods.boundingBoxesIntersect")

    mock_box1 = mocker.MagicMock(spec=hou.BoundingBox)
    mock_box2 = mocker.MagicMock(spec=hou.BoundingBox)

    result = api.bounding_boxes_intersect(mock_box1, mock_box2)
    assert result == mock_intersects.return_value

    mock_intersects.assert_called_with(mock_box1, mock_box2)


def test_compute_bounding_box_intersection(mocker):
    """Test ht.inline.api.compute_bounding_box_intersection."""
    mock_compute = mocker.patch(
        "ht.inline.api._cpp_methods.computeBoundingBoxIntersection"
    )

    mock_box1 = mocker.MagicMock(spec=hou.BoundingBox)
    mock_box2 = mocker.MagicMock(spec=hou.BoundingBox)

    result = api.compute_bounding_box_intersection(mock_box1, mock_box2)
    assert result == mock_compute.return_value

    mock_compute.assert_called_with(mock_box1, mock_box2)


def test_expand_bounding_box(mocker):
    """Test ht.inline.api.expand_bounding_box."""
    mock_expand = mocker.patch("ht.inline.api._cpp_methods.expandBoundingBoxBounds")

    mock_box = mocker.MagicMock(spec=hou.BoundingBox)

    mock_delta_x = mocker.MagicMock(spec=float)
    mock_delta_y = mocker.MagicMock(spec=float)
    mock_delta_z = mocker.MagicMock(spec=float)

    api.expand_bounding_box(mock_box, mock_delta_x, mock_delta_y, mock_delta_z)

    mock_expand.assert_called_with(mock_box, mock_delta_x, mock_delta_y, mock_delta_z)


def test_add_to_bounding_box_min(mocker):
    """Test ht.inline.api.add_to_bounding_box_min."""
    mock_add = mocker.patch("ht.inline.api._cpp_methods.addToBoundingBoxMin")

    mock_box = mocker.MagicMock(spec=hou.BoundingBox)

    mock_vec = mocker.MagicMock(spec=hou.Vector3)

    api.add_to_bounding_box_min(mock_box, mock_vec)

    mock_add.assert_called_with(mock_box, mock_vec)


def test_add_to_bounding_box_max(mocker):
    """Test ht.inline.api.add_to_bounding_box_max."""
    mock_add = mocker.patch("ht.inline.api._cpp_methods.addToBoundingBoxMax")

    mock_box = mocker.MagicMock(spec=hou.BoundingBox)

    mock_vec = mocker.MagicMock(spec=hou.Vector3)

    api.add_to_bounding_box_max(mock_box, mock_vec)

    mock_add.assert_called_with(mock_box, mock_vec)


def test_bounding_box_area(mocker):
    """Test ht.inline.api.bounding_box_area."""
    mock_area = mocker.patch("ht.inline.api._cpp_methods.boundingBoxArea")

    mock_box = mocker.MagicMock(spec=hou.BoundingBox)

    result = api.bounding_box_area(mock_box)
    assert result == mock_area.return_value

    mock_area.assert_called_with(mock_box)


def test_bounding_box_volume(mocker):
    """Test ht.inline.api.bounding_box_volume."""
    mock_volume = mocker.patch("ht.inline.api._cpp_methods.boundingBoxVolume")

    mock_box = mocker.MagicMock(spec=hou.BoundingBox)

    result = api.bounding_box_volume(mock_box)
    assert result == mock_volume.return_value

    mock_volume.assert_called_with(mock_box)


class Test_is_parm_tuple_vector(object):
    """Test ht.inline.api.is_parm_tuple_vector."""

    def test_not_vector(self, mocker):
        mock_parm_tuple = mocker.MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple.parmTemplate.return_value.namingScheme.return_value = (
            hou.parmNamingScheme.RGBA
        )

        assert not api.is_parm_tuple_vector(mock_parm_tuple)

    def test_is_vector(self, mocker):
        mock_parm_tuple = mocker.MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple.parmTemplate.return_value.namingScheme.return_value = (
            hou.parmNamingScheme.XYZW
        )

        assert api.is_parm_tuple_vector(mock_parm_tuple)


class Test_eval_parm_tuple_as_vector(object):
    """Test ht.inline.api.eval_parm_tuple_as_vector."""

    def test_not_vector(self, mocker):
        mock_is_vector = mocker.patch(
            "ht.inline.api.is_parm_tuple_vector", return_value=False
        )

        mock_parm_tuple = mocker.MagicMock(spec=hou.ParmTuple)

        with pytest.raises(ValueError):
            api.eval_parm_tuple_as_vector(mock_parm_tuple)

        mock_is_vector.assert_called_with(mock_parm_tuple)

    def test_vector2(self, mocker):
        mock_is_vector = mocker.patch(
            "ht.inline.api.is_parm_tuple_vector", return_value=True
        )
        mock_hou_vec2 = mocker.patch("ht.inline.api.hou.Vector2", autospec=True)

        mock_value = mocker.MagicMock(spec=tuple)
        mock_value.__len__.return_value = 2

        mock_parm_tuple = mocker.MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple.eval.return_value = mock_value

        result = api.eval_parm_tuple_as_vector(mock_parm_tuple)
        assert result == mock_hou_vec2.return_value

        mock_is_vector.assert_called_with(mock_parm_tuple)

        mock_hou_vec2.assert_called_with(mock_value)

    def test_vector3(self, mocker):
        mock_is_vector = mocker.patch(
            "ht.inline.api.is_parm_tuple_vector", return_value=True
        )
        mock_hou_vec3 = mocker.patch("ht.inline.api.hou.Vector3", autospec=True)

        mock_value = mocker.MagicMock(spec=tuple)
        mock_value.__len__.return_value = 3

        mock_parm_tuple = mocker.MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple.eval.return_value = mock_value

        result = api.eval_parm_tuple_as_vector(mock_parm_tuple)
        assert result == mock_hou_vec3.return_value

        mock_is_vector.assert_called_with(mock_parm_tuple)

        mock_hou_vec3.assert_called_with(mock_value)

    def test_vector4(self, mocker):
        mock_is_vector = mocker.patch(
            "ht.inline.api.is_parm_tuple_vector", return_value=True
        )
        mock_hou_vec4 = mocker.patch("ht.inline.api.hou.Vector4", autospec=True)

        mock_value = mocker.MagicMock(spec=tuple)
        mock_value.__len__.return_value = 4

        mock_parm_tuple = mocker.MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple.eval.return_value = mock_value

        result = api.eval_parm_tuple_as_vector(mock_parm_tuple)
        assert result == mock_hou_vec4.return_value

        mock_is_vector.assert_called_with(mock_parm_tuple)

        mock_hou_vec4.assert_called_with(mock_value)


class Test_is_parm_tuple_color(object):
    """Test ht.inline.api.is_parm_tuple_color."""

    def test_not_color(self, mocker):
        mock_parm_tuple = mocker.MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple.parmTemplate.return_value.look.return_value = hou.parmLook.Angle

        assert not api.is_parm_tuple_color(mock_parm_tuple)

    def test_is_color(self, mocker):
        mock_parm_tuple = mocker.MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple.parmTemplate.return_value.look.return_value = (
            hou.parmLook.ColorSquare
        )

        assert api.is_parm_tuple_color(mock_parm_tuple)


class Test_eval_parm_tuple_as_color(object):
    """Test ht.inline.api.eval_parm_tuple_as_color."""

    def test_not_color(self, mocker):
        mock_is_color = mocker.patch(
            "ht.inline.api.is_parm_tuple_color", return_value=False
        )

        mock_parm_tuple = mocker.MagicMock(spec=hou.ParmTuple)

        with pytest.raises(ValueError):
            api.eval_parm_tuple_as_color(mock_parm_tuple)

        mock_is_color.assert_called_with(mock_parm_tuple)

    def test_color(self, mocker):
        mock_is_color = mocker.patch(
            "ht.inline.api.is_parm_tuple_color", return_value=True
        )
        mock_hou_color = mocker.patch("ht.inline.api.hou.Color", autospec=True)

        mock_parm_tuple = mocker.MagicMock(spec=hou.ParmTuple)

        result = api.eval_parm_tuple_as_color(mock_parm_tuple)
        assert result == mock_hou_color.return_value

        mock_is_color.assert_called_with(mock_parm_tuple)

        mock_hou_color.assert_called_with(mock_parm_tuple.eval.return_value)


class Test_eval_parm_as_strip(object):
    """Test ht.inline.api.eval_parm_as_strip."""

    def test_not_menu(self, mocker):
        mock_template = mocker.MagicMock(spec=hou.ParmTemplate)

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.parmTemplate.return_value = mock_template

        with pytest.raises(TypeError):
            api.eval_parm_as_strip(mock_parm)

    def test_toggle_menu(self, mocker):
        mock_template = mocker.MagicMock(spec=hou.MenuParmTemplate)
        mock_template.menuItems.return_value.__len__.return_value = 5
        mock_template.menuType.return_value = hou.menuType.StringToggle

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = 13
        mock_parm.parmTemplate.return_value = mock_template

        result = api.eval_parm_as_strip(mock_parm)
        assert result == (True, False, True, True, False)

    def test_replace_menu(self, mocker):
        mock_template = mocker.MagicMock(spec=hou.MenuParmTemplate)
        mock_template.menuItems.return_value.__len__.return_value = 5
        mock_template.menuType.return_value = hou.menuType.StringReplace

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = 3
        mock_parm.parmTemplate.return_value = mock_template

        result = api.eval_parm_as_strip(mock_parm)
        assert result == (False, False, False, True, False)


def test_eval_parm_strip_as_string(mocker):
    """Test ht.inline.api.eval_parm_strip_as_string."""
    mock_eval = mocker.patch("ht.inline.api.eval_parm_as_strip")

    mock_eval.return_value = (False, True, True, False, True)

    mock_item1 = mocker.MagicMock(spec=str)
    mock_item2 = mocker.MagicMock(spec=str)
    mock_item3 = mocker.MagicMock(spec=str)
    mock_item4 = mocker.MagicMock(spec=str)
    mock_item5 = mocker.MagicMock(spec=str)

    mock_template = mocker.MagicMock(spec=hou.MenuParmTemplate)
    mock_template.menuItems.return_value = (
        mock_item1,
        mock_item2,
        mock_item3,
        mock_item4,
        mock_item5,
    )

    mock_parm = mocker.MagicMock(spec=hou.Parm)
    mock_parm.parmTemplate.return_value = mock_template

    result = api.eval_parm_strip_as_string(mock_parm)

    assert result == (mock_item2, mock_item3, mock_item5)

    mock_eval.assert_called_with(mock_parm)


class Test_is_parm_multiparm(object):
    """Test ht.inline.api.is_parm_multiparm."""

    def test_folder_is_multiparm(self, mocker):
        mock_folder_type = mocker.MagicMock(spec=hou.folderType)

        mock_template = mocker.MagicMock(spec=hou.FolderParmTemplate)
        mock_template.folderType.return_value = mock_folder_type

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.parmTemplate.return_value = mock_template

        mock_types = (mock_folder_type,)

        mocker.patch("ht.inline.api._MULTIPARM_FOLDER_TYPES", mock_types)

        assert api.is_parm_multiparm(mock_parm)

    def test_folder_not_multiparm(self, mocker):
        mock_folder_type = mocker.MagicMock(spec=hou.folderType)

        mock_template = mocker.MagicMock(spec=hou.FolderParmTemplate)
        mock_template.folderType.return_value = mock_folder_type

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.parmTemplate.return_value = mock_template

        mock_types = ()

        mocker.patch("ht.inline.api._MULTIPARM_FOLDER_TYPES", mock_types)

        assert not api.is_parm_multiparm(mock_parm)

    def test_not_folder(self, mocker):
        mock_template = mocker.MagicMock(spec=hou.ParmTemplate)

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.parmTemplate.return_value = mock_template

        assert not api.is_parm_multiparm(mock_parm)


class Test_get_multiparm_instances_per_item(object):
    """Test ht.inline.api.get_multiparm_instances_per_item."""

    def test_not_multiparm(self, mocker):
        mocker.patch("ht.inline.api.is_parm_multiparm", return_value=False)

        mock_parm = mocker.MagicMock(spec=hou.Parm)

        with pytest.raises(ValueError):
            api.get_multiparm_instances_per_item(mock_parm)

    def test_parm(self, mocker):
        mock_is_multiparm = mocker.patch(
            "ht.inline.api.is_parm_multiparm", return_value=True
        )
        mock_get = mocker.patch(
            "ht.inline.api._cpp_methods.getMultiParmInstancesPerItem"
        )

        mock_parm_tuple = mocker.MagicMock(spec=hou.ParmTuple)

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.tuple.return_value = mock_parm_tuple

        result = api.get_multiparm_instances_per_item(mock_parm)
        assert result == mock_get.return_value

        mock_is_multiparm.assert_called_with(mock_parm)

        mock_get.assert_called_with(
            mock_parm_tuple.node.return_value, mock_parm_tuple.name.return_value
        )

    def test_parm_tuple(self, mocker):
        mock_is_multiparm = mocker.patch(
            "ht.inline.api.is_parm_multiparm", return_value=True
        )
        mock_get = mocker.patch(
            "ht.inline.api._cpp_methods.getMultiParmInstancesPerItem"
        )

        mock_parm_tuple = mocker.MagicMock(spec=hou.ParmTuple)

        result = api.get_multiparm_instances_per_item(mock_parm_tuple)
        assert result == mock_get.return_value

        mock_is_multiparm.assert_called_with(mock_parm_tuple)

        mock_get.assert_called_with(
            mock_parm_tuple.node.return_value, mock_parm_tuple.name.return_value
        )


class Test_get_multiparm_start_offset(object):
    """Test ht.inline.api.get_multiparm_start_offset."""

    def test_not_multiparm(self, mocker):
        mock_is_multiparm = mocker.patch(
            "ht.inline.api.is_parm_multiparm", return_value=False
        )

        mock_parm = mocker.MagicMock(spec=hou.Parm)

        with pytest.raises(ValueError):
            api.get_multiparm_start_offset(mock_parm)

        mock_is_multiparm.assert_called_with(mock_parm)

    def test_default(self, mocker):
        mock_is_multiparm = mocker.patch(
            "ht.inline.api.is_parm_multiparm", return_value=True
        )

        mock_template = mocker.MagicMock(spec=hou.ParmTemplate)
        mock_template.tags.return_value = {}

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.parmTemplate.return_value = mock_template

        result = api.get_multiparm_start_offset(mock_parm)
        assert result == 1

        mock_is_multiparm.assert_called_with(mock_parm)

    def test_specific(self, mocker):
        mock_is_multiparm = mocker.patch(
            "ht.inline.api.is_parm_multiparm", return_value=True
        )

        mock_template = mocker.MagicMock(spec=hou.ParmTemplate)
        mock_template.tags.return_value = {"multistartoffset": "3"}

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.parmTemplate.return_value = mock_template

        result = api.get_multiparm_start_offset(mock_parm)
        assert result == 3

        mock_is_multiparm.assert_called_with(mock_parm)


class Test_get_multiparm_instance_index(object):
    """Test ht.inline.api.get_multiparm_instance_index."""

    def test_not_multiparm(self, mocker):
        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.isMultiParmInstance.return_value = False

        with pytest.raises(ValueError):
            api.get_multiparm_instance_index(mock_parm)

    def test_parm(self, mocker):
        mock_get = mocker.patch("ht.inline.api._cpp_methods.getMultiParmInstanceIndex")

        mock_parm_tuple = mocker.MagicMock(spec=hou.ParmTuple)

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.isMultiParmInstance.return_value = True
        mock_parm.tuple.return_value = mock_parm_tuple

        result = api.get_multiparm_instance_index(mock_parm)
        assert result == tuple(mock_get.return_value)

        mock_get.assert_called_with(
            mock_parm_tuple.node.return_value, mock_parm_tuple.name.return_value
        )

    def test_parm_tuple(self, mocker):
        mock_get = mocker.patch("ht.inline.api._cpp_methods.getMultiParmInstanceIndex")

        mock_parm_tuple = mocker.MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple.isMultiParmInstance.return_value = True

        result = api.get_multiparm_instance_index(mock_parm_tuple)
        assert result == tuple(mock_get.return_value)

        mock_get.assert_called_with(
            mock_parm_tuple.node.return_value, mock_parm_tuple.name.return_value
        )


class Test_get_multiparm_instances(object):
    """Test ht.inline.api.get_multiparm_instances."""

    def test_not_multiparm(self, mocker):
        mock_is_multiparm = mocker.patch(
            "ht.inline.api.is_parm_multiparm", return_value=False
        )

        mock_parm = mocker.MagicMock(spec=hou.Parm)

        with pytest.raises(ValueError):
            api.get_multiparm_instances(mock_parm)

        mock_is_multiparm.assert_called_with(mock_parm)

    def test_parm(self, mocker):
        mock_is_multiparm = mocker.patch(
            "ht.inline.api.is_parm_multiparm", return_value=True
        )
        mock_get = mocker.patch("ht.inline.api._cpp_methods.getMultiParmInstances")

        mock_node = mocker.MagicMock(spec=hou.Node)

        mock_parm_tuple = mocker.MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple.node.return_value = mock_node

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.tuple.return_value = mock_parm_tuple

        mock_name1 = mocker.MagicMock(spec=str)
        mock_name1.__len__.return_value = 1

        mock_name2 = mocker.MagicMock(spec=str)
        mock_name2.__len__.return_value = 0

        mock_name3 = mocker.MagicMock(spec=str)
        mock_name3.__len__.return_value = 1

        mock_name4 = mocker.MagicMock(spec=str)
        mock_name4.__len__.return_value = 0

        mock_name5 = mocker.MagicMock(spec=str)
        mock_name5.__len__.return_value = 1

        mock_get.return_value = (
            (mock_name1, mock_name2, mock_name3),
            (mock_name4, mock_name5),
        )

        mock_tuple1 = mocker.MagicMock(spec=hou.ParmTuple)
        mock_tuple1.__len__.return_value = 2

        mock_tuple3 = mocker.MagicMock(spec=hou.ParmTuple)
        mock_tuple3.__len__.return_value = 1

        mock_tuple5 = mocker.MagicMock(spec=hou.ParmTuple)
        mock_tuple5.__len__.return_value = 2

        mock_node.parmTuple.side_effect = (mock_tuple1, mock_tuple3, mock_tuple5)

        expected = ((mock_tuple1, mock_tuple3.__getitem__.return_value), (mock_tuple5,))

        result = api.get_multiparm_instances(mock_parm)
        assert result == expected

        mock_is_multiparm.assert_called_with(mock_parm)

        mock_get.assert_called_with(mock_node, mock_parm_tuple.name.return_value)

    def test_parm_tuple(self, mocker):
        mock_is_multiparm = mocker.patch(
            "ht.inline.api.is_parm_multiparm", return_value=True
        )
        mock_get = mocker.patch("ht.inline.api._cpp_methods.getMultiParmInstances")

        mock_node = mocker.MagicMock(spec=hou.Node)

        mock_parm_tuple = mocker.MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple.node.return_value = mock_node

        mock_name1 = mocker.MagicMock(spec=str)
        mock_name1.__len__.return_value = 1

        mock_name2 = mocker.MagicMock(spec=str)
        mock_name2.__len__.return_value = 0

        mock_name3 = mocker.MagicMock(spec=str)
        mock_name3.__len__.return_value = 1

        mock_name4 = mocker.MagicMock(spec=str)
        mock_name4.__len__.return_value = 0

        mock_name5 = mocker.MagicMock(spec=str)
        mock_name5.__len__.return_value = 1

        mock_get.return_value = (
            (mock_name1, mock_name2, mock_name3),
            (mock_name4, mock_name5),
        )

        mock_tuple1 = mocker.MagicMock(spec=hou.ParmTuple)
        mock_tuple1.__len__.return_value = 2

        mock_tuple3 = mocker.MagicMock(spec=hou.ParmTuple)
        mock_tuple3.__len__.return_value = 1

        mock_tuple5 = mocker.MagicMock(spec=hou.ParmTuple)
        mock_tuple5.__len__.return_value = 2

        mock_node.parmTuple.side_effect = (mock_tuple1, mock_tuple3, mock_tuple5)

        expected = ((mock_tuple1, mock_tuple3.__getitem__.return_value), (mock_tuple5,))

        result = api.get_multiparm_instances(mock_parm_tuple)
        assert result == expected

        mock_is_multiparm.assert_called_with(mock_parm_tuple)

        mock_get.assert_called_with(mock_node, mock_parm_tuple.name.return_value)


class Test_get_multiparm_instance_values(object):
    """Test ht.inline.api.get_multiparm_instance_values."""

    def test_not_multiparm(self, mocker):
        mock_is_multiparm = mocker.patch(
            "ht.inline.api.is_parm_multiparm", return_value=False
        )

        mock_parm = mocker.MagicMock(spec=hou.Parm)

        with pytest.raises(ValueError):
            api.get_multiparm_instance_values(mock_parm)

        mock_is_multiparm.assert_called_with(mock_parm)

    def test_parm(self, mocker):
        mock_is_multiparm = mocker.patch(
            "ht.inline.api.is_parm_multiparm", return_value=True
        )
        mock_get = mocker.patch("ht.inline.api.get_multiparm_instances")

        mock_parm_tuple = mocker.MagicMock(spec=hou.ParmTuple)

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.tuple.return_value = mock_parm_tuple

        mock_tuple1 = mocker.MagicMock(spec=hou.ParmTuple)
        mock_tuple2 = mocker.MagicMock(spec=hou.ParmTuple)

        mock_parm1 = mocker.MagicMock(spec=hou.Parm)

        mock_get.return_value = ((mock_tuple1, mock_parm1), (mock_tuple2,))

        expected = (
            (mock_tuple1.eval.return_value, mock_parm1.eval.return_value),
            (mock_tuple2.eval.return_value,),
        )

        result = api.get_multiparm_instance_values(mock_parm)
        assert result == expected

        mock_is_multiparm.assert_called_with(mock_parm)

        mock_get.assert_called_with(mock_parm_tuple)

    def test_parm_tuple(self, mocker):
        mock_is_multiparm = mocker.patch(
            "ht.inline.api.is_parm_multiparm", return_value=True
        )
        mock_get = mocker.patch("ht.inline.api.get_multiparm_instances")

        mock_parm_tuple = mocker.MagicMock(spec=hou.ParmTuple)

        mock_tuple1 = mocker.MagicMock(spec=hou.ParmTuple)
        mock_tuple2 = mocker.MagicMock(spec=hou.ParmTuple)

        mock_parm1 = mocker.MagicMock(spec=hou.Parm)

        mock_get.return_value = ((mock_tuple1, mock_parm1), (mock_tuple2,))

        expected = (
            (mock_tuple1.eval.return_value, mock_parm1.eval.return_value),
            (mock_tuple2.eval.return_value,),
        )

        result = api.get_multiparm_instance_values(mock_parm_tuple)
        assert result == expected

        mock_is_multiparm.assert_called_with(mock_parm_tuple)

        mock_get.assert_called_with(mock_parm_tuple)


class Test_eval_multiparm_instance(object):
    """Test ht.inline.api.eval_multiparm_instance."""

    def test_invalid_number_signs(self, mocker):
        mock_node = mocker.MagicMock(spec=hou.Node)

        mock_name = mocker.MagicMock(spec=str)
        mock_name.count.return_value = 2

        mock_index = mocker.MagicMock(spec=int)

        with pytest.raises(ValueError):
            api.eval_multiparm_instance(mock_node, mock_name, mock_index)

        mock_name.count.assert_called_with("#")

    def test_invalid_parm_name(self, mocker):
        mock_ptg = mocker.MagicMock(spec=hou.ParmTemplateGroup)
        mock_ptg.find.return_value = None

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.parmTemplateGroup.return_value = mock_ptg

        mock_name = mocker.MagicMock(spec=str)
        mock_name.count.return_value = 1

        mock_index = mocker.MagicMock(spec=int)

        with pytest.raises(ValueError):
            api.eval_multiparm_instance(mock_node, mock_name, mock_index)

        mock_name.count.assert_called_with("#")

    def test_not_multiparm(self, mocker):
        mock_is_multiparm = mocker.patch(
            "ht.inline.api.is_parm_multiparm", return_value=False
        )

        mock_parm = mocker.MagicMock(spec=hou.Parm)

        mock_template = mocker.MagicMock(spec=hou.ParmTemplate)

        mock_folder_template = mocker.MagicMock(spec=hou.FolderParmTemplate)

        mock_ptg = mocker.MagicMock(spec=hou.ParmTemplateGroup)
        mock_ptg.containingFolder.return_value = mock_folder_template
        mock_ptg.find.return_value = mock_template

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.parmTemplateGroup.return_value = mock_ptg
        mock_node.parm.return_value = mock_parm

        mock_name = mocker.MagicMock(spec=str)
        mock_name.count.return_value = 1

        mock_index = mocker.MagicMock(spec=int)

        with pytest.raises(ValueError):
            api.eval_multiparm_instance(mock_node, mock_name, mock_index)

        mock_name.count.assert_called_with("#")

        mock_ptg.containingFolder.assert_called_with(mock_name)
        mock_node.parm.assert_called_with(mock_folder_template.name.return_value)

        mock_is_multiparm.assert_called_with(mock_parm)

    def test_invalid_index(self, mocker):
        mock_is_multiparm = mocker.patch(
            "ht.inline.api.is_parm_multiparm", return_value=True
        )

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = mocker.MagicMock(spec=int)

        mock_template = mocker.MagicMock(spec=hou.ParmTemplate)

        mock_folder_template = mocker.MagicMock(spec=hou.FolderParmTemplate)

        mock_ptg = mocker.MagicMock(spec=hou.ParmTemplateGroup)
        mock_ptg.containingFolder.return_value = mock_folder_template
        mock_ptg.find.return_value = mock_template

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.parmTemplateGroup.return_value = mock_ptg
        mock_node.parm.return_value = mock_parm

        mock_name = mocker.MagicMock(spec=str)
        mock_name.count.return_value = 1

        mock_index = mocker.MagicMock()
        mock_index.__ge__.return_value = True

        with pytest.raises(IndexError):
            api.eval_multiparm_instance(mock_node, mock_name, mock_index)

        mock_name.count.assert_called_with("#")

        mock_ptg.containingFolder.assert_called_with(mock_name)
        mock_node.parm.assert_called_with(mock_folder_template.name.return_value)

        mock_is_multiparm.assert_called_with(mock_parm)

        mock_index.__ge__.assert_called_with(mock_parm.eval.return_value)

    def test_float_single_component(self, mocker):
        mock_is_multiparm = mocker.patch(
            "ht.inline.api.is_parm_multiparm", return_value=True
        )
        mock_get = mocker.patch("ht.inline.api.get_multiparm_start_offset")
        mock_eval = mocker.patch(
            "ht.inline.api._cpp_methods.eval_multiparm_instance_float"
        )

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = mocker.MagicMock(spec=int)

        mock_template = mocker.MagicMock(spec=hou.ParmTemplate)
        mock_template.dataType.return_value = hou.parmData.Float
        mock_template.numComponents.return_value = 1

        mock_folder_template = mocker.MagicMock(spec=hou.FolderParmTemplate)

        mock_ptg = mocker.MagicMock(spec=hou.ParmTemplateGroup)
        mock_ptg.containingFolder.return_value = mock_folder_template
        mock_ptg.find.return_value = mock_template

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.parmTemplateGroup.return_value = mock_ptg
        mock_node.parm.return_value = mock_parm

        mock_name = mocker.MagicMock(spec=str)
        mock_name.count.return_value = 1

        mock_index = mocker.MagicMock()
        mock_index.__ge__.return_value = False

        result = api.eval_multiparm_instance(mock_node, mock_name, mock_index)
        assert result == mock_eval.return_value

        mock_name.count.assert_called_with("#")

        mock_ptg.containingFolder.assert_called_with(mock_name)
        mock_node.parm.assert_called_with(mock_folder_template.name.return_value)

        mock_is_multiparm.assert_called_with(mock_parm)

        mock_index.__ge__.assert_called_with(mock_parm.eval.return_value)

        mock_get.assert_called_with(mock_parm)

        mock_eval.assert_called_with(
            mock_node, mock_name, 0, mock_index, mock_get.return_value
        )

    def test_int_multiple_components(self, mocker):
        mock_is_multiparm = mocker.patch(
            "ht.inline.api.is_parm_multiparm", return_value=True
        )
        mock_get = mocker.patch("ht.inline.api.get_multiparm_start_offset")
        mock_eval = mocker.patch(
            "ht.inline.api._cpp_methods.eval_multiparm_instance_int"
        )

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = mocker.MagicMock(spec=int)

        mock_template = mocker.MagicMock(spec=hou.ParmTemplate)
        mock_template.dataType.return_value = hou.parmData.Int
        mock_template.numComponents.return_value = 2

        mock_folder_template = mocker.MagicMock(spec=hou.FolderParmTemplate)

        mock_ptg = mocker.MagicMock(spec=hou.ParmTemplateGroup)
        mock_ptg.containingFolder.return_value = mock_folder_template
        mock_ptg.find.return_value = mock_template

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.parmTemplateGroup.return_value = mock_ptg
        mock_node.parm.return_value = mock_parm

        mock_name = mocker.MagicMock(spec=str)
        mock_name.count.return_value = 1

        mock_index = mocker.MagicMock()
        mock_index.__ge__.return_value = False

        result = api.eval_multiparm_instance(mock_node, mock_name, mock_index)
        assert result == (mock_eval.return_value, mock_eval.return_value)

        mock_name.count.assert_called_with("#")

        mock_ptg.containingFolder.assert_called_with(mock_name)
        mock_node.parm.assert_called_with(mock_folder_template.name.return_value)

        mock_is_multiparm.assert_called_with(mock_parm)

        mock_index.__ge__.assert_called_with(mock_parm.eval.return_value)

        mock_get.assert_called_with(mock_parm)

        mock_eval.assert_has_calls(
            [
                mocker.call(mock_node, mock_name, 0, mock_index, mock_get.return_value),
                mocker.call(mock_node, mock_name, 1, mock_index, mock_get.return_value),
            ]
        )

    def test_string_multiple_components(self, mocker):
        mock_is_multiparm = mocker.patch(
            "ht.inline.api.is_parm_multiparm", return_value=True
        )
        mock_get = mocker.patch("ht.inline.api.get_multiparm_start_offset")
        mock_eval = mocker.patch(
            "ht.inline.api._cpp_methods.eval_multiparm_instance_string"
        )

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = mocker.MagicMock(spec=int)

        mock_template = mocker.MagicMock(spec=hou.ParmTemplate)
        mock_template.dataType.return_value = hou.parmData.String
        mock_template.numComponents.return_value = 3

        mock_folder_template = mocker.MagicMock(spec=hou.FolderParmTemplate)

        mock_ptg = mocker.MagicMock(spec=hou.ParmTemplateGroup)
        mock_ptg.containingFolder.return_value = mock_folder_template
        mock_ptg.find.return_value = mock_template

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.parmTemplateGroup.return_value = mock_ptg
        mock_node.parm.return_value = mock_parm

        mock_name = mocker.MagicMock(spec=str)
        mock_name.count.return_value = 1

        mock_index = mocker.MagicMock()
        mock_index.__ge__.return_value = False

        result = api.eval_multiparm_instance(mock_node, mock_name, mock_index)
        assert result == (
            mock_eval.return_value,
            mock_eval.return_value,
            mock_eval.return_value,
        )

        mock_name.count.assert_called_with("#")

        mock_ptg.containingFolder.assert_called_with(mock_name)
        mock_node.parm.assert_called_with(mock_folder_template.name.return_value)

        mock_is_multiparm.assert_called_with(mock_parm)

        mock_index.__ge__.assert_called_with(mock_parm.eval.return_value)

        mock_get.assert_called_with(mock_parm)

        mock_eval.assert_has_calls(
            [
                mocker.call(mock_node, mock_name, 0, mock_index, mock_get.return_value),
                mocker.call(mock_node, mock_name, 1, mock_index, mock_get.return_value),
                mocker.call(mock_node, mock_name, 2, mock_index, mock_get.return_value),
            ]
        )

    def test_invalid_type(self, mocker):
        mock_is_multiparm = mocker.patch(
            "ht.inline.api.is_parm_multiparm", return_value=True
        )
        mock_get = mocker.patch("ht.inline.api.get_multiparm_start_offset")
        mocker.patch("ht.inline.api._cpp_methods.eval_multiparm_instance_string")

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = mocker.MagicMock(spec=int)

        mock_template = mocker.MagicMock(spec=hou.ParmTemplate)
        mock_template.dataType.return_value = hou.parmData.Data
        mock_template.numComponents.return_value = 3

        mock_folder_template = mocker.MagicMock(spec=hou.FolderParmTemplate)

        mock_ptg = mocker.MagicMock(spec=hou.ParmTemplateGroup)
        mock_ptg.containingFolder.return_value = mock_folder_template
        mock_ptg.find.return_value = mock_template

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.parmTemplateGroup.return_value = mock_ptg
        mock_node.parm.return_value = mock_parm

        mock_name = mocker.MagicMock(spec=str)
        mock_name.count.return_value = 1

        mock_index = mocker.MagicMock()
        mock_index.__ge__.return_value = False

        with pytest.raises(TypeError):
            api.eval_multiparm_instance(mock_node, mock_name, mock_index)

        mock_name.count.assert_called_with("#")

        mock_ptg.containingFolder.assert_called_with(mock_name)
        mock_node.parm.assert_called_with(mock_folder_template.name.return_value)

        mock_is_multiparm.assert_called_with(mock_parm)

        mock_index.__ge__.assert_called_with(mock_parm.eval.return_value)

        mock_get.assert_called_with(mock_parm)


def test_disconnect_all_inputs(mocker):
    """Test ht.inline.api.disconnect_all_inputs."""
    mock_undos = mocker.patch("ht.inline.api.hou.undos.group")

    mock_connection1 = mocker.MagicMock(spec=hou.NodeConnection)
    mock_connection2 = mocker.MagicMock(spec=hou.NodeConnection)

    mock_node = mocker.MagicMock(spec=hou.Node)
    mock_node.inputConnections.return_value = (mock_connection1, mock_connection2)

    api.disconnect_all_inputs(mock_node)

    mock_undos.assert_called()

    mock_node.setInput.assert_has_calls(
        [
            mocker.call(mock_connection2.inputIndex.return_value, None),
            mocker.call(mock_connection1.inputIndex.return_value, None),
        ]
    )


def test_disconnect_all_outputs(mocker):
    """Test ht.inline.api.disconnect_all_outputs."""
    mock_undos = mocker.patch("ht.inline.api.hou.undos.group")

    mock_connection1 = mocker.MagicMock(spec=hou.NodeConnection)
    mock_connection2 = mocker.MagicMock(spec=hou.NodeConnection)

    mock_node = mocker.MagicMock(spec=hou.Node)
    mock_node.outputConnections.return_value = (mock_connection1, mock_connection2)

    api.disconnect_all_outputs(mock_node)

    mock_undos.assert_called()

    mock_connection1.outputNode.return_value.setInput.assert_called_with(
        mock_connection1.inputIndex.return_value, None
    )
    mock_connection2.outputNode.return_value.setInput.assert_called_with(
        mock_connection2.inputIndex.return_value, None
    )


class Test_get_node_message_nodes(object):
    """Test ht.inline.api.get_node_message_nodes."""

    def test(self, mocker):
        mock_section = mocker.MagicMock(spec=hou.HDASection)

        mock_definition = mocker.MagicMock(spec=hou.HDADefinition)
        mock_definition.sections.return_value = {"MessageNodes": mock_section}

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = mock_definition

        result = api.get_node_message_nodes(mock_node)
        assert result == mock_node.glob.return_value

        mock_node.glob.assert_called_with(mock_section.contents.return_value)

    def test_no_section(self, mocker):
        mock_definition = mocker.MagicMock(spec=hou.HDADefinition)
        mock_definition.sections.return_value = {}

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = mock_definition

        result = api.get_node_message_nodes(mock_node)
        assert result == ()

    def test_not_hda(self, mocker):
        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = None

        result = api.get_node_message_nodes(mock_node)
        assert result == ()


class Test_get_node_editable_nodes(object):
    """Test ht.inline.api.get_node_editable_nodes."""

    def test(self, mocker):
        mock_section = mocker.MagicMock(spec=hou.HDASection)

        mock_definition = mocker.MagicMock(spec=hou.HDADefinition)
        mock_definition.sections.return_value = {"EditableNodes": mock_section}

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = mock_definition

        result = api.get_node_editable_nodes(mock_node)
        assert result == mock_node.glob.return_value

        mock_node.glob.assert_called_with(mock_section.contents.return_value)

    def test_no_section(self, mocker):
        mock_definition = mocker.MagicMock(spec=hou.HDADefinition)
        mock_definition.sections.return_value = {}

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = mock_definition

        result = api.get_node_editable_nodes(mock_node)
        assert result == ()

    def test_not_hda(self, mocker):
        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = None

        result = api.get_node_editable_nodes(mock_node)
        assert result == ()


class Test_get_node_dive_target(object):
    """Test ht.inline.api.get_node_dive_target."""

    def test(self, mocker):
        mock_section = mocker.MagicMock(spec=hou.HDASection)

        mock_definition = mocker.MagicMock(spec=hou.HDADefinition)
        mock_definition.sections.return_value = {"DiveTarget": mock_section}

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = mock_definition

        result = api.get_node_dive_target(mock_node)
        assert result == mock_node.node.return_value

        mock_node.node.assert_called_with(mock_section.contents.return_value)

    def test_no_section(self, mocker):
        mock_definition = mocker.MagicMock(spec=hou.HDADefinition)
        mock_definition.sections.return_value = {}

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = mock_definition

        result = api.get_node_dive_target(mock_node)
        assert result is None

    def test_not_hda(self, mocker):
        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = None

        result = api.get_node_dive_target(mock_node)
        assert result is None


class Test_get_node_representative_node(object):
    """Test ht.inline.api.get_node_representative_node."""

    def test(self, mocker):
        mock_path = mocker.MagicMock(spec=str)
        mock_path.__len__.return_value = 1

        mock_definition = mocker.MagicMock(spec=hou.HDADefinition)
        mock_definition.representativeNodePath.return_value = mock_path

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = mock_definition

        result = api.get_node_representative_node(mock_node)
        assert result == mock_node.node.return_value

        mock_node.node.assert_called_with(mock_path)

    def test_empty_path(self, mocker):
        mock_path = mocker.MagicMock(spec=str)
        mock_path.__len__.return_value = 0

        mock_definition = mocker.MagicMock(spec=hou.HDADefinition)
        mock_definition.representativeNodePath.return_value = mock_path

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = mock_definition

        result = api.get_node_representative_node(mock_node)
        assert result is None

        mock_node.node.assert_not_called()

    def test_not_hda(self, mocker):
        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = None

        result = api.get_node_representative_node(mock_node)
        assert result is None


class Test_node_is_contained_by(object):
    """Test ht.inline.api.node_is_contained_by."""

    def test_is_parent(self, mocker):
        mock_containing = mocker.MagicMock(spec=hou.Node)

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.parent.return_value = mock_containing

        assert api.node_is_contained_by(mock_node, mock_containing)

    def test_parent_parent(self, mocker):
        mock_containing = mocker.MagicMock(spec=hou.Node)

        mock_parent = mocker.MagicMock(spec=hou.Node)
        mock_parent.parent.return_value = mock_containing

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.parent.return_value = mock_parent

        assert api.node_is_contained_by(mock_node, mock_containing)

    def test_not_contained(self, mocker):
        mock_containing = mocker.MagicMock(spec=hou.Node)

        mock_parent = mocker.MagicMock(spec=hou.Node)
        mock_parent.parent.return_value = None

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.parent.return_value = mock_parent

        assert not api.node_is_contained_by(mock_node, mock_containing)


def test_node_author_name(mocker):
    """Test ht.inline.api.node_author_name."""
    mock_get_author = mocker.patch("ht.inline.api._cpp_methods.getNodeAuthor")

    mock_node = mocker.MagicMock(spec=hou.Node)

    result = api.node_author_name(mock_node)

    assert (
        result
        == mock_get_author.return_value.split.return_value.__getitem__.return_value
    )

    mock_get_author.return_value.split.assert_called_with("@")
    mock_get_author.return_value.split.return_value.__getitem__.assert_called_with(0)


def test_set_node_type_icon(mocker):
    """Test ht.inline.api.set_node_type_icon."""
    mock_set_icon = mocker.patch("ht.inline.api._cpp_methods.setNodeTypeIcon")

    mock_type = mocker.MagicMock(spec=hou.NodeType)
    mock_icon = mocker.MagicMock(spec=str)

    api.set_node_type_icon(mock_type, mock_icon)
    mock_set_icon.assert_called_with(mock_type, mock_icon)


def test_set_node_type_default_icon(mocker):
    """Test ht.inline.api.set_node_type_default_icon."""
    mock_set_icon = mocker.patch("ht.inline.api._cpp_methods.setNodeTypeDefaultIcon")

    mock_type = mocker.MagicMock(spec=hou.NodeType)

    api.set_node_type_default_icon(mock_type)
    mock_set_icon.assert_called_with(mock_type)


def test_is_node_type_python(mocker):
    """Test ht.inline.api.is_node_type_python."""
    mock_is_python = mocker.patch("ht.inline.api._cpp_methods.isNodeTypePythonType")

    mock_type = mocker.MagicMock(spec=hou.NodeType)

    api.is_node_type_python(mock_type)
    mock_is_python.assert_called_with(mock_type)


def test_is_node_type_subnet(mocker):
    """Test ht.inline.api.is_node_type_subnet."""
    mock_is_subnet = mocker.patch("ht.inline.api._cpp_methods.isNodeTypeSubnetType")

    mock_type = mocker.MagicMock(spec=hou.NodeType)

    api.is_node_type_subnet(mock_type)
    mock_is_subnet.assert_called_with(mock_type)


def test_vector_component_along(mocker):
    """Test ht.inline.api.vector_component_along."""
    mock_vec1 = mocker.MagicMock(spec=hou.Vector3)
    mock_vec2 = mocker.MagicMock(spec=hou.Vector3)

    result = api.vector_component_along(mock_vec1, mock_vec2)
    assert result == mock_vec1.dot.return_value

    mock_vec1.dot.assert_called_with(mock_vec2.normalized.return_value)


class Test_vector_project_along(object):
    """Test ht.inline.api.vector_project_along."""

    def test_zero(self, mocker):
        mock_vec1 = mocker.MagicMock(spec=hou.Vector3)
        vec2 = hou.Vector3()

        with pytest.raises(ValueError):
            api.vector_project_along(mock_vec1, vec2)

    def test(self, mocker):
        mock_along = mocker.patch("ht.inline.api.vector_component_along")

        mock_vec1 = mocker.MagicMock(spec=hou.Vector3)
        mock_vec2 = mocker.MagicMock(spec=hou.Vector3)

        result = api.vector_project_along(mock_vec1, mock_vec2)
        assert result == mock_vec2.normalized.return_value * mock_along.return_value

        mock_along.assert_called_with(mock_vec1, mock_vec2)


class Test_vector_contains_nans(object):
    """Test ht.inline.api.vector_contains_nans."""

    def test_contains(self, mocker):
        mock_is_nan = mocker.patch("ht.inline.api.math.isnan")

        mock_value1 = mocker.MagicMock(spec=float)
        mock_value2 = mocker.MagicMock(spec=float)
        mock_value3 = mocker.MagicMock(spec=float)

        values = (mock_value1, mock_value2, mock_value3)

        mock_vec = mocker.MagicMock(spec=hou.Vector3)
        mock_vec.__getitem__.side_effect = values

        mock_is_nan.side_effect = (False, True, False)

        assert api.vector_contains_nans(mock_vec)

        mock_is_nan.assert_has_calls(
            [mocker.call(mock_value1), mocker.call(mock_value2)]
        )

    def test_does_not_contain(self, mocker):
        mock_is_nan = mocker.patch("ht.inline.api.math.isnan")

        mock_value1 = mocker.MagicMock(spec=float)
        mock_value2 = mocker.MagicMock(spec=float)
        mock_value3 = mocker.MagicMock(spec=float)

        values = (mock_value1, mock_value2, mock_value3)

        mock_vec = mocker.MagicMock(spec=hou.Vector3)
        mock_vec.__getitem__.side_effect = values

        mock_is_nan.side_effect = (False, False, False)

        assert not api.vector_contains_nans(mock_vec)

        mock_is_nan.assert_has_calls(
            [
                mocker.call(mock_value1),
                mocker.call(mock_value2),
                mocker.call(mock_value3),
            ]
        )


def test_vector_compute_dual(mocker):
    """Test ht.inline.api.vector_compute_dual."""
    mock_mat = mocker.patch("ht.inline.api.hou.Matrix3", autospec=True)
    mock_get = mocker.patch("ht.inline.api._cpp_methods.vector3GetDual")

    mock_vec = mocker.MagicMock(spec=hou.Vector3)

    result = api.vector_compute_dual(mock_vec)
    assert result == mock_mat.return_value

    mock_get.assert_called_with(mock_vec, mock_mat.return_value)


class Test_is_identity_matrix(object):
    """Test ht.inline.api.is_identity_matrix."""

    def test_mat3_identity(self, mocker):
        mock_mat = mocker.MagicMock(spec=hou.Matrix3)

        mock_mat3 = mocker.patch("ht.inline.api.hou.Matrix3.__new__", autospec=True)
        mock_mat3.return_value = mock_mat

        assert api.is_identity_matrix(mock_mat)

        mock_mat3.return_value.setToIdentity.assert_called()

    def test_mat3_not_identity(self, mocker):
        mock_mat = mocker.MagicMock(spec=hou.Matrix3)

        mock_mat3 = mocker.patch("ht.inline.api.hou.Matrix3.__new__", autospec=True)
        assert not api.is_identity_matrix(mock_mat)

        mock_mat3.return_value.setToIdentity.assert_called()

    def test_mat4_identity(self, mocker):
        mock_ident = mocker.patch("ht.inline.api.hou.hmath.identityTransform")

        mock_mat = mocker.MagicMock(spec=hou.Matrix4)

        mock_ident.return_value = mock_mat

        assert api.is_identity_matrix(mock_mat)

    def test_mat4_not_identity(self, mocker):
        mocker.patch("ht.inline.api.hou.hmath.identityTransform")

        mock_mat = mocker.MagicMock(spec=hou.Matrix4)

        assert not api.is_identity_matrix(mock_mat)


def test_set_matrix_translates(mocker):
    """Test ht.inline.api.set_matrix_translates."""
    mock_mat = mocker.MagicMock(spec=hou.Matrix4)
    mock_values = mocker.MagicMock(spec=tuple)

    api.set_matrix_translates(mock_mat, mock_values)

    mock_mat.setAt.assert_has_calls(
        [
            mocker.call(3, 0, mock_values.__getitem__.return_value),
            mocker.call(3, 1, mock_values.__getitem__.return_value),
            mocker.call(3, 2, mock_values.__getitem__.return_value),
        ]
    )

    mock_values.__getitem__.assert_has_calls(
        [mocker.call(0), mocker.call(1), mocker.call(2)]
    )


def test_build_lookat_matrix(mocker):
    """Test ht.inline.api.build_lookat_matrix."""
    mock_mat3 = mocker.patch("ht.inline.api.hou.Matrix3", autospec=True)
    mock_build = mocker.patch("ht.inline.api._cpp_methods.buildLookatMatrix")

    mock_from_vec = mocker.MagicMock(spec=hou.Vector3)
    mock_to_vec = mocker.MagicMock(spec=hou.Vector3)
    mock_up_vec = mocker.MagicMock(spec=hou.Vector3)

    result = api.build_lookat_matrix(mock_from_vec, mock_to_vec, mock_up_vec)
    assert result == mock_mat3.return_value

    mock_build.assert_called_with(
        mock_mat3.return_value, mock_from_vec, mock_to_vec, mock_up_vec
    )


class Test_get_oriented_point_transform(object):
    """Test ht.inline.api.get_oriented_point_transform."""

    def test_face(self, mocker, fix_hou_exceptions):
        """Test where the bound prim is a hou.Face"""
        mock_connected = mocker.patch("ht.inline.api.connected_prims")
        mocker.patch("ht.inline.api._cpp_methods.point_instance_transform")
        mocker.patch("ht.inline.api.hou.Matrix4", autospec=True)

        mock_face = mocker.MagicMock(spec=hou.Face)

        mock_connected.return_value = (mock_face,)

        mock_point = mocker.MagicMock(spec=hou.Point)

        with pytest.raises(hou.OperationFailed):
            api.get_oriented_point_transform(mock_point)

        mock_connected.assert_called_with(mock_point)

    def test_surface(self, mocker, fix_hou_exceptions):
        """Test where the bound prim is a hou.Surface"""
        mock_connected = mocker.patch("ht.inline.api.connected_prims")
        mocker.patch("ht.inline.api._cpp_methods.point_instance_transform")
        mocker.patch("ht.inline.api.hou.Matrix4", autospec=True)

        mock_surface = mocker.MagicMock(spec=hou.Surface)

        mock_connected.return_value = (mock_surface,)

        mock_point = mocker.MagicMock(spec=hou.Point)

        with pytest.raises(hou.OperationFailed):
            api.get_oriented_point_transform(mock_point)

        mock_connected.assert_called_with(mock_point)

    def test_valid_prim(self, mocker, fix_hou_exceptions):
        """Test where the bound prim is a not a hou.Face of hou.Surface"""
        mock_connected = mocker.patch("ht.inline.api.connected_prims")
        mocker.patch("ht.inline.api._cpp_methods.point_instance_transform")
        mock_build = mocker.patch("hou.hmath.buildTranslate")
        mock_mat4 = mocker.patch("ht.inline.api.hou.Matrix4", autospec=True)

        mock_valid_prim = mocker.MagicMock(spec=hou.PackedPrim)
        mock_face = mocker.MagicMock(spec=hou.Surface)

        mock_connected.return_value = (mock_valid_prim, mock_face)

        mock_point = mocker.MagicMock(spec=hou.Point)

        result = api.get_oriented_point_transform(mock_point)

        assert result == mock_mat4.return_value * mock_build.return_value

        mock_mat4.assert_called_with(mock_valid_prim.transform.return_value)
        mock_build.assert_called_with(mock_point.position.return_value)

        mock_connected.assert_called_with(mock_point)

    def test_unattached_point(self, mocker, fix_hou_exceptions):
        """Test where the point is not attached."""
        mock_connected = mocker.patch("ht.inline.api.connected_prims", return_value=())
        mock_point_instance_transform = mocker.patch(
            "ht.inline.api._cpp_methods.point_instance_transform"
        )

        mock_point = mocker.MagicMock(spec=hou.Point)

        result = api.get_oriented_point_transform(mock_point)

        assert result == mock_point_instance_transform.return_value

        mock_connected.assert_called_with(mock_point)
        mock_point_instance_transform.assert_called_with(mock_point)


def test_point_instance_transform(mocker):
    """Test ht.inline.api.point_instance_transform."""
    mock_get_point_xform = mocker.patch(
        "ht.inline.api._cpp_methods.point_instance_transform"
    )
    mock_mat4 = mocker.patch("ht.inline.api.hou.Matrix4", autospec=True)

    mock_point = mocker.MagicMock(spec=hou.Point)

    result = api.point_instance_transform(mock_point)

    assert result == mock_mat4.return_value

    mock_get_point_xform.assert_called_with(
        mock_point.geometry.return_value, mock_point.number.return_value
    )

    mock_mat4.assert_called_with(mock_get_point_xform.return_value)


class Test_build_instance_matrix(object):
    """Test ht.inline.api.build_instance_matrix."""

    def test_orient(self, mocker):
        mocker.patch("ht.inline.api.hou.Vector3", autospec=True)
        mock_build_scale = mocker.patch("ht.inline.api.hou.hmath.buildScale")
        mock_mat4 = mocker.patch("ht.inline.api.hou.Matrix4", autospec=True)
        mock_build_trans = mocker.patch("ht.inline.api.hou.hmath.buildTranslate")

        mock_pos = mocker.MagicMock(spec=hou.Vector3)
        mock_dir = mocker.MagicMock(spec=hou.Vector3)
        mock_pscale = mocker.MagicMock(spec=float)
        mock_scale = mocker.MagicMock(spec=hou.Vector3)
        mock_up_vector = mocker.MagicMock(spec=hou.Vector3)
        mock_rot = mocker.MagicMock(spec=hou.Quaternion)
        mock_trans = mocker.MagicMock(spec=hou.Vector3)
        mock_pivot = mocker.MagicMock(spec=hou.Vector3)
        mock_orient = mocker.MagicMock(spec=hou.Quaternion)

        result = api.build_instance_matrix(
            mock_pos,
            mock_dir,
            mock_pscale,
            mock_scale,
            mock_up_vector,
            mock_rot,
            mock_trans,
            mock_pivot,
            mock_orient,
        )

        assert (
            result
            == mock_build_trans.return_value
            * mock_build_scale.return_value
            * mock_mat4.return_value
            * mock_mat4.return_value
            * mock_build_trans.return_value
        )

        mock_scale.__mul__.assert_called_with(mock_pscale)
        mock_build_scale.assert_called_with(mock_scale.__mul__.return_value)

        mock_build_trans.assert_has_calls(
            [mocker.call(mock_pivot), mocker.call(mock_pos + mock_trans)]
        )

        mock_mat4.assert_has_calls(
            [
                mocker.call(mock_rot.extractRotationMatrix3.return_value),
                mocker.call(mock_orient.extractRotationMatrix3.return_value),
            ]
        )

    def test_up_vector(self, mocker):
        mock_vec3 = mocker.patch("ht.inline.api.hou.Vector3", autospec=True)
        mock_build_scale = mocker.patch("ht.inline.api.hou.hmath.buildScale")
        mock_mat4 = mocker.patch("ht.inline.api.hou.Matrix4", autospec=True)
        mock_build_trans = mocker.patch("ht.inline.api.hou.hmath.buildTranslate")
        mock_build_lookat = mocker.patch("ht.inline.api.build_lookat_matrix")

        mock_pos = mocker.MagicMock(spec=hou.Vector3)
        mock_dir = mocker.MagicMock(spec=hou.Vector3)
        mock_pscale = mocker.MagicMock(spec=float)
        mock_scale = mocker.MagicMock(spec=hou.Vector3)
        mock_up_vector = mocker.MagicMock(spec=hou.Vector3)
        mock_rot = mocker.MagicMock(spec=hou.Quaternion)
        mock_trans = mocker.MagicMock(spec=hou.Vector3)
        mock_pivot = mocker.MagicMock(spec=hou.Vector3)

        result = api.build_instance_matrix(
            mock_pos,
            mock_dir,
            mock_pscale,
            mock_scale,
            mock_up_vector,
            mock_rot,
            mock_trans,
            mock_pivot,
            None,
        )

        assert (
            result
            == mock_build_trans.return_value
            * mock_build_scale.return_value
            * mock_mat4.return_value
            * mock_mat4.return_value
            * mock_build_trans.return_value
        )

        mock_scale.__mul__.assert_called_with(mock_pscale)
        mock_build_scale.assert_called_with(mock_scale.__mul__.return_value)

        mock_build_trans.assert_has_calls(
            [mocker.call(mock_pivot), mocker.call(mock_pos + mock_trans)]
        )

        mock_mat4.assert_has_calls(
            [
                mocker.call(mock_rot.extractRotationMatrix3.return_value),
                mocker.call(mock_build_lookat.return_value),
            ]
        )

        mock_build_lookat.assert_called_with(
            mock_dir, mock_vec3.return_value, mock_up_vector
        )

    def test_up_vector_is_zero_vec(self, mocker):
        mock_vec3 = mocker.patch("ht.inline.api.hou.Vector3", autospec=True)
        mock_build_scale = mocker.patch("ht.inline.api.hou.hmath.buildScale")
        mock_mat4 = mocker.patch("ht.inline.api.hou.Matrix4", autospec=True)
        mock_build_trans = mocker.patch("ht.inline.api.hou.hmath.buildTranslate")

        mock_pos = mocker.MagicMock(spec=hou.Vector3)
        mock_dir = mocker.MagicMock(spec=hou.Vector3)
        mock_pscale = mocker.MagicMock(spec=float)
        mock_scale = mocker.MagicMock(spec=hou.Vector3)
        mock_up_vector = mock_vec3.return_value
        mock_rot = mocker.MagicMock(spec=hou.Quaternion)
        mock_trans = mocker.MagicMock(spec=hou.Vector3)
        mock_pivot = mocker.MagicMock(spec=hou.Vector3)

        result = api.build_instance_matrix(
            mock_pos,
            mock_dir,
            mock_pscale,
            mock_scale,
            mock_up_vector,
            mock_rot,
            mock_trans,
            mock_pivot,
            None,
        )

        assert (
            result
            == mock_build_trans.return_value
            * mock_build_scale.return_value
            * mock_vec3.return_value.matrixToRotateTo.return_value
            * mock_mat4.return_value
            * mock_build_trans.return_value
        )

        mock_scale.__mul__.assert_called_with(mock_pscale)
        mock_build_scale.assert_called_with(mock_scale.__mul__.return_value)

        mock_build_trans.assert_has_calls(
            [mocker.call(mock_pivot), mocker.call(mock_pos + mock_trans)]
        )

        mock_mat4.assert_has_calls(
            [mocker.call(mock_rot.extractRotationMatrix3.return_value)]
        )

        mock_vec3.return_value.matrixToRotateTo.assert_called_with(mock_dir)


class Test_is_node_digital_asset(object):
    """Test ht.inline.api.is_node_digital_asset."""

    def test_true(self, mocker):
        mock_node = mocker.MagicMock(spec=hou.Node)

        assert api.is_node_digital_asset(mock_node)

    def test_false(self, mocker):
        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.type.return_value.definition.return_value = None

        assert not api.is_node_digital_asset(mock_node)


class Test_asset_file_meta_source(object):
    """Test ht.inline.api.asset_file_meta_source."""

    def test_not_installed(self, mocker):
        mocker.patch("ht.inline.api.hou.hda.loadedFiles", return_value=())

        mock_path = mocker.MagicMock(spec=str)

        assert api.asset_file_meta_source(mock_path) is None

    def test(self, mocker):
        mock_loaded = mocker.patch("ht.inline.api.hou.hda.loadedFiles")
        mock_get = mocker.patch("ht.inline.api._cpp_methods.getMetaSourceForPath")

        mock_path = mocker.MagicMock(spec=str)

        mock_loaded.return_value = (mock_path,)

        result = api.asset_file_meta_source(mock_path)
        assert result == mock_get.return_value

        mock_get.assert_called_with(mock_path)


def test_get_definition_meta_source(mocker):
    """Test ht.inline.api.get_definition_meta_source."""
    mock_source = mocker.patch("ht.inline.api.asset_file_meta_source")

    mock_definition = mocker.MagicMock(spec=hou.HDADefinition)

    result = api.get_definition_meta_source(mock_definition)
    assert result == mock_source.return_value

    mock_source.assert_called_with(mock_definition.libraryFilePath.return_value)


def test_remove_meta_source(mocker):
    """Test ht.inline.api.remove_meta_source."""
    mock_remove = mocker.patch("ht.inline.api._cpp_methods.removeMetaSource")

    mock_source_name = mocker.MagicMock(spec=str)

    result = api.remove_meta_source(mock_source_name)
    assert result == mock_remove.return_value

    mock_remove.assert_called_with(mock_source_name)


def test_libraries_in_meta_source(mocker):
    """Test ht.inline.api.libraries_in_meta_source."""
    mock_get = mocker.patch("ht.inline.api._cpp_methods.getLibrariesInMetaSource")
    mock_clean = mocker.patch("ht.inline.utils.clean_string_values")

    mock_source_name = mocker.MagicMock(spec=str)

    result = api.libraries_in_meta_source(mock_source_name)
    assert result == mock_clean.return_value

    mock_clean.assert_called_with(mock_get.return_value)


def test_is_dummy_definition(mocker):
    """Test ht.inline.api.is_dummy_definition."""
    mock_is_dummy = mocker.patch("ht.inline.api._cpp_methods.isDummyDefinition")

    mock_definition = mocker.MagicMock(spec=hou.HDADefinition)

    result = api.is_dummy_definition(mock_definition)
    assert result == mock_is_dummy.return_value

    mock_is_dummy.assert_called_with(
        mock_definition.libraryFilePath.return_value,
        mock_definition.nodeTypeCategory.return_value.name.return_value,
        mock_definition.nodeTypeName.return_value,
    )
