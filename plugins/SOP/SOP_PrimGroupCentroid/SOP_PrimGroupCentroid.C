/*
 * Produced by:
 *      Graham Thompson
 *      captainhammy@gmail.com
 *      www.captainhammy.com
 *
 * Description:
 *      Create points at the centroids of primitive groups, named primitives
 *      of classes.  If the second input is connected, use those points to
 *      transform the geometry.
 *
 * Name: SOP_PrimGroupCentroid.C
 *
*/

#include "SOP_PrimGroupCentroid.h"

#include <CH/CH_Manager.h>
#include <GA/GA_AttributeRefMap.h>
#include <GA/GA_WeightedSum.h>
#include <OP/OP_Operator.h>
#include <OP/OP_OperatorTable.h>
#include <PRM/PRM_Include.h>
#include <UT/UT_DSOVersion.h>
#include <UT/UT_WorkArgs.h>

void
newSopOperator(OP_OperatorTable *table)
{
    table->addOperator(
        new OP_Operator("com.houdinitoolbox::primgroupcentroid::1",
                        "HT Primitive Group Centroid",
                        SOP_PrimGroupCentroid::myConstructor,
                        SOP_PrimGroupCentroid::myTemplateList,
                        1,
                        2,
                        0)
    );
}

OP_Node *
SOP_PrimGroupCentroid::myConstructor(OP_Network *net,
                                     const char *name,
                                     OP_Operator *op)
{
    return new SOP_PrimGroupCentroid(net, name, op);
}

SOP_PrimGroupCentroid::SOP_PrimGroupCentroid(OP_Network *net,
                                             const char *name,
                                             OP_Operator *op):
    SOP_Node(net, name, op) {}

unsigned
SOP_PrimGroupCentroid::disableParms()
{
    fpreal                      t = CHgetEvalTime();
    unsigned                    changed;
    int                         mode;

    OP_Node                     *bind_input;

    // Partitioning mode.
    mode = MODE(t);

    // Try to get the 2nd input.
    bind_input = getInput(1);

    // Only use the 'group' parm when doing a group operation.
    changed = enableParm("group", mode == MODE_GROUP && bind_input == NULL);

    // Enable the 'store' parm when there is no 2nd input.
    changed += enableParm("store", bind_input == NULL);

    // Enable attribute and variable copying when not using a 2nd input.
    changed += enableParm("attributes", bind_input == NULL);
    changed += enableParm("copyvariables", bind_input == NULL);

    // Enable behavior parm when there is a 2nd input.
    changed += enableParm("behavior", bind_input != NULL);

    changed += enableParm("bind_attributes", bind_input != NULL);

    return changed;
}

bool
SOP_PrimGroupCentroid::validateAttrib(const GA_Attribute *attribute,
                                      void *data)
{
    // Extract the mode value.
    int mode = *((int *)data);

    UT_String attr_name;

    attr_name = attribute->getName();

    // Don't add 'name' when we are doing that type of operation.
    if (mode == MODE_NAME && attr_name == MODENAME_NAME)
        return false;

    // Don't add 'class' when we are doing that type of operation.
    if (mode == MODE_CLASS && attr_name == MODENAME_CLASS)
        return false;

    // Skip 'P'.
    if (attr_name == "P")
        return false;

    return true;
}

void
SOP_PrimGroupCentroid::buildMenu(void *data,
                                 PRM_Name *menu,
                                 int list_size,
                                 const PRM_SpareData *,
                                 const PRM_Parm *)
{
    fpreal                      t = CHgetEvalTime();
    int                         input_index, mode;

    GA_AttributeOwner           owner;

    OP_Node                     *bind_input;

    // Get the instance of the operator.
    SOP_PrimGroupCentroid *me = (SOP_PrimGroupCentroid *)data;

    // Get the operation mode.
    mode = me->MODE(t);

    // Try to get the 2nd input.
    bind_input = me->getInput(1);

    // Not binding, so use primitive attributes from input 0.
    if (bind_input == NULL)
    {
        owner = GA_ATTRIB_PRIMITIVE;
        input_index = 0;
    }
    // We are binding, so use point attributes from input 1.
    else
    {
        owner = GA_ATTRIB_POINT;
        input_index = 1;
    }

    // Populate the menu with the selected attributes.
    me->fillAttribNameMenu(menu,
                           100,
                           owner,
                           input_index,
                           &SOP_PrimGroupCentroid::validateAttrib,
                           &mode);
}

static PRM_Name names[] =
{
    PRM_Name("mode", "Mode"),
    PRM_Name("group", "Group"),
    PRM_Name("method", "Method"),
    PRM_Name("store", "Store Source Identifier"),
    PRM_Name("attributes", "Attributes to Copy"),
    PRM_Name("copyvariables", "Copy Local Variables"),
    PRM_Name("behavior", "Unmatched Behavior"),
    PRM_Name("bind_attributes", "Bind Attributes to Copy"),
};

static PRM_Default defaults[] =
{
    PRM_Default(1),
    PRM_Default(0),
    PRM_Default(0),
    PRM_Default(0),
    PRM_Default(0, ""),
    PRM_Default(1),
    PRM_Default(0),
    PRM_Default(0, ""),
};

static PRM_Name modeChoices[] =
{
    PRM_Name(MODENAME_GROUP, "Group"),
    PRM_Name(MODENAME_NAME, "Name"),
    PRM_Name(MODENAME_CLASS, "Class"),
    PRM_Name(0)
};

static PRM_Name methodChoices[] =
{
    PRM_Name("bary", "Barycenter"),
    PRM_Name("bbox", "Bounding Box"),
    PRM_Name("com", "Center of Mass"),
    PRM_Name(0)
};

static PRM_Name behaviorChoices[] =
{
    PRM_Name("keep", "Keep"),
    PRM_Name("destroy", "Destroy"),
    PRM_Name(0)
};

static PRM_ChoiceList modeChoiceMenu(
    (PRM_ChoiceListType)(PRM_CHOICELIST_EXCLUSIVE | PRM_CHOICELIST_REPLACE),
    modeChoices);

static PRM_ChoiceList methodChoiceMenu(
    (PRM_ChoiceListType)(PRM_CHOICELIST_EXCLUSIVE | PRM_CHOICELIST_REPLACE),
    methodChoices);

static PRM_ChoiceList attribMenu(
    (PRM_ChoiceListType)(PRM_CHOICELIST_TOGGLE),
    &SOP_PrimGroupCentroid::buildMenu);

static PRM_ChoiceList behaviorChoiceMenu(
    (PRM_ChoiceListType)(PRM_CHOICELIST_EXCLUSIVE | PRM_CHOICELIST_REPLACE),
    behaviorChoices);

PRM_Template
SOP_PrimGroupCentroid::myTemplateList[] = {
    PRM_Template(PRM_ORD, 1, &names[0], &defaults[0], &modeChoiceMenu),
    PRM_Template(PRM_STRING, 1, &names[1], &defaults[1], &SOP_Node::primGroupMenu),
    PRM_Template(PRM_ORD, 1, &names[2], &defaults[2], &methodChoiceMenu),
    PRM_Template(PRM_TOGGLE, 1, &names[3], &defaults[3]),
    PRM_Template(PRM_STRING, 1, &names[4], &defaults[4], &attribMenu),
    PRM_Template(PRM_TOGGLE, 1, &names[5], &defaults[5]),
    PRM_Template(PRM_ORD, 1, &names[6], &defaults[6], &behaviorChoiceMenu),
    PRM_Template(PRM_STRING, 1, &names[7], &defaults[7], &attribMenu),
    PRM_Template()
};

int
SOP_PrimGroupCentroid::buildAttribData(int mode,
                                       const GU_Detail *input_geo,
                                       UT_Array<GA_Range> &range_array,
                                       UT_StringArray &string_values,
                                       UT_IntArray &int_values)
{
    int                         unique_count;
    exint                       int_value;

    const GA_Attribute          *attrib;
    GA_Range                    pr_range;
    GA_ROAttributeRef           source_gah;

    UT_String                   attr_name, str_value;

    // Determine the attribute name to use.
    attr_name = (mode == MODE_NAME) ? MODENAME_NAME: MODENAME_CLASS;

    // Find the attribute.
    attrib = input_geo->findPrimitiveAttribute(attr_name);

    // If there is no attribute, add an error message and quit.
    if (!attrib)
    {
        addError(SOP_ATTRIBUTE_INVALID, attr_name);
        return 1;
    }

    source_gah = GA_ROAttributeRef(attrib);

    // If the 'name' attribute isn't a string, add an error and quit.
    if (mode == MODE_NAME && !source_gah.isString())
    {
        addError(SOP_ATTRIBUTE_INVALID, "'name' must be a string.");
        return 1;
    }
    // If the 'class' attribute isn't an int, add an error and quit.
    else if (mode == MODE_CLASS && !source_gah.isInt())
    {
        addError(SOP_ATTRIBUTE_INVALID, "'class' must be an integer.");
        return 1;
    }

    // The number of unique values for the attribute.
    unique_count = input_geo->getUniqueValueCount(source_gah);

    // Add all the ranges and unique values to the appropriate arrays.
    if (mode == MODE_NAME)
    {
        for (int idx=0; idx<unique_count; ++idx)
        {
            // Get the unique string value.
            str_value = input_geo->getUniqueStringValue(source_gah, idx);

            // Get the primitive range corresponding to that value.
            pr_range = input_geo->getRangeByValue(source_gah, str_value);

            // Add the range to the array.
            range_array.append(pr_range);

            // Add the string value to the string value list.
            string_values.append(str_value);
        }
    }
    else
    {
        for (int idx=0; idx<unique_count; ++idx)
        {
            // Get the unique integer value.
            int_value = input_geo->getUniqueIntegerValue(source_gah, idx);

            // Get the primitive range corresponding to that value.
            pr_range = input_geo->getRangeByValue(source_gah, int_value);

            // Add the range to the array.
            range_array.append(pr_range);

            // Add the integer value to the integer value list.
            int_values.append(int_value);
        }
    }

    // Return 0 for success.
    return 0;
}

int
SOP_PrimGroupCentroid::copyLocalVariables(const char *attr,
                                          const char *varname,
                                          void *data)
{
    const GA_Attribute          *attrib;

    GU_Detail                   *gdp;

    // Extract the detail.
    gdp = (GU_Detail *)data;

    // Try to find the attribute we are processing.
    attrib = gdp->findPointAttribute(attr);

    // If a point attribute exists then we can copy this variable mapping.
    if (attrib)
        gdp->addVariableName(attr, varname);

    return 1;
}

void
SOP_PrimGroupCentroid::buildRefMap(fpreal t,
                                   GA_AttributeRefMap &hmap,
                                   UT_String &pattern,
                                   const GU_Detail *input_geo,
                                   int mode,
                                   GA_AttributeOwner owner,
                                   bool copy=false)
{
    const GA_AttributeDict      *dict;
    GA_AttributeDict::iterator  a_it;

    const GA_Attribute          *attrib, *source_attrib;

    UT_String                   attr_name;
    UT_WorkArgs                 tokens;

    // If the pattern isn't empty then we should look for attributes to copy.
    if (pattern.length() > 0)
    {
        // Tokenize the pattern.
        pattern.tokenize(tokens, " ");

        // Select the appropriate attribute dictionary to use.
        if (owner == GA_ATTRIB_PRIMITIVE)
            dict = &input_geo->primitiveAttribs();

        // GA_ATTRIB_POINT
        else
            dict = &input_geo->pointAttribs();

        // Iterate over all the point attributes.
        for (a_it=dict->begin(GA_SCOPE_PUBLIC); !a_it.atEnd(); ++a_it)
        {
            // The current attribute.
            source_attrib = a_it.attrib();

            // Get the attribute name.
            attr_name = source_attrib->getName();

            // If the name doesn't match our pattern, skip it.
            if (!attr_name.matchPattern(tokens))
                continue;

            // Skip attribute names matching our current mode.  These are left
            // to the 'store' parm setting.
            if (mode == MODE_NAME and attr_name == MODENAME_NAME)
            {
                continue;
            }

            else if (mode == MODE_CLASS and attr_name == MODENAME_CLASS)
            {
                continue;
            }

            // Select the appropriate attribute type to search for.
            if (owner == GA_ATTRIB_PRIMITIVE)
            {
                // Try to find the point attribute on the geometry.
                attrib = gdp->findPointAttrib(*source_attrib);
            }

            // GA_ATTRIB_POINT
            else
            {
                // If we are doing points, we can ignore P.
                if (attr_name == "P")
                    continue;

                // Try to find the primitive attribute on the geometry.
                attrib = gdp->findPrimAttrib(*source_attrib);
            }

            // If it doesn't exist, create a new attribute.
            if (!attrib)
            {
                if (owner == GA_ATTRIB_PRIMITIVE)
                {
                    // Create a new point attribute on the current geometry
                    // that is the same as the source attribute.  Append it and
                    // the source to the map.
                    hmap.append(gdp->addPointAttrib(source_attrib),
                                source_attrib);
                }

                else
                {
                    // Create a new point attribute on the current geometry
                    // that is the same as the source attribute.  Append it and
                    // the source to the map.
                    hmap.append(gdp->addPrimAttrib(source_attrib),
                                source_attrib);
                }
            }
        }
    }

    // Copy local variables.
    if (copy)
    {
        // Traverse the variable names on the input geometry and attempt
        // to copy any that match to our new geometry.
        input_geo->traverseVariableNames(
            SOP_PrimGroupCentroid::copyLocalVariables,
            gdp
        );
    }
}

void
SOP_PrimGroupCentroid::buildGroupData(UT_String &pattern,
                                      const GU_Detail *input_geo,
                                      UT_Array<GA_Range> &range_array,
                                      UT_StringArray &string_values)
{
    GA_ElementGroupTable::ordered_iterator group_it;
    const GA_PrimitiveGroup     *group;
    GA_Range                    pr_range;

    UT_String                   group_name;
    UT_WorkArgs                 tokens;

    // Tokenize the pattern.
    pattern.tokenize(tokens);

    // Get all the primitive groups.
    const GA_ElementGroupTable &prim_groups = input_geo->primitiveGroups();

    // For each primitive group in order.
    for (group_it=prim_groups.obegin(); !group_it.atEnd(); ++group_it)
    {
        // Get the group.
        group = static_cast<GA_PrimitiveGroup *>(*group_it);

        // Ensure the group is valid.
        if (!group)
            continue;

        // Skip internal groups.
        if (group->getInternal())
            continue;

        // Check to see if this group name matches the pattern.
        group_name = group->getName();
        if (!group_name.matchPattern(tokens))
            continue;

        // Get a range for the primitives in the group.
        pr_range = input_geo->getPrimitiveRange(group);

        // Add the primitive range and the group name to the arrays.
        range_array.append(pr_range);
        string_values.append(group_name);
    }
}

void
SOP_PrimGroupCentroid::boundingBox(const GU_Detail *input_geo,
                                   GA_Range &pr_range,
                                   UT_Vector3 &pos)
{
    GA_Range                    pt_range;

    UT_BoundingBox              bbox;

    // Initialize the bounding box to contain nothing and have
    // no position.
    bbox.initBounds();

    pt_range = GA_Range(*input_geo, pr_range, GA_ATTRIB_POINT, GA_Range::primitiveref(), false);

    for (GA_Iterator it(pt_range.begin()); !it.atEnd(); ++it)
        bbox.enlargeBounds(input_geo->getPos3(*it));

    // Extract the center.
    pos = bbox.center();
}

void
SOP_PrimGroupCentroid::centerOfMass(const GU_Detail *input_geo,
                                    GA_Range &pr_range,
                                    UT_Vector3 &pos)
{
    fpreal                      area, total_area;

    const GEO_Primitive         *prim;

    // Set the position and total area to 0.
    pos.assign(0,0,0);
    total_area = 0;

    // Iterate over all the primitives in the range.
    for (GA_Iterator it(pr_range); !it.atEnd(); ++it)
    {
        // Get the primitive.
        prim = (const GEO_Primitive *) input_geo->getPrimitive(*it);

        // Calculate the area of the primitive.
        area = prim->calcArea();

        // Add the barycenter multiplied by the area to the position.
        pos += prim->baryCenter() * area;

        // Add this primitive's area to the total area.
        total_area += area;
    }

    // If the total area is not 0, divide the position by the total area.
    if (total_area)
        pos /= total_area;
}

void
SOP_PrimGroupCentroid::baryCenter(const GU_Detail *input_geo,
                                  GA_Range &pr_range,
                                  UT_Vector3 &pos)
{
    GA_Range                    pt_range;

    // Reset the position.
    pos.assign(0,0,0);

    pt_range = GA_Range(*input_geo, pr_range, GA_ATTRIB_POINT, GA_Range::primitiveref(), false);

    for (GA_Iterator it(pt_range.begin()); !it.atEnd(); ++it)
        pos += input_geo->getPos3(*it);

    // Store the average position for all the points we found.
    pos /= pt_range.getEntries();
}

void
SOP_PrimGroupCentroid::buildTransform(UT_Matrix4 &mat,
                                      const GU_Detail *input_geo,
                                      const UT_Vector3 centroid,
                                      GA_Offset ptOff)
{
    bool                        use_orient = false;
    fpreal                      pscale = 1;


    const GA_Attribute          *dir_attrib, *orient_attrib, *pscale_attrib, *rot_attrib, *scale_attrib, *trans_attrib, *up_attrib;

    GA_ROHandleF                pscale_h;
    GA_ROHandleV3               dir_h, scale_h, trans_h, up_h;
    GA_ROHandleV4               orient_h, rot_h;

    UT_Matrix4                  pre_xform, xform;
    UT_Quaternion               orient, rot;
    UT_Vector3                  dir, pt_pos, scale, trans, up;

    pt_pos = input_geo->getPos3(ptOff);

    pre_xform.identity();
    pre_xform.translate(centroid[0], centroid[1], centroid[2]);
    pre_xform.invert();

    // Try to find the specific attribute.
    orient_attrib = input_geo->findFloatTuple(GA_ATTRIB_POINT,
                                              GA_SCOPE_PUBLIC,
                                              "orient",
                                              4,
                                              4);

    // Found the attribute.
    if (orient_attrib)
    {
        orient_h.bind(orient_attrib);

        // Get the attribute value.
        UT_Vector4 value = orient_h.get(ptOff);

        // Construct a quaternion from the values.
        orient.assign(value[0], value[1], value[2], value[3]);
        use_orient = true;
    }

    // Try to find the 'trans' point attribute.
    trans_attrib = input_geo->findFloatTuple(GA_ATTRIB_POINT,
                                             GA_SCOPE_PUBLIC,
                                             "trans",
                                             3,
                                             3);

    // We found it.
    if (trans_attrib)
    {
        // Bind the handle to the attribute..
        trans_h.bind(trans_attrib);

        // Get the attribute value.
        trans = trans_h.get(ptOff);
    }
    else
        trans.assign(0, 0, 0);

    // Try to find the scale attribute.
    scale_attrib = input_geo->findFloatTuple(GA_ATTRIB_POINT,
                                             GA_SCOPE_PUBLIC,
                                             "scale",
                                             3,
                                             3);

    // Try to find the pscale attribute.
    pscale_attrib = input_geo->findFloatTuple(GA_ATTRIB_POINT,
                                              GA_SCOPE_PUBLIC,
                                              "pscale",
                                              1,
                                              1);

    //  If the pscale attribute exists, get the value.
    if (pscale_attrib)
    {
        pscale_h.bind(pscale_attrib);
        pscale = pscale_h.get(ptOff);
    }

    // The scale attribute exists.
    if (scale_attrib)
    {
        scale_h.bind(scale_attrib);
        // Get the scale.
        scale = scale_h.get(ptOff);
    }
    else
    {
        // Use a default scale.
        scale.assign(1, 1, 1);
    }

    // Try to find the specific attribute.
    rot_attrib = input_geo->findFloatTuple(GA_ATTRIB_POINT,
                                           GA_SCOPE_PUBLIC,
                                           "rot",
                                           4,
                                           4);

    // Found the attribute.
    if (rot_attrib)
    {
        rot_h.bind(rot_attrib);

        // Get the attribute value.
        UT_Vector4 value = rot_h.get(ptOff);

        // Construct a quaternion from the values.
        rot.assign(value[0], value[1], value[2], value[3]);
    }

    if (use_orient)
    {
        xform.instance(pt_pos,
                       dir,
                       pscale,
                       &scale,
                       &up,
                       &rot,
                       &trans,
                       &orient);
    }

    // Need to build the transform manually.
    else
    {
        // Try to find the point Normal attribute.
        dir_attrib = input_geo->findNormalAttribute(GA_ATTRIB_POINT);

        // We couldn't find the Normal attribute.
        if (!dir_attrib)
        {
            // Try to find the velocity attribute.
            dir_attrib = input_geo->findVelocityAttribute(GA_ATTRIB_POINT);
        }

        // We found either the normal or velocity attributes.
        if (!dir_attrib)
        {
            // Bind the direction handle to the found attribute.
            dir_h.bind(dir_attrib);

            dir = dir_h.get(ptOff);
        }
        // Default to the Z-axis.
        else
            dir = UT_Vector3(0,0,1);

        // Try to find the upvector ('up') attribute.
        up_attrib = input_geo->findFloatTuple(GA_ATTRIB_POINT,
                                              GA_SCOPE_PUBLIC,
                                              "up",
                                              3,
                                              3);

        // We found the up vector.
        if (up_attrib)
        {
            up_h.bind(up_attrib);

            // Get the up vector.
            up = up_h.get(ptOff);
        }
        // Leave the up vector as the zero vector.
        else
            up.assign(0,0,0);

        xform.instance(pt_pos, dir, pscale, &scale, &up, &rot, &trans, 0);
    }

    // Assign the transform.
    mat = pre_xform * xform;
}

int
SOP_PrimGroupCentroid::buildCentroids(fpreal t, int mode, int method)
{
    bool                        copy, store;
    exint                       int_value;

    const GA_AIFStringTuple     *ident_t;
    GA_Attribute                *ident_attrib;
    GA_Offset                   ptOff;
    GA_RWHandleI                class_h;

    const GU_Detail             *input_geo;

    UT_BoundingBox              bbox;
    UT_String                   attr_name, pattern, str_value;
    UT_Vector3                  pos;

    UT_Array<GA_Range>          range_array;
    UT_Array<GA_Range>::iterator  array_it;
    UT_StringArray              string_values;
    UT_IntArray                 int_values;

    // Get the input geometry as read only.
    GU_DetailHandleAutoReadLock gdl(inputGeoHandle(0));
    input_geo = gdl.getGdp();

    // Check to see if we should store the source group/attribute name as an
    // attribute the generated points.
    store = STORE(t);

    // If we want to we need to create the attributes.
    if (store)
    {
        // A 'class' operation, so create a new integer attribute.
        if (mode == MODE_CLASS)
        {
            // Add the int tuple.
            ident_attrib = gdp->addIntTuple(GA_ATTRIB_POINT, MODENAME_CLASS, 1);

            // Bind the handle.
            class_h.bind(ident_attrib);
        }
        // Using the 'name' attribute or groups, so create a new string
        // attribute.
        else
        {
            attr_name = (mode == MODE_GROUP) ? MODENAME_GROUP : MODENAME_NAME;

            // Create a new string attribute.
            ident_attrib = gdp->addStringTuple(GA_ATTRIB_POINT, attr_name, 1);

            // Get the string tuple so we can set values.
            ident_t = ident_attrib->getAIFStringTuple();
        }
    }

    // Create a new attribute reference map.
    GA_AttributeRefMap          hmap(*gdp, input_geo);

    // Get the attribute selection string.
    ATTRIBUTES(pattern, t);

    copy = COPY(t);

    // Build the reference map.
    buildRefMap(t, hmap, pattern, input_geo, mode, GA_ATTRIB_PRIMITIVE, copy);

    // Creating by groups.
    if (mode == MODE_GROUP)
    {
        // Get the group pattern.
        GROUP(pattern, t);

        // If the group string is empty, get out of here.
        if (pattern.length() == 0)
            return 1;

        buildGroupData(pattern, input_geo, range_array, string_values);
    }
    // 'name' or 'class'.
    else
    {
        // Build the data.  If something failed, return that we had an issue.
        if (buildAttribData(mode, input_geo, range_array, string_values, int_values))
            return 1;
    }

    exint index = 0;

    // Iterate over each of the primitive ranges we found.
    for (array_it=range_array.begin(); !array_it.atEnd(); ++array_it)
    {
        // Create a new point.
        ptOff = gdp->appendPointOffset();

        // Bounding Box
        if (method == 1)
        {
            // Calculate the bouding box center for this range.
            boundingBox(input_geo, *array_it, pos);
            // Set the point's position to the center of the box.
            gdp->setPos3(ptOff, pos);
        }
        // Center of Mass
        else if (method == 2)
        {
            // Calculate the center of mass for this range.
            centerOfMass(input_geo, *array_it, pos);
            // Set the point's position to the center of mass.
            gdp->setPos3(ptOff, pos);
        }
        // Barycenter
        else
        {
            // Calculate the barycenter for this range.
            baryCenter(input_geo, *array_it, pos);
            // Set the point's position to the barycenter.
            gdp->setPos3(ptOff, pos);
        }

        // Store the source value if required.
        if (store)
        {
            // 'class', so get the integer value at this iterator index.
            if (mode == MODE_CLASS)
            {
                int_value = int_values(index);
                class_h.set(ptOff, int_value);
            }
            // 'name' or by group, so get the string value at this iterator
            // index.
            else
            {
                str_value = string_values(index);
                ident_t->setString(ident_attrib, ptOff, str_value, 0);
            }
        }

        // If there are no entries in the map then we don't need to copy
        // anything.
        if (hmap.entries() > 0)
        {
            GA_WeightedSum              sum;

            // Start a weighted sum for the range.
            hmap.startSum(sum, GA_ATTRIB_POINT, ptOff);

            // Add the values for each primitive to the sum.
            for (GA_Iterator it(*array_it); !it.atEnd(); ++it)
            {
                hmap.addSumValue(sum,
                                 GA_ATTRIB_POINT,
                                 ptOff,
                                 GA_ATTRIB_PRIMITIVE,
                                 *it,
                                 1);
            }

            // Finish the sum, normalizing the values.
            hmap.finishSum(sum,
                           GA_ATTRIB_POINT,
                           ptOff,
                           1.0/(*array_it).getEntries());
        }

        index++;
    }

    return 0;
}

int
SOP_PrimGroupCentroid::bindToCentroids(fpreal t, int mode, int method)
{
    int                         behavior;
    exint                       int_value;

    const GA_Attribute          *attrib, *prim_attrib;
    const GA_PrimitiveGroup     *group;
    GA_PrimitiveGroup           *all_prims, *temp_group;
    GA_Range                    pr_range;
    GA_ROAttributeRef           primattr_gah;
    GA_ROHandleI                class_h;
    GA_ROHandleS                str_h;

    const GU_Detail             *input_geo;

    UT_Matrix4                  mat;
    UT_String                   attr_name, pattern, str_value;
    UT_Vector3                  pos;

    // Get the second input geometry as read only.
    GU_DetailHandleAutoReadLock gdl(inputGeoHandle(1));
    input_geo = gdl.getGdp();

    // Get the unmatched geometry behavior.
    behavior = BEHAVIOR(t);

    // Create a new attribute reference map.
    GA_AttributeRefMap          hmap(*gdp, input_geo);

    // Get the attribute selection string.
    BIND(pattern, t);

    // Build the reference map.
    buildRefMap(t, hmap, pattern, input_geo, mode, GA_ATTRIB_POINT);

    // Create a temporary primitive group so we can keep track of all the
    // primitives we have modified.
    all_prims = createAdhocPrimGroup(*gdp, "allprims");

    // Determine which attribute we need from the points, based on the mode.
    switch (mode)
    {
        case MODE_GROUP:
            attr_name = MODENAME_GROUP;
            break;
        case MODE_NAME:
            attr_name = MODENAME_NAME;
            break;
        case MODE_CLASS:
            attr_name = MODENAME_CLASS;
            break;
        default:
            addError(SOP_MESSAGE, "Invalid mode setting");
            return 1;
    }

    // Find the attribute.
    attrib = input_geo->findPointAttribute(attr_name);

    // If there is no attribute, add an error message and quit.
    if (!attrib)
    {
        addError(SOP_ATTRIBUTE_INVALID, attr_name);
        return 1;
    }

    // If not using groups, we need to check if the matching primitive
    // attribute exists on the geometry.
    if (mode != MODE_GROUP)
    {
        // Try to find the attribute.
        prim_attrib = gdp->findPrimitiveAttribute(attr_name);

        // If there is no attribute, add an error message and quit.
        if (!prim_attrib)
        {
            addError(SOP_ATTRIBUTE_INVALID, attr_name);
            return 1;
        }

        primattr_gah = GA_ROAttributeRef(prim_attrib);
    }

    // 'class' uses the int handle.
    if (mode == MODE_CLASS)
        class_h.bind(attrib);
    // Groups and 'name' use the string handle.
    else
        str_h.bind(attrib);

    for (GA_Iterator it(input_geo->getPointRange()); !it.atEnd(); ++it)
    {
        if (mode == MODE_GROUP)
        {
            // Get the unique string value.
            str_value = str_h.get(*it);

            // Find the group on the geometry to bind.
            group = gdp->findPrimitiveGroup(str_value);

            // Ignore non-existent groups.
            if (!group)
                continue;

            // Skip emptry groups.
            if (group->isEmpty())
                continue;

            // The primtives in the group.
            pr_range = gdp->getPrimitiveRange(group);
        }
        else
        {
            if (mode == MODE_NAME)
            {
                // Get the unique string value.
                str_value = str_h.get(*it);
                // Get the prims with that string value.
                pr_range = gdp->getRangeByValue(primattr_gah, str_value);
            }
            else
            {
                // Get the unique integer value.
                int_value = class_h.get(*it);
                // Get the prims with that integery value.
                pr_range = gdp->getRangeByValue(primattr_gah, int_value);
            }
            // Create an adhoc group.
            temp_group = createAdhocPrimGroup(*gdp);
            temp_group->addRange(pr_range);
        }

        // Add the primitives in the range to the groups.
        all_prims->addRange(pr_range);

        // Bounding Box
        if (method == 1)
        {
            // Calculate the bouding box center for this range.
            boundingBox(gdp, pr_range, pos);
        }
        // Center of Mass
        else if (method == 2)
        {
            // Calculate the center of mass for this attribute value.
            centerOfMass(gdp, pr_range, pos);
        }
        // Barycenter
        else
        {
            // Calculate the barycenter for this attribute value.
            baryCenter(gdp, pr_range, pos);
        }

        // Build the transform from the point information.
        buildTransform(mat, input_geo, pos, *it);

        // Transform the geometry from the centroid.
        if (mode == MODE_GROUP)
            gdp->transform(mat, group);
        else
            gdp->transform(mat, temp_group);

        // Copy any necessary attributes from the incoming points to the
        // geometry.
        if (hmap.entries())
        {
            for (GA_Iterator pr_it(pr_range); !pr_it.atEnd(); ++pr_it)
            {
                hmap.copyValue(GA_ATTRIB_PRIMITIVE,
                               *pr_it,
                               GA_ATTRIB_POINT,
                               *it);
            }
        }
    }

    // We want to destroy prims that didn't have a matching name/group.
    if (behavior)
    {
        // Flip the membership of all the prims that we did see.
        all_prims->toggleEntries();

        // Destroy the ones that we didn't.
        gdp->deletePrimitives(*all_prims, true);
    }

    return 0;
}

OP_ERROR
SOP_PrimGroupCentroid::cookMySop(OP_Context &context)
{
    fpreal                      now;
    int                         method, mode;

    now = context.getTime();

    if (lockInputs(context) >= UT_ERROR_ABORT)
        return error();

    // The partitioning mode.
    mode = MODE(now);

    // Find out which calculation method we are attempting.
    method = METHOD(now);

    // Binding geometry.
    if (nConnectedInputs() == 2)
    {
        // Duplicate the source.
        duplicateSource(0, context);

        // Bind to the centroids.  If the function returns 1, unlock
        // the inputs and return.
        if (bindToCentroids(now, mode, method))
        {
            unlockInputs();
            return error();
        }
    }
    // Creating centroids.
    else
    {
        // Clear out any previous data.
        gdp->clearAndDestroy();

        // Build the centroids.  If the function returns 1, unlock
        // the inputs and return.
        if (buildCentroids(now, mode, method))
        {
            unlockInputs();
            return error();
        }
    }

    unlockInputs();
    return error();
}

const char *
SOP_PrimGroupCentroid::inputLabel(unsigned idx) const
{
    switch (idx)
    {
        case 0:
            return "Geometry to generate centroids for.";
        case 1:
            return "Optional transform points.";
        default:
            return "Input";
    }
}

