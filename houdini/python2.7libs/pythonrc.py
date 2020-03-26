"""Run code on Houdini startup."""
# pylint: disable=wrong-import-position

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports

# We want to initialize our logging first thing before the UI starts so that our
# base stream logger is using the actual sys.stdout/shell output.  If we don't
# then it will use sys.stdout which is redirected to any interactive Python
# Shell panes.  We explicitly provide an alternate stream handler for output
# to only these pane tabs.
import ht.logging.config

ht.logging.config.init_config()

import ht.events
import ht.events.callbacks
import ht.sohohooks.aovs
import ht.nodes.styles

# Create any dynamic event handlers, such as using Python's atexit module
ht.events.callbacks.register_callbacks()
