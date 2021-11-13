"""Initialize the aovs package."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox
from houdini_toolbox.sohohooks.aovs.manager import AOV_MANAGER as _AOV_MANAGER
from houdini_toolbox.sohohooks.manager import HOOK_MANAGER as _HOOK_MANAGER

# =============================================================================

# Register the aov adding function with the soho hook manager so it will
# function.
_HOOK_MANAGER.register_hook("post_cameraDisplay", _AOV_MANAGER.add_aovs_to_ifd)
