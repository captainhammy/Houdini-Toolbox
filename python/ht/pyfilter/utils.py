"""This module contains functions related to Mantra Python filtering."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import logging
import os

# =============================================================================
# GLOBALS
# =============================================================================

LOGGER = logging.getLogger(__name__)


# =============================================================================
# FUNCTIONS
# =============================================================================

def build_pyfilter_command(pyfilter_args=None, pyfilter_path=None):
    """Build a PyFilter -P command.

    :param pyfilter_args: Optional list of args to pass to the command.
    :type pyfilter_args: list(str)
    :param pyfilter_path: Optional path to the filter script.
    :type pyfilter_path: str
    :return: The constructed PyFilter command.
    :rtype: str

    """
    import hou

    if pyfilter_args is None:
        pyfilter_args = []

    # If no path was passed, use the one located in the package.
    if pyfilter_path is None:
        try:
            pyfilter_path = hou.findFile("pyfilter/ht-pyfilter.py")

            # If we can't find the script them log an error and return nothing.
        except hou.OperationFailed:
            LOGGER.error("Could not find pyfilter/ht-pyfilter.py")

            return ""

    # Ensure the script path exists.
    if not os.path.exists(pyfilter_path):
        raise OSError("No such file: {}".format(pyfilter_path))

    cmd = '-P "{} {}"'.format(pyfilter_path, " ".join(pyfilter_args))

    return cmd
