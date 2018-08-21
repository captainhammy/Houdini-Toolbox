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

    dialog.show()


def copy_items(scriptargs=None):
    """Copy selected items from a pane tab to a target file."""
    # Find the current network editor pane.
    current_pane = utils.find_current_pane_tab(scriptargs)

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
    dialog.show()


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
    dialog.show()

# ==============================================================================

# Global manager for sources
MANAGER = SourceManager()

# Add any relevant sources.
MANAGER.sources.append(HomeToolDirSource())
