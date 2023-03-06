"""Run code on Houdini startup."""
# pylint: disable=wrong-import-position

# =============================================================================
# IMPORTS
# =============================================================================

# We want to initialize our logging first thing before the UI starts so that our
# base stream logger is using the actual sys.stdout/shell output.  If we don't
# then it will use sys.stdout which is redirected to any interactive Python
# Shell panes.  We explicitly provide an alternate stream handler for output
# to only these pane tabs.

# Houdini Toolbox
import houdini_toolbox.logging.config

houdini_toolbox.logging.config.init_config()

# Houdini Toolbox
# flake8: noqa: E402
import houdini_toolbox.events
import houdini_toolbox.events.callbacks
import houdini_toolbox.nodes.styles
import houdini_toolbox.sohohooks.aovs

# Create any dynamic event handlers, such as using Python's atexit module
houdini_toolbox.events.callbacks.register_callbacks()
