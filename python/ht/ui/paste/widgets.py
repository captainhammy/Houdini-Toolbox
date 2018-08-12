"""Custom widgets for copying/pasting items."""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Standard Library Imports
from PySide2 import QtCore, QtGui, QtWidgets
import os
import re

import ht.ui.paste
from ht.ui.paste import models

# Houdini Imports
import hou

# ==============================================================================
# CLASSES
# ==============================================================================


class _CustomButtonBox(QtWidgets.QDialogButtonBox):
    """A custom QDialogButtonBox for copy/paste buttons."""

    def __init__(self, icon, label, parent=None):
        super(_CustomButtonBox, self).__init__(
            QtWidgets.QDialogButtonBox.Cancel,
            parent=parent
        )

        self.accept_button = QtWidgets.QPushButton(icon, label)
        self.accept_button.setEnabled(False)

        # Acts as the Accept role.
        self.addButton(
            self.accept_button,
            QtWidgets.QDialogButtonBox.AcceptRole
        )


class _NewOrExistingWidget(QtWidgets.QComboBox):

    def __init__(self, parent=None):
        super(_NewOrExistingWidget, self).__init__(parent)

        self.addItem("New File")
        self.addItem("Existing File")

    def get_current_source(self):
        """Get the currently selected source."""
        return self.itemText(self.currentIndex())


class RepositoryWidget(QtWidgets.QWidget):
    """Widget displaying a label and a source chooser."""

    def __init__(self, parent=None):
        super(RepositoryWidget, self).__init__(parent)

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        label = QtWidgets.QLabel("Repository")
        layout.addWidget(label)

        self.menu = QtWidgets.QComboBox()
        layout.addWidget(self.menu, 1)

        for source in ht.ui.paste.MANAGER.sources:
            self.menu.addItem(source.icon, source.display_name, source)

    def get_current_source(self):
        """Get the selected source."""
        return self.menu.itemData(self.menu.currentIndex())

    def get_sources(self):
        return [self.menu.itemData(i) for i in range(self.menu.count())]


class CopyItemNameWidget(QtWidgets.QWidget):
    """Widget to enter an item name."""

    # Signal to emit if anything is changed.
    target_updated_signal = QtCore.Signal()

    def __init__(self, invalid_names=None, parent=None):
        super(CopyItemNameWidget, self).__init__(parent)

        if invalid_names is None:
            invalid_names = ()

        self.invalid_names = invalid_names

        self.target_valid = False

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QtWidgets.QLabel("Enter a simple name (ie: a cool box)"))

        # =====================================================================

        self.name = QtWidgets.QLineEdit()
        layout.addWidget(self.name)

        # =====================================================================

        layout.addWidget(QtWidgets.QLabel("Optional description"))

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

        self.name.textChanged.connect(self._validate_name)

    def _validate_name(self):
        """Validate names against bad characters."""
        value = self.name.text().strip()

        warning_message = ""

        if not value:
            self.target_valid = False

        else:
            if bool(re.search(r"[^a-zA-Z0-9_ ]", value)):
                self.target_valid = False
                warning_message = "Name can only contain [a-zA-Z0-9_ ]"

            else:
                self.target_valid = True

        if value in self.invalid_names:
            self.target_valid = False
            warning_message = "'{}' already exists".format(value)

        if value:
            self.warning_icon.setHidden(self.target_valid)

        else:
            self.warning_icon.setHidden(True)

        if not self.target_valid:
            self.warning_label.setText(warning_message)

        else:
            self.warning_label.setText("")

        # Emit changed signal.
        self.target_updated_signal.emit()


class CopyButtonBox(_CustomButtonBox):
    """Copy button box."""

    def __init__(self, parent=None):
        super(CopyButtonBox, self).__init__(
            hou.qt.createIcon("BUTTONS_copy"),
            "Copy",
            parent
        )


class PasteButtonBox(_CustomButtonBox):
    """Paste button box."""

    def __init__(self, parent=None):
        super(PasteButtonBox, self).__init__(
            hou.qt.createIcon("BUTTONS_paste"),
            "Paste",
            parent
        )


class BaseCopyHelperWidget(QtWidgets.QWidget):
    """A default widget for additional copy related options."""

    def __init__(self, source, context, parent=None):
        super(BaseCopyHelperWidget, self).__init__(parent)

        self.context = context
        self.source = source

        # This widget doesn't have to do anything so just say it is valid.
        self.target_valid = True

    def get_path(self):
        """Do nothing since this widget provides no more info"""
        return None


class BasePasteHelperWidget(QtWidgets.QWidget):
    """A default widget for additional paste related options."""

    def __init__(self, source, context, parent=None):
        super(BasePasteHelperWidget, self).__init__(parent)

        self.context = context
        self.source = source

        # This widget doesn't have to do anything so just say it is valid.
        self.target_valid = True

    def get_path(self):
        """Do nothing since this widget provides no more info"""
        return None

    def get_source(self):
        return None


class FileChooserCopyHelperWidget(BaseCopyHelperWidget):
    """Widget for selecting a target directory when copying."""

    def __init__(self, source, context, parent=None):
        super(FileChooserCopyHelperWidget, self).__init__(source, context, parent)

        self.target_valid = False

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QtWidgets.QLabel("Target Directory"))

        self.path = QtWidgets.QLineEdit()
        layout.addWidget(self.path)

        # Add a file chooser button that only selects directories.
        self.button = hou.qt.createFileChooserButton()
        self.button.setFileChooserFilter(hou.fileType.Directory)
        self.button.setFileChooserTitle("Select directory to copy to")

        layout.addWidget(self.button)

        self.button.fileSelected.connect(self.path.setText)

        self.path.textChanged.connect(self.verify_selection)

    def get_path(self):
        """Cleaned and expanded path."""
        return hou.expandString(self.path.text().strip())

    def verify_selection(self, *args, **kwargs):
        """Verify that the target path is a directory."""
        valid = os.path.isdir(self.get_path())

        # Update the widget valid flag.
        self.target_valid = valid

        # Let the parent widget know that something has updated.
        self.target_updated_signal.emit()


class FileChooserPasteHelperWidget(QtWidgets.QWidget):
    """Widget for selecting an explicit file to paste."""

    # Signal that indicates whether or not the paste target is valid.
    paste_target_valid = QtCore.Signal(bool)

    # Signal used to signal a paste operation (like when double clicked)
    perform_paste_signal = QtCore.Signal()

    def __init__(self, source, context, parent=None):
        super(FileChooserPasteHelperWidget, self).__init__(parent)

        self.context = context

        layout = QtWidgets.QHBoxLayout()

        self.setLayout(layout)

        self.path = QtWidgets.QLineEdit()
        layout.addWidget(self.path)

        self.button = hou.qt.createFileChooserButton()
        self.button.setFileChooserPattern("*.cpio")
        self.button.setFileChooserTitle("Select file to paste from")

        layout.addWidget(self.button)

        self.button.fileSelected.connect(self.path.setText)

        self.path.textChanged.connect(self.verify_selection)

    def get_sources_to_load(self):
        """Get the sources to load."""
        sources = [ht.ui.paste.sources.CPIOCopyPasteItemFile("Object", self.path.text().strip())]
        return sources

    def verify_selection(self, *args, **kwargs):
        """Verify the selection to enable the Paste button.

        The selection is valid if the selected file exists.

        """
        valid = os.path.exists(self.path.text().strip())

        self.paste_target_valid.emit(valid)


class DirectoryItemsPasteHelperWidget(QtWidgets.QTableView):
    """Widget for selected files to paste from a source."""

    # Signal that indicates whether or not the paste target is valid.
    paste_target_valid = QtCore.Signal(bool)

    # Signal used to signal a paste operation (like when double clicked)
    perform_paste_signal = QtCore.Signal()

    def __init__(self, source, context, parent=None):
        super(DirectoryItemsPasteHelperWidget, self).__init__(parent)

        self.table_model = ht.ui.paste.models.PasteTableModel(source, context)

        self.setModel(self.table_model)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.setAlternatingRowColors(True)

        self.selection_model = self.selectionModel()

        self.selection_model.selectionChanged.connect(self.verify_selection)

        self.doubleClicked.connect(self.accept_double_click)

    def accept_double_click(self, index):
        """Accept a double click and paste the selected item."""
        if not index.isValid():
            return

        # When there is a double click we want to immediately paste the clicked
        # item so emit a signal to let the parent know this is the case
        self.perform_paste_signal.emit()

    def get_sources_to_load(self):
        """Get the sources to load."""
        # Get selected rows from the table.
        indexes = self.selection_model.selectedRows()

        # Get the selected sources from the model based on the indexes.
        return [self.table_model.items[index.row()] for index in indexes]

    def verify_selection(self, new_selection, old_selection):
        """Verify the selection to enable the Paste button.

        The selection is valid if one or more rows is selected.

        """
        valid = bool(self.selection_model.selectedRows())

        self.paste_target_valid.emit(valid)


class BasicSourceItemTable(QtWidgets.QTableView):

    perform_operation_signal = QtCore.Signal()
    valid_sources_signal = QtCore.Signal(bool)

    def __init__(self, source, context, selection_mode=QtWidgets.QAbstractItemView.SingleSelection,
                 allow_double_click=False, allow_delete=False, parent=None):
        super(BasicSourceItemTable, self).__init__(parent)
        self.source = source
        self.context = context

        self.allow_delete = allow_delete

        self.table_model = ht.ui.paste.models.BasicSourceItemTableModel(source, context)

        self.setModel(self.table_model)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(selection_mode)

        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.setAlternatingRowColors(True)

        self.selection_model = self.selectionModel()

        self.resizeColumnsToContents()

        if allow_double_click:
            self.doubleClicked.connect(self.accept_double_click)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_menu)

        

    def get_selected_sources(self):
        indexes = self.selection_model.selectedRows()

        # Get the selected sources from the model based on the indexes.
        return [self.table_model.items[index.row()] for index in indexes]

    def has_rows_selected(self):
        return bool(self.selection_model.selectedRows())

    def accept_double_click(self, index):
        """Accept a double click and paste the selected item."""
        if not index.isValid():
            return

        # When there is a double click we want to immediately perform the
        # action on the item item so emit a signal to let the parent know this is the case.
        self.perform_operation_signal.emit()

    def open_menu(self, position):
        """Open the RMB context menu."""
        menu = QtWidgets.QMenu(self)

        menu.addAction(
            "Refresh",
            self._refresh_source,
        )

        if self.allow_delete:
            menu.addSeparator()

            menu.addAction(
                "Delete",
                self._delete_selected,
                QtGui.QKeySequence(QtCore.Qt.Key_Delete),
            )

        menu.exec_(self.mapToGlobal(position))

    def _delete_selected(self):
        selected = self.get_selected_sources()

        result = hou.ui.displayMessage(
            "Are you sure you want to delete these items?",
            buttons=("Yes", "No"),
            severity=hou.severityType.Warning,
            default_choice=1,
            close_choice=1,
            title="Delete items",
            help="\n".join([item.name for item in selected])
        )

        # Chose No, clear selection and bail.
        if result == 1:
            self.clearSelection()
            return

        for item in selected:
            self.source.destroy_item(item)

        self.clearSelection()

        self._refresh_source()

    def _refresh_source(self):
        self.source.refresh()
        self.table_model.refresh()

    def keyPressEvent(self, event):
        """Handle keystrokes."""
        key = event.key()

        if self.allow_delete and key == QtCore.Qt.Key_Delete:
            self._delete_selected()
            return

        super(BasicSourceItemTable, self).keyPressEvent(event)



class HomeToolDirItemsCopyHelperWidget(BaseCopyHelperWidget):

    valid_source_signal = QtCore.Signal(bool)

    def __init__(self, source, context, parent=None):
        super(HomeToolDirItemsCopyHelperWidget, self).__init__(source, context, parent)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.new_or_existing = _NewOrExistingWidget()
        layout.addWidget(self.new_or_existing)

        invalid_names = [item.name for item in source.get_sources(context)]

        self.name_widget = CopyItemNameWidget(invalid_names=invalid_names)
        layout.addWidget(self.name_widget)

        self.table = BasicSourceItemTable(source, context)
        layout.addWidget(self.table)

        self.new_or_existing.currentIndexChanged.connect(self._mode_changed)

        self._mode_changed(0)

        self.name_widget.target_updated_signal.connect(self._validate_options)

        self.table.selection_model.selectionChanged.connect(self._on_table_selection_changed)

    def _mode_changed(self, index):
        if index == 0:
            self.table.setEnabled(False)
            self.table.clearSelection()
            self.name_widget.setEnabled(True)

        else:
            self.table.setEnabled(True)
            self.name_widget.setEnabled(False)

        self._validate_options()

    def _on_table_selection_changed(self, new_selection, old_selection):
        """Verify the selection to enable the Paste button.

        The selection is valid if one or more rows is selected.

        """
        self._validate_options()

    def _validate_options(self):
        mode = self.new_or_existing.currentIndex()

        if mode == 0:
            if self.name_widget.target_valid:
                # TODO: check not existing
                self.valid_source_signal.emit(True)

            else:
                self.valid_source_signal.emit(False)

        else:
            self.valid_source_signal.emit(self.table.has_rows_selected())

    def get_source(self):
        mode = self.new_or_existing.currentIndex()

        if mode == 0:
            name = self.name_widget.name.text()

            description = self.name_widget.description.text()
            if not description:
                description = None

            return self.source.create_source(self.context, name, description)

        else:
            sources = self.table.get_selected_sources()

            return sources[0]


class HomeToolDirItemsPasteHelperWidget(QtWidgets.QWidget):

    perform_operation_signal = QtCore.Signal()
    valid_sources_signal = QtCore.Signal(bool)

    def __init__(self, source, context, parent=None):
        super(HomeToolDirItemsPasteHelperWidget, self).__init__(parent)

        self.source = source
        self.context = context

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # We want to be able to multi-select, delete and double click on items.
        self.table = BasicSourceItemTable(
            source,
            context,
            selection_mode=QtWidgets.QAbstractItemView.ExtendedSelection,
            allow_delete=True,
            allow_double_click=True
        )
        layout.addWidget(self.table)

        self.table.perform_operation_signal.connect(self.perform_operation_signal.emit)
        self.table.selection_model.selectionChanged.connect(self._on_table_selection_changed)

    def _on_table_selection_changed(self, new_selection, old_selection):
        """Verify the selection to enable the Paste button.

        The selection is valid if one or more rows is selected.

        """
        self.valid_sources_signal.emit(self.table.has_rows_selected())

    def get_sources(self):
        return self.table.get_selected_sources()
