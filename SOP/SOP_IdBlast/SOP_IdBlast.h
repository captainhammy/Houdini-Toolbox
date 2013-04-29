/*
 * Produced by:
 *      Graham Thompson
 *      captainhammy@gmail.com
 *      www.captainhammy.com
 *
 * Description:
 *      Delete points by ID.
 *
 * Name: SOP_IdBlast.h
 *
*/

#ifndef __SOP_IdBlast_h__
#define __SOP_IdBlast_h__

#include <boost/unordered_map.hpp>
#include <SOP/SOP_Node.h>

// Simple mapping to a boost::unordered_map that is meant to be a mapping
// between point id values and their corresponding point offset.
typedef boost::unordered_map<exint, GA_Offset> IdOffsetMap;

// An pair that contains a point group and an id map.
typedef std::pair<GA_PointGroup *, IdOffsetMap *> GroupIdMapPair;

class SOP_IdBlast: public SOP_Node
{
public:
    static OP_Node      *myConstructor(OP_Network *,
                                       const char *,
                                       OP_Operator *);
    static PRM_Template myTemplateList[];

protected:
                        SOP_IdBlast(OP_Network *,
                                    const char *,
                                    OP_Operator *);
    virtual             ~SOP_IdBlast() {};
    virtual OP_ERROR    cookMySop(OP_Context &);

private:
    void                GROUP(UT_String &str, fpreal t) { evalString(str, "group", 0, t); }
    bool                NEGATE(fpreal t) { return evalInt("negate", 0, t); }

};

#endif
