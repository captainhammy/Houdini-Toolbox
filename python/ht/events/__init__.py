"""Initialize the events package."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.events.events import rop_render, scene_load
from ht.events.manager import (
    register_event_group,
    register_function,
    register_item,
    run_event,
)
from ht.events.types import HipFileEvents, NodeEvents, RopEvents, SceneEvents


# =============================================================================


# Register the package's ROP render script events.
register_event_group(rop_render.RopRenderEvent())

register_function(scene_load.clear_session_settings, SceneEvents.Load)
