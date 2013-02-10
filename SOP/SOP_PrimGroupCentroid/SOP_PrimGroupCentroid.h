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

// Simple pair to pass along our gdp and attribute pattern args.
typedef std::pair<GU_Detail *, UT_WorkArgs*> AttrCopyPair;

class SOP_PrimGroupCentroid: public SOP_Node
{
public:
    static OP_Node      *myConstructor(OP_Network *,
                                       const char *,
                                       OP_Operator *);
    static PRM_Template myTemplateList[];
    static void         buildMenu(void *,
                                  PRM_Name *,
                                  int,
                                  const PRM_SpareData *,
                                  const PRM_Parm *);
    static bool         validateAttrib(const GA_Attribute *,
                                       void *);
    static int          copyLocalVariables(const char *,
                                           const char *,
                                           void *);

protected:
                        SOP_PrimGroupCentroid(OP_Network *,
                                              const char *,
                                              OP_Operator *);
    virtual             ~SOP_PrimGroupCentroid() {};
    virtual OP_ERROR    cookMySop(OP_Context &context);
    virtual unsigned    disableParms();
    virtual const char  *inputLabel(unsigned) const;

private:
    int                 MODE(fpreal t) { return evalInt("mode", 0, t); }
    int                 METHOD(fpreal t) { return evalInt("method", 0, t); }
    void                GROUP(UT_String &str, fpreal t) { evalString(str, "group", 0, t); }
    bool                STORE(fpreal t) { return evalInt("store", 0, t); }
    bool                COPY(fpreal t) { return evalInt("copyvariables", 0, t); }
    int                 BEHAVIOR(fpreal t) { return evalInt("behavior", 0, t); }
    void                ATTRIBUTES(UT_String &str, fpreal t) { evalString(str, "attributes", 0, t); }
    void                BIND(UT_String &str, fpreal t) { evalString(str, "bind_attributes", 0, t); }
    void                buildRefMap(fpreal,
                                    GA_AttributeRefMap &,
                                    UT_String &,
                                    const GU_Detail *,
                                    int,
                                    GA_AttributeOwner);
    int                 buildAttribData(int,
                                        const GU_Detail *,
                                        UT_Array<GA_Range> &,
                                        UT_StringArray &,
                                        UT_IntArray &);
    void                buildGroupData(UT_String &,
                                       const GU_Detail *,
                                       UT_Array<GA_Range> &,
                                       UT_StringArray &);
    void                boundingBox(const GU_Detail *,
                                    GA_Range &,
                                    const GA_PrimitiveList &,
                                    UT_Vector3 &);
    void                centerOfMass(GA_Range &,
                                     const GA_PrimitiveList &,
                                     UT_Vector3 &);
    void                baryCenter(const GU_Detail *,
                                   GA_Range &,
                                   const GA_PrimitiveList &,
                                   UT_Vector3 &);
    void                buildTransform(UT_Matrix4 &,
                                       const GU_Detail *,
                                       const UT_Vector3,
                                       GA_Offset);
    int                 buildCentroids(fpreal, int, int);
    int                 bindToCentroids(fpreal, int, int);

};

#endif
