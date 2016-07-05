"""Perform tasks when a Houdini node is created."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
import ht.nodes.colors
import ht.nodes.naming

# =============================================================================
# FUNCTIONS
# =============================================================================

def main():
    """Main function."""
    node = kwargs["node"]

    ht.nodes.colors.colorNode(node)

#    if ht.nodes.naming.isNamespacedType(node.type()):
#        ht.nodes.naming.setNamespacedFormattedName(node)

# =============================================================================

main()

