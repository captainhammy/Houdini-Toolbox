"""Perform tasks when a node is loaded from a hip file."""

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
    run_event(NodeEvents.OnLoaded, kwargs)  # pylint: disable=undefined-variable


# =============================================================================

main()
