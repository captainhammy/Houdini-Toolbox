"""Initialize the events package."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.events.manager import registerEventBlock, registerEventGroup, registerFunction, runEvent

from ht.events.events import rop_render, scene_load

# Register the package's ROP render script events.
registerEventGroup(rop_render.RopRenderEvent())

# Register the package's SceneLoadEvent.
registerEventBlock(scene_load.SceneLoadEvent())

