"""Initialize the aovs package."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.sohohooks.aovs.manager import AOV_MANAGER as _AOV_MANAGER
from ht.sohohooks.manager import HOOK_MANAGER as _HOOK_MANAGER

# =============================================================================

# Register the aov adding function with the soho hook manager so it will
# function.
_HOOK_MANAGER.register_hook("post_cameraDisplay", _AOV_MANAGER.add_aovs_to_ifd)
