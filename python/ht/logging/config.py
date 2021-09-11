"""Configure logging for Houdini-Toolbox."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import json
import logging.config
import os

# =============================================================================
# FUNCTIONS
# =============================================================================


def init_config():
    """Load logger config from file.

    :return:

    """
    config_path = os.path.join(os.path.dirname(__file__), "config.json")

    if os.path.exists(config_path):
        with open(config_path, "r") as handle:
            config = json.load(handle)
            logging.config.dictConfig(config)
