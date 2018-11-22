"""This module contains utility functions for the ht package."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import contextlib
import time

# =============================================================================
# FUNCTIONS
# =============================================================================

@contextlib.contextmanager
def timer(label=None):
    """Context manager for outputting timing information.

>>> with ht.utils.timer("sleeping"):
...     time.sleep(2)
...
sleeping - 2.00206804276

    """
    # Start time.
    t = time.time()

    try:
        yield

    finally:
        duration = time.time() - t

        if label is not None:
            print "{} - {}".format(label, duration)
        else:
            print duration


@contextlib.contextmanager
def updateMode(update_mode):
    """Context manager for setting the interface's update mode.

    update_mode should be one of hou.updateMode

    """
    import hou

    # Get the current update mode so it can be restored.
    current = hou.updateModeSetting()

    # Set the desired mode.
    hou.ui.setUpdateMode(update_mode)

    try:
        yield

    finally:
        # Restore the update mode.
        hou.ui.setUpdateMode(current)

