"""This module contains functions related to Mantra Python filtering."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import logging
import os
from typing import List, Optional

_logger = logging.getLogger(__name__)


# =============================================================================
# FUNCTIONS
# =============================================================================


def build_pyfilter_command(
    pyfilter_args: Optional[List[str]] = None, pyfilter_path: Optional[str] = None
) -> str:
    """Build a PyFilter -P command.

    :param pyfilter_args: Optional list of args to pass to the command.
    :param pyfilter_path: Optional path to the filter script.
    :return: The constructed PyFilter command.

    """
    # Houdini
    import hou

    if pyfilter_args is None:
        pyfilter_args = []

    # If no path was passed, use the one located in the HOUDINI_PATH.
    if pyfilter_path is None:
        try:
            pyfilter_path = hou.findFile("pyfilter/ht-pyfilter.py")

            # If we can't find the script them log an error and return nothing.
        except hou.OperationFailed:
            _logger.error("Could not find pyfilter/ht-pyfilter.py")

            return ""

    else:
        # Ensure the script path exists.
        if not os.path.isfile(pyfilter_path):
            raise OSError("No such file: {}".format(pyfilter_path))

    cmd = '-P "{} {}"'.format(pyfilter_path, " ".join(pyfilter_args))

    return cmd
