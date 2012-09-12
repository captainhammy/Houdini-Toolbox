/*
 * Produced by:
 *      Graham Thompson
 *      captainhammy@gmail.com
 *      www.captainhammy.com
 *
 * Description:
 *     	Create a point at the center of each voxel.
 *
 * Name: SOP_PointsFromVoxels.C
 * 
*/

#include "SOP_PointsFromVoxels.h"

#include <GEO/GEO_PrimVolume.h>
#include <PRM/PRM_Include.h>
#include <UT/UT_VoxelArray.h>
#include <OP/OP_Operator.h>
#include <OP/OP_OperatorTable.h>
#include <UT/UT_DSOVersion.h>

void
newSopOperator(OP_OperatorTable *table)
{ 
    table->addOperator(
        new OP_Operator("pointsfromvoxels",
                        "PointsFromVoxels",
                        SOP_PointsFromVoxels::myConstructor,
                        SOP_PointsFromVoxels::myTemplateList,
                        1,
                        1,
                        0)
    );
}

OP_Node *
SOP_PointsFromVoxels::myConstructor(OP_Network *net, 
                                    const char *name,
                                    OP_Operator *op)
{
    return new SOP_PointsFromVoxels(net, name, op);
}

SOP_PointsFromVoxels::SOP_PointsFromVoxels(OP_Network *net, 
                                           const char *name, 
                                           OP_Operator *op): 
    SOP_Node(net, name, op) {}

static PRM_Name names[] =
{
    PRM_Name("prim", "Primitive Number"),
    PRM_Name("cull", "Cull Empty"),
    PRM_Name(0)
};

static PRM_Default defaults[] =
{
    PRM_Default(0),
    PRM_Default(0)
};

static PRM_Range        prim_range(PRM_RANGE_RESTRICTED, 0, PRM_RANGE_UI, 10);

PRM_Template
SOP_PointsFromVoxels::myTemplateList[] = {
    PRM_Template(PRM_INT, 1, &names[0], &defaults[0], 0, &prim_range),
    PRM_Template(PRM_TOGGLE, 1, &names[1], &defaults[1]),
    PRM_Template()
};

OP_ERROR
SOP_PointsFromVoxels::cookMySop(OP_Context &context)
{
    fpreal 			now;
    unsigned			primnum;
    bool                        cull;

    GA_Offset                   ptOff;

    const GU_Detail		*input_geo;
    const GEO_Primitive		*prim;
    const GEO_PrimVolume	*vol;

    UT_Vector3			pos;
    UT_VoxelArrayIteratorF	vit;

    now = context.getTime();

    if (lockInputs(context) >= UT_ERROR_ABORT)
        return error();

    // Get the primitive number.
    primnum = PRIM(now);

    // Check for culling.
    cull = CULL(now);

    // Clear out the detail since we only want our new points.
    gdp->clearAndDestroy();

    // Get the input geometry as read only.
    GU_DetailHandleAutoReadLock gdl(inputGeoHandle(0));
    input_geo = gdl.getGdp();

    // Primitive number is valid.
    if (primnum < input_geo->getNumPrimitives())
    {
	// Get the primitive we need.
	prim = input_geo->primitives()(primnum);
	// The primitive is a volume primitive.
	if (prim->getTypeId().get() == GEO_PRIMVOLUME)
	{
	    // Get the actual PrimVolume.
	    vol = (const GEO_PrimVolume *)prim;

            // Get a voxel read handle from the primitive.
	    UT_VoxelArrayReadHandleF	vox(vol->getVoxelHandle());

            // Attach the voxel iterator to the handle.
	    vit.setHandle(vox);

            // Iterate over all the voxels.
	    for (vit.rewind(); !vit.atEnd(); vit.advance())
	    {
                // If we are culling empty voxels and this voxel's
                // value is 0 we skip it.
                if (cull && vit.getValue() == 0)
                    continue;
                // Convert the voxel index to a position.
                vol->indexToPos(vit.x(), vit.y(), vit.z(), pos);

                // Create a point and set it to the position of the
                // voxel.
                ptOff = gdp->appendPointOffset();
                gdp->setPos3(ptOff, pos);
	    }
	}
	// Primitive isn't a volume primitive.
	else
	    addError(SOP_MESSAGE, "Not a volume primitive.");
    }
    // Picked a primitive number that is out of range.
    else
	addWarning(SOP_MESSAGE, "Invalid source index. Index out of range.");

    unlockInputs();
    return error();
}

