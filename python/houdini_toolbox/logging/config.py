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
    config_file = importlib.resources.open_text("houdini_toolbox.logging", "config.json")
    config = json.load(config_file)
    logging.config.dictConfig(config)
