"""Utility functions to support custom inlinecpp functions."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
from __future__ import annotations
import ctypes
from typing import List, Optional, Sequence, Tuple, Union

# Houdini Imports
import hou


# =============================================================================
# GLOBALS
# =============================================================================

# Tuple of all valid attribute data types.
_ALL_ATTRIB_DATA_TYPES = (
    hou.attribData.Float,
    hou.attribData.Int,
    hou.attribData.String,
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
_GEOMETRY_ATTRIB_MAP = {hou.Vertex: 0, hou.Point: 1, hou.Prim: 2, hou.Geometry: 3}

# Mapping between hou.geometryTypes and corresponding GA_AttributeOwner values.
_GEOMETRY_TYPE_MAP = {
    hou.geometryType.Vertices: 0,
    hou.geometryType.Points: 1,
    hou.geometryType.Primitives: 2,
}

# Mapping between group types and corresponding GA_AttributeOwner values.
_GROUP_ATTRIB_MAP = {hou.VertexGroup: 0, hou.PointGroup: 1, hou.PrimGroup: 2}

# Mapping between group types and corresponding GA_GroupType values.
_GROUP_TYPE_MAP = {
    hou.PointGroup: 0,
    hou.PrimGroup: 1,
    hou.EdgeGroup: 2,
    hou.VertexGroup: 3,
}


# =============================================================================
# FUNCTIONS
# =============================================================================


def build_c_double_array(values: Sequence[float]) -> ctypes.Array:
    """Convert a list of numbers to a ctypes c_double array.

    :param values: A list of floats.
    :return: The values as ctypes compatible values.

    """
    arr = (ctypes.c_double * len(values))(*values)

    return arr


def build_c_int_array(values: Sequence[int]) -> ctypes.Array:
    """Convert a list of numbers to a ctypes c_int array.

    :param values: A list of ints.
    :return: The values as ctypes compatible values.

    """
    arr = (ctypes.c_int * len(values))(*values)

    return arr


def build_c_string_array(values: Sequence[str]) -> ctypes.Array:
    """Convert a list of strings to a ctypes c_char_p array.

    :param values: A list of strings.
    :return: The values as ctypes compatible values.

    """
    converted = [string_encode(value) for value in values]
    arr = (ctypes.c_char_p * len(values))(*converted)

    return arr


def clean_string_values(values: List[str]) -> Tuple[str, ...]:
    """Process a string list, remove empty strings, and convert to utf-8.

    :param values: A list of strings to clean.
    :return: A clean tuple.

    """
    return tuple([string_decode(val) for val in values if val])


def find_attrib(
    geometry: hou.Geometry, attrib_type: hou.attribType, name: str
) -> Optional[hou.Attrib]:
    """Find an attribute with a given name and type on the geometry.

    :param geometry: The geometry to find an attribute on.
    :param attrib_type: The attribute type.
    :param name: The attribute name.
    :return: A found attribute, otherwise None.

    """
    if attrib_type == hou.attribType.Vertex:
        return geometry.findVertexAttrib(name)

    if attrib_type == hou.attribType.Point:
        return geometry.findPointAttrib(name)

    if attrib_type == hou.attribType.Prim:
        return geometry.findPrimAttrib(name)

    if attrib_type == hou.attribType.Global:
        return geometry.findGlobalAttrib(name)

    raise ValueError("Expected hou.attribType, got {}".format(type(attrib_type)))


def find_group(
    geometry: hou.Geometry, group_type: int, name: str
) -> Optional[Union[hou.EdgeGroup, hou.PointGroup, hou.PrimGroup, hou.VertexGroup]]:
    """Find a group with a given name and type.

    group_type corresponds to the integer returned by _get_group_type()

    :param geometry: The geometry to find the group in.
    :param group_type: The group type.
    :param name: The attribute name.
    :return: A found group.

    """
    if group_type == 0:
        return geometry.findPointGroup(name)

    if group_type == 1:
        return geometry.findPrimGroup(name)

    if group_type == 2:
        return geometry.findEdgeGroup(name)

    if group_type == 3:
        return geometry.findVertexGroup(name)

    raise ValueError("Invalid group type {}".format(group_type))


def geo_details_match(geometry1: hou.Geometry, geometry2: hou.Geometry) -> bool:
    """Test if two hou.Geometry objects point to the same detail.

    :param geometry1: A geometry detail.
    :param geometry2: A geometry detail.
    :return: Whether or not the objects represent the same detail.

    """
    # pylint: disable=protected-access
    handle1 = geometry1._guDetailHandle()
    handle2 = geometry2._guDetailHandle()

    details_match = int(handle1._asVoidPointer()) == int(handle2._asVoidPointer())

    handle1.destroy()
    handle2.destroy()

    return details_match


def get_attrib_owner(attribute_type: hou.attribType) -> int:
    """Get an HDK compatible attribute owner value.

    :param attribute_type: The type of attribute.
    :return: An HDK attribute owner value.

    """
    try:
        return _ATTRIB_TYPE_MAP[attribute_type]

    except KeyError as exc:
        raise ValueError("Invalid attribute type: {}".format(attribute_type)) from exc


def get_attrib_owner_from_geometry_entity_type(
    entity_type: Union[hou.Point, hou.Prim, hou.Vertex]
) -> int:
    """Get an HDK compatible attribute owner value from a geometry class.

    The type can be of hou.Geometry, hou.Point, hou.Prim (or subclasses) or hou.Vertex.

    :param entity_type: The entity to get a attribute owner for.
    :return: An HDK attribute owner value.

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
    for key, value in list(_GEOMETRY_ATTRIB_MAP.items()):
        if issubclass(entity_type, key):
            return value

    # Something went wrong so raise an exception.
    raise ValueError("Invalid entity type: {}".format(entity_type))


def get_attrib_owner_from_geometry_type(geometry_type: hou.geometryType) -> int:
    """Get an HDK compatible attribute owner value from a hou.geometryType.

    :param geometry_type: The entity to get a attribute owner for.
    :return: An HDK attribute owner value.

    """
    # If the class is a base class in the map then just return it.
    try:
        return _GEOMETRY_TYPE_MAP[geometry_type]

    except KeyError as exc:
        # Something went wrong so raise an exception.
        raise ValueError("Invalid geometry type: {}".format(geometry_type)) from exc


def get_attrib_storage(data_type: hou.attribType) -> int:
    """Get an HDK compatible attribute storage class value.

    :param data_type: The type of data to store.
    :return: An HDK attribute storage type.

    """
    try:
        return _ATTRIB_STORAGE_MAP[data_type]

    except KeyError as exc:
        raise ValueError("Invalid data type: {}".format(data_type)) from exc


def get_entity_data(
    entity: Union[hou.Geometry, hou.Point, hou.Prim, hou.Vertex]
) -> Tuple[Union[hou.Geometry, hou.Point, hou.Prim, hou.Vertex], hou.Geometry, int]:
    """Get entity data from a list of entities.

    :param entity: A geometry entity.
    :return: The entity type, geometry for the entities and the entity indices.

    """
    # Copying to a geometry entity.
    if not isinstance(entity, hou.Geometry):
        # Get the source entity's geometry.
        geometry = entity.geometry()

        if isinstance(entity, hou.Vertex):
            entity_num = entity.linearNumber()

        else:
            entity_num = entity.number()

    # hou.Geometry means copying to detail attributes.
    else:
        geometry = entity
        entity_num = 0

    # Using __class__ is ghetto, but easier for testing since a MagicMock will
    # return the desired value whereas type() will not :(
    return entity.__class__, geometry, entity_num


def get_entity_data_from_list(
    entities: List[Union[hou.Geometry, hou.Point, hou.Prim, hou.Vertex]]
) -> Tuple[
    Union[hou.Geometry, hou.Point, hou.Prim, hou.Vertex], hou.Geometry, List[int]
]:
    """Get entity data from a list of entities.

    :param entities: List of geometry entities.
    :return: The entity type, geometry for the entities and the entity indices.

    """
    entity = entities[0]

    # Copying to a geometry entity.
    if not isinstance(entity, hou.Geometry):
        # Get the source entity's geometry.
        geometry = entity.geometry()

        if isinstance(entity, hou.Vertex):
            entity_nums = [ent.linearNumber() for ent in entities]

        else:
            entity_nums = [ent.number() for ent in entities]

    # hou.Geometry means copying to detail attributes.
    else:
        geometry = entity
        entity_nums = [0]

    # Using __class__ is ghetto, but easier for testing since a MagicMock will
    # return the desired value whereas type() will not :(
    return entity.__class__, geometry, entity_nums


def get_group_attrib_owner(group: Union[hou.PointGroup, hou.PrimGroup]) -> int:
    """Get an HDK compatible group attribute type value.

    :param group: The group to get the attribute owner for.
    :return: An HDK attribute owner value.

    """
    try:
        return _GROUP_ATTRIB_MAP[type(group)]

    except KeyError as exc:
        raise ValueError("Invalid group type") from exc


def get_group_type(group: Union[hou.EdgeGroup, hou.PointGroup, hou.PrimGroup]) -> int:
    """Get an HDK compatible group type value.

    :param group: The group to get the group type for.
    :return: An HDK group type value.

    """
    try:
        return _GROUP_TYPE_MAP[type(group)]

    except KeyError as exc:
        raise ValueError("Invalid group type") from exc


def get_multiparm_containing_folders(
    name: str, parm_template_group: hou.ParmTemplateGroup
) -> Tuple[hou.FolderParmTemplate, ...]:
    """Given a parameter template name, return a list of containing multiparms.

    If the name is contained in one or more multiparm folders, the returned templates
    will be ordered from innermost to outermost

    |_ outer
      |_ inner#
        |_ param#_#

    In a situation like above, querying for containing folders of param#_# would
    result in a tuple ordered as follows: (<hou.FolderParmTemplate inner#>,  <hou.FolderParmTemplate outer>)

    :param name: The name of the parameter to get the containing names for.
    :param parm_template_group: A parameter template group for a nde.
    :return: A tuple of containing multiparm templates, if any.

    """
    # A list of containing folders.
    containing_folders = []

    # Get the folder the parameter is in.
    containing_folder = parm_template_group.containingFolder(name)

    # Keep looking for containing folders until there are no.
    while True:
        # Add a containing multiparm folder to the list.
        if is_parm_template_multiparm_folder(containing_folder):
            containing_folders.append(containing_folder)

        # Try to find the parent containing folder.
        try:
            containing_folder = parm_template_group.containingFolder(containing_folder)

        # Not inside a folder so bail out.
        except hou.OperationFailed:
            break

    return tuple(containing_folders)


def get_multiparm_container_offsets(
    name: str, parm_template_group: hou.ParmTemplateGroup
) -> Tuple[int, ...]:
    """Given a parameter template name, return a list of containing multiparm folder
    offsets.


    If the name is contained in one or more multiparm folders, the returned offsets
    will be ordered outermost to innermost

    |_ outer (star1ing offset 0)
      |_ inner# (starting offset 1)
        |_ param#_#

    In a situation like above, querying for containing offsets of param#_# would
    result in a tuple ordered as follows: (0, 1)

    :param name: The name of the parameter to get the containing offsets for.
    :param parm_template_group: A parameter template group for a nde.
    :return: A tuple of containing multiparm offsets, if any.

    """
    # A list of contain folders.
    containing_folders = get_multiparm_containing_folders(name, parm_template_group)

    # A list to store the parent multiparm folder offsets.
    offsets = []

    # The containing folder list is ordered by folder closest to the base parameter.
    # We want to process that list in reverse so the first offset item will be for the
    # outermost parameter and match the ordered provided by the user.
    for folder in reversed(containing_folders):
        # Get the start offset. The default offset is 1 so if the tag is not
        # set we use that as a default.
        offsets.append(get_multiparm_start_offset(folder))

    return tuple(offsets)


def get_multiparm_start_offset(parm_template: hou.ParmTemplate) -> int:
    """Get the start offset of items in the multiparm.

    :param parm_template: A multiparm folder parm template
    :return: The start offset of the multiparm.

    """
    if not is_parm_template_multiparm_folder(parm_template):
        raise ValueError("Parameter template is not a multiparm folder")

    return int(parm_template.tags().get("multistartoffset", 1))


def get_nodes_from_paths(paths: List[str]) -> Tuple[hou.Node, ...]:
    """Convert a list of string paths to hou.Node objects.

    :param paths: A list of paths.
    :return: A tuple of hou.Node objects.

    """
    return tuple(hou.node(path) for path in paths if path)


def get_points_from_list(
    geometry: hou.Geometry, point_list: List[int]
) -> Tuple[hou.Point, ...]:
    """Convert a list of point numbers to hou.Point objects.

    :param geometry: The geometry to get points for.
    :param point_list: A list of point numbers.
    :return: Matching points on the geometry.

    """
    # Return a empty tuple if the point list is empty.
    if not point_list:
        return tuple()

    # Convert the list of integers to a space separated string.
    point_str = " ".join([str(i) for i in point_list])

    # Glob for the specified points.
    return geometry.globPoints(point_str)


def get_prims_from_list(
    geometry: hou.Geometry, prim_list: List[int]
) -> Tuple[hou.Prim, ...]:
    """Convert a list of primitive numbers to hou.Prim objects.

    :param geometry: The geometry to get prims for.
    :param prim_list: A list of prim numbers.
    :return: Matching prims on the geometry.

    """
    # Return a empty tuple if the prim list is empty.
    if not prim_list:
        return tuple()

    # Convert the list of integers to a space separated string.
    prim_str = " ".join([str(i) for i in prim_list])

    # Glob for the specified prims.
    return geometry.globPrims(prim_str)


def is_parm_template_multiparm_folder(parm_template: hou.ParmTemplate) -> bool:
    """Returns True if the parm template represents a multiparm folder type.

    :param parm_template: The parameter template to check.
    :return: Whether or not the template represents a multiparm folder.

    """
    if not isinstance(parm_template, hou.FolderParmTemplate):
        return False

    return parm_template.folderType() in (
        hou.folderType.MultiparmBlock,
        hou.folderType.ScrollingMultiparmBlock,
        hou.folderType.TabbedMultiparmBlock,
    )


def string_decode(value: Union[bytes, str]) -> str:
    """Decode a value.

    :param value: The value to decode.
    :return: The decoded value

    """
    if isinstance(value, bytes):
        return value.decode("utf-8")

    return value


def string_encode(value: Union[float, int, str]) -> bytes:
    """Encode a value.

    :param value: The value to encode.
    :return: The encoded value

    """
    return str(value).encode("utf-8")


def validate_multiparm_resolve_values(name: str, indices: Sequence[int]):
    """Validate a multiparm token string and the indices to be resolved.

    This function will raise a ValueError if there are not enough indices
    supplied for the number of tokens.

    :param name: The parameter name to validate.
    :param indices: The indices to format into the token string.
    :return:

    """
    # Get the number of multiparm tokens in the name.
    multi_token_count = name.count("#")

    # Ensure that there are enough indices for the name.  Houdini can handle too many
    # indices but if there are not enough it won't like that and return an unexpected value.
    if multi_token_count > len(indices):
        raise ValueError(
            "Not enough indices provided. Parameter {} expects {}, {} token(s) provided.".format(
                name, multi_token_count, len(indices)
            )
        )
