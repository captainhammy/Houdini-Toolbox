/*
 * Produced by:
 *      Graham Thompson
 *      captainhammy@gmail.com
 *      www.captainhammy.com
 *
 * Description:
 * 	Run a script on render.
 *
 * Name: ROP_Script.h
 *
*/

#ifndef __ROP_Script_h__
#define __ROP_Script_h__

#include <ROP/ROP_Node.h>

class OP_TemplatePair;
class OP_VariablePair;

class ROP_Script: public ROP_Node
{
public:
    static OP_Node		*myConstructor(OP_Network *,
					       const char *,
					       OP_Operator *);
    static OP_TemplatePair	*getTemplatePair();
    static OP_VariablePair	*getVariablePair();

protected:
				ROP_Script(OP_Network *,
					   const char *,
					   OP_Operator *);
    virtual ~ROP_Script() {};
    virtual int		        startRender(int nframes, fpreal s, fpreal e);
    virtual ROP_RENDER_CODE	renderFrame(fpreal time, UT_Interrupt *boss);
    virtual ROP_RENDER_CODE	endRender();

private:
    void 			LANGUAGE(UT_String &str, fpreal t) { evalString(str, "language", 0, t); }
    void 			COMMAND(UT_String &str, fpreal t) { evalString(str, "command", 0, t); }
    fpreal			myEndTime;

};

#endif

