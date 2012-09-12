/*
 * Produced by:
 *      Graham Thompson
 *      captainhammy@gmail.com
 *      www.captainhammy.com
 *
 * Description:
 *     	Create points at the centroid of primitives.
 *
 * Name: SOP_PrimCentroid.C
 * 
*/

#include "SOP_PrimCentroid.h"

#include <CH/CH_Manager.h>
#include <GA/GA_AttributeRefMap.h>
#include <PRM/PRM_Include.h>
#include <UT/UT_WorkArgs.h>
#include <OP/OP_Operator.h>
#include <OP/OP_OperatorTable.h>
#include <UT/UT_DSOVersion.h>

void 
newSopOperator(OP_OperatorTable *table)
{
    table->addOperator(
        new OP_Operator("primcentroid",
                        "PrimitiveCentroid",
                        SOP_PrimCentroid::myConstructor,
                        SOP_PrimCentroid::myTemplateList,
                        1,
                        1,
                        0)
    );
}

OP_Node *
SOP_PrimCentroid::myConstructor(OP_Network *net, 
                                const char *name, 
                                OP_Operator *op)
{
    return new SOP_PrimCentroid(net, name, op);
}

SOP_PrimCentroid::SOP_PrimCentroid(OP_Network *net,
                                   const char *name, 
                                   OP_Operator *op):
    SOP_Node(net, name, op) {}


static PRM_Name methodChoices[] =
{
    PRM_Name("bary", "Barycenter"),
    PRM_Name("bbox", "Bounding Box"),
    PRM_Name(0)
};

static PRM_ChoiceList methodChoiceMenu(
    (PRM_ChoiceListType)(PRM_CHOICELIST_EXCLUSIVE 
                         | PRM_CHOICELIST_REPLACE),
    methodChoices);


static PRM_Name names[] =
{
    PRM_Name("method", "Method"),
    PRM_Name("attributes", "Attributes to Copy"),
};

static PRM_Default defaults[] =
{
    PRM_Default(0),
    PRM_Default(0, ""),
};

void
SOP_PrimCentroid::buildMenu(void *data,
                            PRM_Name *menu,
                            int list_size,
                            const PRM_SpareData *,
                            const PRM_Parm *)
{
    // Get the instance of the operator.
    SOP_PrimCentroid *me = (SOP_PrimCentroid *)data;

    // Populate the menu with primitive attribute names.
    me->fillAttribNameMenu(menu, 100, GEO_PRIMITIVE_DICT , 0);
}

static PRM_ChoiceList attribMenu((PRM_ChoiceListType)(PRM_CHOICELIST_TOGGLE),
                                 &SOP_PrimCentroid::buildMenu);

PRM_Template
SOP_PrimCentroid::myTemplateList[] = {
    PRM_Template(PRM_ORD, 1, &names[0], &defaults[0], &methodChoiceMenu),
    PRM_Template(PRM_STRING, 1, &names[1], &defaults[1], &attribMenu),
    PRM_Template()
};

OP_ERROR
SOP_PrimCentroid::cookMySop(OP_Context &context)
{
    fpreal 		        now;
    int 		        method;

    const GA_Attribute          *source_attr;
    const GA_AttributeDict      *dict;
    GA_AttributeDict::iterator  a_it;
    GA_Offset                   ptOff;
    GA_RWAttributeRef	        n_gah;
    GA_RWHandleV3               n_h;

    const GEO_Primitive	        *prim;

    const GU_Detail             *input_geo;

    UT_BoundingBox	        bbox;
    UT_String                   pattern, attr_name;
    UT_WorkArgs                 tokens;
    
    now = context.getTime();

    if (lockInputs(context) >= UT_ERROR_ABORT)
        return error();

    // Clear out any previous data.
    gdp->clearAndDestroy();

    // Get the input geometry as read only.
    GU_DetailHandleAutoReadLock gdl(inputGeoHandle(0));
    input_geo = gdl.getGdp();

    // Find out which calculation method we are attempting.
    method = METHOD(now);

    // Create the standard point normal (N) attribute.
    n_gah = gdp->addNormalAttribute(GA_ATTRIB_POINT);

    // Bind a read/write attribute handle to the normal attribute.
    n_h.bind(n_gah.getAttribute());

    // Construct an attribute reference map to map attributes.
    GA_AttributeRefMap hmap(*gdp, input_geo);

    // Get the attribute selection string.
    ATTRIBUTES(pattern, now);

    // Make sure we entered something.
    if (pattern.length() > 0)
    {
        // Tokenize the pattern.
        pattern.tokenize(tokens, " ");

        // The primitive attributes on the incoming geometry.
        dict = &input_geo->primitiveAttribs();

        // Iterate over all the primitive attributes.
        for (a_it=dict->begin(GA_SCOPE_PUBLIC); !a_it.atEnd(); ++a_it)
        {
            // The current attribute.
            source_attr = a_it.attrib();
            
            // Get the attribute name.
            attr_name = source_attr->getName();

            // If the name doesn't match our pattern, skip it.
            if (!attr_name.matchPattern(tokens))
                continue;

            // Create a new point attribute on the current geometry
            // that is the same as the source attribute.  Append it and
            // the source to the map.
            hmap.append(gdp->addPointAttrib(source_attr).getAttribute(),
                        source_attr);
        }
    }
     
    // Get the list of input primitives.
    const GA_PrimitiveList &prim_list = input_geo->getPrimitiveList();

    // Iterate over primitives using pages.
    for (GA_Iterator it(input_geo->getPrimitiveRange()); !it.atEnd(); ++it)
    {
        // Get the primitive from the list.
        prim = (const GEO_Primitive *) prim_list.get(*it);

        // Create a new point offset for this primitive.
        ptOff = gdp->appendPointOffset();

        if (method)
        {
            // Get the bounding box for the primitive and set the point's
            // position to be the center of the box.
            prim->getBBox(&bbox);
            gdp->setPos3(ptOff, bbox.center());
        }
        else
            // Set the point's position to be the bary center of the primitive
            gdp->setPos3(ptOff, prim->baryCenter());

        // Set the point's normal to be the normal of the primitive.
        n_h.set(ptOff, prim->computeNormal());

        // If we are copying attributes, copy the primitive attributes from
        // the current primitive to the new point.
        if (hmap.entries() > 0)
            hmap.copyValue(GA_ATTRIB_POINT, ptOff, GA_ATTRIB_PRIMITIVE, *it);
    }

    unlockInputs();
    return error();
}

const char *
SOP_PrimCentroid::inputLabel(unsigned idx) const
{
    switch (idx)
    {
        case 0:
            return "Primitives to generate centroids for.";
        default:
            return "Input";
    }
}

