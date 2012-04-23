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
 * Version: 2.0
*/

#include "SOP_PrimCentroid.h"

#include <PRM/PRM_Include.h>

#include <OP/OP_Operator.h>
#include <OP/OP_OperatorTable.h>
#include <UT/UT_DSOVersion.h>

void 
newSopOperator(OP_OperatorTable *table)
{
    table->addOperator(
        new OP_Operator("primcentroid",
                        "Primitive Centroid",
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

static PRM_Name         method_name("method", "Method");
static PRM_Default      method_default(0);

PRM_Template
SOP_PrimCentroid::myTemplateList[] = {
    PRM_Template(PRM_ORD, 1, &method_name, &method_default, &methodChoiceMenu),
    PRM_Template()
};

OP_ERROR
SOP_PrimCentroid::cookMySop(OP_Context &context)
{
    fpreal 		        now;
    exint 		        method;

    GA_Offset                   ptOff;

    GA_RWAttributeRef	        n_gah;
    GA_RWHandleV3               n_h;

    const GEO_Primitive	        *prim;
    const GU_Detail             *input_geo;

    UT_BoundingBox	        bbox;
    
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
    }

    unlockInputs();
    return error();
}

