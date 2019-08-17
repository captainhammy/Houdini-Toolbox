
#include <HOM/HOM_Module.h>

#include <OP/OP_Node.h>

#include <OPUI/OPUI_GraphBadge.h>
#include <OPUI/OPUI_GraphDisplayOptions.h>
#include <OPUI/OPUI_GraphProxyDescriptor.h>

#include <PY/PY_CPythonAPI.h>
#include <PY/PY_Python.h>
#include <PY/PY_InterpreterAutoLock.h>

#include <UT/UT_DSOVersion.h>

static const UT_StringHolder icon_name("NETVIEW_cop2_info");

static const UT_StringHolder data_name("ht_generic_image");

bool
opuiGenericImageBadgeTest(const OPUI_GraphProxyDescriptor &desc,
        OPUI_GraphBadgeVisibility visibility,
        OP_Context &context,
        UT_StringHolder &icon,
        UT_Color &clr)
{
    OP_Node *node = static_cast<OP_Node *>(desc.myItem);

    UT_StringHolder image_name;

    if (node && node->hasUserData(data_name))
    {
        node->getUserData(data_name, image_name);

        if (image_name.length() > 0)
        {
            icon = UT_StringHolder(image_name);

	        return true;
        }
    }

    return false;
}

void
OPUIaddBadges(OPUI_GraphBadgeArray *add_badges)
{
    add_badges->append(
	    OPUI_GraphBadge(
            "generic_image_badge",
            OPUI_GraphBadge::theMainBadgeCategory,
            "HT Generic Image Badge",
            icon_name,
            BADGEVIS_NORMAL,
            opuiGenericImageBadgeTest,
            BADGE_MULTI_THREADED
        )
    );
}


PY_PyObject *
Get_Badge_Data_Name(PY_PyObject*, PY_PyObject*)
{
    return PY_PyString_FromString(data_name.c_str());
}


void
HOMextendLibrary()
{
    {
	PY_InterpreterAutoLock interpreter_auto_lock;

        static PY_PyMethodDef hom_extension_methods[] = {
            {"get_generic_image_key", Get_Badge_Data_Name, PY_METH_VARARGS(), ""},
            {NULL, NULL, 0, NULL}
        };

        PY_Py_InitModule("_ht_generic_image_badge", hom_extension_methods);
    }
}

