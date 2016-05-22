"""Perform tasks when a .hip file is loaded."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
import ht.nodes.colors

# Houdini Imports
import hou

# =============================================================================
# FUNCTIONS
# =============================================================================

def main():
    """Main function."""
    # Initialize color settings.
    ht.nodes.colors.createSessionColorManager()

    # Remove an icon cache directory variable if it exists.
    hou.hscript("set -u HOUDINI_ICON_CACHE_DIR")

# =============================================================================

main()

