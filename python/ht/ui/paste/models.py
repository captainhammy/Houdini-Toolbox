
# ==============================================================================
# IMPORTS
# ==============================================================================

# DD Imports
from PySide2 import QtCore

# Houdini Imports
import hou

# ==============================================================================
# CLASSES
# ==============================================================================

class CopyItemsListModel(QtCore.QAbstractListModel):
    """Simple model to display item paths and icons."""

    def __init__(self, items, parent=None):
        super(CopyItemsListModel, self).__init__(parent)

        self.items = items

    def columnCount(self, parent):
        """The number of columns in the view."""
        return 1

    def data(self, index, role):
        """Get item data."""
        row = index.row()
        item = self.items[row]

        if role == QtCore.Qt.DisplayRole:
            return item.path()

        if role == QtCore.Qt.DecorationRole:
            # Use node type icons.
            if isinstance(item, hou.Node):
                # This might fail in the event nodes don't have icons, or icons
                # that don't exist.
                try:
                    return hou.qt.createIcon(item.type().icon())

                except hou.OperationFailed as inst:
                    return None

            elif isinstance(item, hou.NetworkBox):
                return hou.qt.createIcon("BUTTONS_network_box")

            elif isinstance(item, hou.StickyNote):
                return hou.qt.createIcon("BUTTONS_network_sticky")

            else:
                return None

    def rowCount(self, parent):
        """The number of rows in the view."""
        return len(self.items)


class PasteTableModel(QtCore.QAbstractTableModel):
    """Table model to display files available to copy."""

    header_labels = ("User", "Description")

    def __init__(self, source, context, parent=None):
        super(PasteTableModel, self).__init__(parent)

        self.context = context
        self.sources = source.get_sources(context)

    def set_source(self, source):
        self.sources = source.get_sources(self.context)
        self.modelReset.emit()

    def columnCount(self, parent):
        """The number of columns."""
        return 2

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Get item data."""
        if not index.isValid():
            return

        row = index.row()
        column = index.column()

        if role == QtCore.Qt.DisplayRole:
            source = self.sources[row]

            if column == 0:
                return source.author

            else:
                return source.description

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

    def rowCount(self, parent):
        """The number of rows.

        Equal to the number of files we can paste.

        """
        return len(self.sources)
