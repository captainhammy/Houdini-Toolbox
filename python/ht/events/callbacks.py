"""Define custom functions that act as event signaling callbacks."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import atexit

# Houdini Toolbox Imports
from ht.events.manager import run_event
from ht.events.types import SceneEvents

# Houdini Imports
import hou

# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

def _atexit_callback(*args, **kwargs):
    """Run SceneEvents.Exit events.

    :return:

    """
    run_event(SceneEvents.Exit)


def _emit_ui_available(*args, **kwargs):
    """Run SceneEvents.WhenUIAvailable events.

    :return:

    """
    run_event(SceneEvents.WhenUIAvailable)


def _register_atexit():
    """Register a dummy function with Python's atexit system that will run
    an event using the event system.

    :return:

    """
    atexit.register(_atexit_callback)


def _register_when_ui_available():
    """Register a function emits the SceneEvents.WhenUIAvailable event.

    This will be emitted when the UI is first brought up and the event
    loop begins running.

    :return:

    """
    # Import here in case UI is not available.
    import hdefereval

    # Emit the event after the event loop has run once.
    hdefereval.executeDeferredAfterWaiting(_emit_ui_available, 1)


# =============================================================================
# FUNCTIONS
# =============================================================================

def register_callbacks():
    """Register any dynamic callback functions.

    :return:

    """
    _register_atexit()

    if hou.isUIAvailable():
        _register_when_ui_available()
