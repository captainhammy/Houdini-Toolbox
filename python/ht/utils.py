"""This module contains utility functions for the ht package."""

# =============================================================================
# IMPORTS
# =============================================================================

from __future__ import annotations

# Standard Library
import contextlib
import logging
import time
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import hou

_logger = logging.getLogger(__name__)


# =============================================================================
# FUNCTIONS
# =============================================================================


@contextlib.contextmanager
def restore_update_mode(update_mode: hou.updateMode):
    """Set a UI update mode and restore the current mode on exit.

    >>> with restore_update_mode(hou.updateMode.Manual):
    ...     # do some stuff while it is in manual mode
    ...

    Original update mode restored after with

    :param update_mode: The update mode to set for the duration.
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


@contextlib.contextmanager
def timer(label: Optional[str] = None):
    """Context manager for outputting timing information.

    >>> with timer("sleeping"):
    ...     time.sleep(2)
    ...
    'sleeping - 2.00206804276'

    :param label: Optional label for output.
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
