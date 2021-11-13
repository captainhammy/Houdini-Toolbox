"""Perform tasks when a Houdini node is created."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox
from houdini_toolbox.events import NodeEvents, run_event

# =============================================================================
# FUNCTIONS
# =============================================================================


def main():
    """Main function."""
    run_event(NodeEvents.OnCreated, kwargs)  # pylint: disable=undefined-variable


# =============================================================================

main()
