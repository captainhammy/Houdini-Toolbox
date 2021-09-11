"""Perform tasks when a Houdini node has its name changed."""

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
    run_event(NodeEvents.OnNameChanged, kwargs)  # pylint: disable=undefined-variable


# =============================================================================

main()
