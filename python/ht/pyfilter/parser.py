"""This module contains functions used to parse PyFilter command line options.

"""

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
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _buildParser():
    """Build the PyFilter argument parser."""
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


def _createPropertySetting(stage_name, property_name, property_block):
    """Build an appropriate PropertySetting object for the property.

    If the property block contains a 'mask' field then a MaskedPropertySetting
    is created to handle masking.

    """
    # Handle masked properties.
    if "mask" in property_block:
        # Filter a plane.
        if stage_name == "plane":
            return MaskedPropertySetting(
                property_name,
                property_block,
                "plane:variable"
            )

        # Something involving an actual object.
        elif stage_name in ("fog", "light", "instance"):
            return MaskedPropertySetting(
                property_name,
                property_block,
                "object:name"
            )

        # If masking is specified but we don't know how to handle it, log a
        # warning message.  We will still return a regular PropertySetting
        # object though.
        else:
            logging.warning(
                "No masking available for {}:{}.".format(
                    stage_name,
                    property_name
                )
            )

    # Generic property setting.
    return PropertySetting(property_name, property_block)


def _parseArgs():
    """Parse the command line args."""
    # Create the parser.
    parser = _buildParser()

    # Parse for known args.
    filter_args, _ = parser.parse_known_args()

    return filter_args


# =============================================================================
# FUNCTIONS
# =============================================================================

def applyProperties(property_dict, stage):
    """Apply properties for a given stage."""
    # Ensure there are properties for this stage.
    if stage in property_dict:
        # Set each property.
        for prop in property_dict[stage]:
            prop.setProperty()


def buildPropertyInformation():
    """Build a dictionary of properties to apply based on the script args."""
    # Get the parsed args.
    filter_args = _parseArgs()

    # Get the logger.
    logger = logging.getLogger()

    # Since the log level argument is a string we should get the corresponding
    # enum from the module and set the log level using it.
    logger.setLevel(getattr(logging, filter_args.logLevel))

    property_dict = {}

    # Process custom files.
    if filter_args.file is not None:
        for path in filter_args.file:
            logging.debug("Reading properties from {}".format(path))

            # Load json data from the file.
            with open(path) as f:
                data = json.load(f, object_hook=ht.utils.convertFromUnicode)

            # Process each filter stage name and it's data.
            for stage_name, state_data in data.iteritems():
                # A list of properties for this stage.
                properties = []

                # Check if the stage should be disabled.
                if "disabled" in state_data:
                    if state_data["disabled"]:
                        logging.debug(
                            "Stage entry disabled: {}".format(stage_name)
                        )

                        continue

                    # If not, remove the disabled entry.
                    del(state_data["disabled"])

                # The data is stored by property name.
                for property_name, property_block in state_data.iteritems():
                    # If we want to set the same property with different
                    # settings multiple times (eg. different masks) we can
                    # have a list of objects instead.  In the case where we
                    # just have a single one (really a dictionary) then add it
                    # to a list so we can process it in a loop.
                    if isinstance(property_block, dict):
                        property_block = [property_block]

                    if isinstance(property_block, Iterable):
                        # Process any properties in the block.
                        for property_elem in property_block:
                            prop = _createPropertySetting(
                                stage_name,
                                property_name,
                                property_elem
                            )

                            properties.append(prop)

                # Store the properties for this stage.
                property_dict[str(stage_name)] = properties

    return property_dict

