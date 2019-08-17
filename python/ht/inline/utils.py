"""Utility functions to support custom inlinecpp functions."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import ctypes

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

# Mapping between geometry types and corresponding GA_AttributeOwner values.
_GEOMETRY_ATTRIB_MAP = {
    hou.Vertex: 0,
    hou.Point: 1,
    hou.Prim: 2,
    hou.Geometry: 3
}

# Mapping between hou.geometryTypes and corresponding GA_AttributeOwner values.
_GEOMETRY_TYPE_MAP = {
    hou.geometryType.Vertices: 0,
    hou.geometryType.Points: 1,
    hou.geometryType.Primitives: 2
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


# =============================================================================
# FUNCTIONS
# =============================================================================

def build_c_double_array(values):
    """Convert a list of numbers to a ctypes double array.

    :param values: A list of floats.
    :type values: list(float)
    :return: The values as ctypes compatible values.
    :rtype: list(ctypes.c_double)

    """
    arr = (ctypes.c_double * len(values))(*values)

    return arr


def build_c_int_array(values):
    """Convert a list of numbers to a ctypes int array.

    :param values: A list of ints.
    :type values: list(int)
    :return: The values as ctypes compatible values.
    :rtype: list(ctypes.c_int)

    """
    arr = (ctypes.c_int * len(values))(*values)

    return arr


def build_c_string_array(values):
    """Convert a list of strings to a ctypes char * array.

    :param values: A list of strings.
    :type values: list(str)
    :return: The values as ctypes compatible values.
    :rtype: list(ctypes.c_char_p)

    """
    arr = (ctypes.c_char_p * len(values))(*values)

    return arr


def clean_string_values(values):
    """Process a string list, removing empty strings.

    :param values: A list of strings to clean.
    :type values: list(str)
    :return: A clean tuple.
    :rtype: tuple(str)

    """
    return tuple([val for val in values if val])


def find_attrib(geometry, attrib_type, name):
    """Find an attribute with a given name and type on the geometry.

    :param geometry: The geometry to find an attribute on.
    :type geometry: hou.Geometry
    :param attrib_type: The attribute type.
    :type attrib_type: hou.attribType.
    :param name: The attribute name.
    :type name: str
    :return: A found attribute, otherwise None.
    :rtype: hou.Attrib or None

    """
    if attrib_type == hou.attribType.Vertex:
        return geometry.findVertexAttrib(name)

    elif attrib_type == hou.attribType.Point:
        return geometry.findPointAttrib(name)

    elif attrib_type == hou.attribType.Prim:
        return geometry.findPrimAttrib(name)

    elif attrib_type == hou.attribType.Global:
        return geometry.findGlobalAttrib(name)

    else:
        raise ValueError("Expected hou.attribType, got {}".format(type(attrib_type)))


def find_group(geometry, group_type, name):
    """Find a group with a given name and type.

    group_type corresponds to the integer returned by _get_group_type()

    :param geometry: The geometry to find the group in.
    :type geometry: hou.Geometry
    :param group_type: The group type.
    :type group_type: int
    :param name: The attribute name.
    :type name: str
    :return: A found group.
    :rtype: hou.EdgeGroup or hou.PointGroup or hou.PrimGroup

    """
    if group_type == 0:
        return geometry.findPointGroup(name)

    elif group_type == 1:
        return geometry.findPrimGroup(name)

    elif group_type == 2:
        return geometry.findEdgeGroup(name)

    else:
        raise ValueError("Invalid group type {}".format(group_type))


def geo_details_match(geometry1, geometry2):
    """Test if two hou.Geometry objects point to the same detail.

    :param geometry1: A geometry detail.
    :type geometry1: hou.Geometry
    :param geometry2: A geometry detail.
    :type geometry2: hou.Geometry
    :return: Whether or not the objects represent the same detail.
    :rtype: bool

    """
    handle1 = geometry1._guDetailHandle()
    handle2 = geometry2._guDetailHandle()

    details_match = int(handle1._asVoidPointer()) == int(handle2._asVoidPointer())

    handle1.destroy()
    handle2.destroy()

    return details_match


def get_attrib_owner(attribute_type):
    """Get an HDK compatible attribute owner value.

    :param attribute_type: The type of attribute.
    :type attribute_type: hou.attribType
    :return: An HDK attribute owner value.
    :rtype: int

    """
    try:
        return _ATTRIB_TYPE_MAP[attribute_type]

    except KeyError:
        raise ValueError("Invalid attribute type: {}".format(attribute_type))


def get_attrib_owner_from_geometry_entity_type(entity_type):
    """Get an HDK compatible attribute owner value from a geometry class.

    The type can be of hou.Geometry, hou.Point, hou.Prim (or subclasses) or hou.Vertex.

    :param entity_type: The entity to get a attribute owner for.
    :type entity_type: hou.Vertex or hou.Point or hou.Prim or hou.Geometry
    :return: An HDK attribute owner value.
    :rtype: int

    """
    # If the class is a base class in the map then just return it.
    try:
        return _GEOMETRY_ATTRIB_MAP[entity_type]

    except KeyError:
        pass

    # If it is not in the map then it is most likely a subclass of hou.Prim,
    # such as hou.Polygon, hou.Face, hou.Volume, etc.  We will check the class
    # against being a subclass of any of our valid types and if it is, return
    # the owner of that class.
    for key, value in _GEOMETRY_ATTRIB_MAP.items():
        if issubclass(entity_type, key):
            return value

    # Something went wrong so raise an exception.
    raise ValueError("Invalid entity type: {}".format(entity_type))


def get_attrib_owner_from_geometry_type(geometry_type):
    """Get an HDK compatible attribute owner value from a hou.geometryType.

    :param geometry_type: The entity to get a attribute owner for.
    :type geometry_type: hou.geometryType
    :return: An HDK attribute owner value.
    :rtype: int

    """
    # If the class is a base class in the map then just return it.
    try:
        return _GEOMETRY_TYPE_MAP[geometry_type]

    except KeyError:
        # Something went wrong so raise an exception.
        raise ValueError("Invalid geometry type: {}".format(geometry_type))


def get_attrib_storage(data_type):
    """Get an HDK compatible attribute storage class value.

    :param data_type: The type of data to store.
    :type data_type: hou.attribData
    :return: An HDK attribute storage type.
    :rtype: int

    """
    try:
        return _ATTRIB_STORAGE_MAP[data_type]

    except KeyError:
        raise ValueError("Invalid data type: {}".format(data_type))


def get_group_attrib_owner(group):
    """Get an HDK compatible group attribute type value.

    :param group: The group to get the attribute owner for.
    :type group: hou.PointGroup or hou.PrimGroup
    :return: An HDK attribute owner value.
    :rtype: int

    """
    try:
        return _GROUP_ATTRIB_MAP[type(group)]

    except KeyError:
        raise ValueError("Invalid group type")


def get_group_type(group):
    """Get an HDK compatible group type value.

    :param group: The group to get the group type for.
    :type group: hou.EdgeGroup or hou.PointGroup or hou.PrimGroup
    :return: An HDK group type value.
    :rtype: int

    """
    try:
        return _GROUP_TYPE_MAP[type(group)]

    except KeyError:
        raise ValueError("Invalid group type")


def get_nodes_from_paths(paths):
    """Convert a list of string paths to hou.Node objects.

    :param paths: A list of paths.
    :type paths: list(str)
    :return: A tuple of hou.Node objects.
    :rtype: tuple(hou.Node)

    """
    return tuple([hou.node(path) for path in paths if path])


def get_points_from_list(geometry, point_list):
    """Convert a list of point numbers to hou.Point objects.

    :param geometry: The geometry to get points for.
    :type geometry: hou.Geometry
    :param point_list: A list of point numbers.
    :type point_list: list(int)
    :return: Matching points on the geometry.
    :rtype: tuple(hou.Point)

    """
    # Return a empty tuple if the point list is empty.
    if not point_list:
        return ()

    # Convert the list of integers to a space separated string.
    point_str = ' '.join([str(i) for i in point_list])

    # Glob for the specified points.
    return geometry.globPoints(point_str)


def get_prims_from_list(geometry, prim_list):
    """Convert a list of primitive numbers to hou.Prim objects.

    :param geometry: The geometry to get prims for.
    :type geometry: hou.Geometry
    :param prim_list: A list of prim numbers.
    :type prim_list: list(int)
    :return: Matching prims on the geometry.
    :rtype: tuple(hou.Prim)

    """
    # Return a empty tuple if the prim list is empty.
    if not prim_list:
        return ()

    # Convert the list of integers to a space separated string.
    prim_str = ' '.join([str(i) for i in prim_list])

    # Glob for the specified prims.
    return geometry.globPrims(prim_str)

