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
 * Name: SOP_IdAttribCopy.h
 *
*/

#ifndef __SOP_IdAttribCopy_h__
#define __SOP_IdAttribCopy_h__

#include <boost/unordered_map.hpp>
#include <GA/GA_AttributeRefMap.h>
#include <GA/GA_SplittableRange.h>
#include <SOP/SOP_Node.h>

// Simple mapping to a boost::unordered_map that is meant to be a mapping
// between point id values and their corresponding point offset.
typedef boost::unordered_map<exint, GA_Offset> IdOffsetMap;

class SOP_IdAttribCopy: public SOP_Node
{
public:
    static OP_Node      *myConstructor(OP_Network *, 
				       const char *, 
				       OP_Operator *);
    static PRM_Template myTemplateList[];
    static void		buildMenu(void *,
				  PRM_Name *,
				  int,
				  const PRM_SpareData *,
				  const PRM_Parm *);
    static bool	        validateAttrib(const GA_Attribute *,
				       void *);
    virtual OP_ERROR             cookInputGroups(OP_Context &context, 
                                                int alone = 0);
protected:
			SOP_IdAttribCopy(OP_Network *, 
					 const char *, 
					 OP_Operator *);
    virtual		~SOP_IdAttribCopy() {};
    virtual OP_ERROR	cookMySop(OP_Context &);
    virtual unsigned	disableParms();
    virtual const char  *inputLabel(unsigned) const;

private:
    void		GROUP(UT_String &str, fpreal t) { evalString(str, "group", 0, t); }
    void		ATTRIBUTES(UT_String &str, fpreal t) { evalString(str, "attributes", 0, t); }
    bool		COPYP(fpreal t) { return evalInt("copyp", 0, t); }
    bool		GROUPMATCHED(fpreal t) { return evalInt("creategroup", 0, t); }
    void		GROUPNAME(UT_String &str, fpreal t) { evalString(str, "groupname", 0, t); }

    GU_DetailGroupPair	myDetailGroupPair;
    const GA_PointGroup *myGroup;

};

#endif
