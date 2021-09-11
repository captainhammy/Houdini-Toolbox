"""Perform tasks an when an asset definition is uninstalled."""

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
    run_event(NodeEvents.OnUninstall, kwargs)  # pylint: disable=undefined-variable


# =============================================================================

main()
