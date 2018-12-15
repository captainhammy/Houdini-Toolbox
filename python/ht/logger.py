"""Base logger for Houdini-Toolbox."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import logging
import logging.config
import os
import yaml

# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

def _get_default_log_level():
    """Get the initial log level.

    If $HT_LOG_LEVEL is set it will be used, otherwise the default will be
    "INFO".

    :return: The default log level.
    :rtype: int

    """
    level = os.getenv("HT_LOG_LEVEL", "INFO")

    return _log_level_from_string(level)


def _init_logger_config():
    """Load logger config from file.

    :return:

    """
    config_path = os.path.join(os.path.dirname(__file__), "loggers", "config.yaml")

    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)


def _log_level_from_string(level):
    """Get a logging level from a string.

    This will attempt to get the uppercase version of the level as an attribute
    from the logging module.

    :param level: The level as a string.
    :type level: str
    :return: A matching logging level, otherwise None.
    :rtype: int

    """
    return getattr(logging, level.upper())

# =============================================================================
# FUNCTIONS
# =============================================================================

def get_logger(name, level=None):
    """Get a named logger, optionally set to a specified level.

    :param name: The name of the logger.
    :type name: str
    :param level: The level to set.
    :type level: str
    :return: A logger with a given name.
    :rtype: logging.logger

    """
    _logger = logging.getLogger(name)

    if level is not None:
        _logger.setLevel(_log_level_from_string(level))

    # Set the logger to the default level.
    else:
        _logger.setLevel(_get_default_log_level())

    return _logger

# =============================================================================

_init_logger_config()

logger = get_logger("Houdini-Toolbox")
