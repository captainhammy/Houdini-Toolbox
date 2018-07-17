

from PySide2 import QtWidgets

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



class PasteItemTableView(QtWidgets.QTableView):

    def __init__(self, source, context, multi_select=True, parent=None):
        super(PasteItemTableView, self).__init__(parent)

        self.table_model = models.PasteTableModel(source, context)

        self.setModel(self.table_model)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        if multi_select:
            self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        else:
            self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.setAlternatingRowColors(True)

        self.selection_model = self.selectionModel()

    def getSourcesToLoad(self):
        # Get selected rows from the table.
        indexes = self.selection_model.selectedRows()

        # Get the selected sources from the model based on the indexes.
        return [self.table_model.sources[index.row()] for index in indexes]

    def setSource(self, source):
        self.table_model.setSource(source)


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
