"""Perform tasks an when an asset definition is installed."""

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
    run_event(NodeEvents.OnInstall, kwargs)  # pylint: disable=undefined-variable


# =============================================================================

main()
