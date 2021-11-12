"""This module contains functions designed to extend the Houdini Object Model
(HOM) through the use of the inlinecpp module and regular Python.

The functions in this module are not mean to be called directly.  This module
uses Python decorators to attach the functions to the corresponding HOM classes
and modules they are meant to extend.

"""

# =============================================================================
# IMPORTS
# =============================================================================

from __future__ import annotations

# Standard Library
import ast
import math
from typing import TYPE_CHECKING, List, Optional, Tuple, Union

# Houdini Toolbox
from ht.inline import utils
from ht.inline.lib import cpp_methods as _cpp_methods

# Houdini
import hou

if TYPE_CHECKING:
    GeometryEntity = Union[hou.Geometry, hou.Point, hou.Prim, hou.Vertex]
    GeometryEntityList = List[GeometryEntity]
    ElementGroupList = List[Union[hou.PointGroup, hou.PrimGroup, hou.VertexGroup]]
    StringTuple = Tuple[str, ...]


# =============================================================================
# EXCEPTIONS
# =============================================================================


class RunPyStatementsError(Exception):
    """Exception for exceptions raised while running Python statements.

    The original exception information is available via the "message"
    attribute.

    The name of the raised exception is available via the "exception_name"
    attribute.

    :param message: The exception message.
    :param exception_name: The name of the c++ exception.

    """

    def __init__(self, message: str, exception_name: str = None):
        super().__init__(message)

        self.exception_name = exception_name


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _assert_prim_vertex_index(prim: hou.Prim, index: int):
    """Validate that a vertex index is valid for a primitive.

    If an index is not valid a IndexError will be raised.

    :param prim: The primitive to validate the index for.
    :param index: The vertex index.
    :return:

    """
    # If the index is less than 0, throw an exception since it's not valid.
    if index < 0:
        raise IndexError("Index must be 0 or greater.")

    # If the index is too high it is also invalid.
    if index >= num_prim_vertices(prim):
        raise IndexError(f"Invalid index: {index}")


def _get_names_in_folder(parent_template: hou.FolderParmTemplate) -> StringTuple:
    """Get a list of template names inside a template folder.

    This should only really ever be called originally with a multiparm template.

    :param parent_template: The parm template to get items for.
    :return: A list of template names inside the template.

    """
    names: List[str] = []

    for parm_template in parent_template.parmTemplates():
        if isinstance(parm_template, hou.FolderParmTemplate):
            # If the template is a folder (but not a multiparm folder) then we
            # need to get the parms inside it as well since they are technically siblings.
            if not utils.is_parm_template_multiparm_folder(parm_template):
                # if parm_template.folderType() in (hou.folderType.Simple, hou.folderType.Collapsible):
                names.extend(_get_names_in_folder(parm_template))

            else:
                # elif utils.is_parm_template_multiparm_folder(parm_template):
                names.append(parm_template.name())

        # else:
        #     names.append(parm_template.name())

        else:
            names.append(parm_template.name())

    return tuple(str(name) for name in names)


# =============================================================================
# FUNCTIONS
# =============================================================================


def clear_caches(cache_names: Optional[List[str]] = None):
    """Clear internal Houdini caches.

    Cache names match those displayed in the Cache Manager window.

    If cache_names is None then all caches will be cleared.

    :param cache_names: Optional list of caches to clear.
    :return:

    """
    # If the value is None then we will pass an empty string to clear all the
    # caches.
    if cache_names is None:
        cache_names = [""]

    for cache_name in cache_names:
        _cpp_methods.clearCacheByName(utils.string_encode(cache_name))


def run_python_statements(code: str, use_new_context: bool = True):
    """Run python statements using Houdini's Python execution code.

    By default the code is run in a new Python context.  If setting
    use_new_context to False the statements will be run in the global namespace.

    If any errors occurring during the run this function will raise a
    RunPyStatementsError exception which will contain the original exception
    data.

    :param code: A block of Python code.
    :param use_new_context: Run the code in a new context.
    :return:

    """
    if use_new_context:
        result = _cpp_methods.run_python_statements_in_new_context(code)

    else:
        result = _cpp_methods.run_python_statements(code)

    if result.occurred:
        message = result.detailed
        exception_name = result.name

        raise RunPyStatementsError(message, exception_name)


def clear_user_data(node: hou.Node):
    """Clear all user data on a node.

    This does not create an Undo event.

    :param node: The node to clear the user data from.
    :return:

    """
    _cpp_methods.clearUserData(node)


def has_user_data(node: hou.Node, name: str) -> bool:
    """Check if a node has user data under the supplied name.

    :param node: The node to check for user data on.
    :param name: The user data name.
    :return: Whether or not the node has user data of the given name.

    """
    return _cpp_methods.hasUserData(node, name)


def set_user_data(node: hou.Node, name: str, value: str):
    """Sets user data.

    This does not create an Undo event.

    :param node: The node to set user data on.
    :param name: The user data name.
    :param value: The user data value.
    :return:

    """
    _cpp_methods.setUserData(node, name, value)


def delete_user_data(node: hou.Node, name: str):
    """Deletes any user data under the supplied name.

    This does not create an Undo event.

    :param node: The node to delete for user data from.
    :param name: The user data name.
    :return:

    """
    _cpp_methods.deleteUserData(node, name)


def hash_string(value: str) -> int:
    """Generate a hash value from a string.

    This is the equivalent of the random_shash() VEX function.

    Uses SYSstring_hash() from SYS_String.h

    :param value: The value to hash.
    :return: The hashed value.

    """
    return _cpp_methods.hashString(value)


def is_rendering() -> bool:
    """Check if Houdini is rendering or not.

    :return: Whether or not Houdini is rendering.

    """
    return _cpp_methods.isRendering()


def get_global_variable_names(dirty: bool = False) -> StringTuple:
    """Get a tuple of all global variable names.

    If dirty is True, return only 'dirty' variables.  A dirty variable is a
    variable that has been created or modified but not updated throughout the
    session by something like the 'varchange' hscript command.

    :param dirty: Whether or not to return only dirty variables.
    :return: A tuple of global variable names.

    """
    # Get all the valid variable names.
    var_names = _cpp_methods.getGlobalVariableNames(dirty)

    # Remove any empty names.
    return utils.clean_string_values(var_names)


def get_variable_names(dirty: bool = False) -> StringTuple:
    """Get a tuple of all available variable names.

    If dirty is True, return only 'dirty' variables.  A dirty variable is a
    variable that has been created or modified but not updated throughout the
    session by something like the 'varchange' hscript command.

    :param dirty: Whether or not to return only dirty variables.
    :return: A tuple of variable names.

    """
    # Get all the valid variable names.
    var_names = _cpp_methods.getVariableNames(dirty)

    # Remove any empty names.
    return utils.clean_string_values(var_names)


def get_variable_value(name: str) -> Optional[str]:
    """Returns the value of the named variable.

    :param name: The variable name.
    :return: The value of the variable if it exists, otherwise None

    """
    # If the variable name isn't in list of variables, return None.
    if name not in get_variable_names():
        return None

    # Get the value of the variable.
    value = utils.string_decode(
        _cpp_methods.getVariableValue(utils.string_encode(name))
    )

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


def set_variable(name: str, value: Union[float, int, str], local: bool = False):
    """Set a variable.

    :param name: The variable name.
    :param value: The variable value.
    :param local: Whether or not to set the variable as local.
    :return:

    """
    _cpp_methods.setVariable(
        utils.string_encode(name), utils.string_encode(value), local
    )


def unset_variable(name: str):
    """Unset a variable.

    This function will do nothing if no such variable exists.

    :param name: The variable name.
    :return:

    """
    _cpp_methods.unsetVariable(utils.string_encode(name))


def emit_var_change():
    """Cook any operators using changed variables.

    When a variable's value changes, the OPs which reference that variable are
    not automatically cooked. Use this function to cook all OPs when a variable
    they use changes.

    :return:

    """
    _cpp_methods.emitVarChange()


def expand_range(pattern: str) -> Tuple[int, ...]:
    """Expand a string range into a tuple of values.

    This function will do string range expansion.  Examples include '0-15',
    '0 4 10-100', '1-100:2', etc.  See Houdini's documentation about geometry
    groups for more information. Wildcards are not supported.

    :param pattern: The pattern to expand:
    :return: A tuple of expanded values.

    """
    return tuple(_cpp_methods.expandRange(utils.string_encode(pattern)))


def num_points(geometry: hou.Geometry) -> int:
    """Get the number of points in the geometry.

    This should be quicker than len(hou.Geometry.iterPoints()) since it uses
    the 'pointcount' intrinsic value from the detail.

    :param geometry: The geometry to get the point count for.
    :return: The point count:

    """
    return geometry.intrinsicValue("pointcount")


def num_prims(geometry: hou.Geometry) -> int:
    """Get the number of primitives in the geometry.

    This should be quicker than len(hou.Geometry.iterPrims()) since it uses
    the 'primitivecount' intrinsic value from the detail.

    :param geometry: The geometry to get the primitive count for.
    :return: The primitive count:

    """
    return geometry.intrinsicValue("primitivecount")


def num_vertices(geometry: hou.Geometry) -> int:
    """Get the number of vertices in the geometry.

    :param geometry: The geometry to get the vertex count for.
    :return: The vertex count.

    """
    return geometry.intrinsicValue("vertexcount")


def num_prim_vertices(prim: hou.Prim) -> int:
    """Get the number of vertices belonging to the primitive.

    :param prim: The primitive to get the vertex count of.
    :return: The vertex count.

    """
    return prim.intrinsicValue("vertexcount")


def sort_geometry_by_values(
    geometry: hou.Geometry, geometry_type: hou.geometryType, values: List[float]
):
    """Sort points or primitives based on a list of corresponding values.

    The list of values must be the same length as the number of geometry
    elements to be sourced.

    :param geometry: The geometry to sort.
    :param geometry_type: The type of geometry to sort.
    :param values: The values to sort by.
    :return:

    """
    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    num_values = len(values)

    if geometry_type == hou.geometryType.Points:
        # Check we have enough points.
        if num_values != num_points(geometry):
            raise hou.OperationFailed(
                "Length of values must equal the number of points."
            )

    elif geometry_type == hou.geometryType.Primitives:
        # Check we have enough primitives.
        if num_values != num_prims(geometry):
            raise hou.OperationFailed(
                "Length of values must equal the number of prims."
            )

    else:
        raise ValueError("Geometry type must be points or primitives.")

    attrib_owner = utils.get_attrib_owner_from_geometry_type(geometry_type)

    # Construct a ctypes double array to pass the values.
    c_values = utils.build_c_double_array(values)

    _cpp_methods.sortGeometryByValues(geometry, attrib_owner, c_values)


def create_point_at_position(
    geometry: hou.Geometry, position: hou.Vector3
) -> hou.Point:
    """Create a new point located at a position.

    :param geometry: The geometry to create a new point for.
    :param position: The point position.
    :return: The new point.

    """
    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    _cpp_methods.createPointAtPosition(geometry, position)

    return geometry.iterPoints()[-1]


def create_n_points(geometry: hou.Geometry, npoints: int) -> Tuple[hou.Point, ...]:
    """Create a specific number of new points.

    :param geometry: The geometry to create points for.
    :param npoints: The number of points to create.
    :return: The newly created points.

    """
    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    if npoints <= 0:
        raise ValueError("Invalid number of points.")

    _cpp_methods.createNPoints(geometry, npoints)

    return tuple(geometry.points()[-npoints:])


def merge_point_group(geometry: hou.Geometry, group: hou.PointGroup):
    """Merges points from a group into the geometry.

    :param geometry: The geometry to merge into.
    :param group: The group to merge.
    :return:

    """
    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    if not isinstance(group, hou.PointGroup):
        raise ValueError("Group is not a point group.")

    _cpp_methods.mergePointGroup(
        geometry, group.geometry(), utils.string_encode(group.name())
    )


def merge_points(geometry: hou.Geometry, points: List[hou.Point]):
    """Merge a list of points from a detail into the geometry.

    :param geometry: The geometry to merge into.
    :param points: A list of points to merge.
    :return:

    """
    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    c_values = utils.build_c_int_array([point.number() for point in points])

    _cpp_methods.mergePoints(geometry, points[0].geometry(), c_values, len(c_values))


def merge_prim_group(geometry: hou.Geometry, group: hou.PrimGroup):
    """Merges primitives from a group into the geometry.

    :param geometry: The geometry to merge into.
    :param group: The group to merge.
    :return:

    """
    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    if not isinstance(group, hou.PrimGroup):
        raise ValueError("Group is not a primitive group.")

    _cpp_methods.mergePrimGroup(
        geometry, group.geometry(), utils.string_encode(group.name())
    )


def merge_prims(geometry: hou.Geometry, prims: List[hou.Prim]):
    """Merges a list of primitives from a detail into the geometry.

    :param geometry: The geometry to merge into.
    :param prims: A list of points to merge.
    :return:

    """
    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    c_values = utils.build_c_int_array([prim.number() for prim in prims])

    _cpp_methods.mergePrims(geometry, prims[0].geometry(), c_values, len(c_values))


def copy_attribute_values(
    source_element: GeometryEntity,
    source_attribs: List[hou.Attrib],
    target_element: GeometryEntity,
):
    """Copy a list of attributes from the source element to the target element.

    :param source_element: The element to copy from.
    :param source_attribs: A list of attributes to copy.
    :param target_element: The element to copy to.
    :return:

    """
    target_type, target_geometry, target_entity_num = utils.get_entity_data(
        target_element
    )

    # Make sure the target geometry is not read only.
    if target_geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    source_type, source_geometry, source_entity_num = utils.get_entity_data(
        source_element
    )

    # Get the attribute owners from the elements.
    target_owner = utils.get_attrib_owner_from_geometry_entity_type(target_type)
    source_owner = utils.get_attrib_owner_from_geometry_entity_type(source_type)

    # Get the attribute names, ensuring we only use attributes on the
    # source's geometry.
    attrib_names = [
        attrib.name()
        for attrib in source_attribs
        if utils.get_attrib_owner(attrib.type()) == source_owner
        and attrib.geometry().sopNode() == source_geometry.sopNode()
    ]

    # Construct a ctypes string array to pass the strings.
    c_values = utils.build_c_string_array(attrib_names)

    _cpp_methods.copyAttributeValues(
        target_geometry,
        target_owner,
        target_entity_num,
        source_geometry,
        source_owner,
        source_entity_num,
        c_values,
        len(c_values),
        False,
    )


def batch_copy_attributes_by_indices(
    source_geometry: hou.Geometry,
    source_type: GeometryEntity,
    source_indices: Union[List[int], Tuple[int]],
    source_attribs: Union[List[hou.Attrib], Tuple[hou.Attrib]],
    target_geometry: hou.Geometry,
    target_type: GeometryEntity,
    target_indices: Union[List[int], Tuple[int]],
):
    """Batch copy attributes given lists of indices.

    :param source_geometry: The geometry to copy attributes from.
    :param source_type: The source entity type.
    :param source_indices: Source entity indices.
    :param source_attribs: The attributes to copy.
    :param target_geometry: The geometry to copy attributes to.
    :param target_type: The target entity type.
    :param target_indices: Target entity indices.
    :return:

    """
    # Make sure the geometry is not read only.
    if target_geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    num_source = len(source_indices)
    num_target = len(target_indices)

    if num_source != num_target:
        raise ValueError("Number of source and target elements must match")

    target_owner = utils.get_attrib_owner_from_geometry_entity_type(target_type)
    source_owner = utils.get_attrib_owner_from_geometry_entity_type(source_type)

    # Get the attribute names, ensuring we only use attributes on the
    # source's geometry.
    attrib_names = [
        attrib.name()
        for attrib in source_attribs
        if utils.get_attrib_owner(attrib.type()) == source_owner
        and attrib.geometry().sopNode() == source_geometry.sopNode()
    ]

    # Construct a ctypes string array to pass the strings.
    names_arr = utils.build_c_string_array(attrib_names)

    _cpp_methods.batchCopyAttributeValues(
        num_target,
        target_geometry,
        target_owner,
        utils.build_c_int_array(target_indices),
        source_geometry,
        source_owner,
        utils.build_c_int_array(source_indices),
        names_arr,
        len(names_arr),
        False,
    )


def batch_copy_attrib_values(
    source_elements: GeometryEntityList,
    source_attribs: Union[List[hou.Attrib], Tuple[hou.Attrib]],
    target_elements: GeometryEntityList,
):
    """Copy a list of attributes from the source element to the target element.

    :param source_elements: The elements to copy from.
    :param source_attribs: The attributes to copy.
    :param target_elements: The elements to copy to.
    :return:

    """
    num_elements = len(target_elements)

    if num_elements != len(source_elements):
        raise ValueError("Number of source and target elements must match")

    target_type, target_geometry, target_entity_nums = utils.get_entity_data_from_list(
        target_elements
    )

    # Make sure the target geometry is not read only.
    if target_geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    source_type, source_geometry, source_entity_nums = utils.get_entity_data_from_list(
        source_elements
    )

    # Get the attribute owners from the elements.
    target_owner = utils.get_attrib_owner_from_geometry_entity_type(target_type)
    source_owner = utils.get_attrib_owner_from_geometry_entity_type(source_type)

    # Get the attribute names, ensuring we only use attributes on the
    # source's geometry.
    attrib_names = [
        attrib.name()
        for attrib in source_attribs
        if utils.get_attrib_owner(attrib.type()) == source_owner
        and attrib.geometry().sopNode() == source_geometry.sopNode()
    ]

    # Construct a ctypes string array to pass the strings.
    arr = utils.build_c_string_array(attrib_names)

    _cpp_methods.batchCopyAttributeValues(
        num_elements,
        target_geometry,
        target_owner,
        utils.build_c_int_array(target_entity_nums),
        source_geometry,
        source_owner,
        utils.build_c_int_array(source_entity_nums),
        arr,
        len(attrib_names),
        False,
    )


def copy_group_membership(
    source_element: GeometryEntity,
    source_groups: ElementGroupList,
    target_element: GeometryEntity,
):
    """Copy group membership from the source element to the target element.

    :param source_element: The element to copy from.
    :param source_groups: A groups to copy membership of.
    :param target_element: The element to copy to.
    :return:

    """
    target_type, target_geometry, target_entity_num = utils.get_entity_data(
        target_element
    )

    # Make sure the target geometry is not read only.
    if target_geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    source_type, source_geometry, source_entity_num = utils.get_entity_data(
        source_element
    )

    # Get the attribute owners from the elements.
    target_owner = utils.get_attrib_owner_from_geometry_entity_type(target_type)
    source_owner = utils.get_attrib_owner_from_geometry_entity_type(source_type)

    # Get the group names, ensuring we only use attributes on the
    # source's geometry.
    group_names = [
        group.name()
        for group in source_groups
        if utils.get_group_attrib_owner(group) == source_owner
        and group.geometry().sopNode() == source_geometry.sopNode()
    ]

    # Construct a ctypes string array to pass the strings.
    c_values = utils.build_c_string_array(group_names)

    _cpp_methods.copyAttributeValues(
        target_geometry,
        target_owner,
        target_entity_num,
        source_geometry,
        source_owner,
        source_entity_num,
        c_values,
        len(c_values),
        True,
    )


def batch_copy_group_membership_by_indices(
    source_geometry: hou.Geometry,
    source_type: GeometryEntity,
    source_indices: Union[List[int], Tuple[int]],
    source_groups: ElementGroupList,
    target_geometry: hou.Geometry,
    target_type: GeometryEntity,
    target_indices: Union[List[int], Tuple[int]],
):
    """Batch copy group membership given lists of indices.

    :param source_geometry: The geometry to copy group membership from.
    :param source_type: The source entity type.
    :param source_indices: Source entity indices.
    :param source_groups: The groups to copy membership of.
    :param target_geometry: The geometry to copy group membership to.
    :param target_type: The target entity type.
    :param target_indices: Target entity indices.
    :return:

    """
    # Make sure the geometry is not read only.
    if target_geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    num_source = len(source_indices)
    num_target = len(target_indices)

    if num_source != num_target:
        raise ValueError("Number of source and target elements must match")

    target_owner = utils.get_attrib_owner_from_geometry_entity_type(target_type)
    source_owner = utils.get_attrib_owner_from_geometry_entity_type(source_type)

    # Get the group names, ensuring we only use attributes on the
    # source's geometry.
    group_names = [
        group.name()
        for group in source_groups
        if utils.get_group_attrib_owner(group) == source_owner
        and group.geometry().sopNode() == source_geometry.sopNode()
    ]

    # Construct a ctypes string array to pass the strings.
    names_arr = utils.build_c_string_array(group_names)

    _cpp_methods.batchCopyAttributeValues(
        num_target,
        target_geometry,
        target_owner,
        utils.build_c_int_array(target_indices),
        source_geometry,
        source_owner,
        utils.build_c_int_array(source_indices),
        names_arr,
        len(names_arr),
        True,
    )


def batch_copy_group_membership(
    source_elements: GeometryEntityList,
    source_groups: ElementGroupList,
    target_elements: GeometryEntityList,
):
    """Copy group membership from the source element to the target element.

    :param source_elements: The elements to copy from.
    :param source_groups: The groups to copy membership of.
    :param target_elements: The elements to copy to.
    :return:

    """
    num_elements = len(target_elements)

    if num_elements != len(source_elements):
        raise ValueError("Number of source and target elements must match")

    target_type, target_geometry, target_entity_nums = utils.get_entity_data_from_list(
        target_elements
    )

    # Make sure the target geometry is not read only.
    if target_geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    source_type, source_geometry, source_entity_nums = utils.get_entity_data_from_list(
        source_elements
    )

    # Get the attribute owners from the elements.
    target_owner = utils.get_attrib_owner_from_geometry_entity_type(target_type)
    source_owner = utils.get_attrib_owner_from_geometry_entity_type(source_type)

    # Get the group names, ensuring we only use group on the
    # source's geometry.
    group_names = [
        group.name()
        for group in source_groups
        if utils.get_group_attrib_owner(group) == source_owner
        and group.geometry().sopNode() == source_geometry.sopNode()
    ]

    # Construct a ctypes string array to pass the strings.
    arr = utils.build_c_string_array(group_names)

    _cpp_methods.batchCopyAttributeValues(
        num_elements,
        target_geometry,
        target_owner,
        utils.build_c_int_array(target_entity_nums),
        source_geometry,
        source_owner,
        utils.build_c_int_array(source_entity_nums),
        arr,
        len(group_names),
        True,
    )


def copy_packed_prims_to_points(  # pylint: disable=too-many-arguments
    geometry: hou.Geometry,
    source_geometry: hou.Geometry,
    prim_list: List[int],
    point_list: List[int],
    copy_attribs: bool = True,
    attribs: Optional[List[hou.Attrib]] = None,
    copy_groups: bool = True,
    groups: Optional[Union[hou.PointGroup, hou.PrimGroup]] = None,
):
    """Copy packed primitives to points by index, optionally copying attributes.

    :param geometry: The geometry to copy the primitives into.
    :param source_geometry: The source geometry containing the primitives.
    :param prim_list: The list of primitive numbers to copy.
    :param point_list: The list of point numbers to copy onto.
    :param copy_attribs: Whether or not to copy primitive attributes and their values.
    :param attribs: Optional list of attributes to copy. If None and copy_attribs is True, copies all primitive
    attributes.
    :param copy_groups: Whether or not to copy primitive groups and their values.
    :param groups: Optional list of groups to copy. If None and copy_groups is True, copies all primitive groups.
    :return:

    """
    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    if len(prim_list) != len(point_list):
        raise ValueError("Point count does not match number of target prims")

    prim_array = utils.build_c_int_array(prim_list)
    point_array = utils.build_c_int_array(point_list)

    _cpp_methods.mergePackedPrims(
        geometry, source_geometry, prim_array, point_array, len(prim_array)
    )

    if copy_attribs:
        if attribs is None:
            attribs = source_geometry.primAttribs()

        batch_copy_attributes_by_indices(
            source_geometry,
            hou.Prim,
            prim_list,
            attribs,
            geometry,
            hou.Prim,
            list(range(len(geometry.iterPrims()))),
        )

    if copy_groups:
        if groups is None:
            groups = source_geometry.primGroups()

        batch_copy_group_membership_by_indices(
            source_geometry,
            hou.Prim,
            prim_list,
            groups,
            geometry,
            hou.Prim,
            list(range(len(geometry.iterPrims()))),
        )


def point_adjacent_polygons(prim: hou.Prim) -> Tuple[hou.Prim, ...]:
    """Get all prims that are adjacent to the prim through a point.

    :param prim: The source primitive.
    :return: Adjacent primitives.

    """
    # Get the geometry the primitive belongs to.
    geometry = prim.geometry()

    # Get a list of prim numbers that are point adjacent the prim.
    result = _cpp_methods.pointAdjacentPolygons(geometry, prim.number())

    return utils.get_prims_from_list(geometry, result)


def edge_adjacent_polygons(prim: hou.Prim) -> Tuple[hou.Prim, ...]:
    """Get all prims that are adjacent to the prim through an edge.

    :param prim: The source primitive.
    :return: Adjacent primitives.

    """
    # Get the geometry the primitive belongs to.
    geometry = prim.geometry()

    # Get a list of prim numbers that are edge adjacent the prim.
    result = _cpp_methods.edgeAdjacentPolygons(geometry, prim.number())

    return utils.get_prims_from_list(geometry, result)


def connected_points(point: hou.Point) -> Tuple[hou.Point, ...]:
    """Get all points that share an edge with the point.

    :param point: The source point.
    :return: Connected points

    """
    # Get the geometry the point belongs to.
    geometry = point.geometry()

    # Get a list of point numbers that are connected to the point.
    result = _cpp_methods.connectedPoints(geometry, point.number())

    # Glob for the points and return them.
    return utils.get_points_from_list(geometry, result)


def prims_connected_to_point(point: hou.Point) -> Tuple[hou.Prim, ...]:
    """Get all primitives that reference the point.

    :param point: The source point.
    :return: Connected primitives.

    """
    # Get the geometry the point belongs to.
    geometry = point.geometry()

    # Get a list of primitive numbers that reference the point.
    result = _cpp_methods.connectedPrims(geometry, point.number())

    return utils.get_prims_from_list(geometry, result)


def referencing_vertices(point: hou.Point) -> Tuple[hou.Vertex, ...]:
    """Get all the vertices referencing the point.

    :param point: The source point.
    :return: Referencing vertices

    """
    # Get the geometry the point belongs to.
    geometry = point.geometry()

    # Get an object containing primitive and vertex index information.
    result = _cpp_methods.referencingVertices(geometry, point.number())

    # Construct a list of vertex strings.  Each element has the format:
    # {prim_num}v{vertex_index}.
    vertex_strings = [
        f"{prim}v{idx}" for prim, idx in zip(result.prims, result.indices)
    ]

    # Glob for the vertices and return them.
    return geometry.globVertices(" ".join(vertex_strings))


def string_table_indices(attrib: hou.Attrib) -> Tuple[int, ...]:
    """Return at tuple of string attribute table indices.

    String attributes are stored using integers referencing a table of
    strings.  This function will return a list of table indices for each
    element.

    :param attrib: The source attribute.
    :return: String table indices

    """
    if attrib.dataType() != hou.attribData.String:
        raise ValueError("Attribute must be a string.")

    # Get the corresponding attribute type id.
    attrib_owner = utils.get_attrib_owner(attrib.type())

    return tuple(
        _cpp_methods.getStringTableIndices(
            attrib.geometry(), attrib_owner, utils.string_encode(attrib.name())
        )
    )


def vertex_string_attrib_values(geometry: hou.Geometry, name: str) -> StringTuple:
    """Return a tuple of strings containing one attribute's values for all the
    vertices.

    :param geometry: The source geometry.
    :param name: The attribute name.
    :return: A list containing all vertex attribute values.

    """
    attrib = geometry.findVertexAttrib(name)

    if attrib is None:
        raise hou.OperationFailed("Invalid attribute name.")

    if attrib.dataType() != hou.attribData.String:
        raise ValueError("Attribute must be a string.")

    results = _cpp_methods.vertexStringAttribValues(geometry, utils.string_encode(name))

    return utils.clean_string_values(results)


def set_vertex_string_attrib_values(
    geometry: hou.Geometry, name: str, values: StringTuple
):
    """Set the string attribute values for all vertices.

    :param geometry: The geometry.
    :param name: The attribute name.
    :param values: The values to set.
    :return:

    """
    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    attrib = geometry.findVertexAttrib(name)

    if attrib is None:
        raise hou.OperationFailed("Invalid attribute name.")

    if attrib.dataType() != hou.attribData.String:
        raise ValueError("Attribute must be a string.")

    if len(values) != num_vertices(geometry):
        raise ValueError("Incorrect attribute value sequence size.")

    # Construct a ctypes string array to pass the strings.
    c_values = utils.build_c_string_array(values)

    _cpp_methods.setVertexStringAttribValues(
        geometry, utils.string_encode(name), c_values, len(c_values)
    )


def set_shared_point_string_attrib(
    geometry: hou.Geometry,
    name: str,
    value: str,
    group: Optional[hou.PointGroup] = None,
):
    """Set a string attribute value for points.

    If group is None, all points will have receive the value.  If a group is
    passed, only the points in the group will be set.

    :param geometry: The geometry.
    :param name: The attribute name.
    :param value: The value to set.
    :param group: An optional point group.
    :return:

    """
    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    attribute = geometry.findPointAttrib(name)

    if attribute is None:
        raise ValueError("Invalid attribute name.")

    if attribute.dataType() != hou.attribData.String:
        raise ValueError("Attribute must be a string.")

    group_name: Union[bytes, int]  # Can be a valid name or 0 to indicate no name.

    # If the group is valid use that group's name.
    if group:
        group_name = utils.string_encode(group.name())

    # If not pass 0 so the char * will be empty.
    else:
        group_name = 0

    _cpp_methods.setSharedStringAttrib(
        geometry,
        utils.get_attrib_owner(attribute.type()),
        utils.string_encode(name),
        utils.string_encode(value),
        group_name,
    )


def set_shared_prim_string_attrib(
    geometry: hou.Geometry, name: str, value: str, group: Optional[hou.PrimGroup] = None
):
    """Set a string attribute value for primitives.

    If group is None, all primitives will have receive the value.  If a group
    is passed, only the primitives in the group will be set.

    :param geometry: The geometry.
    :param name: The attribute name.
    :param value: The value to set.
    :param group: An optional primitive group.
    :return:

    """
    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    attribute = geometry.findPrimAttrib(name)

    if attribute is None:
        raise ValueError("Invalid attribute name.")

    if attribute.dataType() != hou.attribData.String:
        raise ValueError("Attribute must be a string.")

    group_name: Union[bytes, int]  # Can be a valid name or 0 to indicate no name.

    # If the group is valid use that group's name.
    if group:
        group_name = utils.string_encode(group.name())

    # If not pass 0 so the char * will be empty.
    else:
        group_name = 0

    _cpp_methods.setSharedStringAttrib(
        geometry,
        utils.get_attrib_owner(attribute.type()),
        utils.string_encode(name),
        utils.string_encode(value),
        group_name,
    )


def attribute_has_uninitialized_string_values(attribute: hou.Attrib) -> bool:
    """Check if an attribute has uninitialized string indices.

    Uninitialized strings will appear as empty strings when viewed
    don't actually correspond to "" when checked in a conditional
    statement.  CONFUSING!

    :param attribute: The attribute to check.
    :return: Whether or not the attribute has uninitialized string values.

    """
    if attribute.dataType() != hou.attribData.String:
        raise ValueError("Not a string attribute.")

    geometry = attribute.geometry()

    # Get the corresponding attribute type id.
    type_id = utils.get_attrib_owner(attribute.type())

    return _cpp_methods.hasUninitializedStringValues(
        geometry, type_id, attribute.name()
    )


def face_has_edge(face: hou.Face, point1: hou.Point, point2: hou.Point) -> bool:
    """Test if the face has an edge between two points.

    :param face: The face to check for an edge.
    :param point1: A point to test for an edge with.
    :param point2: A point to test for an edge with.
    :return: Whether or not the points share an edge.

    """
    # Test for the edge.
    return _cpp_methods.faceHasEdge(
        face.geometry(), face.number(), point1.number(), point2.number()
    )


def shared_edges(face1: hou.Face, face2: hou.Face) -> Tuple[hou.Edge, ...]:
    """Get a tuple of any shared edges between two primitives.

    :param face1: The face to check for shared edges.
    :param face2: The other face to check for shared edges.
    :return: A tuple of shared edges.

    """
    geometry = face1.geometry()

    # A list of unique edges.
    edges = set()

    # Iterate over each vertex of the primitive.
    for vertex in face1.vertices():
        # Get the point for the vertex.
        vertex_point = vertex.point()

        # Iterate over all the connected points.
        for connected in connected_points(vertex_point):
            # Sort the points.
            pt1, pt2 = sorted((vertex_point, connected), key=lambda pt: pt.number())

            # Ensure the edge exists for both primitives.
            if face_has_edge(face1, pt1, pt2) and face_has_edge(face2, pt1, pt2):
                # Find the edge and add it to the list.
                edges.add(geometry.findEdge(pt1, pt2))

    return tuple(edges)


def insert_vertex(face: hou.Face, point: hou.Point, index: int) -> hou.Vertex:
    """Insert a vertex on the point into this face at a specific index.

    :param face: The face to insert the vertex for.
    :param point: The vertex point.
    :param index: The vertex index.
    :return: The new vertex.

    """
    geometry = face.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    _assert_prim_vertex_index(face, index)

    # Insert the vertex.
    _cpp_methods.insertVertex(geometry, face.number(), point.number(), index)

    return face.vertex(index)


def delete_vertex_from_face(face: hou.Face, index: int):
    """Delete the vertex at the specified index.

    :param face: The face to delete the vertex from.
    :param index: The vertex index to delete.
    :return:

    """
    geometry = face.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    _assert_prim_vertex_index(face, index)

    # Delete the vertex.
    _cpp_methods.deleteVertexFromFace(geometry, face.number(), index)


def set_face_vertex_point(face: hou.Face, index: int, point: hou.Point):
    """Set the vertex, at the specified index, to be attached to the point.

    :param face: The face to delete the vertex from.
    :param index: The vertex index to set.
    :param point: The point to set the vertex to.
    :return:

    """
    geometry = face.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    _assert_prim_vertex_index(face, index)

    # Modify the vertex.
    _cpp_methods.setFaceVertexPoint(geometry, face.number(), index, point.number())


def primitive_bary_center(prim: hou.Prim) -> hou.Vector3:
    """Get the barycenter of the primitive.

    :param prim: The primitive to get the center of.
    :return: The barycenter.

    """
    # Get the Position3D object representing the barycenter.
    pos = _cpp_methods.primitiveBaryCenter(prim.geometry(), prim.number())

    # Construct a vector and return it.
    return hou.Vector3(pos.x, pos.y, pos.z)


def primitive_area(prim: hou.Prim) -> float:
    """Get the area of the primitive.

    This method just wraps the "measuredarea" intrinsic value.

    :param prim: The primitive to get the area of.
    :return: The primitive area.

    """
    return prim.intrinsicValue("measuredarea")


def primitive_perimeter(prim: hou.Prim) -> float:
    """Get the perimeter of the primitive.

    This method just wraps the "measuredperimeter" intrinsic value.

    :param prim: The primitive to get the perimeter of.
    :return: The primitive perimeter.

    """
    return prim.intrinsicValue("measuredperimeter")


def primitive_volume(prim: hou.Prim) -> float:
    """Get the volume of the primitive.

    This method just wraps the "measuredvolume" intrinsic value.

    :param prim: The primitive to get the volume of.
    :return: The primitive volume.

    """
    return prim.intrinsicValue("measuredvolume")


def reverse_prim(prim: hou.Prim):
    """Reverse the vertex order of the primitive.

    :param prim: The primitive to reverse.
    :return:

    """
    geometry = prim.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    _cpp_methods.reversePrimitive(geometry, prim.number())


def check_minimum_polygon_vertex_count(
    geometry: hou.Geometry, minimum_vertices: int, ignore_open: bool = True
) -> bool:
    """Check that all polygons have a minimum number of vertices.

    This will ignore non-polygon types such as packed and volume primitives.

    :param geometry: The geometry to check.
    :param minimum_vertices: The minimum number of vertices a polygon must have.
    :param ignore_open: Ignore polygons which are open.
    :return: Whether or not all the polygons have the minimum number of vertices.

    """
    return _cpp_methods.check_minimum_polygon_vertex_count(
        geometry, minimum_vertices, ignore_open
    )


def geometry_has_prims_with_shared_vertex_points(geometry: hou.Geometry) -> bool:
    """Check if the geometry contains any primitives which have more than one
    vertex referencing the same point.

    :param geometry: The geometry to check.
    :return: Whether or not the geometry has any primitives with shared vertex points.

    """
    return _cpp_methods.hasPrimsWithSharedVertexPoints(geometry)


def get_primitives_with_shared_vertex_points(geometry: hou.Geometry) -> Tuple[hou.Prim, ...]:
    """Get any primitives in the geometry which have more than one vertex
    referencing the same point.

    :param geometry: The geometry to check.
    :return: A list of any primitives which have shared vertex points.

    """
    result = _cpp_methods.getPrimsWithSharedVertexPoints(geometry)

    # Return a tuple of the matching primitives if any were found.
    if result:
        return utils.get_prims_from_list(geometry, result)

    # If none were found, return an empty tuple.
    return tuple()


def primitive_bounding_box(prim: hou.Prim) -> hou.BoundingBox:
    """Get the bounding box of the primitive.

    This method just wraps the "bounds" intrinsic value.

    :param prim: The primitive to get the bounding box of.
    :return: The primitive bounding box.

    """
    bounds = prim.intrinsicValue("bounds")

    # Intrinsic values are out of order for hou.BoundingBox so they need to
    # be shuffled.
    return hou.BoundingBox(
        bounds[0], bounds[2], bounds[4], bounds[1], bounds[3], bounds[5]
    )


def destroy_empty_groups(geometry: hou.Geometry, attrib_type: hou.attribType):
    """Remove any empty groups of the specified type.

    :param geometry: The geometry to destroy empty groups for.
    :param attrib_type: The type of groups to destroy.
    :return:

    """
    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    if attrib_type == hou.attribType.Global:
        raise ValueError("Attribute type must be point, primitive or vertex.")

    # Get the corresponding attribute type id.
    attrib_owner = utils.get_attrib_owner(attrib_type)

    _cpp_methods.destroyEmptyGroups(geometry, attrib_owner)


def rename_group(
    group: Union[hou.EdgeGroup, hou.PointGroup, hou.PrimGroup], new_name: str
) -> Optional[Union[hou.EdgeGroup, hou.PointGroup, hou.PrimGroup]]:
    """Rename a group.

    :param group: The group to rename.
    :param new_name: The new group name.
    :return: The new group, if it was renamed, otherwise None.


    """
    geometry = group.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    # Ensure the new group doesn't have the same name.
    if new_name == group.name():
        raise hou.OperationFailed("Cannot rename to same name.")

    group_type = utils.get_group_type(group)

    success = _cpp_methods.renameGroup(
        geometry,
        utils.string_encode(group.name()),
        utils.string_encode(new_name),
        group_type,
    )

    if success:
        return utils.find_group(geometry, group_type, new_name)

    return None


def group_bounding_box(
    group: Union[hou.EdgeGroup, hou.PointGroup, hou.PrimGroup]
) -> hou.BoundingBox:
    """Get the bounding box of the group.

    :param group: The group to get the bounding box for.
    :return: The bounding box for the group.

    """
    group_type = utils.get_group_type(group)

    # Calculate the bounds for the group.
    bounds = _cpp_methods.groupBoundingBox(
        group.geometry(), group_type, utils.string_encode(group.name())
    )

    return hou.BoundingBox(*bounds)


def group_size(group: Union[hou.EdgeGroup, hou.PointGroup, hou.PrimGroup]) -> int:
    """Get the number of elements in this group.

    :param group: The group to get the size of.
    :return: The group size.

    """
    group_type = utils.get_group_type(group)

    return _cpp_methods.groupSize(
        group.geometry(), utils.string_encode(group.name()), group_type
    )


def toggle_group_entries(group: Union[hou.EdgeGroup, hou.PointGroup, hou.PrimGroup]):
    """Toggle group membership for all elements in the group.

    All elements not in the group will be added to it and all that were in it
    will be removed.

    :param group: The group to toggle entries for.
    :return:

    """
    geometry = group.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    group_type = utils.get_group_type(group)

    _cpp_methods.toggleGroupEntries(
        geometry, utils.string_encode(group.name()), group_type
    )


def copy_group(
    group: Union[hou.PointGroup, hou.PrimGroup], new_group_name: str
) -> Union[hou.PointGroup, hou.PrimGroup]:
    """Create a new group under the new name with the same membership.

    :param group: The group to copy.
    :param new_group_name: The new group name.
    :return: The new group.

    """
    geometry = group.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    # Ensure the new group doesn't have the same name.
    if new_group_name == group.name():
        raise hou.OperationFailed("Cannot copy to group with same name.")

    group_type = utils.get_group_type(group)

    # Check for an existing group of the same name.
    if utils.find_group(geometry, group_type, new_group_name) is not None:
        # If one exists, raise an exception.
        raise hou.OperationFailed(f"Group '{new_group_name}' already exists.")

    attrib_owner = utils.get_group_attrib_owner(group)

    # Copy the group.
    _cpp_methods.copyGroup(
        geometry,
        attrib_owner,
        utils.string_encode(group.name()),
        utils.string_encode(new_group_name),
    )

    # Return the new group.
    return utils.find_group(geometry, group_type, new_group_name)


def groups_share_elements(
    group1: Union[hou.PointGroup, hou.PrimGroup],
    group2: Union[hou.PointGroup, hou.PrimGroup],
) -> bool:
    """Check whether or not the groups contain any of the same elements.

    The groups must be of the same type and in the same detail.

    :param group1: Group to compare..
    :param group2: Group to compare with.
    :return: Whether or not the groups share any elements.

    """
    group1_geometry = group1.geometry()
    group2_geometry = group2.geometry()

    if not utils.geo_details_match(group1_geometry, group2_geometry):
        raise ValueError("Groups are not in the same detail.")

    group1_type = utils.get_group_type(group1)
    group2_type = utils.get_group_type(group2)

    if group1_type != group2_type:
        raise TypeError("Groups are not the same types.")

    return _cpp_methods.groupsShareElements(
        group1_geometry,
        utils.string_encode(group1.name()),
        utils.string_encode(group2.name()),
        group1_type,
    )


def set_group_string_attribute(
    group: Union[hou.PointGroup, hou.PrimGroup], attribute: hou.Attrib, value: str
):
    """Set a string attribute value to all members of a group.

    :param group: The group to set the attribute for.
    :param attribute: The attribute to set.
    :param value: The value to set.
    :return:

    """
    geometry = group.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    if attribute.dataType() != hou.attribData.String:
        raise ValueError("Attribute must be a string.")

    group_type = utils.get_group_type(group)

    _cpp_methods.setGroupStringAttribute(
        geometry, group_type, group.name(), attribute.name(), value
    )


def convert_prim_to_point_group(
    prim_group: hou.PrimGroup,
    new_group_name: Optional[str] = None,
    destroy: bool = True,
) -> hou.PointGroup:
    """Create a new hou.Point group from the primitive group.

    The group will contain all the points referenced by all the vertices of the
    primitives in the group.

    :param prim_group: Group to convert.
    :param new_group_name: The name of the new group.
    :param destroy: Whether or not to destroy this group.
    :return: The new point group.

    """
    geometry = prim_group.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    # If a new name isn't specified, use the current group name.
    if new_group_name is None:
        new_group_name = prim_group.name()

    # If the group already exists, raise an exception.
    if geometry.findPointGroup(new_group_name) is not None:
        raise hou.OperationFailed("Group already exists.")

    # Convert the group.
    _cpp_methods.primToPointGroup(
        geometry,
        utils.string_encode(prim_group.name()),
        utils.string_encode(new_group_name),
        destroy,
    )

    # Return the new group.
    return geometry.findPointGroup(new_group_name)


def convert_point_to_prim_group(
    point_group: hou.PointGroup,
    new_group_name: Optional[str] = None,
    destroy: bool = True,
) -> hou.PrimGroup:
    """Create a new hou.Prim group from the point group.

    The group will contain all the primitives which have vertices referencing
    any of the points in the group.

    :param point_group: Group to convert.
    :param new_group_name: The name of the new group.
    :param destroy: Whether or not to destroy this group.
    :return: The new primitive group.

    """
    geometry = point_group.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    # If a new name isn't specified, use the current group name.
    if new_group_name is None:
        new_group_name = point_group.name()

    # If the group already exists, raise an exception.
    if geometry.findPrimGroup(new_group_name) is not None:
        raise hou.OperationFailed("Group already exists.")

    # Convert the group.
    _cpp_methods.pointToPrimGroup(
        geometry,
        utils.string_encode(point_group.name()),
        utils.string_encode(new_group_name),
        destroy,
    )

    # Return the new group.
    return geometry.findPrimGroup(new_group_name)


def geometry_has_ungrouped_points(geometry: hou.Geometry) -> bool:
    """Check if the geometry has ungrouped points.

    :param geometry: The geometry to check.
    :return: Whether or not the geometry has any ungrouped points.

    """
    return _cpp_methods.hasUngroupedPoints(geometry)


def group_ungrouped_points(geometry: hou.Geometry, group_name: str) -> hou.PointGroup:
    """Create a new point group of any points not already in a group.

    :param geometry: The geometry to group unused points.
    :param group_name: The new group name.
    :return: A new point group containing ungrouped points.

    """
    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    if not group_name:
        raise ValueError(f"Invalid group name: {group_name}")

    if geometry.findPointGroup(group_name) is not None:
        raise hou.OperationFailed(f"Group '{group_name}' already exists")

    _cpp_methods.groupUngroupedPoints(geometry, utils.string_encode(group_name))

    return geometry.findPointGroup(group_name)


def geometry_has_ungrouped_prims(geometry: hou.Geometry) -> bool:
    """Check if the geometry has ungrouped primitives.

    :param geometry: The geometry to check.
    :return: Whether or not the geometry has any ungrouped primitives.

    """
    return _cpp_methods.hasUngroupedPrims(geometry)


def group_ungrouped_prims(geometry: hou.Geometry, group_name: str) -> hou.PrimGroup:
    """Create a new primitive group of any primitives not already in a group.

    :param geometry: The geometry to group unused prims.
    :param group_name: The new group name.
    :return: A new primitive group containing ungrouped primitives.

    """
    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    if not group_name:
        raise ValueError(f"Invalid group name: {group_name}")

    if geometry.findPrimGroup(group_name) is not None:
        raise hou.OperationFailed(f"Group '{group_name}' already exists")

    _cpp_methods.groupUngroupedPrims(geometry, utils.string_encode(group_name))

    return geometry.findPrimGroup(group_name)


def bounding_box_is_inside(
    source_bbox: hou.BoundingBox, target_bbox: hou.BoundingBox
) -> bool:
    """Determine if this bounding box is totally enclosed by another box.

    :param source_bbox: The bounding box to check for being enclosed.
    :param target_bbox: The bounding box to check for enclosure.
    :return: Whether or not this object is totally enclosed by the other box.

    """
    return _cpp_methods.boundingBoxIsInside(source_bbox, target_bbox)


def bounding_boxes_intersect(bbox1: hou.BoundingBox, bbox2: hou.BoundingBox) -> bool:
    """Determine if the bounding boxes intersect.

    :param bbox1: A bounding box to check for intersection with.
    :param bbox2: A bounding box to check for intersection with.
    :return: Whether or not this object intersects the other box.

    """
    return _cpp_methods.boundingBoxesIntersect(bbox1, bbox2)


def compute_bounding_box_intersection(
    bbox1: hou.BoundingBox, bbox2: hou.BoundingBox
) -> bool:
    """Compute the intersection of two bounding boxes.

    This function changes the bounds of the first box to be those of the
    intersection of the box and the second box.

    :param bbox1: A box to compute intersection with.
    :param bbox2: A box to compute intersection with.
    :return: Whether the boxes intersect or not.

    """
    return _cpp_methods.computeBoundingBoxIntersection(bbox1, bbox2)


def expand_bounding_box(
    bbox: hou.BoundingBox, delta_x: float, delta_y: float, delta_z: float
):
    """Expand the min and max bounds in each direction by the axis delta.

    :param bbox: The bounding box to expand.
    :param delta_x: The X value to expand by.
    :param delta_y: The Y value to expand by.
    :param delta_z: The Z value to expand by.
    :return:

    """
    _cpp_methods.expandBoundingBoxBounds(bbox, delta_x, delta_y, delta_z)


def add_to_bounding_box_min(bbox: hou.BoundingBox, vec: hou.Vector3):
    """Add values to the minimum bounds of this bounding box.

    :param bbox: The bounding box to expand.
    :param vec: The values to add.
    :return:

    """
    _cpp_methods.addToBoundingBoxMin(bbox, vec)


def add_to_bounding_box_max(bbox: hou.BoundingBox, vec: hou.Vector3):
    """Add values to the maximum bounds of this bounding box.

    :param bbox: The bounding box to expand.
    :param vec: The values to add.
    :return:

    """
    _cpp_methods.addToBoundingBoxMax(bbox, vec)


def bounding_box_area(bbox: hou.BoundingBox) -> float:
    """Calculate the area of this bounding box.

    :param bbox: The bounding box to get the area of..
    :return: The area of the box.

    """
    return _cpp_methods.boundingBoxArea(bbox)


def bounding_box_volume(bbox: hou.BoundingBox) -> float:
    """Calculate the volume of this bounding box.

    :param bbox: The bounding box to get the volume of..
    :return: The volume of the box.

    """
    return _cpp_methods.boundingBoxVolume(bbox)


def is_parm_tuple_vector(parm_tuple: hou.ParmTuple) -> bool:
    """Check if the tuple is a vector parameter.

    :param parm_tuple: The parm tuple to check.
    :return: Whether or not the parameter tuple is a vector.

    """
    parm_template = parm_tuple.parmTemplate()

    return parm_template.namingScheme() == hou.parmNamingScheme.XYZW


def eval_parm_tuple_as_vector(
    parm_tuple: hou.ParmTuple,
) -> Union[hou.Vector2, hou.Vector3, hou.Vector4]:
    """Return the parameter value as a hou.Vector of the appropriate size.

    :param parm_tuple: The parm tuple to eval.
    :return: The evaluated parameter as a hou.Vector*

    """
    if not is_parm_tuple_vector(parm_tuple):
        raise ValueError("Parameter is not a vector")

    value = parm_tuple.eval()
    size = len(value)

    if size == 2:
        return hou.Vector2(value)

    if size == 3:
        return hou.Vector3(value)

    return hou.Vector4(value)


def is_parm_tuple_color(parm_tuple: hou.ParmTuple) -> bool:
    """Check if the parameter is a color parameter.

    :param parm_tuple: The parm tuple to check.
    :return: Whether or not the parameter tuple is a color.

    """
    parm_template = parm_tuple.parmTemplate()

    return parm_template.look() == hou.parmLook.ColorSquare


def eval_parm_tuple_as_color(parm_tuple: hou.ParmTuple) -> hou.Color:
    """Evaluate a color parameter and return a hou.Color object.

    :param parm_tuple: The parm tuple to eval.
    :return: The evaluated parameter as a hou.Vector*

    """
    if not is_parm_tuple_color(parm_tuple):
        raise ValueError("Parameter is not a color chooser")

    return hou.Color(parm_tuple.eval())


def eval_parm_as_strip(parm: hou.Parm) -> Tuple[bool, ...]:
    """Evaluate the parameter as a Button/Icon Strip.

    Returns a tuple of True/False values indicated which buttons
    are pressed.

    :param parm: The parm to eval.
    :return: True/False values for the strip.

    """
    parm_template = parm.parmTemplate()

    # Right now the best we can do is check that a parameter is a menu
    # since HOM has no idea about what the strips are.  If we aren't one
    # then raise an exception.
    if not isinstance(parm_template, hou.MenuParmTemplate):
        raise TypeError("Parameter must be a menu")

    # Get the value.  This might be the selected index, or a bit mask if we
    # can select more than one.
    value = parm.eval()

    # Initialize a list of False values for each item on the strip.
    num_items = len(parm_template.menuItems())
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


def eval_parm_strip_as_string(parm: hou.Parm) -> StringTuple:
    """Evaluate the parameter as a Button Strip as strings.

    Returns a tuple of the string tokens which are enabled.

    :param parm: The parm to eval.
    :return: String token values.

    """
    strip_results = eval_parm_as_strip(parm)

    menu_items = parm.parmTemplate().menuItems()

    enabled_values = []

    for i, value in enumerate(strip_results):
        if value:
            enabled_values.append(menu_items[i])

    return tuple(str(val) for val in enabled_values)


def is_parm_multiparm(parm: Union[hou.Parm, hou.ParmTuple]) -> bool:
    """Check if this parameter is a multiparm.

    :param parm: The parm or tuple to check for being a multiparm.
    :return: Whether or not the parameter is a multiparm.

    """
    # Get the parameter template for the parm/tuple.
    parm_template = parm.parmTemplate()

    return utils.is_parm_template_multiparm_folder(parm_template)


def get_multiparm_instance_indices(
    parm: Union[hou.Parm, hou.ParmTuple], instance_index: bool = False
) -> Tuple[int, ...]:
    """Get the multiparm instance indices for this parameter tuple.

    If this parameter tuple is part of a multiparm, then its index in the
    multiparm array will be returned as a tuple.  If the multiparm is nested
    in other multiparms, then the resulting tuple will have multiple entries
    (with the outer multiparm listed first, and the inner-most multiparm last
    in the tuple.

    :param parm: The parm to get the multiparm instance index for.
    :param instance_index: Each multi-parm can have multiple parameters in each instance. If instance_index is true,
    the instance number will be returned. Otherwise the raw offset into the multi-parm will be extracted.
    :return The instance indices for the parameter.

    """
    if not parm.isMultiParmInstance():
        raise ValueError("Parameter is not in a multiparm.")

    if isinstance(parm, hou.Parm):
        parm = parm.tuple()

    results = _cpp_methods.getMultiParmInstanceIndex(
        parm.node(), utils.string_encode(parm.name())
    )

    if instance_index:
        offsets = utils.get_multiparm_container_offsets(
            get_multiparm_template_name(parm), parm.node().parmTemplateGroup()  # type: ignore
        )

        results = [result - offset for result, offset in zip(results, offsets)]

    return tuple(results)


def get_multiparm_siblings(parm: Union[hou.Parm, hou.ParmTuple]) -> dict:
    """Get a tuple of any sibling parameters in the multiparm block.

    :param parm: The parameter to get any siblings for.
    :return: Any sibling parameters.

    """
    if not parm.isMultiParmInstance():
        raise ValueError("Parameter is not a multiparm instance")

    if isinstance(parm, hou.Parm):
        parm = parm.tuple()

    # Get the template name for the parameter.
    template_name = get_multiparm_template_name(parm)

    node = parm.node()

    ptg = node.parmTemplateGroup()

    # Find the most immediate containing multiparm folder.
    containing_template = utils.get_multiparm_containing_folders(template_name, ptg)[0]  # type: ignore

    # Get a list of template names in that folder.
    names = _get_names_in_folder(containing_template)

    # The instance indices of the parameter.
    indices = get_multiparm_instance_indices(parm, True)

    parms = {}

    for name in names:
        # Skip the parameter that was passed in.
        if name == template_name:
            continue

        # Resolve the tokens and get the parm tuple.
        parm_name = resolve_multiparm_tokens(name, indices)
        parm_tuple = node.parmTuple(parm_name)

        # If the parm tuple has a size of 1 then just get the parm.
        if len(parm_tuple) == 1:
            parm_tuple = parm_tuple[0]

        parms[name] = parm_tuple

    return parms


def resolve_multiparm_tokens(
    name: str, indices: Union[int, List[int], Tuple[int, ...]]
) -> str:
    """Resolve a multiparm token string with the supplied indices.

    :param name: The parameter name.
    :param indices: One or mode multiparm indices.
    :return: The resolved string.

    """
    # Support passing in just a single value.
    if not isinstance(indices, (list, tuple)):
        indices = [indices]

    utils.validate_multiparm_resolve_values(name, indices)

    c_indices = utils.build_c_int_array(indices)

    return utils.string_decode(
        _cpp_methods.resolve_multiparm_tokens(
            utils.string_encode(name), c_indices, len(c_indices)
        )
    )


def get_multiparm_template_name(parm: Union[hou.Parm, hou.ParmTuple]) -> Optional[str]:
    """Return a multiparm instance's parameter template name.

    :param parm: The parm to get the multiparm instances values for.
    :return: The parameter template name, or None

    """
    # Return None if the parameter isn't a multiparm instance.
    if not parm.isMultiParmInstance():
        return None

    if isinstance(parm, hou.Parm):
        parm = parm.tuple()

    return utils.string_decode(_cpp_methods.get_multiparm_template_name(parm))


def eval_multiparm_instance(
    node: hou.Node,
    name: str,
    indices: Union[List[int], Tuple[int], int],
    raw_indices: bool = False,
) -> Union[Tuple, float, int, str, hou.Ramp]:
    """Evaluate a multiparm parameter by indices.

    The name should include the # value(s) which will be replaced by the indices.

    The index should be the multiparm index, not including any start offset.

    This function raises an IndexError if the indices do not resolve to a valid
    parameter name on the node.

    You cannot try to evaluate a single component of a tuple parameter, evaluate
    the entire tuple instead and get which values you need.

    # Float
    >>> eval_multiparm_instance(node, "float#", 1)
    0.53
    # Float 3
    >>> eval_multiparm_instance(node, "vec#", 1)
    (0.53, 1.0, 2.5)

    :param node: The node to evaluate the parameter on.
    :param name: The base parameter name.
    :param indices: The multiparm indices.
    :param raw_indices: Whether or not the indices are 'raw' and should not try and take the folder offset into account.
    :return: The evaluated parameter value.

    """
    if "#" not in name:
        raise ValueError("Parameter name must contain at least one #")

    ptg = node.parmTemplateGroup()

    parm_template = ptg.find(name)

    if parm_template is None:
        raise ValueError(f"Name {name} does not map to a parameter on {node.path}")

    # Handle directly passing a single index.
    if not isinstance(indices, (list, tuple)):
        indices = [indices]

    if not raw_indices:
        offsets = utils.get_multiparm_container_offsets(name, ptg)

        # Adjust any supplied offsets with the multiparm offset.
        indices = [idx + offset for idx, offset in zip(indices, offsets)]

    # Validate that enough indices were passed.
    utils.validate_multiparm_resolve_values(name, indices)

    # Resolve the name and indices to get the parameter name.
    full_name = resolve_multiparm_tokens(name, indices)

    parm_tuple = node.parmTuple(full_name)

    if parm_tuple is None:
        raise IndexError(f"Invalid indices: {full_name} does not exist")

    values = parm_tuple.eval()

    # Return single value for non-tuple parms.
    if len(values) == 1:
        return values[0]

    return tuple(values)


def unexpanded_string_multiparm_instance(
    node: hou.Node, name: str, indices: Union[List[int], int], raw_indices: bool = False
) -> Union[StringTuple, str]:
    """Get the unexpanded string of a multiparm parameter by index.

    The name should include the # value which will be replaced by the index.

    The index should be the multiparm index, not including any start offset.

    This function raises an IndexError if the index exceeds the number of active
    multiparm instances.

    You cannot try to evaluate a single component of a tuple parameter, evaluate
    the entire tuple instead and get which values you need.

    # String
    >>> eval_multiparm_instance(node, "string#", 1)
    '$HIP'
    # String 2
    >>> eval_multiparm_instance(node, "stringvec#", 1)
    ('$HIP', '$PI')

    :param node: The node to evaluate the parameter on.
    :param name: The base parameter name.
    :param indices: The multiparm indices.
    :param raw_indices: Whether or not the indices are 'raw'and should not try and take the folder offset into account.
    :return: The evaluated parameter value.

    """
    if "#" not in name:
        raise ValueError("Parameter name must contain at least one #")

    ptg = node.parmTemplateGroup()

    parm_template = ptg.find(name)

    if parm_template is None:
        raise ValueError(f"Name {name} does not map to a parameter on {node.path()}")

    if parm_template.dataType() != hou.parmData.String:
        raise TypeError("Parameter must be a string parameter")

    # Handle directly passing a single index.
    if not isinstance(indices, (list, tuple)):
        indices = [indices]

    if not raw_indices:
        offsets = utils.get_multiparm_container_offsets(name, ptg)

        # Adjust any supplied offsets with the multiparm offset.
        indices = [idx + offset for idx, offset in zip(indices, offsets)]

    # Validate that enough indices were passed.
    utils.validate_multiparm_resolve_values(name, indices)

    full_name = resolve_multiparm_tokens(name, indices)

    parm_tuple = node.parmTuple(full_name)

    if parm_tuple is None:
        raise IndexError(f"Invalid indices: {full_name} does not exist")

    values = tuple(str(parm.unexpandedString()) for parm in parm_tuple)

    # Return single value for non-tuple parms.
    if len(values) == 1:
        return values[0]

    return values


def disconnect_all_inputs(node: hou.Node):
    """Disconnect all of this node's inputs.

    :param node: The node to disconnect all inputs for.
    :return:

    """
    connections = node.inputConnections()

    with hou.undos.group("Disconnect inputs"):
        for connection in reversed(connections):
            node.setInput(connection.inputIndex(), None)


def disconnect_all_outputs(node: hou.Node):
    """Disconnect all of this node's outputs.

    :param node: The node to disconnect all outputs for.
    :return:

    """
    connections = node.outputConnections()

    with hou.undos.group("Disconnect outputs"):
        for connection in connections:
            connection.outputNode().setInput(connection.inputIndex(), None)


def get_node_message_nodes(node: hou.Node) -> Tuple[hou.Node, ...]:
    """Get a list of the node's message nodes.

    :param node: The node to get the message nodes for.
    :return: A tuple of message nodes.

    """
    # Get the otl definition for this node's type, if any.
    definition = node.type().definition()

    if definition is not None:
        # Check that there are message nodes.
        if "MessageNodes" in definition.sections():
            # Extract the list of them.
            contents = definition.sections()["MessageNodes"].contents()

            # Glob for any specified nodes and return them.
            return node.glob(contents)

    return tuple()


def get_node_editable_nodes(node: hou.Node) -> Tuple[hou.Node, ...]:
    """Get a list of the node's editable nodes.

    :param node: The node to get the editable nodes for.
    :return: A tuple of editable nodes.

    """
    # Get the otl definition for this node's type, if any.
    definition = node.type().definition()

    if definition is not None:
        # Check that there are editable nodes.
        if "EditableNodes" in definition.sections():
            # Extract the list of them.
            contents = definition.sections()["EditableNodes"].contents()

            # Glob for any specified nodes and return them.
            return node.glob(contents)

    return tuple()


def get_node_dive_target(node: hou.Node) -> Optional[hou.Node]:
    """Get this node's dive target node.

    :param node: The node to get the dive target of.
    :return: The node's dive target.

    """
    # Get the otl definition for this node's type, if any.
    definition = node.type().definition()

    if definition is not None:
        # Check that there is a dive target.
        if "DiveTarget" in definition.sections():
            # Get it's path.
            target = definition.sections()["DiveTarget"].contents()

            # Return the node.
            return node.node(target)

    return None


def get_node_representative_node(node: hou.Node) -> Optional[hou.Node]:
    """Get the representative node of this node, if any.

    :param node: The node to get the representative node for.
    :return: The node's representative node.

    """
    # Get the otl definition for this node's type, if any.
    definition = node.type().definition()

    if definition is not None:
        # Get the path to the representative node, if any.
        path = definition.representativeNodePath()

        if path:
            # Return the node.
            return node.node(path)

    return None


def node_is_contained_by(node: hou.Node, containing_node: hou.Node) -> bool:
    """Test if a node is a contained within another node.

    :param node: The node to check for being contained.
    :param containing_node: A node which may contain this node
    :return: Whether or not this node is a child of the passed node.

    """
    # Get this node's parent.
    parent = node.parent()

    # Keep looking until we have no more parents.
    while parent is not None:
        # If the parent is the target node, return True.
        if parent == containing_node:
            return True

        # Get the parent's parent and try again.
        parent = parent.parent()

    # Didn't find the node, so return False.
    return False


def node_author_name(node: hou.Node) -> str:
    """Get the name of the node creator.

    :param node: The node to get the author of.
    :return: The author name.

    """
    author = utils.string_decode(_cpp_methods.getNodeAuthor(node))

    # Remove any machine name from the user name.
    return author.split("@")[0]


def is_node_type_python(node_type: hou.NodeType) -> bool:
    """Check if the node type represents a Python operator.

    :param node_type: The node type to check.
    :return: Whether or not the operator is a Python operator.

    """
    return _cpp_methods.isNodeTypePythonType(node_type)


def is_node_type_subnet(node_type: hou.NodeType) -> bool:
    """Check if this node type is the primary subnet operator for the table.

    This is the operator type which is used as a default container for nodes.

    :param node_type: The node type to check.
    :return: Whether or not the operator is a Subnet operator.

    """
    return _cpp_methods.isNodeTypeSubnetType(node_type)


def vector_component_along(vector: hou.Vector3, target_vector: hou.Vector3) -> float:
    """Calculate the component of this vector along the target vector.

    :param vector: The vector whose component along we want to get.
    :param target_vector: The vector to calculate against.
    :return: The component of this vector along the other vector.

    """
    # The component of vector A along B is: A dot (unit vector // to B).
    return vector.dot(target_vector.normalized())


def vector_project_along(
    vector: hou.Vector3, target_vector: hou.Vector3
) -> hou.Vector3:
    """Calculate the vector projection of this vector onto another vector.

    This is an orthogonal projection of this vector onto a straight line
    parallel to the supplied vector.

    :param vector: The vector to project.
    :param target_vector: The vector to project onto.
    :return: The vector projected along the other vector.

    """
    # The vector cannot be the zero vector.
    if target_vector == hou.Vector3():
        raise ValueError("Supplied vector must be non-zero.")

    return target_vector.normalized() * vector_component_along(vector, target_vector)


def vector_contains_nans(vector: Union[hou.Vector2, hou.Vector3, hou.Vector4]) -> bool:
    """Check if the vector contains NaNs.

    :param vector: The vector to check for NaNs.
    :return: Whether or not there are any NaNs in the vector.

    """
    # Iterate over each component.
    for component in vector:
        # If this component is a NaN, return True.
        if math.isnan(component):
            return True

    # Didn't find any NaNs, so return False.
    return False


def vector_compute_dual(vector: hou.Vector3) -> hou.Matrix3:
    """Compute the dual of the vector.

    The dual is a matrix which acts like the cross product when multiplied by
    other vectors.

    :param vector: The vector to compute the dual for
    :return: The dual of the vector.

    """
    # The matrix that will be the dual.
    mat = hou.Matrix3()

    # Compute the dual.
    _cpp_methods.vector3GetDual(vector, mat)

    return mat


def matrix_is_identity(matrix: Union[hou.Matrix3, hou.Matrix4]) -> bool:
    """Check if the matrix is the identity matrix.

    :param matrix: The matrix to check.
    :return: Whether or not the matrix is the identity matrix.

    """
    # We are a 3x3 matrix.
    if isinstance(matrix, hou.Matrix3):
        # Construct a new 3x3 matrix.
        mat = hou.Matrix3()

        # Set it to be the identity.
        mat.setToIdentity()

        # Compare the two.
        return matrix == mat

    # Compare against the identity transform from hmath.
    return matrix == hou.hmath.identityTransform()


def matrix_set_translates(matrix: hou.Matrix4, translates: Tuple[float, float, float]):
    """Set the translation values of this matrix.

    :param matrix: The matrix to set the translate for..
    :param translates: The translation values to set.
    :return:

    """
    # The translations are stored in the first 3 columns of the last row of the
    # matrix.  To set the values we just need to set the corresponding columns
    # to the matching components in the vector.
    for i in range(3):
        matrix.setAt(3, i, translates[i])


def build_lookat_matrix(
    from_vec: hou.Vector3, to_vec: hou.Vector3, up_vector: hou.Vector3
) -> hou.Matrix3:
    """Compute a lookat matrix.

    This function will compute a rotation matrix which will provide the rotates
    needed for "from_vec" to look at "to_vec".

    The lookat matrix will have the -Z axis point at the "to_vec" point.  The Y
    axis will be pointing "up".

    :param from_vec: The base vector.
    :param to_vec: The target vector.
    :param up_vector: The up vector.
    :return: The lookat matrix.

    """
    # Create the new matrix to return.
    mat = hou.Matrix3()

    # Calculate the lookat and stick it in the matrix.
    _cpp_methods.buildLookatMatrix(mat, from_vec, to_vec, up_vector)

    return mat


def get_oriented_point_transform(point: hou.Point) -> hou.Matrix4:
    """Get a transform matrix from a point.

    This matrix may be the result of standard point instance attributes or if the
    point has any non-raw geometry primitives bound to it (PackedPrim, Quadric, VDB, Volume)
    then the transform from the first primitive will be returned.

    :param point: The point.
    :return: A matrix representing the point transform.

    """
    # Check for connected primitives.
    prims = prims_connected_to_point(point)

    if prims:
        # Get the first one.  This is probably the only one unless you're doing
        # something strange.
        prim = prims[0]

        # If the primitive is a Face of Surface we can't do anything.
        if isinstance(prim, (hou.Face, hou.Surface)):
            raise hou.OperationFailed(f"Point {point.number()} is bound to raw geometry")

        # Get the primitive's rotation matrix.
        rot_matrix = prim.transform()

        # Create a full transform matrix using the point position as well.
        return hou.Matrix4(rot_matrix) * hou.hmath.buildTranslate(point.position())

    # Just a simple unattached point so we can return the standard point instance
    # matrix.
    return point_instance_transform(point)


def point_instance_transform(point: hou.Point) -> hou.Matrix4:
    """Get a point's instance transform based on existing attributes.

    :param point: The point.
    :return: A matrix representing the instance transform.

    """
    result = _cpp_methods.point_instance_transform(point.geometry(), point.number())

    return hou.Matrix4(result)


def build_instance_matrix(  # pylint: disable=too-many-arguments
    position: hou.Vector3,
    direction: hou.Vector3 = hou.Vector3(0, 0, 1),
    pscale: float = 1.0,
    scale: hou.Vector3 = hou.Vector3(1, 1, 1),
    up_vector: hou.Vector3 = hou.Vector3(0, 1, 0),
    rot: hou.Quaternion = hou.Quaternion(0, 0, 0, 1),
    trans: hou.Vector3 = hou.Vector3(0, 0, 0),
    pivot: hou.Vector3 = hou.Vector3(0, 0, 0),
    orient: Optional[hou.Quaternion] = None,
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
        if up_vector != zero_vec:
            alignment_matrix = hou.Matrix4(
                build_lookat_matrix(direction, zero_vec, up_vector)
            )

        # If the up vector is the zero vector, build a matrix from the
        # dihedral.
        else:
            alignment_matrix = zero_vec.matrixToRotateTo(direction)

    # Return the instance transform matrix.
    return pivot_matrix * scale_matrix * alignment_matrix * rot_matrix * trans_matrix


def is_node_digital_asset(node: hou.Node) -> bool:
    """Determine if this node is a digital asset.

    A node is a digital asset if its node type has a hou.HDADefinition.

    :param node: The node to check for being a digital asset.
    :return: Whether or not this node is a digital asset.

    """
    return node.type().definition() is not None


def asset_file_meta_source(file_path: str) -> Optional[str]:
    """Get the meta install location for the file.

    This function determines where the specified .otl file is installed to in
    the current session.  Examples include "Scanned OTL Directories", "Current
    Hip File", "Fallback Libraries" or specific OPlibraries files.

    :param file_path: The path to get the install location for.
    :return: The meta install location, if any.

    """
    if file_path not in hou.hda.loadedFiles():
        return None

    return utils.string_decode(
        _cpp_methods.getMetaSourceForPath(utils.string_encode(file_path))
    )


def get_definition_meta_source(definition: hou.HDADefinition) -> Optional[str]:
    """Get the meta install location of this asset definition.

    This function determines where the contained .otl file is installed to in
    the current session.  Examples include "Scanned OTL Directories", "Current
    Hip File", "Fallback Libraries" or specific OPlibraries files.

    :param definition: The definition to get the meta source for.
    :return: The meta install location, if any.

    """
    return asset_file_meta_source(definition.libraryFilePath())


def remove_meta_source(meta_source: str) -> bool:
    """Attempt to remove a meta source.

    Removing a meta source will uninstall the libraries it was responsible for.

    :param meta_source: The meta source name.
    :return: Whether or not the source was removed.

    """
    return _cpp_methods.removeMetaSource(utils.string_encode(meta_source))


def libraries_in_meta_source(meta_source: str) -> StringTuple:
    """Get a list of library paths in a meta source.

    :param meta_source: The meta source name.
    :return: A list of paths in the source.

    """
    # Get the any libraries in the meta source.
    result = _cpp_methods.getLibrariesInMetaSource(utils.string_encode(meta_source))

    # Return a tuple of the valid values.
    return utils.clean_string_values(result)


def is_dummy_definition(definition: hou.HDADefinition) -> bool:
    """Check if this definition is a dummy definition.

    A dummy, or empty definition is created by Houdini when it cannot find
    an operator definition that it needs in the current session.

    :param definition: The definition to check.
    :return: Whether or not the asset definition is a dummy definition.

    """
    return _cpp_methods.isDummyDefinition(
        utils.string_encode(definition.libraryFilePath()),
        utils.string_encode(definition.nodeTypeCategory().name()),
        utils.string_encode(definition.nodeTypeName()),
    )
