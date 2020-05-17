"""Integration tests for ht.inline.api."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
from builtins import str
from builtins import range
import os
import sys

# Third Party Imports
import pytest

if sys.version_info.major == 3:
    pytest.skip("Skipping", allow_module_level=True)

# Houdini Toolbox Imports
import ht.inline.api

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
            "test_api_integration.hipnc",
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


def test_get_variable_value():
    """Test ht.inline.api.get_variable_value."""
    hip_name = ht.inline.api.get_variable_value("HIPNAME")

    assert hip_name == os.path.splitext(os.path.basename(hou.hipFile.path()))[0]


def test_set_variable():
    """Test ht.inline.api.set_variable."""
    value = 22
    ht.inline.api.set_variable("awesome", value)

    assert ht.inline.api.get_variable_value("awesome") == 22


def test_get_variable_names():
    """Test ht.inline.api.get_variable_value."""
    variable_names = ht.inline.api.get_variable_names()

    assert "ACTIVETAKE" in variable_names

    # Dirty
    dirty_variable_names = ht.inline.api.get_variable_names(dirty=True)

    assert variable_names != dirty_variable_names


def test_unset_variable():
    """Test ht.inline.api.unset_variable."""
    ht.inline.api.set_variable("tester", 10)
    ht.inline.api.unset_variable("tester")

    assert ht.inline.api.get_variable_value("tester") is None


def test_emit_var_change():
    """Test ht.inline.api.emit_var_change."""
    parm = hou.parm("/obj/test_emit_var_change/file1/file")

    string = "something_$VARCHANGE.bgeo"

    parm.set(string)

    path = parm.eval()

    assert path == string.replace("$VARCHANGE", "")

    ht.inline.api.set_variable("VARCHANGE", 22)

    ht.inline.api.emit_var_change()

    new_path = parm.eval()

    # Test the paths aren't the same.
    assert path != new_path

    # Test the update was successful.
    assert new_path == string.replace("$VARCHANGE", "22")


def test_expand_range():
    """Test ht.inline.api.expand_range."""
    values = ht.inline.api.expand_range("0-5 10-20:2 64 65-66")
    target = (0, 1, 2, 3, 4, 5, 10, 12, 14, 16, 18, 20, 64, 65, 66)

    assert values == target


def test_is_geometry_read_only():
    """Test ht.inline.api.is_geometry_read_only."""
    geo = get_obj_geo("test_read_only")

    assert ht.inline.api.is_geometry_read_only(geo)

    # Not read only
    geo = hou.Geometry()
    assert not ht.inline.api.is_geometry_read_only(geo)


def test_num_points():
    """Test ht.inline.api.num_points."""
    geo = get_obj_geo("test_num_points")

    assert ht.inline.api.num_points(geo) == 5000


def test_num_prims():
    """Test ht.inline.api.num_prims."""
    geo = get_obj_geo("test_num_prims")

    assert ht.inline.api.num_prims(geo) == 12


def test_pack_geometry():
    """Test ht.inline.api.pack_geometry."""
    geo = get_obj_geo("test_pack_geometry")

    prim = geo.prims()[0]

    assert isinstance(prim, hou.PackedGeometry)


def test_sort_geometry_by_attribute():
    """Test ht.inline.api.sort_geometry_by_attribute."""
    geo = get_obj_geo_copy("test_sort_geometry_by_attribute")

    attrib = geo.findPrimAttrib("id")

    ht.inline.api.sort_geometry_by_attribute(geo, attrib)

    values = [int(val) for val in geo.primFloatAttribValues("id")]

    assert values, list(range(10))

    # Reversed
    geo = get_obj_geo_copy("test_sort_geometry_by_attribute")

    attrib = geo.findPrimAttrib("id")

    ht.inline.api.sort_geometry_by_attribute(geo, attrib, reverse=True)

    values = [int(val) for val in geo.primFloatAttribValues("id")]

    assert values == list(reversed(list(range(10))))

    # Invalid index
    geo = get_obj_geo_copy("test_sort_geometry_by_attribute")

    attrib = geo.findPrimAttrib("id")

    with pytest.raises(IndexError):
        ht.inline.api.sort_geometry_by_attribute(geo, attrib, 1)

    # Detail
    geo = get_obj_geo_copy("test_sort_geometry_by_attribute")

    attrib = geo.findGlobalAttrib("varmap")

    with pytest.raises(ValueError):
        ht.inline.api.sort_geometry_by_attribute(geo, attrib)


def test_sort_geometry_along_axis():
    """Test ht.inline.api.sort_geometry_along_axis."""
    # Points
    geo = get_obj_geo_copy("test_sort_geometry_along_axis_points")

    ht.inline.api.sort_geometry_along_axis(geo, hou.geometryType.Points, 0)

    values = [int(val) for val in geo.pointFloatAttribValues("id")]

    assert values == list(range(10))

    # Prims
    geo = get_obj_geo_copy("test_sort_geometry_along_axis_prims")

    ht.inline.api.sort_geometry_along_axis(geo, hou.geometryType.Primitives, 2)

    values = [int(val) for val in geo.primFloatAttribValues("id")]

    assert values == list(range(10))


def test_sort_geometry_by_values():
    """Test ht.inline.api.sort_geometry_by_values."""
    pass


def test_sort_geometry_randomly():
    """Test ht.inline.api.sort_geometry_randomly."""
    # Points
    seed = 11
    target = [5, 9, 3, 8, 0, 2, 6, 1, 4, 7]

    geo = get_obj_geo_copy("test_sort_geometry_randomly_points")
    ht.inline.api.sort_geometry_randomly(geo, hou.geometryType.Points, seed)

    values = [int(val) for val in geo.pointFloatAttribValues("id")]

    assert values == target

    # Prims
    seed = 345
    target = [4, 0, 9, 2, 1, 8, 3, 6, 7, 5]

    geo = get_obj_geo_copy("test_sort_geometry_randomly_prims")
    ht.inline.api.sort_geometry_randomly(geo, hou.geometryType.Primitives, seed)

    values = [int(val) for val in geo.primFloatAttribValues("id")]

    assert values == target


def test_shift_geometry_elements():
    """Test ht.inline.api.shift_geometry_elements."""
    # Points
    offset = -18
    target = [8, 9, 0, 1, 2, 3, 4, 5, 6, 7]

    geo = get_obj_geo_copy("test_shift_geometry_elements_points")
    ht.inline.api.shift_geometry_elements(geo, hou.geometryType.Points, offset)

    values = [int(val) for val in geo.pointFloatAttribValues("id")]

    assert values == target

    # Prims
    offset = 6
    target = [4, 5, 6, 7, 8, 9, 0, 1, 2, 3]

    geo = get_obj_geo_copy("test_shift_geometry_elements_prims")
    ht.inline.api.shift_geometry_elements(geo, hou.geometryType.Primitives, offset)

    values = [int(val) for val in geo.primFloatAttribValues("id")]

    assert values == target


def test_reverse_sort_geometry():
    """Test ht.inline.api.reverse_sort_geometry."""
    # Points
    target = list(range(10))
    target.reverse()

    geo = get_obj_geo_copy("test_reverse_sort_geometry_points")
    ht.inline.api.reverse_sort_geometry(geo, hou.geometryType.Points)

    values = [int(val) for val in geo.pointFloatAttribValues("id")]

    assert values == target

    # Prims
    target = list(range(10))
    target.reverse()

    geo = get_obj_geo_copy("test_reverse_sort_geometry_prims")
    ht.inline.api.reverse_sort_geometry(geo, hou.geometryType.Primitives)

    values = [int(val) for val in geo.primFloatAttribValues("id")]

    assert values == target


def test_sort_geometry_by_proximity_to_position():
    """Test ht.inline.api.sort_geometry_by_proximity_to_position."""
    # Points
    target = [4, 3, 5, 2, 6, 1, 7, 0, 8, 9]
    position = hou.Vector3(4, 1, 2)

    geo = get_obj_geo_copy("test_sort_geometry_by_proximity_to_position_points")
    ht.inline.api.sort_geometry_by_proximity_to_position(
        geo, hou.geometryType.Points, position
    )

    values = [int(val) for val in geo.pointFloatAttribValues("id")]

    assert values == target

    # Prims
    target = [6, 7, 5, 8, 4, 9, 3, 2, 1, 0]
    position = hou.Vector3(3, -1, 2)

    geo = get_obj_geo_copy("test_sort_geometry_by_proximity_to_position_prims")
    ht.inline.api.sort_geometry_by_proximity_to_position(
        geo, hou.geometryType.Primitives, position
    )

    values = [int(val) for val in geo.primFloatAttribValues("id")]

    assert values == target


def test_sort_geometry_by_vertex_order():
    """Test ht.inline.api.sort_geometry_by_vertex_order."""
    target = list(range(10))

    geo = get_obj_geo_copy("test_sort_geometry_by_vertex_order")
    ht.inline.api.sort_geometry_by_vertex_order(geo)

    values = [int(val) for val in geo.pointFloatAttribValues("id")]

    assert values == target


def test_sort_geometry_by_expression():
    """Test ht.inline.api.sort_geometry_by_expression."""
    # Points
    target_geo = OBJ.node("test_sort_geometry_by_expression_points/RESULT").geometry()
    test_geo = OBJ.node("test_sort_geometry_by_expression_points/TEST").geometry()

    assert test_geo.pointFloatAttribValues("id") == target_geo.pointFloatAttribValues(
        "id"
    )

    # Prims
    target_geo = OBJ.node("test_sort_geometry_by_expression_prims/RESULT").geometry()
    test_geo = OBJ.node("test_sort_geometry_by_expression_prims/TEST").geometry()

    assert test_geo.primFloatAttribValues("id") == target_geo.primFloatAttribValues(
        "id"
    )


def test_create_point_at_position():
    """Test ht.inline.api.create_point_at_position."""
    geo = hou.Geometry()

    # Read only
    frozen_geo = geo.freeze(True)

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.create_point_at_position(frozen_geo, hou.Vector3(1, 2, 3))

    # Success
    geo = hou.Geometry()

    point = ht.inline.api.create_point_at_position(geo, hou.Vector3(1, 2, 3))

    assert point.position() == hou.Vector3(1, 2, 3)


def test_create_n_points():
    """Test ht.inline.api.create_n_points."""
    geo = hou.Geometry()

    # Read only
    frozen_geo = geo.freeze(True)

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.create_n_points(frozen_geo, 15)

    # Success
    points = ht.inline.api.create_n_points(geo, 15)

    assert points == geo.points()

    # Invalid Number
    with pytest.raises(ValueError):
        ht.inline.api.create_n_points(geo, -4)


def test_merge_point_group():
    """Test ht.inline.api.merge_point_group."""
    geo = hou.Geometry()

    source_geo = get_obj_geo("test_merge_point_group")

    group = source_geo.pointGroups()[0]

    # Read only
    frozen_geo = geo.freeze(True)

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.merge_point_group(frozen_geo, group)

    # Invalid group type
    prim_group = source_geo.primGroups()[0]

    with pytest.raises(ValueError):
        ht.inline.api.merge_point_group(geo, prim_group)

    # Success
    ht.inline.api.merge_point_group(geo, group)

    assert len(geo.iterPoints()) == len(group.points())


def test_merge_points():
    """Test ht.inline.api.merge_points."""
    geo = hou.Geometry()
    source_geo = get_obj_geo("test_merge_points")

    points = source_geo.globPoints("0 6 15 35-38 66")

    # Read only
    frozen_geo = geo.freeze(True)

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.merge_points(frozen_geo, points)

    # Success
    ht.inline.api.merge_points(geo, points)

    assert len(geo.iterPoints()) == len(points)


def test_merge_prim_group():
    """Test ht.inline.api.merge_prim_group."""
    geo = hou.Geometry()
    source_geo = get_obj_geo("test_merge_prim_group")

    group = source_geo.primGroups()[0]

    # Read only
    frozen_geo = geo.freeze(True)

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.merge_prim_group(frozen_geo, group)

    # Invalid group type
    point_group = source_geo.pointGroups()[0]

    with pytest.raises(ValueError):
        ht.inline.api.merge_prim_group(geo, point_group)

    # Success
    ht.inline.api.merge_prim_group(geo, group)

    assert len(geo.iterPrims()) == len(group.prims())


def test_merge_prims():
    """Test ht.inline.api.merge_prims."""
    geo = hou.Geometry()
    source_geo = get_obj_geo("test_merge_prims")

    prims = source_geo.globPrims("0 6 15 35-38 66")

    # Read only
    frozen_geo = geo.freeze(True)

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.merge_prims(frozen_geo, prims)

    # Success
    ht.inline.api.merge_prims(geo, prims)

    assert len(geo.iterPrims()) == len(prims)


def test_copy_attrib_values():
    """Test ht.inline.api.copy_attribute_values."""
    # Points
    source = get_obj_geo("test_copy_attribute_values")

    attribs = source.pointAttribs()

    geo = hou.Geometry()

    pt1 = geo.createPoint()
    pt2 = geo.createPoint()

    ht.inline.api.copy_attribute_values(source.iterPoints()[2], attribs, pt1)
    ht.inline.api.copy_attribute_values(source.iterPoints()[6], attribs, pt2)

    # Ensure all the attributes got copied right.
    assert len(geo.pointAttribs()) == len(attribs)

    # Ensure P got copied right.
    assert pt1.position().isAlmostEqual(hou.Vector3(1.66667, 0, -5))
    assert pt2.position().isAlmostEqual(hou.Vector3(1.66667, 0, -1.66667))

    # Prims
    source = get_obj_geo("test_copy_attribute_values")

    attribs = source.primAttribs()

    geo = hou.Geometry()

    pr1 = geo.createPolygon()
    pr2 = geo.createPolygon()

    ht.inline.api.copy_attribute_values(source.iterPrims()[1], attribs, pr1)
    ht.inline.api.copy_attribute_values(source.iterPrims()[4], attribs, pr2)

    # Ensure all the attributes got copied right.
    assert len(geo.primAttribs()) == len(attribs)

    # Ensure P got copied right.
    assert pr1.attribValue("prnum") == 1
    assert pr2.attribValue("prnum") == 4

    # Vertex to point
    source = get_obj_geo("test_copy_attribute_values")
    attribs = source.vertexAttribs()

    pt1 = geo.createPoint()

    pr1 = source.prims()[1]

    ht.inline.api.copy_attribute_values(pr1.vertex(2), attribs, pt1)
    assert pt1.attribValue("id") == 6
    assert pt1.attribValue("random_vtx") == 0.031702518463134766

    # Points to global
    source = get_obj_geo("test_copy_attribute_values")

    attribs = source.pointAttribs()
    geo = hou.Geometry()

    ht.inline.api.copy_attribute_values(source.iterPoints()[2], attribs, geo)

    # Ensure all the attributes got copied right.
    assert len(geo.globalAttribs()) == len(attribs)

    assert geo.attribValue("ptnum") == 2

    assert geo.attribValue("random") == 0.5108950138092041

    # Global to point
    source = get_obj_geo("test_copy_attribute_values")

    geo = hou.Geometry()
    attribs = source.globalAttribs()
    pt1 = geo.createPoint()

    ht.inline.api.copy_attribute_values(source, attribs, pt1)

    assert pt1.attribValue("barbles") == 33
    assert pt1.attribValue("foobles") == (1.0, 2.0)

    # Global to global
    source = get_obj_geo("test_copy_attribute_values")
    geo = hou.Geometry()
    attribs = source.globalAttribs()

    ht.inline.api.copy_attribute_values(source, attribs, geo)
    assert geo.attribValue("barbles") == 33
    assert geo.attribValue("foobles") == (1.0, 2.0)

    # Global to vertex

    source = get_obj_geo("test_copy_attribute_values")
    attribs = source.globalAttribs()

    geo = hou.Geometry()

    pt1 = geo.createPoint()
    pr1 = geo.createPolygon()
    pr1.addVertex(pt1)
    vtx1 = pr1.vertex(0)

    ht.inline.api.copy_attribute_values(source, attribs, vtx1)
    assert vtx1.attribValue("barbles") == 33
    assert vtx1.attribValue("foobles") == (1.0, 2)

    # Read only
    source = get_obj_geo("test_copy_attribute_values")
    geo = hou.Geometry().freeze(True)
    attribs = source.globalAttribs()

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.copy_attribute_values(source, attribs, geo)


def test_point_adjacent_polygons():
    """Test ht.inline.api.point_adjacent_polygons."""
    geo = get_obj_geo("test_point_adjacent_polygons")

    target = geo.globPrims("1 2")

    prims = ht.inline.api.point_adjacent_polygons(geo.iterPrims()[0])

    assert prims == target


def test_edge_adjacent_polygons():
    """Test ht.inline.api.edge_adjacent_polygons."""
    geo = get_obj_geo("test_edge_adjacent_polygons")

    target = geo.globPrims("2")

    prims = ht.inline.api.edge_adjacent_polygons(geo.iterPrims()[0])

    assert prims == target


def test_connected_points():
    """Test ht.inline.api.connected_points."""
    geo = get_obj_geo("test_connected_points")

    target = geo.globPoints("1 3 5 7")

    points = ht.inline.api.connected_points(geo.iterPoints()[4])

    assert points == target


def test_connected_prims():
    """Test ht.inline.api.connected_prims."""
    geo = get_obj_geo("test_connected_prims")

    target = geo.prims()

    prims = ht.inline.api.connected_prims(geo.iterPoints()[4])

    assert prims == target


def test_referencing_vertices():
    """Test ht.inline.api.referencing_vertices."""
    geo = get_obj_geo("test_referencing_vertices")

    target = geo.globVertices("0v2 1v3 2v1 3v0")

    vertices = ht.inline.api.referencing_vertices(geo.iterPoints()[4])

    assert vertices == target


def test_string_table_indices():
    """Test ht.inline.api.string_table_indices."""
    # Not a string
    geo = get_obj_geo("test_point_string_table_indices")
    attr = geo.findPointAttrib("not_string")

    with pytest.raises(ValueError):
        ht.inline.api.string_table_indices(attr)

    # Points
    target = (0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1)

    attr = geo.findPointAttrib("test")

    assert ht.inline.api.string_table_indices(attr) == target

    # Prims
    geo = get_obj_geo("test_prim_string_table_indices")

    target = (0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4)

    attr = geo.findPrimAttrib("test")

    assert ht.inline.api.string_table_indices(attr) == target


def test_vertex_string_attrib_values():
    """Test ht.inline.api.vertex_string_attrib_values."""
    geo = get_obj_geo("test_vertex_string_attrib_values")

    with pytest.raises(hou.OperationFailed):
        assert ht.inline.api.vertex_string_attrib_values(geo, "foo")

    with pytest.raises(ValueError):
        assert ht.inline.api.vertex_string_attrib_values(geo, "not_string")

    target = (
        "vertex0",
        "vertex1",
        "vertex2",
        "vertex3",
        "vertex4",
        "vertex5",
        "vertex6",
        "vertex7",
    )

    assert ht.inline.api.vertex_string_attrib_values(geo, "test") == target


def test_set_vertex_string_attrib_values():
    """Test ht.inline.api.set_vertex_string_attrib_values."""
    target = ("vertex0", "vertex1", "vertex2", "vertex3", "vertex4")

    # Read only
    geo = get_obj_geo("test_set_vertex_string_attrib_values")

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.set_vertex_string_attrib_values(geo, "test", target)

    geo = get_obj_geo_copy("test_set_vertex_string_attrib_values")
    attr = geo.findVertexAttrib("test")

    ht.inline.api.set_vertex_string_attrib_values(geo, "test", target)

    values = []

    for prim in geo.prims():
        values.extend([vertex.attribValue(attr) for vertex in prim.vertices()])

    assert tuple(values) == target

    # Invalid attribute
    with pytest.raises(hou.OperationFailed):
        ht.inline.api.set_vertex_string_attrib_values(geo, "thing", target)

    # Invalid attribute type
    with pytest.raises(ValueError):
        ht.inline.api.set_vertex_string_attrib_values(geo, "notstring", target)

    # Invalid attribute size
    target = ("vertex0", "vertex1", "vertex2", "vertex3")

    with pytest.raises(ValueError):
        ht.inline.api.set_vertex_string_attrib_values(geo, "test", target)


def test_set_shared_point_string_attrib():
    """Test ht.inline.api.set_shared_point_string_attrib."""
    target = ["point0"] * 5

    geo = hou.Geometry()

    frozen_geo = geo.freeze(True)

    # Read only
    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.set_shared_point_string_attrib(frozen_geo, "test", "point0")

    # No attribute
    with pytest.raises(ValueError):
        ht.inline.api.set_shared_point_string_attrib(geo, "foo", "point0")

    ht.inline.api.create_n_points(geo, 5)
    attr = geo.addAttrib(hou.attribType.Point, "test", "")
    geo.addAttrib(hou.attribType.Point, "not_string", 0)

    with pytest.raises(ValueError):
        ht.inline.api.set_shared_point_string_attrib(geo, "not_string", "point0")

    ht.inline.api.set_shared_point_string_attrib(geo, attr.name(), "point0")

    values = [point.attribValue(attr) for point in geo.points()]

    assert values == target

    # Group
    target = ["point0"] * 5 + [""] * 5

    geo = hou.Geometry()

    attr = geo.addAttrib(hou.attribType.Point, "test", "")

    ht.inline.api.create_n_points(geo, 5)
    group = geo.createPointGroup("group1")

    for point in geo.points():
        group.add(point)

    ht.inline.api.create_n_points(geo, 5)

    ht.inline.api.set_shared_point_string_attrib(geo, attr.name(), "point0", group)

    values = [point.attribValue(attr) for point in geo.points()]

    assert values == target


def test_set_shared_prim_string_attrib():
    """Test ht.inline.api.set_shared_prim_string_attrib."""
    target = ["value"] * 5
    geo = get_obj_geo_copy("test_set_shared_prim_string_attrib")

    frozen_geo = geo.freeze(True)

    # Read only
    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.set_shared_prim_string_attrib(frozen_geo, "test", "prim0")

    # No attribute
    with pytest.raises(ValueError):
        ht.inline.api.set_shared_prim_string_attrib(geo, "foo", "prim0")

    geo.addAttrib(hou.attribType.Prim, "not_string", 0)

    with pytest.raises(ValueError):
        ht.inline.api.set_shared_prim_string_attrib(geo, "not_string", "value")

    attr = geo.findPrimAttrib("test")

    ht.inline.api.set_shared_prim_string_attrib(geo, attr.name(), "value")

    values = [prim.attribValue(attr) for prim in geo.prims()]

    assert values == target

    # Group
    target = ["value"] * 3 + ["", ""]

    geo = get_obj_geo_copy("test_set_shared_prim_string_attrib")

    attr = geo.findPrimAttrib("test")

    group = geo.findPrimGroup("group1")

    ht.inline.api.set_shared_prim_string_attrib(geo, attr.name(), "value", group)

    values = [prim.attribValue(attr) for prim in geo.prims()]

    assert values == target


def test_face_has_edge():
    """Test ht.inline.api.face_has_edge."""
    geo = get_obj_geo("test_has_edge")

    face = geo.iterPrims()[0]

    pt0 = geo.iterPoints()[0]
    pt1 = geo.iterPoints()[1]

    assert ht.inline.api.face_has_edge(face, pt0, pt1)

    # False
    geo = get_obj_geo("test_has_edge")

    face = geo.iterPrims()[0]

    pt0 = geo.iterPoints()[0]
    pt2 = geo.iterPoints()[2]

    assert ht.inline.api.face_has_edge(face, pt0, pt2)


def test_shared_edges():
    """Test ht.inline.api.shared_edges."""
    geo = get_obj_geo("test_shared_edges")

    pr0, pr1 = geo.prims()

    edges = ht.inline.api.shared_edges(pr0, pr1)

    pt2 = geo.iterPoints()[2]
    pt3 = geo.iterPoints()[3]

    edge = geo.findEdge(pt2, pt3)

    assert edges == (edge,)


def test_insert_vertex():
    """Test ht.inline.api.insert_vertex."""
    # Read only
    geo = get_obj_geo("test_insert_vertex")

    face = geo.iterPrims()[0]

    pt0 = geo.points()[0]

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.insert_vertex(face, pt0, 2)

    # Success
    geo = get_obj_geo_copy("test_insert_vertex")

    face = geo.iterPrims()[0]

    new_point = ht.inline.api.create_point_at_position(geo, hou.Vector3(0.5, 0, 0.5))

    ht.inline.api.insert_vertex(face, new_point, 2)

    assert face.vertex(2).point() == new_point

    # Negative index.
    with pytest.raises(IndexError):
        ht.inline.api.insert_vertex(face, new_point, -1)

    # Invalid index.
    with pytest.raises(IndexError):
        ht.inline.api.insert_vertex(face, new_point, 10)


def test_delete_vertex():
    """Test ht.inline.api.delete_vertex_from_face."""
    # Read only
    geo = get_obj_geo("test_delete_vertex")

    face = geo.iterPrims()[0]

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.delete_vertex_from_face(face, 3)

    # Success
    geo = get_obj_geo_copy("test_delete_vertex")

    face = geo.iterPrims()[0]

    ht.inline.api.delete_vertex_from_face(face, 3)

    assert len(face.vertices()) == 3

    with pytest.raises(IndexError):
        ht.inline.api.delete_vertex_from_face(face, -1)

    with pytest.raises(IndexError):
        ht.inline.api.delete_vertex_from_face(face, 10)


def test_set_face_vertex_point():
    """Test ht.inline.api.set_face_vertex_point."""
    # Read only
    geo = get_obj_geo("test_set_point")

    face = geo.iterPrims()[0]
    pt4 = geo.iterPoints()[4]

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.set_face_vertex_point(face, 3, pt4)

    # Success
    geo = get_obj_geo_copy("test_set_point")

    face = geo.iterPrims()[0]
    pt4 = geo.iterPoints()[4]

    ht.inline.api.set_face_vertex_point(face, 3, pt4)

    assert face.vertex(3).point().number() == 4

    # Negative index.
    with pytest.raises(IndexError):
        ht.inline.api.set_face_vertex_point(face, -1, pt4)

    # Invalid index.
    with pytest.raises(IndexError):
        ht.inline.api.set_face_vertex_point(face, 10, pt4)


def test_primitive_bary_center():
    """Test ht.inline.api.primitive_bary_center."""
    target = hou.Vector3(1.5, 1, -1)
    geo = get_obj_geo_copy("test_bary_center")

    prim = geo.iterPrims()[0]

    assert ht.inline.api.primitive_bary_center(prim) == target


def test_primitive_area():
    """Test ht.inline.api.primitive_area."""
    target = 4.375
    geo = get_obj_geo_copy("test_primitive_area")

    prim = geo.iterPrims()[0]

    assert ht.inline.api.primitive_area(prim) == target


def test_primitive_perimeter():
    """Test ht.inline.api.primitive_perimeter."""
    target = 6.5
    geo = get_obj_geo_copy("test_perimeter")

    prim = geo.iterPrims()[0]

    assert ht.inline.api.primitive_perimeter(prim) == target


def test_primitive_volume():
    """Test ht.inline.api.primitive_volume."""
    target = 0.1666666716337204
    geo = get_obj_geo_copy("test_volume")

    prim = geo.iterPrims()[0]

    assert ht.inline.api.primitive_volume(prim) == target


def test_reverse_prim():
    """Test ht.inline.api.reverse_prim."""
    # Read only
    geo = get_obj_geo("test_reverse_prim")

    prim = geo.iterPrims()[0]

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.reverse_prim(prim)

    # Success
    target = hou.Vector3(0, -1, 0)
    geo = get_obj_geo_copy("test_reverse_prim")

    prim = geo.iterPrims()[0]
    ht.inline.api.reverse_prim(prim)

    assert prim.normal() == target


def test_make_primitive_points_unique():
    """Test ht.inline.api.make_primitive_points_unique."""
    # Read only
    geo = get_obj_geo("test_make_unique")

    prim = geo.iterPrims()[4]

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.make_primitive_points_unique(prim)

    # Success
    target = 28
    geo = get_obj_geo_copy("test_make_unique")

    prim = geo.iterPrims()[4]
    ht.inline.api.make_primitive_points_unique(prim)

    assert len(geo.iterPoints()) == target


def test_check_minimum_polygon_vertex_count():
    """Test ht.inline.api.check_minimum_polygon_vertex_count."""
    geo = get_obj_geo_copy("test_check_minimum_polygon_vertex_count")

    assert ht.inline.api.check_minimum_polygon_vertex_count(geo, 3)

    assert not ht.inline.api.check_minimum_polygon_vertex_count(
        geo, 3, ignore_open=False
    )

    assert not ht.inline.api.check_minimum_polygon_vertex_count(geo, 5)


def test_primitive_bounding_box():
    """Test ht.inline.api.primitive_bounding_box."""
    target = hou.BoundingBox(-0.75, 0, -0.875, 0.75, 1.5, 0.875)
    geo = get_obj_geo_copy("test_prim_bounding_box")

    prim = geo.iterPrims()[0]

    assert ht.inline.api.primitive_bounding_box(prim) == target


def test_compute_point_normals():
    """Test ht.inline.api.compute_point_normals."""
    # Read only
    geo = get_obj_geo("test_compute_point_normals")

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.compute_point_normals(geo)

    # Success
    geo = get_obj_geo_copy("test_compute_point_normals")

    ht.inline.api.compute_point_normals(geo)

    assert geo.findPointAttrib("N") is not None


def test_add_point_normal_attribute():
    """Test ht.inline.api.add_point_normal_attribute."""
    # Read only
    geo = get_obj_geo("test_add_point_normal_attribute")

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.add_point_normal_attribute(geo)

    # Success
    geo = get_obj_geo_copy("test_add_point_normal_attribute")

    assert ht.inline.api.add_point_normal_attribute(geo) is not None


def test_add_point_velocity_attribute():
    """Test ht.inline.api.add_point_velocity_attribute."""
    # Read only
    geo = get_obj_geo("test_add_point_velocity_attribute")

    with pytest.raises(hou.GeometryPermissionError):
        assert ht.inline.api.add_point_velocity_attribute(geo) is not None

    # Success
    geo = get_obj_geo_copy("test_add_point_velocity_attribute")

    assert ht.inline.api.add_point_velocity_attribute(geo) is not None


def test_add_color_attribute():
    """Test ht.inline.api.add_color_attribute."""
    # Read only
    geo = get_obj_geo("test_add_color_attribute")

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.add_color_attribute(geo, hou.attribType.Point)

    # Global error
    geo = get_obj_geo_copy("test_add_color_attribute")

    with pytest.raises(ValueError):
        ht.inline.api.add_color_attribute(geo, hou.attribType.Global)

    # Point
    geo = get_obj_geo_copy("test_add_color_attribute")

    result = ht.inline.api.add_color_attribute(geo, hou.attribType.Point)
    assert result is not None

    # Prim
    geo = get_obj_geo_copy("test_add_color_attribute")

    result = ht.inline.api.add_color_attribute(geo, hou.attribType.Prim)
    assert result is not None

    # Vertex
    geo = get_obj_geo_copy("test_add_color_attribute")

    result = ht.inline.api.add_color_attribute(geo, hou.attribType.Vertex)
    assert result is not None


def test_convex_polygons():
    """Test ht.inline.api.convex_polygons."""
    # Read only
    geo = get_obj_geo("test_convex")

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.convex_polygons(geo)

    # Success
    geo = get_obj_geo_copy("test_convex")

    ht.inline.api.convex_polygons(geo)

    assert len(geo.iterPrims()) == 162

    vertices = [vertex for prim in geo.prims() for vertex in prim.vertices()]
    assert len(vertices) == 486


def test_clip_geometry():
    """Test ht.inline.api.clip_geometry."""
    origin = hou.Vector3(0, 0, 0)
    direction = hou.Vector3(-0.5, 0.6, -0.6)

    # Read only
    geo = get_obj_geo("test_clip")

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.clip_geometry(geo, origin, direction, 0.5)

    # Clip above
    geo = get_obj_geo_copy("test_clip")

    ht.inline.api.clip_geometry(geo, origin, direction, 0.5)

    assert len(geo.iterPrims()) == 42
    assert len(geo.iterPoints()) == 60

    # Clip below
    geo = get_obj_geo_copy("test_clip_below")

    origin = hou.Vector3(0, -0.7, -0.9)

    direction = hou.Vector3(-0.6, 0.1, -0.8)

    ht.inline.api.clip_geometry(geo, origin, direction, 0.6, below=True)

    assert len(geo.iterPrims()) == 61
    assert len(geo.iterPoints()) == 81

    # Clip group
    geo = get_obj_geo_copy("test_clip_group")

    group = geo.primGroups()[0]

    origin = hou.Vector3(-1.3, -1.5, 1.2)
    direction = hou.Vector3(0.8, 0.02, 0.5)

    ht.inline.api.clip_geometry(geo, origin, direction, -0.3, group=group)

    assert len(geo.iterPrims()) == 74
    assert len(geo.iterPoints()) == 98


def test_destroy_empty_groups():
    """Test ht.inline.api.destroy_empty_groups."""
    geo = hou.Geometry()

    # Read only
    frozen_geo = geo.freeze(True)

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.destroy_empty_groups(frozen_geo, hou.attribType.Point)

    # Global attribute
    with pytest.raises(ValueError):
        ht.inline.api.destroy_empty_groups(geo, hou.attribType.Global)

    # Point group
    geo.createPointGroup("empty")

    ht.inline.api.destroy_empty_groups(geo, hou.attribType.Point)

    assert not geo.pointGroups()

    # Prim group
    geo.createPrimGroup("empty")

    ht.inline.api.destroy_empty_groups(geo, hou.attribType.Prim)

    assert not geo.primGroups()


def test_destroy_unused_points():
    """Test ht.inline.api.destroy_unused_points."""
    geo = get_obj_geo("test_destroy_unused_points")

    # Read only
    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.destroy_unused_points(geo)

    # Full geometry
    geo = get_obj_geo_copy("test_destroy_unused_points")
    ht.inline.api.destroy_unused_points(geo)
    assert len(geo.iterPoints()) == 20

    # Destroy unused points in a group.
    geo = get_obj_geo_copy("test_destroy_unused_points_group")
    group = geo.pointGroups()[0]
    ht.inline.api.destroy_unused_points(geo, group)
    assert len(geo.iterPoints()) == 3729


def test_consolidate_points():
    """Test ht.inline.api.consolidate_points."""
    # Read only
    geo = get_obj_geo("test_consolidate_points")

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.consolidate_points(geo)

    # Full geometry
    geo = get_obj_geo_copy("test_consolidate_points")

    ht.inline.api.consolidate_points(geo)

    assert len(geo.iterPoints()) == 100

    # By distance
    geo = get_obj_geo_copy("test_consolidate_points_dist")

    ht.inline.api.consolidate_points(geo, 3)

    assert len(geo.iterPoints()) == 16

    # By group
    geo = get_obj_geo_copy("test_consolidate_points_group")

    group = geo.pointGroups()[0]

    ht.inline.api.consolidate_points(geo, group=group)

    assert len(geo.iterPoints()) == 212


def test_unique_points():
    """Test ht.inline.api.unique_points."""
    # Read only
    geo = get_obj_geo("test_unique_points")

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.unique_points(geo)

    # Full geometry
    geo = get_obj_geo_copy("test_unique_points")

    ht.inline.api.unique_points(geo)

    assert len(geo.iterPoints()) == 324

    # By group
    geo = get_obj_geo_copy("test_unique_points_point_group")

    group = geo.pointGroups()[0]
    ht.inline.api.unique_points(geo, group)

    assert len(geo.iterPoints()) == 195


def test_rename_group():
    """Test ht.inline.api.rename_group."""
    # Read only
    geo = get_obj_geo("test_rename_point_group")
    group = geo.pointGroups()[0]

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.rename_group(group, "test_group")

    # Point group
    geo = get_obj_geo_copy("test_rename_point_group")

    group = geo.pointGroups()[0]

    result = ht.inline.api.rename_group(group, "test_group")

    assert result is not None
    assert result.name() == "test_group"

    # Same name.
    group = geo.pointGroups()[0]
    name = group.name()

    with pytest.raises(hou.OperationFailed):
        ht.inline.api.rename_group(group, name)

    # Prim group
    geo = get_obj_geo_copy("test_rename_prim_group")
    group = geo.primGroups()[0]

    result = ht.inline.api.rename_group(group, "test_group")

    assert result is not None
    assert result.name() == "test_group"

    # Same name
    group = geo.primGroups()[0]
    name = group.name()

    with pytest.raises(hou.OperationFailed):
        ht.inline.api.rename_group(group, name)

    # Edge Group
    geo = get_obj_geo_copy("test_rename_edge_group")
    group = geo.edgeGroups()[0]

    result = ht.inline.api.rename_group(group, "test_group")

    assert result is not None
    assert result.name() == "test_group"

    # Same name
    group = geo.edgeGroups()[0]
    name = group.name()

    with pytest.raises(hou.OperationFailed):
        ht.inline.api.rename_group(group, name)


def test_group_bounding_box():
    """Test ht.inline.api.group_bounding_box."""
    # Point group
    target = hou.BoundingBox(-4, 0, -1, -2, 0, 2)

    geo = get_obj_geo("test_group_bounding_box_point")

    group = geo.pointGroups()[0]
    bbox = ht.inline.api.group_bounding_box(group)

    assert bbox == target

    # Prim group
    target = hou.BoundingBox(-5, 0, -4, 4, 0, 5)

    geo = get_obj_geo("test_group_bounding_box_prim")

    group = geo.primGroups()[0]
    bbox = ht.inline.api.group_bounding_box(group)

    assert bbox == target

    # Edge group
    target = hou.BoundingBox(-5, 0, -5, 4, 0, 5)

    geo = get_obj_geo("test_group_bounding_box_edge")

    group = geo.edgeGroups()[0]
    bbox = ht.inline.api.group_bounding_box(group)

    assert bbox == target


def test_group_size():
    """Test ht.inline.api.group_size."""
    # Point group
    geo = get_obj_geo("test_point_group_size")

    group = geo.pointGroups()[0]

    assert ht.inline.api.group_size(group) == 12

    # Prim group
    geo = get_obj_geo("test_prim_group_size")

    group = geo.primGroups()[0]

    assert ht.inline.api.group_size(group) == 39

    # Edge group
    geo = get_obj_geo("test_edge_group_size")

    group = geo.edgeGroups()[0]

    assert ht.inline.api.group_size(group) == 52


def test_toggle_point_in_group():
    """Test ht.inline.api.toggle_point_in_group."""
    # Read only
    geo = get_obj_geo("test_toggle_point")

    group = geo.pointGroups()[0]
    point = geo.iterPoints()[0]

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.toggle_point_in_group(group, point)

    geo = get_obj_geo_copy("test_toggle_point")

    group = geo.pointGroups()[0]
    point = geo.iterPoints()[0]

    ht.inline.api.toggle_point_in_group(group, point)

    assert group.contains(point)


def test_toggle_prim_in_group():
    """Test ht.inline.api.toggle_point_in_group."""
    # Read only
    geo = get_obj_geo("test_toggle_prim")

    group = geo.primGroups()[0]
    prim = geo.iterPrims()[0]

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.toggle_prim_in_group(group, prim)

    geo = get_obj_geo_copy("test_toggle_prim")

    group = geo.primGroups()[0]
    prim = geo.iterPrims()[0]

    ht.inline.api.toggle_prim_in_group(group, prim)

    assert group.contains(prim)


def test_toggle_group_entries():
    """Test ht.inline.api.toggle_group_entries."""
    # Read only
    geo = get_obj_geo("test_toggle_entries_point")

    group = geo.pointGroups()[0]

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.toggle_group_entries(group)

    # Point group
    geo = get_obj_geo_copy("test_toggle_entries_point")

    values = geo.globPoints(" ".join([str(val) for val in range(1, 100, 2)]))

    group = geo.pointGroups()[0]
    ht.inline.api.toggle_group_entries(group)

    assert group.points() == values

    # Prim group
    geo = get_obj_geo_copy("test_toggle_entries_prim")

    values = geo.globPrims(" ".join([str(val) for val in range(0, 100, 2)]))

    group = geo.primGroups()[0]
    ht.inline.api.toggle_group_entries(group)

    assert group.prims() == values

    # Edge group
    geo = get_obj_geo_copy("test_toggle_entries_edge")

    group = geo.edgeGroups()[0]
    ht.inline.api.toggle_group_entries(group)

    assert len(group.edges()) == 20


def test_copy_group():
    """Test ht.inline.api.copy_group."""
    # Read only
    geo = get_obj_geo("test_copy_point_group")

    group = geo.pointGroups()[0]

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.copy_group(group, "new_group")

    geo = get_obj_geo_copy("test_copy_point_group")

    group = geo.pointGroups()[0]

    new_group = ht.inline.api.copy_group(group, "new_group")

    assert group.points() == new_group.points()

    # Same name
    group = geo.pointGroups()[0]

    with pytest.raises(hou.OperationFailed):
        ht.inline.api.copy_group(group, group.name())

    # Existing group
    geo = get_obj_geo_copy("test_copy_point_group_existing")

    group = geo.pointGroups()[-1]

    other_group = geo.pointGroups()[0]

    with pytest.raises(hou.OperationFailed):
        ht.inline.api.copy_group(group, other_group.name())

    # Prim group
    geo = get_obj_geo_copy("test_copy_prim_group")

    group = geo.primGroups()[0]

    new_group = ht.inline.api.copy_group(group, "new_group")

    assert group.prims() == new_group.prims()

    # Same name
    group = geo.primGroups()[0]

    with pytest.raises(hou.OperationFailed):
        ht.inline.api.copy_group(group, group.name())

    # Existing group
    geo = get_obj_geo_copy("test_copy_prim_group_existing")

    group = geo.primGroups()[-1]

    other_group = geo.primGroups()[0]

    with pytest.raises(hou.OperationFailed):
        ht.inline.api.copy_group(group, other_group.name())


def test_groups_share_elements():
    """Test ht.inline.api.groups_share_elements."""
    geo = get_obj_geo_copy("test_point_group_contains_any")

    group1 = geo.pointGroups()[0]
    group2 = geo.pointGroups()[1]

    assert ht.inline.api.groups_share_elements(group1, group2)

    group1 = (
        OBJ.node("test_point_group_contains_any_False/group1")
        .geometry()
        .pointGroups()[0]
    )
    group2 = (
        OBJ.node("test_point_group_contains_any_False/group2")
        .geometry()
        .pointGroups()[0]
    )

    with pytest.raises(ValueError):
        ht.inline.api.groups_share_elements(group1, group2)

    # Different types
    group3 = (
        OBJ.node("test_point_group_contains_any_False/group2")
        .geometry()
        .primGroups()[0]
    )

    with pytest.raises(TypeError):
        ht.inline.api.groups_share_elements(group3, group2)

    # Prim groups
    geo = get_obj_geo_copy("test_prim_group_contains_any")

    group1 = geo.primGroups()[0]
    group2 = geo.primGroups()[1]

    assert ht.inline.api.groups_share_elements(group1, group2)

    # Different details
    group1 = (
        OBJ.node("test_prim_group_contains_any_False/group1").geometry().primGroups()[0]
    )
    group2 = (
        OBJ.node("test_prim_group_contains_any_False/group2").geometry().primGroups()[0]
    )

    with pytest.raises(ValueError):
        ht.inline.api.groups_share_elements(group1, group2)


def test_convert_prim_to_point_group():
    """Test ht.inline.api.convert_prim_to_point_group."""
    # Read only
    geo = get_obj_geo("test_convert_prim_to_point_group")

    group = geo.primGroups()[0]

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.convert_prim_to_point_group(group)

    geo = get_obj_geo_copy("test_convert_prim_to_point_group")

    group = geo.primGroups()[0]

    new_group = ht.inline.api.convert_prim_to_point_group(group)

    assert len(new_group.points()) == 12

    # Check source group was deleted.
    assert not geo.primGroups()

    # New name
    geo = get_obj_geo_copy("test_convert_prim_to_point_group")

    group = geo.primGroups()[0]

    new_group = ht.inline.api.convert_prim_to_point_group(group, "new_group")

    assert new_group.name() == "new_group"

    # Don't destroy
    geo = get_obj_geo_copy("test_convert_prim_to_point_group")

    group = geo.primGroups()[0]

    ht.inline.api.convert_prim_to_point_group(group, destroy=False)

    # Check source group wasn't deleted.
    assert len(geo.primGroups()) == 1

    # Target name exists
    group = geo.primGroups()[0]

    with pytest.raises(hou.OperationFailed):
        ht.inline.api.convert_prim_to_point_group(group, group.name())


def test_convert_point_to_prim_group():
    """Test ht.inline.api.convert_point_to_prim_group."""
    # Read only
    geo = get_obj_geo("test_convert_point_to_prim_group")

    group = geo.pointGroups()[0]

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.convert_point_to_prim_group(group)

    geo = get_obj_geo_copy("test_convert_point_to_prim_group")

    group = geo.pointGroups()[0]

    new_group = ht.inline.api.convert_point_to_prim_group(group)

    assert len(new_group.prims()) == 5

    # Check source group was deleted.
    assert not geo.pointGroups()

    # New name
    geo = get_obj_geo_copy("test_convert_point_to_prim_group")

    group = geo.pointGroups()[0]

    new_group = ht.inline.api.convert_point_to_prim_group(group, "new_group")

    assert new_group.name() == "new_group"

    # Don't destroy
    geo = get_obj_geo_copy("test_convert_point_to_prim_group")

    group = geo.pointGroups()[0]

    ht.inline.api.convert_point_to_prim_group(group, destroy=False)

    # Check source group wasn't deleted.
    assert len(geo.primGroups()) == 1

    # Target name exists
    group = geo.pointGroups()[0]

    with pytest.raises(hou.OperationFailed):
        ht.inline.api.convert_point_to_prim_group(group, group.name())


# =========================================================================
# UNGROUPED POINTS
# =========================================================================


def test_geometry_has_ungrouped_points():
    """Test ht.inline.api.geometry_has_ungrouped_points."""
    geo = get_obj_geo("test_has_ungrouped_points")

    assert ht.inline.api.geometry_has_ungrouped_points(geo)

    geo = get_obj_geo("test_has_ungrouped_points_False")

    assert not ht.inline.api.geometry_has_ungrouped_points(geo)


def test_group_ungrouped_points():
    """Test ht.inline.api.group_ungrouped_points."""
    # Read only
    geo = get_obj_geo("test_group_ungrouped_points")

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.group_ungrouped_points(geo, "ungrouped")

    geo = get_obj_geo_copy("test_group_ungrouped_points")

    group = ht.inline.api.group_ungrouped_points(geo, "ungrouped")

    assert len(group.points()) == 10

    # Existing name
    geo = get_obj_geo_copy("test_group_ungrouped_points")

    with pytest.raises(hou.OperationFailed):
        ht.inline.api.group_ungrouped_points(geo, "group1")

    # Empty name
    geo = get_obj_geo_copy("test_group_ungrouped_points")

    with pytest.raises(ValueError):
        ht.inline.api.group_ungrouped_points(geo, "")

    # Failure
    geo = get_obj_geo_copy("test_group_ungrouped_points_False")

    group = ht.inline.api.group_ungrouped_points(geo, "ungrouped")

    assert group is None


# =========================================================================
# UNGROUPED PRIMS
# =========================================================================


def test_has_ungrouped_prims():
    """Test ht.inline.api.geometry_has_ungrouped_prims."""
    geo = get_obj_geo("test_has_ungrouped_prims")

    assert ht.inline.api.geometry_has_ungrouped_prims(geo)

    geo = get_obj_geo("test_has_ungrouped_prims_False")

    assert not ht.inline.api.geometry_has_ungrouped_prims(geo)


def test_group_ungrouped_prims():
    """Test ht.inline.api.group_ungrouped_prims."""
    # Read only
    geo = get_obj_geo("test_group_ungrouped_prims")

    with pytest.raises(hou.GeometryPermissionError):
        ht.inline.api.group_ungrouped_prims(geo, "ungrouped")

    geo = get_obj_geo_copy("test_group_ungrouped_prims")

    group = ht.inline.api.group_ungrouped_prims(geo, "ungrouped")

    assert len(group.prims()) == 3

    # Existing name
    geo = get_obj_geo_copy("test_group_ungrouped_prims")

    with pytest.raises(hou.OperationFailed):
        ht.inline.api.group_ungrouped_prims(geo, "group1")

    # Empty name
    geo = get_obj_geo_copy("test_group_ungrouped_prims")

    with pytest.raises(ValueError):
        ht.inline.api.group_ungrouped_prims(geo, "")

    # Failure
    geo = get_obj_geo_copy("test_group_ungrouped_prims_False")

    group = ht.inline.api.group_ungrouped_prims(geo, "ungrouped")

    assert group is None


# =========================================================================
# BOUNDING BOXES
# =========================================================================


def test_bounding_box_is_inside():
    """Test ht.inline.api.bounding_box_is_inside."""
    bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)
    bbox2 = hou.BoundingBox(-1, -1, -1, 1, 1, 1)

    assert ht.inline.api.bounding_box_is_inside(bbox1, bbox2)

    # Bounding box is not inside.
    bbox3 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

    assert not ht.inline.api.bounding_box_is_inside(bbox1, bbox3)


def test_bounding_boxes_intersect():
    """Test ht.inline.api.bounding_boxes_intersect."""
    bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)
    bbox2 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

    assert ht.inline.api.bounding_boxes_intersect(bbox1, bbox2)

    # Bounding boxes don't intersect.
    bbox3 = hou.BoundingBox(-0.5, -0.5, -0.5, -0.1, -0.1, -0.1)

    assert not ht.inline.api.bounding_boxes_intersect(bbox3, bbox2)


def test_compute_bounding_box_intersection():
    """Test ht.inline.api.compute_bounding_box_intersection."""
    bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)
    bbox2 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

    assert ht.inline.api.compute_bounding_box_intersection(bbox1, bbox2)

    assert bbox1.minvec() == hou.Vector3()
    assert bbox1.maxvec() == hou.Vector3(0.5, 0.5, 0.5)

    # Unable to compute interaction.
    bbox3 = hou.BoundingBox(-0.5, -0.5, -0.5, -0.1, -0.1, -0.1)

    assert not ht.inline.api.compute_bounding_box_intersection(bbox3, bbox2)


def test_expand_bounding_box():
    """Test ht.inline.api.expand_bounding_box."""
    bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)
    ht.inline.api.expand_bounding_box(bbox, 1, 1, 1)

    assert bbox.minvec() == hou.Vector3(-2, -2.75, -4)
    assert bbox.maxvec() == hou.Vector3(2, 2.75, 4)


def test_add_to_bounding_box_min():
    """Test ht.inline.api.add_to_bounding_box_min."""
    bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)
    ht.inline.api.add_to_bounding_box_min(bbox, hou.Vector3(1, 0.25, 1))

    assert bbox.minvec() == hou.Vector3(0, -1.5, -2)


def test_add_to_bounding_box_max():
    """Test ht.inline.api.add_to_bounding_box_max."""
    bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)
    ht.inline.api.add_to_bounding_box_max(bbox, hou.Vector3(2, 0.25, 1))

    assert bbox.maxvec() == hou.Vector3(3, 2, 4)


def test_bounding_box_area():
    """Test ht.inline.api.bounding_box_area."""
    bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)

    assert ht.inline.api.bounding_box_area(bbox) == 80


def test_bounding_box_volume():
    """Test ht.inline.api.bounding_box_volume."""
    bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)

    assert ht.inline.api.bounding_box_volume(bbox) == 42


# =========================================================================
# PARMS
# =========================================================================


def test_is_parm_tuple_vector():
    """Test ht.inline.api.is_parm_tuple_vector."""
    node = OBJ.node("test_is_vector/node")
    parm = node.parmTuple("vec")

    assert ht.inline.api.is_parm_tuple_vector(parm)

    # Not a vector parameter.
    parm = node.parmTuple("not_vec")

    assert not ht.inline.api.is_parm_tuple_vector(parm)


def test_eval_parm_tuple_as_vector():
    """Test ht.inline.api.eval_parm_tuple_as_vector."""
    node = OBJ.node("test_eval_as_vector/node")
    parm = node.parmTuple("vec2")

    assert ht.inline.api.eval_parm_tuple_as_vector(parm) == hou.Vector2(1, 2)

    parm = node.parmTuple("vec3")

    assert ht.inline.api.eval_parm_tuple_as_vector(parm) == hou.Vector3(3, 4, 5)

    parm = node.parmTuple("vec4")

    assert ht.inline.api.eval_parm_tuple_as_vector(parm) == hou.Vector4(6, 7, 8, 9)

    parm = node.parmTuple("not_vec")

    with pytest.raises(ValueError):
        ht.inline.api.eval_parm_tuple_as_vector(parm)


def test_is_parm_tuple_color():
    """Test ht.inline.api.is_parm_tuple_color."""
    node = OBJ.node("test_is_color/node")
    parm = node.parmTuple("color")

    assert ht.inline.api.is_parm_tuple_color(parm)

    # Not a color.
    parm = node.parmTuple("not_color")

    assert not ht.inline.api.is_parm_tuple_color(parm)


def test_eval_parm_tuple_as_color():
    """Test ht.inline.api.eval_parm_tuple_as_color."""
    node = OBJ.node("test_eval_as_color/node")
    parm = node.parmTuple("color")

    assert ht.inline.api.eval_parm_tuple_as_color(parm) == hou.Color(0, 0.5, 0.5)

    # Not a color.
    parm = node.parmTuple("not_color")

    with pytest.raises(ValueError):
        ht.inline.api.eval_parm_tuple_as_color(parm)


def test_eval_parm_as_strip():
    """Test ht.inline.api.eval_parm_as_strip."""
    node = OBJ.node("test_eval_as_strip/node")

    parm = node.parm("cacheinput")

    with pytest.raises(TypeError):
        ht.inline.api.eval_parm_as_strip(parm)

    parm = node.parm("strip_normal")

    target = (False, True, False, False)

    assert ht.inline.api.eval_parm_as_strip(parm) == target

    # Toggle strip
    parm = node.parm("strip_toggle")

    target = (True, False, True, True)

    assert ht.inline.api.eval_parm_as_strip(parm) == target


def test_eval_parm_strip_as_string():
    """Test ht.inline.api.eval_parm_strip_as_string."""
    node = OBJ.node("test_eval_as_strip/node")
    parm = node.parm("strip_normal")

    target = ("bar",)

    assert ht.inline.api.eval_parm_strip_as_string(parm) == target

    # Toggle strip.
    parm = node.parm("strip_toggle")

    target = ("foo", "hello", "world")

    assert ht.inline.api.eval_parm_strip_as_string(parm) == target


# =========================================================================
# MULTIPARMS
# =========================================================================


def test_is_parm_multiparm():
    """Test ht.inline.api.is_parm_multiparm."""
    node = OBJ.node("test_is_multiparm/object_merge")
    parm = node.parm("numobj")

    assert ht.inline.api.is_parm_multiparm(parm)

    parm_tuple = node.parmTuple("numobj")
    assert ht.inline.api.is_parm_multiparm(parm_tuple)

    parm = node.parm("objpath1")
    assert not ht.inline.api.is_parm_multiparm(parm)

    parm_tuple = node.parmTuple("objpath1")
    assert not ht.inline.api.is_parm_multiparm(parm_tuple)


def test_get_multiparm_instances_per_item():
    """Test ht.inline.api.get_multiparm_instances_per_item."""
    node = OBJ.node("test_get_multiparm_instances_per_item/object_merge")

    parm = node.parm("numobj")
    assert ht.inline.api.get_multiparm_instances_per_item(parm) == 4

    parm_tuple = node.parmTuple("numobj")
    assert ht.inline.api.get_multiparm_instances_per_item(parm_tuple) == 4

    parm = node.parm("xformtype")

    with pytest.raises(ValueError):
        ht.inline.api.get_multiparm_instances_per_item(parm)


def test_get_multiparm_start_offset():
    """Test ht.inline.api.get_multiparm_start_offset."""
    node = OBJ.node("test_get_multiparm_start_offset/add")

    parm = node.parm("remove")

    with pytest.raises(ValueError):
        ht.inline.api.get_multiparm_start_offset(parm)

    parm = node.parm("points")
    assert ht.inline.api.get_multiparm_start_offset(parm) == 0

    parm_tuple = node.parmTuple("points")
    assert ht.inline.api.get_multiparm_start_offset(parm_tuple) == 0

    node = OBJ.node("test_get_multiparm_start_offset/object_merge")
    parm = node.parm("numobj")

    assert ht.inline.api.get_multiparm_start_offset(parm) == 1

    parm_tuple = node.parmTuple("numobj")
    assert ht.inline.api.get_multiparm_start_offset(parm_tuple) == 1


def test_get_multiparm_instance_index():
    """Test ht.inline.api.get_multiparm_instance_index."""
    target = (2,)

    node = OBJ.node("test_get_multiparm_instance_index/object_merge")
    parm = node.parm("objpath2")

    assert ht.inline.api.get_multiparm_instance_index(parm) == target

    parm_tuple = node.parmTuple("objpath2")

    assert ht.inline.api.get_multiparm_instance_index(parm_tuple) == target

    parm = node.parm("numobj")

    with pytest.raises(ValueError):
        ht.inline.api.get_multiparm_instance_index(parm)

    parm_tuple = node.parmTuple("numobj")

    with pytest.raises(ValueError):
        ht.inline.api.get_multiparm_instance_index(parm_tuple)


def test_get_multiparm_instances():
    """Test ht.inline.api.get_multiparm_instances."""
    node = OBJ.node("test_get_multiparm_instances/null1")

    parm = node.parm("cacheinput")

    with pytest.raises(ValueError):
        ht.inline.api.get_multiparm_instances(parm)

    target = (
        (node.parm("foo1"), node.parmTuple("bar1"), node.parm("hello1")),
        (node.parm("foo2"), node.parmTuple("bar2"), node.parm("hello2")),
    )

    parm = node.parm("things")

    instances = ht.inline.api.get_multiparm_instances(parm)

    assert instances == target

    parm_tuple = node.parmTuple("things")

    instances = ht.inline.api.get_multiparm_instances(parm_tuple)

    assert instances == target


def test_get_multiparm_instance_values():
    """Test ht.inline.api.get_multiparm_instance_values."""
    node = OBJ.node("test_get_multiparm_instance_values/null1")

    parm = node.parm("cacheinput")

    with pytest.raises(ValueError):
        ht.inline.api.get_multiparm_instance_values(parm)

    target = ((1, (2.0, 3.0, 4.0), "foo"), (5, (6.0, 7.0, 8.0), "bar"))

    parm = node.parm("things")

    values = ht.inline.api.get_multiparm_instance_values(parm)

    assert values == target

    parm_tuple = node.parmTuple("things")

    values = ht.inline.api.get_multiparm_instance_values(parm_tuple)

    assert values == target


def test_eval_multiparm_instance():
    """Test ht.inline.api.eval_multiparm_instance."""
    node = OBJ.node("test_eval_multiparm_instance/null1")

    with pytest.raises(ValueError):
        ht.inline.api.eval_multiparm_instance(node, "foo", 0)

    with pytest.raises(ValueError):
        ht.inline.api.eval_multiparm_instance(node, "test#", 0)

    # Ints
    assert ht.inline.api.eval_multiparm_instance(node, "foo#", 0) == 1
    assert ht.inline.api.eval_multiparm_instance(node, "foo#", 1) == 5

    with pytest.raises(IndexError):
        ht.inline.api.eval_multiparm_instance(node, "foo#", 2)

    # Floats
    assert ht.inline.api.eval_multiparm_instance(node, "bar#", 0) == (2.0, 3.0, 4.0)
    assert ht.inline.api.eval_multiparm_instance(node, "bar#", 1) == (6.0, 7.0, 8.0)

    with pytest.raises(IndexError):
        ht.inline.api.eval_multiparm_instance(node, "bar#", 2)

    # Strings
    assert ht.inline.api.eval_multiparm_instance(node, "hello#", 0) == "foo"
    assert ht.inline.api.eval_multiparm_instance(node, "hello#", 1) == "bar"

    # Ramp
    with pytest.raises(TypeError):
        ht.inline.api.eval_multiparm_instance(node, "rampparm#", 0)

    with pytest.raises(IndexError):
        ht.inline.api.eval_multiparm_instance(node, "hello#", 2)


# =========================================================================
# NODES AND NODE TYPES
# =========================================================================


def test_disconnect_all_outputs():
    """Test ht.inline.api.disconnect_all_inputs."""
    node = OBJ.node("test_disconnect_all_outputs/file")

    ht.inline.api.disconnect_all_outputs(node)

    assert not node.outputs()


def test_disconnect_all_inputs():
    """Test ht.inline.api.disconnect_all_outputs."""
    node = OBJ.node("test_disconnect_all_inputs/merge")

    ht.inline.api.disconnect_all_inputs(node)

    assert not node.inputs()


def test_node_is_contained_by():
    """Test ht.inline.api.node_is_contained_by."""
    node = OBJ.node("test_is_contained_by")

    box = node.node("subnet/box")

    assert ht.inline.api.node_is_contained_by(box, node)
    assert not ht.inline.api.node_is_contained_by(node, hou.node("/shop"))


def test_author_name():
    """Test ht.inline.api.node_author_name."""
    node = OBJ.node("test_author_name")

    assert ht.inline.api.node_author_name(node) == "gthompson"


def test_set_node_type_icon():
    """Test ht.inline.api.set_node_type_icon."""
    node_type = hou.nodeType(hou.objNodeTypeCategory(), "geo")
    ht.inline.api.set_node_type_icon(node_type, "SOP_box")

    assert node_type.icon() == "SOP_box"


def test_set_node_type_default_icon():
    """Test ht.inline.api.set_node_type_default_icon."""
    node_type = hou.nodeType(hou.objNodeTypeCategory(), "geo")
    ht.inline.api.set_node_type_icon(node_type, "SOP_box")

    ht.inline.api.set_node_type_default_icon(node_type)

    assert node_type.icon() == "OBJ_geo"


def test_is_node_type_python():
    """Test ht.inline.api.is_node_type_python."""
    node_type = hou.nodeType(hou.sopNodeTypeCategory(), "tableimport")
    assert ht.inline.api.is_node_type_python(node_type)

    # Not python
    node_type = hou.nodeType(hou.sopNodeTypeCategory(), "file")
    assert not ht.inline.api.is_node_type_python(node_type)


def test_is_node_type_subnet():
    """Test ht.inline.api.is_node_type_subnet."""
    node_type = hou.nodeType(hou.objNodeTypeCategory(), "subnet")
    assert ht.inline.api.is_node_type_subnet(node_type)

    # Not a subnet.
    node_type = hou.nodeType(hou.objNodeTypeCategory(), "geo")
    assert not ht.inline.api.is_node_type_subnet(node_type)


# =========================================================================
# VECTORS AND MATRICES
# =========================================================================


def test_vector_component_along():
    """Test ht.inline.api.vector_component_along."""
    vec = hou.Vector3(1, 2, 3)

    assert ht.inline.api.vector_component_along(vec, hou.Vector3(0, 0, 15)) == 3.0


def test_vector_project_along():
    """Test ht.inline.api.vector_project_along."""
    vec = hou.Vector3(-1.3, 0.5, 7.6)
    projection = ht.inline.api.vector_project_along(vec, hou.Vector3(2.87, 3.1, -0.5))

    result = hou.Vector3(-0.948531, -1.02455, 0.165249)

    assert projection.isAlmostEqual(result)


def test_vector_contains_nans():
    """Test ht.inline.api.vector_contains_nans."""
    nan = float("nan")

    vec = hou.Vector2(nan, 1)
    assert ht.inline.api.vector_contains_nans(vec)

    vec = hou.Vector3(6.5, 1, nan)
    assert ht.inline.api.vector_contains_nans(vec)

    vec = hou.Vector4(-4, 5, -0, nan)
    assert ht.inline.api.vector_contains_nans(vec)


def test_vector_compute_dual():
    """Test ht.inline.api.vector_compute_dual."""
    target = hou.Matrix3()
    target.setTo(((0, -3, 2), (3, 0, -1), (-2, 1, 0)))

    vec = hou.Vector3(1, 2, 3)

    assert ht.inline.api.vector_compute_dual(vec) == target


def test_is_identity_matrix():
    """Test ht.inline.api.is_identity_matrix."""
    # Matrix 3
    mat3 = hou.Matrix3()
    mat3.setToIdentity()

    assert ht.inline.api.is_identity_matrix(mat3)

    # Not the identity matrix.
    mat3 = hou.Matrix3()
    assert not ht.inline.api.is_identity_matrix(mat3)

    # Matrix4
    mat4 = hou.Matrix4()
    mat4.setToIdentity()

    assert ht.inline.api.is_identity_matrix(mat4)

    # Not the identity matrix.
    mat4 = hou.Matrix4()
    assert not ht.inline.api.is_identity_matrix(mat4)


def test_set_matrix_translates():
    """Test ht.inline.api.set_matrix_translates."""
    translates = hou.Vector3(1, 2, 3)
    identity = hou.hmath.identityTransform()
    ht.inline.api.set_matrix_translates(identity, translates)

    assert identity.extractTranslates() == translates


def test_build_lookat_matrix():
    """Test ht.inline.api.build_lookat_matrix."""
    target = hou.Matrix3()

    target.setTo(
        (
            (0.70710678118654746, -0.0, 0.70710678118654746),
            (0.0, 1.0, 0.0),
            (-0.70710678118654746, 0.0, 0.70710678118654746),
        )
    )

    mat = ht.inline.api.build_lookat_matrix(
        hou.Vector3(0, 0, 1), hou.Vector3(1, 0, 0), hou.Vector3(0, 1, 0)
    )

    assert mat == target


def test_build_instance_matrix():
    """Test ht.inline.api.build_instance_matrix."""
    target = hou.Matrix4(
        (
            (1.0606601717798214, -1.0606601717798214, 0.0, 0.0),
            (0.61237243569579436, 0.61237243569579436, -1.2247448713915889, 0.0),
            (0.86602540378443882, 0.86602540378443882, 0.86602540378443882, 0.0),
            (-1.0, 2.0, 4.0, 1.0),
        )
    )

    mat = ht.inline.api.build_instance_matrix(
        hou.Vector3(-1, 2, 4),
        hou.Vector3(1, 1, 1),
        pscale=1.5,
        up_vector=hou.Vector3(1, 1, -1),
    )

    assert mat == target

    # By orient
    target = hou.Matrix4(
        (
            (0.33212996389891691, 0.3465703971119134, -0.87725631768953083, 0.0),
            (-0.53068592057761732, 0.83754512635379064, 0.1299638989169675, 0.0),
            (0.77978339350180514, 0.42238267148014441, 0.46209386281588438, 0.0),
            (-1.0, 2.0, 4.0, 1.0),
        )
    )

    mat = ht.inline.api.build_instance_matrix(
        hou.Vector3(-1, 2, 4), orient=hou.Quaternion(0.3, -1.7, -0.9, -2.7)
    )

    assert mat == target


# =========================================================================
# DIGITAL ASSETS
# =========================================================================


def test_get_node_message_nodes():
    """Test ht.inline.api.get_node_message_nodes."""
    node = OBJ.node("test_message_nodes/solver")

    target = (node.node("d/s"),)

    assert ht.inline.api.get_node_message_nodes(node) == target


def test_get_node_editable_nodes():
    """Test ht.inline.api.get_node_editable_nodes."""
    node = OBJ.node("test_message_nodes/solver")

    target = (node.node("d/s"),)

    assert ht.inline.api.get_node_editable_nodes(node) == target


def test_get_node_dive_target():
    """Test ht.inline.api.get_node_dive_target."""
    node = OBJ.node("test_message_nodes/solver")

    target = node.node("d/s")

    assert ht.inline.api.get_node_dive_target(node) == target


def test_get_node_representative_node():
    """Test ht.inline.api.get_node_representative_node."""
    node = OBJ.node("test_representative_node")

    target = node.node("stereo_camera")

    assert ht.inline.api.get_node_representative_node(node) == target


def test_asset_file_meta_source():
    """Test ht.inline.api.asset_file_meta_source."""
    target = "Scanned Asset Library Directories"

    if hou.applicationVersion() >= (18):
        path = hou.text.expandString("$HH/otls/OPlibSop.hda")

    else:
        path = hou.expandString("$HH/otls/OPlibSop.hda")

    assert ht.inline.api.asset_file_meta_source(path) == target


def test_get_definition_meta_source():
    """Test ht.inline.api.get_definition_meta_source."""
    target = "Scanned Asset Library Directories"

    node_type = hou.nodeType(hou.sopNodeTypeCategory(), "explodedview")

    assert ht.inline.api.get_definition_meta_source(node_type.definition()) == target


def test_libraries_in_meta_source():
    """Test ht.inline.api.libraries_in_meta_source."""
    libs = ht.inline.api.libraries_in_meta_source("Scanned Asset Library Directories")
    assert libs


def test_is_dummy_definition():
    """Test ht.inline.api.is_dummy_definition."""
    geo = OBJ.createNode("geo")
    subnet = geo.createNode("subnet")

    # Create a new digital asset.
    asset = subnet.createDigitalAsset("dummyop", "Embedded", "Dummy")
    node_type = asset.type()

    # Not a dummy so far.
    assert not ht.inline.api.is_dummy_definition(node_type.definition())

    # Destroy the definition.
    node_type.definition().destroy()

    # Now it's a dummy.
    assert ht.inline.api.is_dummy_definition(node_type.definition())

    # Destroy the instance.
    asset.destroy()

    # Destroy the dummy definition.
    node_type.definition().destroy()


# =============================================================================
# FUNCTIONS
# =============================================================================


def get_obj_geo(node_path):
    """Get the geometry from the display node of a Geometry object."""
    return OBJ.node(node_path).displayNode().geometry()


def get_obj_geo_copy(node_path):
    """Get a copy of the geometry from the display node of a Geometry object."""
    # Create a new hou.Geometry object.
    geo = hou.Geometry()

    # Get the geometry object's geo.
    source_geo = get_obj_geo(node_path)

    # Merge the geo to copy it.
    geo.merge(source_geo)

    return geo
