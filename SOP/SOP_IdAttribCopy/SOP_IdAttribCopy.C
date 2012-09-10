/*
 * Produced by:
 *      Graham Thompson
 *      captainhammy@gmail.com
 *      www.captainhammy.com
 *
 * Description:
 *      Copy point attributes based on the 'id' attribute instead of the
 *	point number.
 *
 * Name: SOP_IdAttribCopy.C
 * 
*/

#include "SOP_IdAttribCopy.h"

#include <CH/CH_Manager.h>
#include <GA/GA_AttributeRefMap.h>
#include <GA/GA_PageIterator.h>
#include <GA/GA_SplittableRange.h>
#include <OP/OP_Operator.h>
#include <OP/OP_OperatorTable.h>
#include <PRM/PRM_Include.h>
#include <UT/UT_BitArray.h>
#include <UT/UT_DSOVersion.h>
#include <UT/UT_WorkArgs.h>

// This class is used to copy point attributes in a threaded manner.
class AttributeIdCopier {
public:
    AttributeIdCopier(const GA_AttributeRefMap *hmap,
                      const GA_Attribute *id,
                      const IdOffsetMap *id_map,
                      UT_BitArray *matches):
        myAttribMap(hmap), myId(id), myIdMap(id_map), myMatches(matches) {}

    // The function that is called by UTparallelFor to do the work.
    void operator()(const GA_SplittableRange &range) const
    {
        exint                   id;

        GA_Detail               *dest;
        GA_Offset               start, end;
        GA_ROPageHandleI        id_ph(myId);

        IdOffsetMap::const_iterator map_it;

        dest = myAttribMap->getDestDetail();

        // Iterate over the pages.
        for (GA_PageIterator pit = range.beginPages(); !pit.atEnd(); ++pit)
        {
            // Set the handle to this page.
            id_ph.setPage(*pit);

            // Get the offsets in the page.
            for (GA_Iterator it(pit.begin()); it.blockAdvance(start, end); )
            {
                // Iterate over the offsets in the page.
                for (GA_Offset pt = start; pt < end; ++pt)
                {
                    // Get the id value for this point.
                    id = id_ph.get(pt);
                    // Try to find the corresponding id.
                    map_it = myIdMap->find(id);
                    // If the iterator isn't at the end, copy the value.
                    if (map_it != myIdMap->end())
                    {
                        // Copy the point attributes from the offset pointed
                        // to by the found 'id' value to the current point.
                        myAttribMap->copyValue(GA_ATTRIB_POINT,
                                               pt,
                                               GA_ATTRIB_POINT,
                                               (*map_it).second);

                        // If the bit array is valid, set this index to true.
                        if (myMatches)
                            myMatches->setBit(dest->pointIndex(pt), true);
                    }
                }
            }
        }
    }

private:
    const GA_AttributeRefMap    *myAttribMap;
    const GA_Attribute          *myId;
    const IdOffsetMap           *myIdMap;
    UT_BitArray                 *myMatches;

};

void 
newSopOperator(OP_OperatorTable *table)
{
    table->addOperator(
        new OP_Operator("idattribcopy",
                        "IdAttribCopy",
                        SOP_IdAttribCopy::myConstructor,
                        SOP_IdAttribCopy::myTemplateList,
                        2,
                        2,
                        0)
    );
}

OP_Node *
SOP_IdAttribCopy::myConstructor(OP_Network *net, 
                                const char *name, 
                                OP_Operator *op)
{
    return new SOP_IdAttribCopy(net, name, op);
}

SOP_IdAttribCopy::SOP_IdAttribCopy(OP_Network *net,
                                   const char *name, 
                                   OP_Operator *op):
    SOP_Node(net, name, op), myGroup(0) {}

unsigned
SOP_IdAttribCopy::disableParms()
{
    fpreal	t = CHgetEvalTime();
    unsigned 	changed;
    bool 	group;


    // Are we grouping the matched points?
    group = GROUPMATCHED(t);

    // Enable the "Group Name" field.
    changed = enableParm("groupname", group);

    return changed;
}

static PRM_Name names[] =
{
    PRM_Name("group", "Group"),
    PRM_Name("attributes", "Attributes to Copy"),
    PRM_Name("copyp", "Accept \"P\""),
    PRM_Name("creategroup", "Group Matched Points"),
    PRM_Name("groupname", "Group Name"),
};

static PRM_Default defaults[] =
{
    PRM_Default(0, ""),
    PRM_Default(0, "*"),
    PRM_Default(0),
    PRM_Default(0),
    PRM_Default(0, "match"),
};

static PRM_ChoiceList attribMenu((PRM_ChoiceListType)(PRM_CHOICELIST_TOGGLE),
                                 &SOP_IdAttribCopy::buildMenu);

PRM_Template
SOP_IdAttribCopy::myTemplateList[] = {
    PRM_Template(PRM_STRING, 1, &names[0], &defaults[0], &SOP_Node::pointGroupMenu),
    PRM_Template(PRM_STRING, 1, &names[1], &defaults[1], &attribMenu),
    PRM_Template(PRM_TOGGLE, 1, &names[2], &defaults[2]),
    PRM_Template(PRM_TOGGLE, 1, &names[3], &defaults[3]),
    PRM_Template(PRM_STRING, 1, &names[4], &defaults[4]),
    PRM_Template()
};

bool
SOP_IdAttribCopy::validateAttrib(const GA_Attribute *attribute, void *data)
{
    // If the attribute's name is 'id', return false.
    if(strcmp(attribute->getName(), "id") == 0)
        return false;

    return true;
}

void
SOP_IdAttribCopy::buildMenu(void *data,
                            PRM_Name *menu,
                            int list_size,
                            const PRM_SpareData *,
                            const PRM_Parm *)
{
    // Get the instance of the operator.
    SOP_IdAttribCopy *me = (SOP_IdAttribCopy *)data;

    // Populate the menu with point attribute names as long as they
    // aren't the 'id' attribute.
    me->fillAttribNameMenu(menu,
                           100,
                           GEO_POINT_DICT,
                           1,
                           &SOP_IdAttribCopy::validateAttrib);
}


OP_ERROR
SOP_IdAttribCopy::cookInputGroups(OP_Context &context, int alone)
{
    // If we are called by the handle, then "alone" equals 1.  In that
    // case, we have to lock the inputs oursevles, and unlock them
    // before exiting this method.
    if (alone)
        if (lockInputs(context) >= UT_ERROR_ABORT)
            return error();

    UT_String    grp_name;

    // The "gdp" variable is only available if we are called from the SOP
    // itself.  So, if we are called by a handle, we have to get the
    // geometry oursevles.
    GU_Detail   *pgdp = alone ? (GU_Detail *)inputGeo(0, context) : gdp;

    myGroup = 0;

    // Get the group string.
    GROUP(grp_name, context.getTime());

    // If the group string is not null, then we try to parse the group.
    if (grp_name.isstring())
    {
        myGroup = parsePointGroups((const char *)grp_name, pgdp);

        // If the group is not valid, then the group string is invalid
        // as well.  Thus, we add an error to this SOP.
        if (!myGroup)
        {
            addError(SOP_ERR_BADGROUP, grp_name);
        }
        else if (!alone)
        {
            // If the parsed group is valid, then we want to highlight
            // only the group.  The second argument of "1" means that
            // we want the selection to have the same type as our group.
            select(*const_cast<GA_PointGroup*>(myGroup), 1);
        }
    }
    else if (!alone)
    {
        // If no group string is specified, then we operate on the entire
        // geometry, so we highlight every point for this SOP.
        select(GU_SPoint);
    }

    // This is where we notify our handles (if any) if the inputs have changed.
    checkInputChanged(0, -1, myDetailGroupPair, pgdp, myGroup);

    // If we are called by the handles, then we have to unlock our inputs.
    if (alone)
    {
        destroyAdhocGroups();
        unlockInputs();
    }

    return error();
}

OP_ERROR
SOP_IdAttribCopy::cookMySop(OP_Context &context)
{
    bool                        group_matched;
    fpreal 		        now;
    exint                       id; 

    GA_Offset                   start, end;

    GA_PointGroup               *group;

    const GA_Attribute          *source_attr;
    const GA_AttributeDict      *dict;
    GA_ROAttributeRef           id_gah, srcid_gah, attr_gah;
    GA_ROPageHandleI            srcid_ph;

    const GU_Detail             *src_geo;

    UT_BitArray                 matches;
    UT_String                   attribute_name, pattern, group_name;
    UT_WorkArgs                 tokens;
    
    IdOffsetMap                 id_map;

    now = context.getTime();

    if (lockInputs(context) >= UT_ERROR_ABORT)
        return error();

    // Duplicate the incoming geometry.
    duplicateSource(0, context);

    if (error() < UT_ERROR_ABORT && cookInputGroups(context) < UT_ERROR_ABORT)
    {
        // Get the 2nd input geometry as read only.
        GU_DetailHandleAutoReadLock source_gdl(inputGeoHandle(1));
        src_geo = source_gdl.getGdp();

        // Construct an attribute reference map to map attributes.
        GA_AttributeRefMap hmap(*gdp, src_geo);

        // Get the attribute selection string.
        ATTRIBUTES(pattern, now);
        
        // Try to find the 'id' point attribute on the 1st input geometry.
        id_gah = gdp->findPointAttribute(GA_SCOPE_PUBLIC, "id");
        // If it doesn't exist, display a node error message and exit.
        if (id_gah.isInvalid())
        {
            addError(SOP_MESSAGE, "Input 1 has no 'id' attribute.");
            unlockInputs();
            return error();
        }

        // Try to find the 'id' point attribute on the 2nd input geometry.
        srcid_gah = src_geo->findPointAttribute(GA_SCOPE_PUBLIC, "id");
        // If it doesn't exist, display a node error message and exit.
        if (srcid_gah.isInvalid())
        {
            addError(SOP_MESSAGE, "Input 2 has no 'id' attribute.");
            unlockInputs();
            return error();
        }
        // Bind the page handle to the attribute.
        srcid_ph.bind(srcid_gah.getAttribute());

        // Make sure we entered something.
        if (pattern.length() > 0)
        {
            // Tokenize the pattern.
            pattern.tokenize(tokens, " ");

            // Get the point attributes on the 2nd input geometry.
            dict = &src_geo->pointAttribs();

            // Iterate over all the point attributes.
            for (GA_AttributeDict::iterator it=dict->begin(GA_SCOPE_PUBLIC);
                 !it.atEnd();
                 ++it)
            {
                // The current attribute.
                source_attr = it.attrib();

                // Get the attribute name.
                attribute_name = source_attr->getName();

                // Skip the 'id' attribute.
                if (attribute_name == "id")
                    continue;

                // If the name doesn't match our pattern, skip it.
                if (!attribute_name.matchPattern(tokens))
                    continue;

                // Try to find the attribute on the first input geometry.
                attr_gah = gdp->findPointAttrib(*source_attr);
                // If it doesn't exist, create a new attribute.
                if (attr_gah.isInvalid())
                {
                    // Create a new point attribute on the current geometry
                    // that is the same as the source attribute.  Append it and
                    // the source to the map.
                    hmap.append(gdp->addPointAttrib(source_attr).getAttribute(),
                                source_attr);
                }
            }

            // If we are allowing 'P' to be copied, see if we should copy it.
            if (COPYP(now))
            {
                attribute_name = "P";
                // If 'P' matches our pattern, add it to the map.
                if (attribute_name.matchPattern(tokens))
                    hmap.append(gdp->getP(), src_geo->getP());
            }
        }
        // Selected nothing so don't do anything.
        else
        {
            unlockInputs();
            return error();
        }

        // Iterate over the 2nd input geometry points.
        for (GA_Iterator it(src_geo->getPointRange()); it.blockAdvance(start, end); )
        {
            // Set the page handle to the start of this page.
            srcid_ph.setPage(start);
            
            // Iterate over all the points in the page.
            for (GA_Offset pt = start; pt < end; ++pt)
            {
                // Get the 'id' value for the point.
                id = srcid_ph.get(pt);
                // Store a mapping from the 'id' to the point.
                id_map[id] = pt;
            }
        }

        // Check if we are supposed to group the matched points.
        group_matched = GROUPMATCHED(now);

        if (group_matched)
        {
            // Resize the bit array to match the number of points in
            // the detail.
            matches.resize(gdp->getNumPoints());
            
            // Get the group name to use.
            GROUPNAME(group_name, now);
            // Create a new point group.
            group = gdp->newPointGroup(group_name);
        }

        // Get the range to act on.
        GA_SplittableRange parallel_range(gdp->getPointRange(myGroup));

        // Engage attribute copying across threads.  If we are grouping
        // matched points, pass the bit array.  If not, pass 0.
        UTparallelFor(parallel_range,
                      AttributeIdCopier(&hmap,
                                        id_gah.getAttribute(),
                                        &id_map,
                                        group_matched ? &matches : 0)
                     );

        // If we are grouping, check the bit array and add the corresponding
        // indices to the new group.
        if (group_matched)
        {
            int i=0;
            for (matches.iterateInit(i); i >= 0; i = matches.iterateNext(i))
            {
                if (matches(i))
                    group->addOffset(gdp->pointOffset(i));
            }
        }
    }

    unlockInputs();
    return error();
}

const char *
SOP_IdAttribCopy::inputLabel(unsigned idx) const
{
    switch (idx)
    {
        case 0:
            return "Geometry to copy attributes to.";
        case 1:
            return "Geometry to copy attributes from.";
        default:
            return "Input";
    }
}

