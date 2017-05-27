"""This module contains functions designed to extend the Houdini Object Model
(HOM) through the use of the inlinecpp module and regular Python.

The functions in this module are not mean to be called directly.  This module
uses Python decorators to attach the functions to the corresponding HOM classes
and modules they are meant to extend.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Imports
import hou
import inlinecpp

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

_FUNCTION_SOURCES = [
"""
bool
isRendering()
{
    ROP_RenderManager           *manager = ROP_RenderManager::getManager();

    return manager && manager->isActive();
}
""",

"""
StringArray
getGlobalVariables(int dirty=0)
{
    std::vector<std::string>    result;

    CMD_VariableTable           *table;

    OP_CommandManager           *cmd;
    OP_Director                 *director;

    UT_StringArray              names;

    // Get the scene director.
    director = OPgetDirector();

    // Get the command manager.
    cmd = director->getCommandManager();

    table = cmd->getGlobalVariables();

    table->getVariableNames(names, dirty);

    names.toStdVectorOfStrings(result);

    // Check for an empty vector.
    validateStringVector(result);

    return result;
}
""",

"""
char *
getVariable(const char *name)
{
    OP_CommandManager           *cmd;
    OP_Director                 *director;

    UT_String                   value;

    // Get the scene director.
    director = OPgetDirector();

    // Get the command manager.
    cmd = director->getCommandManager();

    cmd->getVariable(name, value);

    return strdup(value.buffer());
}
""",

"""
StringArray
getVariableNames(int dirty=0)
{
    std::vector<std::string>    result;

    OP_CommandManager           *cmd;
    OP_Director                 *director;

    UT_StringArray              names;

    // Get the scene director.
    director = OPgetDirector();

    // Get the command manager.
    cmd = director->getCommandManager();

    cmd->getVariableNames(names, dirty);

    names.toStdVectorOfStrings(result);

    // Check for an empty vector.
    validateStringVector(result);

    return result;
}
""",

"""
void
setVariable(const char *name, const char *value, int local)
{
    OP_CommandManager           *cmd;
    OP_Director                 *director;

    // Get the scene director.
    director = OPgetDirector();

    // Get the command manager.
    cmd = director->getCommandManager();

    cmd->setVariable(name, value, local);
}
""",

"""
void
unsetVariable(const char *name)
{
    OP_CommandManager           *cmd;
    OP_Director                 *director;

    // Get the scene director.
    director = OPgetDirector();

    // Get the command manager.
    cmd = director->getCommandManager();

    cmd->unsetVariable(name);
}
""",

"""
void
varChange()
{
    int                         num_names;

    OP_CommandManager           *cmd;
    OP_Director                 *director;
    OP_Node                     *node;
    OP_NodeList                 nodes;
    OP_NodeList::const_iterator node_it;

    PRM_ParmList                *parms;

    UT_String                   var_name;
    UT_StringArray              dirty_names, var_names;

    // Get the scene director.
    director = OPgetDirector();

    // Get the command manager.
    cmd = director->getCommandManager();

    // Get any dirty variables.
    cmd->getVariableNames(dirty_names, true);

    // The number of dirty variable names.
    num_names = dirty_names.entries();

    // If there are no dirty variables, don't do anything.
    if (num_names == 0)
    {
        return;
    }

    // Process each dirty name and prefix it with a $.
    for (int i=0; i<num_names; ++i)
    {
        var_name.sprintf("$%s", dirty_names(i).buffer());
        var_names.append(var_name);
    }

    // Get all the nodes in the session.
    director->getAllNodes(nodes);

    // Process each node.
    for (node_it=nodes.begin(); !node_it.atEnd(); ++node_it)
    {
        // Get the node.
        node = *node_it;

        // Get the list of parameters for the node.
        parms = node->getParmList();

        // Search for each dirty variable name.
        for (int i=0; i<num_names; ++i)
        {
            // If the variable is used by any parameters on the node, tell
            // them to update.
            if (parms->findString(var_names(i), true, false))
            {
                parms->notifyVarChange(var_names(i));
            }
        }
    }

    // Clear all the diry variables.
    cmd->clearDirtyVariables();
}
""",

"""
int
addNumToRange(int num, int sec, void *data)
{
    std::vector<int>            *values;

    // Get the passed in vector.
    values = (std::vector<int> *)data;

    // Add the number to it.
    values->push_back(num);

    // Return 1 to keep going.
    return 1;
}
""",

"""
IntArray
expandRange(const char *pattern)
{
    std::vector<int>            values;

    UT_String                   range;
    UT_WorkArgs                 tokens;

    range = pattern;

    // Tokenize the pattern to split out the groups of ranges.
    range.tokenize(tokens, ' ');

    for (int i=0; i<tokens.getArgc(); ++i)
    {
        // Get the current range.
        UT_String tmp = tokens[i];

        // Add all the values in the range to the list.
        tmp.traversePattern(-1, &values, addNumToRange);
    }

    return values;
}
""",

"""
const char *
getAuthor(OP_Node *node)
{
    const OP_Stat &stat = node->getStat();
    return stat.getAuthor();
}
""",

"""
void
packGeometry(GU_Detail *source, GU_Detail *target)
{
    GU_DetailHandle gdh;
    gdh.allocateAndSet(source);

    GU_ConstDetailHandle const_handle(gdh);

    GU_PrimPacked *prim = GU_PackedGeometry::packGeometry(
        *target,
        const_handle
    );
}
""",

"""
void
sortByAttribute(GU_Detail *gdp,
                int attribute_type,
                const char *attrib_name,
                int index,
                bool reverse)
{
    GA_AttributeOwner owner = static_cast<GA_AttributeOwner>(attribute_type);

    // Get the index map for the specify attribute type.
    GA_IndexMap &map = gdp->getIndexMap(owner);

    // Build an attribute compare object for the attribute.
    GA_IndexMap::AttributeCompare compare(map, attrib_name, index);

    // Sort by the attribute.
    map.sortIndices(compare);

    // Reverse the sorted list.
    if (reverse)
    {
        map.reverseIndices();
    }
}
""",

"""
void
sortAlongAxis(GU_Detail *gdp, int element_type, int axis)
{
    // Convert the int value to the axis type.
    GU_AxisType axis_type = static_cast<GU_AxisType>(axis);

    // Sort primitives.
    if (element_type)
    {
        gdp->sortPrimitiveList(axis_type);
    }

    // Sort points.
    else
    {
        gdp->sortPointList(axis_type);
    }
}
""",

"""
void
sortListRandomly(GU_Detail *gdp, int element_type, float seed)
{
    // Sort primitives.
    if (element_type)
    {
        gdp->sortPrimitiveList(seed);
    }

    // Sort points.
    else
    {
        gdp->sortPointList(seed);
    }
}
""",

"""
void
shiftList(GU_Detail *gdp, int element_type, int offset)
{
    // Sort primitives.
    if (element_type)
    {
        gdp->shiftPrimitiveList(offset);
    }

    // Sort points.
    else
    {
        gdp->shiftPointList(offset);
    }
}
""",

"""
void
reverseList(GU_Detail *gdp, int element_type)
{
    // Sort primitives.
    if (element_type)
    {
        gdp->reversePrimitiveList();
    }

    // Sort points.
    else
    {
        gdp->reversePointList();
    }
}
""",

"""
void
proximityToList(GU_Detail *gdp, int element_type, const UT_Vector3D *point)
{
    UT_Vector3                  pos(*point);

    // Sort primitives.
    if (element_type)
    {
        gdp->proximityToPrimitiveList(pos);
    }

    // Sort points.
    else
    {
        gdp->proximityToPointList(pos);
    }
}
""",

"""
void
sortByVertexOrder(GU_Detail *gdp)
{
    gdp->sortByVertexOrder();
}
""",

"""
void
sortByValues(GU_Detail *gdp, int element_type, fpreal *values)
{
    // Sort primitives.
    if (element_type)
    {
        gdp->sortPrimitiveList(values);
    }

    // Sort points.
    else
    {
        gdp->sortPointList(values);
    }
}
""",

"""
void
setIcon(OP_Operator *op, const char *icon_name)
{
    op->setIconName(icon_name);
}
""",

"""
void
setDefaultIcon(OP_Operator *op)
{
    op->setDefaultIconName();
}
""",

"""
bool
isSubnetType(OP_Operator *op)
{
    return op->getIsPrimarySubnetType();
}
""",

"""
bool
isPython(OP_Operator *op)
{
    return op->getScriptIsPython();
}
""",

"""
int
createPoint(GU_Detail *gdp, UT_Vector3D *position)
{
    GA_Offset                   ptOff;

    // Add a new point.
    ptOff = gdp->appendPointOffset();

    // Set the position for the point.
    gdp->setPos3(ptOff, *position);

    // Return the point number.
    return gdp->pointIndex(ptOff);
}
""",

"""
int
createNPoints(GU_Detail *gdp, int npoints)
{
    GA_Offset                   ptOff;

    // Build a block of points.
    ptOff = gdp->appendPointBlock(npoints);

    // Return the starting point number.
    return gdp->pointIndex(ptOff);
}
""",

"""
void
mergePointGroup(GU_Detail *gdp, const GU_Detail *src, const char *group_name)
{
    const GA_PointGroup         *group;

    group = src->findPointGroup(group_name);

    gdp->mergePoints(*src, GA_Range(*group));
}
""",

"""
void
mergePoints(GU_Detail *gdp, const GU_Detail *src, int *vals, int num_vals)
{
    GA_OffsetList               points;

    for (int i=0; i<num_vals; ++i)
    {
        points.append(gdp->pointOffset(vals[i]));
    }

    gdp->mergePoints(*src, GA_Range(src->getPointMap(), points));
}
""",

"""
void
mergePrimGroup(GU_Detail *gdp, const GU_Detail *src, const char *group_name)
{
    const GA_PrimitiveGroup     *group;

    group = src->findPrimitiveGroup(group_name);

    gdp->mergePrimitives(*src, GA_Range(*group));
}
""",

"""
void
mergePrims(GU_Detail *gdp, const GU_Detail *src, int *vals, int num_vals)
{
    GA_OffsetList               prims;

    for (int i=0; i<num_vals; ++i)
    {
        prims.append(gdp->primitiveOffset(vals[i]));
    }

    gdp->mergePrimitives(*src, GA_Range(src->getPrimitiveMap(), prims));
}
""",

"""
void
copyAttributeValues(GU_Detail *dest_gdp,
                    int dest_entity_type,
                    int dest_entity_num,
                    const GU_Detail *src_gdp,
                    int src_entity_type,
                    int src_entity_num,
                    const char **attribute_names,
                    int num_attribs)
{
    GA_AttributeOwner           dest_owner, src_owner;

    GA_Attribute                *dest_attrib;
    const GA_Attribute          *attrib;
    GA_Offset                   dest_off, src_off;

    UT_String                   attr_name;

    dest_owner = static_cast<GA_AttributeOwner>(dest_entity_type);
    src_owner = static_cast<GA_AttributeOwner>(src_entity_type);

    // Build an attribute reference map between the geometry.
    GA_AttributeRefMap hmap(*dest_gdp, src_gdp);

    // Iterate over all the attribute names.
    for (int i=0; i < num_attribs; ++i)
    {
        // Get the attribute name.
        attr_name = attribute_names[i];

        // Get the attribute reference from the source geometry.

        attrib = src_gdp->findAttribute(src_owner, attr_name);

        if (attrib)
        {
            dest_attrib = dest_gdp->findAttribute(
                dest_owner,
                attrib->getScope(),
                attrib->getName()
            );

            if (!dest_attrib)
            {
                dest_attrib = dest_gdp->getAttributes().cloneAttribute(
                    dest_owner,
                    attrib->getName(),
                    *attrib,
                    true
                );
            }

            // Add a mapping between the source and dest attributes.
            hmap.append(dest_attrib, attrib);
        }
    }

    switch(src_owner)
    {
        case GA_ATTRIB_VERTEX:
            // Already a vertex offset.
            src_off = src_entity_num;
            break;

        case GA_ATTRIB_POINT:
            src_off = src_gdp->pointOffset(src_entity_num);
            break;

        case GA_ATTRIB_PRIMITIVE:
            src_off = src_gdp->primitiveOffset(src_entity_num);
            break;

        case GA_ATTRIB_GLOBAL:
            src_off = 0;
            break;
    }

    switch(dest_owner)
    {
        case GA_ATTRIB_VERTEX:
            // Already a vertex offset.
            dest_off = dest_entity_num;
            break;

        case GA_ATTRIB_POINT:
            dest_off = dest_gdp->pointOffset(dest_entity_num);
            break;

        case GA_ATTRIB_PRIMITIVE:
            dest_off = dest_gdp->primitiveOffset(dest_entity_num);
            break;

        case GA_ATTRIB_GLOBAL:
            dest_off = 0;
            break;
    }

    // Copy the attribute value.
    hmap.copyValue(dest_owner, dest_off, src_owner, src_off);
}
""",

"""
void
copyPointAttributeValues(GU_Detail *dest_gdp,
                         int dest_pt,
                         const GU_Detail *src_gdp,
                         int src_pt,
                         const char **attribute_names,
                         int num_attribs)
{
    GA_Attribute                *dest_attrib;
    const GA_Attribute          *attrib;
    GA_Offset                   srcOff, destOff;

    UT_String                   attr_name;

    // Build an attribute reference map between the geometry.
    GA_AttributeRefMap hmap(*dest_gdp, src_gdp);

    // Iterate over all the attribute names.
    for (int i=0; i < num_attribs; ++i)
    {
        // Get the attribute name.
        attr_name = attribute_names[i];

        // Get the attribute reference from the source geometry.
        attrib = src_gdp->findPointAttribute(attr_name);

        if (attrib)
        {
            // Try to find the same attribute on the destination geometry.
            dest_attrib = dest_gdp->findPointAttrib(*attrib);

            // If it doesn't exist, create it.
            if (!dest_attrib)
            {
                dest_attrib = dest_gdp->addPointAttrib(attrib);
            }

            // Add a mapping between the source and dest attributes.
            hmap.append(dest_attrib, attrib);
        }
    }

    // Get the point offsets.
    srcOff = src_gdp->pointOffset(src_pt);
    destOff = dest_gdp->pointOffset(dest_pt);

    // Copy the attribute value.
    hmap.copyValue(GA_ATTRIB_POINT, destOff, GA_ATTRIB_POINT, srcOff);
}
""",

"""
void
copyPrimAttributeValues(GU_Detail *dest_gdp,
                        int dest_pr,
                        const GU_Detail *src_gdp,
                        int src_pr,
                        const char **attribute_names,
                        int num_attribs)
{
    GA_Attribute                *dest_attrib;
    const GA_Attribute          *attrib;
    GA_Offset                   srcOff, destOff;

    UT_String                   attr_name;

    // Build an attribute reference map between the geometry.
    GA_AttributeRefMap hmap(*dest_gdp, src_gdp);

    // Iterate over all the attribute names.
    for (int i=0; i < num_attribs; ++i)
    {
        // Get the attribute name.
        attr_name = attribute_names[i];

        // Get the attribute reference from the source geometry.
        attrib = src_gdp->findPrimitiveAttribute(attr_name);

        if (attrib)
        {
            // Try to find the same attribute on the destination geometry.
            dest_attrib = dest_gdp->findPrimAttrib(*attrib);

            // If it doesn't exist, create it.
            if (!dest_attrib)
            {
                dest_attrib = dest_gdp->addPrimAttrib(attrib);
            }

            // Add a mapping between the source and dest attributes.
            hmap.append(dest_attrib, attrib);
        }
    }

    // Get the primitive offsets.
    srcOff = src_gdp->primitiveOffset(src_pr);
    destOff = dest_gdp->primitiveOffset(dest_pr);

    // Copy the attribute value.
    hmap.copyValue(GA_ATTRIB_PRIMITIVE, destOff, GA_ATTRIB_PRIMITIVE, srcOff);
}
""",

"""
IntArray
pointAdjacentPolygons(const GU_Detail *gdp, int prim_num)
{
    std::vector<int>            prim_nums;

    GA_Offset                   primOff;
    GA_OffsetArray              prims;
    GA_OffsetArray::const_iterator prims_it;

    // Find the offset for this primitive.
    primOff = gdp->primitiveOffset(prim_num);

    // Get a list of point adjacent polygons.
    gdp->getPointAdjacentPolygons(prims, primOff);

    // Add the adjacent prim numbers to the list.
    for (prims_it = prims.begin(); !prims_it.atEnd(); ++prims_it)
    {
        prim_nums.push_back(gdp->primitiveIndex(*prims_it));
    }

    return prim_nums;
}
""",

"""
IntArray
edgeAdjacentPolygons(const GU_Detail *gdp, int prim_num)
{
    std::vector<int>            prim_nums;

    GA_Offset                   primOff;
    GA_OffsetArray              prims;
    GA_OffsetArray::const_iterator prims_it;

    // Find the offset for this primitive.
    primOff = gdp->primitiveOffset(prim_num);

    // Get a list of edge adjacent polygons.
    gdp->getEdgeAdjacentPolygons(prims, primOff);

    // Add the adjacent prim numbers to the list.
    for (prims_it = prims.begin(); !prims_it.atEnd(); ++prims_it)
    {
        prim_nums.push_back(gdp->primitiveIndex(*prims_it));
    }

    return prim_nums;
}
""",

"""
IntArray
connectedPrims(const GU_Detail *gdp, int pt_num)
{
    std::vector<int>            prim_nums;

    GA_Offset                   ptOff;
    GA_OffsetArray              prims;
    GA_OffsetArray::const_iterator prims_it;

    // Get the selected point offset.
    ptOff = gdp->pointOffset(pt_num);

    // Get all the primitives referencing this point.
    gdp->getPrimitivesReferencingPoint(prims, ptOff);

    // Add all the primitive numbers to the list.
    for (prims_it = prims.begin(); !prims_it.atEnd(); ++prims_it)
    {
        prim_nums.push_back(gdp->primitiveIndex(*prims_it));
    }

    return prim_nums;
}
""",

"""
IntArray
connectedPoints(const GU_Detail *gdp, int pt_num)
{
    std::vector<int>            pt_nums;

    GA_Offset                   ptOff;
    GA_OffsetArray              prims;
    GA_Range                    pt_range;

    const GEO_Primitive         *prim;

    ptOff = gdp->pointOffset(pt_num);

    // Get the primitives referencing the point.
    gdp->getPrimitivesReferencingPoint(prims, ptOff);

    // Build a range for those primitives.
    GA_Range pr_range(gdp->getPrimitiveMap(), prims);

    for (GA_Iterator pr_it(pr_range.begin()); !pr_it.atEnd(); ++pr_it)
    {
        prim = (GEO_Primitive *)gdp->getPrimitive(*pr_it);

        // Get the points referenced by the vertices of the primitive.
        pt_range = prim->getPointRange();

        for (GA_Iterator pt_it(pt_range.begin()); !pt_it.atEnd(); ++pt_it)
        {
            // Build an edge between the source point and this point on the
            // primitive.
            GA_Edge edge(ptOff, *pt_it);

            // If there is an edge between those 2 points, add the point
            // to the list.
            if (prim->hasEdge(edge))
            {
                pt_nums.push_back(gdp->pointIndex(*pt_it));
            }
        }
    }

    return pt_nums;
}
""",

"""
VertexMap
referencingVertices(const GU_Detail *gdp, int pt_num)
{
    std::vector<int>            prim_indices, vert_indices;

    GA_Index                    primIdx;
    GA_Offset                   ptOff, primOff, vtxOff;
    GA_OffsetArray              vertices;
    GA_OffsetArray::const_iterator vert_it;
    const GA_Primitive          *prim;

    VertexMap                   vert_map;

    ptOff = gdp->pointOffset(pt_num);
    gdp->getVerticesReferencingPoint(vertices, ptOff);

    for (vert_it = vertices.begin(); !vert_it.atEnd(); ++vert_it)
    {
        vtxOff = *vert_it;

        primOff = gdp->vertexPrimitive(vtxOff);
        primIdx = gdp->primitiveIndex(primOff);

        prim = gdp->getPrimitive(primOff);

        for (unsigned i=0; i<prim->getVertexCount(); ++i)
        {
            if (prim->getVertexOffset(i) == vtxOff)
            {
                prim_indices.push_back(primIdx);
                vert_indices.push_back(i);
            }
        }
    }

    vert_map.prims.set(prim_indices);
    vert_map.indices.set(vert_indices);

    return vert_map;
}
""",

"""
IntArray
getStringTableIndices(const GU_Detail *gdp, int attribute_type, const char *attrib_name)
{
    std::vector<int>            result;

    const GA_AIFSharedStringTuple       *s_t;
    const GA_Attribute          *attrib;

    GA_Range                    range;

    GA_StringIndexType          index;

    UT_IntArray                 indices;


    GA_AttributeOwner owner = static_cast<GA_AttributeOwner>(attribute_type);

    attrib = gdp->findStringTuple(owner, attrib_name);

    // Figure out the range of elements we need to iterate over.
    switch(owner)
    {
        case GA_ATTRIB_VERTEX:
            range = gdp->getVertexRange();
            break;

        case GA_ATTRIB_POINT:
            range = gdp->getPointRange();
            break;

        case GA_ATTRIB_PRIMITIVE:
            range = gdp->getPrimitiveRange();
            break;
    }

    // Get a shared string tuple from the attribute.
    s_t = attrib->getAIFSharedStringTuple();

    for (GA_Iterator it(range); !it.atEnd(); ++it)
    {
        result.push_back(s_t->getHandle(attrib, *it, 0));
    }

    return result;
}
""",

"""
StringArray
vertexStringAttribValues(const GU_Detail *gdp, const char *attrib_name)
{
    std::vector<std::string>    result;

    const GA_AIFSharedStringTuple       *s_t;
    const GA_Attribute          *attrib;

    GA_Range                    range;

    attrib = gdp->findStringTuple(GA_ATTRIB_VERTEX, attrib_name);

    range = gdp->getVertexRange();

    // Get a shared string tuple from the attribute.
    s_t = attrib->getAIFSharedStringTuple();

    for (GA_Iterator it(range); !it.atEnd(); ++it)
    {
        result.push_back(s_t->getString(attrib, *it, 0));
    }

    return result;
}
""",

"""
void
setVertexStringAttribValues(GU_Detail *gdp,
                      const char *attrib_name,
                      const char **values,
                      int num_values)
{
    const GA_AIFSharedStringTuple       *s_t;
    GA_Attribute                *attrib;

    GA_Range                    range;

    // Try to find the string attribute.
    attrib = gdp->findStringTuple(GA_ATTRIB_VERTEX, attrib_name);

    // Get a shared string tuple from the attribute.
    s_t = attrib->getAIFSharedStringTuple();


    range = gdp->getVertexRange();

    int i = 0;

    for (GA_Iterator it(range); !it.atEnd(); ++it)
    {
        s_t->setString(attrib, *it, values[i], 0);
        i++;
    }
}
""",

"""
void
setSharedStringAttrib(GU_Detail *gdp,
                      int attribute_type,
                      const char *attrib_name,
                      const char *value,
                      const char *group_name)
{
    const GA_AIFSharedStringTuple       *s_t;
    GA_Attribute                *attrib;

    GA_ElementGroup             *group = 0;

    GA_Range                    range;


    GA_AttributeOwner owner = static_cast<GA_AttributeOwner>(attribute_type);

    // Find the point group if necessary.
    if (group_name)
    {
        switch(owner)
        {
            case GA_ATTRIB_VERTEX:
                group = gdp->findVertexGroup(group_name);
                range = GA_Range(*group);
                break;

            case GA_ATTRIB_POINT:
                group = gdp->findPointGroup(group_name);
                range = GA_Range(*group);
                break;

            case GA_ATTRIB_PRIMITIVE:
                group = gdp->findPrimitiveGroup(group_name);
                range = GA_Range(*group);
                break;
        }
    }

    else
    {
        // Figure out the range of elements we need to iterate over.
        switch(owner)
        {
            case GA_ATTRIB_VERTEX:
                range = gdp->getVertexRange();
                break;

            case GA_ATTRIB_POINT:
                range = gdp->getPointRange();
                break;

            case GA_ATTRIB_PRIMITIVE:
                range = gdp->getPrimitiveRange();
                break;
        }
    }

    // Try to find the string attribute.
    attrib = gdp->findStringTuple(owner, attrib_name);

    // Get a shared string tuple from the attribute.
    s_t = attrib->getAIFSharedStringTuple();

    // Set all the specified elements to the value.
    s_t->setString(attrib, range, value, 0);
}
""",

"""
bool
hasEdge(const GU_Detail *gdp,
        unsigned prim_num,
        unsigned pt_num1,
        unsigned pt_num2)
{
    GA_Offset                   ptOff1, ptOff2;

    const GEO_Face              *face;

    ptOff1 = gdp->pointOffset(pt_num1);
    ptOff2 = gdp->pointOffset(pt_num2);

    face = (GEO_Face *)gdp->getPrimitiveByIndex(prim_num);

    // Build an edge between the the two points.
    GA_Edge edge(ptOff1, ptOff2);

    return face->hasEdge(edge);
}
""",

"""
void
insertVertex(GU_Detail *gdp,
             unsigned prim_num,
             unsigned pt_num,
             unsigned idx)
{
    GA_Offset                   ptOff;

    GEO_Face                    *face;

    ptOff = gdp->pointOffset(pt_num);

    face = (GEO_Face *)gdp->getPrimitiveByIndex(prim_num);

    face->insertVertex(ptOff, idx);
}
""",

"""
void
deleteVertex(GU_Detail *gdp, unsigned prim_num, unsigned idx)
{
    GEO_Face                    *face;

    face = (GEO_Face *)gdp->getPrimitiveByIndex(prim_num);

    face->deleteVertex(idx);
}
""",

"""
void
setPoint(GU_Detail *gdp, unsigned prim_num, unsigned idx, unsigned pt_num)
{
    GA_Offset                   ptOff;
    GA_Primitive                *prim;

    ptOff = gdp->pointOffset(pt_num);

    prim = gdp->getPrimitiveByIndex(prim_num);

    prim->setPointOffset(idx, ptOff);
}
""",

"""
Position3D
baryCenter(const GU_Detail *gdp, unsigned prim_num)
{
    const GEO_Primitive         *prim;

    UT_Vector3                  center;

    Position3D                  pos;

    prim = (GEO_Primitive *)gdp->getPrimitiveByIndex(prim_num);

    center = prim->baryCenter();

    pos.x = center.x();
    pos.y = center.y();
    pos.z = center.z();

    return pos;
}
""",

"""
void
reversePrimitive(const GU_Detail *gdp, unsigned prim_num)
{
    GEO_Primitive               *prim;

    prim = (GEO_Primitive *)gdp->getPrimitiveByIndex(prim_num);

    return prim->reverse();
}
""",

"""
void
makeUnique(GU_Detail *gdp, unsigned prim_num)
{
    GEO_Primitive               *prim;

    prim = (GEO_Primitive *)gdp->getPrimitiveByIndex(prim_num);

    gdp->uniquePrimitive(prim);
}
""",

"""
bool
renameGroup(GU_Detail *gdp, const char *from_name, const char *to_name, int group_type)
{
    GA_GroupType owner = static_cast<GA_GroupType>(group_type);

    GA_GroupTable *table = gdp->getGroupTable(owner);

    return table->renameGroup(from_name, to_name);
}
""",

"""
FloatArray
groupBoundingBox(const GU_Detail *gdp, int group_type, const char *group_name)
{
    std::vector<double>         result;

    const GA_Group              *group;

    UT_BoundingBox              bbox;

    GA_GroupType type = static_cast<GA_GroupType>(group_type);

    switch (type)
    {
        // Point group.
        case GA_GROUP_POINT:
            group = gdp->findPointGroup(group_name);
            break;

        // Prim group.
        case GA_GROUP_PRIMITIVE:
            group = gdp->findPrimitiveGroup(group_name);
            break;

        // Edge group.
        case GA_GROUP_EDGE:
            group = gdp->findEdgeGroup(group_name);
            break;
    }

    gdp->getGroupBBox(&bbox, group);

    result.push_back(bbox.xmin());
    result.push_back(bbox.ymin());
    result.push_back(bbox.zmin());

    result.push_back(bbox.xmax());
    result.push_back(bbox.ymax());
    result.push_back(bbox.zmax());

    return result;
}
""",

"""
bool
addNormalAttribute(GU_Detail *gdp)
{
    GA_Attribute                *attrib;

    attrib = gdp->addNormalAttribute(GA_ATTRIB_POINT);

    // Return true if the attribute was created.
    if (attrib)
    {
        return true;
    }

    // False otherwise.
    return false;
}
""",

"""
bool
addVelocityAttribute(GU_Detail *gdp)
{
    GA_Attribute                *attrib;

    attrib = gdp->addVelocityAttribute(GA_ATTRIB_POINT);

    // Return true if the attribute was created.
    if (attrib)
    {
        return true;
    }

    // False otherwise.
    return false;
}
""",

"""
bool
addDiffuseAttribute(GU_Detail *gdp, int attribute_type)
{
    GA_Attribute                *attrib;

    GA_AttributeOwner owner = static_cast<GA_AttributeOwner>(attribute_type);

    attrib = gdp->addDiffuseAttribute(owner);

    // Return true if the attribute was created.
    if (attrib)
    {
        return true;
    }

    // False otherwise.
    return false;
}
""",

"""
void
computePointNormals(GU_Detail *gdp)
{
    gdp->normal();
}
""",

"""
void
convexPolygons(GU_Detail *gdp, unsigned maxpts=3)
{
    gdp->convex(maxpts);
}
""",

"""
void
destroyEmptyGroups(GU_Detail *gdp, int attribute_type)
{
    GA_AttributeOwner owner = static_cast<GA_AttributeOwner>(attribute_type);

    gdp->destroyEmptyGroups(owner);
}
""",

"""
void
destroyUnusedPoints(GU_Detail *gdp, const char *group_name)
{
    GA_PointGroup               *group = 0;

    // If we passed in a valid group, try to find it.
    if (group_name)
    {
        group = gdp->findPointGroup(group_name);
    }

    gdp->destroyUnusedPoints(group);
}
""",

"""
void
consolidatePoints(GU_Detail *gdp, double distance, const char *group_name)
{
    GA_PointGroup               *group = 0;

    if (group_name)
    {
        group = gdp->findPointGroup(group_name);
    }

    gdp->fastConsolidatePoints(distance, group);
}
""",

"""
void
uniquePoints(GU_Detail *gdp, const char *group_name)
{
    gdp->uniquePoints(gdp->findPointGroup(group_name));
}
""",

"""
int
groupSize(const GU_Detail *gdp, const char *group_name, int group_type)
{
    const GA_Group              *group;

    GA_GroupType type = static_cast<GA_GroupType>(group_type);

    switch (type)
    {
        // Point group.
        case GA_GROUP_POINT:
            group = gdp->findPointGroup(group_name);
            break;

        // Prim group.
        case GA_GROUP_PRIMITIVE:
            group = gdp->findPrimitiveGroup(group_name);
            break;

        // Edge group.
        case GA_GROUP_EDGE:
            group = gdp->findEdgeGroup(group_name);
            break;
    }

    return group->entries();
}
""",

"""
void
toggleMembership(GU_Detail *gdp,
                 const char *group_name,
                 int group_type,
                 int elem_num)
{
    GA_ElementGroup             *group;
    GA_Offset                   elem_offset;

    GA_GroupType type = static_cast<GA_GroupType>(group_type);

    switch (type)
    {
        case GA_GROUP_POINT:
            group = gdp->findPointGroup(group_name);
            elem_offset = gdp->pointOffset(elem_num);
            break;

        case GA_GROUP_PRIMITIVE:
            group = gdp->findPrimitiveGroup(group_name);
            elem_offset = gdp->primitiveOffset(elem_num);
            break;
    }

    group->toggleOffset(elem_offset);
}
""",

"""
void
setEntries(GU_Detail *gdp, const char *group_name, int group_type)
{
    GA_ElementGroup             *group;

    GA_GroupType type = static_cast<GA_GroupType>(group_type);

    switch (type)
    {
        case GA_GROUP_POINT:
            group = gdp->findPointGroup(group_name);
            break;

        case GA_GROUP_PRIMITIVE:
            group = gdp->findPrimitiveGroup(group_name);
            break;
    }

    group->setEntries();
}
""",

"""
void
toggleEntries(GU_Detail *gdp, const char *group_name, int group_type)
{
    GA_EdgeGroup                *egroup;
    GA_ElementGroup             *group;

    GA_GroupType type = static_cast<GA_GroupType>(group_type);

    switch (type)
    {
        case GA_GROUP_POINT:
            group = gdp->findPointGroup(group_name);
            group->toggleEntries();
            break;

        case GA_GROUP_PRIMITIVE:
            group = gdp->findPrimitiveGroup(group_name);
            group->toggleEntries();
            break;

        case GA_GROUP_EDGE:
            egroup = gdp->findEdgeGroup(group_name);
            egroup->toggleEntries();
            break;
    }
}
""",

"""
void
copyGroup(GU_Detail *gdp,
          int group_type,
          const char *group_name,
          const char *new_group_name)
{
    GA_AttributeOwner           owner;
    GA_ElementGroup             *new_group;
    const GA_ElementGroup       *group;

    owner = static_cast<GA_AttributeOwner>(group_type);

    // Find the current group.
    group = gdp->findElementGroup(owner, group_name);

    // Create the new group.
    new_group = gdp->createElementGroup(owner, new_group_name);

    // Copy the membership to the new group.
    new_group->copyMembership(*group);
}
""",

"""
bool
containsAny(const GU_Detail *gdp,
            const char *group_name,
            const char *other_group_name,
            int group_type)
{
    const GA_ElementGroup       *group;
    const GA_PointGroup         *point_group;
    const GA_PrimitiveGroup     *prim_group;

    GA_Range                    range;


    GA_GroupType type = static_cast<GA_GroupType>(group_type);

    switch (type)
    {
        case GA_GROUP_POINT:
            group = gdp->findPointGroup(group_name);
            point_group = gdp->findPointGroup(other_group_name);

            range = gdp->getPointRange(point_group);
            break;

        case GA_GROUP_PRIMITIVE:
            group = gdp->findPrimitiveGroup(group_name);
            prim_group = gdp->findPrimitiveGroup(other_group_name);

            range = gdp->getPrimitiveRange(prim_group);
            break;
    }

    return group->containsAny(range);
}
""",

"""
void
primToPointGroup(GU_Detail *gdp,
                 const char *group_name,
                 const char *new_group_name,
                 bool destroy)
{
    GA_PointGroup               *point_group;
    GA_PrimitiveGroup           *prim_group;
    GA_Range                    pr_range, pt_range;

    // The source group.
    prim_group = gdp->findPrimitiveGroup(group_name);

    // Create a new point group.
    point_group = gdp->newPointGroup(new_group_name);

    // Get the range of primitives in the source group.
    pr_range = GA_Range(*prim_group);

    for (GA_Iterator pr_it(pr_range); !pr_it.atEnd(); ++pr_it)
    {
        // Get the range of points referenced by the vertices of
        // the primitive.
        pt_range = gdp->getPrimitive(*pr_it)->getPointRange();

        // Add each point offset to the group.
        for (GA_Iterator pt_it(pt_range); !pt_it.atEnd(); ++pt_it)
        {
            point_group->addOffset(*pt_it);
        }
    }

    // Destroy the source group if necessary.
    if (destroy)
    {
        gdp->destroyPrimitiveGroup(prim_group);
    }
}
""",

"""
void
pointToPrimGroup(GU_Detail *gdp,
                 const char *group_name,
                 const char *new_group_name,
                 bool destroy)
{
    GA_OffsetArray              prims;
    GA_OffsetArray::const_iterator prims_it;
    GA_PointGroup               *point_group;
    GA_PrimitiveGroup           *prim_group;
    GA_Range                    pr_range, pt_range;

    // The source group.
    point_group = gdp->findPointGroup(group_name);

    // Create a new primitive group.
    prim_group = gdp->newPrimitiveGroup(new_group_name);

    // The range of points in the source group.
    pt_range = GA_Range(*point_group);

    for (GA_Iterator pt_it(pt_range); !pt_it.atEnd(); ++pt_it)
    {
        // Get an array of primitives that reference the point.
        gdp->getPrimitivesReferencingPoint(prims, *pt_it);

        // Add each primitive offset to the group.
        for (prims_it = prims.begin(); !prims_it.atEnd(); ++prims_it)
        {
            prim_group->addOffset(*prims_it);
        }
    }

    // Destroy the source group if necessary.
    if (destroy)
    {
        gdp->destroyPointGroup(point_group);
    }
}
""",

"""
bool
hasUngroupedPoints(const GU_Detail *gdp)
{
    GA_PointGroup  *all, *group;

    all = gdp->newDetachedPointGroup();

    GA_FOR_ALL_POINTGROUPS(gdp, group)
    {
        (*all) |= *group;
    }

    return all->entries() < gdp->getNumPoints();
}
""",

"""
void
groupUngroupedPoints(GU_Detail *gdp, const char *ungrouped_name)
{
    GA_PointGroup  *all, *group, *ungrouped;

    all = gdp->newDetachedPointGroup();

    GA_FOR_ALL_POINTGROUPS(gdp, group)
    {
        (*all) |= *group;
    }

    if (all->entries() < gdp->getNumPoints())
    {
        all->toggleEntries();

        ungrouped = gdp->newPointGroup(ungrouped_name);

        ungrouped->combine(all);
    }
}
""",

"""
bool
hasUngroupedPrims(const GU_Detail *gdp)
{
    GA_PrimitiveGroup  *all, *group;

    all = gdp->newDetachedPrimitiveGroup();

    GA_FOR_ALL_PRIMGROUPS(gdp, group)
    {
        (*all) |= *group;
    }

    return all->entries() < gdp->getNumPrimitives();
}
""",

"""
void
groupUngroupedPrims(GU_Detail *gdp, const char *ungrouped_name)
{
    GA_PrimitiveGroup  *all, *group, *ungrouped;

    all = gdp->newDetachedPrimitiveGroup();

    GA_FOR_ALL_PRIMGROUPS(gdp, group)
    {
        (*all) |= *group;
    }

    if (all->entries() < gdp->getNumPrimitives())
    {
        all->toggleEntries();

        ungrouped = gdp->newPrimitiveGroup(ungrouped_name);

        ungrouped->combine(all);
    }
}
""",

"""
void
clip(GU_Detail *gdp,
     UT_DMatrix4 *xform,
     UT_Vector3D *normal,
     float dist,
     const char *group_name)
{
    GA_PrimitiveGroup           *group = 0;

    UT_Matrix4 mat(*xform);
    UT_Vector3 dir(*normal);

    // Invert the matrix to move the geometry from our cutting location to the
    // origin and transform it.
    mat.invert();
    gdp->transform(mat);

    // Find the primitive group if necessary.
    if (group_name)
    {
        group = gdp->findPrimitiveGroup(group_name);
    }

    // Construct a new GQ Detail to do the clipping.
    GQ_Detail *gqd = new GQ_Detail(gdp, group);

    // Clip the geometry.
    gqd->clip(dir, -dist, 0);

    // Remove the detail.
    delete gqd;

    // Invert the matrix again and move the geometry back to its original
    // position.
    mat.invert();
    gdp->transform(mat);
}
""",

"""
bool
isInside(const UT_BoundingBoxD *bbox1, const UT_BoundingBoxD *bbox2)
{
    return bbox1->isInside(*bbox2);
}
""",

"""
bool
intersects(UT_BoundingBoxD *bbox1, const UT_BoundingBoxD *bbox2)
{
    return bbox1->intersects(*bbox2);
}
""",

"""
bool
computeIntersection(UT_BoundingBoxD *bbox1, const UT_BoundingBoxD *bbox2)
{
    return bbox1->computeIntersection(*bbox2);
}
""",

"""
void
expandBounds(UT_BoundingBoxD *bbox, float dltx, float dlty, float dltz)
{
    bbox->expandBounds(dltx, dlty, dltz);
}
""",

"""
void
addToMin(UT_BoundingBoxD *bbox, const UT_Vector3D *vec)
{
    bbox->addToMin(*vec);
}
""",

"""
void
addToMax(UT_BoundingBoxD *bbox, const UT_Vector3D *vec)
{
    bbox->addToMax(*vec);
}
""",

"""
double
boundingBoxArea(const UT_BoundingBoxD *bbox)
{
    return bbox->area();
}
""",

"""
double
boundingBoxVolume(const UT_BoundingBoxD *bbox)
{
    return bbox->volume();
}
""",

"""
void
disconnectAllOutputs(OP_Node *node)
{
    node->disconnectAllOutputs();
}
""",

"""
bool
isCompiled(const OP_Node *node)
{
    return node->isCompiled();
}
""",

"""
int
getMultiParmInstancesPerItem(OP_Node *node, const char *parm_name)
{
    int                         instances;

    PRM_Parm                    *parm;

    PRM_Parm &multiparm = node->getParm(parm_name);

    instances = multiparm.getMultiParmInstancesPerItem();

    return instances;
}
""",

"""
int
getMultiParmStartOffset(OP_Node *node, const char *parm_name)
{
    int                         offset;

    PRM_Parm                    *parm;

    PRM_Parm &multiparm = node->getParm(parm_name);

    offset = multiparm.getMultiStartOffset();

    return offset;
}
""",

"""
IntArray
getMultiParmInstanceIndex(OP_Node *node, const char *parm_name)
{
    std::vector<int>            result;

    UT_IntArray                 indices;

    PRM_Parm &parm = node->getParm(parm_name);

    parm.getMultiInstanceIndex(indices);

    indices.toStdVector(result);

    return result;
}
""",

"""
StringTuple
getMultiParmInstances(OP_Node *node, const char *parm_name)
{
    int                         items, instances;
    std::vector<StringArray>    blocks;

    PRM_Parm                    *parm;

    PRM_Parm &multiparm = node->getParm(parm_name);

    // The number of multi parm blocks.
    items = multiparm.getMultiParmNumItems();

    // The number of parms in each block.
    instances = multiparm.getMultiParmInstancesPerItem();

    for (int i=0; i < items; ++i)
    {
        std::vector<std::string>    result;

        for (int j=0; j < instances; ++j)
        {
            parm = multiparm.getMultiParm(i * instances + j);
            result.push_back(parm->getToken());
        }

        // Check for an empty vector.
        validateStringVector(result);

        blocks.push_back(result);
    }

    // If there are no entries, add an empty block.
    if (blocks.size() == 0)
    {
        std::vector<std::string>    result;
        result.push_back("");
        blocks.push_back(result);
    }

    return blocks;
}
""",

"""
void
buildLookat(UT_DMatrix3 *mat,
            const UT_Vector3D *from,
            const UT_Vector3D *to,
            const UT_Vector3D *up)
{
    mat->lookat(*from, *to, *up);
}
""",

"""
void
getDual(const UT_Vector3D *vec, UT_DMatrix3 *mat)
{
    vec->getDual(*mat);
}
""",

"""
const char *
getMetaSource(const char *filename)
{
    int                         idx;

    OP_OTLLibrary               *lib;

    UT_String                   test;

    OP_OTLManager &manager = OPgetDirector()->getOTLManager();
    idx = manager.findLibrary(filename);

    lib = (idx >= 0) ? manager.getLibrary(idx): NULL;

    if (lib)
    {
        return lib->getMetaSource();
    }

    return "";
}
""",

"""
bool
removeMetaSource(const char *metasrc)
{
    OP_OTLManager &manager = OPgetDirector()->getOTLManager();

    // Try to remove the meta source and return whether or not it was
    // successful.
    return manager.removeMetaSource(metasrc);
}
""",

"""
StringArray
getLibrariesInMetaSource(const char *metasrc)
{
    std::vector<std::string>    result;

    OP_OTLLibrary               *library;

    OP_OTLManager &manager = OPgetDirector()->getOTLManager();

    // Iterate through the list of libraries.
    for (int i=0; i<manager.getNumLibraries(); ++i)
    {
        // Get the current library.
        library = manager.getLibrary(i);

        // Check if the meta source is equal to the target one.  If so, add
        // the library file path to the string list.
        if (library->getMetaSource() == metasrc)
        {
            result.push_back(library->getSource().toStdString());
        }

    }

    // Check for an empty vector.
    validateStringVector(result);

    return result;
}
""",

"""
bool
isDummyDefinition(const char *filename,
                  const char *tablename,
                  const char *opname)
{
    int                         def_idx, lib_idx;

    OP_OTLDefinition            definition;
    OP_OTLLibrary               *lib;

    // Get the OTL manager.
    OP_OTLManager &manager = OPgetDirector()->getOTLManager();

    // Try to find the library with the file name.
    lib_idx = manager.findLibrary(filename);

    // Get the library.
    lib = (lib_idx >= 0) ? manager.getLibrary(lib_idx): NULL;

    if (lib)
    {
        // Try to find a definition for the operator type.
        def_idx = lib->getDefinitionIndex(tablename, opname);

        // If it exists, query if it is a dummy definition.
        if (def_idx >= 0)
        {
            return lib->getDefinitionIsDummy(def_idx);
        }
    }

    // Couldn't find the library or definition inside is, so return false.
    return false;
}
"""
]

# Create the library as a private object.
_cpp_methods = inlinecpp.createLibrary(
    "cpp_methods",
    acquire_hom_lock=True,
    catch_crashes=True,
    includes="""
#include <CMD/CMD_Variable.h>
#include <GA/GA_AttributeRefMap.h>
#include <GA/GA_Primitive.h>
#include <GEO/GEO_Face.h>
#include <GEO/GEO_PointTree.h>
#include <GQ/GQ_Detail.h>
#include <GU/GU_Detail.h>
#include <GU/GU_PackedGeometry.h>
#include <GU/GU_PrimPacked.h>
#include <OBJ/OBJ_Node.h>
#include <OP/OP_CommandManager.h>
#include <OP/OP_Director.h>
#include <OP/OP_Node.h>
#include <OP/OP_OTLDefinition.h>
#include <OP/OP_OTLLibrary.h>
#include <OP/OP_OTLManager.h>
#include <PRM/PRM_Parm.h>
#include <ROP/ROP_RenderManager.h>
#include <UT/UT_WorkArgs.h>

using namespace std;

// Validate a vector of strings so that it can be returned as a StringArray.
// Currently we cannot return an empty vector.
void validateStringVector(std::vector<std::string> &string_vec)
{
    // Check for an empty vector.
    if (string_vec.size() == 0)
    {
        // An an empty string.
        string_vec.push_back("");
    }
}

""",
    structs=[
        ("IntArray", "*i"),
        ("FloatArray", "*d"),
        ("StringArray", "**c"),
        ("StringTuple", "*StringArray"),
        ("VertexMap", (("prims", "*i"), ("indices", "*i"))),
        ("Position3D", (("x", "d"), ("y", "d"), ("z", "d"))),
    ],
    function_sources=_FUNCTION_SOURCES
)

# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

def _buildCDoubleArray(values):
    """Convert a list of numbers to a ctypes double array."""
    import ctypes
    arr = (ctypes.c_double * len(values))()
    arr[:] = values

    return arr


def _buildCIntArray(values):
    """Convert a list of numbers to a ctypes int array."""
    import ctypes
    arr = (ctypes.c_int * len(values))()
    arr[:] = values

    return arr

def _buildCStringArray(values):
    """Convert a list of numbers to a ctypes char * array."""
    import ctypes
    arr = (ctypes.c_char_p * len(values))()
    arr[:] = values

    return arr


def _cleanStringValues(values):
    """Process a string list, removing empty strings."""
    return tuple([val for val in values if val])


def _findAttrib(geometry, attrib_type, name):
    """Find an attribute with a given name and type on the geometry."""
    if attrib_type == hou.attribType.Vertex:
        return geometry.findVertexAttrib(name)

    elif attrib_type == hou.attribType.Point:
        return geometry.findPointAttrib(name)

    elif attrib_type == hou.attribType.Prim:
        return geometry.findPrimAttrib(name)

    else:
        return geometry.findGlobalAttrib(name)


def _findGroup(geometry, group_type, name):
    """Find a group with a given name and type.

    group_type corresponds to the integer returned by _getGroupType()

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


def _getAttribStorage(data_type):
    """Get an HDK compatible attribute storage class value."""
    return _ATTRIB_STORAGE_MAP[data_type]


def _getAttribOwner(attribute_type):
    """Get an HDK compatible attribute owner value."""
    return _ATTRIB_TYPE_MAP[attribute_type]


def _getAttribOwnerFromGeometryType(entity_type):
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


def _getGroupAttribOwner(group):
    """Get an HDK compatible group attribute type value."""
    try:
        return _GROUP_ATTRIB_MAP[type(group)]

    except KeyError:
        raise hou.OperationFailed("Invalid group type")


def _getGroupType(group):
    """Get an HDK compatible group type value."""
    try:
        return _GROUP_TYPE_MAP[type(group)]

    except KeyError:
        raise hou.OperationFailed("Invalid group type")


def _getNodesFromPaths(paths):
    """Convert a list of string paths to hou.Node objects."""
    return tuple([hou.node(path) for path in paths if path])


def _getPointsFromList(geometry, point_list):
    """Convert a list of point numbers to hou.Point objects."""
    # Return a empty tuple if the point list is empty.
    if not point_list:
        return ()

    # Convert the list of integers to a space separated string.
    point_str = ' '.join([str(i) for i in point_list])

    # Glob for the specified points.
    return geometry.globPoints(point_str)


def _getPrimsFromList(geometry, prim_list):
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

def addToClass(*args, **kwargs):
    """This function decorator adds the function to specified classes,
    optionally specifying a different function name.

    *args:
        One of more HOM classes to extend.

    **kwargs:
        name: Set a specific name for the unbound method.

    """
    import types

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


def addToModule(module):
    """This function decorator adds the function to a specified module."""

    def decorator(func):
        # Simply add the function to the module object.
        setattr(module, func.__name__, func)
        return func

    return decorator

# =============================================================================

@addToModule(hou)
def isRendering():
    """Check if Houdini is rendering or not."""
    return _cpp_methods.isRendering()


@addToModule(hou)
def getGlobalVariableNames(dirty=False):
    """Get a tuple of all global variable names.

    If dirty is True, return only 'dirty' variables.  A dirty variable is a
    variable that has been created or modified but not updated throughout the
    session by something like the 'varchange' hscript command.

    """
    # Get all the valid variable names.
    var_names = _cpp_methods.getGlobalVariables(dirty)

    # Remove any empty names.
    return _cleanStringValues(var_names)


@addToModule(hou)
def getVariable(name):
    """Returns the value of the named variable.

    Returns None if no such variable exists.

    """
    # Since Houdini stores all variable values as strings we use the ast module
    # to handle parsing the string and returning the proper data type.
    import ast

    # If the variable name isn't in list of variables, return None.
    if name not in getVariableNames():
        return None

    # Get the value of the variable.
    value = _cpp_methods.getVariable(name)

    # Try to convert it to the proper Python type.
    try:
        return ast.literal_eval(value)

    # Except against common parsing/evaluating errors and return the raw
    # value since the type will be a string.
    except SyntaxError:
        return value

    except ValueError:
        return value


@addToModule(hou)
def getVariableNames(dirty=False):
    """Get a tuple of all available variable names.

    If dirty is True, return only 'dirty' variables.  A dirty variable is a
    variable that has been created or modified but not updated throughout the
    session by something like the 'varchange' hscript command.

    """
    # Get all the valid variable names.
    var_names = _cpp_methods.getVariableNames(dirty)

    # Remove any empty names.
    return _cleanStringValues(var_names)


@addToModule(hou)
def setVariable(name, value, local=False):
    """Set a variable."""
    _cpp_methods.setVariable(name, str(value), local)


@addToModule(hou)
def unsetVariable(name):
    """Unset a variable.

    This function will do nothing if no such variable exists.

    """
    _cpp_methods.unsetVariable(name)


@addToModule(hou)
def varChange():
    """Cook any operators using changed variables.

    When a variable's value changes, the OPs which reference that variable are
    not automatically cooked. Use this function to cook all OPs when a variable
    they use changes.

    """
    _cpp_methods.varChange()


@addToModule(hou)
def expandRange(pattern):
    """Expand a string range into a tuple of values.

    This function will do string range expansion.  Examples include '0-15',
    '0 4 10-100', '1-100:2', etc.  See Houdini's documentation about geometry
    groups for more information. Wildcards are not supported.

    """
    return tuple(_cpp_methods.expandRange(pattern))


@addToClass(hou.Geometry)
def isReadOnly(self):
    """Check if the geometry is read only."""
    # Get a GU Detail Handle for the geometry.
    handle = self._guDetailHandle()
    # Check if the handle is read only.
    result = handle.isReadOnly()
    # Destroy the handle.
    handle.destroy()

    return result


@addToClass(hou.Geometry)
def numPoints(self):
    """Get the number of points in the geometry.

    This should be quicker than len(hou.Geometry.iterPoints()) since it uses
    the 'pointcount' intrinsic value from the detail.

    """
    return self.intrinsicValue("pointcount")


@addToClass(hou.Geometry)
def numPrims(self):
    """Get the number of primitives in the geometry.

    This should be quicker than len(hou.Geometry.iterPrims()) since it uses
    the 'primitivecount' intrinsic value from the detail.

    """
    return self.intrinsicValue("primitivecount")


@addToClass(hou.Geometry)
def numVertices(self):
    """Get the number of vertices in the geometry."""
    return self.intrinsicValue("vertexcount")


@addToClass(hou.Geometry)
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


@addToClass(hou.Geometry)
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
    attrib_owner = _getAttribOwner(attrib_type)

    _cpp_methods.sortByAttribute(
        self,
        attrib_owner,
        attrib_name,
        tuple_index,
        reverse
    )


@addToClass(hou.Geometry)
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


@addToClass(hou.Geometry)
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
        arr = _buildCDoubleArray(values)

        _cpp_methods.sortByValues(self, 0, arr)

    elif geometry_type == hou.geometryType.Primitives:
        # Check we have enough primitives.
        if len(values) != len(self.iterPrims()):
            raise hou.OperationFailed(
                "Length of values must equal the number of prims."
            )

        # Construct a ctypes double array to pass the values.
        arr = _buildCDoubleArray(values)

        _cpp_methods.sortByValues(self, 1, arr)

    else:
        raise hou.OperationFailed(
            "Geometry type must be points or primitives."
        )


@addToClass(hou.Geometry)
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


@addToClass(hou.Geometry)
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


@addToClass(hou.Geometry)
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


@addToClass(hou.Geometry)
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


@addToClass(hou.Geometry)
def sortByVertexOrder(self):
    """Sorts points to match the order of the vertices on the primitives.

    If you have a curve whose point numbers do not increase along the curve,
    this will reorder the point numbers so they match the curve direction.

    """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    _cpp_methods.sortByVertexOrder(self)


@addToClass(hou.Geometry)
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


@addToClass(hou.Geometry)
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


@addToClass(hou.Geometry)
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

    return _getPointsFromList(self, point_nums)


@addToClass(hou.Geometry)
def mergePointGroup(self, group):
    """Merges points from a group into this detail. """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    _cpp_methods.mergePointGroup(self, group.geometry(), group.name())


@addToClass(hou.Geometry)
def mergePoints(self, points):
    """Merge a list of points from a detail into this detail."""
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    arr = _buildCIntArray([point.number() for point in points])

    _cpp_methods.mergePoints(self, points[0].geometry(), arr, len(arr))


@addToClass(hou.Geometry)
def mergePrimGroup(self, group):
    """Merges prims from a group into this detail."""
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    _cpp_methods.mergePrimGroup(self, group.geometry(), group.name())


@addToClass(hou.Geometry)
def mergePrims(self, prims):
    """Merges a list of prims from a detail into this detail."""
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    arr = _buildCIntArray([prim.number() for prim in prims])

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
    target_owner = _getAttribOwnerFromGeometryType(type(target_element))
    source_owner = _getAttribOwnerFromGeometryType(type(source_element))

    # Get the attribute names, ensuring we only use attributes on the
    # source's geometry.
    attrib_names = [
        attrib.name() for attrib in source_attribs
        if _getAttribOwner(attrib.type()) == source_owner and
        attrib.geometry().sopNode() == source_geometry.sopNode()
    ]

    # Construct a ctypes string array to pass the strings.
    arr = _buildCStringArray(attrib_names)

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


@addToClass(hou.Point, name="copyAttribValues")
def copyPointAttributeValues(self, source_point, attributes):
    """Copy attribute values from the source point to this point.

    If the attributes do not exist on the destination detail they will be
    created.

    This function is deprecated.  Use copyAttributeValues instead.

    """
    copyAttributeValues(source_point, attributes, self)


@addToClass(hou.Prim, name="copyAttribValues")
def copyPrimAttributeValues(self, source_prim, attributes):
    """Copy attribute values from the source primitive to this primitive.

    If the attributes do not exist on the destination primitive they will be
    created.

    This function is deprecated.  Use copyAttributeValues instead.

    """
    copyAttributeValues(source_prim, attributes, self)


@addToClass(hou.Prim)
def pointAdjacentPolygons(self):
    """Get all prims that are adjacent to this prim through a point."""
    # Get the geometry this primitive belongs to.
    geometry = self.geometry()

    # Get a list of prim numbers that are point adjacent this prim.
    result = _cpp_methods.pointAdjacentPolygons(geometry, self.number())

    return _getPrimsFromList(geometry, result)


@addToClass(hou.Prim)
def edgeAdjacentPolygons(self):
    """Get all prims that are adjacent to this prim through an edge."""
    # Get the geometry this primitive belongs to.
    geometry = self.geometry()

    # Get a list of prim numbers that are edge adjacent this prim.
    result = _cpp_methods.edgeAdjacentPolygons(geometry, self.number())

    return _getPrimsFromList(geometry, result)


@addToClass(hou.Point)
def connectedPrims(self):
    """Get all primitives that reference this point."""
    # Get the geometry the point belongs to.
    geometry = self.geometry()

    # Get a list of primitive numbers that reference the point.
    result = _cpp_methods.connectedPrims(geometry, self.number())

    return _getPrimsFromList(geometry, result)


@addToClass(hou.Point)
def connectedPoints(self):
    """Get all points that share an edge with this point."""
    # Get the geometry the point belongs to.
    geometry = self.geometry()

    # Get a list of point numbers that are connected to the point.
    result = _cpp_methods.connectedPoints(geometry, self.number())

    # Glob for the points and return them.
    return _getPointsFromList(geometry, result)


@addToClass(hou.Point)
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


@addToClass(hou.Attrib)
def stringTableIndices(self):
    """Return at tuple of string attribute table indices.

    String attributes are stored using integers referencing a table of
    strings.  This function will return a list of table indices for each
    element.

    """
    if self.dataType() != hou.attribData.String:
        raise hou.OperationFailed("Attribute must be a string.")

    # Get the corresponding attribute type id.
    attrib_owner = _getAttribOwner(self.type())

    return tuple(_cpp_methods.getStringTableIndices(self.geometry(), attrib_owner, self.name()))


@addToClass(hou.Geometry)
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


@addToClass(hou.Geometry)
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
    arr = _buildCStringArray(values)

    _cpp_methods.setVertexStringAttribValues(
        self,
        name,
        arr,
        len(values)
    )


@addToClass(hou.Geometry)
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
        _getAttribOwner(attribute.type()),
        name,
        value,
        group_name
    )


@addToClass(hou.Geometry)
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
        _getAttribOwner(attribute.type()),
        name,
        value,
        group_name
    )


@addToClass(hou.Face)
def hasEdge(self, point1, point2):
    """Test if this face has an edge between two points."""
    # Test for the edge.
    return _cpp_methods.hasEdge(
        self.geometry(),
        self.number(),
        point1.number(),
        point2.number()
    )


@addToClass(hou.Face)
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


@addToClass(hou.Face)
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


@addToClass(hou.Face)
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


@addToClass(hou.Face)
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


@addToClass(hou.Prim)
def baryCenter(self):
    """Get the barycenter of this primitive."""
    # Get the Position3D object representing the barycenter.
    pos = _cpp_methods.baryCenter(self.geometry(), self.number())

    # Construct a vector and return it.
    return hou.Vector3(pos.x, pos.y, pos.z)


@addToClass(hou.Prim, name="area")
def primitiveArea(self):
    """Get the area of this primitive."""
    return self.intrinsicValue("measuredarea")


@addToClass(hou.Prim)
def perimeter(self):
    """Get the perimeter of this primitive."""
    return self.intrinsicValue("measuredperimeter")


@addToClass(hou.Prim)
def volume(self):
    """Get the volume of this primitive."""
    return self.intrinsicValue("measuredvolume")


@addToClass(hou.Prim, name="reverse")
def reversePrim(self):
    """Reverse the vertex order of this primitive."""
    geometry = self.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    return _cpp_methods.reversePrimitive(geometry, self.number())


@addToClass(hou.Prim)
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


@addToClass(hou.Prim, name="boundingBox")
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


@addToClass(hou.Geometry)
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


@addToClass(hou.Geometry, name="addPointNormals")
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


@addToClass(hou.Geometry, name="addPointVelocity")
def addPointVelocityAttribute(self):
    """Add point velocity to the geometry."""
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    success = _cpp_methods.addVelocityAttribute(self)

    if success:
        return self.findPointAttrib("v")

    raise hou.OperationFailed("Could not add velocity attribute.")


@addToClass(hou.Geometry)
def addColorAttribute(self, attrib_type):
    """Add a color (Cd) attribute to the geometry.

    Point, primitive and vertex colors are supported.

    """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    if attrib_type == hou.attribType.Global:
        raise hou.TypeError("Invalid attribute type.")

    owner = _getAttribOwner(attrib_type)

    # Try to add the Cd attribute.
    success = _cpp_methods.addDiffuseAttribute(self, owner)

    if success:
        return _findAttrib(self, attrib_type, "Cd")

    # We didn't create an attribute, so throw an exception.
    raise hou.OperationFailed("Could not add Cd attribute.")


@addToClass(hou.Geometry)
def convex(self, max_points=3):
    """Convex the geometry into polygons with a certain number of points.

    This operation is similar to using the Divide SOP and setting the 'Maximum
    Edges'.

    """
    # Make sure the geometry is not read only.
    if self.isReadOnly():
        raise hou.GeometryPermissionError()

    _cpp_methods.convexPolygons(self, max_points)


@addToClass(hou.Geometry)
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


@addToClass(hou.Geometry)
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
    attrib_owner = _getAttribOwner(attrib_type)

    _cpp_methods.destroyEmptyGroups(self, attrib_owner)


@addToClass(hou.Geometry)
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


@addToClass(hou.Geometry)
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


@addToClass(hou.Geometry)
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


@addToClass(hou.Geometry)
def renameGroup(self, group, new_name):
    """Rename this group."""
    # Make sure the geometry is not read only.
    if isReadOnly(self):
        raise hou.GeometryPermissionError()

    # Ensure the new group doesn't have the same name.
    if new_name == group.name():
        raise hou.OperationFailed("Cannot rename to same name.")

    group_type = _getGroupType(group)

    success = _cpp_methods.renameGroup(
        self,
        group.name(),
        new_name,
        group_type
    )

    if success:
        return _findGroup(self, group_type, new_name)

    else:
        return None


@addToClass(hou.PointGroup, hou.PrimGroup, hou.EdgeGroup, name="boundingBox")
def groupBoundingBox(self):
    """Get the bounding box of this group."""
    group_type = _getGroupType(self)

    # Calculate the bounds for the group.
    bounds = _cpp_methods.groupBoundingBox(
        self.geometry(),
        group_type,
        self.name()
    )

    return hou.BoundingBox(*bounds)


@addToClass(hou.EdgeGroup, hou.PointGroup, hou.PrimGroup, name="__len__")
@addToClass(hou.EdgeGroup, hou.PointGroup, hou.PrimGroup, name="size")
def groupSize(self):
    """Get the number of elements in this group."""
    geometry = self.geometry()

    group_type = _getGroupType(self)

    return _cpp_methods.groupSize(geometry, self.name(), group_type)


@addToClass(hou.PointGroup, name="toggle")
def togglePoint(self, point):
    """Toggle group membership for a point.

    If the point is a part of the group, it will be removed.  If it isn't, it
    will be added.

    """
    geometry = self.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    group_type = _getGroupType(self)

    _cpp_methods.toggleMembership(
        geometry,
        self.name(),
        group_type,
        point.number()
    )


@addToClass(hou.PrimGroup, name="toggle")
def togglePrim(self, prim):
    """Toggle group membership for a primitive.

    If the primitive is a part of the group, it will be removed.  If it isnt,
    it will be added.

    """
    geometry = self.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    group_type = _getGroupType(self)

    _cpp_methods.toggleMembership(
        geometry,
        self.name(),
        group_type,
        prim.number()
    )


@addToClass(hou.EdgeGroup, hou.PointGroup, hou.PrimGroup)
def toggleEntries(self):
    """Toggle group membership for all elements in the group.

    All elements not in the group will be added to it and all that were in it
    will be removed.

    """
    geometry = self.geometry()

    # Make sure the geometry is not read only.
    if geometry.isReadOnly():
        raise hou.GeometryPermissionError()

    group_type = _getGroupType(self)

    _cpp_methods.toggleEntries(geometry, self.name(), group_type)


@addToClass(hou.PointGroup, name="copy")
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

    attrib_owner = _getGroupAttribOwner(self)

    # Copy the group.
    _cpp_methods.copyGroup(geometry, attrib_owner, self.name(), new_group_name)

    # Return the new group.
    return geometry.findPointGroup(new_group_name)


@addToClass(hou.PrimGroup, name="copy")
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

    attrib_owner = _getGroupAttribOwner(self)

    # Copy the group.
    _cpp_methods.copyGroup(geometry, attrib_owner, self.name(), new_group_name)

    # Return the new group.
    return geometry.findPrimGroup(new_group_name)


@addToClass(hou.PointGroup, name="containsAny")
def pointGroupContainsAny(self, group):
    """Returns whether or not any points in the group are in this group."""
    geometry = self.geometry()

    group_type = _getGroupType(self)

    return _cpp_methods.containsAny(geometry, self.name(), group.name(), group_type)


@addToClass(hou.PrimGroup, name="containsAny")
def primGroupContainsAny(self, group):
    """Returns whether or not any prims in the group are in this group."""
    geometry = self.geometry()

    group_type = _getGroupType(self)

    return _cpp_methods.containsAny(geometry, self.name(), group.name(), group_type)


@addToClass(hou.PrimGroup)
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


@addToClass(hou.PointGroup)
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


@addToClass(hou.Geometry)
def hasUngroupedPoints(self):
    """Check if the geometry has ungrouped points."""
    return _cpp_methods.hasUngroupedPoints(self)


@addToClass(hou.Geometry)
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


@addToClass(hou.Geometry)
def hasUngroupedPrims(self):
    """Check if the geometry has ungrouped primitives."""
    return _cpp_methods.hasUngroupedPrims(self)


@addToClass(hou.Geometry)
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


@addToClass(hou.BoundingBox)
def isInside(self, bbox):
    """Determine if this bounding box is totally enclosed by another box."""
    return _cpp_methods.isInside(self, bbox)


@addToClass(hou.BoundingBox)
def intersects(self, bbox):
    """Determine if the bounding boxes intersect."""
    return _cpp_methods.intersects(self, bbox)


@addToClass(hou.BoundingBox)
def computeIntersection(self, bbox):
    """Compute the intersection of two bounding boxes.

    This function changes the bounds of this box to be those of the
    intersection of this box and the supplied box.

    """
    return _cpp_methods.computeIntersection(self, bbox)


@addToClass(hou.BoundingBox)
def expandBounds(self, dltx, dlty, dltz):
    """Expand the min and max bounds in each direction by the axis delta."""
    _cpp_methods.expandBounds(self, dltx, dlty, dltz)


@addToClass(hou.BoundingBox)
def addToMin(self, vec):
    """Add values to the minimum bounds of this bounding box."""
    _cpp_methods.addToMin(self, vec)

@addToClass(hou.BoundingBox)
def addToMax(self, vec):
    """Add values to the maximum bounds of this bounding box."""
    _cpp_methods.addToMax(self, vec)


@addToClass(hou.BoundingBox, name="area")
def boundingBoxArea(self):
    """Calculate the area of this bounding box."""
    return _cpp_methods.boundingBoxArea(self)


@addToClass(hou.BoundingBox, name="volume")
def boundingBoxVolume(self):
    """Calculate the volume of this bounding box."""
    return _cpp_methods.boundingBoxVolume(self)


@addToClass(hou.ParmTuple)
def isVector(self):
    """Check if the tuple is a vector parameter."""
    parm_template = self.parmTemplate()

    return parm_template.namingScheme() == hou.parmNamingScheme.XYZW


@addToClass(hou.ParmTuple)
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


@addToClass(hou.ParmTuple)
def isColor(self):
    """Check if the parameter is a color parameter."""
    parm_template = self.parmTemplate()

    return parm_template.look() == hou.parmLook.ColorSquare


@addToClass(hou.ParmTuple)
def evalAsColor(self):
    """Evaluate a color parameter and return a hou.Color object."""
    if not self.isColor():
        raise hou.Error("Parameter is not a color chooser")

    return hou.Color(self.eval())


@addToClass(hou.Parm)
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


@addToClass(hou.Parm)
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


@addToClass(hou.Parm)
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


@addToClass(hou.Parm, hou.ParmTuple)
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


@addToClass(hou.Parm)
def getMultiParmInstancesPerItem(self):
    """Get the number of items in a multiparm instance."""
    return self.tuple().getMultiParmInstancesPerItem()


@addToClass(hou.ParmTuple, name="getMultiParmInstancesPerItem")
def getTupleMultiParmInstancesPerItem(self):
    """Get the number of items in a multiparm instance."""
    if not self.isMultiParm():
        raise hou.OperationFailed("Parameter tuple is not a multiparm.")

    return _cpp_methods.getMultiParmInstancesPerItem(
        self.node(),
        self.name()
    )


@addToClass(hou.Parm)
def getMultiParmStartOffset(self):
    """Get the start offset of items in the multiparm."""
    return self.tuple().getMultiParmStartOffset()


@addToClass(hou.ParmTuple, name="getMultiParmStartOffset")
def getTupleMultiParmStartOffset(self):
    """Get the start offset of items in the multiparm."""
    if not self.isMultiParm():
        raise hou.OperationFailed("Parameter tuple is not a multiparm.")

    return _cpp_methods.getMultiParmStartOffset(
        self.node(),
        self.name()
    )


@addToClass(hou.Parm)
def getMultiParmInstanceIndex(self):
    """Get the multiparm instance indices for this parameter.

    If this parameter is part of a multiparm, then its index in the multiparm
    array will be returned as a tuple.  If the multiparm is nested in other
    multiparms, then the resulting tuple will have multiple entries (with
    the outer multiparm listed first, and the inner-most multiparm last in
    the tuple.

    """
    return self.tuple().getMultiParmInstanceIndex()


@addToClass(hou.ParmTuple, name="getMultiParmInstanceIndex")
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


@addToClass(hou.Parm, hou.ParmTuple)
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

@addToClass(hou.Parm, hou.ParmTuple)
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


@addToClass(hou.Node)
def disconnectAllInputs(self):
    """Disconnect all of this node's inputs."""
    connections = self.inputConnections()

    for connection in reversed(connections):
        self.setInput(connection.inputIndex(), None)


@addToClass(hou.Node)
def disconnectAllOutputs(self):
    """Disconnect all of this node's outputs. """
    connections = self.outputConnections()

    for connection in connections:
        connection.outputNode().setInput(connection.inputIndex(), None)


@addToClass(hou.Node)
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


@addToClass(hou.Node)
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


@addToClass(hou.Node)
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


@addToClass(hou.Node)
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


@addToClass(hou.Node)
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


@addToClass(hou.Node)
def isCompiled(self):
    """Check if this node is compiled.

    This check can be used to determine if a node is compiled for Orbolt,
    or has somehow become compiled on its own.

    """
    return _cpp_methods.isCompiled(self)


@addToClass(hou.Node)
def authorName(self):
    """Get the name of the node creator."""
    author = _cpp_methods.getAuthor(self)

    # Remove any machine name from the user name.
    return author.split('@')[0]


@addToClass(hou.NodeType)
def setIcon(self, icon_name):
    """Set the node type's icon name."""
    return _cpp_methods.setIcon(self, icon_name)


@addToClass(hou.NodeType)
def setDefaultIcon(self):
    """Set this node type's icon name to its default value."""
    return _cpp_methods.setDefaultIcon(self)


@addToClass(hou.NodeType)
def isPython(self):
    """Check if this node type represents a Python operator."""
    return _cpp_methods.isPython(self)


@addToClass(hou.NodeType)
def isSubnetType(self):
    """Check if this node type is the primary subnet operator for the table.

    This is the operator type which is used as a default container for nodes.

    """
    return _cpp_methods.isSubnetType(self)


@addToClass(hou.Vector3)
def componentAlong(self, vector):
    """Calculate the component of this vector along another vector."""
    # The component of vector A along B is: A dot (unit vector // to B).
    return self.dot(vector.normalized())


@addToClass(hou.Vector3)
def project(self, vector):
    """Calculate the vector projection of this vector onto another vector.

    This is an orthogonal projection of this vector onto a straight line
    parallel to the supplied vector.

    """
    # The vector cannot be the zero vector.
    if vector == hou.Vector3():
        raise hou.OperationFailed("Supplied vector must be non-zero.")

    return vector.normalized() * self.componentAlong(vector)


@addToClass(hou.Vector2, hou.Vector3, hou.Vector4)
def isNan(self):
    """Check if this vector contains NaNs."""
    import math

    # Iterate over each component.
    for i in range(len(self)):
        # If this component is a NaN, return True.
        if math.isnan(self[i]):
            return True

    # Didn't find any NaNs, so return False.
    return False


@addToClass(hou.Vector3)
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


@addToClass(hou.Matrix3, hou.Matrix4)
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


@addToClass(hou.Matrix4)
def setTranslates(self, translates):
    """Set the translation values of this matrix."""
    # The translations are stored in the first 3 columns of the last row of the
    # matrix.  To set the values we just need to set the corresponding columns
    # to the matching components in the vector.
    for i in range(3):
        self.setAt(3, i, translates[i])


@addToModule(hou.hmath)
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
@addToModule(hou.hmath)
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


@addToClass(hou.Node)
def isDigitalAsset(self):
    """Determine if this node is a digital asset.

    A node is a digital asset if its node type has a hou.HDADefinition.

    """
    return self.type().definition() is not None


@addToModule(hou.hda)
def metaSource(file_path):
    """Get the meta install location for the file.

    This function determines where the specified .otl file is installed to in
    the current session.  Examples include "Scanned OTL Directories", "Current
    Hip File", "Fallback Libraries" or specific OPlibraries files.

    """
    if file_path not in hou.hda.loadedFiles():
        return None

    return _cpp_methods.getMetaSource(file_path)


@addToClass(hou.HDADefinition, name="metaSource")
def getMetaSource(self):
    """Get the meta install location of this asset definition.

    This function determines where the contained .otl file is installed to in
    the current session.  Examples include "Scanned OTL Directories", "Current
    Hip File", "Fallback Libraries" or specific OPlibraries files.

    """
    return hou.hda.metaSource(self.libraryFilePath())


@addToModule(hou.hda)
def removeMetaSource(meta_source):
    """Attempt to remove a meta source.

    Removing a meta source will uninstall the libraries it was responsible for.

    """
    return _cpp_methods.removeMetaSource(meta_source)


@addToModule(hou.hda)
def librariesInMetaSource(meta_source):
    """Get a list of library paths in a meta source."""
    # Get the any libraries in the meta source.
    result = _cpp_methods.getLibrariesInMetaSource(meta_source)

    # Return a tuple of the valid values.
    return _cleanStringValues(result)


@addToClass(hou.HDADefinition)
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

