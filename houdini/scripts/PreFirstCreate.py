"""Perform tasks before the first instance of an operator type is created."""

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
    runEvent(NodeEvents.PreFirstCreate, kwargs)

# =============================================================================

main()

