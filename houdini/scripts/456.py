"""Perform tasks when a .hip file is loaded."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
#import ht.nodes.shapes
from ht.events import runEvents

# =============================================================================
# FUNCTIONS
# =============================================================================

def main():
    """Main function."""
    runEvents("456", None)
#    ht.nodes.shapes.createSessionShapeManager()

# =============================================================================

main()

