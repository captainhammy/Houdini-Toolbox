"""This module contains utility functions for the ht package."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
from __future__ import absolute_import
import contextlib
import logging
import time

_logger = logging.getLogger(__name__)


# =============================================================================
# FUNCTIONS
# =============================================================================


@contextlib.contextmanager
def timer(label=None):
    """Context manager for outputting timing information.

    >>> with ht.utils.timer("sleeping"):
    ...     time.sleep(2)
    ...
    'sleeping - 2.00206804276'

    :param label: Optional label for output.
    :type label: str
    :return:


    """
    # Start time.
    t = time.time()

    try:
        yield

    finally:
        duration = time.time() - t

        if label is not None:
            _logger.info("%s - %s", label, duration)
        else:
            _logger.info(duration)


@contextlib.contextmanager
def restore_update_mode(update_mode):
    """Set a UI update mode and restore the current mode on exit.

    >>> with ht.utils.restore_update_mode(hou.updateMode.Manual):
    ...     # do some stuff while it is in manual mode
    ...

    Original update mode restored after with

    :param update_mode: The update mode to set for the duration.
    :type update_mode: hou.updateMode
    :return:

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
