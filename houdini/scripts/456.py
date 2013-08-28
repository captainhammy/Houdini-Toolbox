"""Perform tasks when a .hip file is loaded."""

__author__ = "Graham Thompson"
__email__ = "captainhammy@gmail.com"

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
import ht.nodes.colors

# Houdini Imports
import hou

# Initialize color settings.
ht.nodes.colors.createSessionColorManager()

# Remove an icon cache directory variable if it exists.
hou.hscript("set -u HOUDINI_ICON_CACHE_DIR")

