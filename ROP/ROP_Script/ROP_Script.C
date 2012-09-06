/*
 * Produced by:
 *      Graham Thompson
 *      captainhammy@gmail.com
 *      www.captainhammy.com
 *
 * Description:
 * 	Run a script on render.
 *
 * Name: ROP_Script.C
 *
 * Version: 1.0
*/

#include "ROP_Script.h"

#include <OP/OP_Director.h>
#include <OP/OP_Operator.h>
#include <OP/OP_OperatorTable.h>
#include <PRM/PRM_Include.h>
#include <PY/PY_Python.h>
#include <ROP/ROP_Templates.h>
#include <UT/UT_DSOVersion.h>

void
newDriverOperator(OP_OperatorTable *table)
{
    table->addOperator(
        new OP_Operator("script",
			"Script",
			ROP_Script::myConstructor,
			ROP_Script::getTemplatePair(),
			0,
			0,
			ROP_Script::getVariablePair(),
			OP_FLAG_GENERATOR)
    );
}

static PRM_Name names[] =
{
    PRM_Name("sepparm1", "Separator"),
    PRM_Name("command", "Command"),
    PRM_Name("language", "Language"),
    PRM_Name("sepparm2", "Separator"),
};

static PRM_Default defaults[] =
{
    PRM_Default(0, ""),
    PRM_Default(0, "hscript"),
};

static PRM_Name languages[] =
{
    PRM_Name("hscript", "Hscript"),
    PRM_Name("python", "Python"),
    PRM_Name(0)
};

static PRM_ChoiceList   languageMenu(
    (PRM_ChoiceListType)(PRM_CHOICELIST_EXCLUSIVE
                         | PRM_CHOICELIST_REPLACE),
    languages);

static PRM_Template *
getTemplates()
{
    static PRM_Template	*theTemplate = 0;

    if (theTemplate)
	return theTemplate;

    // Array large enough to hold our custom parms and all the
    // render script parms.
    theTemplate = new PRM_Template[17];

    // Separator between frame/take parms and the code parm.
    theTemplate[0] = PRM_Template(PRM_SEPARATOR, 1, &names[0]);

    // String paramater containing the code to run.  Horizontally
    // joined to the next parm.
    theTemplate[1] = PRM_Template(PRM_STRING, 1, &names[1], &defaults[0]);
    theTemplate[1].setJoinNext(true);

    // String menu to select the code language.
    theTemplate[2] = PRM_Template(PRM_STRING, 1, &names[2], &defaults[1], &languageMenu);
    theTemplate[2].setTypeExtended(PRM_TYPE_NO_LABEL);

    // Separator between the code parm and the render scripts.
    theTemplate[3] = PRM_Template(PRM_SEPARATOR, 1, &names[3]);

    theTemplate[4] = theRopTemplates[ROP_TPRERENDER_TPLATE];
    theTemplate[5] = theRopTemplates[ROP_PRERENDER_TPLATE];
    theTemplate[6] = theRopTemplates[ROP_LPRERENDER_TPLATE];

    theTemplate[7] = theRopTemplates[ROP_TPREFRAME_TPLATE];
    theTemplate[8] = theRopTemplates[ROP_PREFRAME_TPLATE];
    theTemplate[9] = theRopTemplates[ROP_LPREFRAME_TPLATE];

    theTemplate[10] = theRopTemplates[ROP_TPOSTFRAME_TPLATE];
    theTemplate[11] = theRopTemplates[ROP_POSTFRAME_TPLATE];
    theTemplate[12] = theRopTemplates[ROP_LPOSTFRAME_TPLATE];

    theTemplate[13] = theRopTemplates[ROP_TPOSTRENDER_TPLATE];
    theTemplate[14] = theRopTemplates[ROP_POSTRENDER_TPLATE];
    theTemplate[15] = theRopTemplates[ROP_LPOSTRENDER_TPLATE];

    theTemplate[16] = PRM_Template();

    return theTemplate;
}

OP_TemplatePair *
ROP_Script::getTemplatePair()
{
    static OP_TemplatePair *ropPair = 0;

    if (!ropPair)
    {
	OP_TemplatePair	*base;

	base = new OP_TemplatePair(getTemplates());
	ropPair = new OP_TemplatePair(ROP_Node::getROPbaseTemplate(), base);
    }

    return ropPair;
}

OP_VariablePair *
ROP_Script::getVariablePair()
{
    static OP_VariablePair *pair = 0;

    if (!pair)
	pair = new OP_VariablePair(ROP_Node::myVariableList);

    return pair;
}

OP_Node *
ROP_Script::myConstructor(OP_Network *net,
                          const char *name,
                          OP_Operator *op)
{
    return new ROP_Script(net, name, op);
}

ROP_Script::ROP_Script(OP_Network *net,
                       const char *name,
                       OP_Operator *entry):
    ROP_Node(net, name, entry) {}

int
ROP_Script::startRender(int /*nframes*/, fpreal tstart, fpreal tend)
{
    myEndTime = tend;
    if (error() < UT_ERROR_ABORT)
	executePreRenderScript(tstart);

    return 1;
}

ROP_RENDER_CODE
ROP_Script::renderFrame(fpreal time, UT_Interrupt *)
{
    UT_String                   command, language;

    OP_CommandManager           *cmd;
    OP_Director                 *director;

    PY_Result                   result;

    // Execute the pre-frame script.
    executePreFrameScript(time);

    // Get the language and command we want to run.
    LANGUAGE(language, time);
    COMMAND(command, time);

    // If it's 'python', execute the statements.
    if (language == "python")
    {
        // Run the statements in a new context and store the result.
        result = PYrunPythonStatementsInNewContext(command);
        // Add a node error if necessary.
        addPythonNodeError(result);
    }
    // If the language is 'hscript', or any other value, run the command
    // as hscript.
    else
    {
        // Get the scene director.
        director = OPgetDirector();
        // Get the command manager.
        cmd = director->getCommandManager();
        // Run the hscript command.
        cmd->execute(command);
    }

    // If no problems have been encountered, execute the post-frame
    // script.
    if (error() < UT_ERROR_ABORT)
	executePostFrameScript(time);

    return ROP_CONTINUE_RENDER;
}

ROP_RENDER_CODE
ROP_Script::endRender()
{
    if (error() < UT_ERROR_ABORT)
	executePostRenderScript(myEndTime);
    return ROP_CONTINUE_RENDER;
}

