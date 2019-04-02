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
        hou.hipFile.load(os.path.join(THIS_DIR, "test_inline.hipnc"), ignore_load_warnings=True)

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
        hip_name = ht.inline.api.get_variable_value("HIPNAME")

        self.assertEqual(hip_name, os.path.splitext(os.path.basename(hou.hipFile.path()))[0])

    def test_set_variable(self):
        value = 22
        ht.inline.api.set_variable("awesome", value)

        self.assertEqual(ht.inline.api.get_variable_value("awesome"), 22)

    def test_get_variable_names(self):
        variable_names = ht.inline.api.get_variable_names()

        self.assertTrue("ACTIVETAKE" in variable_names)

    def test_getDirtyVariableNames(self):
        variable_names = ht.inline.api.get_variable_names()

        dirty_variable_names = ht.inline.api.get_variable_names(dirty=True)

        self.assertNotEqual(variable_names, dirty_variable_names)

    def test_unset_variable(self):
        ht.inline.api.set_variable("tester", 10)
        ht.inline.api.unset_variable("tester")

        self.assertTrue(ht.inline.api.get_variable_value("tester") is None)

    def test_emit_var_change(self):
        parm = hou.parm("/obj/test_emit_var_change/file1/file")

        string = "something_$VARCHANGE.bgeo"

        parm.set(string)

        path = parm.eval()

        self.assertEqual(path, string.replace("$VARCHANGE", ""))

        ht.inline.api.set_variable("VARCHANGE", 22)

        ht.inline.api.emit_var_change()

        new_path = parm.eval()

        # Test the paths aren't the same.
        self.assertNotEqual(path, new_path)

        # Test the update was successful.
        self.assertEqual(new_path, string.replace("$VARCHANGE", "22"))

    def test_expand_range(self):
        values = ht.inline.api.expand_range("0-5 10-20:2 64 65-66")
        target = (0, 1, 2, 3, 4, 5, 10, 12, 14, 16, 18, 20, 64, 65, 66)

        self.assertEqual(values, target)

    def test_read_only(self):
        geo = get_obj_geo("test_read_only")

        self.assertTrue(ht.inline.api.is_geometry_read_only(geo))

    def test_read_onlyFalse(self):
        geo = hou.Geometry()
        self.assertFalse(ht.inline.api.is_geometry_read_only(geo))

    def test_num_points(self):
        geo = get_obj_geo("test_num_points")

        self.assertEqual(ht.inline.api.num_points(geo), 5000)

    def test_num_prims(self):
        geo = get_obj_geo("test_num_prims")

        self.assertEqual(ht.inline.api.num_prims(geo), 12)

    def test_pack_geometry(self):
        geo = get_obj_geo("test_pack_geometry")

        prim = geo.prims()[0]

        self.assertTrue(isinstance(prim, hou.PackedGeometry))

    def test_sort_geometry_by_attribute(self):
        geo = get_obj_geo_copy("test_sort_geometry_by_attribute")

        attrib = geo.findPrimAttrib("id")

        ht.inline.api.sort_geometry_by_attribute(geo, attrib)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, range(10))

    def test_sort_geometry_by_attribute_reversed(self):
        geo = get_obj_geo_copy("test_sort_geometry_by_attribute")

        attrib = geo.findPrimAttrib("id")

        ht.inline.api.sort_geometry_by_attribute(geo, attrib, reverse=True)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, list(reversed(range(10))))

    def test_sort_geometry_by_attribute_invalid_index(self):
        geo = get_obj_geo_copy("test_sort_geometry_by_attribute")

        attrib = geo.findPrimAttrib("id")

        with self.assertRaises(IndexError):
            ht.inline.api.sort_geometry_by_attribute(geo, attrib, 1)

    def test_sort_geometry_by_attribute_detail(self):
        geo = get_obj_geo_copy("test_sort_geometry_by_attribute")

        attrib = geo.findGlobalAttrib("varmap")

        with self.assertRaises(ValueError):
            ht.inline.api.sort_geometry_by_attribute(geo, attrib)

    def test_sort_geometry_along_axis_points(self):
        geo = get_obj_geo_copy("test_sort_geometry_along_axis_points")

        ht.inline.api.sort_geometry_along_axis(geo, hou.geometryType.Points, 0)

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, range(10))

    def test_sort_geometry_along_axis_prims(self):
        geo = get_obj_geo_copy("test_sort_geometry_along_axis_prims")

        ht.inline.api.sort_geometry_along_axis(geo, hou.geometryType.Primitives, 2)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, range(10))

    def test_sort_geometry_by_values(self):
        # TODO: Test this.
        pass

    def test_sort_geometry_randomly__points(self):
        SEED = 11
        target = [5, 9, 3, 8, 0, 2, 6, 1, 4, 7]

        geo = get_obj_geo_copy("test_sort_geometry_randomly_points")
        ht.inline.api.sort_geometry_randomly(geo, hou.geometryType.Points, SEED)

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, target)

    def test_sort_geometry_randomly__prims(self):
        SEED = 345
        target = [4, 0, 9, 2, 1, 8, 3, 6, 7, 5]

        geo = get_obj_geo_copy("test_sort_geometry_randomly_prims")
        ht.inline.api.sort_geometry_randomly(geo, hou.geometryType.Primitives, SEED)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, target)

    def test_shift_geometry_elementsPoints(self):
        OFFSET = -18
        target = [8, 9, 0, 1, 2, 3, 4, 5, 6, 7]

        geo = get_obj_geo_copy("test_shift_geometry_elements_points")
        ht.inline.api.shift_geometry_elements(geo, hou.geometryType.Points, OFFSET)

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, target)

    def test_shift_geometry_elementsPrims(self):
        OFFSET = 6
        target = [4, 5, 6, 7, 8, 9, 0, 1, 2, 3]

        geo = get_obj_geo_copy("test_shift_geometry_elements_prims")
        ht.inline.api.shift_geometry_elements(geo, hou.geometryType.Primitives, OFFSET)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, target)

    def test_reverse_sort_geometryPoints(self):
        target = range(10)
        target.reverse()

        geo = get_obj_geo_copy("test_reverse_sort_geometry_points")
        ht.inline.api.reverse_sort_geometry(geo, hou.geometryType.Points)

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, target)

    def test_reverse_sort_geometryPrims(self):
        target = range(10)
        target.reverse()

        geo = get_obj_geo_copy("test_reverse_sort_geometry_prims")
        ht.inline.api.reverse_sort_geometry(geo, hou.geometryType.Primitives)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, target)

    def test_sort_geometry_by_proximity_to_position_points(self):
        target = [4, 3, 5, 2, 6, 1, 7, 0, 8, 9]
        POSITION = hou.Vector3(4, 1, 2)

        geo = get_obj_geo_copy("test_sort_geometry_by_proximity_to_position_points")
        ht.inline.api.sort_geometry_by_proximity_to_position(geo, hou.geometryType.Points, POSITION)

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, target)

    def test_sort_geometry_by_proximity_to_position_prims(self):
        target = [6, 7, 5, 8, 4, 9, 3, 2, 1, 0]
        POSITION = hou.Vector3(3, -1, 2)

        geo = get_obj_geo_copy("test_sort_geometry_by_proximity_to_position_prims")
        ht.inline.api.sort_geometry_by_proximity_to_position(geo, hou.geometryType.Primitives, POSITION)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, target)

    def test_sort_geometry_by_vertex_order(self):
        target = range(10)

        geo = get_obj_geo_copy("test_sort_geometry_by_vertex_order")
        ht.inline.api.sort_geometry_by_vertex_order(geo, )

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, target)

    def test_sort_geometry_by_expression_points(self):
        target_geo = OBJ.node("test_sort_geometry_by_expression_points/RESULT").geometry()
        test_geo = OBJ.node("test_sort_geometry_by_expression_points/TEST").geometry()

        self.assertEqual(
            test_geo.pointFloatAttribValues("id"),
            target_geo.pointFloatAttribValues("id"),
        )

    def test_sort_geometry_by_expression_prims(self):
        target_geo = OBJ.node("test_sort_geometry_by_expression_prims/RESULT").geometry()
        test_geo = OBJ.node("test_sort_geometry_by_expression_prims/TEST").geometry()

        self.assertEqual(
            test_geo.primFloatAttribValues("id"),
            target_geo.primFloatAttribValues("id"),
        )

    def test_create_point_at_position(self):
        geo = hou.Geometry()

        point = ht.inline.api.create_point_at_position(geo, hou.Vector3(1, 2, 3))

        self.assertEqual(point.position(), hou.Vector3(1, 2, 3))

    def test_create_n_points(self):
        geo = hou.Geometry()
        points = ht.inline.api.create_n_points(geo, 15)

        self.assertEqual(points, geo.points())

    def test_create_n_pointsInvalidNumber(self):
        geo = hou.Geometry()

        with self.assertRaises(ValueError):
            ht.inline.api.create_n_points(geo, -4)

    def test_merge_point_group(self):
        geo = hou.Geometry()
        source_geo = get_obj_geo("test_merge_point_group")

        group = source_geo.pointGroups()[0]

        ht.inline.api.merge_point_group(geo, group)

        self.assertEqual(len(geo.iterPoints()), len(group.points()))

    def test_merge_points(self):
        geo = hou.Geometry()
        source_geo = get_obj_geo("test_merge_points")

        points = source_geo.globPoints("0 6 15 35-38 66")

        ht.inline.api.merge_points(geo, points)

        self.assertEqual(len(geo.iterPoints()), len(points))

    def test_merge_prim_group(self):
        geo = hou.Geometry()
        source_geo = get_obj_geo("test_merge_prim_group")

        group = source_geo.primGroups()[0]

        ht.inline.api.merge_prim_group(geo, group)

        self.assertEqual(len(geo.iterPrims()), len(group.prims()))

    def test_merge_prims(self):
        geo = hou.Geometry()
        source_geo = get_obj_geo("test_merge_prims")

        prims = source_geo.globPrims("0 6 15 35-38 66")

        ht.inline.api.merge_prims(geo, prims)

        self.assertEqual(len(geo.iterPrims()), len(prims))

    def test_copy_point_attribute_values(self):
        source = get_obj_geo("test_copy_point_attribute_values")

        attribs = source.pointAttribs()

        geo = hou.Geometry()

        p1 = geo.createPoint()
        p2 = geo.createPoint()

        ht.inline.api.copy_point_attribute_values(p1, source.iterPoints()[2], attribs)
        ht.inline.api.copy_point_attribute_values(p2, source.iterPoints()[6], attribs)

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

        ht.inline.api.copy_point_attribute_values(p1, source.iterPrims()[1], attribs)
        ht.inline.api.copy_point_attribute_values(p2, source.iterPrims()[4], attribs)

        # Ensure all the attributes got copied right.
        self.assertEqual(len(geo.primAttribs()), len(attribs))

        # Ensure P got copied right.
        self.assertEqual(p1.attribValue("prnum"), 1)
        self.assertEqual(p2.attribValue("prnum"), 4)

    def test_point_adjacent_polygons(self):
        geo = get_obj_geo("test_point_adjacent_polygons")

        target = geo.globPrims("1 2")

        prims = ht.inline.api.point_adjacent_polygons(geo.iterPrims()[0])

        self.assertEqual(prims, target)

    def test_edge_adjacent_polygons(self):
        geo = get_obj_geo("test_edge_adjacent_polygons")

        target = geo.globPrims("2")

        prims = ht.inline.api.edge_adjacent_polygons(geo.iterPrims()[0])

        self.assertEqual(prims, target)

    def test_connected_prims(self):
        geo = get_obj_geo("test_connected_prims")

        target = geo.prims()

        prims = ht.inline.api.connected_prims(geo.iterPoints()[4])

        self.assertEqual(prims, target)

    def test_connected_points(self):
        geo = get_obj_geo("test_connected_points")

        target = geo.globPoints("1 3 5 7")

        points = ht.inline.api.connected_points(geo.iterPoints()[4])

        self.assertEqual(points, target)

    def test_referencing_vertices(self):
        geo = get_obj_geo("test_referencing_vertices")

        target = geo.globVertices("0v2 1v3 2v1 3v0")

        verts = ht.inline.api.referencing_vertices(geo.iterPoints()[4])

        self.assertEqual(verts, target)

    def test_point_string_table_indices(self):
        geo = get_obj_geo("test_point_string_table_indices")

        target = (0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1)

        attr = geo.findPointAttrib("test")

        self.assertEqual(ht.inline.api.string_table_indices(attr), target)

    def test_prim_string_table_indices(self):
        geo = get_obj_geo("test_prim_string_table_indices")

        target = (0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4)

        attr = geo.findPrimAttrib("test")

        self.assertEqual(ht.inline.api.string_table_indices(attr), target)

    def test_vertex_string_attrib_values(self):
        geo = get_obj_geo("test_vertex_string_attrib_values")

        target = ('vertex0', 'vertex1', 'vertex2', 'vertex3', 'vertex4', 'vertex5', 'vertex6', 'vertex7')

        self.assertEqual(ht.inline.api.vertex_string_attrib_values(geo, "test"), target)

    def test_set_vertex_string_attrib_values(self):
        target = ('vertex0', 'vertex1', 'vertex2', 'vertex3', 'vertex4')

        geo = get_obj_geo_copy("test_set_vertex_string_attrib_values")
        attr = geo.findVertexAttrib("test")

        ht.inline.api.set_vertex_string_attrib_values(geo, "test", target)

        vals = []

        for prim in geo.prims():
            vals.extend([vert.attribValue(attr) for vert in prim.vertices()])

        self.assertEqual(tuple(vals), target)

    def test_set_vertex_string_attrib_valuesInvalidAttribute(self):
        target = ('vertex0', 'vertex1', 'vertex2', 'vertex3', 'vertex4')

        geo = get_obj_geo_copy("test_set_vertex_string_attrib_values")

        with self.assertRaises(hou.OperationFailed):
           ht.inline.api.set_vertex_string_attrib_values(geo, "thing", target)

    def test_set_vertex_string_attrib_valuesInvalidAttributeType(self):
        target = ('vertex0', 'vertex1', 'vertex2', 'vertex3', 'vertex4')

        geo = get_obj_geo_copy("test_set_vertex_string_attrib_values")

        with self.assertRaises(ValueError):
           ht.inline.api.set_vertex_string_attrib_values(geo, "notstring", target)

    def test_setPrimStringAttribValuesInvalidAttributeSize(self):
        target = ('vertex0', 'vertex1', 'vertex2', 'vertex3')

        geo = get_obj_geo_copy("test_set_vertex_string_attrib_values")

        with self.assertRaises(ValueError):
           ht.inline.api.set_vertex_string_attrib_values(geo, "test", target)

    def test_set_shared_point_string_attrib(self):
        target = ["point0"]*5
        geo = hou.Geometry()
        ht.inline.api.create_n_points(geo, 5)
        attr = geo.addAttrib(hou.attribType.Point, "test", "")

        ht.inline.api.set_shared_point_string_attrib(geo, attr.name(), "point0")

        vals = [point.attribValue(attr) for point in geo.points()]

        self.assertEqual(vals, target)

    def test_set_shared_point_string_attribGroup(self):
        target = ["point0"]*5 + [""]*5

        geo = hou.Geometry()

        attr = geo.addAttrib(hou.attribType.Point, "test", "")

        ht.inline.api.create_n_points(geo, 5)
        group = geo.createPointGroup("group1")

        for point in geo.points():
            group.add(point)

        ht.inline.api.create_n_points(geo, 5)

        ht.inline.api.set_shared_point_string_attrib(geo, attr.name(), "point0", group)

        vals = [point.attribValue(attr) for point in geo.points()]

        self.assertEqual(vals, target)

    def test_set_shared_prim_string_attrib(self):
        target = ["value"]*5

        geo = get_obj_geo_copy("test_set_shared_prim_string_attrib")

        attr = geo.findPrimAttrib("test")

        ht.inline.api.set_shared_prim_string_attrib(geo, attr.name(), "value")

        vals = [prim.attribValue(attr) for prim in geo.prims()]

        self.assertEqual(vals, target)

    def test_set_shared_prim_string_attribGroup(self):
        target = ["value"]*3 + ["", ""]

        geo = get_obj_geo_copy("test_set_shared_prim_string_attrib")

        attr = geo.findPrimAttrib("test")

        group = geo.findPrimGroup("group1")

        ht.inline.api.set_shared_prim_string_attrib(geo, attr.name(), "value", group)

        vals = [prim.attribValue(attr) for prim in geo.prims()]

        self.assertEqual(vals, target)

    def test_has_edge(self):
        geo = get_obj_geo("test_has_edge")

        face = geo.iterPrims()[0]

        p0 = geo.iterPoints()[0]
        p1 = geo.iterPoints()[1]

        self.assertTrue(ht.inline.api.face_has_edge(face, p0, p1))

    def test_has_edgeFail(self):
        geo = get_obj_geo("test_has_edge")

        face = geo.iterPrims()[0]

        p0 = geo.iterPoints()[0]
        p2 = geo.iterPoints()[2]

        self.assertTrue(ht.inline.api.face_has_edge(face, p0, p2))

    def test_shared_edges(self):
        geo = get_obj_geo("test_shared_edges")

        pr0, pr1 = geo.prims()

        edges = ht.inline.api.shared_edges(pr0, pr1)

        pt2 = geo.iterPoints()[2]
        pt3 = geo.iterPoints()[3]

        edge = geo.findEdge(pt2, pt3)

        self.assertEqual(edges, (edge,))

    def test_insert_vertex(self):
        geo = get_obj_geo_copy("test_insert_vertex")

        face = geo.iterPrims()[0]

        pt = ht.inline.api.create_point_at_position(geo, hou.Vector3(0.5, 0, 0.5))

        ht.inline.api.insert_vertex(face, pt, 2)

        self.assertEqual(face.vertex(2).point(), pt)

    def test_insert_vertexNegativeIndex(self):
        geo = get_obj_geo_copy("test_insert_vertex")

        face = geo.iterPrims()[0]

        pt = ht.inline.api.create_point_at_position(geo, hou.Vector3(0.5, 0, 0.5))

        with self.assertRaises(IndexError):
            ht.inline.api.insert_vertex(face, pt, -1)

    def test_insert_vertexInvalidIndex(self):
        geo = get_obj_geo_copy("test_insert_vertex")

        face = geo.iterPrims()[0]

        pt = ht.inline.api.create_point_at_position(geo, hou.Vector3(0.5, 0, 0.5))

        with self.assertRaises(IndexError):
            ht.inline.api.insert_vertex(face, pt, 10)

    def test_delete_vertex(self):
        geo = get_obj_geo_copy("test_delete_vertex")

        face = geo.iterPrims()[0]

        ht.inline.api.delete_vertex_from_face(face, 3)

        self.assertEqual(len(face.vertices()), 3)

    def test_delete_vertexNegativeIndex(self):
        geo = get_obj_geo_copy("test_delete_vertex")

        face = geo.iterPrims()[0]

        with self.assertRaises(IndexError):
            ht.inline.api.delete_vertex_from_face(face, -1)

    def test_delete_vertexInvalidIndex(self):
        geo = get_obj_geo_copy("test_delete_vertex")

        face = geo.iterPrims()[0]

        with self.assertRaises(IndexError):
            ht.inline.api.delete_vertex_from_face(face, 10)

    def test_set_point(self):
        geo = get_obj_geo_copy("test_set_point")

        face = geo.iterPrims()[0]
        pt = geo.iterPoints()[4]

        ht.inline.api.set_face_vertex_point(face, 3, pt)

        self.assertEqual(face.vertex(3).point().number(), 4)

    def test_set_point_negative_index(self):
        geo = get_obj_geo_copy("test_set_point")

        face = geo.iterPrims()[0]
        pt = geo.iterPoints()[4]

        with self.assertRaises(IndexError):
            ht.inline.api.set_face_vertex_point(face, -1, pt)

    def test_set_point_invalid_index(self):
        geo = get_obj_geo_copy("test_set_point")

        face = geo.iterPrims()[0]
        pt = geo.iterPoints()[4]

        with self.assertRaises(IndexError):
            ht.inline.api.set_face_vertex_point(face, 10, pt)

    def test_bary_center(self):
        target = hou.Vector3(1.5, 1, -1)
        geo = get_obj_geo_copy("test_bary_center")

        prim = geo.iterPrims()[0]

        self.assertEqual(ht.inline.api.primitive_bary_center(prim), target)

    def test_primitive_area(self):
        target = 4.375
        geo = get_obj_geo_copy("test_primitive_area")

        prim = geo.iterPrims()[0]

        self.assertEqual(ht.inline.api.primitive_area(prim), target)

    def test_perimeter(self):
        target = 6.5
        geo = get_obj_geo_copy("test_perimeter")

        prim = geo.iterPrims()[0]

        self.assertEqual(ht.inline.api.primitive_perimeter(prim), target)

    def test_volume(self):
        target = 0.1666666716337204
        geo = get_obj_geo_copy("test_volume")

        prim = geo.iterPrims()[0]

        self.assertEqual(ht.inline.api.primitive_volume(prim), target)

    def test_reverse_prim(self):
        target = hou.Vector3(0, -1, 0)
        geo = get_obj_geo_copy("test_reverse_prim")

        prim = geo.iterPrims()[0]
        ht.inline.api.reverse_prim(prim)

        self.assertEqual(prim.normal(), target)

    def test_make_unique(self):
        target = 28
        geo = get_obj_geo_copy("test_make_unique")

        prim = geo.iterPrims()[4]
        ht.inline.api.make_primitive_points_unique(prim)

        self.assertEqual(len(geo.iterPoints()), target)

    def test_prim_bounding_box(self):
        target = hou.BoundingBox(-0.75, 0, -0.875, 0.75, 1.5, 0.875)
        geo = get_obj_geo_copy("test_prim_bounding_box")

        prim = geo.iterPrims()[0]

        self.assertEqual(ht.inline.api.primitive_bounding_box(prim), target)

    def test_compute_point_normals(self):
        geo = get_obj_geo_copy("test_compute_point_normals")

        ht.inline.api.compute_point_normals(geo)

        self.assertNotEqual(geo.findPointAttrib("N"), None)

    def test_add_point_normal_attribute(self):
        geo = get_obj_geo_copy("test_add_point_normal_attribute")

        self.assertNotEqual(ht.inline.api.add_point_normal_attribute(geo), None)

    def test_add_point_velocity_attribute(self):
        geo = get_obj_geo_copy("test_add_point_velocity_attribute")

        self.assertNotEqual(ht.inline.api.add_point_velocity_attribute(geo), None)

    def test_add_color_attribute_point(self):
        geo = get_obj_geo_copy("test_add_color_attribute")

        result = ht.inline.api.add_color_attribute(geo, hou.attribType.Point)

        self.assertNotEqual(result, None)

    def test_add_color_attribute_prim(self):
        geo = get_obj_geo_copy("test_add_color_attribute")

        result = ht.inline.api.add_color_attribute(geo, hou.attribType.Prim)

        self.assertNotEqual(result, None)

    def test_add_color_attribute_vertex(self):
        geo = get_obj_geo_copy("test_add_color_attribute")

        result = ht.inline.api.add_color_attribute(geo, hou.attribType.Vertex)

        self.assertNotEqual(result, None)

    def test_add_color_attribute_point(self):
        geo = get_obj_geo_copy("test_add_color_attribute")

        with self.assertRaises(ValueError):
            ht.inline.api.add_color_attribute(geo, hou.attribType.Global)

    def test_convex(self):
        geo = get_obj_geo_copy("test_convex")

        ht.inline.api.convex_polygons(geo)

        self.assertEqual(len(geo.iterPrims()), 162)

        verts = [vert for prim in geo.prims() for vert in prim.vertices()]
        self.assertEqual(len(verts), 486)

    def test_clip(self):
        geo = get_obj_geo_copy("test_clip")

        origin = hou.Vector3(0, 0, 0)

        direction = hou.Vector3(-0.5, 0.6, -0.6)

        ht.inline.api.clip_geometry(geo, origin, direction, 0.5)

        self.assertEqual(len(geo.iterPrims()), 42)

        self.assertEqual(len(geo.iterPoints()), 60)

    def test_clip_below(self):
        geo = get_obj_geo_copy("test_clip_below")

        origin = hou.Vector3(0, -0.7, -0.9)

        direction = hou.Vector3(-0.6, 0.1, -0.8)

        ht.inline.api.clip_geometry(geo, origin, direction, 0.6, below=True)

        self.assertEqual(len(geo.iterPrims()), 61)

        self.assertEqual(len(geo.iterPoints()), 81)

    def test_clip_group(self):
        geo = get_obj_geo_copy("test_clip_group")

        group = geo.primGroups()[0]

        origin = hou.Vector3(-1.3, -1.5, 1.2)

        direction = hou.Vector3(0.8, 0.02, 0.5)

        ht.inline.api.clip_geometry(geo, origin, direction, -0.3, group=group)

        self.assertEqual(len(geo.iterPrims()), 74)

        self.assertEqual(len(geo.iterPoints()), 98)

    def test_destroyEmpty_point_groups(self):
        geo = hou.Geometry()

        geo.createPointGroup("empty")

        ht.inline.api.destroy_empty_groups(geo, hou.attribType.Point)

        self.assertEqual(len(geo.pointGroups()), 0)

    def test_destroyEmpty_prim_groups(self):
        geo = hou.Geometry()

        geo.createPrimGroup("empty")

        ht.inline.api.destroy_empty_groups(geo, hou.attribType.Prim)

        self.assertEqual(len(geo.primGroups()), 0)

    def test_destroy_unused_points(self):
        geo = get_obj_geo_copy("test_destroy_unused_points")

        ht.inline.api.destroy_unused_points(geo, )

        self.assertEqual(len(geo.iterPoints()), 20)

    def test_destroy_unused_points_group(self):
        geo = get_obj_geo_copy("test_destroy_unused_points_group")

        group = geo.pointGroups()[0]

        ht.inline.api.destroy_unused_points(geo, group)

        self.assertEqual(len(geo.iterPoints()), 3729)

    def test_consolidate_points(self):
        geo = get_obj_geo_copy("test_consolidate_points")

        ht.inline.api.consolidate_points(geo, )

        self.assertEqual(len(geo.iterPoints()), 100)

    def test_consolidate_points_dist(self):
        geo = get_obj_geo_copy("test_consolidate_points_dist")

        ht.inline.api.consolidate_points(geo, 3)

        self.assertEqual(len(geo.iterPoints()), 16)

    def test_consolidate_points_group(self):
        geo = get_obj_geo_copy("test_consolidate_points_group")

        group = geo.pointGroups()[0]

        ht.inline.api.consolidate_points(geo, group=group)

        self.assertEqual(len(geo.iterPoints()), 212)

    def test_unique_points(self):
        geo = get_obj_geo_copy("test_unique_points")

        ht.inline.api.unique_points(geo, )

        self.assertEqual(len(geo.iterPoints()), 324)

    def test_unique_points_point_group(self):
        geo = get_obj_geo_copy("test_unique_points_point_group")

        group = geo.pointGroups()[0]
        ht.inline.api.unique_points(geo, group)

        self.assertEqual(len(geo.iterPoints()), 195)

    def test_rename_point_group(self):
        geo = get_obj_geo_copy("test_rename_point_group")

        group = geo.pointGroups()[0]

        result = ht.inline.api.rename_group(group, "test_group")

        self.assertTrue(result is not None)
        self.assertTrue(result.name() == "test_group")

    def test_rename_point_group_same_name(self):
        geo = get_obj_geo_copy("test_rename_point_group")

        group = geo.pointGroups()[0]
        name = group.name()

        with self.assertRaises(hou.OperationFailed):
            ht.inline.api.rename_group(group, name)

    def test_rename_prim_group(self):
        geo = get_obj_geo_copy("test_rename_prim_group")

        group = geo.primGroups()[0]

        result = ht.inline.api.rename_group(group, "test_group")

        self.assertTrue(result is not None)
        self.assertTrue(result.name() == "test_group")

    def test_rename_prim_group_same_name(self):
        geo = get_obj_geo_copy("test_rename_prim_group")

        group = geo.primGroups()[0]
        name = group.name()

        with self.assertRaises(hou.OperationFailed):
            ht.inline.api.rename_group(group, name)

    def test_rename_edge_group(self):
        geo = get_obj_geo_copy("test_rename_edge_group")

        group = geo.edgeGroups()[0]

        result = ht.inline.api.rename_group(group, "test_group")

        self.assertTrue(result is not None)
        self.assertTrue(result.name() == "test_group")

    def test_rename_edge_group_same_name(self):
        geo = get_obj_geo_copy("test_rename_edge_group")

        group = geo.edgeGroups()[0]
        name = group.name()

        with self.assertRaises(hou.OperationFailed):
            ht.inline.api.rename_group(group, name)

    def test_group_bounding_box_point(self):
        target = hou.BoundingBox(-4, 0, -1, -2, 0, 2)

        geo = get_obj_geo("test_group_bounding_box_point")

        group = geo.pointGroups()[0]
        bbox = ht.inline.api.group_bounding_box(group)

        self.assertEqual(bbox, target)

    def test_group_bounding_box_prim(self):
        target = hou.BoundingBox(-5, 0, -4, 4, 0, 5)

        geo = get_obj_geo("test_group_bounding_box_prim")

        group = geo.primGroups()[0]
        bbox = ht.inline.api.group_bounding_box(group)

        self.assertEqual(bbox, target)

    def test_group_bounding_box_edge(self):
        target = hou.BoundingBox(-5, 0, -5, 4, 0, 5)

        geo = get_obj_geo("test_group_bounding_box_edge")

        group = geo.edgeGroups()[0]
        bbox = ht.inline.api.group_bounding_box(group)

        self.assertEqual(bbox, target)

    def test_point_group_size(self):
        geo = get_obj_geo("test_point_group_size")

        group = geo.pointGroups()[0]

        self.assertEqual(ht.inline.api.group_size(group) , 12)

    def test_prim_group_size(self):
        geo = get_obj_geo("test_prim_group_size")

        group = geo.primGroups()[0]

        self.assertEqual(ht.inline.api.group_size(group) , 39)

    def test_edge_group_size(self):
        geo = get_obj_geo("test_edge_group_size")

        group = geo.edgeGroups()[0]

        self.assertEqual(ht.inline.api.group_size(group) , 52)

    def test_toggle_point(self):
        geo = get_obj_geo_copy("test_toggle_point")

        group = geo.pointGroups()[0]
        point = geo.iterPoints()[0]

        ht.inline.api.toggle_point_in_group(group, point)

        self.assertTrue(group.contains(point))

    def test_toggle_prim(self):
        geo = get_obj_geo_copy("test_toggle_prim")

        group = geo.primGroups()[0]
        prim = geo.iterPrims()[0]

        ht.inline.api.toggle_prim_in_group(group, prim)

        self.assertTrue(group.contains(prim))

    def test_toggle_entries_point(self):
        geo = get_obj_geo_copy("test_toggle_entries_point")

        vals = geo.globPoints(" ".join([str(val) for val in range(1, 100, 2)]))

        group = geo.pointGroups()[0]
        ht.inline.api.toggle_group_entries(group)

        self.assertEquals(group.points(), vals)

    def test_toggle_entries_prim(self):
        geo = get_obj_geo_copy("test_toggle_entries_prim")

        vals = geo.globPrims(" ".join([str(val) for val in range(0, 100, 2)]))

        group = geo.primGroups()[0]
        ht.inline.api.toggle_group_entries(group)

        self.assertEquals(group.prims(), vals)

    def test_toggle_entries_edge(self):
        geo = get_obj_geo_copy("test_toggle_entries_edge")

        group = geo.edgeGroups()[0]
        ht.inline.api.toggle_group_entries(group)

        self.assertEquals(len(group.edges()),  20)

    def test_copy_point_group(self):
        geo = get_obj_geo_copy("test_copy_point_group")

        group = geo.pointGroups()[0]

        new_group = ht.inline.api.copy_group(group, "new_group")

        self.assertEquals(group.points(), new_group.points())

    def test_copy_point_group_same_name(self):
        geo = get_obj_geo_copy("test_copy_point_group")

        group = geo.pointGroups()[0]

        with self.assertRaises(hou.OperationFailed):
            ht.inline.api.copy_group(group, group.name())

    def test_copy_point_group_existing(self):
        geo = get_obj_geo_copy("test_copy_point_group_existing")

        group = geo.pointGroups()[-1]

        other_group = geo.pointGroups()[0]

        with self.assertRaises(hou.OperationFailed):
            ht.inline.api.copy_group(group, other_group.name())

    def test_copy_prim_group(self):
        geo = get_obj_geo_copy("test_copy_prim_group")

        group = geo.primGroups()[0]

        new_group = ht.inline.api.copy_group(group, "new_group")

        self.assertEquals(group.prims(), new_group.prims())

    def test_copy_prim_group_same_name(self):
        geo = get_obj_geo_copy("test_copy_prim_group")

        group = geo.primGroups()[0]

        with self.assertRaises(hou.OperationFailed):
            ht.inline.api.copy_group(group, group.name())

    def test_copy_prim_group_existing(self):
        geo = get_obj_geo_copy("test_copy_prim_group_existing")

        group = geo.primGroups()[-1]

        other_group = geo.primGroups()[0]

        with self.assertRaises(hou.OperationFailed):
            ht.inline.api.copy_group(group, other_group.name())

    def test_point_groups_share_elements(self):
        geo = get_obj_geo_copy("test_point_group_contains_any")

        group1 = geo.pointGroups()[0]
        group2 = geo.pointGroups()[1]

        self.assertTrue(ht.inline.api.groups_share_elements(group1, group2))

    def test_point_groups_share_elements_False(self):
        group1 = OBJ.node("test_point_group_contains_any_False/group1").geometry().pointGroups()[0]
        group2 = OBJ.node("test_point_group_contains_any_False/group2").geometry().pointGroups()[0]

        with self.assertRaises(ValueError):
            ht.inline.api.groups_share_elements(group1, group2)

    def test_prim_groups_share_elements(self):
        geo = get_obj_geo_copy("test_prim_group_contains_any")

        group1 = geo.primGroups()[0]
        group2 = geo.primGroups()[1]

        self.assertTrue(ht.inline.api.groups_share_elements(group1, group2))

    def test_prim_groups_share_elements_False(self):
        group1 = OBJ.node("test_prim_group_contains_any_False/group1").geometry().primGroups()[0]
        group2 = OBJ.node("test_prim_group_contains_any_False/group2").geometry().primGroups()[0]

        with self.assertRaises(ValueError):
            ht.inline.api.groups_share_elements(group1, group2)

    def test_convert_prim_to_point_group(self):
        geo = get_obj_geo_copy("test_convert_prim_to_point_group")

        group = geo.primGroups()[0]

        new_group = ht.inline.api.convert_prim_to_point_group(group)

        self.assertEqual(len(new_group.points()), 12)

        # Check source group was deleted.
        self.assertEqual(len(geo.primGroups()), 0)

    def test_convert_prim_to_point_group_with_name(self):
        geo = get_obj_geo_copy("test_convert_prim_to_point_group")

        group = geo.primGroups()[0]

        new_group = ht.inline.api.convert_prim_to_point_group(group, "new_group")

        self.assertEqual(new_group.name(), "new_group")

    def test_convert_prim_to_point_group_no_destroy(self):
        geo = get_obj_geo_copy("test_convert_prim_to_point_group")

        group = geo.primGroups()[0]

        new_group = ht.inline.api.convert_prim_to_point_group(group, destroy=False)

        # Check source group wasn't deleted.
        self.assertEqual(len(geo.primGroups()), 1)

    def test_convert_point_to_prim_group(self):
        geo = get_obj_geo_copy("test_convert_point_to_prim_group")

        group = geo.pointGroups()[0]

        new_group = ht.inline.api.convert_point_to_prim_group(group, )

        self.assertEqual(len(new_group.prims()), 5)

        # Check source group was deleted.
        self.assertEqual(len(geo.pointGroups()), 0)

    def test_convert_point_to_prim_group_with_name(self):
        geo = get_obj_geo_copy("test_convert_point_to_prim_group")

        group = geo.pointGroups()[0]

        new_group = ht.inline.api.convert_point_to_prim_group(group, "new_group")

        self.assertEqual(new_group.name(), "new_group")

    def test_convert_point_to_prim_group_no_destroy(self):
        geo = get_obj_geo_copy("test_convert_point_to_prim_group")

        group = geo.pointGroups()[0]

        new_group = ht.inline.api.convert_point_to_prim_group(group, destroy=False)

        # Check source group wasn't deleted.
        self.assertEqual(len(geo.primGroups()), 1)

    # =========================================================================
    # UNGROUPED POINTS
    # =========================================================================

    def test_has_ungrouped_points(self):
        geo = get_obj_geo("test_has_ungrouped_points")

        self.assertTrue(ht.inline.api.geometry_has_ungrouped_points(geo))

    def test_has_ungrouped_points_False(self):
        geo = get_obj_geo("test_has_ungrouped_points_False")

        self.assertFalse(ht.inline.api.geometry_has_ungrouped_points(geo))

    def test_group_ungrouped_points(self):
        geo = get_obj_geo_copy("test_group_ungrouped_points")

        group = ht.inline.api.group_ungrouped_points(geo, "ungrouped")

        self.assertEquals(len(group.points()), 10)

    def test_group_ungrouped_pointsExistingName(self):
        geo = get_obj_geo_copy("test_group_ungrouped_points")

        with self.assertRaises(hou.OperationFailed):
            ht.inline.api.group_ungrouped_points(geo, "group1")

    def test_group_ungrouped_pointsNoName(self):
        geo = get_obj_geo_copy("test_group_ungrouped_points")

        with self.assertRaises(ValueError):
            ht.inline.api.group_ungrouped_points(geo, "")

    def test_group_ungrouped_points_False(self):
        geo = get_obj_geo_copy("test_group_ungrouped_points_False")

        group = ht.inline.api.group_ungrouped_points(geo, "ungrouped")

        self.assertEquals(group, None)

    # =========================================================================
    # UNGROUPED PRIMS
    # =========================================================================

    def test_has_ungrouped_prims(self):
        geo = get_obj_geo("test_has_ungrouped_prims")

        self.assertTrue(ht.inline.api.geometry_has_ungrouped_prims(geo))

    def test_has_ungrouped_prims(self):
        geo = get_obj_geo("test_has_ungrouped_prims_False")

        self.assertFalse(ht.inline.api.geometry_has_ungrouped_prims(geo))

    def test_group_ungrouped_prims(self):
        geo = get_obj_geo_copy("test_group_ungrouped_prims")

        group = ht.inline.api.group_ungrouped_prims(geo, "ungrouped")

        self.assertEquals(len(group.prims()), 3)

    def test_group_ungrouped_prims_ExistingName(self):
        geo = get_obj_geo_copy("test_group_ungrouped_prims")

        with self.assertRaises(hou.OperationFailed):
            ht.inline.api.group_ungrouped_prims(geo, "group1")

    def test_group_ungrouped_prims_NoName(self):
        geo = get_obj_geo_copy("test_group_ungrouped_prims")

        with self.assertRaises(ValueError):
            ht.inline.api.group_ungrouped_prims(geo, "")

    def test_group_ungrouped_prims_False(self):
        geo = get_obj_geo_copy("test_group_ungrouped_prims_False")

        group = ht.inline.api.group_ungrouped_prims(geo, "ungrouped")

        self.assertEquals(group, None)

    # =========================================================================
    # BOUNDING BOXES
    # =========================================================================

    def test_is_inside(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)
        bbox2 = hou.BoundingBox(-1, -1, -1, 1, 1, 1)

        self.assertTrue(ht.inline.api.bounding_box_is_inside(bbox1, bbox2))

    def test_is_insideFail(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)
        bbox2 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

        self.assertFalse(ht.inline.api.bounding_box_is_inside(bbox1, bbox2))

    def test_intersects(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)
        bbox2 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

        self.assertTrue(ht.inline.api.bounding_boxes_intersect(bbox1, bbox2))

    def test_intersectsFail(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, -0.1, -0.1, -0.1)
        bbox2 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

        self.assertFalse(ht.inline.api.bounding_boxes_intersect(bbox1, bbox2))

    def test_compute_intersection(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)
        bbox2 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

        self.assertTrue(ht.inline.api.compute_bounding_box_intersection(bbox1, bbox2))

        self.assertEqual(bbox1.minvec(), hou.Vector3())
        self.assertEqual(bbox1.maxvec(), hou.Vector3(0.5, 0.5, 0.5))

    def test_compute_intersectionFail(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, -0.1, -0.1, -0.1)
        bbox2 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

        self.assertFalse(ht.inline.api.compute_bounding_box_intersection(bbox1, bbox2))

    def test_expand_bounds(self):
        bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)
        ht.inline.api.expand_bounding_box(bbox, 1, 1, 1)

        self.assertEqual(bbox.minvec(), hou.Vector3(-2, -2.75, -4))
        self.assertEqual(bbox.maxvec(), hou.Vector3(2, 2.75, 4))

    def test_add_to_min(self):
        bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)
        ht.inline.api.add_to_bounding_box_min(bbox, hou.Vector3(1, 0.25, 1))

        self.assertEqual(bbox.minvec(), hou.Vector3(0, -1.5, -2))

    def test_add_to_max(self):
        bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)
        ht.inline.api.add_to_bounding_box_max(bbox, hou.Vector3(2, 0.25, 1))

        self.assertEqual(bbox.maxvec(), hou.Vector3(3, 2, 4))

    def test_area(self):
        bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)

        self.assertEqual(ht.inline.api.bounding_box_area(bbox), 80)

    def test_bounding_box_volume(self):
        bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)

        self.assertEqual(ht.inline.api.bounding_box_volume(bbox), 42)

    # =========================================================================
    # PARMS
    # =========================================================================

    def test_is_vector(self):
        node = OBJ.node("test_is_vector/node")
        parm = node.parmTuple("vec")

        self.assertTrue(ht.inline.api.is_parm_tuple_vector(parm))

    def test_is_vector_False(self):
        node = OBJ.node("test_is_vector/node")
        parm = node.parmTuple("not_vec")

        self.assertFalse(ht.inline.api.is_parm_tuple_vector(parm))

    def test_eval_as_vector2(self):
        node = OBJ.node("test_eval_as_vector/node")
        parm = node.parmTuple("vec2")

        self.assertEqual(ht.inline.api.eval_parm_tuple_as_vector(parm), hou.Vector2(1,2))

    def test_eval_as_vector3(self):
        node = OBJ.node("test_eval_as_vector/node")
        parm = node.parmTuple("vec3")

        self.assertEqual(ht.inline.api.eval_parm_tuple_as_vector(parm), hou.Vector3(3,4,5))

    def test_eval_as_vector4(self):
        node = OBJ.node("test_eval_as_vector/node")
        parm = node.parmTuple("vec4")

        self.assertEqual(ht.inline.api.eval_parm_tuple_as_vector(parm), hou.Vector4(6,7,8,9))

    def test_eval_as_vector_Fail(self):
        node = OBJ.node("test_eval_as_vector/node")
        parm = node.parmTuple("not_vec")

        with self.assertRaises(ValueError):
            ht.inline.api.eval_parm_tuple_as_vector(parm)

    def test_is_color(self):
        node = OBJ.node("test_is_color/node")
        parm = node.parmTuple("color")

        self.assertTrue(ht.inline.api.is_parm_tuple_color(parm))

    def test_is_colorFalse(self):
        node = OBJ.node("test_is_color/node")
        parm = node.parmTuple("not_color")

        self.assertFalse(ht.inline.api.is_parm_tuple_color(parm))

    def test_eval_as_color(self):
        node = OBJ.node("test_eval_as_color/node")
        parm = node.parmTuple("color")

        self.assertEqual(ht.inline.api.eval_parm_tuple_as_color(parm), hou.Color(0,0.5,0.5))

    def test_eval_as_color_fail(self):
        node = OBJ.node("test_eval_as_color/node")
        parm = node.parmTuple("not_color")

        with self.assertRaises(ValueError):
            ht.inline.api.eval_parm_tuple_as_color(parm)

    def test_eval_as_strip_single(self):
        node = OBJ.node("test_eval_as_strip/node")
        parm = node.parm("strip_normal")

        target = (False, True, False, False)

        self.assertEqual(
            ht.inline.api.eval_parm_as_strip(parm),
            target
        )

    def test_eval_as_strip_toggle(self):
        node = OBJ.node("test_eval_as_strip/node")
        parm = node.parm("strip_toggle")

        target = (True, False, True, True)

        self.assertEqual(
            ht.inline.api.eval_parm_as_strip(parm),
            target
        )

    def test_eval_strip_as_string_single(self):
        node = OBJ.node("test_eval_as_strip/node")
        parm = node.parm("strip_normal")

        target = ('bar',)

        self.assertEqual(
            ht.inline.api.eval_parm_strip_as_string(parm),
            target
        )

    def test_eval_strip_as_string_toggle(self):
        node = OBJ.node("test_eval_as_strip/node")
        parm = node.parm("strip_toggle")

        target = ('foo', 'hello', 'world')

        self.assertEqual(
            ht.inline.api.eval_parm_strip_as_string(parm),
            target
        )

    # =========================================================================
    # MULTIPARMS
    # =========================================================================

    def test_is_multiparm(self):
        node = OBJ.node("test_is_multiparm/object_merge")
        parm = node.parm("numobj")

        self.assertTrue(ht.inline.api.is_parm_multiparm(parm))

        parmTuple = node.parmTuple("numobj")
        self.assertTrue(ht.inline.api.is_parm_multiparm(parmTuple))

    def test_is_multiparmFalse(self):
        node = OBJ.node("test_is_multiparm/object_merge")
        parm = node.parm("objpath1")

        self.assertFalse(ht.inline.api.is_parm_multiparm(parm))

        parm_tuple = node.parmTuple("objpath1")
        self.assertFalse(ht.inline.api.is_parm_multiparm(parm_tuple))

    def test_get_multiparm_instances_per_item(self):
        node = OBJ.node("test_get_multiparm_instances_per_item/object_merge")
        parm = node.parm("numobj")

        self.assertEqual(ht.inline.api.get_multiparm_instances_per_item(parm), 4)

        parm_tuple = node.parmTuple("numobj")
        self.assertEqual(ht.inline.api.get_multiparm_instances_per_item(parm_tuple), 4)

    def test_get_multiparm_start_offset0(self):
        node = OBJ.node("test_get_multiparm_start_offset/add")
        parm = node.parm("points")

        self.assertEqual(ht.inline.api.get_multiparm_start_offset(parm), 0)

        parm_tuple = node.parmTuple("points")
        self.assertEqual(ht.inline.api.get_multiparm_start_offset(parm_tuple), 0)

    def test_get_multiparm_start_offset1(self):
        node = OBJ.node("test_get_multiparm_start_offset/object_merge")
        parm = node.parm("numobj")

        self.assertEqual(ht.inline.api.get_multiparm_start_offset(parm), 1)

        parm_tuple = node.parmTuple("numobj")
        self.assertEqual(ht.inline.api.get_multiparm_start_offset(parm_tuple), 1)

    def test_get_multiparm_instance_index(self):
        target = (2, )

        node = OBJ.node("test_get_multiparm_instance_index/object_merge")
        parm = node.parm("objpath2")

        self.assertEqual(ht.inline.api.get_multiparm_instance_index(parm), target)

        parm_tuple = node.parmTuple("objpath2")

        self.assertEqual(ht.inline.api.get_multiparm_instance_index(parm_tuple), target)

    def test_get_multiparm_instance_index_fail(self):
        node = OBJ.node("test_get_multiparm_instance_index/object_merge")
        parm = node.parm("numobj")

        with self.assertRaises(ValueError):
            ht.inline.api.get_multiparm_instance_index(parm)

        parm_tuple = node.parmTuple("numobj")

        with self.assertRaises(ValueError):
            ht.inline.api.get_multiparm_instance_index(parm_tuple)

    def test_get_multiparm_instances(self):
        node = OBJ.node("test_get_multiparm_instances/null1")

        target = (
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

        parm_tuple = node.parmTuple("things")

        instances = ht.inline.api.get_multiparm_instances(parm_tuple)

        self.assertEqual(instances, target)

    def test_get_multiparm_instance_values(self):
        node = OBJ.node("test_get_multiparm_instance_values/null1")

        target = (
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

        parm_tuple = node.parmTuple("things")

        values = ht.inline.api.get_multiparm_instance_values(parm_tuple)

        self.assertEqual(values, target)

    def test_eval_multiparm_instance(self):
        node = OBJ.node("test_get_multiparm_instance_values/null1")

        # Ints
        self.assertEqual(ht.inline.api.eval_multiparm_instance(node, "foo#", 0), 1)
        self.assertEqual(ht.inline.api.eval_multiparm_instance(node, "foo#", 1), 5)

        with self.assertRaises(IndexError):
            ht.inline.api.eval_multiparm_instance(node, "foo#", 2)

        # Floats
        self.assertEqual(ht.inline.api.eval_multiparm_instance(node, "bar#", 0), (2.0, 3.0, 4.0))
        self.assertEqual(ht.inline.api.eval_multiparm_instance(node, "bar#", 1), (6.0, 7.0, 8.0))

        with self.assertRaises(IndexError):
            ht.inline.api.eval_multiparm_instance(node, "bar#", 2)

        # Strings
        self.assertEqual(ht.inline.api.eval_multiparm_instance(node, "hello#", 0), "foo")
        self.assertEqual(ht.inline.api.eval_multiparm_instance(node, "hello#", 1), "bar")

        with self.assertRaises(IndexError):
            ht.inline.api.eval_multiparm_instance(node, "hello#", 2)

    # =========================================================================
    # NODES AND NODE TYPES
    # =========================================================================

    def test_disconnect_all_outputs(self):
        node = OBJ.node("test_disconnect_all_outputs/file")

        ht.inline.api.disconnect_all_outputs(node)

        self.assertEqual(len(node.outputs()), 0)

    def test_disconnect_all_inputs(self):
        node = OBJ.node("test_disconnect_all_inputs/merge")

        ht.inline.api.disconnect_all_inputs(node)

        self.assertEqual(len(node.inputs()), 0)

    def node_is_contained_by(self):
        node = OBJ.node("is_contained_by")

        box = node.node("box")

        self.assertTrue(ht.inline.api.node_is_contained_by(box, node))

    def is_contained_by_False(self):
        node = OBJ.node("is_contained_by")

        self.assertFalse(ht.inline.api.node_is_contained_by(node, hou.node("/shop")))

    def test_author_name(self):
        node = OBJ.node("test_author_name")

        self.assertEqual(ht.inline.api.node_author_name(node), "gthompson")

    def test_set_node_type_icon(self):
        node_type = hou.nodeType(hou.objNodeTypeCategory(), "geo")
        ht.inline.api.set_node_type_icon(node_type, "SOP_box")

        self.assertEqual(node_type.icon(), "SOP_box")

    def test_set_node_type_default_icon(self):
        node_type = hou.nodeType(hou.objNodeTypeCategory(), "geo")
        ht.inline.api.set_node_type_icon(node_type, "SOP_box")

        ht.inline.api.set_node_type_default_icon(node_type)

        self.assertEqual(node_type.icon(), "OBJ_geo")

    def test_is_node_type_python(self):
        node_type = hou.nodeType(hou.sopNodeTypeCategory(), "tableimport")

        self.assertTrue(ht.inline.api.is_node_type_python(node_type))

    def test_is_node_type_python_false(self):
        node_type = hou.nodeType(hou.sopNodeTypeCategory(), "file")

        self.assertFalse(ht.inline.api.is_node_type_python(node_type))

    def test_is_node_type_subnet(self):
        node_type = hou.nodeType(hou.objNodeTypeCategory(), "subnet")

        self.assertTrue(ht.inline.api.is_node_type_subnet(node_type))

    def test_is_node_type_subnet_false(self):
        node_type = hou.nodeType(hou.objNodeTypeCategory(), "geo")

        self.assertFalse(ht.inline.api.is_node_type_subnet(node_type))

    # =========================================================================
    # VECTORS AND MATRICES
    # =========================================================================

    def test_v3ComponentAlong(self):
        v3 = hou.Vector3(1, 2, 3)

        self.assertEqual(
            ht.inline.api.vector_component_along(v3, hou.Vector3(0, 0, 15)),
            3.0
        )

    def test_v3Project(self):
        v3 = hou.Vector3(-1.3, 0.5, 7.6)
        proj = ht.inline.api.vector_project_along(v3, hou.Vector3(2.87, 3.1, -0.5))

        result = hou.Vector3(-0.948531, -1.02455, 0.165249)

        self.assertTrue(proj.isAlmostEqual(result))

    def test_v2IsNan(self):
        nan = float('nan')
        vec = hou.Vector2(nan, 1)

        self.assertTrue(ht.inline.api.vector_contains_nans(vec))

    def test_v3IsNan(self):
        nan = float('nan')
        vec = hou.Vector3(6.5, 1, nan)

        self.assertTrue(ht.inline.api.vector_contains_nans(vec))

    def test_v4IsNan(self):
        nan = float('nan')
        vec = hou.Vector4(-4, 5, -0, nan)

        self.assertTrue(ht.inline.api.vector_contains_nans(vec))

    def test_get_vector_dual(self):
        target = hou.Matrix3(((0, -3, 2), (3, 0, -1), (-2, 1, 0)))

        vec = hou.Vector3(1, 2, 3)

        self.assertEqual(ht.inline.api.vector_compute_dual(vec), target)

    def test_m3IdentIsIdentity(self):
        m3 = hou.Matrix3()
        m3.setToIdentity()

        self.assertTrue(ht.inline.api.is_identity_matrix(m3))

    def test_m3ZeroIsNotIdentity(self):
        m3 = hou.Matrix3()

        self.assertFalse(ht.inline.api.is_identity_matrix(m3))

    def test_m4IdentIsIdentity(self):
        m4 = hou.Matrix4()
        m4.setToIdentity()

        self.assertTrue(ht.inline.api.is_identity_matrix(m4))

    def test_m4ZeroIsNotIdentity(self):
        m4 = hou.Matrix4()

        self.assertFalse(ht.inline.api.is_identity_matrix(m4))

    def test_m4SetTranslates(self):
        translates = hou.Vector3(1,2,3)
        identity = hou.hmath.identityTransform()
        ht.inline.api.set_matrix_translates(identity, translates)

        self.assertEqual(
            identity.extractTranslates(),
            translates
        )

    def test_build_lookat_matrix(self):
        target = hou.Matrix3(
            (
                (0.70710678118654746, -0.0, 0.70710678118654746),
                (0.0, 1.0, 0.0),
                (-0.70710678118654746, 0.0, 0.70710678118654746)
            )
        )

        mat = ht.inline.api.build_lookat_matrix(
            hou.Vector3(0, 0, 1),
            hou.Vector3(1, 0, 0),
            hou.Vector3(0, 1, 0)
        )

        self.assertEqual(mat, target)

    def test_build_instance_matrix(self):
        target = hou.Matrix4(
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

        mat = ht.inline.api.build_instance_matrix(
            hou.Vector3(-1, 2, 4),
            hou.Vector3(1, 1, 1),
            pscale=1.5,
            up_vector=hou.Vector3(1, 1, -1)
        )

        self.assertEqual(mat, target)

    def test_build_instance_matrixOrient(self):
        target = hou.Matrix4(
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

        mat = ht.inline.api.build_instance_matrix(
            hou.Vector3(-1, 2, 4),
            orient=hou.Quaternion(0.3, -1.7, -0.9, -2.7)
        )

        self.assertEqual(mat, target)

    # =========================================================================
    # DIGITAL ASSETS
    # =========================================================================

    def test_get_node_message_nodes(self):
        node = OBJ.node("test_message_nodes/solver")

        target = (node.node("d/s"),)

        self.assertEqual(ht.inline.api.get_node_message_nodes(node), target)

    def test_get_node_editable_nodes(self):
        node = OBJ.node("test_message_nodes/solver")

        target = (node.node("d/s"),)

        self.assertEqual(ht.inline.api.get_node_editable_nodes(node), target)

    def test_get_node_dive_target(self):
        node = OBJ.node("test_message_nodes/solver")

        target = node.node("d/s")

        self.assertEqual(ht.inline.api.get_node_dive_target(node), target)

    def test_get_node_representative_node(self):
        node = OBJ.node("test_representative_node")

        target = node.node("stereo_camera")

        self.assertEqual(ht.inline.api.get_node_representative_node(node), target)

    def test_is_contained_by__true(self):
        source_node = OBJ.node("test_is_contained_by/subnet/box")
        target_node = OBJ.node("test_is_contained_by")

        self.assertTrue(ht.inline.api.node_is_contained_by(source_node, target_node))

    def test_is_contained_by__false(self):
        source_node = OBJ.node("test_is_contained_by/subnet/box")
        target_node = OBJ.node("test_is_contained_by/other_subnet")

        self.assertFalse(ht.inline.api.node_is_contained_by(source_node, target_node))

    def test_asset_file_meta_source(self):
        target = "Scanned Asset Library Directories"
        path = hou.expandString("$HH/otls/OPlibSop.hda")

        self.assertEqual(ht.inline.api.asset_file_meta_source(path), target)

    def test_get_definition_meta_source(self):
        target = "Scanned Asset Library Directories"

        node_type = hou.nodeType(hou.sopNodeTypeCategory(), "explodedview")

        self.assertEqual(ht.inline.api.get_definition_meta_source(node_type.definition()), target)

    def test_libraries_in_meta_source(self):
        libs = ht.inline.api.libraries_in_meta_source("Scanned Asset Library Directories")
        self.assertTrue(len(libs) > 0)

    def test_is_dummy_definition(self):
        geo = OBJ.createNode("geo")
        subnet = geo.createNode("subnet")

        # Create a new digital asset.
        asset = subnet.createDigitalAsset("dummyop", "Embedded", "Dummy")
        node_type = asset.type()

        # Not a dummy so far.
        self.assertFalse(ht.inline.api.is_dummy_definition(node_type.definition()))

        # Destroy the definition.
        node_type.definition().destroy()

        # Now it's a dummy.
        self.assertTrue(ht.inline.api.is_dummy_definition(node_type.definition()))

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

# =============================================================================

if __name__ == '__main__':
    unittest.main()

