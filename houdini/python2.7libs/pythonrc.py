"""Run code on Houdini startup."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
import ht.events
import ht.events.callbacks
import ht.sohohooks.aovs
import ht.nodes.styles

# Create any dynamic event handlers, such as using Python's atexit module
ht.events.callbacks.registerCallbacks()
