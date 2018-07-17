"""Utilities related to copy/pasting items between sessions."""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Houdini Imports
import hou

# ==============================================================================
# FUNCTIONS
# ==============================================================================

def findCurrentPaneTab(scriptargs):
    """Attempt to find the current pane tab."""
    # Try to get the current pane.
    pane = scriptargs.get("pane")

    # There might not be one so  attempt to find the pane under the cursor.
    if pane is None:
        desktop = hou.ui.curDesktop()
        pane = desktop.paneTabUnderCursor()

        # It is possible that there is no valid pane tab under the mouse so
        # in that case we look for a pane tab that is current and has a selection.
        if pane is None:
            # Find all displayed NetworkEditor panes
            network_panes = [panetab for panetab in desktop.paneTabs()
                             if isinstance(panetab, hou.NetworkEditor) and
                             panetab.isCurrentTab()]

            # Look for any panes with a selection.
            for network_pane in network_panes:
                if network_pane.pwd().selectedItems(True, True):
                    pane = network_pane
                    break

    return pane
