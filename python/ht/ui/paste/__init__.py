"""Initialize the ht.ui.paste module."""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Houdini Toolbox Imports
from ht.ui.paste import dialogs, utils
from ht.ui.paste.sources import HomeToolDirSource, SourceManager

# Houdini Imports
import hou

# ==============================================================================
# FUNCTIONS
# ==============================================================================

def copy_item(item):
    """Copy a single item to a target file."""
    items = (item,)
    parent = item.parent()

    # Run the copy dialog.
    dialog = dialogs.CopyItemsDialog(items, parent, parent=hou.qt.mainWindow())

    dialog.exec_()


def copy_items(scriptargs=None):
    """Copy selected items from a pane tab to a target file."""
    # Find the current network editor pane.
    current_pane = utils.find_current_pane_tab(scriptargs)

    # Check to make sure the pane is a network editor.  If it isn't we can't
    # do much.
    if not isinstance(current_pane, hou.NetworkEditor):
        current_pane = None

    # Couldn't determine where to paste so we display a warning
    # and abort.
    if current_pane is None:
        hou.ui.displayMessage(
            "Cannot copy items",
            help="Could not determine copy context",
            severity=hou.severityType.Warning,
        )

        return

    parent = current_pane.pwd()

    items = parent.selectedItems(True, True)

    # If there are no items elected display a warning and abort.
    if not items:
        hou.ui.displayMessage(
            "Could not copy items",
            help="No selected nodes",
            severity=hou.severityType.Warning,
        )

        return

    # Run the copy dialog.
    dialog = dialogs.CopyItemsDialog(items, parent, parent=hou.qt.mainWindow())
    dialog.exec_()


def copy_items_from_graph(editor):
    """Copy items from a network editor event."""
    parent = editor.pwd()

    items = parent.selectedItems(True, True)

    # If there are no items selected then display an error and abort.
    if not items:
        hou.ui.displayMessage(
            "Could not copy selected items",
            help="Nothing was selected",
            severity=hou.severityType.Error,
        )

        return None, True

    dialog = dialogs.CopyItemsDialog(items, parent, parent=hou.qt.mainWindow())
    dialog.exec_()

    # This is a one off event so we don't care what happens after this.
    return None, True


def paste_items(scriptargs=None):
    """Paste items into the current context."""
    # Try to find the current pane/context/level.
    current_pane = utils.find_current_pane_tab(scriptargs)

    # Couldn't determine where to paste so we display a warning
    # and abort.
    if current_pane is None:
        hou.ui.displayMessage(
            "Could not paste items",
            help="Could not determine paste context",
            severity=hou.severityType.Warning,
        )

        return

    pos = current_pane.cursorPosition()

    # Run the paste dialog.
    dialog = dialogs.PasteItemsDialog(current_pane, pos, pos, parent=hou.qt.mainWindow())
    dialog.exec_()


def paste_items_to_graph(eventtype, editor, uievent):
    """Paste items from a network editor event."""
    if eventtype == "keyhit":
        mousepos = uievent.mousepos

    elif eventtype == "menukeyhit":
        mousepos = editor.screenBounds().center()

    else:
        mousepos = None

    if mousepos is not None:
        pos = editor.posFromScreen(mousepos)

    else:
        pos = None

    dialog = dialogs.PasteItemsDialog(editor, pos, mousepos, parent=hou.qt.mainWindow())
    dialog.exec_()

    # This is a one off event so we don't care what happens after this.
    return None, True

# ==============================================================================

# Global manager for sources
MANAGER = SourceManager()

# Add any relevant sources.
MANAGER.sources.append(HomeToolDirSource())
