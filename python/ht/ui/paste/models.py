"""Custom models for Copy/Paste widgets"""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Python Imports
from PySide2 import QtCore
from operator import attrgetter

# Houdini Toolbox Imports
from ht.ui.paste import utils


# ==============================================================================
# CLASSES
# ==============================================================================

class BasicSourceItemTableModel(QtCore.QAbstractTableModel):
    """Table model to display items available to paste."""

    header_labels = ("Name", "Description", "Author", "Date")

    def __init__(self, source, context, parent=None):
        super(BasicSourceItemTableModel, self).__init__(parent)

        self.context = context
        self.source = source

        self.items = []

        self.refresh()

    def columnCount(self, parent):
        """The number of columns."""
        return len(self.header_labels)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Get item data."""
        if not index.isValid():
            return None

        row = index.row()
        column = index.column()

        if role == QtCore.Qt.DisplayRole:
            item = self.items[row]

            if column == 0:
                return item.name

            if column == 1:
                return item.description

            elif column == 2:
                return item.author

            elif column == 3:
                if item.date is not None:
                    return utils.date_to_string(item.date)

        return None

    def flags(self, index):
        """Item flags.

        We want items to be enabled and selectable.
        """
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """Populate column headers with our labels."""
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return self.header_labels[section]

        return QtCore.QAbstractTableModel.headerData(self, section, orientation, role)

    def index(self, row, column, parent=QtCore.QModelIndex()):
        """Create model indexes for items."""
        return self.createIndex(row, column, parent)

    def refresh(self):
        """Refresh the internal items list."""
        self.items = self.source.get_sources(self.context)
        self.items.sort(key=attrgetter("name"))
        self.modelReset.emit()

    def rowCount(self, parent):
        """The number of rows.

        Equal to the number of files we can paste.

        """
        return len(self.items)
