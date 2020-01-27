"""Initialize the aovs package."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini-Toolbox Imports
from ht.sohohooks.aovs import manager
from ht.sohohooks.manager import MANAGER as _MANAGER

# =============================================================================

# Register the aov adding function with the soho hook manager so it will
# function.
_MANAGER.register_hook("post_cameraDisplay", manager.MANAGER.add_aovs_to_ifd)
