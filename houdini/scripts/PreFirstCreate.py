"""Perform tasks before the first instance of an operator type is created."""

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
    run_event(NodeEvents.PreFirstCreate, kwargs)


# =============================================================================

main()
