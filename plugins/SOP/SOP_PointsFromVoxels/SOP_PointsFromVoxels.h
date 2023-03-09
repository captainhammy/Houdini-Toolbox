#ifndef __SOP_PointsFromVoxels_h__
#define __SOP_PointsFromVoxels_h__

#include <SOP/SOP_Node.h>

class SOP_PointsFromVoxels: public SOP_Node
{
public:
    static OP_Node      *myConstructor(OP_Network *,
                                       const char *,
                                       OP_Operator *);
    static PRM_Template myTemplateList[];

protected:
                        SOP_PointsFromVoxels(OP_Network *,
                                             const char *,
                                             OP_Operator *);
    virtual             ~SOP_PointsFromVoxels() {};
    virtual OP_ERROR    cookMySop(OP_Context &context);

private:
    unsigned            PRIM(fpreal t) { return evalInt("prim", 0, t); }
    unsigned            CULL(fpreal t) { return evalInt("cull", 0, t); }
    unsigned            STORE(fpreal t) { return evalInt("store", 0, t); }

};

#endif
