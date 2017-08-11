"""Define custom functions that act as event signaling callbacks."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import atexit

# Houdini Toolbox Imports
from ht.events import SceneEvents, runEvent

# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

def _registerAtExit():
    """Register a dummy function with Python's atexit system that will run
    an event using the event system.

    """
    def _atExitCallback(*args, **kwargs):
        runEvent(SceneEvents.Exit)

    atexit.register(_atExitCallback)

# =============================================================================
# FUNCTIONS
# =============================================================================

def registerCallbacks():
    """Register any dynamic callback funcions."""
    _registerAtExit()
