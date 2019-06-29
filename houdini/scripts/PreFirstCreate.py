"""Perform tasks before the first instance of an operator type is created."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.events import NodeEvents, run_event


# =============================================================================
# FUNCTIONS
# =============================================================================

def main():
    """Main function."""
    run_event(NodeEvents.PreFirstCreate, kwargs)  # pylint: disable=undefined-variable


# =============================================================================

main()
