#
# Produced by:
#       Graham Thompson
#       captainhammy@gmail.com
#       www.captainhammy.com
#
# Name: OnNameChanged.py
#
# Comments: Perform tasks when a Houdini node has its name changed.
# 

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
import ht.nodes.colors

node = kwargs["node"]

ht.nodes.colors.colorNodeByName(node)

