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
import inlinecpp

# =============================================================================

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
getGlobalVariableNames(int dirty=0)
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

#if (UT_MAJOR_VERSION_INT >= 17 )
    UTarrayToStdVectorOfStrings(names, result);
#else
    names.toStdVectorOfStrings(result);
#endif
    // Check for an empty vector.
    validateStringVector(result);

    return result;
}
""",

"""
char *
getVariableValue(const char *name)
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

#if (UT_MAJOR_VERSION_INT >= 17 )
    UTarrayToStdVectorOfStrings(names, result);
#else
    names.toStdVectorOfStrings(result);
#endif

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
emitVarChange()
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
getNodeAuthor(OP_Node *node)
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
sortGeometryByAttribute(GU_Detail *gdp,
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
sortGeometryAlongAxis(GU_Detail *gdp, int attribute_type, int axis)
{
    GA_AttributeOwner owner = static_cast<GA_AttributeOwner>(attribute_type);

    // Convert the int value to the axis type.
    GU_AxisType axis_type = static_cast<GU_AxisType>(axis);

    switch(owner)
    {
        case GA_ATTRIB_POINT:
            gdp->sortPointList(axis_type);
            break;

        case GA_ATTRIB_PRIMITIVE:
            gdp->sortPrimitiveList(axis_type);
            break;
    }
}
""",

"""
void
sortGeometryRandomly(GU_Detail *gdp, int attribute_type, float seed)
{
    GA_AttributeOwner owner = static_cast<GA_AttributeOwner>(attribute_type);

    switch(owner)
    {
        case GA_ATTRIB_POINT:
            gdp->sortPointList(seed);
            break;

        case GA_ATTRIB_PRIMITIVE:
            gdp->sortPrimitiveList(seed);
            break;
    }
}
""",

"""
void
shiftGeometry(GU_Detail *gdp, int attribute_type, int offset)
{
    GA_AttributeOwner owner = static_cast<GA_AttributeOwner>(attribute_type);

    switch(owner)
    {
        case GA_ATTRIB_POINT:
            gdp->shiftPointList(offset);
            break;

        case GA_ATTRIB_PRIMITIVE:
            gdp->shiftPrimitiveList(offset);
            break;
    }
}
""",

"""
void
reverseSortGeometry(GU_Detail *gdp, int attribute_type)
{
    GA_AttributeOwner owner = static_cast<GA_AttributeOwner>(attribute_type);

    switch(owner)
    {
        case GA_ATTRIB_POINT:
            gdp->reversePointList();
            break;

        case GA_ATTRIB_PRIMITIVE:
            gdp->reversePrimitiveList();
            break;
    }
}
""",

"""
void
sortGeometryByProximity(GU_Detail *gdp, int attribute_type, const UT_Vector3D *point)
{
    UT_Vector3                  pos(*point);

    GA_AttributeOwner owner = static_cast<GA_AttributeOwner>(attribute_type);

    switch(owner)
    {
        case GA_ATTRIB_POINT:
            gdp->proximityToPointList(pos);
            break;

        case GA_ATTRIB_PRIMITIVE:
            gdp->proximityToPrimitiveList(pos);
            break;
    }
}
""",

"""
void
sortGeometryByVertexOrder(GU_Detail *gdp)
{
    gdp->sortByVertexOrder();
}
""",

"""
void
sortGeometryByValues(GU_Detail *gdp, int attribute_type, fpreal *values)
{
    GA_AttributeOwner owner = static_cast<GA_AttributeOwner>(attribute_type);

    switch(owner)
    {
        case GA_ATTRIB_POINT:
            gdp->sortPointList(values);
            break;

        case GA_ATTRIB_PRIMITIVE:
            gdp->sortPrimitiveList(values);
            break;
    }
}
""",

"""
void
setNodeTypeIcon(OP_Operator *op, const char *icon_name)
{
    op->setIconName(icon_name);
}
""",

"""
void
setNodeTypeDefaultIcon(OP_Operator *op)
{
    op->setDefaultIconName();
}
""",

"""
bool
isNodeTypeSubnetType(OP_Operator *op)
{
    return op->getIsPrimarySubnetType();
}
""",

"""
bool
isNodeTypePythonType(OP_Operator *op)
{
    return op->getScriptIsPython();
}
""",

"""
void
createPointAtPosition(GU_Detail *gdp, UT_Vector3D *position)
{
    GA_Offset                   ptOff;

    // Add a new point.
    ptOff = gdp->appendPointOffset();

    // Set the position for the point.
    gdp->setPos3(ptOff, *position);

}
""",

"""
void
createNPoints(GU_Detail *gdp, int npoints)
{
    GA_Offset                   ptOff;

    // Build a block of points.
    ptOff = gdp->appendPointBlock(npoints);
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
faceHasEdge(const GU_Detail *gdp,
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
deleteVertexFromFace(GU_Detail *gdp, unsigned prim_num, unsigned idx)
{
    GEO_Face                    *face;

    face = (GEO_Face *)gdp->getPrimitiveByIndex(prim_num);

    face->deleteVertex(idx);
}
""",

"""
void
setFaceVertexPoint(GU_Detail *gdp, unsigned prim_num, unsigned idx, unsigned pt_num)
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
primitiveBaryCenter(const GU_Detail *gdp, unsigned prim_num)
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

    prim->reverse();
}
""",

"""
void
makePrimitiveUnique(GU_Detail *gdp, unsigned prim_num)
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
toggleGroupMembership(GU_Detail *gdp,
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
toggleGroupEntries(GU_Detail *gdp, const char *group_name, int group_type)
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
groupsShareElements(const GU_Detail *gdp,
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
clipGeometry(GU_Detail *gdp,
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
boundingBoxisInside(const UT_BoundingBoxD *bbox1, const UT_BoundingBoxD *bbox2)
{
    return bbox1->isInside(*bbox2);
}
""",

"""
bool
boundingBoxesIntersect(UT_BoundingBoxD *bbox1, const UT_BoundingBoxD *bbox2)
{
    return bbox1->intersects(*bbox2);
}
""",

"""
bool
computeBoundingBoxIntersection(UT_BoundingBoxD *bbox1, const UT_BoundingBoxD *bbox2)
{
    return bbox1->computeIntersection(*bbox2);
}
""",

"""
void
expandBoundingBoxBounds(UT_BoundingBoxD *bbox, float dltx, float dlty, float dltz)
{
    bbox->expandBounds(dltx, dlty, dltz);
}
""",

"""
void
addToBoundingBoxMin(UT_BoundingBoxD *bbox, const UT_Vector3D *vec)
{
    bbox->addToMin(*vec);
}
""",

"""
void
addToBoundingBoxMax(UT_BoundingBoxD *bbox, const UT_Vector3D *vec)
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

#if (UT_MAJOR_VERSION_INT >= 17 )
    UTarrayToStdVector(indices, result);
#else
    indices.toStdVector(result);
#endif
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
buildLookatMatrix(UT_DMatrix3 *mat,
            const UT_Vector3D *from,
            const UT_Vector3D *to,
            const UT_Vector3D *up)
{
    mat->lookat(*from, *to, *up);
}
""",

"""
void
vector3GetDual(const UT_Vector3D *vec, UT_DMatrix3 *mat)
{
    vec->getDual(*mat);
}
""",

"""
const char *
getMetaSourceForPath(const char *filename)
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
cpp_methods = inlinecpp.createLibrary(
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
#include <UT/UT_Version.h>
#include <UT/UT_WorkArgs.h>

#if (UT_MAJOR_VERSION_INT >= 17)
    #include <UT/UT_StdUtil.h>
#endif

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


