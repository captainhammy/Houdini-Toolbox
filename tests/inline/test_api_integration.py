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
        hou.hipFile.load(os.path.join(THIS_DIR, "test_inline.hip"))

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

    def test_getVariable(self):
        hip_name = hou.getVariable("HIPNAME")

        self.assertEqual(hip_name, os.path.splitext(os.path.basename(hou.hipFile.path()))[0])

    def test_setVariable(self):
        value = 22
        hou.setVariable("awesome", value)

        self.assertEqual(hou.getVariable("awesome"), 22)

    def test_getVariableNames(self):
        variableNames = hou.getVariableNames()

        self.assertTrue("ACTIVETAKE" in variableNames)

    def test_getDirtyVariableNames(self):
        variableNames = hou.getVariableNames()

        dirtyVariableNames = hou.getVariableNames(dirty=True)

        self.assertNotEqual(variableNames, dirtyVariableNames)

    def test_unsetVariable(self):
        hou.setVariable("tester", 10)
        hou.unsetVariable("tester")

        self.assertTrue(hou.getVariable("tester") is None)

    def test_varChange(self):
        parm = hou.parm("/obj/test_varChange/file1/file")

        string = "something_$VARCHANGE.bgeo"

        parm.set(string)

        path = parm.eval()

        self.assertEqual(path, string.replace("$VARCHANGE", ""))

        hou.setVariable("VARCHANGE", 22)

        hou.varChange()

        newPath = parm.eval()

        # Test the paths aren't the same.
        self.assertNotEqual(path, newPath)

        # Test the update was successful.
        self.assertEqual(newPath, string.replace("$VARCHANGE", "22"))

    def test_expandRange(self):
        values = hou.expandRange("0-5 10-20:2 64 65-66")
        target = (0, 1, 2, 3, 4, 5, 10, 12, 14, 16, 18, 20, 64, 65, 66)

        self.assertEqual(values, target)

    def test_isReadOnly(self):
        geo = get_obj_geo("test_isReadOnly")

        self.assertTrue(geo.isReadOnly)

    def test_isReadOnlyFalse(self):
        geo = hou.Geometry()
        self.assertFalse(geo.isReadOnly())

    def test_numPoints(self):
        geo = get_obj_geo("test_numPoints")

        self.assertEqual(geo.numPoints(), 5000)

    def test_numPrims(self):
        geo = get_obj_geo("test_numPrims")

        self.assertEqual(geo.numPrims(), 12)

    def test_packGeometry(self):
        geo = get_obj_geo("test_packGeometry")

        prim = geo.prims()[0]

        self.assertTrue(isinstance(prim, hou.PackedGeometry))

    def test_sortByAttribute(self):
        geo = get_obj_geo_copy("test_sortByAttribute")

        attrib = geo.findPrimAttrib("id")

        geo.sortByAttribute(attrib)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, range(10))

    def test_sortByAttributeReversed(self):
        geo = get_obj_geo_copy("test_sortByAttribute")

        attrib = geo.findPrimAttrib("id")

        geo.sortByAttribute(attrib, reverse=True)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, list(reversed(range(10))))

    def test_sortByAttributeInvalidIndex(self):
        geo = get_obj_geo_copy("test_sortByAttribute")

        attrib = geo.findPrimAttrib("id")

        with self.assertRaises(IndexError):
            geo.sortByAttribute(attrib, 1)

    def test_sortByAttributeDetail(self):
        geo = get_obj_geo_copy("test_sortByAttribute")

        attrib = geo.findGlobalAttrib("varmap")

        with self.assertRaises(hou.OperationFailed):
            geo.sortByAttribute(attrib)

    def test_sortAlongAxisPoints(self):
        geo = get_obj_geo_copy("test_sortAlongAxisPoints")

        geo.sortAlongAxis(hou.geometryType.Points, 0)

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, range(10))

    def test_sortAlongAxisPrims(self):
        geo = get_obj_geo_copy("test_sortAlongAxisPrims")

        geo.sortAlongAxis(hou.geometryType.Primitives, 2)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, range(10))

    def test_sortByValues(self):
        # TODO: Test this.
        pass

    def test_sortRandomlyPoints(self):
        SEED = 11
        TARGET = [5, 9, 3, 8, 0, 2, 6, 1, 4, 7]

        geo = get_obj_geo_copy("test_sortRandomlyPoints")
        geo.sortRandomly(hou.geometryType.Points, SEED)

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_sortRandomlyPrims(self):
        SEED = 345
        TARGET = [4, 0, 9, 2, 1, 8, 3, 6, 7, 5]

        geo = get_obj_geo_copy("test_sortRandomlyPrims")
        geo.sortRandomly(hou.geometryType.Primitives, SEED)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_shiftElementsPoints(self):
        OFFSET = -18
        TARGET = [8, 9, 0, 1, 2, 3, 4, 5, 6, 7]

        geo = get_obj_geo_copy("test_shiftElementsPoints")
        geo.shiftElements(hou.geometryType.Points, OFFSET)

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_shiftElementsPrims(self):
        OFFSET = 6
        TARGET = [4, 5, 6, 7, 8, 9, 0, 1, 2, 3]

        geo = get_obj_geo_copy("test_shiftElementsPrims")
        geo.shiftElements(hou.geometryType.Primitives, OFFSET)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_reverseSortPoints(self):
        TARGET = range(10)
        TARGET.reverse()

        geo = get_obj_geo_copy("test_reverseSortPoints")
        geo.reverseSort(hou.geometryType.Points)

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_reverseSortPrims(self):
        TARGET = range(10)
        TARGET.reverse()

        geo = get_obj_geo_copy("test_reverseSortPrims")
        geo.reverseSort(hou.geometryType.Primitives)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_sortByProximityPoints(self):
        TARGET = [4, 3, 5, 2, 6, 1, 7, 0, 8, 9]
        POSITION = hou.Vector3(4, 1, 2)

        geo = get_obj_geo_copy("test_sortByProximityPoints")
        geo.sortByProximityToPosition(hou.geometryType.Points, POSITION)

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_sortByProximityPrims(self):
        TARGET = [6, 7, 5, 8, 4, 9, 3, 2, 1, 0]
        POSITION = hou.Vector3(3, -1, 2)

        geo = get_obj_geo_copy("test_sortByProximityPrims")
        geo.sortByProximityToPosition(hou.geometryType.Primitives, POSITION)

        values = [int(val) for val in geo.primFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_sortByVertexOrder(self):
        TARGET = range(10)

        geo = get_obj_geo_copy("test_sortByVertexOrder")
        geo.sortByVertexOrder()

        values = [int(val) for val in geo.pointFloatAttribValues("id")]

        self.assertEqual(values, TARGET)

    def test_sortByExpressionPoints(self):
        # TODO: Figure out how to test this.  Maybe include inline Python SOP?
        pass

    def test_sortByExpressionPrims(self):
        # TODO: Figure out how to test this.  Maybe include inline Python SOP?
        pass

    def test_createPointAtPosition(self):
        geo = hou.Geometry()

        point = geo.createPointAtPosition(hou.Vector3(1, 2, 3))

        self.assertEqual(point.position(), hou.Vector3(1, 2, 3))

    def test_createNPoints(self):
        geo = hou.Geometry()
        points = geo.createNPoints(15)

        self.assertEqual(points, geo.points())

    def test_createNPointsInvalidNumber(self):
        geo = hou.Geometry()

        with self.assertRaises(hou.OperationFailed):
            geo.createNPoints(-4)

    def test_mergePointGroup(self):
        geo = hou.Geometry()
        sourceGeo = get_obj_geo("test_mergePointGroup")

        group = sourceGeo.pointGroups()[0]

        geo.mergePointGroup(group)

        self.assertEqual(len(geo.iterPoints()), len(group.points()))

    def test_mergePoints(self):
        geo = hou.Geometry()
        sourceGeo = get_obj_geo("test_mergePoints")

        points = sourceGeo.globPoints("0 6 15 35-38 66")

        geo.mergePoints(points)

        self.assertEqual(len(geo.iterPoints()), len(points))

    def test_mergePrimGroup(self):
        geo = hou.Geometry()
        sourceGeo = get_obj_geo("test_mergePrimGroup")

        group = sourceGeo.primGroups()[0]

        geo.mergePrimGroup(group)

        self.assertEqual(len(geo.iterPrims()), len(group.prims()))

    def test_mergePrims(self):
        geo = hou.Geometry()
        sourceGeo = get_obj_geo("test_mergePrims")

        prims = sourceGeo.globPrims("0 6 15 35-38 66")

        geo.mergePrims(prims)

        self.assertEqual(len(geo.iterPrims()), len(prims))


    def test_copyPointAttributeValues(self):
        source = get_obj_geo("test_copyPointAttributeValues")

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

    def test_copyPrimAttributeValues(self):
        source = get_obj_geo("test_copyPrimAttributeValues")

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

    def test_pointAdjacentPolygons(self):
        geo = get_obj_geo("test_pointAdjacentPolygons")

        TARGET = geo.globPrims("1 2")

        prims = geo.iterPrims()[0].pointAdjacentPolygons()

        self.assertEqual(prims, TARGET)

    def test_edgeAdjacentPolygons(self):
        geo = get_obj_geo("test_edgeAdjacentPolygons")

        TARGET = geo.globPrims("2")

        prims = geo.iterPrims()[0].edgeAdjacentPolygons()

        self.assertEqual(prims, TARGET)

    def test_connectedPrims(self):
        geo = get_obj_geo("test_connectedPrims")

        TARGET = geo.prims()

        prims = geo.iterPoints()[4].connectedPrims()

        self.assertEqual(prims, TARGET)

    def test_connectedPoints(self):
        geo = get_obj_geo("test_connectedPoints")

        TARGET = geo.globPoints("1 3 5 7")

        points = geo.iterPoints()[4].connectedPoints()

        self.assertEqual(points, TARGET)

    def test_referencingVertices(self):
        geo = get_obj_geo("test_referencingVertices")

        TARGET = geo.globVertices("0v2 1v3 2v1 3v0")

        verts = geo.iterPoints()[4].referencingVertices()

        self.assertEqual(verts, TARGET)

    def test_pointStringTableIndices(self):
        geo = get_obj_geo("test_pointStringTableIndices")

        TARGET = (0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1)

        attr = geo.findPointAttrib("test")

        self.assertEqual(attr.stringTableIndices(), TARGET)

    def test_primStringTableIndices(self):
        geo = get_obj_geo("test_primStringTableIndices")

        TARGET = (0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4)

        attr = geo.findPrimAttrib("test")

        self.assertEqual(attr.stringTableIndices(), TARGET)

    def test_vertexStringAttribValues(self):
        geo = get_obj_geo("test_vertexStringAttribValues")

        TARGET = ('vertex0', 'vertex1', 'vertex2', 'vertex3', 'vertex4', 'vertex5', 'vertex6', 'vertex7')

        self.assertEqual(geo.vertexStringAttribValues("test"), TARGET)

    def test_setVertexStringAttribValues(self):
        TARGET = ('vertex0', 'vertex1', 'vertex2', 'vertex3', 'vertex4')

        geo = get_obj_geo_copy("test_setVertexStringAttribValues")
        attr = geo.findVertexAttrib("test")

        geo.setVertexStringAttribValues("test", TARGET)

        vals = []

        for prim in geo.prims():
            vals.extend([vert.attribValue(attr) for vert in prim.vertices()])

        self.assertEqual(tuple(vals), TARGET)

    def test_setVertexStringAttribValuesInvalidAttribute(self):
        TARGET = ('vertex0', 'vertex1', 'vertex2', 'vertex3', 'vertex4')

        geo = get_obj_geo_copy("test_setVertexStringAttribValues")

        with self.assertRaises(hou.OperationFailed):
            geo.setVertexStringAttribValues("thing", TARGET)

    def test_setVertexStringAttribValuesInvalidAttributeType(self):
        TARGET = ('vertex0', 'vertex1', 'vertex2', 'vertex3', 'vertex4')

        geo = get_obj_geo_copy("test_setVertexStringAttribValues")

        with self.assertRaises(hou.OperationFailed):
            geo.setVertexStringAttribValues("notstring", TARGET)

    def test_setPrimStringAttribValuesInvalidAttributeSize(self):
        TARGET = ('vertex0', 'vertex1', 'vertex2', 'vertex3')

        geo = get_obj_geo_copy("test_setVertexStringAttribValues")

        with self.assertRaises(hou.OperationFailed):
            geo.setVertexStringAttribValues("test", TARGET)

    def test_setSharedPointStringAttrib(self):
        TARGET = ["point0"]*5
        geo = hou.Geometry()
        geo.createNPoints(5)
        attr = geo.addAttrib(hou.attribType.Point, "test", "")

        geo.setSharedPointStringAttrib(attr.name(), "point0")

        vals = [point.attribValue(attr) for point in geo.points()]

        self.assertEqual(vals, TARGET)

    def test_setSharedPointStringAttribGroup(self):
        TARGET = ["point0"]*5 + [""]*5

        geo = hou.Geometry()

        attr = geo.addAttrib(hou.attribType.Point, "test", "")

        geo.createNPoints(5)
        group = geo.createPointGroup("group1")

        for point in geo.points():
            group.add(point)

        geo.createNPoints(5)

        geo.setSharedPointStringAttrib(attr.name(), "point0", group)

        vals = [point.attribValue(attr) for point in geo.points()]

        self.assertEqual(vals, TARGET)

    def test_setSharedPrimStringAttrib(self):
        TARGET = ["value"]*5

        geo = get_obj_geo_copy("test_setSharedPrimStringAttrib")

        attr = geo.findPrimAttrib("test")

        geo.setSharedPrimStringAttrib(attr.name(), "value")

        vals = [prim.attribValue(attr) for prim in geo.prims()]

        self.assertEqual(vals, TARGET)

    def test_setSharedPrimStringAttribGroup(self):
        TARGET = ["value"]*3 + ["", ""]

        geo = get_obj_geo_copy("test_setSharedPrimStringAttrib")

        attr = geo.findPrimAttrib("test")

        group = geo.findPrimGroup("group1")

        geo.setSharedPrimStringAttrib(attr.name(), "value", group)

        vals = [prim.attribValue(attr) for prim in geo.prims()]

        self.assertEqual(vals, TARGET)

    def test_hasEdge(self):
        geo = get_obj_geo("test_hasEdge")

        face = geo.iterPrims()[0]

        p0 = geo.iterPoints()[0]
        p1 = geo.iterPoints()[1]

        self.assertTrue(face.hasEdge(p0, p1))

    def test_hasEdgeFail(self):
        geo = get_obj_geo("test_hasEdge")

        face = geo.iterPrims()[0]

        p0 = geo.iterPoints()[0]
        p2 = geo.iterPoints()[2]

        self.assertTrue(face.hasEdge(p0, p2))

    def test_sharedEdges(self):
        geo = get_obj_geo("test_sharedEdges")

        pr0, pr1 = geo.prims()

        edges = pr0.sharedEdges(pr1)

        pt2 = geo.iterPoints()[2]
        pt3 = geo.iterPoints()[3]

        edge = geo.findEdge(pt2, pt3)

        self.assertEqual(edges, (edge,))


    def test_insertVertex(self):
        geo = get_obj_geo_copy("test_insertVertex")

        face = geo.iterPrims()[0]

        pt = geo.createPointAtPosition(hou.Vector3(0.5, 0, 0.5))

        face.insertVertex(pt, 2)

        self.assertEqual(face.vertex(2).point(), pt)

    def test_insertVertexNegativeIndex(self):
        geo = get_obj_geo_copy("test_insertVertex")

        face = geo.iterPrims()[0]

        pt = geo.createPointAtPosition(hou.Vector3(0.5, 0, 0.5))

        with self.assertRaises(IndexError):
            face.insertVertex(pt, -1)

    def test_insertVertexInvalidIndex(self):
        geo = get_obj_geo_copy("test_insertVertex")

        face = geo.iterPrims()[0]

        pt = geo.createPointAtPosition(hou.Vector3(0.5, 0, 0.5))

        with self.assertRaises(IndexError):
            face.insertVertex(pt, 10)

    def test_deleteVertex(self):
        geo = get_obj_geo_copy("test_deleteVertex")

        face = geo.iterPrims()[0]

        face.deleteVertex(3)

        self.assertEqual(len(face.vertices()), 3)

    def test_deleteVertexNegativeIndex(self):
        geo = get_obj_geo_copy("test_deleteVertex")

        face = geo.iterPrims()[0]

        with self.assertRaises(IndexError):
            face.deleteVertex(-1)

    def test_deleteVertexInvalidIndex(self):
        geo = get_obj_geo_copy("test_deleteVertex")

        face = geo.iterPrims()[0]

        with self.assertRaises(IndexError):
            face.deleteVertex(10)

    def test_setPoint(self):
        geo = get_obj_geo_copy("test_setPoint")

        face = geo.iterPrims()[0]
        pt = geo.iterPoints()[4]

        face.setPoint(3, pt)

        self.assertEqual(face.vertex(3).point().number(), 4)

    def test_setPointNegativeIndex(self):
        geo = get_obj_geo_copy("test_setPoint")

        face = geo.iterPrims()[0]
        pt = geo.iterPoints()[4]

        with self.assertRaises(IndexError):
            face.setPoint(-1, pt)

    def test_setPointInvalidIndex(self):
        geo = get_obj_geo_copy("test_setPoint")

        face = geo.iterPrims()[0]
        pt = geo.iterPoints()[4]

        with self.assertRaises(IndexError):
            face.setPoint(10, pt)

    def test_baryCenter(self):
        TARGET = hou.Vector3(1.5, 1, -1)
        geo = get_obj_geo_copy("test_baryCenter")

        prim = geo.iterPrims()[0]

        self.assertEqual(prim.baryCenter(), TARGET)

    def test_primitiveArea(self):
        TARGET = 4.375
        geo = get_obj_geo_copy("test_primitiveArea")

        prim = geo.iterPrims()[0]

        self.assertEqual(prim.area(), TARGET)

    def test_perimeter(self):
        TARGET = 6.5
        geo = get_obj_geo_copy("test_perimeter")

        prim = geo.iterPrims()[0]

        self.assertEqual(prim.perimeter(), TARGET)

    def test_reversePrim(self):
        TARGET = hou.Vector3(0, -1, 0)
        geo = get_obj_geo_copy("test_reversePrim")

        prim = geo.iterPrims()[0]
        prim.reverse()

        self.assertEqual(prim.normal(), TARGET)

    def test_makeUnique(self):
        TARGET = 28
        geo = get_obj_geo_copy("test_makeUnique")

        prim = geo.iterPrims()[4]
        prim.makeUnique()

        self.assertEqual(len(geo.iterPoints()), TARGET)

    def test_primBoundingBox(self):
        TARGET = hou.BoundingBox(-0.75, 0, -0.875, 0.75, 1.5, 0.875)
        geo = get_obj_geo_copy("test_primBoundingBox")

        prim = geo.iterPrims()[0]

        self.assertEqual(prim.boundingBox(), TARGET)

    def test_computePointNormals(self):
        geo = get_obj_geo_copy("test_computePointNormals")

        geo.computePointNormals()

        self.assertNotEqual(geo.findPointAttrib("N"), None)

    def test_addPointNormalAttribute(self):
        geo = get_obj_geo_copy("test_addPointNormalAttribute")

        self.assertNotEqual(geo.addPointNormals(), None)

    def test_addPointVelocityAttribute(self):
        geo = get_obj_geo_copy("test_addPointVelocityAttribute")

        self.assertNotEqual(geo.addPointVelocity(), None)

    def test_addColorAttributePoint(self):
        geo = get_obj_geo_copy("test_addColorAttribute")

        result = geo.addColorAttribute(hou.attribType.Point)

        self.assertNotEqual(result, None)

    def test_addColorAttributePrim(self):
        geo = get_obj_geo_copy("test_addColorAttribute")

        result = geo.addColorAttribute(hou.attribType.Prim)

        self.assertNotEqual(result, None)

    def test_addColorAttributeVertex(self):
        geo = get_obj_geo_copy("test_addColorAttribute")

        result = geo.addColorAttribute(hou.attribType.Vertex)

        self.assertNotEqual(result, None)

    def test_addColorAttributePoint(self):
        geo = get_obj_geo_copy("test_addColorAttribute")

        with self.assertRaises(hou.TypeError):
            geo.addColorAttribute(hou.attribType.Global)

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

    def test_clipBelow(self):
        geo = get_obj_geo_copy("test_clipBelow")

        origin = hou.Vector3(0, -0.7, -0.9)

        direction = hou.Vector3(-0.6, 0.1, -0.8)

        geo.clip(origin, direction, 0.6, below=True)

        self.assertEqual(len(geo.iterPrims()), 61)

        self.assertEqual(len(geo.iterPoints()), 81)

    def test_clipGroup(self):
        geo = get_obj_geo_copy("test_clipGroup")

        group = geo.primGroups()[0]

        origin = hou.Vector3(-1.3, -1.5, 1.2)

        direction = hou.Vector3(0.8, 0.02, 0.5)

        geo.clip(origin, direction, -0.3, group=group)

        self.assertEqual(len(geo.iterPrims()), 74)

        self.assertEqual(len(geo.iterPoints()), 98)

    def test_destroyEmptyPointGroups(self):
        geo = hou.Geometry()

        geo.createPointGroup("empty")

        geo.destroyEmptyGroups(hou.attribType.Point)

        self.assertEqual(len(geo.pointGroups()), 0)

    def test_destroyEmptyPrimGroups(self):
        geo = hou.Geometry()

        geo.createPrimGroup("empty")

        geo.destroyEmptyGroups(hou.attribType.Prim)

        self.assertEqual(len(geo.primGroups()), 0)

    def test_destroyUnusedPoints(self):
        geo = get_obj_geo_copy("test_destroyUnusedPoints")

        geo.destroyUnusedPoints()

        self.assertEqual(len(geo.iterPoints()), 20)

    def test_destroyUnusedPointsGroup(self):
        geo = get_obj_geo_copy("test_destroyUnusedPointsGroup")

        group = geo.pointGroups()[0]

        geo.destroyUnusedPoints(group)

        self.assertEqual(len(geo.iterPoints()), 3729)

    def test_consolidatePoints(self):
        geo = get_obj_geo_copy("test_consolidatePoints")

        geo.consolidatePoints()

        self.assertEqual(len(geo.iterPoints()), 100)

    def test_consolidatePointsDist(self):
        geo = get_obj_geo_copy("test_consolidatePointsDist")

        geo.consolidatePoints(3)

        self.assertEqual(len(geo.iterPoints()), 16)

    def test_consolidatePointsGroup(self):
        geo = get_obj_geo_copy("test_consolidatePointsGroup")

        group = geo.pointGroups()[0]

        geo.consolidatePoints(group=group)

        self.assertEqual(len(geo.iterPoints()), 212)

    def test_uniquePoints(self):
        geo = get_obj_geo_copy("test_uniquePoints")

        geo.uniquePoints()

        self.assertEqual(len(geo.iterPoints()), 324)

    def test_uniquePointsPointGroup(self):
        geo = get_obj_geo_copy("test_uniquePointsPointGroup")

        group = geo.pointGroups()[0]
        geo.uniquePoints(group)

        self.assertEqual(len(geo.iterPoints()), 195)


    def test_renamePointGroup(self):
        geo = get_obj_geo_copy("test_renamePointGroup")

        group = geo.pointGroups()[0]

        result = geo.renameGroup(group, "test_group")

        self.assertTrue(result is not None)
        self.assertTrue(result.name() == "test_group")


    def test_renamePointGroupSameName(self):
        geo = get_obj_geo_copy("test_renamePointGroup")

        group = geo.pointGroups()[0]
        name = group.name()

        with self.assertRaises(hou.OperationFailed):
            geo.renameGroup(group, name)

    def test_renamePrimGroup(self):
        geo = get_obj_geo_copy("test_renamePrimGroup")

        group = geo.primGroups()[0]

        result = geo.renameGroup(group, "test_group")

        self.assertTrue(result is not None)
        self.assertTrue(result.name() == "test_group")

    def test_renamePrimGroupSameName(self):
        geo = get_obj_geo_copy("test_renamePrimGroup")

        group = geo.primGroups()[0]
        name = group.name()

        with self.assertRaises(hou.OperationFailed):
            geo.renameGroup(group, name)

    def test_renameEdgeGroup(self):
        geo = get_obj_geo_copy("test_renameEdgeGroup")

        group = geo.edgeGroups()[0]

        result = geo.renameGroup(group, "test_group")

        self.assertTrue(result is not None)
        self.assertTrue(result.name() == "test_group")

    def test_renameEdgeGroupSameName(self):
        geo = get_obj_geo_copy("test_renameEdgeGroup")

        group = geo.edgeGroups()[0]
        name = group.name()

        with self.assertRaises(hou.OperationFailed):
            geo.renameGroup(group, name)

    def test_groupBoundingBoxPoint(self):
        TARGET = hou.BoundingBox(-4, 0, -1, -2, 0, 2)

        geo = get_obj_geo("test_groupBoundingBoxPoint")

        group = geo.pointGroups()[0]
        bbox = group.boundingBox()

        self.assertEqual(bbox, TARGET)

    def test_groupBoundingBoxPrim(self):
        TARGET = hou.BoundingBox(-5, 0, -4, 4, 0, 5)

        geo = get_obj_geo("test_groupBoundingBoxPrim")

        group = geo.primGroups()[0]
        bbox = group.boundingBox()

        self.assertEqual(bbox, TARGET)

    def test_groupBoundingBoxEdge(self):
        TARGET = hou.BoundingBox(-5, 0, -5, 4, 0, 5)

        geo = get_obj_geo("test_groupBoundingBoxEdge")

        group = geo.edgeGroups()[0]
        bbox = group.boundingBox()

        self.assertEqual(bbox, TARGET)

    def test_pointGroupSize(self):
        geo = get_obj_geo("test_pointGroupSize")

        group = geo.pointGroups()[0]

        self.assertEqual(group.size(), 12)
        self.assertEqual(len(group), 12)

    def test_primGroupSize(self):
        geo = get_obj_geo("test_primGroupSize")

        group = geo.primGroups()[0]

        self.assertEqual(group.size(), 39)
        self.assertEqual(len(group), 39)

    def test_edgeGroupSize(self):
        geo = get_obj_geo("test_edgeGroupSize")

        group = geo.edgeGroups()[0]

        self.assertEqual(group.size(), 52)
        self.assertEqual(len(group), 52)

    def test_togglePoint(self):
        geo = get_obj_geo_copy("test_togglePoint")

        group = geo.pointGroups()[0]
        point = geo.iterPoints()[0]

        group.toggle(point)

        self.assertTrue(group.contains(point))

    def test_togglePrim(self):
        geo = get_obj_geo_copy("test_togglePrim")

        group = geo.primGroups()[0]
        prim = geo.iterPrims()[0]

        group.toggle(prim)

        self.assertTrue(group.contains(prim))

    def test_toggleEntriesPoint(self):
        geo = get_obj_geo_copy("test_toggleEntriesPoint")

        vals = geo.globPoints(" ".join([str(val) for val in range(1, 100, 2)]))

        group = geo.pointGroups()[0]
        group.toggleEntries()

        self.assertEquals(group.points(), vals)

    def test_toggleEntriesPrim(self):
        geo = get_obj_geo_copy("test_toggleEntriesPrim")

        vals = geo.globPrims(" ".join([str(val) for val in range(0, 100, 2)]))

        group = geo.primGroups()[0]
        group.toggleEntries()

        self.assertEquals(group.prims(), vals)

    def test_toggleEntriesEdge(self):
        geo = get_obj_geo_copy("test_toggleEntriesEdge")

        group = geo.edgeGroups()[0]
        group.toggleEntries()

        self.assertEquals(len(group.edges()),  20)

    def test_copyPointGroup(self):
        geo = get_obj_geo_copy("test_copyPointGroup")

        group = geo.pointGroups()[0]

        new_group = group.copy("new_group")

        self.assertEquals(group.points(), new_group.points())

    def test_copyPointGroupSameName(self):
        geo = get_obj_geo_copy("test_copyPointGroup")

        group = geo.pointGroups()[0]

        with self.assertRaises(hou.OperationFailed):
            group.copy(group.name())

    def test_copyPointGroupExisting(self):
        geo = get_obj_geo_copy("test_copyPointGroupExisting")

        group = geo.pointGroups()[-1]

        other_group = geo.pointGroups()[0]

        with self.assertRaises(hou.OperationFailed):
            group.copy(other_group.name())

    def test_copyPrimGroup(self):
        geo = get_obj_geo_copy("test_copyPrimGroup")

        group = geo.primGroups()[0]

        new_group = group.copy("new_group")

        self.assertEquals(group.prims(), new_group.prims())

    def test_copyPrimGroupSameName(self):
        geo = get_obj_geo_copy("test_copyPrimGroup")

        group = geo.primGroups()[0]

        with self.assertRaises(hou.OperationFailed):
            group.copy(group.name())

    def test_copyPrimGroupExisting(self):
        geo = get_obj_geo_copy("test_copyPrimGroupExisting")

        group = geo.primGroups()[-1]

        other_group = geo.primGroups()[0]

        with self.assertRaises(hou.OperationFailed):
            group.copy(other_group.name())

    def test_pointGroupContainsAny(self):
        geo = get_obj_geo_copy("test_pointGroupContainsAny")

        group1 = geo.pointGroups()[0]
        group2 = geo.pointGroups()[1]

        self.assertTrue(group1.containsAny(group2))

    def test_pointGroupContainsAnyFalse(self):
        geo = get_obj_geo_copy("test_pointGroupContainsAnyFalse")

        group1 = geo.pointGroups()[0]
        group2 = geo.pointGroups()[1]

        self.assertFalse(group1.containsAny(group2))

    def test_primGroupContainsAny(self):
        geo = get_obj_geo_copy("test_primGroupContainsAny")

        group1 = geo.primGroups()[0]
        group2 = geo.primGroups()[1]

        self.assertTrue(group1.containsAny(group2))

    def test_primGroupContainsAnyFalse(self):
        geo = get_obj_geo_copy("test_primGroupContainsAnyFalse")

        group1 = geo.primGroups()[0]
        group2 = geo.primGroups()[1]

        self.assertFalse(group1.containsAny(group2))

    def test_convertPrimToPointGroup(self):
        geo = get_obj_geo_copy("test_convertPrimToPointGroup")

        group = geo.primGroups()[0]

        new_group = group.convertToPointGroup()

        self.assertEqual(len(new_group.points()), 12)

        # Check source group was deleted.
        self.assertEqual(len(geo.primGroups()), 0)

    def test_convertPrimToPointGroupWithName(self):
        geo = get_obj_geo_copy("test_convertPrimToPointGroup")

        group = geo.primGroups()[0]

        new_group = group.convertToPointGroup("new_group")

        self.assertEqual(new_group.name(), "new_group")

    def test_convertPrimToPointGroupNoDestroy(self):
        geo = get_obj_geo_copy("test_convertPrimToPointGroup")

        group = geo.primGroups()[0]

        new_group = group.convertToPointGroup(destroy=False)

        # Check source group wasn't deleted.
        self.assertEqual(len(geo.primGroups()), 1)

    def test_convertPointToPrimGroup(self):
        geo = get_obj_geo_copy("test_convertPointToPrimGroup")

        group = geo.pointGroups()[0]

        new_group = group.convertToPrimGroup()

        self.assertEqual(len(new_group.prims()), 5)

        # Check source group was deleted.
        self.assertEqual(len(geo.pointGroups()), 0)

    def test_convertPointToPrimGroupWithName(self):
        geo = get_obj_geo_copy("test_convertPointToPrimGroup")

        group = geo.pointGroups()[0]

        new_group = group.convertToPrimGroup("new_group")

        self.assertEqual(new_group.name(), "new_group")

    def test_convertPointToPrimGroupNoDestroy(self):
        geo = get_obj_geo_copy("test_convertPointToPrimGroup")

        group = geo.pointGroups()[0]

        new_group = group.convertToPrimGroup(destroy=False)

        # Check source group wasn't deleted.
        self.assertEqual(len(geo.primGroups()), 1)

    # =========================================================================
    # UNGROUPED POINTS
    # =========================================================================

    def test_hasUngroupedPoints(self):
        geo = get_obj_geo("test_hasUngroupedPoints")

        self.assertTrue(geo.hasUngroupedPoints())

    def test_hasUngroupedPointsFalse(self):
        geo = get_obj_geo("test_hasUngroupedPointsFalse")

        self.assertFalse(geo.hasUngroupedPoints())

    def test_groupUngroupedPoints(self):
        geo = get_obj_geo_copy("test_groupUngroupedPoints")

        group = geo.groupUngroupedPoints("ungrouped")

        self.assertEquals(len(group.points()), 10)

    def test_groupUngroupedPointsExistingName(self):
        geo = get_obj_geo_copy("test_groupUngroupedPoints")

        with self.assertRaises(hou.OperationFailed):
            geo.groupUngroupedPoints("group1")

    def test_groupUngroupedPointsNoName(self):
        geo = get_obj_geo_copy("test_groupUngroupedPoints")

        with self.assertRaises(hou.OperationFailed):
            geo.groupUngroupedPoints("")

    def test_groupUngroupedPointsFalse(self):
        geo = get_obj_geo_copy("test_groupUngroupedPointsFalse")

        group = geo.groupUngroupedPoints("ungrouped")

        self.assertEquals(group, None)

    # =========================================================================
    # UNGROUPED PRIMS
    # =========================================================================

    def test_hasUngroupedPrims(self):
        geo = get_obj_geo("test_hasUngroupedPrims")

        self.assertTrue(geo.hasUngroupedPrims())

    def test_hasUngroupedPrims(self):
        geo = get_obj_geo("test_hasUngroupedPrimsFalse")

        self.assertFalse(geo.hasUngroupedPrims())

    def test_groupUngroupedPrims(self):
        geo = get_obj_geo_copy("test_groupUngroupedPrims")

        group = geo.groupUngroupedPrims("ungrouped")

        self.assertEquals(len(group.prims()), 3)

    def test_groupUngroupedPrimsExistingName(self):
        geo = get_obj_geo_copy("test_groupUngroupedPrims")

        with self.assertRaises(hou.OperationFailed):
            geo.groupUngroupedPrims("group1")

    def test_groupUngroupedPrimsNoName(self):
        geo = get_obj_geo_copy("test_groupUngroupedPrims")

        with self.assertRaises(hou.OperationFailed):
            geo.groupUngroupedPrims("")

    def test_groupUngroupedPrimsFalse(self):
        geo = get_obj_geo_copy("test_groupUngroupedPrimsFalse")

        group = geo.groupUngroupedPrims("ungrouped")

        self.assertEquals(group, None)

    # =========================================================================
    # BOUNDING BOXES
    # =========================================================================

    def test_isInside(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)
        bbox2 = hou.BoundingBox(-1, -1, -1, 1, 1, 1)

        self.assertTrue(bbox1.isInside(bbox2))

    def test_isInsideFail(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)
        bbox2 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

        self.assertFalse(bbox1.isInside(bbox2))

    def test_intersects(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)
        bbox2 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

        self.assertTrue(bbox1.intersects(bbox2))

    def test_intersectsFail(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, -0.1, -0.1, -0.1)
        bbox2 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

        self.assertFalse(bbox1.intersects(bbox2))

    def test_computeIntersection(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, 0.5, 0.5, 0.5)
        bbox2 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

        self.assertTrue(bbox1.computeIntersection(bbox2))

        self.assertEqual(bbox1.minvec(), hou.Vector3())
        self.assertEqual(bbox1.maxvec(), hou.Vector3(0.5, 0.5, 0.5))

    def test_computeIntersectionFail(self):
        bbox1 = hou.BoundingBox(-0.5, -0.5, -0.5, -0.1, -0.1, -0.1)
        bbox2 = hou.BoundingBox(0, 0, 0, 0.5, 0.5, 0.5)

        self.assertFalse(bbox1.computeIntersection(bbox2))

    def test_expandBounds(self):
        bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)
        bbox.expandBounds(1, 1, 1)

        self.assertEqual(bbox.minvec(), hou.Vector3(-2, -2.75, -4))
        self.assertEqual(bbox.maxvec(), hou.Vector3(2, 2.75, 4))

    def test_addToMin(self):
        bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)
        bbox.addToMin(hou.Vector3(1, 0.25, 1))

        self.assertEqual(bbox.minvec(), hou.Vector3(0, -1.5, -2))

    def test_addToMax(self):
        bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)
        bbox.addToMax(hou.Vector3(2, 0.25, 1))

        self.assertEqual(bbox.maxvec(), hou.Vector3(3, 2, 4))

    def test_area(self):
        bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)

        self.assertEqual(bbox.area(), 80)

    def test_volume(self):
        bbox = hou.BoundingBox(-1, -1.75, -3, 1, 1.75, 3)

        self.assertEqual(bbox.volume(), 42)

    # =========================================================================
    # PARMS
    # =========================================================================

    def test_isVector(self):
        node = OBJ.node("test_isVector/node")
        parm = node.parmTuple("vec")

        self.assertTrue(parm.isVector())

    def test_isVectorFalse(self):
        node = OBJ.node("test_isVector/node")
        parm = node.parmTuple("not_vec")

        self.assertFalse(parm.isVector())

    def test_evalAsVector2(self):
        node = OBJ.node("test_evalAsVector/node")
        parm = node.parmTuple("vec2")

        self.assertEqual(parm.evalAsVector(), hou.Vector2(1,2))

    def test_evalAsVector3(self):
        node = OBJ.node("test_evalAsVector/node")
        parm = node.parmTuple("vec3")

        self.assertEqual(parm.evalAsVector(), hou.Vector3(3,4,5))

    def test_evalAsVector4(self):
        node = OBJ.node("test_evalAsVector/node")
        parm = node.parmTuple("vec4")

        self.assertEqual(parm.evalAsVector(), hou.Vector4(6,7,8,9))

    def test_evalAsVectorFail(self):
        node = OBJ.node("test_evalAsVector/node")
        parm = node.parmTuple("not_vec")

        with self.assertRaises(hou.Error):
            parm.evalAsVector()

    def test_isColor(self):
        node = OBJ.node("test_isColor/node")
        parm = node.parmTuple("color")

        self.assertTrue(parm.isColor())

    def test_isColorFalse(self):
        node = OBJ.node("test_isColor/node")
        parm = node.parmTuple("not_color")

        self.assertFalse(parm.isColor())

    def test_evalAsColor(self):
        node = OBJ.node("test_evalAsColor/node")
        parm = node.parmTuple("color")

        self.assertEqual(parm.evalAsColor(), hou.Color(0,0.5,0.5))

    def test_evalAsColorFail(self):
        node = OBJ.node("test_evalAsColor/node")
        parm = node.parmTuple("not_color")

        with self.assertRaises(hou.Error):
            parm.evalAsColor()

    def test_evalAsStripSingle(self):
        node = OBJ.node("test_evalAsStrip/node")
        parm = node.parm("strip_normal")

        TARGET = (False, True, False, False)

        self.assertEqual(
            parm.evalAsStrip(),
            TARGET
        )

    def test_evalAsStripToggle(self):
        node = OBJ.node("test_evalAsStrip/node")
        parm = node.parm("strip_toggle")

        TARGET = (True, False, True, True)

        self.assertEqual(
            parm.evalAsStrip(),
            TARGET
        )


    def test_evalStripAsStringSingle(self):
        node = OBJ.node("test_evalAsStrip/node")
        parm = node.parm("strip_normal")

        TARGET = ('bar',)

        self.assertEqual(
            parm.evalStripAsString(),
            TARGET
        )

    def test_evalStripAsStringToggle(self):
        node = OBJ.node("test_evalAsStrip/node")
        parm = node.parm("strip_toggle")

        TARGET = ('foo', 'hello', 'world')

        self.assertEqual(
            parm.evalStripAsString(),
            TARGET
        )


    # =========================================================================
    # MULTIPARMS
    # =========================================================================

    def test_isMultiParm(self):
        node = OBJ.node("test_isMultiParm/object_merge")
        parm = node.parm("numobj")

        self.assertTrue(parm.isMultiParm())

        parmTuple = node.parmTuple("numobj")
        self.assertTrue(parmTuple.isMultiParm())

    def test_isMultiParmFalse(self):
        node = OBJ.node("test_isMultiParm/object_merge")
        parm = node.parm("objpath1")

        self.assertFalse(parm.isMultiParm())

        parmTuple = node.parmTuple("objpath1")
        self.assertFalse(parmTuple.isMultiParm())

    def test_getMultiParmInstancesPerItem(self):
        node = OBJ.node("test_getMultiParmInstancesPerItem/object_merge")
        parm = node.parm("numobj")

        self.assertEqual(parm.getMultiParmInstancesPerItem(), 4)

        parm_tuple = node.parmTuple("numobj")
        self.assertEqual(parm_tuple.getMultiParmInstancesPerItem(), 4)


    def test_getMultiParmStartOffset0(self):
        node = OBJ.node("test_getMultiParmStartOffset/add")
        parm = node.parm("points")

        self.assertEqual(parm.getMultiParmStartOffset(), 0)

        parm_tuple = node.parmTuple("points")
        self.assertEqual(parm_tuple.getMultiParmStartOffset(), 0)

    def test_getMultiParmStartOffset1(self):
        node = OBJ.node("test_getMultiParmStartOffset/object_merge")
        parm = node.parm("numobj")

        self.assertEqual(parm.getMultiParmStartOffset(), 1)

        parm_tuple = node.parmTuple("numobj")
        self.assertEqual(parm_tuple.getMultiParmStartOffset(), 1)

    def test_getMultiParmInstanceIndex(self):
        TARGET = (2, )

        node = OBJ.node("test_getMultiParmInstanceIndex/object_merge")
        parm = node.parm("objpath2")

        self.assertEqual(parm.getMultiParmInstanceIndex(), TARGET)

        parm_tuple = node.parmTuple("objpath2")

        self.assertEqual(parm_tuple.getMultiParmInstanceIndex(), TARGET)

    def test_getMultiParmInstanceIndexFail(self):
        node = OBJ.node("test_getMultiParmInstanceIndex/object_merge")
        parm = node.parm("numobj")

        with self.assertRaises(hou.OperationFailed):
            parm.getMultiParmInstanceIndex()

        parm_tuple = node.parmTuple("numobj")

        with self.assertRaises(hou.OperationFailed):
            parm_tuple.getMultiParmInstanceIndex()

    def test_getMultiParmInstances(self):
        node = OBJ.node("test_getMultiParmInstances/null1")

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

        instances = parmTuple.getMultiParmInstances()

        self.assertEqual(instances, TARGET)

    def test_getMultiParmInstanceValues(self):
        node = OBJ.node("test_getMultiParmInstanceValues/null1")

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

        values = parmTuple.getMultiParmInstanceValues()

        self.assertEqual(values, TARGET)

    # =========================================================================
    # NODES AND NODE TYPES
    # =========================================================================

    def test_disconnectAllOutputs(self):
        node = OBJ.node("test_disconnectAllOutputs/file")

        node.disconnectAllOutputs()

        self.assertEqual(len(node.outputs()), 0)

    def test_disconnectAllInputs(self):
        node = OBJ.node("test_disconnectAllInputs/merge")

        node.disconnectAllInputs()

        self.assertEqual(len(node.inputs()), 0)

    def test_isContainedBy(self):
        node = OBJ.node("test_isContainedBy")

        box = node.node("box")

        self.assertTrue(box.isContainedBy(node))

    def test_isContainedByFalse(self):
        node = OBJ.node("test_isContainedBy")

        self.assertFalse(node.isContainedBy(hou.node("/shop")))

#    def test_isCompiled(self):
        # TODO: Figure out how to test this.
#        pass

    def test_authorName(self):
        node = OBJ.node("test_authorName")

        self.assertEqual(node.authorName(), "gthompson")

    def test_typeSetIcon(self):
        nodeType = hou.nodeType(hou.objNodeTypeCategory(), "geo")
        nodeType.setIcon("SOP_box")

        self.assertEqual(nodeType.icon(), "SOP_box")

    def test_typeSetDefaultIcon(self):
        nodeType = hou.nodeType(hou.objNodeTypeCategory(), "geo")
        nodeType.setIcon("SOP_box")

        nodeType.setDefaultIcon()

        self.assertEqual(nodeType.icon(), "OBJ_geo")

    def test_typeIsPython(self):
        nodeType = hou.nodeType(hou.sopNodeTypeCategory(), "tableimport")

        self.assertTrue(nodeType.isPython())

    def test_typeIsNotPython(self):
        nodeType = hou.nodeType(hou.sopNodeTypeCategory(), "file")

        self.assertFalse(nodeType.isPython())

    def test_typeIsSubnet(self):
        nodeType = hou.nodeType(hou.objNodeTypeCategory(), "subnet")

        self.assertTrue(nodeType.isSubnetType())

    def test_typeIsNotSubnet(self):
        nodeType = hou.nodeType(hou.objNodeTypeCategory(), "geo")

        self.assertFalse(nodeType.isSubnetType())

    # =========================================================================
    # VECTORS AND MATRICES
    # =========================================================================

    def test_v3ComponentAlong(self):
        v3 = hou.Vector3(1, 2, 3)
        self.assertEqual(
            v3.componentAlong(hou.Vector3(0, 0, 15)),
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

        self.assertTrue(v2.isNan())

    def test_v3IsNan(self):
        nan = float('nan')
        v3 = hou.Vector3(6.5, 1, nan)

        self.assertTrue(v3.isNan())

    def test_v3IsNan(self):
        nan = float('nan')
        v4 = hou.Vector4(-4, 5, -0, nan)

        self.assertTrue(v4.isNan())

    def test_getDual(self):
        TARGET = hou.Matrix3(((0, -3, 2), (3, 0, -1), (-2, 1, 0)))

        v3 = hou.Vector3(1, 2, 3)

        self.assertEqual(v3.getDual(), TARGET)

    def test_m3IdentIsIdentity(self):
        m3 = hou.Matrix3()
        m3.setToIdentity()

        self.assertTrue(m3.isIdentity())

    def test_m3ZeroIsNotIdentity(self):
        m3 = hou.Matrix3()

        self.assertFalse(m3.isIdentity())

    def test_m4IdentIsIdentity(self):
        m4 = hou.Matrix4()
        m4.setToIdentity()

        self.assertTrue(m4.isIdentity())

    def test_m4ZeroIsNotIdentity(self):
        m4 = hou.Matrix4()

        self.assertFalse(m4.isIdentity())

    def test_m4SetTranslates(self):
        translates = hou.Vector3(1,2,3)
        identity = hou.hmath.identityTransform()
        identity.setTranslates(translates)

        self.assertEqual(
            identity.extractTranslates(),
            translates
        )

    def test_buildLookat(self):
        TARGET = hou.Matrix3(
            (
                (0.70710678118654746, -0.0, 0.70710678118654746),
                (0.0, 1.0, 0.0),
                (-0.70710678118654746, 0.0, 0.70710678118654746)
            )
        )

        lookAt = hou.hmath.buildLookat(
            hou.Vector3(0, 0, 1),
            hou.Vector3(1, 0, 0),
            hou.Vector3(0, 1, 0)
        )

        self.assertEqual(lookAt, TARGET)

    def test_buildInstance(self):
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

        mat = hou.hmath.buildInstance(
            hou.Vector3(-1, 2, 4),
            hou.Vector3(1, 1, 1),
            pscale = 1.5,
            up=hou.Vector3(1, 1, -1)
        )

        self.assertEqual(mat, TARGET)

    def test_buildInstanceOrient(self):
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

        mat = hou.hmath.buildInstance(
            hou.Vector3(-1, 2, 4),
            orient=hou.Quaternion(0.3, -1.7, -0.9, -2.7)
        )

        self.assertEqual(mat, TARGET)

    # =========================================================================
    # DIGITAL ASSETS
    # =========================================================================

    def test_messageNodes(self):
        node = OBJ.node("test_messageNodes/solver")

        TARGET = (node.node("d/s"),)

        self.assertEqual(node.messageNodes(), TARGET)


    def test_editableNodes(self):
        node = OBJ.node("test_messageNodes/solver")

        TARGET = (node.node("d/s"),)

        self.assertEqual(node.editableNodes(), TARGET)

    def test_diveTarget(self):
        node = OBJ.node("test_messageNodes/solver")

        TARGET = node.node("d/s")

        self.assertEqual(node.diveTarget(), TARGET)

    def test_representativeNode(self):
        node = OBJ.node("test_representativeNode")

        TARGET = node.node("stereo_camera")

        self.assertEqual(node.representativeNode(), TARGET)

    def test_isDigitalAsset(self):
        self.assertTrue(OBJ.node("test_isDigitalAsset").isDigitalAsset())

    def test_isNotDigitalAsset(self):
        self.assertFalse(OBJ.node("test_isNotDigitalAsset").isDigitalAsset())

    def test_metaSource(self):
        TARGET = "Scanned Asset Library Directories"
        path = hou.expandString("$HH/otls/OPlibSop.hda")

        self.assertEqual(hou.hda.metaSource(path), TARGET)

    def test_getMetaSource(self):
        TARGET = "Scanned Asset Library Directories"

        node_type = hou.nodeType(hou.sopNodeTypeCategory(), "explodedview")

        self.assertEqual(node_type.definition().metaSource(), TARGET)

    def test_librariesInMetaSource(self):
        libs = hou.hda.librariesInMetaSource("Scanned Asset Library Directories")
        self.assertTrue(len(libs) > 0)

    def test_isDummy(self):
        geo = OBJ.createNode("geo")
        subnet = geo.createNode("subnet")

        # Create a new digital asset.
        asset = subnet.createDigitalAsset("dummyop", "Embedded", "Dummy")
        node_type = asset.type()

        # Not a dummy so far.
        self.assertFalse(node_type.definition().isDummy())

        # Destroy the definition.
        node_type.definition().destroy()

        # Now it's a dummy.
        self.assertTrue(node_type.definition().isDummy())

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
    sourceGeo = get_obj_geo(nodePath)

    # Merge the geo to copy it.
    geo.merge(sourceGeo)

    return geo

# =============================================================================

if __name__ == '__main__':
    unittest.main()

