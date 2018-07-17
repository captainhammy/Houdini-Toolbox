



import hou

import nodegraphutils


def pasteItemsFromSources(sources, editor, pos=None, mousepos=None):
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


def saveItemsToSource(source, parent, items):
    """Save a list of items to a file."""
    source.save_items(parent, items)
