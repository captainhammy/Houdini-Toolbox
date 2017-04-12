"""Initialize ht.events."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.events.manager import registerEvent, registerFunction, runEvents

from ht.events.events import rop_render, scene_load

# Register the package's ROP render script events.
registerEvent(rop_render.RopRenderEvent())

# Register the package's SceneLoadEvent.
registerEvent(scene_load.SceneLoadEvent())

