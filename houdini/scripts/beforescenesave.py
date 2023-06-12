"""Perform any registered before scene save events."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox
from houdini_toolbox.events import SceneEvents, run_event

# =============================================================================

run_event(SceneEvents.PreSave, kwargs)
