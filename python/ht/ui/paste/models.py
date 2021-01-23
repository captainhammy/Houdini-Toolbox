"""Custom models for Copy/Paste widgets"""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Standard Library Imports
from operator import attrgetter

# Third Party Imports
from PySide2 import QtCore

# Houdini Toolbox Imports
from ht.ui.paste import utils


# ==============================================================================
# CLASSES
# ==============================================================================


class BasicSourceItemTableModel(QtCore.QAbstractTableModel):
    """Table model to display items available to paste.

    :param source: The source item.
    :type source: ht.ui.paste.sources.CopyPasteSource
    :param context: The operator context.
    :type context: str
    :param parent: Optional parent.
    :type parent: QtCore.QWidget

    """

    header_labels = ("Name", "Description", "Author", "Date")

    def __init__(self, source, context, parent=None):
        super().__init__(parent)

        self.context = context
        self.source = source

        self.items = []

        self.refresh()

    def columnCount(
        self, parent=QtCore.QModelIndex()
    ):  # pylint: disable=invalid-name,unused-argument
        """The number of columns.

        :param parent: The parent item.
        :type parent: QtCore.QModelIndex
        :return: The number of columns.
        :rtype: int

        """
        return len(self.header_labels)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Get item data.

        :param index: THe index to get the data for.
        :type index: QtCore.QModelIndex
        :param role: The role to get the data for.
        :type role: int
        :return: The item data.
        :rtype: object

        """
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

            if column == 2:
                return item.author

            if column == 3:
                if item.date is not None:
                    return utils.date_to_string(item.date)

        return None

    def flags(self, index):  # pylint: disable=no-self-use,unused-argument
        """Item flags.

        We want items to be enabled and selectable.

        :param index: The index for get the flags for.
        :type index: QtCore.QModelIndex
        :return: The desired flags.
        :rtype: QtCore.Qt.ItemFlags

        """
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(
        self, section, orientation, role=QtCore.Qt.DisplayRole
    ):  # pylint: disable=invalid-name,
        """Populate column headers with our labels.

        :param section: The header index.
        :type section: int
        :param orientation: The header orientation.
        :type orientation: QtCore.Qt.Orientation
        :param role: The desired role.
        :type role: int
        :return: The header data
        :rtype: object

        """
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return self.header_labels[section]

        return QtCore.QAbstractTableModel.headerData(self, section, orientation, role)

    def index(self, row, column, parent=QtCore.QModelIndex()):
        """Create model indexes for items.

        :param row: The item row.
        :type row: int
        :param column: The item column.
        :type row: int
        :param parent: The parent index.
        :type parent: QtCore.QModelIndex
        :return: A model index for the item.
        :rtype: QtCore.QModelIndex

        """
        return self.createIndex(row, column, parent)

    def refresh(self):
        """Refresh the internal items list.

        :return:

        """
        self.items = self.source.get_sources(self.context)
        self.items.sort(key=attrgetter("name"))
        self.modelReset.emit()

    def rowCount(
        self, parent=QtCore.QModelIndex()
    ):  # pylint: disable=invalid-name,unused-argument
        """The number of rows.

        Equal to the number of files we can paste.

        :param parent: The parent item.
        :type parent: QtCore.QModelIndex
        :return: The number of rows.
        :rtype: int

        """
        return len(self.items)
