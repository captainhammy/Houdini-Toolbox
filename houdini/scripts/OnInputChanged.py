"""Perform tasks an input connection of a node is changed."""

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
    run_event(NodeEvents.OnInputChanged, kwargs)  # pylint: disable=undefined-variable


# =============================================================================

main()
