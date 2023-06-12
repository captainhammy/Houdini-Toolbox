"""Tests for houdini_toolbox.logging.config module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import logging

# Houdini Toolbox
import houdini_toolbox.logging.config

# =============================================================================
# TESTS
# =============================================================================


def test_init_config():
    """Test houdini_toolbox.logging.config.init_config()."""
    # Initialize our logging config.
    houdini_toolbox.logging.config.init_config()

    logger = logging.getLogger("houdini_toolbox")

    # Verify that the 'houdini_toolbox' parent logger has our expected handlers attached.
    assert [handler.name for handler in logger.handlers] == [
        "console",
        "houdini_python_shell",
    ]
