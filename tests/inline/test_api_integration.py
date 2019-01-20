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
import os
import unittest

# Houdini Toolbox Imports
import ht.inline.api

# Houdini Imports
import hou

# =============================================================================
# GLOBALS
# =============================================================================

OBJ = hou.node("/obj")
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

# =============================================================================
# CLASSES
# =============================================================================

class TestInlineCpp(unittest.TestCase):
    """This class implements test cases for the fuctions added through the
    inline.py module.

    """

    @classmethod
    def setUpClass(cls):
        hou.hipFile.load(os.path.join(THIS_DIR, "test_inline.hipnc"))

    @classmethod
    def tearDownClass(cls):
        hou.hipFile.clear()

    # =========================================================================

    def test_get_attrib_owner_from_geometry_entity_type(self):
        self.assertEquals(ht.inline.api._get_attrib_owner_from_geometry_entity_type(hou.Vertex), 0)
        self.assertEquals(ht.inline.api._get_attrib_owner_from_geometry_entity_type(hou.Point), 1)
        self.assertEquals(ht.inline.api._get_attrib_owner_from_geometry_entity_type(hou.Prim), 2)
        self.assertEquals(ht.inline.api._get_attrib_owner_from_geometry_entity_type(hou.Face), 2)
        self.assertEquals(ht.inline.api._get_attrib_owner_from_geometry_entity_type(hou.Volume), 2)
        self.assertEquals(ht.inline.api._get_attrib_owner_from_geometry_entity_type(hou.Polygon), 2)
        self.assertEquals(ht.inline.api._get_attrib_owner_from_geometry_entity_type(hou.Geometry), 3)

        with self.assertRaises(TypeError):
            ht.inline.api._get_attrib_owner_from_geometry_entity_type(None)

    def test_ge_variable(self):
        hip_name = hou.get_variable("HIPNAME")

        self.assertEqual(hip_name, os.path.splitext(os.path.basename(hou.hipFile.path()))[0])

    def test_set_variable(self):
        value = 22
        hou.set_variable("awesome", value)

        self.assertEqual(hou.get_variable("awesome"), 22)

    def test_get_variable_names(self):
        variableNames = hou.get_variable_names()

        self.assertTrue("ACTIVETAKE" in variableNames)

    def test_getDirtyVariableNames(self):
        variableNames = hou.get_variable_names()

        dirtyVariableNames = hou.get_variable_names(dirty=True)

        self.assertNotEqual(variableNames, dirtyVariableNames)

    def test_unset_variable(self):
        hou.set_variable("tester", 10)
        hou.unset_variable("tester")

        self.assertTrue(hou.get_variable("tester") is None)

    def test_emit_var_change(self):
        parm = hou.parm("/obj/test_emit_var_change/file1/file")

        string = "something_$VARCHANGE.bgeo"

        parm.set(string)

        path = parm.eval()

        self.assertEqual(path, string.replace("$VARCHANGE", ""))

        hou.set_variable("VARCHANGE", 22)

        hou.emit_var_change()

        new_path = parm.eval()

        # Test the paths aren't the same.
        self.assertNotEqual(path, new_path)

        # Test the update was successful.
        self.assertEqual(new_path, string.replace("$VARCHANGE", "22"))

    def test_expand_range(self):
        values = hou.expand_range("0-5 10-20:2 64 65-66")
        target = (0, 1, 2, 3, 4, 5, 10, 12, 14, 16, 18, 20, 64, 65, 66)

        self.assertEqual(values, target)

    def test_read_only(self):
        geo = get_obj_geo("test_read_only")

        self.assertTrue(geo.read_only)

    def test_read_onlyFalse(self):
        geo = hou.Geometry()
        self.assertFalse(geo.read_only())

    def test_num_points(self):
        geo = get_obj_geo("test_num_points")

        self.assertEqual(geo.num_points(), 5000)

    def test_num_prims(self):
        geo = get_obj_geo("test_num_prims")

        self.assertEqual(geo.num_prims(), 12)

    def test_pack_geometry(self):
        geo = get_obj_geo("test_pack_geometry")

        prim = geo.prims()[0]

        self.assertTrue(isinstance(prim, hou.PackedGeometry))

    def test_sort_by_attribute(self):
        geo = get_obj_geo_copy("test_sort_by_attribute")

        attrib = geo.findPrimAttrib("id")

        geo.sort_by_attribute(attrib)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, range(10))

    def test_sort_by_attribute_reversed(self):
        geo = get_obj_geo_copy("test_sort_by_attribute")

        attrib = geo.findPrimAttrib("id")

        geo.sort_by_attribute(attrib, reverse=True)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, list(reversed(range(10))))

    def test_sort_by_attribute_invalid_index(self):
        geo = get_obj_geo_copy("test_sort_by_attribute")

        attrib = geo.findPrimAttrib("id")

        with self.assertRaises(IndexError):
            geo.sort_by_attribute(attrib, 1)

    def test_sort_by_attribute_detail(self):
        geo = get_obj_geo_copy("test_sort_by_attribute")

        attrib = geo.findGlobalAttrib("varmap")

        with self.assertRaises(hou.OperationFailed):
            geo.sort_by_attribute(attrib)

    def test_sort_along_axis_points(self):
        geo = get_obj_geo_copy("test_sort_along_axis_points")

        geo.sort_along_axis(hou.geometryType.Points, 0)

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, range(10))

    def test_sort_along_axis_prims(self):
        geo = get_obj_geo_copy("test_sort_along_axis_prims")

        geo.sort_along_axis(hou.geometryType.Primitives, 2)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, range(10))

    def test_sort_by_values(self):
        # TODO: Test this.
        pass

    def test_sort_randomlyPoints(self):
        SEED = 11
        TARGET = [5, 9, 3, 8, 0, 2, 6, 1, 4, 7]

        geo = get_obj_geo_copy("test_sort_randomly_points")
        geo.sort_randomly(hou.geometryType.Points, SEED)

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_sort_randomlyPrims(self):
        SEED = 345
        TARGET = [4, 0, 9, 2, 1, 8, 3, 6, 7, 5]

        geo = get_obj_geo_copy("test_sort_randomly_prims")
        geo.sort_randomly(hou.geometryType.Primitives, SEED)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_shift_elementsPoints(self):
        OFFSET = -18
        TARGET = [8, 9, 0, 1, 2, 3, 4, 5, 6, 7]

        geo = get_obj_geo_copy("test_shift_elements_points")
        geo.shift_elements(hou.geometryType.Points, OFFSET)

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_shift_elementsPrims(self):
        OFFSET = 6
        TARGET = [4, 5, 6, 7, 8, 9, 0, 1, 2, 3]

        geo = get_obj_geo_copy("test_shift_elements_prims")
        geo.shift_elements(hou.geometryType.Primitives, OFFSET)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_reverse_sortPoints(self):
        TARGET = range(10)
        TARGET.reverse()

        geo = get_obj_geo_copy("test_reverse_sort_points")
        geo.reverse_sort(hou.geometryType.Points)

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_reverse_sortPrims(self):
        TARGET = range(10)
        TARGET.reverse()

        geo = get_obj_geo_copy("test_reverse_sort_prims")
        geo.reverse_sort(hou.geometryType.Primitives)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_sort_by_proximity_points(self):
        TARGET = [4, 3, 5, 2, 6, 1, 7, 0, 8, 9]
        POSITION = hou.Vector3(4, 1, 2)

        geo = get_obj_geo_copy("test_sort_by_proximity_points")
        geo.sort_by_proximity_to_position(hou.geometryType.Points, POSITION)

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_sort_by_proximity_prims(self):
        TARGET = [6, 7, 5, 8, 4, 9, 3, 2, 1, 0]
        POSITION = hou.Vector3(3, -1, 2)

        geo = get_obj_geo_copy("test_sort_by_proximity_prims")
        geo.sort_by_proximity_to_position(hou.geometryType.Primitives, POSITION)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_sort_by_vertex_order(self):
        TARGET = range(10)

        geo = get_obj_geo_copy("test_sort_by_vertex_order")
        geo.sort_by_vertex_order()

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_sort_by_expression_points(self):
        target_geo = OBJ.node("test_sort_by_expression_points/RESULT").geometry()
        test_geo = OBJ.node("test_sort_by_expression_points/TEST").geometry()

        self.assertEqual(
            test_geo.pointFloatAttribValues("id"),
            target_geo.pointFloatAttribValues("id"),
        )

    def test_sort_by_expression_prims(self):
        target_geo = OBJ.node("test_sort_by_expression_prims/RESULT").geometry()
        test_geo = OBJ.node("test_sort_by_expression_prims/TEST").geometry()

        self.assertEqual(
            test_geo.primFloatAttribValues("id"),
            target_geo.primFloatAttribValues("id"),
        )

    def test_create_point_at_position(self):
        geo = hou.Geometry()

        point = geo.create_point_at_position(hou.Vector3(1, 2, 3))

        self.assertEqual(point.position(), hou.Vector3(1, 2, 3))

    def test_create_n_points(self):
        geo = hou.Geometry()
        points = geo.create_n_points(15)

        self.assertEqual(points, geo.points())

    def test_create_n_pointsInvalidNumber(self):
        geo = hou.Geometry()

        with self.assertRaises(hou.OperationFailed):
            geo.create_n_points(-4)

    def test_merge_point_group(self):
        geo = hou.Geometry()
        source_geo = get_obj_geo("test_merge_point_group")

        group = source_geo.pointGroups()[0]

        geo.merge_point_group(group)

        self.assertEqual(len(geo.iterPoints()), len(group.points()))

    def test_merge_points(self):
        geo = hou.Geometry()
        source_geo = get_obj_geo("test_merge_points")

        points = source_geo.globPoints("0 6 15 35-38 66")

        geo.merge_points(points)

        self.assertEqual(len(geo.iterPoints()), len(points))

    def test_merge_prim_group(self):
        geo = hou.Geometry()
        source_geo = get_obj_geo("test_merge_prim_group")

        group = source_geo.primGroups()[0]

        geo.merge_prim_group(group)

        self.assertEqual(len(geo.iterPrims()), len(group.prims()))

    def test_merge_prims(self):
        geo = hou.Geometry()
        source_geo = get_obj_geo("test_merge_prims")

        prims = source_geo.globPrims("0 6 15 35-38 66")

        geo.merge_prims(prims)

        self.assertEqual(len(geo.iterPrims()), len(prims))


    def test_copy_point_attribute_values(self):
        source = get_obj_geo("test_copy_point_attribute_values")

        attribs = source.pointAttribs()

        geo = hou.Geometry()

        p1 = geo.createPoint()
        p2 = geo.createPoint()

        p1.copyAttribValues(source.iterPoints()[2], attribs)
        p2.copyAttribValues(source.iterPoints()[6], attribs)

        # Ensure all the attributes got copied right.
        self.assertEqual(len(geo.pointAttribs()), len(attribs))

        # Ensure P got copied right.
        self.assertEqual(p1.position(), hou.Vector3(5, 0, -5))
        self.assertEqual(p2.position(), hou.Vector3(-5, 0, 5))

    def test_copy_prim_attribute_values(self):
        source = get_obj_geo("test_copy_prim_attribute_values")

        attribs = source.primAttribs()

        geo = hou.Geometry()

        p1 = geo.createPolygon()
        p2 = geo.createPolygon()

        p1.copyAttribValues(source.iterPrims()[1], attribs)
        p2.copyAttribValues(source.iterPrims()[4], attribs)

        # Ensure all the attributes got copied right.
        self.assertEqual(len(geo.primAttribs()), len(attribs))

        # Ensure P got copied right.
        self.assertEqual(p1.attribValue("prnum"), 1)
        self.assertEqual(p2.attribValue("prnum"), 4)

    def test_point_adjacent_polygons(self):
        geo = get_obj_geo("test_point_adjacent_polygons")

        TARGET = geo.globPrims("1 2")

        prims = geo.iterPrims()[0].point_adjacent_polygons()

        self.assertEqual(prims, TARGET)

    def test_edge_adjacent_polygons(self):
        geo = get_obj_geo("test_edge_adjacent_polygons")

        TARGET = geo.globPrims("2")

        prims = geo.iterPrims()[0].edge_adjacent_polygons()

        self.assertEqual(prims, TARGET)

    def test_connected_prims(self):
        geo = get_obj_geo("test_connected_prims")

        TARGET = geo.prims()

        prims = geo.iterPoints()[4].connected_prims()

        self.assertEqual(prims, TARGET)

    def test_connected_points(self):
        geo = get_obj_geo("test_connected_points")

        TARGET = geo.globPoints("1 3 5 7")

        points = geo.iterPoints()[4].connected_points()

        self.assertEqual(points, TARGET)

    def test_referencing_vertices(self):
        geo = get_obj_geo("test_referencing_vertices")

        TARGET = geo.globVertices("0v2 1v3 2v1 3v0")

        verts = geo.iterPoints()[4].referencing_vertices()

        self.assertEqual(verts, TARGET)

    def test_point_string_table_indices(self):
        geo = get_obj_geo("test_point_string_table_indices")

        TARGET = (0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1)

        attr = geo.findPointAttrib("test")

        self.assertEqual(attr.string_table_indices(), TARGET)

    def test_prim_string_table_indices(self):
        geo = get_obj_geo("test_prim_string_table_indices")

        TARGET = (0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4)

        attr = geo.findPrimAttrib("test")

        self.assertEqual(attr.string_table_indices(), TARGET)

    def test_vertex_string_attrib_values(self):
        geo = get_obj_geo("test_vertex_string_attrib_values")

        TARGET = ('vertex0', 'vertex1', 'vertex2', 'vertex3', 'vertex4', 'vertex5', 'vertex6', 'vertex7')

        self.assertEqual(geo.vertex_string_attrib_values("test"), TARGET)

    def test_set_vertex_string_attrib_values(self):
        TARGET = ('vertex0', 'vertex1', 'vertex2', 'vertex3', 'vertex4')

        geo = get_obj_geo_copy("test_set_vertex_string_attrib_values")
        attr = geo.findVertexAttrib("test")

        geo.set_vertex_string_attrib_values("test", TARGET)

        vals = []

        for prim in geo.prims():
            vals.extend([vert.attribValue(attr) for vert in prim.vertices()])

        self.assertEqual(tuple(vals), TARGET)

    def test_set_vertex_string_attrib_valuesInvalidAttribute(self):
        TARGET = ('vertex0', 'vertex1', 'vertex2', 'vertex3', 'vertex4')

        geo = get_obj_geo_copy("test_set_vertex_string_attrib_values")

        with self.assertRaises(hou.OperationFailed):
            geo.set_vertex_string_attrib_values("thing", TARGET)

    def test_set_vertex_string_attrib_valuesInvalidAttributeType(self):
        TARGET = ('vertex0', 'vertex1', 'vertex2', 'vertex3', 'vertex4')

        geo = get_obj_geo_copy("test_set_vertex_string_attrib_values")

        with self.assertRaises(hou.OperationFailed):
            geo.set_vertex_string_attrib_values("notstring", TARGET)

    def test_setPrimStringAttribValuesInvalidAttributeSize(self):
        TARGET = ('vertex0', 'vertex1', 'vertex2', 'vertex3')

        geo = get_obj_geo_copy("test_set_vertex_string_attrib_values")

        with self.assertRaises(hou.OperationFailed):
            geo.set_vertex_string_attrib_values("test", TARGET)

    def test_set_shared_point_string_attrib(self):
        TARGET = ["point0"]*5
        geo = hou.Geometry()
        geo.create_n_points(5)
        attr = geo.addAttrib(hou.attribType.Point, "test", "")

        geo.set_shared_point_string_attrib(attr.name(), "point0")

        vals = [point.attribValue(attr) for point in geo.points()]

        self.assertEqual(vals, TARGET)

    def test_set_shared_point_string_attribGroup(self):
        TARGET = ["point0"]*5 + [""]*5

        geo = hou.Geometry()

        attr = geo.addAttrib(hou.attribType.Point, "test", "")

        geo.create_n_points(5)
        group = geo.createPointGroup("group1")

        for point in geo.points():
            group.add(point)

        geo.create_n_points(5)

        geo.set_shared_point_string_attrib(attr.name(), "point0", group)

        vals = [point.attribValue(attr) for point in geo.points()]

        self.assertEqual(vals, TARGET)

    def test_set_shared_prim_string_attrib(self):
        TARGET = ["value"]*5

        geo = get_obj_geo_copy("test_set_shared_prim_string_attrib")

        attr = geo.findPrimAttrib("test")

        geo.set_shared_prim_string_attrib(attr.name(), "value")

        vals = [prim.attribValue(attr) for prim in geo.prims()]

        self.assertEqual(vals, TARGET)

    def test_set_shared_prim_string_attribGroup(self):
        TARGET = ["value"]*3 + ["", ""]

        geo = get_obj_geo_copy("test_set_shared_prim_string_attrib")

        attr = geo.findPrimAttrib("test")

        group = geo.findPrimGroup("group1")

        geo.set_shared_prim_string_attrib(attr.name(), "value", group)

        vals = [prim.attribValue(attr) for prim in geo.prims()]

        self.assertEqual(vals, TARGET)

    def test_has_edge(self):
        geo = get_obj_geo("test_has_edge")

        face = geo.iterPrims()[0]

        p0 = geo.iterPoints()[0]
        p1 = geo.iterPoints()[1]

        self.assertTrue(face.has_edge(p0, p1))

    def test_has_edgeFail(self):
        geo = get_obj_geo("test_has_edge")

        face = geo.iterPrims()[0]

        p0 = geo.iterPoints()[0]
        p2 = geo.iterPoints()[2]

        self.assertTrue(face.has_edge(p0, p2))

    def test_shared_edges(self):
        geo = get_obj_geo("test_shared_edges")

        pr0, pr1 = geo.prims()

        edges = pr0.shared_edges(pr1)

        pt2 = geo.iterPoints()[2]
        pt3 = geo.iterPoints()[3]

        edge = geo.findEdge(pt2, pt3)

        self.assertEqual(edges, (edge,))

    def test_insert_vertex(self):
        geo = get_obj_geo_copy("test_insert_vertex")

        face = geo.iterPrims()[0]

        pt = geo.create_point_at_position(hou.Vector3(0.5, 0, 0.5))

        face.insert_vertex(pt, 2)

        self.assertEqual(face.vertex(2).point(), pt)

    def test_insert_vertexNegativeIndex(self):
        geo = get_obj_geo_copy("test_insert_vertex")

        face = geo.iterPrims()[0]

        pt = geo.create_point_at_position(hou.Vector3(0.5, 0, 0.5))

        with self.assertRaises(IndexError):
            face.insert_vertex(pt, -1)

    def test_insert_vertexInvalidIndex(self):
        geo = get_obj_geo_copy("test_insert_vertex")

        face = geo.iterPrims()[0]

        pt = geo.create_point_at_position(hou.Vector3(0.5, 0, 0.5))

        with self.assertRaises(IndexError):
            face.insert_vertex(pt, 10)

    def test_delete_vertex(self):
        geo = get_obj_geo_copy("test_delete_vertex")

        face = geo.iterPrims()[0]

        face.delete_vertex(3)

        self.assertEqual(len(face.vertices()), 3)

    def test_delete_vertexNegativeIndex(self):
        geo = get_obj_geo_copy("test_delete_vertex")

        face = geo.iterPrims()[0]

        with self.assertRaises(IndexError):
            face.delete_vertex(-1)

    def test_delete_vertexInvalidIndex(self):
        geo = get_obj_geo_copy("test_delete_vertex")

        face = geo.iterPrims()[0]

        with self.assertRaises(IndexError):
            face.delete_vertex(10)

    def test_set_point(self):
        geo = get_obj_geo_copy("test_set_point")

        face = geo.iterPrims()[0]
        pt = geo.iterPoints()[4]

        face.set_point(3, pt)

        self.assertEqual(face.vertex(3).point().number(), 4)

    def test_set_point_negative_index(self):
        geo = get_obj_geo_copy("test_set_point")

        face = geo.iterPrims()[0]
        pt = geo.iterPoints()[4]

        with self.assertRaises(IndexError):
            face.set_point(-1, pt)

    def test_set_point_invalid_index(self):
        geo = get_obj_geo_copy("test_set_point")

        face = geo.iterPrims()[0]
        pt = geo.iterPoints()[4]

        with self.assertRaises(IndexError):
            face.set_point(10, pt)

    def test_bary_center(self):
        TARGET = hou.Vector3(1.5, 1, -1)
        geo = get_obj_geo_copy("test_bary_center")

        prim = geo.iterPrims()[0]

        self.assertEqual(prim.bary_center(), TARGET)

    def test_primitive_area(self):
        TARGET = 4.375
        geo = get_obj_geo_copy("test_primitive_area")

        prim = geo.iterPrims()[0]

        self.assertEqual(prim.area(), TARGET)

    def test_perimeter(self):
        TARGET = 6.5
        geo = get_obj_geo_copy("test_perimeter")

        prim = geo.iterPrims()[0]

        self.assertEqual(prim.perimeter(), TARGET)

    def test_volume(self):
        TARGET = 0.1666666716337204
        geo = get_obj_geo_copy("test_volume")

        prim = geo.iterPrims()[0]

        self.assertEqual(prim.volume(), TARGET)

    def test_reverse_prim(self):
        TARGET = hou.Vector3(0, -1, 0)
        geo = get_obj_geo_copy("test_reverse_prim")

        prim = geo.iterPrims()[0]
        prim.reverse()

        self.assertEqual(prim.normal(), TARGET)

    def test_make_unique(self):
        TARGET = 28
        geo = get_obj_geo_copy("test_make_unique")

        prim = geo.iterPrims()[4]
        prim.make_unique()

        self.assertEqual(len(geo.iterPoints()), TARGET)

    def test_prim_bounding_box(self):
        TARGET = hou.BoundingBox(-0.75, 0, -0.875, 0.75, 1.5, 0.875)
        geo = get_obj_geo_copy("test_prim_bounding_box")

        prim = geo.iterPrims()[0]

        self.assertEqual(prim.boundingBox(), TARGET)

    def test_compute_point_normals(self):
        geo = get_obj_geo_copy("test_compute_point_normals")

        geo.compute_point_normals()

        self.assertNotEqual(geo.findPointAttrib("N"), None)

    def test_add_point_normal_attribute(self):
        geo = get_obj_geo_copy("test_add_point_normal_attribute")

        self.assertNotEqual(geo.addPointNormals(), None)

    def test_add_point_velocity_attribute(self):
        geo = get_obj_geo_copy("test_add_point_velocity_attribute")

        self.assertNotEqual(geo.addPointVelocity(), None)

    def test_add_color_attribute_point(self):
        geo = get_obj_geo_copy("test_add_color_attribute")

        result = geo.add_color_attribute(hou.attribType.Point)

        self.assertNotEqual(result, None)

    def test_add_color_attribute_prim(self):
        geo = get_obj_geo_copy("test_add_color_attribute")

        result = geo.add_color_attribute(hou.attribType.Prim)

        self.assertNotEqual(result, None)

    def test_add_color_attribute_vertex(self):
        geo = get_obj_geo_copy("test_add_color_attribute")

        result = geo.add_color_attribute(hou.attribType.Vertex)

        self.assertNotEqual(result, None)

    def test_add_color_attribute_point(self):
        geo = get_obj_geo_copy("test_add_color_attribute")

        with self.assertRaises(hou.TypeError):
            geo.add_color_attribute(hou.attribType.Global)

    def test_convex(self):
        geo = get_obj_geo_copy("test_convex")

        geo.convex()

        self.assertEqual(len(geo.iterPrims()), 162)

        verts = [vert for prim in geo.prims() for vert in prim.vertices()]
        self.assertEqual(len(verts), 486)

    def test_clip(self):
        geo = get_obj_geo_copy("test_clip")

        origin = hou.Vector3(0, 0, 0)

        direction = hou.Vector3(-0.5, 0.6, -0.6)

        geo.clip(origin, direction, 0.5)

        self.assertEqual(len(geo.iterPrims()), 42)

        self.assertEqual(len(geo.iterPoints()), 60)

    def test_clip_below(self):
        geo = get_obj_geo_copy("test_clip_below")

        origin = hou.Vector3(0, -0.7, -0.9)

        direction = hou.Vector3(-0.6, 0.1, -0.8)

        geo.clip(origin, direction, 0.6, below=True)

        self.assertEqual(len(geo.iterPrims()), 61)

        self.assertEqual(len(geo.iterPoints()), 81)

    def test_clip_group(self):
        geo = get_obj_geo_copy("test_clip_group")

        group = geo.primGroups()[0]

        origin = hou.Vector3(-1.3, -1.5, 1.2)

        direction = hou.Vector3(0.8, 0.02, 0.5)

        geo.clip(origin, direction, -0.3, group=group)

        self.assertEqual(len(geo.iterPrims()), 74)

        self.assertEqual(len(geo.iterPoints()), 98)

    def test_destroyEmpty_point_groups(self):
        geo = hou.Geometry()

        geo.createPointGroup("empty")

        geo.destroy_empty_groups(hou.attribType.Point)

        self.assertEqual(len(geo.pointGroups()), 0)

    def test_destroyEmpty_prim_groups(self):
        geo = hou.Geometry()

        geo.createPrimGroup("empty")

        geo.destroy_empty_groups(hou.attribType.Prim)

        self.assertEqual(len(geo.primGroups()), 0)

    def test_destroy_unused_points(self):
        geo = get_obj_geo_copy("test_destroy_unused_points")

        geo.destroy_unused_points()

        self.assertEqual(len(geo.iterPoints()), 20)

    def test_destroy_unused_points_group(self):
        geo = get_obj_geo_copy("test_destroy_unused_points_group")

        group = geo.pointGroups()[0]

        geo.destroy_unused_points(group)

        self.assertEqual(len(geo.iterPoints()), 3729)

    def test_consolidate_points(self):
        geo = get_obj_geo_copy("test_consolidate_points")

        geo.consolidate_points()

        self.assertEqual(len(geo.iterPoints()), 100)

    def test_consolidate_points_dist(self):
        geo = get_obj_geo_copy("test_consolidate_points_dist")

        geo.consolidate_points(3)

        self.assertEqual(len(geo.iterPoints()), 16)

    def test_consolidate_points_group(self):
        geo = get_obj_geo_copy("test_consolidate_points_group")

        group = geo.pointGroups()[0]

        geo.consolidate_points(group=group)

        self.assertEqual(len(geo.iterPoints()), 212)

    def test_unique_points(self):
        geo = get_obj_geo_copy("test_unique_points")

        geo.unique_points()

        self.assertEqual(len(geo.iterPoints()), 324)

    def test_unique_points_point_group(self):
        geo = get_obj_geo_copy("test_unique_points_point_group")

        group = geo.pointGroups()[0]
        geo.unique_points(group)

        self.assertEqual(len(geo.iterPoints()), 195)

    def test_rename_point_group(self):
        geo = get_obj_geo_copy("test_rename_point_group")

        group = geo.pointGroups()[0]

        result = geo.rename_group(group, "test_group")

        self.assertTrue(result is not None)
        self.assertTrue(result.name() == "test_group")


    def test_rename_point_group_same_name(self):
        geo = get_obj_geo_copy("test_rename_point_group")

        group = geo.pointGroups()[0]
        name = group.name()

        with self.assertRaises(hou.OperationFailed):
            geo.rename_group(group, name)

    def test_rename_prim_group(self):
        geo = get_obj_geo_copy("test_rename_prim_group")

        group = geo.primGroups()[0]

        result = geo.rename_group(group, "test_group")

        self.assertTrue(result is not None)
        self.assertTrue(result.name() == "test_group")

    def test_rename_prim_group_same_name(self):
        geo = get_obj_geo_copy("test_rename_prim_group")

        group = geo.primGroups()[0]
        name = group.name()

        with self.assertRaises(hou.OperationFailed):
            geo.rename_group(group, name)

    def test_rename_edge_group(self):
        geo = get_obj_geo_copy("test_rename_edge_group")

        group = geo.edgeGroups()[0]

        result = geo.rename_group(group, "test_group")

        self.assertTrue(result is not None)
        self.assertTrue(result.name() == "test_group")

    def test_rename_edge_group_same_name(self):
        geo = get_obj_geo_copy("test_rename_edge_group")

        group = geo.edgeGroups()[0]
        name = group.name()

        with self.assertRaises(hou.OperationFailed):
            geo.rename_group(group, name)

    def test_group_bounding_box_point(self):
        TARGET = hou.BoundingBox(-4, 0, -1, -2, 0, 2)

        geo = get_obj_geo("test_group_bounding_box_point")

        group = geo.pointGroups()[0]
        bbox = group.boundingBox()

        self.assertEqual(bbox, TARGET)

    def test_group_bounding_box_prim(self):
        TARGET = hou.BoundingBox(-5, 0, -4, 4, 0, 5)

        geo = get_obj_geo("test_group_bounding_box_prim")

        group = geo.primGroups()[0]
        bbox = group.boundingBox()

        self.assertEqual(bbox, TARGET)

    def test_group_bounding_box_edge(self):
        TARGET = hou.BoundingBox(-5, 0, -5, 4, 0, 5)

        geo = get_obj_geo("test_group_bounding_box_edge")

        group = geo.edgeGroups()[0]
        bbox = group.boundingBox()

        self.assertEqual(bbox, TARGET)

    def test_point_group_size(self):
        geo = get_obj_geo("test_point_group_size")

        group = geo.pointGroups()[0]

        self.assertEqual(group.size(), 12)
        self.assertEqual(len(group), 12)

    def test_prim_group_size(self):
        geo = get_obj_geo("test_prim_group_size")

        group = geo.primGroups()[0]

        self.assertEqual(group.size(), 39)
        self.assertEqual(len(group), 39)

    def test_edge_group_size(self):
        geo = get_obj_geo("test_edge_group_size")

        group = geo.edgeGroups()[0]

        self.assertEqual(group.size(), 52)
        self.assertEqual(len(group), 52)

    def test_toggle_point(self):
        geo = get_obj_geo_copy("test_toggle_point")

        group = geo.pointGroups()[0]
        point = geo.iterPoints()[0]

        group.toggle(point)

        self.assertTrue(group.contains(point))

    def test_toggle_prim(self):
        geo = get_obj_geo_copy("test_toggle_prim")

        group = geo.primGroups()[0]
        prim = geo.iterPrims()[0]

        group.toggle(prim)

        self.assertTrue(group.contains(prim))

    def test_toggle_entries_point(self):
        geo = get_obj_geo_copy("test_toggle_entries_point")

        vals = geo.globPoints(" ".join([str(val) for val in range(1, 100, 2)]))

        group = geo.pointGroups()[0]
        group.toggle_entries()

        self.assertEquals(group.points(), vals)

    def test_toggle_entries_prim(self):
        geo = get_obj_geo_copy("test_toggle_entries_prim")

        vals = geo.globPrims(" ".join([str(val) for val in range(0, 100, 2)]))

        group = geo.primGroups()[0]
        group.toggle_entries()

        self.assertEquals(group.prims(), vals)

    def test_toggle_entries_edge(self):
        geo = get_obj_geo_copy("test_toggle_entries_edge")

        group = geo.edgeGroups()[0]
        group.toggle_entries()

        self.assertEquals(len(group.edges()),  20)

    def test_copy_point_group(self):
        geo = get_obj_geo_copy("test_copy_point_group")

        group = geo.pointGroups()[0]

        new_group = group.copy("new_group")

        self.assertEquals(group.points(), new_group.points())

    def test_copy_point_group_same_name(self):
        geo = get_obj_geo_copy("test_copy_point_group")

        group = geo.pointGroups()[0]

        with self.assertRaises(hou.OperationFailed):
            group.copy(group.name())

    def test_copy_point_group_existing(self):
        geo = get_obj_geo_copy("test_copy_point_group_existing")

        group = geo.pointGroups()[-1]

        other_group = geo.pointGroups()[0]

        with self.assertRaises(hou.OperationFailed):
            group.copy(other_group.name())

    def test_copy_prim_group(self):
        geo = get_obj_geo_copy("test_copy_prim_group")

        group = geo.primGroups()[0]

        new_group = group.copy("new_group")

        self.assertEquals(group.prims(), new_group.prims())

    def test_copy_prim_group_same_name(self):
        geo = get_obj_geo_copy("test_copy_prim_group")

        group = geo.primGroups()[0]

        with self.assertRaises(hou.OperationFailed):
            group.copy(group.name())

    def test_copy_prim_group_existing(self):
        geo = get_obj_geo_copy("test_copy_prim_group_existing")

        group = geo.primGroups()[-1]

        other_group = geo.primGroups()[0]

        with self.assertRaises(hou.OperationFailed):
            group.copy(other_group.name())

    def test_point_group_contains_any(self):
        geo = get_obj_geo_copy("test_point_group_contains_any")

        group1 = geo.pointGroups()[0]
        group2 = geo.pointGroups()[1]

        self.assertTrue(group1.containsAny(group2))

    def test_point_group_contains_any_False(self):
        geo = get_obj_geo_copy("test_point_group_contains_any_False")

        group1 = geo.pointGroups()[0]
        group2 = geo.pointGroups()[1]

        self.assertFalse(group1.containsAny(group2))

    def test_prim_group_contains_any(self):
        geo = get_obj_geo_copy("test_prim_group_contains_any")

        group1 = geo.primGroups()[0]
        group2 = geo.primGroups()[1]

        self.assertTrue(group1.containsAny(group2))

    def test_prim_group_contains_any_False(self):
        geo = get_obj_geo_copy("test_prim_group_contains_any_False")

        group1 = geo.primGroups()[0]
        group2 = geo.primGroups()[1]

        self.assertFalse(group1.containsAny(group2))

    def test_convert_prim_to_point_group(self):
        geo = get_obj_geo_copy("test_convert_prim_to_point_group")

        group = geo.primGroups()[0]

        new_group = group.convert_to_point_group()

        self.assertEqual(len(new_group.points()), 12)

        # Check source group was deleted.
        self.assertEqual(len(geo.primGroups()), 0)

    def test_convert_prim_to_point_group_with_name(self):
        geo = get_obj_geo_copy("test_convert_prim_to_point_group")

        group = geo.primGroups()[0]

        new_group = group.convert_to_point_group("new_group")

        self.assertEqual(new_group.name(), "new_group")

    def test_convert_prim_to_point_group_no_destroy(self):
        geo = get_obj_geo_copy("test_convert_prim_to_point_group")

        group = geo.primGroups()[0]

        new_group = group.convert_to_point_group(destroy=False)

        # Check source group wasn't deleted.
        self.assertEqual(len(geo.primGroups()), 1)

    def test_convert_point_to_prim_group(self):
        geo = get_obj_geo_copy("test_convert_point_to_prim_group")

        group = geo.pointGroups()[0]

        new_group = group.convert_to_prim_group()

        self.assertEqual(len(new_group.prims()), 5)

        # Check source group was deleted.
        self.assertEqual(len(geo.pointGroups()), 0)

    def test_convert_point_to_prim_group_with_name(self):
        geo = get_obj_geo_copy("test_convert_point_to_prim_group")

        group = geo.pointGroups()[0]

        new_group = group.convert_to_prim_group("new_group")

        self.assertEqual(new_group.name(), "new_group")

    def test_convert_point_to_prim_group_no_destroy(self):
        geo = get_obj_geo_copy("test_convert_point_to_prim_group")

        group = geo.pointGroups()[0]

        new_group = group.convert_to_prim_group(destroy=False)

        # Check source group wasn't deleted.
        self.assertEqual(len(geo.primGroups()), 1)

    # =========================================================================
    # UNGROUPED POINTS
    # =========================================================================

    def test_has_ungrouped_points(self):
        geo = get_obj_geo("test_has_ungrouped_points")

        self.assertTrue(geo.has_ungrouped_points())

    def test_has_ungrouped_points_False(self):
        geo = get_obj_geo("test_has_ungrouped_points_False")

        self.assertFalse(geo.has_ungrouped_points())

    def test_group_ungrouped_points(self):
        geo = get_obj_geo_copy("test_group_ungrouped_points")

        group = geo.group_ungrouped_points("ungrouped")

        self.assertEquals(len(group.points()), 10)

    def test_group_ungrouped_pointsExistingName(self):
        geo = get_obj_geo_copy("test_group_ungrouped_points")

        with self.assertRaises(hou.OperationFailed):
            geo.group_ungrouped_points("group1")

    def test_group_ungrouped_pointsNoName(self):
        geo = get_obj_geo_copy("test_group_ungrouped_points")

        with self.assertRaises(hou.OperationFailed):
            geo.group_ungrouped_points("")

    def test_group_ungrouped_points_False(self):
        geo = get_obj_geo_copy("test_group_ungrouped_points_False")

        group = geo.group_ungrouped_points("ungrouped")

        self.assertEquals(group, None)

    # =========================================================================
    # UNGROUPED PRIMS
    # =========================================================================

    def test_has_ungrouped_prims(self):
        geo = get_obj_geo("test_has_ungrouped_prims")

        self.assertTrue(geo.has_ungrouped_prims())

    def test_has_ungrouped_prims(self):
        geo = get_obj_geo("test_has_ungrouped_prims_False")

        self.assertFalse(geo.has_ungrouped_prims())

    def test_group_ungrouped_prims(self):
        geo = get_obj_geo_copy("test_group_ungrouped_prims")

        group = geo.group_ungrouped_prims("ungrouped")

        self.assertEquals(len(group.prims()), 3)

    def test_group_ungrouped_primsExistingName(self):
        geo = get_obj_geo_copy("test_group_ungrouped_prims")

        with self.assertRaises(hou.OperationFailed):
            geo.group_ungrouped_prims("group1")

    def test_group_ungrouped_primsNoName(self):
        geo = get_obj_geo_copy("test_group_ungrouped_prims")

        with self.assertRaises(hou.OperationFailed):
            geo.group_ungrouped_prims("")

    def test_group_ungrouped_primsFalse(self):
        geo = get_obj_geo_copy("test_group_ungrouped_prims_False")

        group = geo.group_ungrouped_prims("ungrouped")

        self.assertEquals(group, None)

    # =========================================================================
    # BOUNDING BOXES
    # =========================================================================

    def test_is_inside(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)
        bbox2 = hou.BoundingBox(-1, -1, -1, 1, 1, 1)

        self.assertTrue(bbox1.is_inside(bbox2))

    def test_is_insideFail(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)
        bbox2 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

        self.assertFalse(bbox1.is_inside(bbox2))

    def test_intersects(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)
        bbox2 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

        self.assertTrue(bbox1.intersects(bbox2))

    def test_intersectsFail(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, -0.1, -0.1, -0.1)
        bbox2 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

        self.assertFalse(bbox1.intersects(bbox2))

    def test_compute_intersection(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)
        bbox2 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

        self.assertTrue(bbox1.compute_intersection(bbox2))

        self.assertEqual(bbox1.minvec(), hou.Vector3())
        self.assertEqual(bbox1.maxvec(), hou.Vector3(0.5, 0.5, 0.5))

    def test_compute_intersectionFail(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, -0.1, -0.1, -0.1)
        bbox2 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

        self.assertFalse(bbox1.compute_intersection(bbox2))

    def test_expand_bounds(self):
        bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)
        bbox.expand_bounds(1, 1, 1)

        self.assertEqual(bbox.minvec(), hou.Vector3(-2, -2.75, -4))
        self.assertEqual(bbox.maxvec(), hou.Vector3(2, 2.75, 4))

    def test_add_to_min(self):
        bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)
        bbox.add_to_min(hou.Vector3(1, 0.25, 1))

        self.assertEqual(bbox.minvec(), hou.Vector3(0, -1.5, -2))

    def test_add_to_max(self):
        bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)
        bbox.add_to_max(hou.Vector3(2, 0.25, 1))

        self.assertEqual(bbox.maxvec(), hou.Vector3(3, 2, 4))

    def test_area(self):
        bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)

        self.assertEqual(bbox.area(), 80)

    def test_bounding_box_volume(self):
        bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)

        self.assertEqual(bbox.volume(), 42)

    # =========================================================================
    # PARMS
    # =========================================================================

    def test_is_vector(self):
        node = OBJ.node("test_is_vector/node")
        parm = node.parmTuple("vec")

        self.assertTrue(parm.is_vector())

    def test_is_vectorFalse(self):
        node = OBJ.node("test_is_vector/node")
        parm = node.parmTuple("not_vec")

        self.assertFalse(parm.is_vector())

    def test_eval_as_vector2(self):
        node = OBJ.node("test_eval_as_vector/node")
        parm = node.parmTuple("vec2")

        self.assertEqual(parm.eval_as_vector(), hou.Vector2(1,2))

    def test_eval_as_vector3(self):
        node = OBJ.node("test_eval_as_vector/node")
        parm = node.parmTuple("vec3")

        self.assertEqual(parm.eval_as_vector(), hou.Vector3(3,4,5))

    def test_eval_as_vector4(self):
        node = OBJ.node("test_eval_as_vector/node")
        parm = node.parmTuple("vec4")

        self.assertEqual(parm.eval_as_vector(), hou.Vector4(6,7,8,9))

    def test_eval_as_vectorFail(self):
        node = OBJ.node("test_eval_as_vector/node")
        parm = node.parmTuple("not_vec")

        with self.assertRaises(hou.Error):
            parm.eval_as_vector()

    def test_is_color(self):
        node = OBJ.node("test_is_color/node")
        parm = node.parmTuple("color")

        self.assertTrue(parm.is_color())

    def test_is_colorFalse(self):
        node = OBJ.node("test_is_color/node")
        parm = node.parmTuple("not_color")

        self.assertFalse(parm.is_color())

    def test_eval_as_color(self):
        node = OBJ.node("test_eval_as_color/node")
        parm = node.parmTuple("color")

        self.assertEqual(parm.eval_as_color(), hou.Color(0,0.5,0.5))

    def test_eval_as_colorFail(self):
        node = OBJ.node("test_eval_as_color/node")
        parm = node.parmTuple("not_color")

        with self.assertRaises(hou.Error):
            parm.eval_as_color()

    def test_eval_as_stripSingle(self):
        node = OBJ.node("test_eval_as_strip/node")
        parm = node.parm("strip_normal")

        TARGET = (False, True, False, False)

        self.assertEqual(
            parm.eval_as_strip(),
            TARGET
        )

    def test_eval_as_stripToggle(self):
        node = OBJ.node("test_eval_as_strip/node")
        parm = node.parm("strip_toggle")

        TARGET = (True, False, True, True)

        self.assertEqual(
            parm.eval_as_strip(),
            TARGET
        )


    def test_eval_strip_as_stringSingle(self):
        node = OBJ.node("test_eval_as_strip/node")
        parm = node.parm("strip_normal")

        TARGET = ('bar',)

        self.assertEqual(
            parm.eval_strip_as_string(),
            TARGET
        )

    def test_eval_strip_as_stringToggle(self):
        node = OBJ.node("test_eval_as_strip/node")
        parm = node.parm("strip_toggle")

        TARGET = ('foo', 'hello', 'world')

        self.assertEqual(
            parm.eval_strip_as_string(),
            TARGET
        )


    # =========================================================================
    # MULTIPARMS
    # =========================================================================

    def test_is_multiparm(self):
        node = OBJ.node("test_is_multiparm/object_merge")
        parm = node.parm("numobj")

        self.assertTrue(parm.is_multiparm())

        parmTuple = node.parmTuple("numobj")
        self.assertTrue(parmTuple.is_multiparm())

    def test_is_multiparmFalse(self):
        node = OBJ.node("test_is_multiparm/object_merge")
        parm = node.parm("objpath1")

        self.assertFalse(parm.is_multiparm())

        parmTuple = node.parmTuple("objpath1")
        self.assertFalse(parmTuple.is_multiparm())

    def test_get_multiparm_instances_per_item(self):
        node = OBJ.node("test_get_multiparm_instances_per_item/object_merge")
        parm = node.parm("numobj")

        self.assertEqual(parm.get_multiparm_instances_per_item(), 4)

        parm_tuple = node.parmTuple("numobj")
        self.assertEqual(parm_tuple.get_multiparm_instances_per_item(), 4)

    def test_get_multiparm_start_offset0(self):
        node = OBJ.node("test_get_multiparm_start_offset/add")
        parm = node.parm("points")

        self.assertEqual(parm.get_multiparm_start_offset(), 0)

        parm_tuple = node.parmTuple("points")
        self.assertEqual(parm_tuple.get_multiparm_start_offset(), 0)

    def test_get_multiparm_start_offset1(self):
        node = OBJ.node("test_get_multiparm_start_offset/object_merge")
        parm = node.parm("numobj")

        self.assertEqual(parm.get_multiparm_start_offset(), 1)

        parm_tuple = node.parmTuple("numobj")
        self.assertEqual(parm_tuple.get_multiparm_start_offset(), 1)

    def test_get_multiparm_instance_index(self):
        TARGET = (2, )

        node = OBJ.node("test_get_multiparm_instance_index/object_merge")
        parm = node.parm("objpath2")

        self.assertEqual(parm.get_multiparm_instance_index(), TARGET)

        parm_tuple = node.parmTuple("objpath2")

        self.assertEqual(parm_tuple.get_multiparm_instance_index(), TARGET)

    def test_get_multiparm_instance_index_fail(self):
        node = OBJ.node("test_get_multiparm_instance_index/object_merge")
        parm = node.parm("numobj")

        with self.assertRaises(hou.OperationFailed):
            parm.get_multiparm_instance_index()

        parm_tuple = node.parmTuple("numobj")

        with self.assertRaises(hou.OperationFailed):
            parm_tuple.get_multiparm_instance_index()

    def test_get_multiparm_instances(self):
        node = OBJ.node("test_get_multiparm_instances/null1")

        TARGET = (
            (
                node.parm("foo1"),
                node.parmTuple("bar1"),
                node.parm("hello1")
            ),
            (
                node.parm("foo2"),
                node.parmTuple("bar2"),
                node.parm("hello2")
            ),
        )

        parmTuple = node.parmTuple("things")

        instances = parmTuple.get_multiparm_instances()

        self.assertEqual(instances, TARGET)

    def test_get_multiparm_instance_values(self):
        node = OBJ.node("test_get_multiparm_instance_values/null1")

        TARGET = (
            (
                1,
                (2.0, 3.0, 4.0),
                "foo"
            ),
            (
                5,
                (6.0, 7.0, 8.0),
                "bar"
            ),
        )

        parmTuple = node.parmTuple("things")

        values = parmTuple.get_multiparm_instance_values()

        self.assertEqual(values, TARGET)

    # =========================================================================
    # NODES AND NODE TYPES
    # =========================================================================

    def test_disconnect_all_outputs(self):
        node = OBJ.node("test_disconnect_all_outputs/file")

        node.disconnect_all_outputs()

        self.assertEqual(len(node.outputs()), 0)

    def test_disconnect_all_inputs(self):
        node = OBJ.node("test_disconnect_all_inputs/merge")

        node.disconnect_all_inputs()

        self.assertEqual(len(node.inputs()), 0)

    def is_contained_by(self):
        node = OBJ.node("is_contained_by")

        box = node.node("box")

        self.assertTrue(box.isContainedBy(node))

    def is_contained_by_False(self):
        node = OBJ.node("is_contained_by")

        self.assertFalse(node.isContainedBy(hou.node("/shop")))

    def test_author_name(self):
        node = OBJ.node("test_author_name")

        self.assertEqual(node.author_name(), "gthompson")

    def test_typeSetIcon(self):
        nodeType = hou.nodeType(hou.objNodeTypeCategory(), "geo")
        nodeType.set_icon("SOP_box")

        self.assertEqual(nodeType.icon(), "SOP_box")

    def test_set_default_icon(self):
        node_type = hou.nodeType(hou.objNodeTypeCategory(), "geo")
        node_type.set_icon("SOP_box")

        node_type.set_default_icon()

        self.assertEqual(node_type.icon(), "OBJ_geo")

    def test_typeIsPython(self):
        nodeType = hou.nodeType(hou.sopNodeTypeCategory(), "tableimport")

        self.assertTrue(nodeType.is_node_type_python())

    def test_typeIsNotPython(self):
        nodeType = hou.nodeType(hou.sopNodeTypeCategory(), "file")

        self.assertFalse(nodeType.is_node_type_python())

    def test_typeIsSubnet(self):
        nodeType = hou.nodeType(hou.objNodeTypeCategory(), "subnet")

        self.assertTrue(nodeType.is_node_type_subnet())

    def test_typeIsNotSubnet(self):
        nodeType = hou.nodeType(hou.objNodeTypeCategory(), "geo")

        self.assertFalse(nodeType.is_node_type_subnet())

    # =========================================================================
    # VECTORS AND MATRICES
    # =========================================================================

    def test_v3ComponentAlong(self):
        v3 = hou.Vector3(1, 2, 3)
        self.assertEqual(
            v3.component_along(hou.Vector3(0, 0, 15)),
            3.0
        )

    def test_v3Project(self):
        v3 = hou.Vector3(-1.3, 0.5, 7.6)
        proj = v3.project(hou.Vector3(2.87, 3.1, -0.5))

        result = hou.Vector3(-0.948531, -1.02455, 0.165249)

        self.assertTrue(proj.isAlmostEqual(result))

    def test_v2IsNan(self):
        nan = float('nan')
        v2 = hou.Vector2(nan, 1)

        self.assertTrue(v2.is_nan())

    def test_v3IsNan(self):
        nan = float('nan')
        v3 = hou.Vector3(6.5, 1, nan)

        self.assertTrue(v3.is_nan())

    def test_v3IsNan(self):
        nan = float('nan')
        v4 = hou.Vector4(-4, 5, -0, nan)

        self.assertTrue(v4.is_nan())

    def test_get_vector_dual(self):
        TARGET = hou.Matrix3(((0, -3, 2), (3, 0, -1), (-2, 1, 0)))

        v3 = hou.Vector3(1, 2, 3)

        self.assertEqual(v3.get_vector_dual(), TARGET)

    def test_m3IdentIsIdentity(self):
        m3 = hou.Matrix3()
        m3.setToIdentity()

        self.assertTrue(m3.is_identity_matrix())

    def test_m3ZeroIsNotIdentity(self):
        m3 = hou.Matrix3()

        self.assertFalse(m3.is_identity_matrix())

    def test_m4IdentIsIdentity(self):
        m4 = hou.Matrix4()
        m4.setToIdentity()

        self.assertTrue(m4.is_identity_matrix())

    def test_m4ZeroIsNotIdentity(self):
        m4 = hou.Matrix4()

        self.assertFalse(m4.is_identity_matrix())

    def test_m4SetTranslates(self):
        translates = hou.Vector3(1,2,3)
        identity = hou.hmath.identityTransform()
        identity.set_matrix_translates(translates)

        self.assertEqual(
            identity.extractTranslates(),
            translates
        )

    def test_build_lookat_matrix(self):
        TARGET = hou.Matrix3(
            (
                (0.70710678118654746, -0.0, 0.70710678118654746),
                (0.0, 1.0, 0.0),
                (-0.70710678118654746, 0.0, 0.70710678118654746)
            )
        )

        lookAt = hou.hmath.build_lookat_matrix(
            hou.Vector3(0, 0, 1),
            hou.Vector3(1, 0, 0),
            hou.Vector3(0, 1, 0)
        )

        self.assertEqual(lookAt, TARGET)

    def test_build_instance_matrix(self):
        TARGET = hou.Matrix4(
            (
                (
                    1.0606601717798214,
                    -1.0606601717798214,
                    0.0,
                    0.0
                ),
                (
                    0.61237243569579436,
                    0.61237243569579436,
                    -1.2247448713915889,
                    0.0
                ),
                (
                    0.86602540378443882,
                    0.86602540378443882,
                    0.86602540378443882,
                    0.0
                ),
                (
                    -1.0,
                    2.0,
                    4.0,
                    1.0
                )
            )
        )

        mat = hou.hmath.build_instance_matrix(
            hou.Vector3(-1, 2, 4),
            hou.Vector3(1, 1, 1),
            pscale = 1.5,
            up=hou.Vector3(1, 1, -1)
        )

        self.assertEqual(mat, TARGET)

    def test_build_instance_matrixOrient(self):
        TARGET = hou.Matrix4(
            (
                (
                    0.33212996389891691,
                    0.3465703971119134,
                    -0.87725631768953083,
                    0.0
                ),
                (
                    -0.53068592057761732,
                    0.83754512635379064,
                    0.1299638989169675,
                    0.0
                ),
                (
                    0.77978339350180514,
                    0.42238267148014441,
                    0.46209386281588438,
                    0.0
                ),
                (
                    -1.0,
                    2.0,
                    4.0,
                    1.0
                )
            )
        )

        mat = hou.hmath.build_instance_matrix(
            hou.Vector3(-1, 2, 4),
            orient=hou.Quaternion(0.3, -1.7, -0.9, -2.7)
        )

        self.assertEqual(mat, TARGET)

    # =========================================================================
    # DIGITAL ASSETS
    # =========================================================================

    def test_message_nodes(self):
        node = OBJ.node("test_message_nodes/solver")

        TARGET = (node.node("d/s"),)

        self.assertEqual(node.message_nodes(), TARGET)

    def test_editable_nodes(self):
        node = OBJ.node("test_message_nodes/solver")

        TARGET = (node.node("d/s"),)

        self.assertEqual(node.editable_nodes(), TARGET)

    def test_dive_target(self):
        node = OBJ.node("test_message_nodes/solver")

        TARGET = node.node("d/s")

        self.assertEqual(node.dive_target(), TARGET)

    def test_representative_node(self):
        node = OBJ.node("test_representative_node")

        TARGET = node.node("stereo_camera")

        self.assertEqual(node.representative_node(), TARGET)

    def test_is_contained_by__true(self):

        source_node = OBJ.node("test_is_contained_by/subnet/box")
        target_node = OBJ.node("test_is_contained_by")

        self.assertTrue(source_node.is_contained_by(target_node))

    def test_is_contained_by__false(self):

        source_node = OBJ.node("test_is_contained_by/subnet/box")
        target_node = OBJ.node("test_is_contained_by/other_subnet")

        self.assertFalse(source_node.is_contained_by(target_node))

    def test_meta_source(self):
        TARGET = "Scanned Asset Library Directories"
        path = hou.expandString("$HH/otls/OPlibSop.hda")

        self.assertEqual(hou.hda.meta_source(path), TARGET)

    def test_get_definition_meta_source(self):
        TARGET = "Scanned Asset Library Directories"

        node_type = hou.nodeType(hou.sopNodeTypeCategory(), "explodedview")

        self.assertEqual(node_type.definition().meta_source(), TARGET)

    def test_libraries_in_meta_source(self):
        libs = hou.hda.libraries_in_meta_source("Scanned Asset Library Directories")
        self.assertTrue(len(libs) > 0)

    def test_is_dummy_definition(self):
        geo = OBJ.createNode("geo")
        subnet = geo.createNode("subnet")

        # Create a new digital asset.
        asset = subnet.createDigitalAsset("dummyop", "Embedded", "Dummy")
        node_type = asset.type()

        # Not a dummy so far.
        self.assertFalse(node_type.definition().is_dummy_definition())

        # Destroy the definition.
        node_type.definition().destroy()

        # Now it's a dummy.
        self.assertTrue(node_type.definition().is_dummy_definition())

        # Destroy the instance.
        asset.destroy()

        # Destroy the dummy definition.
        node_type.definition().destroy()

# =============================================================================
# FUNCTIONS
# =============================================================================

def get_obj_geo(nodePath):
    """Get the geometry from the display node of a Geometry object."""
    return OBJ.node(nodePath).displayNode().geometry()

def get_obj_geo_copy(nodePath):
    """Get a copy of the geometry from the display node of a Geometry object."""
    # Create a new hou.Geometry object.
    geo = hou.Geometry()

    # Get the geometry object's geo.
    source_geo = get_obj_geo(nodePath)

    # Merge the geo to copy it.
    geo.merge(source_geo)

    return geo

# =============================================================================

if __name__ == '__main__':
    unittest.main()

