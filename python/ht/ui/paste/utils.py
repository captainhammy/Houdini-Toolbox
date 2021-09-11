"""Utilities related to copy/pasting items between sessions."""

# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import annotations

# Standard Library
import datetime
from typing import TYPE_CHECKING, List, Optional, Tuple

# Houdini
import hou

if TYPE_CHECKING:
    from ht.ui.paste.sources import CopyPasteItemSource


# ==============================================================================
# FUNCTIONS
# ==============================================================================


def date_from_string(value: str) -> datetime.datetime:
    """Convert a string value into a datetime object.

    The value must be formatted as: %m/%d/%Y %H:%M

    :param value: The date string.
    :return: A datetime object representing the string.

    """
    return datetime.datetime.strptime(value, "%m/%d/%Y %H:%M")


def date_to_string(date: datetime.datetime) -> str:
    """Convert a datetime object to a string.

    The date string will be formatted as: %m/%d/%Y %H:%M

    :param date: The datetime object to convert.
    :return: The date as a string.

    """
    return date.strftime("%m/%d/%Y %H:%M")


def find_current_pane_tab(scriptargs: dict) -> Optional[hou.NetworkEditor]:
    """Attempt to find the current network editor pane tab.

    :param scriptargs: Houdini kwargs dict.
    :return: The found current network editor pane tab, if any.

    """
    # Try to get the current pane.
    pane = scriptargs.get("pane")

    # There might not be one so attempt to find the pane under the cursor.
    if pane is None:
        desktop = hou.ui.curDesktop()
        pane = desktop.paneTabUnderCursor()

        # It is possible that there is no valid pane tab under the mouse so
        # in that case we look for a pane tab that is current and has a selection.
        if pane is None:
            # Find all displayed NetworkEditor panes
            network_panes = [
                pane_tab
                for pane_tab in desktop.paneTabs()
                if isinstance(pane_tab, hou.NetworkEditor) and pane_tab.isCurrentTab()
            ]

            # Look for any panes with a selection.
            for network_pane in network_panes:
                if network_pane.pwd().selectedItems(True, True):
                    pane = network_pane
                    break

    return pane


def paste_items_from_sources(
    sources: List[CopyPasteItemSource],
    editor: hou.NetworkEditor,
    pos: Optional[List[float]] = None,
    mousepos: Optional[List[float]] = None,
):
    """Paste sources to the current location.

    :param sources: A list of sources to paste.
    :param editor: The editor to paste the items in.
    :param pos: The position to paste the items to.
    :param mousepos: The position of the mouse.
    :return:

    """
    # Tuck away to avoid possible UI related import errors.
    import nodegraphutils

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


def save_items_to_source(
    source: CopyPasteItemSource, parent: hou.Node, items: Tuple[hou.NetworkItem]
):
    """Save a list of items to a source.

    :param source: The target source.
    :param parent: The parent node of the items.
    :param items: The items to save to the source.

    """
    source.save_items(parent, items)
