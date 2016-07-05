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
from collections import Iterable
import json
import logging

# Houdini Toolbox Imports
from ht.pyfilter.properties import MaskedPropertySetting, PropertySetting
import ht.utils

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "applyProperties",
    "buildPropertyInformation",
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
def _buildParser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-file",
        nargs=1,
        action="store",
        help="Use a file to define render properties to override.",
    )

    parser.add_argument(
        "-logLevel",
        action="store",
        default="INFO",
        choices=("CRITICAL", "DEBUG", "ERROR", "INFO", "WARNING"),
        help="The Python logging level"
    )

    return parser


# -----------------------------------------------------------------------------
#    Name: _createPropertySetting
#    Args: stageName : (str)
#              The name of the current stage.
#          propertyName : (str)
#              The name of the property to create.
#          propertyBlock : (dict)
#              The property information dictionary.
#  Raises: N/A
# Returns: MaskedPropertySetting|PropertySetting
#              The PropertySetting object for the property.
#    Desc: Build an appropriate PropertySetting object for the property.  If
#          the property block contains a 'mask' field then a
#          MaskedPropertySetting is created to handle masking.
# -----------------------------------------------------------------------------
def _createPropertySetting(stageName, propertyName, propertyBlock):
    # Handle masked properties.
    if "mask" in propertyBlock:
        # Filter a plane.
        if stageName == "plane":
            return MaskedPropertySetting(
                propertyName,
                propertyBlock,
                "plane:variable"
            )

        # Something involving an actual object.
        elif stageName in ("fog", "light", "instance"):
            return MaskedPropertySetting(
                propertyName,
                propertyBlock,
                "object:name"
            )

        # If masking is specified but we don't know how to handle it, log a
        # warning message.  We will still return a regular PropertySetting
        # object though.
        else:
            logging.warning(
                "No masking available for {}:{}.".format(
                    stageName,
                    propertyName
                )
            )

    # Generic property setting.
    return PropertySetting(propertyName, propertyBlock)


# -----------------------------------------------------------------------------
#    Name: _parseArgs
#  Raises: N/A
# Returns: argparse.Namespace:
#              The result of the argument parsing.
#    Desc: Parse the command line args.
# -----------------------------------------------------------------------------
def _parseArgs():
    # Create the parser.
    parser = _buildParser()

    # Parse for known args.
    filterArgs, _ = parser.parse_known_args()

    return filterArgs


# =============================================================================
# FUNCTIONS
# =============================================================================

def applyProperties(propertyDict, stage):
    """Apply properties for a given stage.

    Args:
        propertyDict : (dict)
            A dictionary whose keys are stage names and values are dictionaries
            containing PropertySetting objects.

        stage : (str)
            The name of the stage whose properties to apply.

    Raises:
        N/A

    Returns:
        None

    """
    # Ensure there are properties for this stage.
    if stage in propertyDict:
        # Set each property.
        for prop in propertyDict[stage]:
            prop.setProperty()


def buildPropertyInformation():
    """Build a dictionary of properties to apply based on the script args.

    Raises:
        N/A

    Returns:
        dict
            A dictionary whose keys are filter stage names and values are lists
            of PropertySetting objects for each stage.

    """
    # Get the parsed args.
    filterArgs = _parseArgs()

    # Get the logger.
    logger = logging.getLogger()

    # Since the log level argument is a string we should get the corresponding
    # enum from the module and set the log level using it.
    logger.setLevel(getattr(logging, filterArgs.logLevel))

    propertyDict = {}

    # Process custom files.
    if filterArgs.file is not None:
        for path in filterArgs.file:
            logging.debug("Reading properties from {}".format(path))

            # Load json data from the file.
            with open(path) as f:
                data = json.load(f, object_hook=ht.utils.convertFromUnicode)

            # Process each filter stage name and it's data.
            for stageName, stageData in data.iteritems():
                # A list of properties for this stage.
                properties = []

                # Check if the stage should be disabled.
                if "disabled" in stageData:
                    if stageData["disabled"]:
                        logging.debug(
                            "Stage entry disabled: {}".format(stageName)
                        )

                        continue

                    # If not, remove the disabled entry.
                    del(stageData["disabled"])

                # The data is stored by property name.
                for propertyName, propertyBlock in stageData.iteritems():
                    # If we want to set the same property with different
                    # settings multiple times (eg. different masks) we can
                    # have a list of objects instead.  In the case where we
                    # just have a single one (really a dictionary) then add it
                    # to a list so we can process it in a loop.
                    if isinstance(propertyBlock, dict):
                        propertyBlock = [propertyBlock]

                    if isinstance(propertyBlock, Iterable):
                        # Process any properties in the block.
                        for propertyElem in propertyBlock:
                            prop = _createPropertySetting(
                                stageName,
                                propertyName,
                                propertyElem
                            )

                            properties.append(prop)

                # Store the properties for this stage.
                propertyDict[str(stageName)] = properties

    return propertyDict

