"""Initialize the aovs package."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini-Toolbox Imports
from ht.sohohooks.manager import MANAGER

from ht.sohohooks.aovs import manager

# =============================================================================

# Register the aov adding function with the soho hook manager so it will
# function.
MANAGER.register_hook(
    "post_cameraDisplay",
    manager.MANAGER.add_aovs_to_ifd
)

