"""Dialogs related to copying/pasting items."""
# ==============================================================================
# IMPORTS
# ==============================================================================

# DD Imports
from PySide2 import QtWidgets

from ht.ui.paste import utils, widgets

# Houdini Imports
import hou

# ==============================================================================
# CLASSES
# ==============================================================================

class CopyItemsDialog(QtWidgets.QDialog):
    """Dialog to copy items."""

    def __init__(self, items, parent_node, parent=None):
        super(CopyItemsDialog, self).__init__(parent)

        self.parent_node = parent_node
        self.items = items

        self.context = self.parent_node.childTypeCategory().name()

        self.setWindowTitle("Copy Items")
        self.setProperty("houdiniStyle", True)
        self.setStyleSheet(hou.ui.qtStyleSheet())

        self.initUI()

        self.setMinimumWidth(350)

    def copy(self):
        """Copy the selected items to a file based on the description."""
        self.accept()

        file_source = self.choose_widget.get_source()

        # Save the items to target.
        utils.save_items_to_source(file_source, self.parent_node, self.items)

    def initUI(self):
        """Inititialize the UI."""
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.choose_widget = widgets.ChooseCopySourceWidget(self.context, self.items)
        layout.addWidget(self.choose_widget)

        # =====================================================================

        self.button_box = widgets.CopyButtonBox()
        layout.addWidget(self.button_box)

        # Connect the accept/copy button action to the copy method
        self.button_box.accepted.connect(self.copy)
        self.button_box.rejected.connect(self.reject)

        # =====================================================================

        self.choose_widget.target_valid_signal.connect(self.button_box.accept_button.setEnabled)


class PasteItemsDialog(QtWidgets.QDialog):
    """Dialog to paste items."""

    def __init__(self, editor, pos, mousepos, parent=None):
        super(PasteItemsDialog, self).__init__(parent)

        self.editor = editor
        self.pos = pos
        self.mousepos = mousepos

        self.setWindowTitle("Paste Items")
        self.setProperty("houdiniStyle", True)
        self.setStyleSheet(hou.ui.qtStyleSheet())

        self.initUI()

        self.setMinimumWidth(550)
        self.setMinimumHeight(350)

    def initUI(self):
        """Initialize the UI."""
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        context = self.editor.pwd().childTypeCategory().name()

        self.choose_widget = widgets.ChoosePasteSourceWidget(context)

        self.choose_widget.performPasteSignal.connect(self.paste)
        layout.addWidget(self.choose_widget)

        # =====================================================================

        self.button_box = widgets.PasteButtonBox()

        layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.paste)
        self.button_box.rejected.connect(self.reject)

        self.choose_widget.source_valid_signal.connect(self.button_box.accept_button.setEnabled)

    def paste(self):
        """Paste the selected files into the scene."""
        self.accept()

        to_load = self.choose_widget.get_sources_to_load()

        utils.paste_items_from_sources(to_load, self.editor, self.pos, self.mousepos)


# ==============================================================================
# FUNCTIONS
# ==============================================================================

def copy_item(item):
    """Copy a single item to a target file."""
    items = (item,)
    parent = item.parent()

    # Run the copy dialog.
    dialog = CopyItemsDialog(items, parent, parent=hou.qt.mainWindow())

    dialog.show()


def copy_items(scriptargs):
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
    dialog = CopyItemsDialog(items, parent, parent=hou.qt.mainWindow())
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
    dialog = PasteItemsDialog(current_pane, pos, pos, parent=hou.qt.mainWindow())
    dialog.show()
