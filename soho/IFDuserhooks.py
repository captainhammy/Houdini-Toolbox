"""This script is executed by SOHO during IFD generation.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import traceback

# Houdini Imports
from IFDapi import ray_comment

# Custom Imports
import sohohooks.planes

# =============================================================================
# CONSTANTS
# =============================================================================

_HOOK_FUNCTIONS = {
    # Called after wrangling the camera.
    "post_cameraDisplay": (sohohooks.planes.addRenderPlanes,),
}

# =============================================================================
# FUNCTIONS
# =============================================================================

def call(hookName="", *args, **kwargs):
    """Hook callback function.

    Args:
        hookName="" : (str)
            SOHO hook function name.

        args : (list)
            Arguments passed to the hook function call.

        kwargs : (dict)
            Keyword arguments passed to the hook function call.

    Raises:
        N/A

    Returns:
        bool
            The result of the hook call.

    """
    # Try to get methods to call for this hook.
    methods = _HOOK_FUNCTIONS.get(hookName, ())

    for method in methods:
        # Try to call the function.
        try:
            result = method(*args, **kwargs)

        # Catch any exceptions.
        except Exception as e:
            # Write error information into the ifd.
            ray_comment(
                "Hook Error[{0}]: {1} {2}".format(hookName, __file__, str(e))
            )

            ray_comment(
                "Traceback:\n# {0}\n".format(
                        "\n#".join(traceback.format_exc().split('\n'))
                )
            )

        if result:
            return True

    return False

