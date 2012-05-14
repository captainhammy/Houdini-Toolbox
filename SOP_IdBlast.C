/*
 * Produced by:
 *      Graham Thompson
 *      captainhammy@gmail.com
 *      www.captainhammy.com
 *
 * Description:
 *      Delete points by ID.
 *
 * Name: SOP_IdBlast.C
 * 
 * Version: 1.0
*/

#include "SOP_IdBlast.h"

#include <OP/OP_Operator.h>
#include <OP/OP_OperatorTable.h>
#include <PRM/PRM_Include.h>
#include <UT/UT_DSOVersion.h>
#include <UT/UT_WorkArgs.h>

void 
newSopOperator(OP_OperatorTable *table)
{
    table->addOperator(
        new OP_Operator("idblast",
                        "IdBlast",
                        SOP_IdBlast::myConstructor,
                        SOP_IdBlast::myTemplateList,
                        1,
                        1,
                        0)
    );
}

OP_Node *
SOP_IdBlast::myConstructor(OP_Network *net, 
                                const char *name, 
                                OP_Operator *op)
{
    return new SOP_IdBlast(net, name, op);
}

SOP_IdBlast::SOP_IdBlast(OP_Network *net,
                                   const char *name, 
                                   OP_Operator *op):
    SOP_Node(net, name, op) {}

static PRM_Name names[] =
{
    PRM_Name("ids", "Ids"),
};

static PRM_Default defaults[] =
{
    PRM_Default(0, ""),
};

PRM_Template
SOP_IdBlast::myTemplateList[] = {
    PRM_Template(PRM_STRING, 1, &names[0], &defaults[0]),
    PRM_Template()
};

int addOffsetToGroup(int num, int sec, void *data)
{
    GroupIdMapPair              *pair;

    GA_PointGroup               *group;

    IdOffsetMap                 *id_map;
    IdOffsetMap::const_iterator map_it;


    // Get the pair.
    pair = (GroupIdMapPair *)data;

    // Get the group and id map from the pair.
    group = pair->first;
    id_map = pair->second;

    // Try to find an id matching the current number.
    map_it = id_map->find(num);
    // If one exists, add the corresponding offset to the group.
    if (map_it != id_map->end())
        group->addOffset((*map_it).second);

    return 1;
}

OP_ERROR
SOP_IdBlast::cookMySop(OP_Context &context)
{
    fpreal 		        now;
    exint                       id; 

    GA_Offset                   start, end;

    GA_PointGroup               *group;

    GA_ROAttributeRef           id_gah;
    GA_ROPageHandleI            id_ph;

    UT_String                   pattern;
    UT_WorkArgs                 tokens;

    IdOffsetMap                 id_map, srcid_map;
    GroupIdMapPair              pair;

    now = context.getTime();

    if (lockInputs(context) >= UT_ERROR_ABORT)
        return error();

    // Duplicate the incoming geometry.
    duplicateSource(0, context);

    // Get the id pattern.
    IDS(pattern, now);
    // If it's emptry, don't do anything.
    if (pattern.length() == 0)
    {
        unlockInputs();
        return error();
    }

    // Tokenize the range so we can handle multiple blocks.
    pattern.tokenize(tokens, " ");

    // Try to find the 'id' point attribute on the 1st input geometry.
    id_gah = gdp->findPointAttribute(GA_SCOPE_PUBLIC, "id");
    // If it doesn't exist, display a node error message and exit.
    if (id_gah.isInvalid())
    {
        addError(SOP_MESSAGE, "Input 1 has no 'id' attribute.");
        unlockInputs();
        return error();
    }
  
    // Bind the page handles to the attributes.
    id_ph.bind(id_gah.getAttribute());

    // Iterate over all the points we selected.
    for (GA_Iterator it(gdp->getPointRange()); it.blockAdvance(start, end); )
    {
        // Set the page handle to the start of this block.
        id_ph.setPage(start);
        
        // Iterate over all the points in the block.
        for (GA_Offset pt = start; pt < end; ++pt)
        {
            // Get the 'id' value for the point.
            id = id_ph.get(pt);
            id_map[id] = pt;
        }
    }

    // Create the group.
    group = createAdhocPointGroup(*gdp);

    //  Add the group and the id map to the pair.
    pair.first = group;
    pair.second = &id_map;

    // Iterate over each block in the tokens and add any ids to the group.
    for (int i=0; i < tokens.getArgc(); ++i)
    {
        UT_String id_range(tokens[i]);
        id_range.traversePattern(-1, &pair, addOffsetToGroup);
    }

    // Destroy the points.
    gdp->destroyPointOffsets(GA_Range(*group));

    unlockInputs();
    return error();
}

