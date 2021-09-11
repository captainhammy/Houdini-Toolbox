"""Custom models for Copy/Paste widgets"""

# ==============================================================================
# IMPORTS
# ==============================================================================

from __future__ import annotations

# Standard Library
from operator import attrgetter
from typing import TYPE_CHECKING, Any, List, Optional

# Third Party
from PySide2 import QtCore

# Houdini Toolbox
from ht.ui.paste import utils

if TYPE_CHECKING:
    # pylint: disable=ungrouped-imports
    from PySide2 import QtWidgets

    from ht.ui.paste.sources import CopyPasteItemSource, CopyPasteSource

# ==============================================================================
# CLASSES
# ==============================================================================


class BasicSourceItemTableModel(QtCore.QAbstractTableModel):
    """Table model to display items available to paste.

    :param source: The source item.
    :param context: The operator context.
    :param parent: Optional parent.

    """

    header_labels = ("Name", "Description", "Author", "Date")

    def __init__(
        self,
        source: CopyPasteSource,
        context: str,
        parent: Optional[QtWidgets.QWidget] = None,
    ):
        super().__init__(parent)

        self.context = context
        self.source = source

        self.items: List[CopyPasteItemSource] = []

        self.refresh()

    def columnCount(  # pylint: disable=unused-argument
        self, parent: QtCore.QModelIndex = QtCore.QModelIndex()
    ) -> int:
        """The number of columns.

        :param parent: The parent item.
        :return: The number of columns.

        """
        return len(self.header_labels)

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.DisplayRole) -> Any:
        """Get item data.

        :param index: THe index to get the data for.
        :param role: The role to get the data for.
        :return: The item data.

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

    def flags(
        self, index: QtCore.QModelIndex  # pylint: disable=no-self-use,unused-argument
    ) -> QtCore.Qt.ItemFlags:
        """Item flags.

        We want items to be enabled and selectable.

        :param index: The index for get the flags for.
        :return: The desired flags.

        """
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(
        self,
        section: int,
        orientation: QtCore.Qt.Orientation,
        role: int = QtCore.Qt.DisplayRole,
    ) -> Any:
        """Populate column headers with our labels.

        :param section: The header index.
        :param orientation: The header orientation.
        :param role: The desired role.
        :return: The header data

        """
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return self.header_labels[section]

        return QtCore.QAbstractTableModel.headerData(self, section, orientation, role)

    def index(
        self, row: int, column: int, parent: QtCore.QModelIndex = QtCore.QModelIndex()
    ) -> QtCore.QModelIndex:
        """Create model indexes for items.

        :param row: The item row.
        :param column: The item column.
        :param parent: The parent index.
        :return: A model index for the item.

        """
        return self.createIndex(row, column, parent)

    def refresh(self):
        """Refresh the internal items list.

        :return:

        """
        self.items = self.source.get_sources(self.context)
        self.items.sort(key=attrgetter("name"))
        self.modelReset.emit()

    def rowCount(  # pylint: disable=unused-argument
        self, parent: QtCore.QModelIndex = QtCore.QModelIndex()
    ) -> int:
        """The number of rows.

        Equal to the number of files we can paste.

        :param parent: The parent item.
        :return: The number of rows.

        """
        return len(self.items)
