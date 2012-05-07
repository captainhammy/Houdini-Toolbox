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
 * Version: 1.0
*/

#include "SOP_IdAttribCopy.h"

#include <GA/GA_AttributeRefMap.h>
#include <GA/GA_PageIterator.h>
#include <GA/GA_SplittableRange.h>
#include <OP/OP_Operator.h>
#include <OP/OP_OperatorTable.h>
#include <PRM/PRM_Include.h>
#include <UT/UT_DSOVersion.h>
#include <UT/UT_WorkArgs.h>

// This class is used to copy point attributes in a threaded manner.
class AttributeIdCopier {
public:
    AttributeIdCopier(const GA_AttributeRefMap *hmap,
                      const GA_Attribute *id,
                      const IdOffsetMap *id_map):
        myAttribMap(hmap), myId(id), myIdMap(id_map) {}

    // The function that is called by UTparallelFor to do the work.
    void operator()(const GA_SplittableRange &range) const
    {
        exint                   id;

        GA_Offset               start, end;
        GA_ROPageHandleI        id_ph(myId);

        IdOffsetMap::const_iterator map_it;

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
                    }
                }
            }
        }
    }

private:
    const GA_AttributeRefMap    *myAttribMap;
    const GA_Attribute          *myId;
    const IdOffsetMap           *myIdMap;

};

// The function to run the threaded attribute copying.
void
copyById(const GA_Range &range,
         GA_AttributeRefMap *hmap,
         const GA_Attribute *id,
         IdOffsetMap *id_map)
{
    // Engage attribute copying across threads.
    UTparallelFor(GA_SplittableRange(range),
                  AttributeIdCopier(hmap, id, id_map));
}

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
    SOP_Node(net, name, op) {}

static PRM_Name names[] =
{
    PRM_Name("attributes", "Attributes to copy"),
    PRM_Name("copyp", "Accept \"P\""),
};

static PRM_Default defaults[] =
{
    PRM_Default(0, "*"),
    PRM_Default(0),
};

static PRM_ChoiceList attribMenu((PRM_ChoiceListType)(PRM_CHOICELIST_TOGGLE),
                                 &SOP_IdAttribCopy::buildMenu);

PRM_Template
SOP_IdAttribCopy::myTemplateList[] = {
    PRM_Template(PRM_STRING, 1, &names[0], &defaults[0], &attribMenu),
    PRM_Template(PRM_TOGGLE, 1, &names[1], &defaults[1]),
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
SOP_IdAttribCopy::cookMySop(OP_Context &context)
{
    fpreal 		        now;
    exint                       id; 

    GA_Offset                   start, end;

    const GA_Attribute          *source_attr;
    const GA_AttributeDict      *dict;
    GA_ROAttributeRef           id_gah, srcid_gah, attr_gah;
    GA_ROPageHandleI            srcid_ph;

    const GU_Detail             *src_geo;

    UT_String                   name, pattern;
    UT_WorkArgs                 tokens;
    
    IdOffsetMap                 id_map;

    now = context.getTime();

    if (lockInputs(context) >= UT_ERROR_ABORT)
        return error();

    // Duplicate the incoming geometry.
    duplicateSource(0, context);

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
            name = source_attr->getName();

            // Skip the 'id' attribute.
            if (name == "id")
                continue;

            // If the name doesn't match our pattern, skip it.
            if (!name.matchPattern(tokens))
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
            name = "P";
            // If 'P' matches our pattern, add it to the map.
            if (name.matchPattern(tokens))
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

    // Copy the attributes.
    copyById(gdp->getPointRange(), &hmap, id_gah.getAttribute(), &id_map);

    unlockInputs();
    return error();
}

