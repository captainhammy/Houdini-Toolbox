"""Perform parameter updates between node versions."""

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
    run_event(NodeEvents.SyncNodeVersion, kwargs) # pylint: disable=undefined-variable

# =============================================================================

main()

