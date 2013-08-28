"""Perform tasks when a Houdini node is created."""

__author__ = "Graham Thompson"
__email__ = "captainhammy@gmail.com"

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
import ht.nodes.colors

node = kwargs["node"]

ht.nodes.colors.colorNode(node)

