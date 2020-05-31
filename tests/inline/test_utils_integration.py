"""Test ht.inline.utils module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
from builtins import range
from builtins import object
import ctypes
import os

# Third Party Imports
import pytest

# Houdini Toolbox Imports
from ht.inline import utils

# Houdini Imports
import hou


# =============================================================================
# GLOBALS
# =============================================================================

OBJ = hou.node("/obj")


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(scope="module")
def load_test_file():
    """Load the test hip file."""
    hou.hipFile.load(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data",
            "test_utils_integration.hipnc",
        ),
        ignore_load_warnings=True,
    )

    yield

    hou.hipFile.clear()


# Need to ensure the hip file gets loaded.
pytestmark = pytest.mark.usefixtures("load_test_file")


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
    values = list(range(5))
    values.reverse()

    result = utils.build_c_int_array(values)

    assert list(result) == values

    expected_type = type((ctypes.c_int * len(values))())
    assert isinstance(result, expected_type)


def test_build_c_string_array():
    """Test ht.inline.utils.build_c_string_array."""

    values = ["foo", "bar", "test"]

    result = utils.build_c_string_array(values)

    assert list(result) == [b"foo", b"bar", b"test"]

    expected_type = type((ctypes.c_char_p * len(values))())
    assert isinstance(result, expected_type)


@pytest.mark.parametrize("values, expected", [
        ([], ()),
        (["foo", "", "bar"], ("foo", "bar")),
        (("foo", "", "bar"), ("foo", "bar"))
])
def test_clean_string_values(values, expected):
    """Test ht.inline.utils.clean_string_values."""
    result = utils.clean_string_values(values)

    assert result == expected


@pytest.mark.parametrize("attrib_type, name", [
    (hou.attribType.Vertex, "vertex_attrib"),
    (hou.attribType.Point, "point_attrib"),
    (hou.attribType.Prim, "prim_attrib"),
    (hou.attribType.Global, "global_attrib"),
    (None, "bad"),
])
def test_find_attrib(attrib_type, name):
    """Test ht.inline.utils.find_attrib."""
    geometry = OBJ.node("find_attrib").displayNode().geometry()

    if attrib_type is not None:
        result = utils.find_attrib(geometry, attrib_type, name)

        assert isinstance(result, hou.Attrib)
        assert result.name() == name
        assert result.type() == attrib_type

    else:
        with pytest.raises(ValueError):
            utils.find_attrib(geometry, attrib_type, name)


@pytest.mark.parametrize("group_type, name, expected_cls", [
    (0, "point_group", hou.PointGroup),
    (1, "prim_group", hou.PrimGroup),
    (2, "edge_group", hou.EdgeGroup),
    (3, "vertex_group", hou.VertexGroup),
    (4, "bad", None),
])
def test_find_group(group_type, name, expected_cls):
    """Test ht.inline.utils.find_group."""
    geometry = OBJ.node("find_group").displayNode().geometry()

    if group_type != 4:
        result = utils.find_group(geometry, group_type, name)

        assert isinstance(result, expected_cls)
        assert result.name() == name

    else:
        with pytest.raises(ValueError):
            utils.find_group(geometry, group_type, name)


@pytest.mark.parametrize("detail1, detail2, expected", [
    ("detail1", "detail2", True),
    ("detail1", "detail3", False),
    ("detail2", "detail3", False),
])
def test_details_match(detail1, detail2, expected):
    container = OBJ.node("geo_details_match")

    geo1 = container.node(detail1).geometry()
    geo2 = container.node(detail2).geometry()

    assert utils.geo_details_match(geo1, geo2) is expected


@pytest.mark.parametrize("value, expected", [
    (hou.attribType.Vertex, 0),
    (hou.attribType.Point, 1),
    (hou.attribType.Prim, 2),
    (hou.attribType.Global, 3),
    (None, None)
])
def test_get_attrib_owner(value, expected):
    """Test ht.inline.utils.get_attrib_owner."""
    if value is not None:
        result = utils.get_attrib_owner(value)

        assert result == expected

    else:
        with pytest.raises(ValueError):
            utils.get_attrib_owner(value)


class Test_get_attrib_owner_from_geometry_entity_type(object):
    """Test ht.inline.utils.get_attrib_owner_from_geometry_entity_type."""

    def test_in_map(self):
        geometry = OBJ.node("get_attrib_owner_from_geometry_entity_type/grid").geometry()

        result = utils.get_attrib_owner_from_geometry_entity_type(type(geometry))

        assert result == 3

    def test_subclass_in_map(self):
        geometry = OBJ.node("get_attrib_owner_from_geometry_entity_type/grid").geometry()

        prim = geometry.prims()[0]

        result = utils.get_attrib_owner_from_geometry_entity_type(type(prim))

        assert result == 2

    def test_invalid_type(self):
        with pytest.raises(ValueError):
            utils.get_attrib_owner_from_geometry_entity_type(hou.Vector2)


@pytest.mark.parametrize("geometry_type, expected", [
    (hou.geometryType.Vertices, 0),
    (hou.geometryType.Points, 1),
    (hou.geometryType.Primitives, 2),
    (None, None)
])
def test_get_attrib_owner_from_geometry_type(geometry_type, expected):
    """Test ht.inline.utils.get_attrib_owner_from_geometry_type."""
    if geometry_type is not None:
        result = utils.get_attrib_owner_from_geometry_type(geometry_type)

        assert result == expected

    else:
        with pytest.raises(ValueError):
            utils.get_attrib_owner_from_geometry_type(geometry_type)


@pytest.mark.parametrize("data_type, expected", [
    (hou.attribData.Int, 0),
    (hou.attribData.Float, 1),
    (hou.attribData.String, 2),
    (None, None)
])
def test_get_attrib_storage(data_type, expected):
    """Test ht.inline.utils.get_attrib_storage."""
    if data_type is not None:
        result = utils.get_attrib_storage(data_type)

        assert result == expected

    else:
        with pytest.raises(ValueError):
            utils.get_attrib_storage(data_type)


class Test_get_group_attrib_owner(object):
    """Test ht.inline.utils.get_group_attrib_owner."""

    def test_point_group(self):
        geometry = OBJ.node("get_group_attrib_owner").displayNode().geometry()

        group = geometry.findPointGroup("point_group")

        result = utils.get_group_attrib_owner(group)

        assert result == 1

    def test_prim_group(self):
        geometry = OBJ.node("get_group_attrib_owner").displayNode().geometry()

        group = geometry.findPrimGroup("prim_group")

        result = utils.get_group_attrib_owner(group)

        assert result == 2

    def test_invalid(self):
        with pytest.raises(ValueError):
            utils.get_group_attrib_owner(None)


class Test_get_group_type(object):
    """Test ht.inline.utils.get_group_type."""

    def test_point_group(self):
        geometry = OBJ.node("get_group_type").displayNode().geometry()

        group = geometry.findPointGroup("point_group")

        result = utils.get_group_type(group)

        assert result == 0

    def test_prim_group(self):
        geometry = OBJ.node("get_group_type").displayNode().geometry()

        group = geometry.findPrimGroup("prim_group")

        result = utils.get_group_type(group)

        assert result == 1

    def test_edge_group(self):
        geometry = OBJ.node("get_group_type").displayNode().geometry()

        group = geometry.findEdgeGroup("edge_group")

        result = utils.get_group_type(group)

        assert result == 2

    def test_vertex_group(self):
        geometry = OBJ.node("get_group_type").displayNode().geometry()

        group = geometry.findVertexGroup("vertex_group")

        result = utils.get_group_type(group)

        assert result == 3

    def test_invalid(self):
        with pytest.raises(ValueError):
            utils.get_group_type(None)


def test_get_nodes_from_paths():
    """Test ht.inline.utils.get_nodes_from_paths."""
    paths = (
        "/obj/get_nodes_from_paths/null1",
        "",
        "/obj/get_nodes_from_paths/null3",
    )

    expected = (
        hou.node("/obj/get_nodes_from_paths/null1"),
        hou.node("/obj/get_nodes_from_paths/null3"),
    )

    result = utils.get_nodes_from_paths(paths)

    assert result == expected


class Test_get_points_from_list(object):
    """Test ht.inline.utils.get_points_from_list."""

    def test_empty(self):
        geometry = OBJ.node("get_points_from_list/no_points").geometry()

        result = utils.get_points_from_list(geometry, [])

        assert result == ()

    def test(self):
        geometry = OBJ.node("get_points_from_list/points").geometry()

        nums = [0, 1, 2, 4]
        result = utils.get_points_from_list(geometry, nums)

        expected = (
            geometry.points()[0],
            geometry.points()[1],
            geometry.points()[2],
        )

        assert result == expected


class Test_get_prims_from_list(object):
    """Test ht.inline.utils.get_prims_from_list."""

    def test_empty(self):
        geometry = OBJ.node("get_prims_from_list/no_prims").geometry()

        result = utils.get_prims_from_list(geometry, [])

        assert result == ()

    def test(self):
        geometry = OBJ.node("get_prims_from_list/prims").geometry()

        nums = [0, 1, 2, 4]
        result = utils.get_prims_from_list(geometry, nums)

        expected = (
            geometry.prims()[0],
            geometry.prims()[1],
            geometry.prims()[2],
        )

        assert result == expected
