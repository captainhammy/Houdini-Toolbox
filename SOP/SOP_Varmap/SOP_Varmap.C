/*
 * Produced by:
 *      Graham Thompson
 *      captainhammy@gmail.com
 *      www.captainhammy.com
 *
 * Description:
 *     	Automatically generate local variable mappings.
 *
 * Name: SOP_Varmap.C
 *
*/

#include "SOP_Varmap.h"

#include <PRM/PRM_Include.h>
#include <OP/OP_Operator.h>
#include <OP/OP_OperatorTable.h>
#include <UT/UT_DSOVersion.h>

void
newSopOperator(OP_OperatorTable *table)
{
    table->addOperator(
        new OP_Operator("varmap",
                        "Varmap",
                        SOP_Varmap::myConstructor,
                        SOP_Varmap::myTemplateList,
                        1,
                        1,
                        0)
    );
}

OP_Node *
SOP_Varmap::myConstructor(OP_Network *net,
                          const char *name,
                          OP_Operator *op)
{
    return new SOP_Varmap(net, name, op);
}

SOP_Varmap::SOP_Varmap(OP_Network *net,
                       const char *name,
                       OP_Operator *op):
    SOP_Node(net, name, op) {}

static PRM_Name names[] =
{
    PRM_Name("point", "Point Attributes"),
    PRM_Name("vertex", "Vertex Attributes"),
    PRM_Name("primitive", "Primitive Attributes"),
    PRM_Name("global", "Glboal Attributes"),
    PRM_Name(0)
};

static PRM_Default defaults[] =
{
    PRM_Default(1),
    PRM_Default(1),
    PRM_Default(1),
    PRM_Default(1),
};

PRM_Template
SOP_Varmap::myTemplateList[] = {
    PRM_Template(PRM_TOGGLE, 1, &names[0], &defaults[0]),
    PRM_Template(PRM_TOGGLE, 1, &names[1], &defaults[1]),
    PRM_Template(PRM_TOGGLE, 1, &names[2], &defaults[2]),
    PRM_Template(PRM_TOGGLE, 1, &names[3], &defaults[3]),
    PRM_Template()
};

void
SOP_Varmap::addMappings(const GA_AttributeDict *dict,
                        const GA_AIFSharedStringTuple *s_t,
                        GA_Attribute *varmap)
{
    GA_Attribute                *attrib;
    GA_AttributeDict::ordered_iterator  a_it;

    UT_String                   attr_name, new_name, upper_name;

    // Iterate over all the public attributes, in order.
    for (a_it=dict->obegin(GA_SCOPE_PUBLIC); !a_it.atEnd(); ++a_it)
    {
        // Get the actual attribute.
        attrib = *a_it;

        attr_name = attrib->getName();

        // Skip creating a reference to the 'varmap'.
        if (attr_name == "varmap")
            continue;

        // Get the name as upper case.
        upper_name = attrib->getName();
        upper_name.toUpper();

        // Build an attribute mapping string.
        new_name.sprintf("%s -> %s", attr_name.buffer(), upper_name.buffer());

        // Add it to the varmap.
        s_t->arrayAppendUniqueString(varmap, new_name);
    }
}

OP_ERROR
SOP_Varmap::cookMySop(OP_Context &context)
{
    fpreal 			now;

    const GA_AIFSharedStringTuple       *s_t;
    GA_Attribute                *varmap;
    const GA_AttributeDict      *dict;
    GA_RWAttributeRef           varmap_gah;

    now = context.getTime();

    if (lockInputs(context) >= UT_ERROR_ABORT)
        return error();

    duplicateSource(0, context);

    // Try to find the string attribute.
    varmap_gah = gdp->findStringTuple(GA_ATTRIB_DETAIL, "varmap");

    // If it doesn't exist, add it.
    if (varmap_gah.isInvalid())
    {
        varmap_gah = gdp->createStringAttribute(GA_ATTRIB_DETAIL, "varmap");
    }

    // Get the actual attribute.
    varmap = varmap_gah.getAttribute();

    // Get a shared string tuple from the attribute.
    s_t = varmap->getAIFSharedStringTuple();

    // Process each type of attribute.
    if (POINT(now))
    {
        dict = &gdp->pointAttribs();
        addMappings(dict, s_t, varmap);
    }

    if (VERT(now))
    {
        dict = &gdp->vertexAttribs();
        addMappings(dict, s_t, varmap);
    }

    if (PRIM(now))
    {
        dict = &gdp->primitiveAttribs();
        addMappings(dict, s_t, varmap);
    }

    if (DETAIL(now))
    {
        dict = &gdp->attribs();
        addMappings(dict, s_t, varmap);
    }

    unlockInputs();
    return error();
}

