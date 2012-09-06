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
#include <OP/OP_Operator.h>
#include <OP/OP_OperatorTable.h>
#include <PRM/PRM_Include.h>
#include <UT/UT_DSOVersion.h>
#include <UT/UT_WorkArgs.h>

void
newSopOperator(OP_OperatorTable *table)
{
    table->addOperator(
        new OP_Operator("primgroupcentroid",
                        "PrimitiveGroupCentroid",
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
    exint                       mode;

    OP_Node                     *bind_input;

    // Partitioning mode.
    mode = MODE(t);

    // Try to get the 2nd input.
    bind_input = getInput(1);

    // Only use the 'group' parm when doing a group operation.
    changed = enableParm("group", mode == 0);

    // Enable the 'store' parm when there is no 2nd input.
    changed += enableParm("store", bind_input == NULL);

    // Enable the 'behavior' parm when there is a 2nd input.
    changed += enableParm("behavior", bind_input != NULL);

    return changed;
}

static PRM_Name names[] =
{
    PRM_Name("mode", "Mode"),
    PRM_Name("group", "Group"),
    PRM_Name("method", "Method"),
    PRM_Name("store", "Store Source Identifier"),
    PRM_Name("behavior", "Unmatched Behavior")
};

static PRM_Name modeChoices[] =
{
    PRM_Name("group", "Group"),
    PRM_Name("name", "Name"),
    PRM_Name("class", "Class"),
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
    (PRM_ChoiceListType)(PRM_CHOICELIST_EXCLUSIVE
                         | PRM_CHOICELIST_REPLACE),
    modeChoices);

static PRM_ChoiceList methodChoiceMenu(
    (PRM_ChoiceListType)(PRM_CHOICELIST_EXCLUSIVE
                         | PRM_CHOICELIST_REPLACE),
    methodChoices);

static PRM_ChoiceList behaviorChoiceMenu(
    (PRM_ChoiceListType)(PRM_CHOICELIST_EXCLUSIVE
                         | PRM_CHOICELIST_REPLACE),
    behaviorChoices);

static PRM_Default defaults[] =
{
    PRM_Default(1),
    PRM_Default(0),
    PRM_Default(0),
    PRM_Default(0),
    PRM_Default(0),
};

PRM_Template
SOP_PrimGroupCentroid::myTemplateList[] = {
    PRM_Template(PRM_ORD, 1, &names[0], &defaults[0], &modeChoiceMenu),
    PRM_Template(PRM_STRING, 1, &names[1], &defaults[1], &SOP_Node::primGroupMenu),
    PRM_Template(PRM_ORD, 1, &names[2], &defaults[2], &methodChoiceMenu),
    PRM_Template(PRM_TOGGLE, 1, &names[3], &defaults[3]),
    PRM_Template(PRM_ORD, 1, &names[4], &defaults[4], &behaviorChoiceMenu),
    PRM_Template()
};

void
SOP_PrimGroupCentroid::centerOfMass(GA_Range &pr_range,
                                    const GA_PrimitiveList &prim_list,
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
        prim = (const GEO_Primitive *) prim_list.get(*it);
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
                                  const GA_PrimitiveList &prim_list,
                                  UT_Vector3 &pos)
{
    GA_Range                    pt_range;

    GA_OffsetArray              points;
    GA_OffsetArray::const_iterator points_it;

    // We need to iterate over each primitive in the range and
    // find out which points it references.
    for (GA_Iterator pr_it(pr_range); !pr_it.atEnd(); ++pr_it)
    {
        // Get the range of points for the primitive using the
        // offset from the primitive list.
        pt_range = prim_list.get(*pr_it)->getPointRange();

        // Add each point's offset to the array, checking for duplicates.
        for (GA_Iterator pt_it(pt_range); !pt_it.atEnd(); ++pt_it)
            points.append(*pt_it, true);
    }

    // Reset the position.
    pos.assign(0,0,0);

    // Add the positions for all the points.
    for (points_it = points.begin(); !points_it.atEnd(); ++points_it)
        pos += input_geo->getPos3(*points_it);

    // Store the average position for all the points we found.
    pos /= points.entries();
}

void
SOP_PrimGroupCentroid::buildTransform(UT_Matrix4 &mat,
                                      const GU_Detail *input_geo,
                                      const UT_Vector3 centroid,
                                      GA_Offset ptOff)
{
    bool                        use_orient = false;
    fpreal                      pscale = 1;

    GA_ROAttributeRef           dir_gah, orient_gah, pscale_gah, rot_gah, scale_gah, trans_gah, up_gah;
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
    orient_gah = input_geo->findFloatTuple(GA_ATTRIB_POINT,
                                      GA_SCOPE_PUBLIC,
                                      "orient",
                                      4,
                                      4);

    // Found the attribute.
    if (orient_gah.isValid())
    {
        orient_h.bind(orient_gah.getAttribute());
        // Get the attribute value.
        UT_Vector4 value = orient_h.get(ptOff);

        // Construct a quaternion from the values.
        orient.assign(value[0], value[1], value[2], value[3]);
        use_orient = true;
    }


    // Try to find the 'trans' point attribute.
    trans_gah = input_geo->findFloatTuple(GA_ATTRIB_POINT,
                                          GA_SCOPE_PUBLIC,
                                          "trans",
                                          3,
                                          3);

    // We found it.
    if (trans_gah.isValid())
    {
        // Bind the handle to the attribute..
        trans_h.bind(trans_gah.getAttribute());

        // Get the attribute value.
        trans = trans_h.get(ptOff);
    }
    else
        trans.assign(0, 0, 0);

    // Try to find the scale attribute.
    scale_gah = input_geo->findFloatTuple(GA_ATTRIB_POINT,
                                          GA_SCOPE_PUBLIC,
                                          "scale",
                                          3,
                                          3);

    // Try to find the pscale attribute.
    pscale_gah = input_geo->findFloatTuple(GA_ATTRIB_POINT,
                                           GA_SCOPE_PUBLIC,
                                           "pscale",
                                           1,
                                           1);

    //  If the pscale attribute exists, get the value.
    if (pscale_gah.isValid())
    {
        pscale_h.bind(pscale_gah.getAttribute());
        pscale = pscale_h.get(ptOff);
    }

    // The scale attribute exists.
    if (scale_gah.isValid())
    {
        scale_h.bind(scale_gah.getAttribute());
        // Get the scale.
        scale = scale_h.get(ptOff);
    }
    else
        // Use a default scale.
        scale.assign(1, 1, 1);

    // Try to find the specific attribute.
    rot_gah = input_geo->findFloatTuple(GA_ATTRIB_POINT,
                                        GA_SCOPE_PUBLIC,
                                        "rot",
                                        4,
                                        4);

    // Found the attribute.
    if (rot_gah.isValid())
    {
        rot_h.bind(rot_gah.getAttribute());
        // Get the attribute value.
        UT_Vector4 value = rot_h.get(ptOff);

        // Construct a quaternion from the values.
        rot.assign(value[0], value[1], value[2], value[3]);
    }

    if (use_orient)
        xform.instance(pt_pos, dir, pscale, &scale, &up, &rot, &trans, &orient);
    else
    {
        // Try to find the point Normal attribute.
        dir_gah = input_geo->findNormalAttribute(GA_ATTRIB_POINT);

        // We couldn't find the Normal attribute.
        if (dir_gah.isInvalid())
        {
            // Try to find the velocity attribute.
            dir_gah = input_geo->findVelocityAttribute(GA_ATTRIB_POINT);
        }

        // We found either the normal or velocity attributes.
        if (dir_gah.isValid())
        {
            // Bind the direction handle to the found attribute.
            dir_h.bind(dir_gah.getAttribute());

            dir = dir_h.get(ptOff);
        }
        // Default to the Z-axis.
        else
            dir = UT_Vector3(0,0,1);

        // Try to find the upvector ('up') attribute.
        up_gah = input_geo->findFloatTuple(GA_ATTRIB_POINT,
                                           GA_SCOPE_PUBLIC,
                                           "up",
                                           3,
                                           3);

        // We found the up vector.
        if (up_gah.isValid())
        {
            up_h.bind(up_gah.getAttribute());
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
SOP_PrimGroupCentroid::buildCentroids(fpreal t, exint mode, exint method)
{
    bool                        store;
    exint                       int_value, unique_count;

    const GA_AIFStringTuple     *src_t;
    GA_Attribute                *src_attrib;
    GA_Offset                   ptOff;
    const GA_PrimitiveGroup     *group;
    GA_Range                    pr_range, pt_range;
    GA_ROAttributeRef           class_gah, name_gah;
    GA_RWAttributeRef           src_gah;
    GA_RWHandleI                class_h;

    const GU_Detail             *input_geo;

    UT_BoundingBox              bbox;
    UT_String                   attr_name, group_name, pattern, str_value;
    UT_Vector3                  pos;
    UT_WorkArgs                 tokens;

    // Get the input geometry as read only.
    GU_DetailHandleAutoReadLock gdl(inputGeoHandle(0));
    input_geo = gdl.getGdp();

    // Should we store the source group name/name attribute value as a
    // string attribute on the generated point.
    store = STORE(t);

    // If we want to we need to create a new string attribute.
    if (store)
    {
        // 'class' operation.
        if (mode == 2)
        {
            // Add the int tuple.
            src_gah = gdp->addIntTuple(GA_ATTRIB_POINT, "class", 1);
            // Bind the handle.
            class_h.bind(src_gah.getAttribute());
        }
        else
        {
            // 'group' operation.
            if (mode == 0)
                attr_name = "group";
            // 'name' operation.
            else
                attr_name = "name";

            // Create a new string attribute.
            src_gah = gdp->addStringTuple(GA_ATTRIB_POINT, attr_name, 1);
            src_attrib = src_gah.getAttribute();
            // Get the string tuple so we can set values.
            src_t = src_gah.getAIFStringTuple();
        }
    }

    // The list of GA_Primitives in the input geometry.
    const GA_PrimitiveList &prim_list = input_geo->getPrimitiveList();

    // We are using the 'name' attribute.
    if (mode == 1 || mode == 2)
    {
        if (mode == 1)
        {
            // Find the attribute.
            name_gah = input_geo->findPrimitiveAttribute("name");

            // If there is no 'name' attribute, add an error message and
            // quit.
            if (name_gah.isInvalid())
            {
                addError(SOP_ATTRIBUTE_INVALID, "name");
                return 1;
            }

            if (!name_gah.isString())
            {
                addError(SOP_MESSAGE, "'name' must be a string.");
                return 1;
            }

            // The number of unique string values for the attribute.
            unique_count = input_geo->getUniqueValueCount(name_gah);
        }
        else
        {
            // Find the attribute.
            class_gah = input_geo->findPrimitiveAttribute("class");

            // If there is no 'class' attribute, add an error message and
            // quit.
            if (class_gah.isInvalid())
            {
                addError(SOP_ATTRIBUTE_INVALID, "class");
                return 1;
            }

            if (!class_gah.isInt())
            {
                addError(SOP_ATTRIBUTE_INVALID, "'class' must be an integer.");
                return 1;
            }
            // The number of unique string values for the attribute.
            unique_count = input_geo->getUniqueValueCount(class_gah);
        }

        for (int idx=0; idx<unique_count; ++idx)
        {
            // Get the unique string value.
            if (mode == 1)
            {
                str_value = input_geo->getUniqueStringValue(name_gah, idx);
                pr_range = input_geo->getRangeByValue(name_gah, str_value);
            }
            else
            {
                int_value = input_geo->getUniqueIntegerValue(class_gah, idx);
                pr_range = input_geo->getRangeByValue(class_gah, int_value);
            }

            // Create a new point offset for this value.
            ptOff = gdp->appendPointOffset();

            // Bounding Box
            if (method == 1)
            {
                // Initialize the bounding box to contain nothing and have
                // no position.
                bbox.initBounds();

                // Iterate over each primitive in the range.
                for (GA_Iterator pr_it(pr_range); !pr_it.atEnd(); ++pr_it)
                {
                    // Get the range of points for the primitive using the
                    // offset from the primitive list.
                    pt_range = prim_list.get(*pr_it)->getPointRange();

                    // For each point in the primitive, enlarge the bounding
                    // box to contain it.
                    for (GA_Iterator pt_it(pt_range); !pt_it.atEnd(); ++pt_it)
                        bbox.enlargeBounds(input_geo->getPos3(*pt_it));
                }

                // Set the point's position to the center of the box.
                gdp->setPos3(ptOff, bbox.center());
            }
            // Center of Mass
            else if (method == 2)
            {
                // Calculate the center of mass for this name value.
                centerOfMass(pr_range, prim_list, pos);
                // Set the point's position to the center of mass.
                gdp->setPos3(ptOff, pos);
            }
            // Barycenter
            else
            {
                // Calculate the barycenter for this name value.
                baryCenter(input_geo, pr_range, prim_list, pos);
                // Set the point's position to the barycenter.
                gdp->setPos3(ptOff, pos);
            }

            // Store the source value if required.
            if (store)
            {
                if (mode == 1)
                    src_t->setString(src_attrib, ptOff, str_value, 0);
                else
                    class_h.set(ptOff, int_value);
            }
        }
    }

    else
    {
        // Get the group pattern.
        GROUP(pattern, t);

        // If the group string is empty, get out of here.
        if (pattern.length() == 0)
            return 1;

        // Tokenize the pattern.
        pattern.tokenize(tokens);

        // For each primitive group in order.
        for (GA_ElementGroupTable::ordered_iterator it(input_geo->primitiveGroups().obegin()); !it.atEnd(); ++it)
        {
            // Get the group.
            group = static_cast<GA_PrimitiveGroup *>(*it);

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

            // Create a new point offset for this group.
            ptOff = gdp->appendPointOffset();

            // Get a range for the primitives in the group.
            pr_range = input_geo->getPrimitiveRange(group);

            // Bounding Box
            if (method == 1)
            {
                // Get the bounding box for the group and store its center
                // position.
                input_geo->getBBox(&bbox, group);
                // Set the point's position to the center of the box.
                gdp->setPos3(ptOff, bbox.center());
            }
            // Center of Mass
            else if (method == 2)
            {
                // Calculate the center of mass for this group.
                centerOfMass(pr_range, prim_list, pos);
                // Set the point's position to the center of mass.
                gdp->setPos3(ptOff, pos);
            }
            // Barycenter
            else
            {
                // Calculate the barycenter for this group.
                baryCenter(input_geo, pr_range, prim_list, pos);
                // Set the point's position to the barycenter.
                gdp->setPos3(ptOff, pos);
            }

            // Store the group name if required.
            if (store)
            {
                src_t->setString(src_attrib, ptOff, group_name, 0);
            }
        }
    }
    return 0;
}

int
SOP_PrimGroupCentroid::bindToCentroids(fpreal t, exint mode, exint method)
{
    exint                       behavior, int_value;

    const GA_PrimitiveGroup     *group;
    GA_PrimitiveGroup           *all_prims, *temp_group;
    GA_Range         pr_range;
    GA_ROAttributeRef           attr_gah, primattr_gah;
    GA_ROHandleI                class_h;
    GA_ROHandleS                str_h;

    const GU_Detail             *input_geo;

    UT_BoundingBox              bbox;
    UT_Matrix4                  mat;
    UT_String                   attr_name, pattern, group_name, str_value;
    UT_Vector3                  pos;
    UT_WorkArgs                 tokens;

    // Get the second input geometry as read only.
    GU_DetailHandleAutoReadLock gdl(inputGeoHandle(1));
    input_geo = gdl.getGdp();

    // Get the unmatched geometry behavior.
    behavior = BEHAVIOR(t);

    // The list of GA_Primitives in the input geometry.
    const GA_PrimitiveList &prim_list = gdp->getPrimitiveList();

    all_prims = createAdhocPrimGroup(*gdp, "allprims");

    // We are using the 'name' attribute.
    if (mode == 1 || mode == 2)
    {
        if (mode == 1)
            attr_name = "name";
        else
            attr_name = "class";

        // Find the attributes.
        attr_gah = input_geo->findPointAttribute(attr_name);
        primattr_gah = gdp->findPrimitiveAttribute(attr_name);

        // If there is no attribute, add an error message and quit.
        if (attr_gah.isInvalid())
        {
            addError(SOP_ATTRIBUTE_INVALID, attr_name);
            return 1;
        }

        // If there is no attribute, add an error message and quit.
        if (primattr_gah.isInvalid())
        {
            addError(SOP_ATTRIBUTE_INVALID, attr_name);
            return 1;
        }

        // Bind the appropriate attribute handle.
        if (mode == 1)
            str_h.bind(attr_gah.getAttribute());
        else
            class_h.bind(attr_gah.getAttribute());

        for (GA_Iterator it(input_geo->getPointRange()); !it.atEnd(); ++it)
        {
            if (mode == 1)
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

            // Add the primitives in the range to the groups.
            all_prims->addRange(pr_range);
            temp_group->addRange(pr_range);

            // Bounding Box
            if (method == 1)
            {
                gdp->getBBox(&bbox, temp_group);
                pos = bbox.center();
            }
            // Center of Mass
            else if (method == 2)
            {
                // Calculate the center of mass for this attribute value.
                centerOfMass(pr_range, prim_list, pos);
            }
            // Barycenter
            else
            {
                // Calculate the barycenter for this attribute value.
                baryCenter(gdp, pr_range, prim_list, pos);
            }

            // Transform the geometry from the centroid.
            buildTransform(mat, input_geo, pos, *it);
            gdp->transform(mat, temp_group);
        }

    }

    // Using the group mask.
    else
    {
        // Get the group pattern.
        GROUP(pattern, t);

        // If the group string is empty, get out of here.
        if (pattern.length() == 0)
            return 1;

        // Tokenize the pattern.
        pattern.tokenize(tokens);

        // Find the 'group' point attribute on the incoming points.
        attr_gah = input_geo->findPointAttribute("group");

        // If there is no attribute, add an error message and quit.
        if (attr_gah.isInvalid())
        {
            addError(SOP_ATTRIBUTE_INVALID, "group");
            return 1;
        }

        // Bind the attribute handle.
        str_h.bind(attr_gah.getAttribute());

        for (GA_Iterator it(input_geo->getPointRange()); !it.atEnd(); ++it)
        {
            // Get the 'group' string value.
            str_value = str_h.get(*it);

            // If the group name doesn't match our pattern, continue.
            if (!str_value.matchPattern(tokens))
                continue;

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

            // Add the primitives in the range to the group.
            all_prims->addRange(pr_range);

            // Bounding Box
            if (method == 1)
            {
                gdp->getBBox(&bbox, group);
                pos = bbox.center();
            }
            // Center of Mass
            else if (method == 2)
            {
                // Calculate the center of mass for this name value.
                centerOfMass(pr_range, prim_list, pos);
            }
            // Barycenter
            else
            {
                // Calculate the barycenter for this name value.
                baryCenter(gdp, pr_range, prim_list, pos);
            }

            // Transform the geometry from the centroid.
            buildTransform(mat, input_geo, pos, *it);
            gdp->transform(mat, group);
        }
    }

    // We want to destroy prims that didn't have a matching name/group.
    if (behavior)
    {
        // Flip the membership of all the prims that we did see.
        all_prims->toggleEntries();

        // Destroy them.
        gdp->deletePrimitives(*all_prims, true);
    }

    return 0;
}

OP_ERROR
SOP_PrimGroupCentroid::cookMySop(OP_Context &context)
{
    fpreal                      now;
    exint                       method, mode;

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

