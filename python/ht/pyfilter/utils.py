"""This module contains functions related to Mantra Python filtering."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import os

# Houdini Toolbox Imports
from ht.logger import logger

# =============================================================================
# FUNCTIONS
# =============================================================================

def build_pyfilter_command(pyfilter_args=None, pyfilter_path=None):
    """Build a PyFilter -P command."""
    import hou

    if pyfilter_args is None:
        pyfilter_args = []

    # If no path was passed, use the one located in the package.
    if pyfilter_path is None:
        try:
            pyfilter_path = hou.findFile("pyfilter/ht-pyfilter.py")

            # If we can't find the script them log an error and return nothing.
        except hou.OperationFailed:
            logger.error("Could not find pyfilter/ht-pyfilter.py")

            return ""

    # Ensure the script path exists.
    if not os.path.exists(pyfilter_path):
        raise OSError("No such file: {}".format(pyfilter_path))

    cmd = '-P "{} {}"'.format(pyfilter_path, " ".join(pyfilter_args))

    return cmd

