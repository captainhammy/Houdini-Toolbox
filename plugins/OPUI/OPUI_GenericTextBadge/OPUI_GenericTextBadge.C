
#include <HOM/HOM_Module.h>

#include <OP/OP_Node.h>

#include <OPUI/OPUI_GraphTextBadge.h>
#include <OPUI/OPUI_GraphDisplayOptions.h>
#include <OPUI/OPUI_GraphProxyDescriptor.h>

#include <PY/PY_CPythonAPI.h>
#include <PY/PY_Python.h>
#include <PY/PY_InterpreterAutoLock.h>

#include <UT/UT_DSOVersion.h>
#include <UT/UT_Color.h>

static const UT_StringHolder icon_name("SOP_font");

static const UT_StringHolder data_name("ht_generic_text");
static const UT_StringHolder color_data_name("ht_generic_text_color");

bool
opuiGenericTextBadgeTest(const OPUI_GraphProxyDescriptor &desc,
	OP_Context &context,
	UT_StringHolder &text,
	UT_Color &clr)
{
    OP_Node	*node = static_cast<OP_Node *>(desc.myItem);

    UT_StringHolder generic_text, generic_text_color;
    UT_Color color;

    if (node && node->hasUserData(data_name))
    {
        node->getUserData(data_name, generic_text);

        if (generic_text.length() > 0)
        {
            text = generic_text;

            if (node->hasUserData(color_data_name))
            {
                node->getUserData(color_data_name, generic_text_color);
                color.setColorByName(generic_text_color);
            }

            else
            {
                color = UT_WHITE;
            }

            clr = color;

            return true;
        }
    }

    return false;
}

void
OPUIaddTextBadges(OPUI_GraphTextBadgeArray *add_textbadges)
{
    add_textbadges->append(
        OPUI_GraphTextBadge(
            "generictextbadge", OPUI_GraphTextBadge::theMainTextBadgeCategory,
            "HT Generic Text Badge", icon_name, 0.0,
            TEXTBADGEVIS_TRUNCATED,
            opuiGenericTextBadgeTest,
            TEXTBADGE_MULTI_THREADED
        )
    );
}


PY_PyObject *
Get_Badge_Data_Name(PY_PyObject*, PY_PyObject*)
{
    return PY_PyString_FromString(data_name.c_str());
}

PY_PyObject *
Get_Badge_Color_Data_Name(PY_PyObject*, PY_PyObject*)
{
    return PY_PyString_FromString(color_data_name.c_str());
}

void
HOMextendLibrary()
{
    {
	PY_InterpreterAutoLock interpreter_auto_lock;

        static PY_PyMethodDef hom_extension_methods[] = {
            {"get_generic_text_key", Get_Badge_Data_Name, PY_METH_VARARGS(), ""},
            {"get_generic_text_color_key", Get_Badge_Color_Data_Name, PY_METH_VARARGS(), ""},
            {NULL, NULL, 0, NULL}
        };

        PY_Py_InitModule("_ht_generic_text_badge", hom_extension_methods);
    }
}
