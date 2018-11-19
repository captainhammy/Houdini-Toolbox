"""This script is executed by SOHO during IFD generation."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.sohohooks.manager import MANAGER

# =============================================================================
# FUNCTIONS
# =============================================================================

def call(hook_name="", *args, **kwargs):
    """Hook callback function."""
    return MANAGER.call_hook(hook_name, *args, **kwargs)

