"""Define custom functions that act as event signaling callbacks."""

# =============================================================================
# IMPORTS
# =============================================================================

# Future
from __future__ import annotations

# Standard Library
import atexit
from typing import Any

# Houdini Toolbox
from houdini_toolbox.events.manager import run_event
from houdini_toolbox.events.types import HipFileEvents, SceneEvents

# Houdini
import hou

# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _atexit_callback(
    *args: Any, **kwargs: Any
) -> None:  # pylint: disable=unused-argument
    """Run SceneEvents.Exit events.

    :return:

    """
    run_event(SceneEvents.Exit)


def _emit_ui_available(
    *args: Any, **kwargs: Any
) -> None:  # pylint: disable=unused-argument
    """Run SceneEvents.WhenUIAvailable events.

    :return:

    """
    run_event(SceneEvents.WhenUIAvailable)


def _hip_event_callback(event_type: hou.hipFileEventType) -> None:
    """Run HipFileEvents events

    :param event_type: The hip file event type which is running.
    :return:

    """
    event_name = getattr(HipFileEvents, event_type.name(), None)

    if event_name is not None:
        scriptargs = {"hip_file_event_type": event_type}

        run_event(event_name, scriptargs)


def _register_when_ui_available() -> None:
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


def register_callbacks() -> None:
    """Register any dynamic callback functions.

    :return:

    """
    atexit.register(_atexit_callback)

    if hou.isUIAvailable():
        _register_when_ui_available()

    hou.hipFile.addEventCallback(_hip_event_callback)
