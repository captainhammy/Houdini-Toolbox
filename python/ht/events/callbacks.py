"""Define custom functions that act as event signaling callbacks."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import atexit

# Houdini Toolbox Imports
from ht.events.manager import run_event
from ht.events.types import HipFileEvents, SceneEvents

# Houdini Imports
import hou


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _atexit_callback(*args, **kwargs):  # pylint: disable=unused-argument
    """Run SceneEvents.Exit events.

    :return:

    """
    run_event(SceneEvents.Exit)


def _emit_ui_available(*args, **kwargs):  # pylint: disable=unused-argument
    """Run SceneEvents.WhenUIAvailable events.

    :return:

    """
    run_event(SceneEvents.WhenUIAvailable)


def _hip_event_callback(event_type):
    """Run HipFileEvents events

    :param event_type: The hip file event type which is running.
    :type event_type: hou.hipFileEventType
    :return:

    """
    event_name = getattr(HipFileEvents, event_type.name(), None)

    if event_name is not None:
        scriptargs = {"hip_file_event_type": event_type}

        run_event(event_name, scriptargs)


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
    atexit.register(_atexit_callback)

    if hou.isUIAvailable():
        _register_when_ui_available()

    hou.hipFile.addEventCallback(_hip_event_callback)
