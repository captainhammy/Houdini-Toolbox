"""Perform tasks when the last instance of an operator type is deleted."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.events import NodeEvents, runEvent

# =============================================================================
# FUNCTIONS
# =============================================================================

def main():
    """Main function."""
    runEvent(NodeEvents.PostLastDelete, kwargs)

# =============================================================================

main()

