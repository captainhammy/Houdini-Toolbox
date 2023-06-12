"""Perform tasks when the last instance of an operator type is deleted."""

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
    run_event(NodeEvents.PostLastDelete, kwargs)


# =============================================================================

main()
