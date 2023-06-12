"""Test the houdini_toolbox.nodes.parameters module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Third Party
import pytest

# Houdini Toolbox
import houdini_toolbox.nodes.parameters

# Houdini
import hou

# Need to ensure the hip file gets loaded.
pytestmark = pytest.mark.usefixtures("load_module_test_file")


# =============================================================================
# TESTS
# =============================================================================


@pytest.mark.parametrize(
    "varname, expected_parms",
    (
        ("$BAR", ()),
        (
            "$HIP",
            (
                "/obj/geo1/font1/text",
                "/out/mantra1/vm_picture",
                "/out/mantra1/soho_diskfile",
                "/out/mantra1/vm_dcmfilename",
                "/out/mantra1/vm_dsmfilename",
                "/out/mantra1/vm_tmpsharedstorage",
                "/stage/rendergallerysource",
                "/tasks/topnet1/taskgraphfile",
                "/tasks/topnet1/checkpointfile",
                "/tasks/topnet1/localscheduler/pdg_workingdir",
            ),
        ),
        (
            "$HIPNAME",
            (
                "/out/mantra1/vm_picture",
                "/stage/rendergallerysource",
                "/tasks/topnet1/taskgraphfile",
                "/tasks/topnet1/checkpointfile",
                "/tasks/topnet1/localscheduler/tempdircustom",
            ),
        ),
        ("$HIPFILE", ("/obj/geo1/font2/text",)),
        (
            "F",  # Test var with no $ to handle auto adding.
            ("/obj/geo1/font1/text", "/tasks/topnet1/taskgraphfile"),
        ),
        ("$F4", ("/out/mantra1/vm_picture",)),
    ),
)
def test_find_parameters_using_variable(varname, expected_parms):
    """Test houdini_toolbox.nodes.parameters.find_parameters_using_variable()."""
    parms = {hou.parm(name) for name in expected_parms}

    result = houdini_toolbox.nodes.parameters.find_parameters_using_variable(varname)

    assert set(result) == parms


def test_find_parameters_with_value():
    """Test houdini_toolbox.nodes.parameters.find_parameters_with_value()."""
    result = houdini_toolbox.nodes.parameters.find_parameters_with_value("gaussian")
    assert result == (hou.parm("/out/mantra1/vm_pfilter"),)

    result = houdini_toolbox.nodes.parameters.find_parameters_with_value("render1")
    assert result == ()

    result = houdini_toolbox.nodes.parameters.find_parameters_with_value("render")
    assert result == (
        hou.parm("/obj/geo1/font1/text"),
        hou.parm("/out/mantra1/vm_picture"),
    )

    result = houdini_toolbox.nodes.parameters.find_parameters_with_value("renders")
    assert result == (hou.parm("/obj/geo1/font2/text"),)
