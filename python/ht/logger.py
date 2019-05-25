"""Base logger for Houdini-Toolbox."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import json
import logging
import logging.config
import os

# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _init_logger_config():
    """Load logger config from file.

    :return:

    """
    config_path = os.path.join(os.path.dirname(__file__), "loggers", "config.json")

    if os.path.exists(config_path):
        with open(config_path, 'r') as handle:
            config = json.load(handle)
            logging.config.dictConfig(config)


# =============================================================================

_init_logger_config()

