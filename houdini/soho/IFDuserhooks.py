"""This script is executed by SOHO during IFD generation.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
import ht.sohohooks.manager

# =============================================================================
# FUNCTIONS
# =============================================================================

def call(hook_name="", *args, **kwargs):
    """Hook callback function."""
    manager = ht.sohohooks.manager.getManager()

    return manager.callHook(hook_name, *args, **kwargs)

