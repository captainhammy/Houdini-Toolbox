"""This module contains functions designed to extend the Houdini Object Model
(HOM) through the use of the inlinecpp module and regular Python.

The functions in this module are not mean to be called directly.  This module
uses Python decorators to attach the functions to the corresponding HOM classes
and modules they are meant to extend.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import ast
import ctypes
import math
import types

# Houdini Toolbox Imports
from ht.inline.lib import cpp_methods as _cpp_methods

# Houdini Imports
import hou

# =============================================================================
# GLOBALS
# =============================================================================

# Tuple of all valid attribute data types.
_ALL_ATTRIB_DATA_TYPES = (
    hou.attribData.Float,
    hou.attribData.Int,
    hou.attribData.String
)

# Tuple of all valid attribute types.
_ALL_ATTRIB_TYPES = (
    hou.attribType.Global,
    hou.attribType.Point,
    hou.attribType.Prim,
    hou.attribType.Vertex,
)

# Mapping between hou.attribData and corresponding GA_StorageClass values.
_ATTRIB_STORAGE_MAP = {
    hou.attribData.Int: 0,
    hou.attribData.Float: 1,
    hou.attribData.String: 2,
}

# Mapping between hou.attribTypes and corresponding GA_AttributeOwner values.
_ATTRIB_TYPE_MAP = {
    hou.attribType.Vertex: 0,
    hou.attribType.Point: 1,
    hou.attribType.Prim: 2,
    hou.attribType.Global: 3,
}

# Mapping between group types and corresponding GA_AttributeOwner values.
_GROUP_ATTRIB_MAP = {
    hou.PointGroup: 1,
    hou.PrimGroup: 2,
}

# Mapping between group types and corresponding GA_GroupType values.
_GROUP_TYPE_MAP = {
    hou.PointGroup: 0,
    hou.PrimGroup: 1,
    hou.EdgeGroup: 2,
}

# Mapping between geometry types and corresponding GA_AttributeOwner values.
_GEOMETRY_ATTRIB_MAP = {
    hou.Vertex: 0,
    hou.Point: 1,
    hou.Prim: 2,
    hou.Geometry: 3
}

# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

def _build_c_double_array(values):
    """Convert a list of numbers to a ctypes double array."""
    arr = (ctypes.c_double * len(values))()
    arr[:] = values

    return arr


def _build_c_int_array(values):
    """Convert a list of numbers to a ctypes int array."""
    arr = (ctypes.c_int * len(values))()
    arr[:] = values

    return arr

def _build_c_string_array(values):
    """Convert a list of numbers to a ctypes char * array."""
    arr = (ctypes.c_char_p * len(values))()
    arr[:] = values

    return arr


def _clean_string_values(values):
    """Process a string list, removing empty strings."""
    return tuple([val for val in values if val])


def _find_attrib(geometry, attrib_type, name):
    """Find an attribute with a given name and type on the geometry."""
    if attrib_type == hou.attribType.Vertex:
        return geometry.findVertexAttrib(name)

    elif attrib_type == hou.attribType.Point:
        return geometry.findPointAttrib(name)

    elif attrib_type == hou.attribType.Prim:
        return geometry.findPrimAttrib(name)

    else:
        return geometry.findGlobalAttrib(name)


def _find_group(geometry, group_type, name):
    """Find a group with a given name and type.

    group_type corresponds to the integer returned by _get_group_type()

    """
    if group_type == 0:
        return geometry.findPointGroup(name)

    elif group_type == 1:
        return geometry.findPrimGroup(name)

    elif group_type == 2:
        return geometry.findEdgeGroup(name)

    else:
        raise hou.OperationFailed(
            "Invalid group type {}".format(group_type)
        )


def _get_attrib_storage(data_type):
    """Get an HDK compatible attribute storage class value."""
    return _ATTRIB_STORAGE_MAP[data_type]


def _get_attrib_owner(attribute_type):
    """Get an HDK compatible attribute owner value."""
    return _ATTRIB_TYPE_MAP[attribute_type]


def _get_attrib_owner_from_geometry_type(entity_type):
    """Get an HDK compatible attribute owner value from a geometry class.

    The type can be of hou.Geometry, hou.Point, hou.Prim (or subclasses) or hou.Vertex.

    """
    # If the class is a base class in the map then just return it.
    if entity_type in _GEOMETRY_ATTRIB_MAP:
        return _GEOMETRY_ATTRIB_MAP[entity_type]

    # If it is not in the map then it is most likely a subclass of hou.Prim,
    # such as hou.Polygon, hou.Face, hou.Volume, etc.  We will check the class
    # against being a subclass of any of our valid types and if it is, return
    # the owner of that class.
    for key, value in _GEOMETRY_ATTRIB_MAP.iteritems():
        if issubclass(entity_type, key):
            return value

    # Something went wrong so raise an exception.
    raise TypeError("Invalid entity type: {}".format(entity_type))


def _get_group_attrib_owner(group):
    """Get an HDK compatible group attribute type value."""
    try:
        return _GROUP_ATTRIB_MAP[type(group)]

    except KeyError:
        raise hou.OperationFailed("Invalid group type")


def _get_group_type(group):
    """Get an HDK compatible group type value."""
    try:
        return _GROUP_TYPE_MAP[type(group)]

    except KeyError:
        raise hou.OperationFailed("Invalid group type")


def _get_nodes_from_paths(paths):
    """Convert a list of string paths to hou.Node objects."""
    return tuple([hou.node(path) for path in paths if path])


def _get_points_from_list(geometry, point_list):
    """Convert a list of point numbers to hou.Point objects."""
    # Return a empty tuple if the point list is empty.
    if not point_list:
        return ()

    # Convert the list of integers to a space separated string.
    point_str = ' '.join([str(i) for i in point_list])

    # Glob for the specified points.
    return geometry.globPoints(point_str)


def _get_prims_from_list(geometry, prim_list):
    """Convert a list of primitive numbers to hou.Prim objects."""
    # Return a empty tuple if the prim list is empty.
    if not prim_list:
        return ()

    # Convert the list of integers to a space separated string.
    prim_str = ' '.join([str(i) for i in prim_list])

    # Glob for the specified prims.
    return geometry.globPrims(prim_str)

# =============================================================================
# FUNCTIONS
# =============================================================================

def add_to_class(*args, **kwargs):
    """This function decorator adds the function to specified classes,
    optionally specifying a different function name.

    *args:
        One of more HOM classes to extend.

    **kwargs:
        name: Set a specific name for the unbound method.

    """
    def decorator(func):
        # Iterate over each class passed in.
        for target_class in args:
            # Check if we tried to set the method name.  If so, use the
            # specified value.
            if "name" in kwargs:
                func_name = kwargs["name"]
            # If not, use the original name.
            else:
                func_name = func.__name__

            # Create a new unbound method.
            method = types.MethodType(func, None, target_class)

            # Attach the method to the class.
            setattr(target_class, func_name, method)

        # We don't really care about modifying the function so just return
        # it.
        return func

    return decorator


def add_to_module(module):
    """This function decorator adds the function to a specified module."""

    def decorator(func):
        # Simply add the function to the module object.
        setattr(module, func.__name__, func)
        return func

    return decorator

# =============================================================================

@add_to_module(hou)
def isRendering():
    """Check if Houdini is rendering or not."""
    return _cpp_methods.isRendering()


@add_to_module(hou)
def getGlobalVariableNames(dirty=False):
    """Get a tuple of all global variable names.

    If dirty is True, return only 'dirty' variables.  A dirty variable is a
    variable that has been created or modified but not updated throughout the
    session by something like the 'varchange' hscript command.

    """
    # Get all the valid variable names.
    var_names = _cpp_methods.getGlobalVariables(dirty)

    # Remove any empty names.
    return _clean_string_values(var_names)


@add_to_module(hou)
def getVariable(name):
    """Returns the value of the named variable.

    Returns None if no such variable exists.

    """
    # If the variable name isn't in list of variables, return None.
    if name not in getVariableNames():
        return None

    # Get the value of the variable.
    value = _cpp_methods.getVariable(name)

    # Try to convert it to the proper Python type.
    # Since Houdini stores all variable values as strings we use the ast module
    # to handle parsing the string and returning the proper data type.
    try:
        return ast.literal_eval(value)

    # Except against common parsing/evaluating errors and return the raw
    # value since the type will be a string.
    except SyntaxError:
        return value

    except ValueError:
        return value


@add_to_module(hou)
def getVariableNames(dirty=False):
    """Get a tuple of all available variable names.

    If dirty is True, return only 'dirty' variables.  A dirty variable is a
    variable that has been created or modified but not updated throughout the
    session by something like the 'varchange' hscript command.

    """
    # Get all the valid variable names.
    var_names = _cpp_methods.getVariableNames(dirty)

    # Remove any empty names.
    return _clean_string_values(var_names)


@add_to_module(hou)
def setVariable(name, value, local=False):
    """Set a variable."""
    _cpp_methods.setVariable(name, str(value), local)


@add_to_module(hou)
def unsetVariable(name):
    """Unset a variable.

    This function will do nothing if no such variable exists.

    """
    _cpp_methods.unsetVariable(name)


@add_to_module(hou)
def varChange():
    """Cook any operators using changed variables.

    When a variable's value changes, the OPs which reference that variable are
    not automatically cooked. Use this function to cook all OPs when a variable
    they use changes.

    """
    _cpp_methods.varChange()


@add_to_module(hou)
def expandRange(pattern):
    """Expand a string range into a tuple of values.

    This function will do string range expansion.  Examples include '0-15',
    '0 4 10-100', '1-100:2', etc.  See Houdini's documentation about geometry
    groups for more information. Wildcards are not supported.

    """
    return tuple(_cpp_methods.expandRange(pattern))


@add_to_class(hou.Geometry)
def isReadOnly(self):
    """Check if the geometry is read only."""
    # Get a GU Detail Handle for the geometry.
    handle = self._guDetailHandle()
    # Check if the handle is read only.
    result = handle.isReadOnly()
    # Destroy the handle.
    handle.destroy()

    return result


@add_to_class(hou.Geometry)
def numPoints(self):
    """Get the number of points in the geometry.

    This should be quicker than len(hou.Geometry.iterPoints()) since it uses
    the 'pointcount' intrinsic value from the detail.

    """
    return self.intrinsicValue("pointcount")


@add_to_class(hou.Geometry)
def numPrims(self):
    """Get the number of primitives in the geometry.

    This should be quicker than len(hou.Geometry.iterPrims()) since it uses
    the 'primitivecount' intrinsic value from the detail.

    """
    return self.intrinsicValue("primitivecount")


@add_to_class(hou.Geometry)
def numVertices(self):
    """Get the number of vertices in the geometry."""
    return self.intrinsicValue("vertexcount")


@add_to_class(hou.Geometry)
def packGeometry(self, source):
    """Pack the source geometry into a PackedGeometry prim in this geometry.

    This function works by packing the supplied geometry into the current
    detail, returning the new PackedGeometry primitive.

    Both hou.Geometry objects must not be read only.

    """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    # Make sure the source geometry is not read only.
    if source.isReadOnly():
        raise hou.GeometryPermissionError()

    _cpp_methods.packGeometry(source, self)

    return self.iterPrims()[-1]


@add_to_class(hou.Geometry)
def sortByAttribute(self, attribute, tuple_index=0, reverse=False):
    """Sort points, primitives or vertices based on attribute values.

    tuple_index is used to determine which index to sort by when using an
    attribute that has a size > 1. eg. to sort by P.y use tuple_index=1

    """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    # Verify the tuple index is valid.
    if tuple_index not in range(attribute.size()):
        raise IndexError("Invalid tuple index: {}".format(tuple_index))

    attrib_type = attribute.type()
    attrib_name = attribute.name()

    if attrib_type == hou.attribType.Global:
        raise hou.OperationFailed(
            "Attribute type must be point, primitive or vertex."
        )

    # Get the corresponding attribute type id.
    attrib_owner = _get_attrib_owner(attrib_type)

    _cpp_methods.sortByAttribute(
        self,
        attrib_owner,
        attrib_name,
        tuple_index,
        reverse
    )


@add_to_class(hou.Geometry)
def sortAlongAxis(self, geometry_type, axis):
    """Sort points or primitives based on increasing positions along an axis.

    The axis to sort along: (X=0, Y=1, Z=2)

    """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    # Verify the axis.
    if axis not in range(3):
        raise ValueError("Invalid axis: {}".format(axis))

    # Sort the points along an axis.
    if geometry_type == hou.geometryType.Points:
        _cpp_methods.sortAlongAxis(self, 0, axis)

    # Sort the primitives along an axis.
    elif geometry_type == hou.geometryType.Primitives:
        _cpp_methods.sortAlongAxis(self, 1, axis)

    else:
        raise hou.OperationFailed(
            "Geometry type must be points or primitives."
        )


@add_to_class(hou.Geometry)
def sortByValues(self, geometry_type, values):
    """Sort points or primitives based on a list of corresponding values.

    The list of values must be the same length as the number of geometry
    elements to be sourced.

    """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    if geometry_type == hou.geometryType.Points:
        # Check we have enough points.
        if len(values) != len(self.iterPoints()):
            raise hou.OperationFailed(
                "Length of values must equal the number of points."
            )

        # Construct a ctypes double array to pass the values.
        arr = _build_c_double_array(values)

        _cpp_methods.sortByValues(self, 0, arr)

    elif geometry_type == hou.geometryType.Primitives:
        # Check we have enough primitives.
        if len(values) != len(self.iterPrims()):
            raise hou.OperationFailed(
                "Length of values must equal the number of prims."
            )

        # Construct a ctypes double array to pass the values.
        arr = _build_c_double_array(values)

        _cpp_methods.sortByValues(self, 1, arr)

    else:
        raise hou.OperationFailed(
            "Geometry type must be points or primitives."
        )


@add_to_class(hou.Geometry)
def sortRandomly(self, geometry_type, seed=0.0):
    """Sort points or primitives randomly."""
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    if not isinstance(seed, (float, int)):
        raise TypeError(
            "Got '{}', expected 'float'.".format(type(seed).__name__)
        )

    # Randomize the point order.
    if geometry_type == hou.geometryType.Points:
        _cpp_methods.sortListRandomly(self, 0, seed)

    # Randomize the primitive order.
    elif geometry_type == hou.geometryType.Primitives:
        _cpp_methods.sortListRandomly(self, 1, seed)

    else:
        raise hou.OperationFailed(
            "Geometry type must be points or primitives."
        )


@add_to_class(hou.Geometry)
def shiftElements(self, geometry_type, offset):
    """Shift all point or primitives indices forward by an offset.

    Each point or primitive number gets the offset added to it to get its new
    number.  If this exceeds the number of points or primitives, it wraps
    around.

    """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    if not isinstance(offset, int):
        raise TypeError(
            "Got '{}', expected 'int'.".format(type(offset).__name__)
        )

    # Shift the point order.
    if geometry_type == hou.geometryType.Points:
        _cpp_methods.shiftList(self, 0, offset)

    # Shift the primitive order.
    elif geometry_type == hou.geometryType.Primitives:
        _cpp_methods.shiftList(self, 1, offset)

    else:
        raise hou.OperationFailed(
            "Geometry type must be points or primitives."
        )


@add_to_class(hou.Geometry)
def reverseSort(self, geometry_type):
    """Reverse the ordering of the points or primitives.

    The highest numbered becomes the lowest numbered, and vice versa.

    """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    # Reverse the point order.
    if geometry_type == hou.geometryType.Points:
        _cpp_methods.reverseList(self, 0)

    # Reverse the primitive order.
    elif geometry_type == hou.geometryType.Primitives:
        _cpp_methods.reverseList(self, 1)

    else:
        raise hou.OperationFailed(
            "Geometry type must be points or primitives."
        )


@add_to_class(hou.Geometry)
def sortByProximityToPosition(self, geometry_type, pos):
    """Sort elements by their proximity to a point.

    The distance to the point in space is used as a priority. The points or
    primitives are then sorted so that the 0th entity is the one closest to
    that point.

    """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    # Sort the points.
    if geometry_type == hou.geometryType.Points:
        _cpp_methods.proximityToList(self, 0, pos)

    # Sort the primitives.
    elif geometry_type == hou.geometryType.Primitives:
        _cpp_methods.proximityToList(self, 1, pos)

    else:
        raise hou.OperationFailed(
            "Geometry type must be points or primitives."
        )


@add_to_class(hou.Geometry)
def sortByVertexOrder(self):
    """Sorts points to match the order of the vertices on the primitives.

    If you have a curve whose point numbers do not increase along the curve,
    this will reorder the point numbers so they match the curve direction.

    """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    _cpp_methods.sortByVertexOrder(self)


@add_to_class(hou.Geometry)
def sortByExpression(self, geometry_type, expression):
    """Sort points or primitives based on an expression for each element.

    The specified expression is evaluated for each point or primitive. This
    determines the priority of that primitive, and the entities are reordered
    according to that priority. The point or primitive with the least evaluated
    expression value will be numbered 0 after the sort.

    """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    values = []

    # Get the current cooking SOP node.  We need to do this as the geometry is
    # frozen and  has no reference to the SOP node it belongs to.
    sop_node = hou.pwd()

    if geometry_type == hou.geometryType.Points:
        # Iterate over each point.
        for point in self.points():
            # Get this point to be the current point.  This allows '$PT' to
            # work properly in the expression.
            sop_node.setCurPoint(point)

            # Add the evaluated expression value to the list.
            values.append(hou.hscriptExpression(expression))

    elif geometry_type == hou.geometryType.Primitives:
        # Iterate over each primitive.
        for prim in self.prims():
            # Get this point to be the current point.  This allows '$PR' to
            # work properly in the expression.
            sop_node.setCurPrim(prim)

            # Add the evaluated expression value to the list.
            values.append(hou.hscriptExpression(expression))

    else:
        raise hou.OperationFailed(
            "Geometry type must be points or primitives."
        )

    sortByValues(self, geometry_type, values)


@add_to_class(hou.Geometry)
def createPoint(self, position=None):
    """Create a new point, optionally located at a position."""
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    # If no position is specified, use the origin.
    if position is None:
        position = hou.Vector3()

    result = _cpp_methods.createPoint(self, position)

    return self.iterPoints()[result]


@add_to_class(hou.Geometry)
def createNPoints(self, npoints):
    """Create a specific number of new points."""
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    if npoints <= 0:
        raise hou.OperationFailed("Invalid number of points.")

    result = _cpp_methods.createNPoints(self, npoints)

    # Since the result is only the starting point number we need to
    # build a starting from that.
    point_nums = range(result, result+npoints)

    return _get_points_from_list(self, point_nums)


@add_to_class(hou.Geometry)
def mergePointGroup(self, group):
    """Merges points from a group into this detail. """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    _cpp_methods.mergePointGroup(self, group.geometry(), group.name())


@add_to_class(hou.Geometry)
def mergePoints(self, points):
    """Merge a list of points from a detail into this detail."""
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    arr = _build_c_int_array([point.number() for point in points])

    _cpp_methods.mergePoints(self, points[0].geometry(), arr, len(arr))


@add_to_class(hou.Geometry)
def mergePrimGroup(self, group):
    """Merges prims from a group into this detail."""
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    _cpp_methods.mergePrimGroup(self, group.geometry(), group.name())


@add_to_class(hou.Geometry)
def mergePrims(self, prims):
    """Merges a list of prims from a detail into this detail."""
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    arr = _build_c_int_array([prim.number() for prim in prims])

    _cpp_methods.mergePrims(self, prims[0].geometry(), arr, len(arr))


def copyAttributeValues(source_element, source_attribs, target_element):
    """Copy a list of attributes from the source element to the target element."""
    # Copying to a geometry entity.
    if not isinstance(target_element, hou.Geometry):
        # Get the source element's geometry.
        target_geometry = target_element.geometry()

        # Entity number is generally just the number().
        target_entity_num = target_element.number()

        # If we're copying to a vertex then we need to get the offset.
        if isinstance(target_element, hou.Vertex):
            target_entity_num = target_element.linearNumber()

    # hou.Geometry means copying to detail attributes.
    else:
        target_geometry = target_element
        target_entity_num = 0

    # Make sure the target geometry is not read only.
    if target_geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    # Copying from a geometry entity.
    if not isinstance(source_element, hou.Geometry):
        # Get the source point's geometry.
        source_geometry = source_element.geometry()
        source_entity_num = source_element.number()

        if isinstance(source_element, hou.Vertex):
            source_entity_num = source_element.linearNumber()

    # Copying from detail attributes.
    else:
        source_geometry = source_element
        source_entity_num = 0

    # Get the attribute owners from the elements.
    target_owner = _get_attrib_owner_from_geometry_type(type(target_element))
    source_owner = _get_attrib_owner_from_geometry_type(type(source_element))

    # Get the attribute names, ensuring we only use attributes on the
    # source's geometry.
    attrib_names = [
        attrib.name() for attrib in source_attribs
        if _get_attrib_owner(attrib.type()) == source_owner and
        attrib.geometry().sopNode() == source_geometry.sopNode()
    ]

    # Construct a ctypes string array to pass the strings.
    arr = _build_c_string_array(attrib_names)

    _cpp_methods.copyAttributeValues(
        target_geometry,
        target_owner,
        target_entity_num,
        source_geometry,
        source_owner,
        source_entity_num,
        arr,
        len(attrib_names)
    )


@add_to_class(hou.Point, name="copyAttribValues")
def copyPointAttributeValues(self, source_point, attributes):
    """Copy attribute values from the source point to this point.

    If the attributes do not exist on the destination detail they will be
    created.

    This function is deprecated.  Use copyAttributeValues instead.

    """
    copyAttributeValues(source_point, attributes, self)


@add_to_class(hou.Prim, name="copyAttribValues")
def copyPrimAttributeValues(self, source_prim, attributes):
    """Copy attribute values from the source primitive to this primitive.

    If the attributes do not exist on the destination primitive they will be
    created.

    This function is deprecated.  Use copyAttributeValues instead.

    """
    copyAttributeValues(source_prim, attributes, self)


@add_to_class(hou.Prim)
def pointAdjacentPolygons(self):
    """Get all prims that are adjacent to this prim through a point."""
    # Get the geometry this primitive belongs to.
    geometry = self.geometry()

    # Get a list of prim numbers that are point adjacent this prim.
    result = _cpp_methods.pointAdjacentPolygons(geometry, self.number())

    return _get_prims_from_list(geometry, result)


@add_to_class(hou.Prim)
def edgeAdjacentPolygons(self):
    """Get all prims that are adjacent to this prim through an edge."""
    # Get the geometry this primitive belongs to.
    geometry = self.geometry()

    # Get a list of prim numbers that are edge adjacent this prim.
    result = _cpp_methods.edgeAdjacentPolygons(geometry, self.number())

    return _get_prims_from_list(geometry, result)


@add_to_class(hou.Point)
def connectedPrims(self):
    """Get all primitives that reference this point."""
    # Get the geometry the point belongs to.
    geometry = self.geometry()

    # Get a list of primitive numbers that reference the point.
    result = _cpp_methods.connectedPrims(geometry, self.number())

    return _get_prims_from_list(geometry, result)


@add_to_class(hou.Point)
def connectedPoints(self):
    """Get all points that share an edge with this point."""
    # Get the geometry the point belongs to.
    geometry = self.geometry()

    # Get a list of point numbers that are connected to the point.
    result = _cpp_methods.connectedPoints(geometry, self.number())

    # Glob for the points and return them.
    return _get_points_from_list(geometry, result)


@add_to_class(hou.Point)
def referencingVertices(self):
    """Get all the vertices referencing this point."""
    # Get the geometry the point belongs to.
    geometry = self.geometry()

    # Get an object containing primitive and vertex index information.
    result = _cpp_methods.referencingVertices(geometry, self.number())

    # Construct a list of vertex strings.  Each element has the format:
    # {prim_num}v{vertex_index}.
    vertex_strings = ["{}v{}".format(prim, idx)
                      for prim, idx in zip(result.prims, result.indices)]

    # Glob for the vertices and return them.
    return geometry.globVertices(' '.join(vertex_strings))


@add_to_class(hou.Attrib)
def stringTableIndices(self):
    """Return at tuple of string attribute table indices.

    String attributes are stored using integers referencing a table of
    strings.  This function will return a list of table indices for each
    element.

    """
    if self.dataType() != hou.attribData.String:
        raise hou.OperationFailed("Attribute must be a string.")

    # Get the corresponding attribute type id.
    attrib_owner = _get_attrib_owner(self.type())

    return tuple(_cpp_methods.getStringTableIndices(self.geometry(), attrib_owner, self.name()))


@add_to_class(hou.Geometry)
def vertexStringAttribValues(self, name):
    """Return a tuple of strings containing one attribute's values for all the
    vertices.

    """
    attrib = self.findVertexAttrib(name)

    if attrib is None:
        raise hou.OperationFailed("Invalid attribute name.")

    if attrib.dataType() != hou.attribData.String:
        raise hou.OperationFailed("Attribute must be a string.")

    return _cpp_methods.vertexStringAttribValues(
        self,
        name
    )


@add_to_class(hou.Geometry)
def setVertexStringAttribValues(self, name, values):
    """Set the string attribute values for all vertices."""
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    attrib = self.findVertexAttrib(name)

    if attrib is None:
        raise hou.OperationFailed("Invalid attribute name.")

    if attrib.dataType() != hou.attribData.String:
        raise hou.OperationFailed("Attribute must be a string.")

    if len(values) != self.numVertices():
        raise hou.OperationFailed("Incorrect attribute value sequence size.")

    # Construct a ctypes string array to pass the strings.
    arr = _build_c_string_array(values)

    _cpp_methods.setVertexStringAttribValues(
        self,
        name,
        arr,
        len(values)
    )


@add_to_class(hou.Geometry)
def setSharedPointStringAttrib(self, name, value, group=None):
    """Set a string attribute value for points.

    If group is None, all points will have receive the value.  If a group is
    passed, only the points in the group will be set.

    """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    attribute = self.findPointAttrib(name)

    if attribute is None:
        raise hou.OperationFailed("Invalid attribute name.")

    if attribute.dataType() != hou.attribData.String:
        raise hou.OperationFailed("Attribute must be a string.")

    # If the group is valid use that group's name.
    if group:
        group_name = group.name()

    # If not pass 0 so the char * will be empty.
    else:
        group_name = 0

    _cpp_methods.setSharedStringAttrib(
        self,
        _get_attrib_owner(attribute.type()),
        name,
        value,
        group_name
    )


@add_to_class(hou.Geometry)
def setSharedPrimStringAttrib(self, name, value, group=None):
    """Set a string attribute value for primitives.

    If group is None, all primitives will have receive the value.  If a group
    is passed, only the primitives in the group will be set.

    """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    attribute = self.findPrimAttrib(name)

    if attribute is None:
        raise hou.OperationFailed("Invalid attribute name.")

    if attribute.dataType() != hou.attribData.String:
        raise hou.OperationFailed("Attribute must be a string.")

    # If the group is valid use that group's name.
    if group:
        group_name = group.name()

    # If not pass 0 so the char * will be empty.
    else:
        group_name = 0

    _cpp_methods.setSharedStringAttrib(
        self,
        _get_attrib_owner(attribute.type()),
        name,
        value,
        group_name
    )


@add_to_class(hou.Face)
def hasEdge(self, point1, point2):
    """Test if this face has an edge between two points."""
    # Test for the edge.
    return _cpp_methods.hasEdge(
        self.geometry(),
        self.number(),
        point1.number(),
        point2.number()
    )


@add_to_class(hou.Face)
def sharedEdges(self, prim):
    """Get a tuple of any shared edges between two prims."""
    # A comparison function key function to sort points by their numbers.
    test_key = lambda pt: pt.number()

    geometry = self.geometry()

    # A list of unique edges.
    edges = set()

    # Iterate over each vertex of the primitive.
    for vertex in self.vertices():
        # Get the point for the vertex.
        vertex_point = vertex.point()

        # Iterate over all the connected points.
        for connected in vertex_point.connectedPoints():
            # Sort the points.
            pt1, pt2 = sorted((vertex_point, connected), key=test_key)

            # Ensure the edge exists for both primitives.
            if self.hasEdge(pt1, pt2) and prim.hasEdge(pt1, pt2):
                # Find the edge and add it to the list.
                edges.add(geometry.findEdge(pt1, pt2))

    return tuple(edges)


@add_to_class(hou.Face)
def insertVertex(self, point, index):
    """Insert a vertex on the point into this face at a specific index."""
    geometry = self.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    # If the index is less than 0, throw an exception since it's not valid.
    if index < 0:
        raise IndexError("Index must be 0 or greater.")

    # If the index is too high it is also invalid.
    if index >= self.numVertices():
        raise IndexError("Invalid index: {}".format(index))

    # Insert the vertex.
    _cpp_methods.insertVertex(geometry, self.number(), point.number(), index)


@add_to_class(hou.Face)
def deleteVertex(self, index):
    """Delete the vertex at the specified index."""
    geometry = self.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    # If the index is less than 0, throw an exception since it's not valid.
    if index < 0:
        raise IndexError("Index must be 0 or greater.")

    # If the index is too high it is also invalid.
    if index >= self.numVertices():
        raise IndexError("Invalid index: {}".format(index))

    # Delete the vertex.
    _cpp_methods.deleteVertex(geometry, self.number(), index)


@add_to_class(hou.Face)
def setPoint(self, index, point):
    """Set the vertex, at the specified index, to be attached to the point."""
    geometry = self.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    # If the index is less than 0, throw an exception since it's not valid.
    if index < 0:
        raise IndexError("Index must be 0 or greater.")

    # If the index is too high it is also invalid.
    if index >= self.numVertices():
        raise IndexError("Invalid index: {}".format(index))

    # Modify the vertex.
    _cpp_methods.setPoint(geometry, self.number(), index, point.number())


@add_to_class(hou.Prim)
def baryCenter(self):
    """Get the barycenter of this primitive."""
    # Get the Position3D object representing the barycenter.
    pos = _cpp_methods.baryCenter(self.geometry(), self.number())

    # Construct a vector and return it.
    return hou.Vector3(pos.x, pos.y, pos.z)


@add_to_class(hou.Prim, name="area")
def primitiveArea(self):
    """Get the area of this primitive."""
    return self.intrinsicValue("measuredarea")


@add_to_class(hou.Prim)
def perimeter(self):
    """Get the perimeter of this primitive."""
    return self.intrinsicValue("measuredperimeter")


@add_to_class(hou.Prim)
def volume(self):
    """Get the volume of this primitive."""
    return self.intrinsicValue("measuredvolume")


@add_to_class(hou.Prim, name="reverse")
def reversePrim(self):
    """Reverse the vertex order of this primitive."""
    geometry = self.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    return _cpp_methods.reversePrimitive(geometry, self.number())


@add_to_class(hou.Prim)
def makeUnique(self):
    """Unique all the points that are in this primitive.

    This function will unique all the points even if they are referenced by
    other primitives.

    """
    geometry = self.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    return _cpp_methods.makeUnique(geometry, self.number())


@add_to_class(hou.Prim, name="boundingBox")
def primBoundingBox(self):
    """Get the bounding box of this primitive."""
    bounds = self.intrinsicValue("bounds")

    # Intrinsic values are out of order for hou.BoundingBox so they need to
    # be shuffled.
    return hou.BoundingBox(
        bounds[0],
        bounds[2],
        bounds[4],
        bounds[1],
        bounds[3],
        bounds[5],
    )


@add_to_class(hou.Geometry)
def computePointNormals(self):
    """Computes the point normals for the geometry.

    This is equivalent to using a Point sop, selecting 'Add Normal' and
    leaving the default values.  It will add the 'N' attribute if it does not
    exist.

    """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    _cpp_methods.computePointNormals(self)


@add_to_class(hou.Geometry, name="addPointNormals")
def addPointNormalAttribute(self):
    """Add point normals to the geometry.

    This function will only create the Normal attribute and will not
    initialize the values.  See hou.Geometry.computePointNormals().

    """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    success = _cpp_methods.addNormalAttribute(self)

    if success:
        return self.findPointAttrib("N")

    raise hou.OperationFailed("Could not add normal attribute.")


@add_to_class(hou.Geometry, name="addPointVelocity")
def addPointVelocityAttribute(self):
    """Add point velocity to the geometry."""
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    success = _cpp_methods.addVelocityAttribute(self)

    if success:
        return self.findPointAttrib("v")

    raise hou.OperationFailed("Could not add velocity attribute.")


@add_to_class(hou.Geometry)
def addColorAttribute(self, attrib_type):
    """Add a color (Cd) attribute to the geometry.

    Point, primitive and vertex colors are supported.

    """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    if attrib_type == hou.attribType.Global:
        raise hou.TypeError("Invalid attribute type.")

    owner = _get_attrib_owner(attrib_type)

    # Try to add the Cd attribute.
    success = _cpp_methods.addDiffuseAttribute(self, owner)

    if success:
        return _find_attrib(self, attrib_type, "Cd")

    # We didn't create an attribute, so throw an exception.
    raise hou.OperationFailed("Could not add Cd attribute.")


@add_to_class(hou.Geometry)
def convex(self, max_points=3):
    """Convex the geometry into polygons with a certain number of points.

    This operation is similar to using the Divide SOP and setting the 'Maximum
    Edges'.

    """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    _cpp_methods.convexPolygons(self, max_points)


@add_to_class(hou.Geometry)
def clip(self, origin, normal, dist=0, below=False, group=None):
    """Clip this geometry along a plane."""
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    # If the group is valid, use that group's name.
    if group:
        group_name = group.name()

    # If not, pass an empty string to signify no group.
    else:
        group_name = ""

    # If we want to keep the prims below the plane we need to offset
    # the origin along the normal by the distance and then reverse
    # the normal and set the distance to 0.
    if below:
        origin += normal * dist
        normal *= -1
        dist = 0

    # Build a transform to modify the geometry so we can have the plane not
    # centered at the origin.
    xform = hou.hmath.buildTranslate(origin)

    _cpp_methods.clip(self, xform, normal.normalized(), dist, group_name)


@add_to_class(hou.Geometry)
def destroyEmptyGroups(self, attrib_type):
    """Remove any empty groups of the specified type. """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    if attrib_type == hou.attribType.Global:
        raise hou.OperationFailed(
            "Attribute type must be point, primitive or vertex."
        )

    # Get the corresponding attribute type id.
    attrib_owner = _get_attrib_owner(attrib_type)

    _cpp_methods.destroyEmptyGroups(self, attrib_owner)


@add_to_class(hou.Geometry)
def destroyUnusedPoints(self, group=None):
    """Remove any unused points.

    If group is not None, only unused points within the group are removed.

    """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    if group is not None:
        _cpp_methods.destroyUnusedPoints(self, group.name())
    else:
        _cpp_methods.destroyUnusedPoints(self, 0)


@add_to_class(hou.Geometry)
def consolidatePoints(self, distance=0.001, group=None):
    """Consolidate points within a specified distance.

    If group is not None, only points in that group are consolidated.

    """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    if group is not None:
        _cpp_methods.consolidatePoints(self, distance, group.name())
    else:
        _cpp_methods.consolidatePoints(self, distance, 0)


@add_to_class(hou.Geometry)
def uniquePoints(self, group=None):
    """Unique points in the geometry.

    If a point group is specified, only points in that group are uniqued.

    """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    if group is not None:
        _cpp_methods.uniquePoints(self, group.name())

    else:
        _cpp_methods.uniquePoints(self, 0, 0)


@add_to_class(hou.Geometry)
def renameGroup(self, group, new_name):
    """Rename this group."""
    # Make sure the geometry is not read only.
    if isReadOnly(self):
        raise hou.GeometryPermissionError()

    # Ensure the new group doesn't have the same name.
    if new_name == group.name():
        raise hou.OperationFailed("Cannot rename to same name.")

    group_type = _get_group_type(group)

    success = _cpp_methods.renameGroup(
        self,
        group.name(),
        new_name,
        group_type
    )

    if success:
        return _find_group(self, group_type, new_name)

    else:
        return None


@add_to_class(hou.PointGroup, hou.PrimGroup, hou.EdgeGroup, name="boundingBox")
def groupBoundingBox(self):
    """Get the bounding box of this group."""
    group_type = _get_group_type(self)

    # Calculate the bounds for the group.
    bounds = _cpp_methods.groupBoundingBox(
        self.geometry(),
        group_type,
        self.name()
    )

    return hou.BoundingBox(*bounds)


@add_to_class(hou.EdgeGroup, hou.PointGroup, hou.PrimGroup, name="__len__")
@add_to_class(hou.EdgeGroup, hou.PointGroup, hou.PrimGroup, name="size")
def groupSize(self):
    """Get the number of elements in this group."""
    geometry = self.geometry()

    group_type = _get_group_type(self)

    return _cpp_methods.groupSize(geometry, self.name(), group_type)


@add_to_class(hou.PointGroup, name="toggle")
def togglePoint(self, point):
    """Toggle group membership for a point.

    If the point is a part of the group, it will be removed.  If it isn't, it
    will be added.

    """
    geometry = self.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    group_type = _get_group_type(self)

    _cpp_methods.toggleMembership(
        geometry,
        self.name(),
        group_type,
        point.number()
    )


@add_to_class(hou.PrimGroup, name="toggle")
def togglePrim(self, prim):
    """Toggle group membership for a primitive.

    If the primitive is a part of the group, it will be removed.  If it isnt,
    it will be added.

    """
    geometry = self.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    group_type = _get_group_type(self)

    _cpp_methods.toggleMembership(
        geometry,
        self.name(),
        group_type,
        prim.number()
    )


@add_to_class(hou.EdgeGroup, hou.PointGroup, hou.PrimGroup)
def toggleEntries(self):
    """Toggle group membership for all elements in the group.

    All elements not in the group will be added to it and all that were in it
    will be removed.

    """
    geometry = self.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    group_type = _get_group_type(self)

    _cpp_methods.toggleEntries(geometry, self.name(), group_type)


@add_to_class(hou.PointGroup, name="copy")
def copyPointGroup(self, new_group_name):
    """Create a new point group under the new name with the same membership."""
    geometry = self.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    # Ensure the new group doesn't have the same name.
    if new_group_name == self.name():
        raise hou.OperationFailed("Cannot copy to group with same name.")

    # Check for an existing group of the same name.
    if geometry.findPointGroup(new_group_name):
        # If one exists, raise an exception.
        raise hou.OperationFailed(
            "Point group '{}' already exists.".format(new_group_name)
        )

    attrib_owner = _get_group_attrib_owner(self)

    # Copy the group.
    _cpp_methods.copyGroup(geometry, attrib_owner, self.name(), new_group_name)

    # Return the new group.
    return geometry.findPointGroup(new_group_name)


@add_to_class(hou.PrimGroup, name="copy")
def copyPrimGroup(self, new_group_name):
    """Create a group under the new name with the same membership."""
    geometry = self.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    # Ensure the new group doesn't have the same name.
    if new_group_name == self.name():
        raise hou.OperationFailed("Cannot copy to group with same name.")

    # Check for an existing group of the same name.
    if geometry.findPrimGroup(new_group_name):
        # If one exists, raise an exception.
        raise hou.OperationFailed(
            "Primitive group '{}' already exists.".format(new_group_name)
        )

    attrib_owner = _get_group_attrib_owner(self)

    # Copy the group.
    _cpp_methods.copyGroup(geometry, attrib_owner, self.name(), new_group_name)

    # Return the new group.
    return geometry.findPrimGroup(new_group_name)


@add_to_class(hou.PointGroup, name="containsAny")
def pointGroupContainsAny(self, group):
    """Returns whether or not any points in the group are in this group."""
    geometry = self.geometry()

    group_type = _get_group_type(self)

    return _cpp_methods.containsAny(geometry, self.name(), group.name(), group_type)


@add_to_class(hou.PrimGroup, name="containsAny")
def primGroupContainsAny(self, group):
    """Returns whether or not any prims in the group are in this group."""
    geometry = self.geometry()

    group_type = _get_group_type(self)

    return _cpp_methods.containsAny(geometry, self.name(), group.name(), group_type)


@add_to_class(hou.PrimGroup)
def convertToPointGroup(self, new_group_name=None, destroy=True):
    """Create a new hou.Point group from this primitive group.

    The group will contain all the points referenced by all the vertices of the
    primitives in the group.

    """
    geometry = self.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    # If a new name isn't specified, use the current group name.
    if new_group_name is None:
        new_group_name = self.name()

    # If the group already exists, raise an exception.
    if geometry.findPointGroup(new_group_name):
        raise hou.OperationFailed("Group already exists.")

    # Convert the group.
    _cpp_methods.primToPointGroup(
        geometry,
        self.name(),
        new_group_name,
        destroy
    )

    # Return the new group.
    return geometry.findPointGroup(new_group_name)


@add_to_class(hou.PointGroup)
def convertToPrimGroup(self, new_group_name=None, destroy=True):
    """Create a new hou.Prim group from this point group.

    The group will contain all the primitives which have vertices referencing
    any of the points in the group.

    """
    geometry = self.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    # If a new name isn't specified, use the current group name.
    if new_group_name is None:
        new_group_name = self.name()

    # If the group already exists, raise an exception.
    if geometry.findPrimGroup(new_group_name):
        raise hou.OperationFailed("Group already exists.")

    # Convert the group.
    _cpp_methods.pointToPrimGroup(
        geometry,
        self.name(),
        new_group_name,
        destroy
    )

    # Return the new group.
    return geometry.findPrimGroup(new_group_name)


@add_to_class(hou.Geometry)
def hasUngroupedPoints(self):
    """Check if the geometry has ungrouped points."""
    return _cpp_methods.hasUngroupedPoints(self)


@add_to_class(hou.Geometry)
def groupUngroupedPoints(self, group_name):
    """Create a new point group of any points not already in a group."""
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    if not group_name:
        raise hou.OperationFailed("Invalid group name: {}".format(group_name))

    if self.findPointGroup(group_name) is not None:
        raise hou.OperationFailed("Group '{}' already exists".format(group_name))

    _cpp_methods.groupUngroupedPoints(self, group_name)

    return self.findPointGroup(group_name)


@add_to_class(hou.Geometry)
def hasUngroupedPrims(self):
    """Check if the geometry has ungrouped primitives."""
    return _cpp_methods.hasUngroupedPrims(self)


@add_to_class(hou.Geometry)
def groupUngroupedPrims(self, group_name):
    """Create a new primitive group of any primitives not already in a group."""
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    if not group_name:
        raise hou.OperationFailed("Invalid group name: {}".format(group_name))

    if self.findPrimGroup(group_name) is not None:
        raise hou.OperationFailed("Group '{}' already exists".format(group_name))

    _cpp_methods.groupUngroupedPrims(self, group_name)

    return self.findPrimGroup(group_name)


@add_to_class(hou.BoundingBox)
def isInside(self, bbox):
    """Determine if this bounding box is totally enclosed by another box."""
    return _cpp_methods.isInside(self, bbox)


@add_to_class(hou.BoundingBox)
def intersects(self, bbox):
    """Determine if the bounding boxes intersect."""
    return _cpp_methods.intersects(self, bbox)


@add_to_class(hou.BoundingBox)
def computeIntersection(self, bbox):
    """Compute the intersection of two bounding boxes.

    This function changes the bounds of this box to be those of the
    intersection of this box and the supplied box.

    """
    return _cpp_methods.computeIntersection(self, bbox)


@add_to_class(hou.BoundingBox)
def expandBounds(self, dltx, dlty, dltz):
    """Expand the min and max bounds in each direction by the axis delta."""
    _cpp_methods.expandBounds(self, dltx, dlty, dltz)


@add_to_class(hou.BoundingBox)
def addToMin(self, vec):
    """Add values to the minimum bounds of this bounding box."""
    _cpp_methods.addToMin(self, vec)

@add_to_class(hou.BoundingBox)
def addToMax(self, vec):
    """Add values to the maximum bounds of this bounding box."""
    _cpp_methods.addToMax(self, vec)


@add_to_class(hou.BoundingBox, name="area")
def boundingBoxArea(self):
    """Calculate the area of this bounding box."""
    return _cpp_methods.boundingBoxArea(self)


@add_to_class(hou.BoundingBox, name="volume")
def boundingBoxVolume(self):
    """Calculate the volume of this bounding box."""
    return _cpp_methods.boundingBoxVolume(self)


@add_to_class(hou.ParmTuple)
def isVector(self):
    """Check if the tuple is a vector parameter."""
    parm_template = self.parmTemplate()

    return parm_template.namingScheme() == hou.parmNamingScheme.XYZW


@add_to_class(hou.ParmTuple)
def evalAsVector(self):
    """Return the parameter value as a hou.Vector of the appropriate size."""
    if not self.isVector():
        raise hou.Error("Parameter is not a vector")

    value = self.eval()
    size = len(value)

    if size == 2:
        return hou.Vector2(value)

    elif size == 3:
        return hou.Vector3(value)

    return hou.Vector4(value)


@add_to_class(hou.ParmTuple)
def isColor(self):
    """Check if the parameter is a color parameter."""
    parm_template = self.parmTemplate()

    return parm_template.look() == hou.parmLook.ColorSquare


@add_to_class(hou.ParmTuple)
def evalAsColor(self):
    """Evaluate a color parameter and return a hou.Color object."""
    if not self.isColor():
        raise hou.Error("Parameter is not a color chooser")

    return hou.Color(self.eval())


@add_to_class(hou.Parm)
def getReferencedNode(self):
    """Get the referenced node, if any, for this parameter."""
    parm_template = self.parmTemplate()

    # Parameter must be a string parameter.
    if not isinstance(parm_template, hou.StringParmTemplate):
        raise hou.Error("Parameter is not a string type")

    # String parameter must be a node reference.
    if parm_template.stringType() != hou.stringParmType.NodeReference:
        raise hou.Error("Parameter is not a node reference")

    # Look for the pointed to node, relative to the parameter's node.
    return self.node().node(self.eval())


@add_to_class(hou.Parm)
def evalAsStrip(self):
    """Evaluate the parameter as a Button/Icon Strip.

    Returns a tuple of True/False values indicated which buttons
    are pressed.

    """
    parm_template = self.parmTemplate()

    # Right now the best we can do is check that a parameter is a menu
    # since HOM has no idea about what the strips are.  If we aren't one
    # then raise an exception.
    if not isinstance(parm_template,  hou.MenuParmTemplate):
        raise TypeError("Parameter must be a menu")

    # Get the value.  This might be the selected index, or a bit mask if we
    # can select more than one.
    value = self.eval()

    # Initialize a list of False values for each item on the strip.
    menu_items = parm_template.menuItems()
    num_items = len(menu_items)
    values = [False] * num_items

    # If our menu type is a Toggle that means we can select more than one
    # item at the same time so our value is really a bit mask.
    if parm_template.menuType() == hou.menuType.StringToggle:
        # Check which items are selected.
        for i in range(num_items):
            mask = 1 << i

            if value & mask:
                values[i] = True

    # Value is just the selected index so set that one to True.
    else:
        values[value] = True

    return tuple(values)


@add_to_class(hou.Parm)
def evalStripAsString(self):
    """Evaluate the parameter as a Button Strip as strings.

    Returns a tuple of the string tokens which are enabled.

    """
    strip_results = self.evalAsStrip()

    menu_items = self.parmTemplate().menuItems()

    enabled_values = []

    for i, value in enumerate(strip_results):
        if value:
            enabled_values.append(menu_items[i])

    return tuple(enabled_values)


@add_to_class(hou.Parm, hou.ParmTuple)
def isMultiParm(self):
    """Check if this parameter is a multiparm."""
    # Get the parameter template for the parm/tuple.
    parm_template = self.parmTemplate()

    # Make sure the parm is a folder parm.
    if isinstance(parm_template, hou.FolderParmTemplate):
        # Get the folder type.
        folder_type = parm_template.folderType()

        # A tuple of folder types that are multiparms.
        multi_types = (
            hou.folderType.MultiparmBlock,
            hou.folderType.ScrollingMultiparmBlock,
            hou.folderType.TabbedMultiparmBlock
        )

        # If the folder type is in the list return True.
        if folder_type in multi_types:
            return True

    return False


@add_to_class(hou.Parm)
def getMultiParmInstancesPerItem(self):
    """Get the number of items in a multiparm instance."""
    return self.tuple().getMultiParmInstancesPerItem()


@add_to_class(hou.ParmTuple, name="getMultiParmInstancesPerItem")
def getTupleMultiParmInstancesPerItem(self):
    """Get the number of items in a multiparm instance."""
    if not self.isMultiParm():
        raise hou.OperationFailed("Parameter tuple is not a multiparm.")

    return _cpp_methods.getMultiParmInstancesPerItem(
        self.node(),
        self.name()
    )


@add_to_class(hou.Parm)
def getMultiParmStartOffset(self):
    """Get the start offset of items in the multiparm."""
    return self.tuple().getMultiParmStartOffset()


@add_to_class(hou.ParmTuple, name="getMultiParmStartOffset")
def getTupleMultiParmStartOffset(self):
    """Get the start offset of items in the multiparm."""
    if not self.isMultiParm():
        raise hou.OperationFailed("Parameter tuple is not a multiparm.")

    return _cpp_methods.getMultiParmStartOffset(
        self.node(),
        self.name()
    )


@add_to_class(hou.Parm)
def getMultiParmInstanceIndex(self):
    """Get the multiparm instance indices for this parameter.

    If this parameter is part of a multiparm, then its index in the multiparm
    array will be returned as a tuple.  If the multiparm is nested in other
    multiparms, then the resulting tuple will have multiple entries (with
    the outer multiparm listed first, and the inner-most multiparm last in
    the tuple.

    """
    return self.tuple().getMultiParmInstanceIndex()


@add_to_class(hou.ParmTuple, name="getMultiParmInstanceIndex")
def getTupleMultiParmInstanceIndex(self):
    """Get the multiparm instance indices for this parameter tuple.

    If this parameter tuple is part of a multiparm, then its index in the
    multiparm array will be returned as a tuple.  If the multiparm is nested
    in other multiparms, then the resulting tuple will have multiple entries
    (with the outer multiparm listed first, and the inner-most multiparm last
    in the tuple.

    """
    if not self.isMultiParmInstance():
        raise hou.OperationFailed("Parameter tuple is not in a multiparm.")

    result = _cpp_methods.getMultiParmInstanceIndex(
        self.node(),
        self.name()
    )

    return tuple(result)


@add_to_class(hou.Parm, hou.ParmTuple)
def getMultiParmInstances(self):
    """Return all the parameters in this multiparm block.

    The parameters are returned as a tuple of parameters based on each
    instance.

    """
    node = self.node()

    if not self.isMultiParm():
        raise hou.OperationFailed("Not a multiparm.")

    # Get the multiparm parameter names.
    result = _cpp_methods.getMultiParmInstances(node, self.name())

    multi_parms = []

    # Iterate over each multiparm instance.
    for block in result:
        parms = []
        # Build a list of parameters in the instance.
        for parm_name in block:
            if not parm_name:
                continue

            # Assume hou.ParmTuple by default.
            parm_tuple = node.parmTuple(parm_name)

            # If tuple only has one element then use that hou.Parm.
            if len(parm_tuple) == 1:
                parm_tuple = parm_tuple[0]

            parms.append(parm_tuple)

        multi_parms.append(tuple(parms))

    return tuple(multi_parms)


# TODO: Function to get sibling parameters

@add_to_class(hou.Parm, hou.ParmTuple)
def getMultiParmInstanceValues(self):
    """Return all the parameter values in this multiparm block.

    The values are returned as a tuple of values based on each instance.

    """
    if not self.isMultiParm():
        raise hou.OperationFailed("Not a multiparm.")

    # Get the multiparm parameters.
    parms = getMultiParmInstances(self)

    all_values = []

    # Iterate over each multiparm instance.
    for block in parms:
        values = [parm.eval() for parm in block]
        all_values.append(tuple(values))

    return tuple(all_values)


@add_to_class(hou.Node)
def disconnectAllInputs(self):
    """Disconnect all of this node's inputs."""
    connections = self.inputConnections()

    for connection in reversed(connections):
        self.setInput(connection.inputIndex(), None)


@add_to_class(hou.Node)
def disconnectAllOutputs(self):
    """Disconnect all of this node's outputs. """
    connections = self.outputConnections()

    for connection in connections:
        connection.outputNode().setInput(connection.inputIndex(), None)


@add_to_class(hou.Node)
def messageNodes(self):
    """Get a list of this node's message nodes."""
    # Get the otl definition for this node's type, if any.
    definition = self.type().definition()

    if definition is not None:
        # Check that there are message nodes.
        if "MessageNodes" in definition.sections():
            # Extract the list of them.
            contents = definition.sections()["MessageNodes"].contents()

            # Glob for any specified nodes and return them.
            return self.glob(contents)

    return ()


@add_to_class(hou.Node)
def editableNodes(self):
    """Get a list of this node's editable nodes."""
    # Get the otl definition for this node's type, if any.
    definition = self.type().definition()

    if definition is not None:
        # Check that there are editable nodes.
        if "EditableNodes" in definition.sections():
            # Extract the list of them.
            contents = definition.sections()["EditableNodes"].contents()

            # Glob for any specified nodes and return them.
            return self.glob(contents)

    return ()


@add_to_class(hou.Node)
def diveTarget(self):
    """Get this node's dive target node."""
    # Get the otl definition for this node's type, if any.
    definition = self.type().definition()

    if definition is not None:
        # Check that there is a dive target.
        if "DiveTarget" in definition.sections():
            # Get it's path.
            target = definition.sections()["DiveTarget"].contents()

            # Return the node.
            return self.node(target)

    return None


@add_to_class(hou.Node)
def representativeNode(self):
    """Get the representative node of this node, if any."""
    # Get the otl definition for this node's type, if any.
    definition = self.type().definition()

    if definition is not None:
        # Get the path to the representative node, if any.
        path = definition.representativeNodePath()

        if path:
            # Return the node.
            return self.node(path)

    return None


@add_to_class(hou.Node)
def isContainedBy(self, node):
    """Test if this node is a contained within the node."""
    # Get this node's parent.
    parent = self.parent()

    # Keep looking until we have no more parents.
    while parent is not None:
        # If the parent is the target node, return True.
        if parent == node:
            return True

        # Get the parent's parent and try again.
        parent = parent.parent()

    # Didn't find the node, so return False.
    return False


@add_to_class(hou.Node)
def isCompiled(self):
    """Check if this node is compiled.

    This check can be used to determine if a node is compiled for Orbolt,
    or has somehow become compiled on its own.

    """
    return _cpp_methods.isCompiled(self)


@add_to_class(hou.Node)
def authorName(self):
    """Get the name of the node creator."""
    author = _cpp_methods.getAuthor(self)

    # Remove any machine name from the user name.
    return author.split('@')[0]


@add_to_class(hou.NodeType)
def setIcon(self, icon_name):
    """Set the node type's icon name."""
    return _cpp_methods.setIcon(self, icon_name)


@add_to_class(hou.NodeType)
def setDefaultIcon(self):
    """Set this node type's icon name to its default value."""
    return _cpp_methods.setDefaultIcon(self)


@add_to_class(hou.NodeType)
def isPython(self):
    """Check if this node type represents a Python operator."""
    return _cpp_methods.isPython(self)


@add_to_class(hou.NodeType)
def isSubnetType(self):
    """Check if this node type is the primary subnet operator for the table.

    This is the operator type which is used as a default container for nodes.

    """
    return _cpp_methods.isSubnetType(self)


@add_to_class(hou.Vector3)
def componentAlong(self, vector):
    """Calculate the component of this vector along another vector."""
    # The component of vector A along B is: A dot (unit vector // to B).
    return self.dot(vector.normalized())


@add_to_class(hou.Vector3)
def project(self, vector):
    """Calculate the vector projection of this vector onto another vector.

    This is an orthogonal projection of this vector onto a straight line
    parallel to the supplied vector.

    """
    # The vector cannot be the zero vector.
    if vector == hou.Vector3():
        raise hou.OperationFailed("Supplied vector must be non-zero.")

    return vector.normalized() * self.componentAlong(vector)


@add_to_class(hou.Vector2, hou.Vector3, hou.Vector4)
def isNan(self):
    """Check if this vector contains NaNs."""
    # Iterate over each component.
    for i in range(len(self)):
        # If this component is a NaN, return True.
        if math.isnan(self[i]):
            return True

    # Didn't find any NaNs, so return False.
    return False


@add_to_class(hou.Vector3)
def getDual(self):
    """Returns the dual of this vector.

    The dual is a matrix which acts like the cross product when multiplied by
    other vectors.

    """
    # The matrix that will be the dual.
    mat = hou.Matrix3()

    # Compute the dual.
    _cpp_methods.getDual(self, mat)

    return mat


@add_to_class(hou.Matrix3, hou.Matrix4)
def isIdentity(self):
    """Check if this matrix is the identity matrix."""
    # We are a 3x3 matrix.
    if isinstance(self, hou.Matrix3):
        # Construct a new 3x3 matrix.
        mat = hou.Matrix3()

        # Set it to be the identity.
        mat.setToIdentity()

        # Compare the two.
        return self == mat

    # Compare against the identity transform from hmath.
    return self == hou.hmath.identityTransform()


@add_to_class(hou.Matrix4)
def setTranslates(self, translates):
    """Set the translation values of this matrix."""
    # The translations are stored in the first 3 columns of the last row of the
    # matrix.  To set the values we just need to set the corresponding columns
    # to the matching components in the vector.
    for i in range(3):
        self.setAt(3, i, translates[i])


@add_to_module(hou.hmath)
def buildLookat(from_vec, to_vec, up):
    """Compute a lookat matrix.

    This function will compute a rotation matrix which will provide the rotates
    needed for "from_vec" to look at "to_vec".

    The lookat matrix will have the -Z axis point at the "to_vec" point.  The Y
    axis will be pointing "up".

    """
    # Create the new matrix to return.
    mat = hou.Matrix3()

    # Calculate the lookat and stick it in the matrix.
    _cpp_methods.buildLookat(mat, from_vec, to_vec, up)

    return mat


# TODO: create instance from point
@add_to_module(hou.hmath)
def buildInstance(position, direction=hou.Vector3(0, 0, 1), pscale=1,
                  scale=hou.Vector3(1, 1, 1), up=hou.Vector3(0, 1, 0),
                  rot=hou.Quaternion(0, 0, 0, 1), trans=hou.Vector3(0, 0, 0),
                  pivot=hou.Vector3(0, 0, 0),
                  orient=None
                 ):
    """Compute a transform to orient to a given direction.

    The transform can be computed for an optional position and scale.

    The up vector is optional and will orient the matrix to this up vector.  If
    no up vector is given, the Z axis will be oriented to point in the supplied
    direction.

    If a rotation quaternion is specified, the orientation will be additionally
    transformed by the rotation.

    If a translation is specified, the entire frame of reference will be moved
    by this translation (unaffected by the scale or rotation).

    If a pivot is specified, use it as the local transformation of the
    instance.

    If an orientation quaternion is specified, the orientation (using the
    direction and up vector will not be performed and this orientation will
    instead be used to define an original orientation.

    """
    zero_vec = hou.Vector3()

    # Scale the non-uniform scale by the uniform scale.
    scale *= pscale

    # Construct the scale matrix.
    scale_matrix = hou.hmath.buildScale(scale)

    # Build a rotation matrix from the rotation quaternion.
    rot_matrix = hou.Matrix4(rot.extractRotationMatrix3())

    pivot_matrix = hou.hmath.buildTranslate(pivot)

    # Build a translation matrix from the position and the translation vector.
    trans_matrix = hou.hmath.buildTranslate(position + trans)

    # If an orientation quaternion is passed, construct a matrix from it.
    if orient is not None:
        alignment_matrix = hou.Matrix4(orient.extractRotationMatrix3())

    else:
        # If the up vector is not the zero vector, build a lookat matrix
        # between the direction and zero vectors using the up vector.
        if up != zero_vec:
            alignment_matrix = hou.Matrix4(
                buildLookat(direction, zero_vec, up)
            )

        # If the up vector is the zero vector, build a matrix from the
        # dihedral.
        else:
            alignment_matrix = zero_vec.matrixToRotateTo(direction)

    # Return the instance transform matrix.
    return pivot_matrix * scale_matrix * alignment_matrix * rot_matrix * trans_matrix


@add_to_class(hou.Node)
def isDigitalAsset(self):
    """Determine if this node is a digital asset.

    A node is a digital asset if its node type has a hou.HDADefinition.

    """
    return self.type().definition() is not None


@add_to_module(hou.hda)
def metaSource(file_path):
    """Get the meta install location for the file.

    This function determines where the specified .otl file is installed to in
    the current session.  Examples include "Scanned OTL Directories", "Current
    Hip File", "Fallback Libraries" or specific OPlibraries files.

    """
    if file_path not in hou.hda.loadedFiles():
        return None

    return _cpp_methods.getMetaSource(file_path)


@add_to_class(hou.HDADefinition, name="metaSource")
def getMetaSource(self):
    """Get the meta install location of this asset definition.

    This function determines where the contained .otl file is installed to in
    the current session.  Examples include "Scanned OTL Directories", "Current
    Hip File", "Fallback Libraries" or specific OPlibraries files.

    """
    return hou.hda.metaSource(self.libraryFilePath())


@add_to_module(hou.hda)
def removeMetaSource(meta_source):
    """Attempt to remove a meta source.

    Removing a meta source will uninstall the libraries it was responsible for.

    """
    return _cpp_methods.removeMetaSource(meta_source)


@add_to_module(hou.hda)
def librariesInMetaSource(meta_source):
    """Get a list of library paths in a meta source."""
    # Get the any libraries in the meta source.
    result = _cpp_methods.getLibrariesInMetaSource(meta_source)

    # Return a tuple of the valid values.
    return _clean_string_values(result)


@add_to_class(hou.HDADefinition)
def isDummy(self):
    """Check if this definition is a dummy definition.

    A dummy, or empty definition is created by Houdini when it cannot find
    an operator definition that it needs in the current session.
    """
    return _cpp_methods.isDummyDefinition(
        self.libraryFilePath(),
        self.nodeTypeCategory().name(),
        self.nodeTypeName()
    )

