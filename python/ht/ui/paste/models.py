"""Custom models for Copy/Paste widgets"""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Standard Library Imports
from PySide2 import QtCore, QtGui
from operator import attrgetter

# Houdini Toolbox Imports
from ht.ui.paste import utils
import ht.ui.paste
import ht.ui.utils

# Houdini Imports
import hou

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
            return

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


class TreeNode(object):
    """The base tree node class for use in AOV and group display.

    """

    def __init__(self, parent=None):
        self._children = []
        self._expanded = True
        self._parent = parent

        # If we have a parent, add this node to the parent's list of children.
        if parent is not None:
            parent.addChild(self)

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __cmp__(self, node):
        return cmp(self.name, node.name)

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.name)

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def author(self):
        return ""

    @property
    def date(self):
        return ""

    @property
    def children(self):
        """The list of child nodes."""
        return self._children

    @property
    def description(self):
        return ""

    @property
    def expanded(selfs):
        return self._expanded

    @expanded.setter
    def expanded(self, expanded):
        self._expanded = expanded

    @property
    def icon(self):
        return None

    @property
    def name(self):
        """Node name."""
        return "root"

    @property
    def parent(self):
        """Parent node, if any."""
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    @property
    def row(self):
        """The child number of this node."""
        if self.parent is not None:
            return self.parent.children.index(self)

    # =========================================================================
    # METHODS
    # =========================================================================

    def addChild(self, node):
        """Add a node as a child of this node."""
        self._children.append(node)

        node.parent = self

    def insertChild(self, position, node):
        """Insert a node as a child of this node in a particular position."""
        if position < 0 or position > len(self.children):
            raise ValueError("Position out of range")

        self.children.insert(position, node)
        node.parent = self

    def removeAllChildren(self):
        """Remove all children of this node."""
        self._children = []

    def removeChild(self, position):
        """Remove the child node at a particular position."""
        if position < 0 or position > len(self.children):
            raise ValueError("Position out of range")

        # Remove the child node at the specified position and remove the parent
        # reference.
        child = self.children.pop(position)
        child.parent = None


class SourceNode(TreeNode):
    """Tree node representing a folder."""

    def __init__(self, source, parent=None):
        super(SourceNode, self).__init__(parent)

        self._source = source

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def icon(self):
        """Node icon."""
        return self._source.icon

    @property
    def name(self):
        """The display name"""
        return self._source.display_name


class ContextNode(TreeNode):

    def __init__(self, name, parent=None):
        super(ContextNode, self).__init__(parent)

        self._name = name

    @property
    def icon(self):
        return ht.ui.utils.get_icon_for_category_name(self.name)

    @property
    def name(self):
        """The display name"""
        return self._name


class ItemSourceNode(TreeNode):

    def __init__(self, item, parent=None):
        super(ItemSourceNode, self).__init__(parent)

        self._item = item

    @property
    def author(self):
        return self.item.author

    @property
    def date(self):
        return utils.date_to_string(self.item.date)

    @property
    def description(self):
        return self.item.description

    @property
    def icon(self):
        """Node icon."""
        return None

    @property
    def item(self):
        return self._item

    @property
    def name(self):
        """The display name"""
        return self.item.name


class CopyPasteBrowserModel(QtCore.QAbstractItemModel):

    filter_role = QtCore.Qt.UserRole
    sort_role = QtCore.Qt.UserRole + 1

    _LABELS = ["Name", "Description", "Author", "Date"]

    def __init__(self, root, parent=None):
        super(CopyPasteBrowserModel, self).__init__(parent)

        self._root = root

        for source in ht.ui.paste.MANAGER.sources:
            source_node = SourceNode(source, self.root)

            for context in sorted(source.sources):
                context_node = ContextNode(context, source_node)

                item_sources = source.sources[context]

                for item_source in item_sources:
                    item_node = ItemSourceNode(item_source, context_node)

    @property
    def root(self):
        return self._root

    # =========================================================================

    def columnCount(self, parent):
        """The number of columns in the view."""
        return len(self._LABELS)

    def data(self, index, role):
        """Get item data."""
        if not index.isValid():
            return

        column = index.column()

        # Get the tree node.
        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole:
            if column == 0:
                return node.name

            elif column == 1:
                return node.description

            elif column == 2:
                return node.author

            elif column == 3:
                return node.date

        if role == QtCore.Qt.DecorationRole:
            if column == 0:
                return node.icon

        if role == self.filter_role:
            if isinstance(node, (SourceNode, ContextNode)):
                return True

            if isinstance(node, ItemSourceNode):
                if column == 0:
                    return node.name

                elif column == 1:
                    return node.description

                elif column == 2:
                    return node.author

                elif column == 3:
                    return node.date

            return True

        if role == self.sort_role:
            if isinstance(node, TreeNode):
                if column == 0:
                    return node.name

                elif column == 1:
                    return node.description

                elif column == 2:
                    return node.author

                elif column == 3:
                    return node.date

    def getNode(self, index):
        """Get the node at an index."""
        if index.isValid():
            node = index.internalPointer()

            if node:
                return node

        return self.root

    def index(self, row, column, parent):
        """Create an index at a specific location."""
        parent = self.getNode(parent)

        if row < len(parent.children):
            child_item = parent.children[row]

            if child_item:
                return self.createIndex(row, column, child_item)

        return QtCore.QModelIndex()

    def parent(self, index):
        """Get the parent node of an index."""
        node = self.getNode(index)

        parent = node.parent

        if parent == self.root:
            return QtCore.QModelIndex()

        return self.createIndex(parent.row, 0, parent)

    def rowCount(self, parent):
        """The number of children for an index."""
        if not parent.isValid():
            node = self.root

        else:
            node = parent.internalPointer()

        return len(node.children)

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._LABELS[section]

    def flags(self, index):
        """Item flags."""
        if not index.isValid():
            return

        node = index.internalPointer()

        if isinstance(node, (SourceNode, ContextNode)):
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


class LeafFilterProxyModel(QtCore.QSortFilterProxyModel):
    """Custom QSortFilterProxyModel designed to filter based on various
    TreeNode child types.

    """

    def __init__(self, parent=None):
        super(LeafFilterProxyModel, self).__init__(parent)

        self.filter_string = "*"

        # Make filter case insensitive.
#        self.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setFilterRole(CopyPasteBrowserModel.filter_role)

        self.setSortRole(CopyPasteBrowserModel.sort_role)
        self.setDynamicSortFilter(True)

    # =========================================================================
    # METHODS
    # =========================================================================

    def set_filter_string(self, value):
        if value == "":
            value = "*"

        else:
            value = "*" + value + "*"

        self.filter_string = value

        self.invalidateFilter()


    def filterAcceptsRow(self, row_num, source_parent):
        """Check if this filter will accept the row."""
        if self.filterAcceptsRowItself(row_num, source_parent):
            return True

        return self.hasAcceptedChildren(row_num, source_parent)

    def filterAcceptsRowItself(self, row_num, source_parent):
        """Check if this filter accepts this row."""

        model = self.sourceModel()

        node = model.getNode(source_parent)

        #print self.filterRegExp()

        if isinstance(node, ContextNode):
            results = []

            for i in range(3):
                index = model.index(row_num, i, source_parent)
                data = model.data(index, model.filter_role)
             #   results.append(hou.patternMatch(self.filter_string, data, True))
                results.append(self.filterRegExp().exactMatch(data))

            return any(results)

        return False

      #  return super(LeafFilterProxyModel, self).filterAcceptsRow(
       #     row_num,
        #    source_parent
        #)

    def hasAcceptedChildren(self, row_num, parent):
        """Starting from the current node as root, traverse all the
        descendants and test if any of the children match.

        """
        model = self.sourceModel()
        source_index = model.index(row_num, 0, parent)

        num_children = model.rowCount(source_index)

        for i in range(num_children):
            if self.filterAcceptsRow(i, source_index):
                return True

        return False
