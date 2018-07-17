"""Dialogs related to copying/pasting items."""
# ==============================================================================
# IMPORTS
# ==============================================================================

# Python Imports
import re

# DD Imports
from PySide2 import QtWidgets

from ht.nodes.paste import api, utils
from ht.ui.paste import widgets

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

        self.setWindowTitle("Copy Items")
        self.setProperty("houdiniStyle", True)
        self.setStyleSheet(hou.ui.qtStyleSheet())

        self.initUI()

        self.setMinimumWidth(350)

    def _validateDescription(self):
        """Validate desriptions against bad characters."""
        value = self.description.text()

        if not value:
            valid = False

        else:
            valid = not bool(re.search(r"[^a-zA-Z0-9_ ]", value))

        self.button_box.accept_button.setEnabled(valid)
        self.warning_icon.setHidden(valid)

        if not valid:
            self.warning_label.setText(
                "Description can only contain [a-zA-Z0-9_ ]"
            )

        else:
            self.warning_label.setText("")

    def copy(self):
        """Copy the selected items to a file based on the description."""
        self.accept()

        context = self.parent_node.childTypeCategory().name()

        source = self.source_chooser.getSource()

        file_source = source.create_source(context, self.description.text())

        # Save the items to target.
        api.saveItemsToSource(file_source, self.parent_node, self.items)

    def initUI(self):
        """Inititialize the UI."""
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.source_chooser = widgets.LabeledSourceWidget("Copy items to")
        layout.addWidget(self.source_chooser)

        current_source = self.source_chooser.getSource()

        # =====================================================================

        context = self.parent_node.childTypeCategory().name()
    #    self.table = widgets.PasteItemTableView(current_source, context, multi_select=False)
      #  layout.addWidget(self.table)

        # =====================================================================

        layout.addWidget(QtWidgets.QLabel("Enter a description (ie: a cool box)"))

        # =====================================================================

        self.description = QtWidgets.QLineEdit()
        layout.addWidget(self.description)

        # =====================================================================

        warning_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(warning_layout)

        self.warning_icon = QtWidgets.QLabel()
        warning_layout.addWidget(self.warning_icon)

        warning_icon = hou.qt.createIcon("DIALOG_warning")
        self.warning_icon.setPixmap(warning_icon.pixmap(14, 14))
        self.warning_icon.setHidden(True)

        self.warning_label = QtWidgets.QLabel()
        warning_layout.addWidget(self.warning_label)

        warning_layout.addStretch(1)

        # =====================================================================

        self.item_list = widgets.CopyItemListView(self.items)
        layout.addWidget(self.item_list)

        # =====================================================================

        self.button_box = widgets.CopyButtonBox()
        layout.addWidget(self.button_box)

        # Connect the accept/copy button action to the copy method
        self.button_box.accepted.connect(self.copy)
        self.button_box.rejected.connect(self.reject)

        # =====================================================================

        self.description.textChanged.connect(self._validateDescription)


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

        self.source_chooser.menu.currentIndexChanged.connect(self._sourceChanged)

    def _sourceChanged(self, index):
        source = self.source_chooser.menu.manager.sources[index]

        self.source_choice_widget.setSource(source)

    def _verifySelection(self, new_selection, old_selection):
        """Verify the selection to enable the Paste button.

        The selection is valid if one or more rows is selected.

        """
        valid = self.source_choice_widget.verifySelection(new_selection, old_selection)

        # Enable/disable button based on the validity of the selection.
        self.button_box.accept_button.setEnabled(valid)

    def acceptDoubleClick(self, index):
        """Accept a double click and paste the selected item."""
        if not index.isValid():
            return

        self.paste()

    def initUI(self):
        """Initialize the UI."""
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # =====================================================================

        self.source_chooser = widgets.LabeledSourceWidget("Paste items from")
        layout.addWidget(self.source_chooser)

        current_source = self.source_chooser.getSource()

        # =====================================================================

        context = self.editor.pwd().childTypeCategory().name()
        layout.addWidget(widgets.ContextDisplayWidget(context))

        # =====================================================================

        self.source_choice_widget = widgets.PasteItemTableView(current_source, context)

        layout.addWidget(self.source_choice_widget)

        # In the event of a double click we want to trigger a paste of the
        # selected item.
        self.source_choice_widget.doubleClicked.connect(self.acceptDoubleClick)

        # =====================================================================

        self.button_box = widgets.PasteButtonBox()

        layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.paste)
        self.button_box.rejected.connect(self.reject)

        # =====================================================================

        # Whenever the selection of the table is changed we need to verify
        # something is chosen
        self.source_choice_widget.selection_model.selectionChanged.connect(self._verifySelection)

    def paste(self):
        """Paste the selected files into the scene."""
        self.accept()

        to_load = self.source_choice_widget.getSourcesToLoad()

        api.pasteItemsFromSources(to_load, self.editor, self.pos, self.mousepos)


# ==============================================================================
# FUNCTIONS
# ==============================================================================

def copyItem(item):
    """Copy a single item to a target file."""
    items = (item,)
    parent = item.parent()

    # Run the copy dialog.
    dialog = CopyItemsDialog(items, parent, parent=hou.qt.mainWindow())
    dialog.exec_()


def copyItems(scriptargs):
    """Copy selected items from a pane tab to a target file."""
    # Find the current network editor pane.
    current_pane = utils.findCurrentPaneTab(scriptargs)

    # Couldn't determine where to paste so we display a warning
    # and abort.
    if current_pane is None:
        hou.ui.displayMessage(
            "Can not copy items",
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
    dialog.exec_()


def pasteItems(scriptargs=None):
    """Paste items into the current context."""
    # Try to find the current pane/context/level.
    current_pane = utils.findCurrentPaneTab(scriptargs)

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
    dialog.exec_()
