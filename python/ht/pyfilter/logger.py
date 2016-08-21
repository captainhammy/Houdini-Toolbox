"""This module defines the logger for PyFilter operations."""

__author__ = "Graham Thompson"
__email__ = "captainhammy@gmail.com"

# =============================================================================
# IMPORTS
# =============================================================================

import logging

# =============================================================================

logger = logging.getLogger("PyFilter")

logger.setLevel(logging.DEBUG)

sh = logging.StreamHandler()

formatter = logging.Formatter(
    "%(levelname)s - %(asctime)s - %(message)s",
    "%H:%M:%S %Y-%m-%d"
)

sh.setFormatter(formatter)

logger.addHandler(sh)
