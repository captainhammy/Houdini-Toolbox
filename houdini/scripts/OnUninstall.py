"""Perform tasks an when an asset definition is uninstalled."""

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
    run_event(NodeEvents.OnUninstall, kwargs)  # pylint: disable=undefined-variable


# =============================================================================

main()
