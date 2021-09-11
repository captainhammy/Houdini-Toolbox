"""Perform tasks when an operator definition is updated."""

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
    run_event(NodeEvents.OnUpdated, kwargs)  # pylint: disable=undefined-variable


# =============================================================================

main()
