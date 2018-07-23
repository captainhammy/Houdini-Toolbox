

from PySide2 import QtCore, QtWidgets
import os
import re

import ht.nodes.paste
from ht.ui.paste import models

import hou


_CONTEXT_ICON_MAP = {
    "Chop": "chop",
    "ChopNet": "chop",
    "Cop2": "cop2",
    "CopNet": "cop2",
    "Director": "root",
    "Dop": "dop",
    "Object": "obj",
    "Particle": "pop",
    "Pop": "pop",
    "Driver": "rop",
    "Shop": "shop",
    "Sop": "sop",
    "Vop": "vop",
    "VopNet": "vopnet",
}


class ContextDisplayWidget(QtWidgets.QWidget):

    def __init__(self, context, parent=None):
        super(ContextDisplayWidget, self).__init__(parent)
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        label = QtWidgets.QLabel()
        icon = getContextIcon(context).pixmap(16, 16)
        label.setPixmap(icon)
        layout.addWidget(label)

        label = QtWidgets.QLabel(context)
        layout.addWidget(label, 1)


class CopyItemListView(QtWidgets.QListView):

    def __init__(self, items, parent=None):
        super(CopyItemListView, self).__init__(parent)

        self.list_model = models.CopyItemsListModel(items)
        self.setModel(self.list_model)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)


class _CustomButtonBox(QtWidgets.QDialogButtonBox):

    def __init__(self, icon, label, parent=None):
        super(_CustomButtonBox, self).__init__(
            QtWidgets.QDialogButtonBox.Cancel,
            parent=parent
        )

        self.accept_button = QtWidgets.QPushButton(
            icon,
            label
        )

        self.accept_button.setEnabled(False)

        # Acts as the Accept role.
        self.addButton(
            self.accept_button,
            QtWidgets.QDialogButtonBox.AcceptRole
        )


class CopyButtonBox(_CustomButtonBox):

    def __init__(self, parent=None):
        super(CopyButtonBox, self).__init__(
            hou.qt.createIcon("BUTTONS_copy"),
            "Copy",
            parent
        )


class PasteButtonBox(_CustomButtonBox):

    def __init__(self, parent=None):
        super(PasteButtonBox, self).__init__(
            hou.qt.createIcon("BUTTONS_paste"),
            "Paste",
            parent
        )


class CopyHelperChooserWidget(QtWidgets.QWidget):
    target_updated_signal = QtCore.Signal()

    def __init__(self, parent=None):
        super(CopyHelperChooserWidget, self).__init__(parent)

        self.target_valid = True

    def getPath(self):
        return None


class CopyFileChooserWidget(QtWidgets.QWidget):
    target_updated_signal = QtCore.Signal()

    def __init__(self, context, parent=None):
        super(CopyFileChooserWidget, self).__init__(parent)

        self.target_valid = False

        self.context = context

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QtWidgets.QLabel("Target Directory"))

        self.path = QtWidgets.QLineEdit()
        layout.addWidget(self.path)

        self.button = hou.qt.createFileChooserButton()
        self.button.setFileChooserFilter(hou.fileType.Directory)
        self.button.setFileChooserTitle("Select directory to copy to")

        layout.addWidget(self.button)

        self.button.fileSelected.connect(self.setPath)

        self.path.textChanged.connect(self.verifySelection)

#    def createSource(self):
#        sources = [ht.nodes.paste.sources.CPIOCopyPasteItemSource("Object", self.path.text().strip())]
#        return sources

    def getPath(self):
        return hou.expandString(self.path.text().strip())

    def setPath(self, path):
        self.path.setText(path)

    def setSource(self, source):
        pass

    def verifySelection(self, *args, **kwargs):
        valid = os.path.isdir(self.getPath())
        self.target_valid = valid

        self.target_updated_signal.emit()


class PasteFileChooserWidget(QtWidgets.QWidget):
    sourceAbleToPasteSignal = QtCore.Signal(bool)
    performPasteSignal = QtCore.Signal()

    def __init__(self, context, parent=None):
        super(PasteFileChooserWidget, self).__init__(parent)

        self.context = context

        layout = QtWidgets.QHBoxLayout()

        self.setLayout(layout)

        self.path = QtWidgets.QLineEdit()
        layout.addWidget(self.path)

        self.button = hou.qt.createFileChooserButton()
        self.button.setFileChooserPattern("*.cpio")
        self.button.setFileChooserTitle("Select file to paste from")

        layout.addWidget(self.button)

        self.button.fileSelected.connect(self.setPath)

        self.path.textChanged.connect(self.verifySelection)

    def getSourcesToLoad(self):
        sources = [ht.nodes.paste.sources.CPIOCopyPasteItemSource("Object", self.path.text().strip())]
        return sources

    def setPath(self, path):
        self.path.setText(path)

    def setSource(self, source):
        pass

    def verifySelection(self, *args, **kwargs):
        valid = os.path.exists(self.path.text().strip())

        self.sourceAbleToPasteSignal.emit(valid)


def _getCopyChooserForSource(source, context):

    if isinstance(source, ht.nodes.paste.sources.FileChooserCPIOSource):

        return CopyFileChooserWidget(context)

    else:
        return CopyHelperChooserWidget()


def _getPasteChooserForSource(source, context):

    if isinstance(source, ht.nodes.paste.sources.FileChooserCPIOSource):

        return PasteFileChooserWidget(context)

    else:
        return PasteItemTableView(source, context)


class PasteItemTableView(QtWidgets.QTableView):
    sourceAbleToPasteSignal = QtCore.Signal(bool)
    performPasteSignal = QtCore.Signal()

    def __init__(self, source, context, parent=None):
        super(PasteItemTableView, self).__init__(parent)

        self.table_model = models.PasteTableModel(source, context)

        self.setModel(self.table_model)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.setAlternatingRowColors(True)

        self.selection_model = self.selectionModel()

        self.selection_model.selectionChanged.connect(self.verifySelection)

        self.doubleClicked.connect(self.acceptDoubleClick)

    def acceptDoubleClick(self, index):
        """Accept a double click and paste the selected item."""
        if not index.isValid():
            return

        self.performPasteSignal.emit()

    def getSourcesToLoad(self):
        # Get selected rows from the table.
        indexes = self.selection_model.selectedRows()

        # Get the selected sources from the model based on the indexes.
        return [self.table_model.sources[index.row()] for index in indexes]

    def setSource(self, source):
        self.table_model.setSource(source)

    def verifySelection(self, new_selection, old_selection):
        """Verify the selection to enable the Paste button.

        The selection is valid if one or more rows is selected.

        """
        valid = bool(self.selection_model.selectedRows())

        self.sourceAbleToPasteSignal.emit(valid)


class LabeledSourceWidget(QtWidgets.QWidget):

    def __init__(self, text, parent=None):
        super(LabeledSourceWidget, self).__init__(parent)

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        label = QtWidgets.QLabel(text)
        layout.addWidget(label)

        self.menu = _SourceChooserWidget()
        layout.addWidget(self.menu, 1)

    def getSource(self):
        return self.menu.getSource()


class _SourceChooserWidget(QtWidgets.QComboBox):

    def __init__(self, parent=None):
        super(_SourceChooserWidget, self).__init__(parent)
        self._manager = ht.nodes.paste.MANAGER

        for source in self.manager.sources:
            self.addItem(source.icon, source.display_name, source)

    def getSource(self):
        return self.itemData(self.currentIndex())

    @property
    def manager(self):
        return self._manager


def getContextIcon(context):
    icon_name = _CONTEXT_ICON_MAP.get(context)

    if icon_name is not None:
        icon_name = "NETWORKS_{}".format(icon_name)

    return hou.qt.createIcon(icon_name)


def _buildCopyWidgetsForSources(context):
    source_widgets = []

    for source in ht.nodes.paste.MANAGER.sources:
        widget = _getCopyChooserForSource(source, context)

        source_widgets.append(widget)

    return source_widgets


def _buildPasteWidgetsForSources(context):
    source_widgets = []

    for source in ht.nodes.paste.MANAGER.sources:
        widget = _getPasteChooserForSource(source, context)

        source_widgets.append(widget)

    return source_widgets


class CopyDescriptionWidget(QtWidgets.QWidget):
    target_updated_signal = QtCore.Signal()

    def __init__(self, parent=None):
        super(CopyDescriptionWidget, self).__init__(parent)

        self.target_valid = False

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

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

        self.description.textChanged.connect(self._validateDescription)

    def _validateDescription(self):
        """Validate desriptions against bad characters."""
        value = self.description.text()

        if not value:
            self.target_valid = False

        else:
            self.target_valid = not bool(re.search(r"[^a-zA-Z0-9_ ]", value))

        self.warning_icon.setHidden(self.target_valid)

        if not self.target_valid:
            self.warning_label.setText(
                "Description can only contain [a-zA-Z0-9_ ]"
            )

        else:
            self.warning_label.setText("")

        self.target_updated_signal.emit()


class ChooseCopySourceWidget(QtWidgets.QWidget):
    target_valid_signal = QtCore.Signal(bool)

    def __init__(self, context, parent=None):
        super(ChooseCopySourceWidget, self).__init__(parent)

        self.context = context

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # =====================================================================

        self.source_menu = LabeledSourceWidget("Copy items to")
        layout.addWidget(self.source_menu)

        # =====================================================================

        self.description_widget = CopyDescriptionWidget()
        layout.addWidget(self.description_widget)

        self.description_widget.target_updated_signal.connect(self._validate_inputs)

        # =====================================================================

        self.source_chooser = QtWidgets.QStackedWidget()
        layout.addWidget(self.source_chooser)

        source_widgets = _buildCopyWidgetsForSources(context)

        for widget in source_widgets:
            widget.target_updated_signal.connect(self._validate_inputs)
            self.source_chooser.addWidget(widget)

        layout.addWidget(self.source_chooser)

        self.source_menu.menu.currentIndexChanged.connect(self._sourceChanged)

    def _sourceChanged(self, index):
        self.source_chooser.setCurrentIndex(index)

        self._validate_inputs()

    def _validate_inputs(self):
        description_valid = self.description_widget.target_valid

        source_widget = self.source_chooser.currentWidget()
        extra_valid = source_widget.target_valid

        all_valid = all([description_valid, extra_valid])

        self.target_valid_signal.emit(all_valid)

    def get_source(self):
        description = self.description_widget.description.text()

        source = self.source_menu.getSource()

        source_widget = self.source_chooser.currentWidget()

        base_path = None

        if isinstance(source_widget, CopyFileChooserWidget):
            base_path = source_widget.getPath()

        file_source = source.create_source(self.context, description, base_path=base_path)


        print file_source

        return file_source

class ChoosePasteSourceWidget(QtWidgets.QWidget):
    source_valid_signal = QtCore.Signal(bool)
    performPasteSignal = QtCore.Signal()

    def __init__(self, context, parent=None):
        super(ChoosePasteSourceWidget, self).__init__(parent)

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # =====================================================================

        self.source_menu = LabeledSourceWidget("Paste items from")
        layout.addWidget(self.source_menu)

        # =====================================================================

        layout.addWidget(ContextDisplayWidget(context))

        # =====================================================================

        self.source_chooser = QtWidgets.QStackedWidget()

        source_widgets = _buildPasteWidgetsForSources(context)

        for widget in source_widgets:
            widget.sourceAbleToPasteSignal.connect(self.source_valid_signal.emit)
            widget.performPasteSignal.connect(self.performPasteSignal.emit)
            self.source_chooser.addWidget(widget)

        layout.addWidget(self.source_chooser)

        self.source_menu.menu.currentIndexChanged.connect(self._sourceChanged)

    def _sourceChanged(self, index):
        self.source_chooser.setCurrentIndex(index)
        self.source_valid_signal.emit(False)

    def getSourcesToLoad(self):
        current = self.source_chooser.currentWidget()
        return current.getSourcesToLoad()
