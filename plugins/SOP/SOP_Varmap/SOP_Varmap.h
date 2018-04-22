/*
 * Produced by:
 *      Graham Thompson
 *      captainhammy@gmail.com
 *      www.captainhammy.com
 *
 * Description:
 *      Automatically generate local variable mappings.
 *
 * Name: SOP_Varmap.h
 *
*/

#ifndef __SOP_Varmap_h__
#define __SOP_Varmap_h__

#include <SOP/SOP_Node.h>

class SOP_Varmap: public SOP_Node
{
public:
    static OP_Node      *myConstructor(OP_Network *,
                                       const char *,
                                       OP_Operator *);
    static PRM_Template myTemplateList[];
    void                addMappings(const GA_AttributeDict *);

protected:
                        SOP_Varmap(OP_Network *,
                                   const char *,
                                   OP_Operator *);
    virtual             ~SOP_Varmap() {};
    virtual OP_ERROR    cookMySop(OP_Context &context);

private:
    unsigned            POINT(fpreal t) { return evalInt("point", 0, t); }
    unsigned            VERT(fpreal t) { return evalInt("vertex", 0, t); }
    unsigned            PRIM(fpreal t) { return evalInt("primitive", 0, t); }
    unsigned            DETAIL(fpreal t) { return evalInt("global", 0, t); }

};

#endif
