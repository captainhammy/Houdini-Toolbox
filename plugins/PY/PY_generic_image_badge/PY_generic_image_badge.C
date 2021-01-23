
#include <Python.h>

#include <HOM/HOM_Module.h>

#include <OP/OP_Node.h>

#include <OPUI/OPUI_GraphBadge.h>
#include <OPUI/OPUI_GraphDisplayOptions.h>
#include <OPUI/OPUI_GraphProxyDescriptor.h>
#include <OPUI/OPUI_GraphTextBadge.h>

#include <PY/PY_CPythonAPI.h>
#include <PY/PY_Python.h>
#include <PY/PY_InterpreterAutoLock.h>

#include <UT/UT_DSOVersion.h>
#include <UT/UT_Color.h>

#include "OPUI_GenericImageBadge.h"


PY_PyObject *
Get_Badge_Data_Name(PY_PyObject*, PY_PyObject*)
{
    return PY_PyString_FromString(GENERIC_IMAGE_BADGE_DATA_NAME.c_str());
}

extern "C" __attribute__((visibility("default"))) PyObject*

PyInit__ht_generic_image_badge(void)
{
    //
    // This is the initialization function that Python calls when
    // importing the extension module.
    //
    PY_PyObject *module = nullptr;

    {
        // A PY_InterpreterAutoLock will grab the Python global interpreter
        // lock (GIL).  It's important that we have the GIL before making
        // any calls into the Python API.
        PY_InterpreterAutoLock interpreter_auto_lock;
        // We'll create a new module named "_hom_extensions", and add functions
        // to it.  We don't give a docstring here because it's given in the
        // Python implementation below.
        static PY_PyMethodDef hom_extension_methods[] = {
            {"get_generic_image_key", Get_Badge_Data_Name, PY_METH_VARARGS(), ""},
            {NULL, NULL, 0, NULL}
        };

        module = PY_Py_InitModule("_ht_generic_image_badge", hom_extension_methods);
    }
    return reinterpret_cast<PyObject *>(module);
}

