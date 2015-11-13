"""This module contains functions used to parse PyFilter command line options.

Synopsis
--------

Functions:
    applyProperties()
        Apply properties for a given stage.

    buildPropertyInformation()
        Build a dictionary of properties to apply based on the script args.

"""
__author__ = "Graham Thompson"
__email__ = "captainhammy@gmail.com"

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import argparse

# Houdini Toolbox Imports

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "buildParser",
]

# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

# -----------------------------------------------------------------------------
#    Name: _buildParser
#  Raises: N/A
# Returns: argparse.ArgumentParser:
#              The created argument parser.
#    Desc: Build the PyFilter argument parser.
# -----------------------------------------------------------------------------
def buildParser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-logLevel",
        action="store",
        default="INFO",
        choices=("CRITICAL", "DEBUG", "ERROR", "INFO", "WARNING"),
        help="The Python logging level"
    )

    return parser

