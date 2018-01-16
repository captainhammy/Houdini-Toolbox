"""This module contains custom PySide models and associated functions."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
from PySide2 import QtCore, QtGui
import pickle

# Houdini Toolbox Imports
from ht.sohohooks.aovs import manager
from ht.sohohooks.aovs.aov import AOV, IntrinsicAOVGroup, GroupBasedAOV
from ht.ui.aovs import utils
import ht.ui.icons

# Houdini Imports
import hou

# =============================================================================
# TREE NODES
# =============================================================================

class TreeNode(object):
    """The base tree node class for use in AOV and group display.

    """

    def __init__(self, parent=None):
        self._children = []
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
    def children(self):
        """The list of child nodes."""
        return self._children

    @property
    def icon(self):
        """Icon for this node."""
        return hou.qt.createIcon("NETWORKS_root")

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

    def tooltip(self):
        """Return a tooltip for the node."""
        pass

# =============================================================================

class FolderNode(TreeNode):
    """Tree node representing a folder."""

    def __init__(self, name, parent=None):
        super(FolderNode, self).__init__(parent)

        self._name = name

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def icon(self):
        """Node icon."""
        return QtGui.QIcon(":ht/rsc/icons/aovs/folder.png")

    @property
    def items(self):
        """Items belonging to this nodes children."""
        return [child.item for child in self.children]

    @property
    def name(self):
        """The display name"""
        return self._name

# =============================================================================

class AOVBaseNode(TreeNode):
    """Base node for AOV related items.

    """

    def __init__(self, item, parent=None):
        super(AOVBaseNode, self).__init__(parent)

        self._item = item

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def item(self):
        """AOV related item represented by this node."""
        return self._item

    @item.setter
    def item(self, item):
        self._item = item

    @property
    def path(self):
        """File path of this nodes item."""
        return self._item.filePath

# =============================================================================

class AOVNode(AOVBaseNode):
    """Node representing an AOV."""

    def __init__(self, aov, parent=None):
        super(AOVNode, self).__init__(aov, parent)

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def icon(self):
        """Icon for this AOV."""
        return utils.getIconFromVexType(self.item.vextype)

    @property
    def name(self):
        """The display name for this node."""
        return self.item.variable

    @property
    def aov(self):
        """The AOV object represented by this node."""
        return self.item

    @aov.setter
    def aov(self, aov):
        self.item = aov

    # =========================================================================
    # METHODS
    # =========================================================================

    def tooltip(self):
        """Return a tooltip for the AOV."""
        aov = self.aov

        lines = [
            "VEX Variable: {}".format(aov.variable),
            "VEX Type: {}".format(aov.vextype),
        ]

        if aov.channel:
            lines.append("Channel Name: {}".format(aov.channel))

        if aov.quantize is not None:
            lines.append("Quantize: {}".format(aov.quantize))

        if aov.sfilter is not None:
            lines.append("Sample Filter: {}".format(aov.sfilter))

        if aov.pfilter is not None:
            lines.append("Pixel Filter: {}".format(aov.pfilter))

        if aov.exclude_from_dcm is not None:
            lines.append(
                "Exclude from DCM: {}".format(aov.exclude_from_dcm)
            )

        if aov.componentexport:
            lines.append(
                "\nExport variable for each component: {}".format(
                    aov.componentexport
                )
            )

            lines.append(
                "Export Components: {}".format(", ".join(aov.components))
            )

        if aov.lightexport is not None:
            lines.append("\nLight Exports: {}".format(aov.lightexport))
            lines.append("Light Mask: {}".format(aov.lightexport_scope))
            lines.append("Light Selection: {}".format(aov.lightexport_select))

        if aov.comment:
            lines.append("\nComment: {}".format(aov.comment))

        if aov.priority > -1:
            lines.append("\nPriority: {}".format(aov.priority))

        if aov.source is not None:
            path = aov.source.path

            if aov.source.read_only:
                path = "{} (read only)".format(path)

            lines.append("\n{}".format(path))

        return '\n'.join(lines)


class GroupAOVNode(AOVNode):

    pass

# =============================================================================

class AOVGroupNode(AOVBaseNode):
    """Node representing an AOVGroup."""

    def __init__(self, group, parent=None):
        super(AOVGroupNode, self).__init__(group, parent)

        # Create child nodes for the group's AOVs.
        for aov in group.aovs:
            if isinstance(aov, GroupBasedAOV):
                GroupAOVNode(aov, self)

            else:
                AOVNode(aov, self)

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def icon(self):
        """Icon for this AOV group."""
        return utils.getIconFromGroup(self.group)

    @property
    def group(self):
        """The AOVGroup object represented by this node."""
        return self.item

    @group.setter
    def group(self, group):
        self.item = group

    @property
    def name(self):
        """The group name for this node."""
        return self.group.name

    # =========================================================================
    # METHODS
    # =========================================================================

    def tooltip(self):
        """Return a tooltip for the AOV group."""
        group = self.group

        lines = ["Name: {}".format(group.name)]

        if group.comment:
            lines.append("\nComment: {}".format(group.comment))

        if group.priority > -1:
            lines.append("\nPriority: {}".format(group.priority))

        if group.icon is not None:
            lines.append("\nIcon: {}".format(group.icon))

        if group.source is not None:
            path = group.source.path

            if group.source.read_only:
                path = "{} (read only)".format(path)

            lines.append("\n{}".format(path))

        return '\n'.join(lines)

# =============================================================================

class IntrinsicAOVGroupNode(AOVGroupNode):

    def __init__(self, group, parent=None):
        super(IntrinsicAOVGroupNode, self).__init__(group, parent)

    # =========================================================================

    @property
    def name(self):
        return self.group.name.lstrip("i:")

# =============================================================================
# PROXY MODELS
# =============================================================================

class LeafFilterProxyModel(QtCore.QSortFilterProxyModel):
    """Custom QSortFilterProxyModel designed to filter based on various
    TreeNode child types.

    """

    def __init__(self, parent=None):
        super(LeafFilterProxyModel, self).__init__(parent)

        # Make filter case insensitive.
        self.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setFilterRole(BaseAOVTreeModel.filterRole)

        self.setSortRole(BaseAOVTreeModel.sortRole)
        self.setDynamicSortFilter(True)

    # =========================================================================
    # METHODS
    # =========================================================================

    def filterAcceptsAnyParent_parent(self, parent):
        """Traverse to the root node and check if any of the ancestors
        match the filter.

        """
        while parent.isValid():
            if self.filterAcceptsRowItself(parent.row(), parent.parent()):
                return True

            parent = parent.parent()

        return False

    def filterAcceptsRow(self, row_num, source_parent):
        """Check if this filter will accept the row."""
        if self.filterAcceptsRowItself(row_num, source_parent):
            return True

        # Traverse up all the way to root and check if any of them match
        if self.filterAcceptsAnyParent_parent(source_parent):
            return True

        return self.hasAcceptedChildren(row_num, source_parent)

    def filterAcceptsRowItself(self, row_num, source_parent):
        """Check if this filter accepts this row."""
        return super(LeafFilterProxyModel, self).filterAcceptsRow(
            row_num,
            source_parent
        )

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

    def insertData(self, data, position=None):
        """Insert data at an optional position."""
        return self.sourceModel().insertData(data, position)

    def removeIndex(self, index):
        """Remove the row at an index."""
        return self.sourceModel().removeIndex(
            self.mapToSource(index)
        )

# =============================================================================
# TREE MODELS
# =============================================================================

class BaseAOVTreeModel(QtCore.QAbstractItemModel):
    """Base model for tree views."""

    filterRole = QtCore.Qt.UserRole
    sortRole = QtCore.Qt.UserRole + 1

    def __init__(self, root, parent=None):
        super(BaseAOVTreeModel, self).__init__(parent)

        self._root = root

    # =========================================================================

    @property
    def items(self):
        """A list of all AOV/AOVGroup items belonging to child nodes."""
        return [child.item for child in self.root.children]

    @property
    def root(self):
        return self._root

    # =========================================================================

    def columnCount(self, parent):
        """The number of columns in the view."""
        return 1

    def data(self, index, role):
        """Get item data."""
        if not index.isValid():
            return

        # Get the tree node.
        node = index.internalPointer()
        parent = node.parent

        if role == QtCore.Qt.DisplayRole:
            # If the item is an AOV who has an explicit channel set
            # then display the channel as well.
            if isinstance(node, AOVNode):
                aov = node.item

                if aov.channel:
                    return "{} ({})".format(aov.variable, aov.channel)

            return node.name

        if role == QtCore.Qt.DecorationRole:
            return node.icon

        if role == QtCore.Qt.ToolTipRole:
            return node.tooltip()

        if role == QtCore.Qt.FontRole:
            # Italicize AOVs inside groups.
            if not isinstance(node, GroupAOVNode):
                if isinstance(parent, AOVGroupNode):
                    font = QtGui.QFont()
                    font.setItalic(True)
                    return font

            return

        if role == QtCore.Qt.ForegroundRole:
            brush = QtGui.QBrush()

            # Grey out installed AOVs.
            if self.isInstalled(node):
                brush.setColor(QtGui.QColor(131, 131, 131))
                return brush

            if not isinstance(node, GroupAOVNode):
                # Grey out AOVs inside groups.
                if isinstance(parent, AOVGroupNode):
                    brush.setColor(QtGui.QColor(131, 131, 131))
                    return brush

            return

        if role == BaseAOVTreeModel.filterRole:
            if isinstance(node, FolderNode):
                return True

            if isinstance(node, AOVGroupNode):
                return node.name

            if isinstance(node.parent, AOVGroupNode):
                return True

            if isinstance(node, AOVNode):
                return node.name

            return True

        if role == self.sortRole:
            if isinstance(node, AOVBaseNode):
                return node.name

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

    def isInstalled(self, node):
        """Check whether a node is installed."""
        return False

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

# =============================================================================

class AOVSelectModel(BaseAOVTreeModel):
    """The model for the 'AOVs and Groups' tree."""

    def __init__(self, root, parent=None):
        super(AOVSelectModel, self).__init__(root, parent)

        self._installed = set()

    def findNamedFolder(self, name):
        """Find a folder with a given name."""
        node = self.getNode(QtCore.QModelIndex())

        for row in range(len(node.children)):
            child = node.children[row]

            if child.name == name:
                return self.createIndex(row, 0, child)

        return

    def initFromManager(self):
        """Initialize the data from the global manager."""
        self.beginResetModel()

        groups_node = FolderNode("Groups", self.root)
        aovs_node = FolderNode("AOVs", self.root)

        if manager.MANAGER.groups:
            groups = manager.MANAGER.groups

            for group in groups.itervalues():
                if isinstance(group, IntrinsicAOVGroup):
                    IntrinsicAOVGroupNode(group, groups_node)
                else:
                    AOVGroupNode(group, groups_node)

        if manager.MANAGER.aovs:
            aovs = manager.MANAGER.aovs

            for aov in aovs.itervalues():
                AOVNode(aov, aovs_node)

        self.endResetModel()

    def isInstalled(self, node):
        """Check if a node is installed."""
        if node in self._installed:
            return True

        return False

    def flags(self, index):
        """Item flags."""
        if not index.isValid():
            return

        node = index.internalPointer()
        parent = node.parent

        if isinstance(parent, AOVGroupNode):
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled

    def insertAOV(self, aov):
        """Insert an AOV into the tree."""
        index = self.findNamedFolder("AOVs")

        parent_node = self.getNode(index)

        # Check to see if an AOV of the same name already exists.  If it does
        # then we want to just update the internal item for the node.
        for row, child in enumerate(parent_node.children):
            # Check the child's AOV against the one to be added.
            if child.aov == aov:
                # Update the internal item.
                child.aov = aov

                existing_index = self.index(row, 0, index)

                # Signal the internal data changed.
                self.dataChanged.emit(
                    existing_index,
                    existing_index
                )

                # We're done here.
                break

        # Didn't find an existing one so insert a new node.
        else:
            position = len(parent_node.children)

            self.beginInsertRows(index, position, position)

            AOVNode(aov, parent_node)

            self.endInsertRows()

        return True

    def insertGroup(self, group):
        """Insert an AOVGroup into the tree."""
        index = self.findNamedFolder("Groups")

        parent_node = self.getNode(index)

        # Check to see if an AOV Group of the same name already exists.  If it
        # does then we want to just update the internal item for the node.
        for row, child in enumerate(parent_node.children):
            # Check the child's group against the one to be added.
            if child.group == group:
                # Update the internal item.
                child.group = group

                existing_index = self.index(row, 0, index)

                # Signal the internal data changed.
                self.dataChanged.emit(
                    existing_index,
                    existing_index
                )

                # We're done here.
                break

        else:
            position = len(parent_node.children)

            self.beginInsertRows(index, position, position)

            if isinstance(group, IntrinsicAOVGroup):
                IntrinsicAOVGroupNode(group, parent_node)
            else:
                AOVGroupNode(group, parent_node)

            self.endInsertRows()

        return True

    def markInstalled(self, items):
        """Mark a list of items as installed."""
        for item in items:
            self._installed.add(item)

    def markUninstalled(self, items):
        """Mark a list of items as uninstalled."""
        for item in items:
            self._installed.remove(item)

        parent = QtCore.QModelIndex()
        parent_node = self.getNode(parent)

        self.dataChanged.emit(
            self.index(0, 0, parent),
            self.index(len(parent_node.children)-1, 0, parent),
            [QtCore.Qt.DisplayRole],
        )

    def mimeData(self, indexes):
        """Generate mime data for indexes."""
        nodes = [self.getNode(index) for index in indexes]

        items = []

        for node in nodes:
            if self.isInstalled(node):
                continue

            if isinstance(node, FolderNode):
                for child in reversed(node.children):
                    items.append(child.item)
            else:
                items.append(node.item)

        mime_data = QtCore.QMimeData()

        mime_data.setData("text/csv", pickle.dumps(items))

        return mime_data

    def removeAOV(self, aov):
        """Remove an AOV from the tree."""
        index = self.findNamedFolder("AOVs")

        parent_node = self.getNode(index)

        for row, child in enumerate(parent_node.children):
            if child.aov == aov:
                self.beginRemoveRows(index, row, row)
                parent_node.removeChild(row)
                self.endRemoveRows()

                break

    def removeGroup(self, group):
        """Remove a group from the tree."""
        index = self.findNamedFolder("Groups")

        parent_node = self.getNode(index)

        for row, child in enumerate(parent_node.children):
            if child.group == group:
                self.beginRemoveRows(index, row, row)
                parent_node.removeChild(row)
                self.endRemoveRows()

                break

    def updateGroup(self, group):
        """Update the members of a group.

        This works by removing all existing AOVNodes and adding them back
        based on the new group membership.

        """
        index = self.findNamedFolder("Groups")

        parent_node = self.getNode(index)

        # Process each group in the tree.
        for row, child in enumerate(parent_node.children):
            # This group is the one to be updated.
            if child.group == group:
                child_index = self.index(row, 0, index)

                # Remove all the existing AOV nodes.
                self.beginRemoveRows(child_index, 0, len(child.children)-1)

                child.removeAllChildren()

                self.endRemoveRows()

                # Add all the AOVs from the updated group.
                self.beginInsertRows(child_index, 0, len(group.aovs) - 1)

                for aov in group.aovs:
                    AOVNode(aov, child)

                self.endInsertRows()

                # We're done here.
                break

# =============================================================================

class AOVsToAddModel(BaseAOVTreeModel):
    """This class represents the available AOVs and AOVGroups that will be
    added.

    """

    insertedItemsSignal = QtCore.Signal([AOVBaseNode])
    removedItemsSignal = QtCore.Signal([AOVBaseNode])

    def __init__(self, root, parent=None):
        super(AOVsToAddModel, self).__init__(root, parent)

    # =========================================================================
    # METHODS
    # =========================================================================

    def clearAll(self):
        """Clear the tree of any nodes."""
        parent = QtCore.QModelIndex()
        node = self.getNode(parent)

        # Remove each child.
        for row in reversed(range(len(node.children))):
            index = self.index(row, 0, parent)
            self.removeIndex(index)

    def dropMimeData(self, data, action, row, column, parent):
        """Handle dropping mime data on the view."""
        if not data.hasFormat("text/csv"):
            return False

        self.insertData(pickle.loads(data.data("text/csv")))

        return True

    def flags(self, index):
        """Tree node flags."""
        if not index.isValid():
            return

        node = index.internalPointer()
        parent = node.parent

        if parent == self.root:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled

        if isinstance(parent, AOVGroupNode):
            return QtCore.Qt.ItemIsEnabled

        return

    def insertData(self, data, position=None):
        """Insert data into the model."""
        parent = QtCore.QModelIndex()

        # Filter data to remove items that area already installed.
        data = [item for item in data if item not in self.items]

        parent_node = self.getNode(parent)

        if position is None:
            position = len(self.items)

        rows = len(data)

        if not rows:
            return False

        self.beginInsertRows(parent, position, position + rows - 1)

        added_items = []

        for item in data:
            if isinstance(item, AOV):
                child_node = AOVNode(item)

            elif isinstance(item, IntrinsicAOVGroup):
                child_node = IntrinsicAOVGroupNode(item)

            else:
                child_node = AOVGroupNode(item)

            parent_node.insertChild(position, child_node)
            added_items.append(child_node)

        self.insertedItemsSignal.emit(added_items)

        self.endInsertRows()

        return True

    def removeIndex(self, index):
        """Remove an index."""
        parent = QtCore.QModelIndex()
        parent_node = self.getNode(parent)

        row = index.row()

        self.beginRemoveRows(parent, row, row)

        self.removedItemsSignal.emit([parent_node.children[row]])
        parent_node.removeChild(row)

        self.endRemoveRows()

        return True

    def supportedDropActions(self):
        """Supported drop actions."""
        # Add support for MoveAction since that's what Houdini thinks is
        # happening when you try and drop a node on a widget.
        return QtCore.Qt.CopyAction

# =============================================================================

class AOVGroupEditListModel(QtCore.QAbstractListModel):
    """This class represents data defining AOVs belonging to an AOVGroup."""

    def __init__(self, parent=None):
        super(AOVGroupEditListModel, self).__init__(parent)

        # Grab all the possible AOVs at time of creation.
        self._aovs = manager.MANAGER.aovs.values()

        # List containing the checked state of each AOV
        self._checked = [False] * len(self._aovs)

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def aovs(self):
        """List of AOV choices."""
        return self._aovs

    @property
    def checked(self):
        return self._checked

    # =========================================================================
    # METHODS
    # =========================================================================

    def checkedAOVs(self):
        """Returns a list of AOVs which are checked."""
        return [aov for checked, aov in zip(self._checked, self.aovs)
                if checked]

    def data(self, index, role):
        """Get item data."""
        row = index.row()
        value = self.aovs[row]

        if role == QtCore.Qt.DisplayRole:
            return value.variable

        if role == QtCore.Qt.DecorationRole:
            return utils.getIconFromVexType(value.vextype)

        if role == QtCore.Qt.CheckStateRole:
            return self._checked[row]

    def flags(self, index):
        """Item flags."""
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable

    def rowCount(self, parent):
        """Number of rows."""
        return len(self.aovs)

    def setData(self, index, value, role):
        """Set item data."""
        if role == QtCore.Qt.CheckStateRole:
            row = index.row()

            # Update the internal checked stat.
            self._checked[row] = not self._checked[row]

            # Emit signal that the index changed.
            self.dataChanged.emit(index, index, [QtCore.Qt.CheckStateRole])

            return True

    def uncheckAll(self):
        """Uncheck all AOVs in the list."""
        self._checked = [False] * len(self._aovs)

# =============================================================================
# Info Dialog Models
# =============================================================================

class InfoTableModel(QtCore.QAbstractTableModel):
    """Base class for information table models."""

    def __init__(self, parent=None):
        super(InfoTableModel, self).__init__(parent)

        # Store the titles and values in lists since the count my vary
        # depending on the data set on the group.  This prevents having to do
        # redundant calculations inside rowCount() and data()
        self._titles = []
        self._values = []

    # =========================================================================
    # METHODS
    # =========================================================================

    def columnCount(self, parent):
        """Number of columns."""
        return 2

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Get item data."""
        if not index.isValid():
            return

        row = index.row()
        column = index.column()

        if role == QtCore.Qt.DisplayRole:
            if column == 0:
                return self._titles[row]
            else:
                return self._values[row]

    def flags(self, index):
        """Item flags."""
        return QtCore.Qt.ItemIsEnabled

    def index(self, row, column, parent=QtCore.QModelIndex()):
        """Get an index at a certain location."""
        return self.createIndex(row, column, parent)

    def rowCount(self, parent):
        """Number of rows."""
        return len(self._titles)

# =============================================================================

class AOVInfoTableModel(InfoTableModel):
    """This class represents information data about an AOV."""

    def __init__(self, parent=None):
        super(AOVInfoTableModel, self).__init__(parent)

    # =========================================================================
    # METHODS
    # =========================================================================

    def initDataFromAOV(self, aov):
        """Initialize data from an AOV."""
        self._titles = []
        self._values = []

        self._titles.append("VEX Variable")
        self._values.append(aov.variable)

        self._titles.append("VEX Type")
        self._values.append(aov.vextype)

        if aov.channel:
            self._titles.append("Channel Name")
            self._values.append(aov.channel)

        if aov.quantize is not None:
            self._titles.append("Quantize")
            self._values.append(aov.quantize)

        if aov.sfilter is not None:
            self._titles.append("Sample Filter")
            self._values.append(aov.sfilter)

        if aov.pfilter is not None:
            self._titles.append("Pixel Filter")
            self._values.append(aov.pfilter)

        if aov.exclude_from_dcm is not None:
            self._titles.append("Exclude from DCM")
            self._values.append(aov.exclude_from_dcm)

        if aov.componentexport:
            self._titles.append("Export Each Component")
            self._values.append(str(aov.componentexport))

            if aov.components:
                self._titles.append("Export Components")
                self._values.append(", ".join(aov.components))

        if aov.lightexport is not None:
            self._titles.append("Light Exports")
            self._values.append(aov.lightexport)

            if aov.lightexport != "per-category":
                self._titles.append("Light Mask")
                self._values.append(aov.lightexport_scope)

                self._titles.append("Light Selection")
                self._values.append(aov.lightexport_select)

        if aov.priority > -1:
            self._titles.append("Priority")
            self._values.append(aov.priority)

        if aov.intrinsics:
            self._titles.append("Intrinsics")
            self._values.append(", ".join(aov.intrinsics))

        if aov.comment:
            self._titles.append("Comment")
            self._values.append(aov.comment)

        if aov.source is not None:
            self._titles.append("Source")
            self._values.append(aov.source.path)

# =============================================================================

class AOVGroupInfoTableModel(InfoTableModel):
    """This class represents information data about an AOVGroup."""

    def __init__(self, parent=None):
        super(AOVGroupInfoTableModel, self).__init__(parent)

    # =========================================================================
    # METHODS
    # =========================================================================

    def initDataFromGroup(self, group):
        """Initialize table data from an AOVGroup."""
        is_intrinsic = isinstance(group, IntrinsicAOVGroup)

        # Reset data.
        self._titles = []
        self._values = []

        self._titles.append("Name")
        self._values.append(group.name)

        if group.comment:
            self._titles.append("Comment")
            self._values.append(group.comment)

        if group.priority > -1:
            self._titles.append("Priority")
            self._values.append(group.priority)

        if group.icon:
            self._titles.append("Icon")
            self._values.append(group.icon)

        if not is_intrinsic:
            self._titles.append("Source")
            self._values.append(group.source.path)

    def rowCount(self, parent):
        return len(self._titles)

# =============================================================================

class AOVGroupMemberListModel(QtCore.QAbstractListModel):
    """This class represents a list of AOVs belonging to an AOVGroup."""

    def __init__(self, parent=None):
        super(AOVGroupMemberListModel, self).__init__(parent)

        self._aovs = []

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def aovs(self):
        """AOVs contained in this group."""
        return self._aovs

    # =========================================================================
    # METHODS
    # =========================================================================

    def data(self, index, role):
        """Get item data."""
        row = index.row()
        value = self.aovs[row]

        if role == QtCore.Qt.DisplayRole:
            return value.variable

        if role == QtCore.Qt.DecorationRole:
            return utils.getIconFromVexType(value.vextype)

    def flags(self, index):
        """Item flags."""
        return QtCore.Qt.ItemIsEnabled

    def initDataFromGroup(self, group):
        """Initialize data from an AOVGroup."""
        self.beginResetModel()
        self._aovs = group.aovs
        self.endResetModel()

    def rowCount(self, parent):
        """Number of rows."""
        return len(self.aovs)

