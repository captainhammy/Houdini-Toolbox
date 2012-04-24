/*
 * Produced by:
 *      Graham Thompson
 *      captainhammy@gmail.com
 *      www.captainhammy.com
 *
 * Description:
 *     	Create points at the centroids of primitive groups or at the
 *      centroids of unique primitive 'name' attribute values.
 *
 * Name: SOP_PrimGroupCentroid.C
 *
 * Version: 3.0
*/

#include "SOP_PrimGroupCentroid.h"

#include <CH/CH_Manager.h>
#include <PRM/PRM_Include.h>
#include <UT/UT_BitArray.h>
#include <UT/UT_WorkArgs.h>

#include <OP/OP_Operator.h>
#include <OP/OP_OperatorTable.h>
#include <UT/UT_DSOVersion.h>

void
newSopOperator(OP_OperatorTable *table)
{
    table->addOperator(
        new OP_Operator("primgroupcentroid",
                        "PrimitiveGroupCentroid",
                        SOP_PrimGroupCentroid::myConstructor,
                        SOP_PrimGroupCentroid::myTemplateList,
                        1,
                        1,
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
    fpreal	t = CHgetEvalTime();
    unsigned 	changed;
    bool 	store, name;

    // Are we using the 'name' attribute.
    name = USENAME(t);
    // Are we storing the attribute name.
    store = STORE(t);

    // Disable setting an attribute name when we are storing and using
    // the 'name' attribute.
    changed = enableParm("name", store && !name);
    // Disable the 'group' parm when we are using the 'name' attribute.
    changed += enableParm("group", !name);

    return changed;
}

static PRM_Name names[] =
{
    PRM_Name("method", "Method"),
    PRM_Name("useName", "Use Name Attribute"),
    PRM_Name("group", "Group"),
    PRM_Name("store", "Store Source Group"),
    PRM_Name("name", "Attribute Name")
};

static PRM_Name methodChoices[] =
{
    PRM_Name("bary", "Barycenter"),
    PRM_Name("bbox", "Bounding Box"),
    PRM_Name("com", "Center of Mass"),
    PRM_Name(0)
};

static PRM_ChoiceList methodChoiceMenu(
    (PRM_ChoiceListType)(PRM_CHOICELIST_EXCLUSIVE
                         | PRM_CHOICELIST_REPLACE),
    methodChoices);

static PRM_Default defaults[] =
{
    PRM_Default(0),
    PRM_Default(0),
    PRM_Default(0),
    PRM_Default(0),
    PRM_Default(0, "source_group")
};

PRM_Template
SOP_PrimGroupCentroid::myTemplateList[] = {
    PRM_Template(PRM_ORD, 1, &names[0], &defaults[0], &methodChoiceMenu),
    PRM_Template(PRM_TOGGLE, 1, &names[1], &defaults[1]),
    PRM_Template(PRM_STRING, 1, &names[2], &defaults[2], &SOP_Node::primGroupMenu),
    PRM_Template(PRM_TOGGLE, 1, &names[3], &defaults[3]),
    PRM_Template(PRM_STRING, 1, &names[4], &defaults[4]),
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
    // If the total area is not 0, divide the position by the total.
    if (total_area)
        pos /= total_area;
}

void
SOP_PrimGroupCentroid::baryCenter(const GU_Detail *input_geo,
                                  UT_BitArray &pt_mask,
                                  GA_Range &pr_range,
                                  const GA_PrimitiveList &prim_list,
                                  UT_Vector3 &pos)
{
    exint                       num_pts = 0;

    GA_Index                    pt_idx;
    GA_Range                    pt_range;

    // Reset the position.
    pos.assign(0,0,0);

    // We need to iterate over each primitive in the range and
    // find out which points it references.
    for (GA_Iterator pr_it(pr_range); !pr_it.atEnd(); ++pr_it)
    {
        // Get the range of points for the primitive using the
        // offset from the primitive list.
        pt_range = prim_list.get(*pr_it)->getPointRange();
        for (GA_Iterator pt_it(pt_range); !pt_it.atEnd(); ++pt_it)
        {
            // Get the index (point number) for this point.
            pt_idx = input_geo->pointIndex(*pt_it);
            // If we've seen this point already the go to the next one.
            if (pt_mask.getBit(pt_idx))
                continue;

            // Add in the position of the point.
            pos += input_geo->getPos3(*pt_it);
            // Store that we've touched this index.
            pt_mask.setBit(pt_idx, true);
            // Incrememt the number of points we've seen.
            num_pts++;
        }
    }

    // Reset the mask for the next group.
    pt_mask.setAllBits(0);

    // Store the average position for all the points we found.
    pos /= num_pts;
}

OP_ERROR
SOP_PrimGroupCentroid::cookMySop(OP_Context &context)
{
    fpreal 			now;
    exint			method, uniqueCount;
    bool 			useName, store;

    GA_Offset			ptOff;
    GA_Range			pr_range, pt_range;

    const GA_PrimitiveGroup	*group;

    const GA_AIFStringTuple 	*src_t;
    GA_Attribute		*src_attrib;
    GA_ROAttributeRef           name_gah;
    GA_RWAttributeRef		src_gah;

    const GU_Detail		*input_geo;

    UT_BitArray 		pt_mask;
    UT_BoundingBox		bbox;
    UT_String			pattern, group_name, attr_name, value;
    UT_Vector3			pos;
    UT_WorkArgs			tokens;

    now = context.getTime();

    if (lockInputs(context) >= UT_ERROR_ABORT)
        return error();

    // Clear out any previous data.
    gdp->clearAndDestroy();

    // Get the group pattern.
    GROUP(pattern, now);

    // Area we using the 'name' attribute.
    useName = USENAME(now);

    // If we aren't we need to check the group pattern and tokenize it.
    if (!useName)
    {
        // If the group string is empty, get out of here.
        if (pattern.length() == 0)
        {
            unlockInputs();
            return error();
        }

        // Tokenize the pattern.
        pattern.tokenize(tokens, " ");
    }

    // Get the input geometry as read only.
    GU_DetailHandleAutoReadLock gdl(inputGeoHandle(0));
    input_geo = gdl.getGdp();

    // Find out which calculation method we are attempting.
    method = METHOD(now);

    // Should we store the source group name/name attribute value as a
    // string attribute on the generated point.
    store = STORE(now);

    // If we want to we need to create a new string attribute.
    if (store)
    {
        // If we are using a name attribute we will automatically store
        // the value back as the name attribute.
        if (useName)
            attr_name = "name";
        // Get the attribute name.
        else
        {
            ATTRIB(attr_name, now);

            // If the entered name is empty, use a default name.
            if (attr_name.length() == 0)
                attr_name = "source_group";
        }

        // Create a new string attribute.
        src_gah = gdp->addStringTuple(GA_ATTRIB_POINT, attr_name, 1);
        src_attrib = src_gah.getAttribute();
        // Get the string tuple so we can set values.
        src_t = src_gah.getAIFStringTuple();
    }

    // The list of GA_Primitives in the input geometry.
    const GA_PrimitiveList &prim_list = input_geo->getPrimitiveList();

    // When doing barycenters, initialize the point mask.
    if (method == 0)
    {
        // Use an array of bits that is the same size as the number of
        // points in the detail to keep track of which points in the
        // group have already been touched.
        pt_mask.resize(input_geo->getNumPoints());
    }

    // We are using the 'name' attribute.
    if (useName)
    {
        // Find the attribute.
        name_gah = input_geo->findPrimitiveAttribute("name");

        // If there is no 'name' attribute, add an error message and
        // quit.
        if (name_gah.isInvalid())
        {
            addError(SOP_ATTRIBUTE_INVALID, "name");
            unlockInputs();
            return error();
        }

        // The number of unique string values for the attribute.
        uniqueCount = input_geo->getUniqueValueCount(name_gah);

        for (int idx=0; idx<uniqueCount; ++idx)
        {
            // Get the unique string value.
            value = input_geo->getUniqueStringValue(name_gah, idx);

            // Get the range of primitives that have this value.
            pr_range = input_geo->getRangeByValue(name_gah, value);

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
                baryCenter(input_geo, pt_mask, pr_range, prim_list, pos);
                // Set the point's position to the barycenter.
                gdp->setPos3(ptOff, pos);
            }

            // Store the name value if required.
            if (store)
                src_t->setString(src_attrib, ptOff, value, 0);
        }
    }

    else
    {
        // For each primitive group in order.
        for (GA_ElementGroupTable::ordered_iterator 
                __iter = (input_geo)->getElementGroupTable(GA_ATTRIB_PRIMITIVE).obegin(),
                __end = (input_geo)->getElementGroupTable(GA_ATTRIB_PRIMITIVE).oend();
            __iter != __end && 
                (group = static_cast<GA_ElementGroupTableT<GA_ATTRIB_PRIMITIVE>::GROUP_TYPE *>(__iter.item())); 
            ++__iter)
        {
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
                baryCenter(input_geo, pt_mask, pr_range, prim_list, pos);
                // Set the point's position to the barycenter.
                gdp->setPos3(ptOff, pos);
            }

            // Store the group name if required.
            if (store)
                src_t->setString(src_attrib, ptOff, group_name, 0);
        }
    }

    unlockInputs();
    return error();
}

