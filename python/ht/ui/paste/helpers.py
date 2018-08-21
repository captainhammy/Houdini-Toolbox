"""Custom helper widgets for copying/pasting sources."""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Standard Library Imports
from PySide2 import QtCore, QtWidgets
import os

import ht.ui.paste
from ht.ui.paste import utils, widgets

# Houdini Imports
import hou

# ==============================================================================
# CLASSES
# ==============================================================================


class BaseCopyHelperWidget(QtWidgets.QWidget):
    """A default widget for additional copy related options."""

    def __init__(self, source, context, parent=None):
        super(BaseCopyHelperWidget, self).__init__(parent)

        self.context = context
        self.source = source

        # This widget doesn't have to do anything so just say it is valid.
      #  self.target_valid = True

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
#        self.target_valid = True

#    def get_path(self):
#        """Do nothing since this widget provides no more info"""
#        return None

    def get_sources(self):
        pass


class FileChooserCopyHelperWidget(BaseCopyHelperWidget):
    """Widget for selecting a target directory when copying."""
    valid_source_signal = QtCore.Signal(bool)

    def __init__(self, source, context, parent=None):
        super(FileChooserCopyHelperWidget, self).__init__(source, context, parent)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        chooser_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(chooser_layout)

        chooser_layout.addWidget(QtWidgets.QLabel("Target Directory"))

        self.path = QtWidgets.QLineEdit()
        chooser_layout.addWidget(self.path)

        # Add a file chooser button that only selects directories.
        self.button = hou.qt.createFileChooserButton()
        self.button.setFileChooserFilter(hou.fileType.Directory)
        self.button.setFileChooserTitle("Select directory to copy to")

        chooser_layout.addWidget(self.button)

        self.new_or_existing = widgets.NewOrExistingWidget()
        layout.addWidget(self.new_or_existing)

        self.name_widget = widgets.CopyItemNameWidget(invalid_names=None)
        layout.addWidget(self.name_widget)

  #      self.table = BasicSourceItemTable(source, context)
#        layout.addWidget(self.table)

        self.button.fileSelected.connect(self.path.setText)

        self.path.textChanged.connect(self.verify_selection)

    def _get_real_path(self):
        return hou.expandString(self.path.text().strip())

    def get_source(self):
        return None

    def verify_selection(self, *args, **kwargs):
        """Verify that the target path is a directory."""
        path = self._get_real_path()

        valid = os.path.isdir(path)

        # Let the parent widget know that something has updated.
        self.valid_source_signal.emit(valid)


class FileChooserPasteHelperWidget(BasePasteHelperWidget):
    """Widget for selecting an explicit file to paste."""

    perform_operation_signal = QtCore.Signal()

    valid_sources_signal = QtCore.Signal(bool)

    def __init__(self, source, context, parent=None):
        super(FileChooserPasteHelperWidget, self).__init__(source, context, parent)

        layout = QtWidgets.QVBoxLayout()

        self.setLayout(layout)

        chooser_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(chooser_layout)

        self.path = QtWidgets.QLineEdit()
        chooser_layout.addWidget(self.path)

        self.button = hou.qt.createFileChooserButton()
        self.button.setFileChooserPattern("*.cpio")
        self.button.setFileChooserTitle("Select file to paste from")
        self.button.fileSelected.connect(self.path.setText)

        chooser_layout.addWidget(self.button)

        self.warning = widgets.WarningWidget()
        layout.addWidget(self.warning)

        self.path.textChanged.connect(self.verify_selection)

    def _get_real_path(self):
        return hou.expandString(self.path.text().strip())

    def get_sources(self):
        """Get the sources to load."""
        path = self._get_real_path()

        # Create a source to paste from the path.
        sources = [ht.ui.paste.sources.CPIOContextCopyPasteItemFile.from_path(path)]
        return sources

    def verify_selection(self, *args, **kwargs):
        """Verify the selection to enable the Paste button.

        The selection is valid if the selected file exists.

        """
        path = self._get_real_path()

        if not os.path.exists(path):
            self.warning.set_warning("Selected file does not exist")
            self.valid_sources_signal.emit(False)

            return

        data = ht.ui.paste.sources.FileChooserCPIOSource.read_sidecar_file(path)

        context = data.get("context")

        if context != self.context:
            self.warning.set_warning("Selected file has invalid context for paste: {}".format(context))
            self.valid_sources_signal.emit(False)

            return

        self.warning.clear_warning()

        self.valid_sources_signal.emit(True)



class HomeToolDirItemsCopyHelperWidget(BaseCopyHelperWidget):

    valid_source_signal = QtCore.Signal(bool)

    def __init__(self, source, context, parent=None):
        super(HomeToolDirItemsCopyHelperWidget, self).__init__(source, context, parent)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.new_or_existing = widgets.NewOrExistingWidget()
        layout.addWidget(self.new_or_existing)

        invalid_names = [item.name for item in source.get_sources(context)]

        self.name_widget = widgets.CopyItemNameWidget(invalid_names=invalid_names)
        layout.addWidget(self.name_widget)

        self.table = widgets.BasicSourceItemTable(source, context)
        layout.addWidget(self.table)

        self.new_or_existing.currentIndexChanged.connect(self._mode_changed)

        self._mode_changed(0)

        self.name_widget.valid_source_signal.connect(self.valid_source_signal.emit)
        self.table.valid_sources_signal.connect(self.valid_source_signal.emit)

    def _mode_changed(self, index):
        if index == 0:
            self.table.setEnabled(False)
            self.table.clearSelection()
            self.name_widget.setEnabled(True)
            self.name_widget.validate_name()

        else:
            self.table.setEnabled(True)
            self.name_widget.setEnabled(False)

            self.valid_source_signal.emit(False)

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


class HomeToolDirItemsPasteHelperWidget(BasePasteHelperWidget):

    perform_operation_signal = QtCore.Signal()
    valid_sources_signal = QtCore.Signal(bool)

    def __init__(self, source, context, parent=None):
        super(HomeToolDirItemsPasteHelperWidget, self).__init__(source, context, parent)

        #self.source = source
        #self.context = context

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # We want to be able to multi-select, delete and double click on items.
        self.table = widgets.BasicSourceItemTable(
            source,
            context,
            selection_mode=QtWidgets.QAbstractItemView.ExtendedSelection,
            allow_delete=True,
            allow_double_click=True
        )
        layout.addWidget(self.table)

        self.table.perform_operation_signal.connect(self.perform_operation_signal.emit)
        self.table.valid_sources_signal.connect(self.valid_sources_signal.emit)

    def get_sources(self):
        return self.table.get_selected_sources()

