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
 * Name: SOP_PrimGroupCentroid.h
 *
 * Version: 3.0
*/

#ifndef __SOP_PrimGroupCentroid_h__
#define __SOP_PrimGroupCentroid_h__

#include <SOP/SOP_Node.h>

class SOP_PrimGroupCentroid: public SOP_Node
{
public:
    static OP_Node 	*myConstructor(OP_Network *, 
				       const char *, 
				       OP_Operator *);
    static PRM_Template myTemplateList[];

protected:
			SOP_PrimGroupCentroid(OP_Network *,
					      const char *, 
					      OP_Operator *);
    virtual		~SOP_PrimGroupCentroid() {};
    virtual OP_ERROR	cookMySop(OP_Context &context);
    virtual unsigned	disableParms();

private:
    exint		METHOD(fpreal t) { return evalInt("method", 0, t); }
    void		GROUP(UT_String &str, fpreal t)	{ evalString(str, "group", 0, t); }
    exint		USENAME(fpreal t) { return evalInt("useName", 0, t); }
    bool		STORE(fpreal t) { return evalInt("store", 0, t); }
    void		ATTRIB(UT_String &str, fpreal t) { evalString(str, "name", 0, t); }
    void		centerOfMass(GA_Range&,
				     const GA_PrimitiveList&,
				     UT_Vector3&);
    void		baryCenter(const GU_Detail *,
				   UT_BitArray&,
				   GA_Range&,
				   const GA_PrimitiveList&,
				   UT_Vector3&);

};

#endif
