/*
 * Produced by:
 *      Graham Thompson
 *      captainhammy@gmail.com
 *      www.captainhammy.com
 *
 * Description:
 *      Create points at the centroids of primitive groups, named primitives
 *      of classes.  If the second input is connected, use those points to
 *      transform the geometry.
 *
 * Name: SOP_PrimGroupCentroid.h
 *
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
    virtual const char  *inputLabel(unsigned) const;

private:
    exint		MODE(fpreal t) { return evalInt("mode", 0, t); }
    exint		METHOD(fpreal t) { return evalInt("method", 0, t); }
    void		GROUP(UT_String &str, fpreal t)	{ evalString(str, "group", 0, t); }
    bool		STORE(fpreal t) { return evalInt("store", 0, t); }
    exint		BEHAVIOR(fpreal t) { return evalInt("behavior", 0, t); }
    void		centerOfMass(GA_Range &,
				     const GA_PrimitiveList &,
				     UT_Vector3 &);
    void		baryCenter(const GU_Detail *,
				   GA_Range &,
				   const GA_PrimitiveList &,
				   UT_Vector3 &);
    void		buildTransform(UT_Matrix4 &,
				       const GU_Detail *,
				       const UT_Vector3,
				       GA_Offset);
    int			buildCentroids(fpreal, exint, exint);
    int			bindToCentroids(fpreal, exint, exint);

};

#endif
