/*
 * Produced by:
 *      Graham Thompson
 *      captainhammy@gmail.com
 *      www.captainhammy.com
 *
 * Description:
 *     	Create points at the centroid of primitives.
 * 
 * Name: SOP_PrimCentroid.h
 *
 * Version: 2.0
*/

#ifndef __SOP_PrimCentroid_h__
#define __SOP_PrimCentroid_h__

#include <SOP/SOP_Node.h>

class SOP_PrimCentroid: public SOP_Node
{
public:
    static OP_Node 	*myConstructor(OP_Network *, 
				       const char *, 
				       OP_Operator *);
    static PRM_Template myTemplateList[];

protected:
			SOP_PrimCentroid(OP_Network *, 
					 const char *, 
					 OP_Operator *);
    virtual		~SOP_PrimCentroid() {};
    virtual OP_ERROR	cookMySop(OP_Context &);

private:
    exint		METHOD(fpreal t) { return evalInt("method", 0, t); }

};

#endif
