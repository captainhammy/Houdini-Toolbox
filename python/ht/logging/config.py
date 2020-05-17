"""Configure logging for Houdini-Toolbox."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import json
import logging.config
import os

# Third Party Imports
import builtins

# =============================================================================
# FUNCTIONS
# =============================================================================


def init_config():
    """Load logger config from file.

    :return:

    """
    config_path = os.path.join(os.path.dirname(__file__), "config.json")

    if os.path.exists(config_path):
        # Use builtins.open() so we can mock this better between Python 2 and 3.
        with builtins.open(config_path, "r") as handle:
            config = json.load(handle)
            logging.config.dictConfig(config)
