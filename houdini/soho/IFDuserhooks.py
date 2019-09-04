"""This script is executed by SOHO during IFD generation."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.sohohooks.manager import MANAGER


# =============================================================================
# FUNCTIONS
# =============================================================================

def call(hook_name="", *args, **kwargs):  # pylint: disable=keyword-arg-before-vararg
    """Hook callback function.

    :param hook_name: The name of the hook to call.
    :type hook_name: str
    :return: Whether or not code should continue after the hook.
    :rtype: bool

    """
    return MANAGER.call_hook(hook_name, *args, **kwargs)
