"""Perform tasks when the last instance of an operator type is deleted."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox
from ht.events import NodeEvents, run_event

# =============================================================================
# FUNCTIONS
# =============================================================================


def main():
    """Main function."""
    run_event(NodeEvents.PostLastDelete, kwargs)  # pylint: disable=undefined-variable


# =============================================================================

main()
