"""Test houdini_toolbox.inline.utils module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import ctypes

# Third Party
import pytest

# Houdini Toolbox
from houdini_toolbox.inline import utils

# Houdini
import hou


# Need to ensure the hip file gets loaded.
pytestmark = pytest.mark.usefixtures("load_module_test_file")


# =============================================================================
# GLOBALS
# =============================================================================

OBJ = hou.node("/obj")


# =============================================================================
# TESTS
# =============================================================================


def test_build_c_double_array():
    """Test houdini_toolbox.inline.utils.build_c_double_array."""
    values = [float(val) for val in range(5)]
    values.reverse()

    result = utils.build_c_double_array(values)

    assert list(result) == values

    expected_type = type((ctypes.c_double * len(values))())
    assert isinstance(result, expected_type)


def test_build_c_int_array():
    """Test houdini_toolbox.inline.utils.build_c_int_array."""
    values = list(range(5))
    values.reverse()

    result = utils.build_c_int_array(values)

    assert list(result) == values

    expected_type = type((ctypes.c_int * len(values))())
    assert isinstance(result, expected_type)


def test_build_c_string_array():
    """Test houdini_toolbox.inline.utils.build_c_string_array."""

    values = ["foo", "bar", "test"]

    result = utils.build_c_string_array(values)

    assert list(result) == [b"foo", b"bar", b"test"]

    expected_type = type((ctypes.c_char_p * len(values))())
    assert isinstance(result, expected_type)


@pytest.mark.parametrize(
    "values, expected",
    [
        ([], ()),
        (["foo", "", "bar"], ("foo", "bar")),
        (("foo", "", "bar"), ("foo", "bar")),
    ],
)
def test_clean_string_values(values, expected):
    """Test houdini_toolbox.inline.utils.clean_string_values."""
    result = utils.clean_string_values(values)

    assert result == expected


@pytest.mark.parametrize(
    "attrib_type, name",
    [
        (hou.attribType.Vertex, "vertex_attrib"),
        (hou.attribType.Point, "point_attrib"),
        (hou.attribType.Prim, "prim_attrib"),
        (hou.attribType.Global, "global_attrib"),
        (None, "bad"),
    ],
)
def test_find_attrib(attrib_type, name):
    """Test houdini_toolbox.inline.utils.find_attrib."""
    geometry = OBJ.node("test_find_attrib").displayNode().geometry()

    if attrib_type is not None:
        result = utils.find_attrib(geometry, attrib_type, name)

        assert isinstance(result, hou.Attrib)
        assert result.name() == name
        assert result.type() == attrib_type

    else:
        with pytest.raises(ValueError):
            utils.find_attrib(geometry, attrib_type, name)


@pytest.mark.parametrize(
    "group_type, name, expected_cls",
    [
        (0, "point_group", hou.PointGroup),
        (1, "prim_group", hou.PrimGroup),
        (2, "edge_group", hou.EdgeGroup),
        (3, "vertex_group", hou.VertexGroup),
        (4, "bad", object),
    ],
)
def test_find_group(group_type, name, expected_cls):
    """Test houdini_toolbox.inline.utils.find_group."""
    geometry = OBJ.node("test_find_group").displayNode().geometry()

    if group_type != 4:
        result = utils.find_group(geometry, group_type, name)

        assert isinstance(result, expected_cls)
        assert result.name() == name

    else:
        with pytest.raises(ValueError):
            utils.find_group(geometry, group_type, name)


@pytest.mark.parametrize(
    "detail1, detail2, expected",
    [
        ("detail1", "detail2", True),
        ("detail1", "detail3", False),
        ("detail2", "detail3", False),
    ],
)
def test_details_match(detail1, detail2, expected):
    """Test houdini_toolbox.inline.utils.geo_details_match."""
    container = OBJ.node("test_geo_details_match")

    geo1 = container.node(detail1).geometry()
    geo2 = container.node(detail2).geometry()

    assert utils.geo_details_match(geo1, geo2) is expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (hou.attribType.Vertex, 0),
        (hou.attribType.Point, 1),
        (hou.attribType.Prim, 2),
        (hou.attribType.Global, 3),
        (None, None),
    ],
)
def test_get_attrib_owner(value, expected):
    """Test houdini_toolbox.inline.utils.get_attrib_owner."""
    if value is not None:
        result = utils.get_attrib_owner(value)

        assert result == expected

    else:
        with pytest.raises(ValueError):
            utils.get_attrib_owner(value)


class Test_get_attrib_owner_from_geometry_entity_type:
    """Test houdini_toolbox.inline.utils.get_attrib_owner_from_geometry_entity_type."""

    def test_in_map(self):
        """Test when the entity type is explicitly in the map."""
        geometry = OBJ.node(
            "test_get_attrib_owner_from_geometry_entity_type/grid"
        ).geometry()

        result = utils.get_attrib_owner_from_geometry_entity_type(type(geometry))

        assert result == 3

    def test_subclass_in_map(self):
        """Test when the entity type is a subclass of something in the map."""
        geometry = OBJ.node(
            "test_get_attrib_owner_from_geometry_entity_type/grid"
        ).geometry()

        prim = geometry.prims()[0]

        result = utils.get_attrib_owner_from_geometry_entity_type(type(prim))

        assert result == 2

    def test_invalid_type(self):
        """Test when the value is not in the map or a subclass of something in the map."""
        with pytest.raises(ValueError):
            utils.get_attrib_owner_from_geometry_entity_type(hou.Vector2)


@pytest.mark.parametrize(
    "geometry_type, expected",
    [
        (hou.geometryType.Vertices, 0),
        (hou.geometryType.Points, 1),
        (hou.geometryType.Primitives, 2),
        (None, None),
    ],
)
def test_get_attrib_owner_from_geometry_type(geometry_type, expected):
    """Test houdini_toolbox.inline.utils.get_attrib_owner_from_geometry_type."""
    if geometry_type is not None:
        result = utils.get_attrib_owner_from_geometry_type(geometry_type)

        assert result == expected

    else:
        with pytest.raises(ValueError):
            utils.get_attrib_owner_from_geometry_type(geometry_type)


@pytest.mark.parametrize(
    "data_type, expected",
    [
        (hou.attribData.Int, 0),
        (hou.attribData.Float, 1),
        (hou.attribData.String, 2),
        (None, None),
    ],
)
def test_get_attrib_storage(data_type, expected):
    """Test houdini_toolbox.inline.utils.get_attrib_storage."""
    if data_type is not None:
        result = utils.get_attrib_storage(data_type)

        assert result == expected

    else:
        with pytest.raises(ValueError):
            utils.get_attrib_storage(data_type)


class Test_get_entity_data:
    """Test houdini_toolbox.inline.utils.get_entity_data."""

    def test_vertex(self):
        """Test getting data for a hou.Vertex object."""
        geometry = OBJ.node("test_get_entity_data").displayNode().geometry()
        prim = geometry.iterPrims()[3]
        vertex = prim.vertices()[3]

        result = utils.get_entity_data(vertex)

        assert result[0] == hou.Vertex
        assert utils.geo_details_match(result[1], geometry)
        assert result[2] == 15

    def test_point(self):
        """Test getting data for a hou.Point object."""
        geometry = OBJ.node("test_get_entity_data").displayNode().geometry()
        point = geometry.points()[2]

        result = utils.get_entity_data(point)

        assert result[0] == hou.Point
        assert utils.geo_details_match(result[1], geometry)
        assert result[2] == 2

    def test_geometry(self):
        """Test getting data for a hou.Geometry object."""
        geometry = OBJ.node("test_get_entity_data").displayNode().geometry()

        result = utils.get_entity_data(geometry)

        assert result == (hou.Geometry, geometry, 0)


class Test_get_entity_data_from_list:
    """Test houdini_toolbox.inline.utils.get_entity_data_from_list."""

    def test_vertex(self):
        """Test getting data for a list of hou.Vertex objects."""
        geometry = OBJ.node("test_get_entity_data_from_list").displayNode().geometry()
        prim = geometry.iterPrims()[2]
        vertex1 = prim.vertices()[1]
        vertex2 = prim.vertices()[2]

        result = utils.get_entity_data_from_list([vertex1, vertex2])

        assert result[0] == hou.Vertex
        assert utils.geo_details_match(result[1], geometry)
        assert result[2] == [9, 10]

    def test_point(self):
        """Test getting data for a list of hou.Point objects."""
        geometry = OBJ.node("test_get_entity_data_from_list").displayNode().geometry()

        point1 = geometry.points()[2]
        point2 = geometry.points()[12]

        result = utils.get_entity_data_from_list([point1, point2])

        assert result[0] == hou.Point
        assert utils.geo_details_match(result[1], geometry)
        assert result[2] == [2, 12]

    def test_geometry(self):
        """Test getting data for a single item list of hou.Geometry objects."""

        geometry = OBJ.node("test_get_entity_data_from_list").displayNode().geometry()

        result = utils.get_entity_data_from_list([geometry])

        assert result == (hou.Geometry, geometry, [0])


class Test_get_group_attrib_owner:
    """Test houdini_toolbox.inline.utils.get_group_attrib_owner."""

    def test_point_group(self):
        """Test getting the group owner of a point group."""
        geometry = OBJ.node("test_get_group_attrib_owner").displayNode().geometry()

        group = geometry.findPointGroup("point_group")

        result = utils.get_group_attrib_owner(group)

        assert result == 1

    def test_prim_group(self):
        """Test getting the group owner of a prim group."""
        geometry = OBJ.node("test_get_group_attrib_owner").displayNode().geometry()

        group = geometry.findPrimGroup("prim_group")

        result = utils.get_group_attrib_owner(group)

        assert result == 2

    def test_invalid(self):
        """Test getting the group owner of an invalid type object."""
        with pytest.raises(ValueError):
            utils.get_group_attrib_owner(None)


class Test_get_group_type:
    """Test houdini_toolbox.inline.utils.get_group_type."""

    def test_point_group(self):
        """Test getting the group type of a point group."""
        geometry = OBJ.node("test_get_group_type").displayNode().geometry()

        group = geometry.findPointGroup("point_group")

        result = utils.get_group_type(group)

        assert result == 0

    def test_prim_group(self):
        """Test getting the group type of a prim group."""
        geometry = OBJ.node("test_get_group_type").displayNode().geometry()

        group = geometry.findPrimGroup("prim_group")

        result = utils.get_group_type(group)

        assert result == 1

    def test_edge_group(self):
        """Test getting the group type of an edge group."""
        geometry = OBJ.node("test_get_group_type").displayNode().geometry()

        group = geometry.findEdgeGroup("edge_group")

        result = utils.get_group_type(group)

        assert result == 2

    def test_vertex_group(self):
        """Test getting the group type of a vertex group."""
        geometry = OBJ.node("test_get_group_type").displayNode().geometry()

        group = geometry.findVertexGroup("vertex_group")

        result = utils.get_group_type(group)

        assert result == 3

    def test_invalid(self):
        """Test getting the group type of an invalid type object."""
        with pytest.raises(ValueError):
            utils.get_group_type(None)


@pytest.mark.parametrize(
    "name, expected",
    [
        ("vecparm#", ("base",)),
        ("leaf#_#", ("inner#", "base")),
        ("bottom#_#_#", ("deepest#_#", "inner#", "base")),
    ],
)
def test_get_multiparm_containing_folders(name, expected):
    """Test houdini_toolbox.inline.utils.get_multiparm_containing_folders."""
    node = OBJ.node("test_get_multiparm_containing_folders/null")

    ptg = node.parmTemplateGroup()

    expected_folders = tuple(ptg.find(folder_name) for folder_name in expected)

    assert utils.get_multiparm_containing_folders(name, ptg) == expected_folders


@pytest.mark.parametrize(
    "name, expected",
    [
        ("vecparm#", (0,)),
        ("leaf#_#", (0, 1)),
        ("bottom#_#_#", (0, 1, 2)),
    ],
)
def test_get_multiparm_container_offsets(name, expected):
    """Test houdini_toolbox.inline.utils.get_multiparm_container_offsets."""
    node = OBJ.node("test_get_multiparm_container_offsets/null")

    ptg = node.parmTemplateGroup()

    assert utils.get_multiparm_container_offsets(name, ptg) == expected


@pytest.mark.parametrize(
    "name, expected",
    [
        ("normal", None),
        ("multi0", 0),  # Parameter with default of 0, stored in tag.
        ("multi1", 1),  # Parameter with default of 1, template contains no tags.
        ("multi2", 2),  # Parameter with default of 2, stored in tag.
    ],
)
def test_get_multiparm_start_offset(name, expected):
    """Test houdini_toolbox.inline.utils.get_multiparm_start_offset."""
    node = OBJ.node("test_get_multiparm_start_offset/null")

    parm_template = node.parm(name).parmTemplate()

    if expected is None:
        with pytest.raises(ValueError):
            utils.get_multiparm_start_offset(parm_template)

    else:
        assert utils.get_multiparm_start_offset(parm_template) == expected


def test_get_nodes_from_paths():
    """Test houdini_toolbox.inline.utils.get_nodes_from_paths."""
    paths = (
        "/obj/test_get_nodes_from_paths/null1",
        "",
        "/obj/test_get_nodes_from_paths/null3",
    )

    expected = (
        hou.node("/obj/test_get_nodes_from_paths/null1"),
        hou.node("/obj/test_get_nodes_from_paths/null3"),
    )

    result = utils.get_nodes_from_paths(paths)

    assert result == expected


class Test_get_points_from_list:
    """Test houdini_toolbox.inline.utils.get_points_from_list."""

    def test_empty(self):
        """Test passing an empty list of point numbers to get."""
        geometry = OBJ.node("test_get_points_from_list/points").geometry()

        result = utils.get_points_from_list(geometry, [])

        assert result == ()

    def test_valid_list(self):
        """Test passing an list of point numbers to get."""
        geometry = OBJ.node("test_get_points_from_list/points").geometry()

        nums = [0, 1, 2, 4]
        result = utils.get_points_from_list(geometry, nums)

        expected = (geometry.points()[0], geometry.points()[1], geometry.points()[2])

        assert result == expected


class Test_get_prims_from_list:
    """Test houdini_toolbox.inline.utils.get_prims_from_list."""

    def test_empty_list(self):
        """Test passing an empty list of prim numbers to get."""
        geometry = OBJ.node("test_get_prims_from_list/prims").geometry()

        result = utils.get_prims_from_list(geometry, [])

        assert result == ()

    def test_valid_list(self):
        """Test passing an list of prim numbers to get."""
        geometry = OBJ.node("test_get_prims_from_list/prims").geometry()

        nums = [0, 1, 2, 4]
        result = utils.get_prims_from_list(geometry, nums)

        expected = (geometry.prims()[0], geometry.prims()[1], geometry.prims()[2])

        assert result == expected


@pytest.mark.parametrize(
    "name, expected",
    [
        ("tabs", False),
        ("simple", False),
        ("multilist", True),
        ("multiscroll", True),
        ("multitab", True),
    ],
)
def test_is_parm_template_multiparm_folder(name, expected):
    """Test houdini_toolbox.inline.utils.is_parm_template_multiparm_folder."""
    node = OBJ.node("test_is_parm_template_multiparm_folder/null")

    parm_template = node.parm(name).parmTemplate()

    assert utils.is_parm_template_multiparm_folder(parm_template) == expected


@pytest.mark.parametrize("value, expected", [(b"foo", "foo"), ("bar", "bar")])
def test_string_decode(value, expected):
    """Test houdini_toolbox.inline.utils.string_decode."""
    result = utils.string_decode(value)

    assert result == expected


@pytest.mark.parametrize(
    "value, expected", [(4, b"4"), ("4", b"4"), ("bar", b"bar"), ("bar", b"bar")]
)
def test_string_encode(value, expected):
    """Test houdini_toolbox.inline.utils.string_decode."""
    result = utils.string_encode(value)

    assert result == expected


@pytest.mark.parametrize(
    "name, indices, success",
    [
        ("foo#_#", (1,), False),  # Test with not enough indices.
        ("foo#_#", (1, 2), True),
        ("foo#_#", (1, 2, 3), True),  # Test with more than enough indices.
    ],
)
def test_validate_multiparm_resolve_values(name, indices, success):
    """Test houdini_toolbox.inline.utils.validate_multiparm_resolve_values."""

    # Test failure scenario (not enough indices)
    if not success:
        with pytest.raises(ValueError):
            utils.validate_multiparm_resolve_values(name, indices)

    else:
        utils.validate_multiparm_resolve_values(name, indices)
