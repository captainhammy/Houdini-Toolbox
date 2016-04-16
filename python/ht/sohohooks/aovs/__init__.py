"""Initialize the aovs package."""

# =============================================================================
# IMPORTS
# =============================================================================

from ht.sohohooks.manager import getManager

import ht.sohohooks.aovs.aov
from ht.sohohooks.aovs.manager import AOVManager

# =============================================================================

hook_manager = getManager()

# Register the aov adding function with the soho hook manager so it will
# function.
hook_manager.registerHook(
    "post_cameraDisplay",
    AOVManager.addAOVsToIfd
)

