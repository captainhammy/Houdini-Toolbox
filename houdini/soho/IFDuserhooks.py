"""This script is executed by SOHO during IFD generation."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.sohohooks.manager import HOOK_MANAGER


# =============================================================================
# FUNCTIONS
# =============================================================================


def call(
    hook_name: str = "", *args, **kwargs
) -> bool:  # pylint: disable=keyword-arg-before-vararg
    """Hook callback function.

    :param hook_name: The name of the hook to call.
    :return: Whether or not code should continue after the hook.

    """
    return HOOK_MANAGER.call_hook(hook_name, *args, **kwargs)
