"""Perform any registered after scene save events."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.events import SceneEvents, run_event

# =============================================================================

run_event(SceneEvents.PostSave, kwargs) # pylint: disable=undefined-variable

