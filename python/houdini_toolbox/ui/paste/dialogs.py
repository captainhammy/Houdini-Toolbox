"""Dialogs related to copying/pasting items."""

# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import annotations

# Standard Library
from typing import List, Optional

# Third Party
from PySide2 import QtCore, QtWidgets

# Houdini Toolbox
from houdini_toolbox.ui.paste import utils, widgets

# Houdini
import hou

# ==============================================================================
# CLASSES
# ==============================================================================


class CopyItemsDialog(QtWidgets.QDialog):
    """Dialog to copy items.

    :param items: The items to copy.
    :param parent_node: The parent node.
    :param parent: Optional parent.

    """

    def __init__(
        self,
        items: List[hou.NetworkItem],
        parent_node: hou.Node,
        parent: Optional[QtWidgets.QWidget] = None,
    ):
        super().__init__(parent)

        self.parent_node = parent_node
        self.items = items

        self.context = self.parent_node.childTypeCategory().name()

        self.setWindowTitle(f"Copy Items - {self.parent_node.path()}")
        self.setProperty("houdiniStyle", True)
        self.setStyleSheet(hou.qt.styleSheet())
        self.setMinimumWidth(650)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # =====================================================================

        self.source_menu = widgets.RepositoryWidget()
        layout.addWidget(self.source_menu)

        # =====================================================================

        # Use a QStackedWidget to hold the widgets for each source.
        self.source_chooser = QtWidgets.QStackedWidget()
        layout.addWidget(self.source_chooser)

        # =====================================================================

        self.button_box = widgets.CopyButtonBox()
        layout.addWidget(self.button_box)

        # Connect the accept/copy button action to the copy method
        self.button_box.accepted.connect(self.copy)
        self.button_box.rejected.connect(self.reject)

        # Add all source helper widgets to the stack.
        for source in self.source_menu.get_sources():
            widget = source.copy_helper_widget(self.context)
            widget.valid_source_signal.connect(self.button_box.accept_button.setEnabled)

            self.source_chooser.addWidget(widget)

        self.source_menu.menu.currentIndexChanged.connect(
            self.source_chooser.setCurrentIndex
        )

    @QtCore.Slot()
    def copy(self):
        """Copy the selected items to a file based on the description.

        :return:

        """
        self.accept()

        file_source = self.source_chooser.currentWidget().get_source()

        # Save the items to target.
        utils.save_items_to_source(file_source, self.parent_node, self.items)


class PasteItemsDialog(QtWidgets.QDialog):
    """Dialog to paste items.

    :param editor: The editor to paste the items into.
    :param pos: The position to paste the items.
    :param mousepos: The position of the mouse.
    :param parent: Optional parent.

    """

    def __init__(
        self,
        editor: hou.NetworkEditor,
        pos: hou.Vector2,
        mousepos: hou.Vector2,
        parent: Optional[QtWidgets.QWidget] = None,
    ):
        super().__init__(parent)

        self.editor = editor
        self.pos = pos
        self.mousepos = mousepos

        self.setWindowTitle(f"Paste Items - {self.editor.pwd().path()}")
        self.setProperty("houdiniStyle", True)
        self.setStyleSheet(hou.qt.styleSheet())
        self.setMinimumWidth(650)
        self.setMinimumHeight(350)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        context = self.editor.pwd().childTypeCategory().name()

        self.source_menu = widgets.RepositoryWidget()
        layout.addWidget(self.source_menu)

        # Use a QStackedWidget to hold the widgets for each source.
        self.source_chooser = QtWidgets.QStackedWidget()
        layout.addWidget(self.source_chooser)

        self.source_menu.menu.currentIndexChanged.connect(self._source_changed)

        # ---------------------------------------------------------------------

        self.button_box = widgets.PasteButtonBox()

        layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.paste)
        self.button_box.rejected.connect(self.reject)

        # ---------------------------------------------------------------------

        # Add all source helper widgets to the stack.
        for source in self.source_menu.get_sources():
            widget = source.paste_helper_widget(context)
            widget.perform_operation_signal.connect(self.paste)
            widget.valid_sources_signal.connect(
                self.button_box.accept_button.setEnabled
            )

            self.source_chooser.addWidget(widget)

    @QtCore.Slot(int)
    def _source_changed(self, index: int):
        """Update the displayed widget to match the selected source.

        :param index: The current index.
        :return:

        """
        self.source_chooser.setCurrentIndex(index)

        # Source was changed so disable the button.
        self.button_box.accept_button.setEnabled(False)

    @QtCore.Slot()
    def paste(self):
        """Paste the selected files into the scene.

        :return:

        """
        self.accept()

        to_load = self.source_chooser.currentWidget().get_sources()

        utils.paste_items_from_sources(to_load, self.editor, self.pos, self.mousepos)
