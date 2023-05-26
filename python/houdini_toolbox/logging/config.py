"""Configure logging for Houdini-Toolbox."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import importlib.resources
import json
import logging.config

# =============================================================================
# FUNCTIONS
# =============================================================================


def init_config():
    """Load logger config from file.

    :return:

    """
    config_file = importlib.resources.files("houdini_toolbox.logging").joinpath("config.json")

    with config_file.open() as handle:
        config = json.load(handle)
        logging.config.dictConfig(config)
