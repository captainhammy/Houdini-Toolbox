#ifndef __SOP_DopImpactPoints_h__
#define __SOP_DopImpactPoints_h__

#include <SOP/SOP_Node.h>

class SOP_DopImpactPoints : public SOP_Node
{
public:
    static OP_Node      *myConstructor(OP_Network *,
                                       const char *,
                                       OP_Operator *);
    static PRM_Template myTemplateList[];

protected:
                        SOP_DopImpactPoints(OP_Network *,
                                            const char *,
                                            OP_Operator *);
    virtual             ~SOP_DopImpactPoints() {};
    virtual OP_ERROR    cookMySop(OP_Context &context);
    virtual unsigned    disableParms();

private:
    void                DOPPATH(UT_String &str, fpreal t) { evalString(str, "doppath", 0, t); }
    bool                NORMAL(fpreal t) { return evalInt("normal", 0, t); }
    bool                IMPULSE(fpreal t) { return evalInt("impulse", 0, t); }
    bool                SOURCEID(fpreal t) { return evalInt("sourceid", 0, t); }
    bool                OTHEROBJID(fpreal t) { return evalInt("otherobjid", 0, t); }

    unsigned            INSTANCES(fpreal t) { return evalInt("num_configs", 0, t); }
    bool                ENABLED(int i, fpreal t) { return evalIntInst("enable#", &i, 0, t); }
    void                OBJPATTERN(UT_String &str, int i, fpreal t) { return evalStringInst("objpattern#", &i, str, 0, t); }
    void                OBJMASK(UT_String &str, int i, fpreal t) { return evalStringInst("impactpattern#", &i, str, 0, t); }
    fpreal              THRESHOLD(int i, fpreal t) { return evalFloatInst("threshold#", &i, 0, t); }

};

#endif
