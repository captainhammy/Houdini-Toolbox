/*
 * Produced by:
 *      Graham Thompson
 *      captainhammy@gmail.com
 *      www.captainhammy.com
 *
 * Description:
 *     	Copy point attributes based on the 'id' attribute instead of the
 *	point number.
 * 
 * Name: SOP_IdAttribCopy.h
 *
 * Version: 1.0
*/

#ifndef __SOP_IdAttribCopy_h__
#define __SOP_IdAttribCopy_h__

#include <boost/unordered_map.hpp>
#include <GA/GA_AttributeRefMap.h>
#include <GA/GA_AttributeRefMap.h>
#include <GA/GA_SplittableRange.h>
#include <SOP/SOP_Node.h>

// Simple mapping to a boost::unordered_map that is meant to be a mapping
// between point id values and their corresponding point offset.
typedef boost::unordered_map<exint, GA_Offset> IdOffsetMap;

class SOP_IdAttribCopy: public SOP_Node
{
public:
    static OP_Node 	*myConstructor(OP_Network *, 
				       const char *, 
				       OP_Operator *);
    static PRM_Template myTemplateList[];
    static void		buildMenu(void *,
				  PRM_Name *,
				  int,
				  const PRM_SpareData *,
				  const PRM_Parm *);
    static bool	     	validateAttrib(const GA_Attribute *,
				       void *);

    /// This method is created so that it can be called by handles.  It only
    /// cooks the input group of this SOP.  The geometry in this group is
    /// the only geometry manipulated by this SOP.
    virtual OP_ERROR             cookInputGroups(OP_Context &context, 
                                                int alone = 0);
protected:
			SOP_IdAttribCopy(OP_Network *, 
					 const char *, 
					 OP_Operator *);
    virtual		~SOP_IdAttribCopy() {};
    virtual OP_ERROR	cookMySop(OP_Context &);


    THREADED_METHOD4(SOP_IdAttribCopy, range.canMultiThread(), testBuild,
		     const GA_SplittableRange &, range,
		     GA_AttributeRefMap, hmap,
		     const GA_Attribute *, id_gah,
		     const IdOffsetMap &, id_map);

    void testBuildPartial(const GA_SplittableRange &range,
			  GA_AttributeRefMap hmap,
			  const GA_Attribute *id_gah,
			  const IdOffsetMap &id_map,
			  const UT_JobInfo &info);


private:
    void		GROUP(UT_String &str, fpreal t) { evalString(str, "group", 0, t); }
    void		ATTRIBUTES(UT_String &str, fpreal t) { evalString(str, "attributes", 0, t); }
    bool		COPYP(fpreal t) { return evalInt("copyp", 0, t); }


    /// This variable is used together with the call to the "checkInputChanged"
    /// routine to notify the handles (if any) if the input has changed.
    GU_DetailGroupPair   myDetailGroupPair;

    /// This is the group of geometry to be manipulated by this SOP and cooked
    /// by the method "cookInputGroups".
    const GA_PointGroup *myGroup;

};

#endif
