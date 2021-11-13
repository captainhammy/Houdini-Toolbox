"""Perform tasks when an operator definition is updated."""

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
    run_event(NodeEvents.OnUpdated, kwargs)  # pylint: disable=undefined-variable


# =============================================================================

main()
