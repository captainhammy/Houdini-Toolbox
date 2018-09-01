"""Utilities related to copy/pasting items between sessions."""

# ==============================================================================
# IMPORTS
# ==============================================================================

import datetime

# Houdini Imports
import hou
import nodegraphutils


# ==============================================================================
# FUNCTIONS
# ==============================================================================


def date_from_string(value):
    return datetime.datetime.strptime(value, "%m/%d/%Y %H:%M")


def date_to_string(date):
    return date.strftime("%m/%d/%Y %H:%M")


def find_current_pane_tab(scriptargs):
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
            network_panes = [pane_tab for pane_tab in desktop.paneTabs()
                             if isinstance(pane_tab, hou.NetworkEditor) and
                             pane_tab.isCurrentTab()]

            # Look for any panes with a selection.
            for network_pane in network_panes:
                if network_pane.pwd().selectedItems(True, True):
                    pane = network_pane
                    break

    return pane


def find_network_pane_for_category(category):
    """Search for visible NetworkEditor pane tabs matching a node type category."""
    desktop = hou.ui.curDesktop()

    network_panes = [pane_tab for pane_tab in desktop.paneTabs()
                     if isinstance(pane_tab, hou.NetworkEditor) and
                     pane_tab.pwd().childTypeCategory() == category and
                     pane_tab.isCurrentTab()]

    if network_panes:
        return network_panes[0]

    return None


def find_network_pane_from_selection():
    items = hou.selectedItems()

    if not items:
        return None

    parent = items[0].parent()

    desktop = hou.ui.curDesktop()

    network_panes = [pane_tab for pane_tab in desktop.paneTabs()
                     if isinstance(pane_tab, hou.NetworkEditor) and
                     pane_tab.pwd() == parent and pane_tab.isCurrentTab()]

    if network_panes:
        return network_panes[0]

    return None


def paste_items_from_sources(sources, editor, pos=None, mousepos=None):
    """Paste sources to the current location."""
    parent = editor.pwd()

    # Look for any existing selected items.
    selected_items = parent.selectedItems(True, True)

    # If any items are already selected we need to deselect them so they are
    # not moved when pasting.
    if selected_items:
        for item in selected_items:
            item.setSelected(False)

    # Create an undo block to paste all the items under.
    with hou.undos.group("Pasting items"):
        for source in sources:
            source.load_items(parent)

            if pos is not None and mousepos is not None:
                nodegraphutils.moveItemsToLocation(editor, pos, mousepos)

            nodegraphutils.updateCurrentItem(editor)


def save_items_to_source(source, parent, items):
    """Save a list of items to a file."""
    source.save_items(parent, items)
