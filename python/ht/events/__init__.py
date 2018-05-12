"""Initialize the events package."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.events.events import aov_events , rop_render, scene_load
from ht.events.manager import registerEventBlock, registerEventGroup, registerFunction, runEvent
from ht.events.types import NodeEvents, RopEvents, SceneEvents

# =============================================================================

# Register the package's ROP render script events.
registerEventGroup(rop_render.RopRenderEvent())

# Register the package's SceneLoadEvent.
registerEventBlock(scene_load.SceneLoadEvent())

registerEventGroup(aov_events.AOVEvents())
