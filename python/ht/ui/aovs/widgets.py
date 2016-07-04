"""This module contains custom PySide widgets."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
from PySide import QtCore, QtGui
import os
import pickle

# Houdini Toolbox Imports
from ht.sohohooks.aovs import manager
from ht.sohohooks.aovs.aov import AOV, AOVGroup, IntrinsicAOVGroup
from ht.ui.aovs import models, uidata, utils

# Houdini Imports
import hou

# =============================================================================
# CLASSES
# =============================================================================

class AOVManagerWidget(QtGui.QWidget):
    """Primary AOV Manager widget."""

    invalidAOVSelectedSignal = QtCore.Signal()
    selectedAOVContainedSignal = QtCore.Signal(bool)

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, node=None, parent=None):
        super(AOVManagerWidget, self).__init__(parent)

        self.node = node

        self.initUI()

        # Left/right button action signals.
        self.select_widget.installSignal.connect(self.to_add_widget.installListener)
        self.select_widget.uninstallSignal.connect(self.to_add_widget.uninstallListener)

        # Update left/right buttons after data changed.
        self.select_widget.aov_tree.selectionChangedSignal.connect(self.checkNodeAdded)
        self.to_add_widget.updateEnabledSignal.connect(self.checkNodeAdded)

        # Left/right button enabling/disabling.
        self.selectedAOVContainedSignal.connect(self.select_widget.install_bar.enableHandler)
        self.invalidAOVSelectedSignal.connect(self.select_widget.install_bar.disableHandler)

        # Really need a signal?  Maybe just refresh everything?
        manager.MANAGER.initInterface()
        manager.MANAGER.interface.aovAddedSignal.connect(self.select_widget.aov_tree.insertAOV)
        manager.MANAGER.interface.aovRemovedSignal.connect(self.select_widget.aov_tree.removeAOV)
        manager.MANAGER.interface.groupAddedSignal.connect(self.select_widget.aov_tree.insertGroup)
        manager.MANAGER.interface.groupRemovedSignal.connect(self.select_widget.aov_tree.removeGroup)

        self.to_add_widget.tree.model().sourceModel().insertedItemsSignal.connect(
            self.select_widget.markItemsInstalled
        )

        self.to_add_widget.tree.model().sourceModel().removedItemsSignal.connect(
            self.select_widget.markItemsUninstalled
        )

        self.setStyleSheet(uidata.TOOLTIP_STYLE)

    # =========================================================================
    # METHODS
    # =========================================================================

    def checkNodeAdded(self):
        """This function detects whether selected tree nodes are currently
        in the 'AOVs to Apply' tree.

        """
        # Get selected nodes in the 'AOVs and Groups' tree.
        nodes = self.select_widget.getSelectedNodes()

        if nodes:
            # Are any contained.
            contains = False

            for node in nodes:
                # See if the node corresponds to an index in the target view.
                if self.to_add_widget.tree.nodeIndexInModel(node) is not None:
                    contains = True
                    break

            # Notify the move to left/right buttons on the status.
            self.selectedAOVContainedSignal.emit(contains)

        else:
            self.invalidAOVSelectedSignal.emit()

    def initUI(self):
        """Initliaze the UI."""
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        layout.setContentsMargins(0, 0, 0, 0)

        # =====================================================================

        splitter = QtGui.QSplitter()
        layout.addWidget(splitter)

        self.select_widget = AOVSelectWidget()
        splitter.addWidget(self.select_widget)

        # =====================================================================

        self.to_add_widget = AOVsToAddWidget(self.node)
        splitter.addWidget(self.to_add_widget)


class AOVViewerToolBar(QtGui.QToolBar):
    """This class represents a base toolbar class used for AOVs."""

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, parent=None):
        super(AOVViewerToolBar, self).__init__(parent)

        self.setStyleSheet(uidata.AOVVIEWERTOOLBAR_STYLE)
        self.setIconSize(QtCore.QSize(24, 24))

# =============================================================================
# AOVs and Groups
# =============================================================================

class AOVSelectTreeWidget(QtGui.QTreeView):
    """This class represents a tree with AOVs and AOVGroups that can be
    added to renders.

    """
    selectionChangedSignal = QtCore.Signal()

    installItemsSignal = QtCore.Signal(models.AOVBaseNode)
    uninstallItemsSignal = QtCore.Signal(models.AOVBaseNode)

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, parent=None):
        super(AOVSelectTreeWidget, self).__init__(parent)

        self.root = models.TreeNode()

        model = models.AOVSelectModel(self.root)
        self.proxy_model = models.LeafFilterProxyModel()
        self.proxy_model.setSourceModel(model)
        self.setModel(self.proxy_model)

        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        self.setAlternatingRowColors(True)
        self.setHeaderHidden(True)
        self.setDragEnabled(True)

        self.setSortingEnabled(True)
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)

        selection_model = self.selectionModel()
        selection_model.selectionChanged.connect(self.selectionChangedHandler)

        self.initFromManager()

        self.setAcceptDrops(True)

    # =========================================================================
    # METHODS
    # =========================================================================

    def collapseBelow(self):
        """Collapse all child folders and groups."""
        indexes = self.selectedIndexes()

        for index in indexes:
            self.collapseIndex(index)

    def collapseIndex(self, index):
        """Collapse an index and all it's children."""
        self.collapse(index)

        if self.model().hasChildren(index):
            for i in range(self.model().rowCount(index)):
                idx = self.model().index(i, 0, index)
                self.collapseIndex(idx)

    def collapseSelected(self):
        """Collapse selected folders and groups."""
        indexes = self.selectedIndexes()

        for index in reversed(indexes):
            self.collapse(index)

    def dragEnterEvent(self, event):
        """Event occuring when something is dragged into the widget."""
        # Accept text containing events so we can drop Houdini nodes and files.
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Event when dropping items onto widget."""
        import ht.ui.aovs.dialogs

        # Get the data attached to this event.
        mime_data = event.mimeData()

        # Get text data which corresponds to node paths (or files).
        data = str(mime_data.text())
        paths = data.split(",")

        # Process any urls (files).
        if mime_data.hasUrls():
            for url in mime_data.urls():
                # Only care about actual files on disk.
                if not url.scheme() == "file":
                    continue

                # Extract file path.
                path = str(url.toLocalFile())

                # Load a .json file that exists on disk.
                if os.path.exists(path):
                    ext = os.path.splitext(path)[-1]

                    if ext == ".json":
                        manager.MANAGER.load(path)

        # Process paths, looking for nodes.  Any file paths represented by
        # urls that were handled above will also be in this list because they
        # are strings but will be ignored below since the call to hou.node()
        # will not return anything.
        for path in paths:
            # Find the node.
            node = hou.node(path)

            if node is None:
                continue

            # Can only import from Mantra nodes.
            if node.type() != hou.nodeType("Driver/ifd"):
                continue

            num_aovs = node.evalParm("vm_numaux")

            if not num_aovs:
                continue

            # Get AOV objects from multiparms.
            aovs = utils.buildAOVsFromMultiparm(node)

            # Launch the Create New AOV dialog on each AOV.
            for aov in aovs:
                ht.ui.aovs.dialogs.createNewAOV(aov)

    def editSelected(self):
        """Edit selected nodes."""
        self.editSelectedAOVs()
        self.editSelectedGroups()

    def editSelectedAOVs(self):
        """Edit selected AOVs."""
        import ht.ui.aovs.dialogs

        aovs = [node.item for node in self.getSelectedNodes()
                if not isinstance(node, models.FolderNode) and isinstance(node.item, AOV)]

        for aov in aovs:
            ht.ui.aovs.dialogs.editAOV(aov)

    def editSelectedGroups(self):
        """Edit selected AOVs."""
        import ht.ui.aovs.dialogs

        groups = [node.item for node in self.getSelectedNodes()
                  if not isinstance(node, models.FolderNode) and isinstance(node.item, AOVGroup)]

        parent = QtGui.QApplication.instance().activeWindow()

        # TODO: Move to function in dialogs and handle group update. Like above calls editAOV()
        for group in groups:
            if isinstance(group, IntrinsicAOVGroup):
                continue

            edit_dialog = ht.ui.aovs.dialogs.EditGroupDialog(
                group,
                parent
            )

            edit_dialog.groupUpdatedSignal.connect(self.updateGroup)

            edit_dialog.show()

    def expandBelow(self):
        """Expand all child folders and groups."""
        indexes = self.selectedIndexes()

        for index in indexes:
            self.expandIndex(index)

    def expandIndex(self, index):
        """Expand an index and all it's children."""
        self.expand(index)

        if self.model().hasChildren(index):
            for i in range(self.model().rowCount(index)):
                idx = self.model().index(i, 0, index)
                self.expandIndex(idx)

    def expandSelected(self):
        """Expand selected folders and groups."""
        indexes = self.selectedIndexes()

        for index in reversed(indexes):
            self.expand(index)

    def getSelectedNodes(self):
        """Get a list of selected tree nodes."""
        nodes = []

        indexes = self.selectionModel().selectedIndexes()

        model = self.model()
        source_model = model.sourceModel()

        for index in indexes:
            index = model.mapToSource(index)
            nodes.append(source_model.getNode(index))

        return nodes

    def initFromManager(self):
        """Initliaze the tree from the manager."""
        self.root.removeAllChildren()

        self.proxy_model.sourceModel().initFromManager()

        # Expand the main folders but not the groups.
        self.expandToDepth(0)

    def insertAOV(self, aov):
        """Add an AOV to the model."""
        self.model().sourceModel().insertAOV(aov)

    def insertGroup(self, group):
        """Add an AOVGroup to the model."""
        self.model().sourceModel().insertGroup(group)

    def installSelected(self):
        """Install selected nodes."""
        nodes = self.getSelectedNodes()

        if nodes:
            self.installItemsSignal.emit(nodes)

    def keyPressEvent(self, event):
        """Handle keystrokes."""
        key = event.key()

        if key == QtCore.Qt.Key_I:
            self.showInfo()
            return

        elif key == QtCore.Qt.Key_Y:
            self.installSelected()
            return

        elif key == QtCore.Qt.Key_U:
            self.uninstallSelected()
            return

        elif key == QtCore.Qt.Key_E:
            self.editSelected()
            return

        super(AOVSelectTreeWidget, self).keyPressEvent(event)

    def markItemsInstalled(self, items):
        """Mark items as currently installed in the tree."""
        self.model().sourceModel().markInstalled(items)

    def markItemsUninstalled(self, items):
        """Mark items as not currently installed in the tree."""
        self.model().sourceModel().markUninstalled(items)

    def openMenu(self, position):
        """Open the RMB context menu."""
        indexes = self.selectedIndexes()

        menu = QtGui.QMenu(self)

        show_expand = False
        show_collapse = False
        show_exp_col_all = False

        show_install = False
        show_uninstall = False

        show_edit = False
        show_info = False

        model = self.model()
        source_model = model.sourceModel()

        for index in indexes:
            source_index = model.mapToSource(index)
            node = source_index.internalPointer()

            # We can collapse and expand folder and group nodes.
            if isinstance(node, (models.AOVGroupNode, models.FolderNode)):
                show_exp_col_all = True

                if self.isExpanded(index):
                    show_collapse = True
                else:
                    show_expand = True

            # Show into item for AOVs and groups.
            if isinstance(node, (models.AOVNode, models.AOVGroupNode)):
                show_info = True

                if isinstance(node, models.IntrinsicAOVGroupNode):
                    show_edit = show_edit or False

                else:
                    show_edit = True

                is_installed = source_model.isInstalled(node)

                if is_installed:
                    show_uninstall = True

                else:
                    show_install = True

        if show_collapse:
            menu.addAction(
                "Collapse",
                self.collapseSelected,
                QtGui.QKeySequence(QtCore.Qt.Key_Left)
            )

        if show_expand:
            menu.addAction(
                "Expand",
                self.expandSelected,
                QtGui.QKeySequence(QtCore.Qt.Key_Right)
            )

        if show_exp_col_all:
            menu.addAction(
                "Collapse All",
                self.collapseBelow
            )

            menu.addAction(
                "Expand All",
                self.expandBelow
            )

            menu.addSeparator()

        menu.addAction(
            "Select All",
            self.selectAll,
            QtGui.QKeySequence.SelectAll
        )

        menu.addSeparator()

        if show_info:
            menu.addAction(
                "Info",
                self.showInfo,
                QtGui.QKeySequence(QtCore.Qt.Key_I),
            )

            menu.addSeparator()

        if show_install:
            menu.addAction(
                "Install",
                self.installSelected,
                QtGui.QKeySequence(QtCore.Qt.Key_Y),
            )

        if show_uninstall:
            menu.addAction(
                "Uninstall",
                self.uninstallSelected,
                QtGui.QKeySequence(QtCore.Qt.Key_U),
            )

        if show_edit:
            menu.addSeparator()

            menu.addAction(
                "Edit",
                self.editSelected,
                QtGui.QKeySequence(QtCore.Qt.Key_E),
            )

        menu.exec_(self.mapToGlobal(position))

    def removeAOV(self, aov):
        """Remove an AOV from the model."""
        self.model().sourceModel().removeAOV(aov)

    def removeGroup(self, group):
        """Remove a group from the model."""
        self.model().sourceModel().removeGroup(group)

    def selectionChangedHandler(self, selected, deselected):
        """Selection change handler."""
        self.selectionChangedSignal.emit()

    def showAOVInfo(self):
        """Show info for selected AOVs."""
        import ht.ui.aovs.dialogs

        nodes = self.getSelectedNodes()

        filtered = [node for node in nodes
                    if isinstance(node, models.AOVNode)]

        parent = QtGui.QApplication.instance().activeWindow()

        for node in filtered:
            info_dialog = ht.ui.aovs.dialogs.AOVInfoDialog(
                node.aov,
                parent
            )

            info_dialog.show()

    def showAOVGroupInfo(self):
        """Show info for selected AOVGroups."""
        import ht.ui.aovs.dialogs

        nodes = self.getSelectedNodes()

        filtered = [node for node in nodes
                    if isinstance(node, models.AOVGroupNode)]

        parent = QtGui.QApplication.instance().activeWindow()

        for node in filtered:
            info_dialog = ht.ui.aovs.dialogs.AOVGroupInfoDialog(
                node.group,
                parent
            )

            info_dialog.groupUpdatedSignal.connect(self.updateGroup)

            info_dialog.show()

    def showInfo(self):
        """Show info for selected nodes."""
        self.showAOVInfo()
        self.showAOVGroupInfo()

    def uninstallSelected(self):
        """Uninstall selected nodes."""
        nodes = self.getSelectedNodes()

        if nodes:
            self.uninstallItemsSignal.emit(nodes)

    def updateGroup(self, group):
        """Update a group's members."""
        self.model().sourceModel().updateGroup(group)


class AOVInstallBarWidget(QtGui.QWidget):
    """This class represents the vertical bar with buttons to install and
    uninstall items from the 'AOVs and Groups' tree.

    """

    installSignal = QtCore.Signal()
    uninstallSignal = QtCore.Signal()

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, parent=None):
        super(AOVInstallBarWidget, self).__init__(parent)

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        # =====================================================================

        self.reload = QtGui.QPushButton("")
        layout.addWidget(self.reload)

        self.reload.setIcon(
            hou.ui.createQtIcon("BUTTONS_reload")
        )
        self.reload.setIconSize(QtCore.QSize(14, 14))
        self.reload.setMaximumSize(QtCore.QSize(20, 20))
        self.reload.setToolTip("Refresh the tree display.")
        self.reload.setFlat(True)

        # =====================================================================

        layout.addStretch(1)

        # =====================================================================

        self.install_button = QtGui.QPushButton("")
        layout.addWidget(self.install_button, alignment=QtCore.Qt.AlignVCenter)

        self.install_button.setIcon(
            hou.ui.createQtIcon("BUTTONS_move_to_right")
        )
        self.install_button.setIconSize(QtCore.QSize(14, 14))
        self.install_button.setMaximumSize(QtCore.QSize(20, 20))
        self.install_button.setToolTip("Add selected to list.")
        self.install_button.setEnabled(False)
        self.install_button.setFlat(True)

        self.install_button.clicked.connect(self.installSignal)

        # =====================================================================

        self.uninstall_button = QtGui.QPushButton("")
        layout.addWidget(self.uninstall_button, alignment=QtCore.Qt.AlignVCenter)

        self.uninstall_button.setIcon(
            hou.ui.createQtIcon("BUTTONS_move_to_left")
        )
        self.uninstall_button.setIconSize(QtCore.QSize(14, 14))
        self.uninstall_button.setMaximumSize(QtCore.QSize(20, 20))
        self.uninstall_button.setToolTip("Remove selected from list.")
        self.uninstall_button.setEnabled(False)
        self.uninstall_button.setFlat(True)

        self.uninstall_button.clicked.connect(self.uninstallSignal)

        # =====================================================================

        layout.addStretch(1)
        layout.setContentsMargins(0, 0, 0, 0)

    # =========================================================================
    # METHODS
    # =========================================================================

    def disableHandler(self):
        """Disable both buttons."""
        self.install_button.setEnabled(False)
        self.uninstall_button.setEnabled(False)

    def enableHandler(self, contains):
        """Enable and disable buttons based on if an item is contained."""
        self.install_button.setEnabled(not contains)
        self.uninstall_button.setEnabled(contains)


class AvailableAOVsToolBar(AOVViewerToolBar):
    """This class represents the toolbar for the 'AOVs and Groups' tree."""

    displayInfoSignal = QtCore.Signal()
    editAOVSignal = QtCore.Signal()
    editGroupSignal = QtCore.Signal()
    newGroupSignal = QtCore.Signal()

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, parent=None):
        super(AvailableAOVsToolBar, self).__init__(parent)

        import ht.ui.aovs.dialogs

        # Button and action to create a new AOV.
        new_aov_button = QtGui.QToolButton(self)
        self.addWidget(new_aov_button)

        new_aov_action = QtGui.QAction(
            QtGui.QIcon(":ht/rsc/icons/aovs/create_aov.png"),
            "Create a new AOV.",
            self,
            triggered=ht.ui.aovs.dialogs.createNewAOV
        )

        new_aov_button.setDefaultAction(new_aov_action)

        # =====================================================================

        # Button and action to edit an AOV.
        self.edit_aov_button = QtGui.QToolButton(self)
        self.addWidget(self.edit_aov_button)

        edit_aov_action = QtGui.QAction(
            QtGui.QIcon(":ht/rsc/icons/aovs/edit_aov.png"),
            "Edit AOV.",
            self,
            triggered=self.editAOVSignal.emit
        )

        self.edit_aov_button.setDefaultAction(edit_aov_action)
        self.edit_aov_button.setEnabled(False)

        # =====================================================================

        self.addSeparator()

        # =====================================================================

        # Button and action to create a new AOVGroup.
        new_group_button = QtGui.QToolButton(self)
        self.addWidget(new_group_button)

        new_group_action = QtGui.QAction(
            QtGui.QIcon(":ht/rsc/icons/aovs/create_group.png"),
            "Create a new AOV group.",
            self,
            triggered=self.newGroupSignal.emit
        )

        new_group_button.setDefaultAction(new_group_action)

        # =====================================================================

        # Button and action to edit an AOVGroup.
        self.edit_group_button = QtGui.QToolButton(self)
        self.addWidget(self.edit_group_button)

        edit_group_action = QtGui.QAction(
            QtGui.QIcon(":ht/rsc/icons/aovs/edit_group.png"),
            "Edit an AOV group.",
            self,
            triggered=self.editGroupSignal.emit
        )

        self.edit_group_button.setDefaultAction(edit_group_action)
        self.edit_group_button.setEnabled(False)

        # =====================================================================

        self.addSeparator()

        # =====================================================================

        # Button and action to load a .json file.
        load_file_button = QtGui.QToolButton(self)
        self.addWidget(load_file_button)

        load_file_action = QtGui.QAction(
            hou.ui.createQtIcon("COMMON_file"),
            "Load AOVs from .json files.",
            self,
            triggered=manager.loadJsonFiles
        )

        load_file_button.setDefaultAction(load_file_action)

        # =====================================================================

        spacer = QtGui.QWidget()
        spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.addWidget(spacer)

        # =====================================================================

        # Button and action to display information for selected items.
        self.info_button = QtGui.QToolButton(self)
        self.addWidget(self.info_button)

        info_action = QtGui.QAction(
            hou.ui.createQtIcon("BUTTONS_info"),
            "Display information about the AOV or group.",
            self,
            triggered=self.displayInfoSignal.emit
        )

        self.info_button.setDefaultAction(info_action)
        self.info_button.setEnabled(False)

    # =========================================================================
    # METHODS
    # =========================================================================

    def enableEditAOV(self, enable):
        """Enable the Edit AOV button."""
        self.edit_aov_button.setEnabled(enable)

    def enableEditAOVGroup(self, enable):
        """Enable the Edit AOV Group button."""
        self.edit_group_button.setEnabled(enable)

    def enableInfoButton(self, enable):
        """Enable the View Info button."""
        self.info_button.setEnabled(enable)


class AOVSelectWidget(QtGui.QWidget):
    """This class represents the AOVs and Groups widget."""

    # Install and remove signals.
    installSignal = QtCore.Signal(models.AOVBaseNode)
    uninstallSignal = QtCore.Signal(models.AOVBaseNode)

    # Button enabling signals.
    enableEditAOVSignal = QtCore.Signal(bool)
    enableEditAOVGroupSignal = QtCore.Signal(bool)
    enableInfoButtonSignal = QtCore.Signal(bool)

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, parent=None):
        super(AOVSelectWidget, self).__init__(parent)

        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)

        tree_layout = QtGui.QVBoxLayout()
        layout.addLayout(tree_layout)

        # =====================================================================

        label = QtGui.QLabel("AOVs and Groups")
        tree_layout.addWidget(label)

        bold_font = QtGui.QFont()
        bold_font.setBold(True)
        label.setFont(bold_font)

        # =====================================================================

        self.aov_tree = AOVSelectTreeWidget(parent=self)
        tree_layout.addWidget(self.aov_tree)

        self.aov_tree.selectionChangedSignal.connect(self.updateToolButtons)
        self.aov_tree.installItemsSignal.connect(self.installSignal.emit)
        self.aov_tree.uninstallItemsSignal.connect(self.uninstallSignal.emit)

        # =====================================================================

        self.filter = FilterWidget()
        tree_layout.addWidget(self.filter)

        self.filter.field.textChanged.connect(self.aov_tree.proxy_model.setFilterWildcard)

        # =====================================================================

        self.toolbar = AvailableAOVsToolBar(parent=self)
        tree_layout.addWidget(self.toolbar)

        self.toolbar.displayInfoSignal.connect(self.displayInfo)
        self.toolbar.editAOVSignal.connect(self.editAOV)
        self.toolbar.editGroupSignal.connect(self.editGroup)
        self.toolbar.newGroupSignal.connect(self.createGroup)

        # =====================================================================

        self.install_bar = AOVInstallBarWidget()
        layout.addWidget(self.install_bar)

        self.install_bar.installSignal.connect(self.emitInstallSignal)
        self.install_bar.uninstallSignal.connect(self.emitUninstallSignal)
        self.install_bar.reload.clicked.connect(self.reload)

        # =====================================================================

        # Connect signals to update the toolbar.
        self.enableEditAOVSignal.connect(self.toolbar.enableEditAOV)
        self.enableEditAOVGroupSignal.connect(self.toolbar.enableEditAOVGroup)
        self.enableInfoButtonSignal.connect(self.toolbar.enableInfoButton)

    # =========================================================================
    # METHODS
    # =========================================================================

    def createGroup(self):
        """Create a new group using any selected AOVs."""
        import ht.ui.aovs.dialogs

        aovs = [node.item for node in self.aov_tree.getSelectedNodes()
                if isinstance(node.item, AOV)]

        ht.ui.aovs.dialogs.createNewGroup(aovs)

    def displayInfo(self):
        """Display information based on the tree selection."""
        self.aov_tree.showInfo()

    def editAOV(self):
        """Edit selected AOVs."""
        self.aov_tree.editSelectedAOVs()

    def editGroup(self):
        """Edit selected AOVGroups."""
        self.aov_tree.editSelectedGroups()

    def emitInstallSignal(self):
        """Emit a signal to install selected nodes."""
        nodes = self.getSelectedNodes()

        if nodes:
            self.installSignal.emit(nodes)

    def emitUninstallSignal(self):
        """Emit a signal to removel selected nodes."""
        nodes = self.getSelectedNodes()

        if nodes:
            self.uninstallSignal.emit(nodes)

    def getSelectedNodes(self):
        """Get a list of selected nodes in the tree."""
        return self.aov_tree.getSelectedNodes()

    def markItemsInstalled(self, items):
        """Mark items as currently installed in the tree."""
        self.aov_tree.markItemsInstalled(items)

    def markItemsUninstalled(self, items):
        """Mark items as not currently installed in the tree."""
        self.aov_tree.markItemsUninstalled(items)

    def reload(self):
        """Reinitialize the tree from the manager."""
        self.aov_tree.initFromManager()

    def updateToolButtons(self):
        """Enable toolbar buttons based on node selection."""
        nodes = self.getSelectedNodes()

        enable_edit_aov = False
        enable_edit_group = False
        enable_info = False

        if nodes:
            for node in nodes:
                if isinstance(node, models.AOVNode):
                    enable_edit_aov = True
                    enable_info = True

                elif isinstance(node, models.IntrinsicAOVGroupNode):
                    enable_edit_group = False
                    enable_info = True

                elif isinstance(node, models.AOVGroupNode):
                    enable_edit_group = True
                    enable_info = True

        self.enableEditAOVSignal.emit(enable_edit_aov)
        self.enableEditAOVGroupSignal.emit(enable_edit_group)
        self.enableInfoButtonSignal.emit(enable_info)

# =============================================================================
# AOVs to Apply
# =============================================================================

class AOVsToAddTreeWidget(QtGui.QTreeView):
    """This class represents a tree with AOVs and AOVGroups that can be applied
    to a node or render.

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, parent=None):
        super(AOVsToAddTreeWidget, self).__init__(parent)

        self.root = models.TreeNode(None)

        model = models.AOVsToAddModel(self.root)

        self.proxy_model = models.LeafFilterProxyModel()
        self.proxy_model.setSourceModel(model)
        self.setModel(self.proxy_model)

        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        self.setAlternatingRowColors(True)
        self.setHeaderHidden(True)
        self.setAcceptDrops(True)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)

    # =========================================================================
    # METHODS
    # =========================================================================

    def clearAll(self):
        """Clear all items from the tree."""
        self.model().sourceModel().clearAll()

    def collapseSelected(self):
        """Collapse any selected indexes."""
        indexes = self.selectedIndexes()

        for index in indexes:
            self.collapse(index)

    def dragEnterEvent(self, event):
        """Event occuring when something is dragged into the widget."""
        # Dropping our items.
        if event.mimeData().hasFormat("text/csv"):
            event.acceptProposedAction()

        # Dropping Houdini nodes.
        elif event.mimeData().hasFormat("text/plain"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Event when dropping items onto widget."""
        # Get the data attached to this event.
        mime_data = event.mimeData()

        # Handle our own drop events.
        if mime_data.hasFormat("text/csv"):
            # Extract the serialized json mimedata from the event.
            data = pickle.loads(mime_data.data("text/csv"))

            # Flatten any data when moving with Ctrl.
            if event.keyboardModifiers() == QtCore.Qt.ControlModifier:
                data = utils.flattenList(data)

                # Repack the data with out flattened list.
                mime_data.setData("text/csv", pickle.dumps(data))

        # Try to handle dropping nodes on the tree.
        elif mime_data.hasFormat("text/plain"):
            # Nodes are represented as string paths, possibly comma-separated
            # in the case of multiple nodes.
            data = str(mime_data.data("text/plain"))
            paths = data.split(",")

            found_nodes = False

            new_data = []

            for path in paths:
                node = hou.node(path)

                if node is not None:
                    value = ""
                    aov_parm = node.parm("auto_aovs")

                    if aov_parm is not None:
                        value = aov_parm.eval()

                    names = utils.getAOVNamesFromMultiparm(node)
                    if names:
                        value = "{} {}".format(value, " ".join(names))

                    aovs = manager.MANAGER.getAOVsFromString(value)

                    if aovs:
                        new_data.extend(aovs)
                        found_nodes = True

            # Allow for Ctrl + Drop to extract groups.
            if event.keyboardModifiers() == QtCore.Qt.ControlModifier:
                new_data = utils.flattenList(new_data)

            # If we've found any nodes we'll add the AOV data and remove the
            # old data.
            if found_nodes:
                mime_data.setData("text/csv", pickle.dumps(new_data))
                mime_data.removeFormat("text/plain")

        # Call the superclass dropEvent() with our possibly modified data to
        # pass the work to the model dropMimeData() method.
        super(AOVsToAddTreeWidget, self).dropEvent(event)

    def expandSelected(self):
        """Expand selected AOVGroups."""
        indexes = self.selectedIndexes()

        for index in indexes:
            self.expand(index)

    def extractSelected(self):
        """Extract AOVs from selected AOVGroups."""
        indexes = self.selectedIndexes()

        model = self.model()

        # Process list in reverse since we're removing things.
        for index in reversed(indexes):
            source_index = model.mapToSource(index)
            node = source_index.internalPointer()

            # Only care about AOVGroupNodes.
            if isinstance(node, models.AOVNode):
                continue

            # Use a reversed list of AOVs since we're inserting them all in the
            # sample position so they maintain their order as shown in the
            # group.
            aovs = reversed(node.group.aovs)
            row = index.row()

            # Remove the AOVGroupNode from the list.
            model.removeIndex(index)

            # Add the AOVs from that group to the tree it the groups previous
            # position.
            model.sourceModel().insertData(aovs, row)

    def getElementsToAdd(self):
        """Get a list of elements in the tree."""
        return self.model().sourceModel().items

    def installItems(self, items):
        """Install items into the tree."""
        self.model().insertData(items)

    def keyPressEvent(self, event):
        """Handle keystrokes."""
        key = event.key()

        if key == QtCore.Qt.Key_Delete:
            self.removeSelected()
            return

        elif key == QtCore.Qt.Key_E:
            self.extractSelected()
            return

        super(AOVsToAddTreeWidget, self).keyPressEvent(event)

    def nodeIndexInModel(self, node):
        """Given an tree node, attempt to find its index in the trees model."""
        model = self.model()

        root = QtCore.QModelIndex()

        if model.hasChildren(root):
            for i in range(model.rowCount(root)):
                index = model.index(i, 0, root)
                item = model.mapToSource(index).internalPointer()

                if item == node:
                    return index

        return None

    def numItemsToAdd(self):
        """Get the number of items in the tree."""
        return self.model().sourceModel().rowCount(QtCore.QModelIndex())

    def openMenu(self, position):
        """Open the RMB context menu."""
        indexes = self.selectedIndexes()

        menu = QtGui.QMenu(self)

        # Expand/collapse
        show_expand = False
        show_collapse = False

        for index in indexes:
            source_index = self.model().mapToSource(index)
            node = source_index.internalPointer()

            if isinstance(node, models.AOVGroupNode):
                if self.isExpanded(index):
                    show_collapse = True
                else:
                    show_expand = True

        if show_collapse:
            menu.addAction(
                "Collapse",
                self.collapseSelected,
                QtGui.QKeySequence(QtCore.Qt.Key_Left)
            )

        if show_expand:
            menu.addAction(
                "Expand",
                self.expandSelected,
                QtGui.QKeySequence(QtCore.Qt.Key_Right)
            )

        if show_collapse or show_expand:
            menu.addAction(
                "Collapse All",
                self.collapseAll
            )

            menu.addAction(
                "Expand All",
                self.expandAll
            )

            menu.addSeparator()

        menu.addAction(
            "Select All",
            self.selectAll,
            QtGui.QKeySequence.SelectAll
        )

        menu.addAction(
            "Delete",
            self.removeSelected,
            QtGui.QKeySequence.Delete,
        )

        menu.addSeparator()

        show_extract = False

        for index in indexes:
            idx = self.model().mapToSource(index)
            node = idx.internalPointer()

            if isinstance(node, models.AOVGroupNode):
                show_extract = True
                break

        if show_extract:
            menu.addAction(
                "Extract AOVs from group",
                self.extractSelected,
                QtGui.QKeySequence(QtCore.Qt.Key_E),
            )

        menu.exec_(self.mapToGlobal(position))

    def removeSelected(self):
        """Remove selected items."""
        indexes = self.selectedIndexes()

        for index in reversed(indexes):
            self.model().removeIndex(index)


class AOVsToAddToolBar(AOVViewerToolBar):
    """This class represents the toolbar for the 'AOVs to Apply' tree."""

    # Signals for applying to nodes.
    applyAtRenderTimeSignal = QtCore.Signal()
    applyToParmsSignal = QtCore.Signal()

    # Signal to create a group from selected things.
    newGroupSignal = QtCore.Signal()

    # Signal to install items to the tree.
    installSignal = QtCore.Signal(list)

    # Signal for clearing all items.
    clearAOVsSignal = QtCore.Signal()

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, parent=None):
        super(AOVsToAddToolBar, self).__init__(parent)

        # Button and action to apply AOVs at render time.
        self.apply_button = QtGui.QToolButton(self)
        self.addWidget(self.apply_button)

        apply_action = QtGui.QAction(
            hou.ui.createQtIcon("NETWORKS_rop"),
            "Apply",
            self,
            triggered=self.applyAtRenderTimeSignal.emit

        )

        apply_action.setToolTip("Apply AOVs to selected nodes at render time.")

        self.apply_button.setDefaultAction(apply_action)
        self.apply_button.setEnabled(False)

        # =====================================================================

        # Button and action to apply AOVs are multiparms.
        self.apply_as_parms_button = QtGui.QToolButton(self)
        self.addWidget(self.apply_as_parms_button)

        parms_action = QtGui.QAction(
            hou.ui.createQtIcon("PANETYPES_parameters"),
            "Apply AOVs to selected nodes as parameters.",
            self,
            triggered=self.applyToParmsSignal.emit

        )

        self.apply_as_parms_button.setDefaultAction(parms_action)
        self.apply_as_parms_button.setEnabled(False)

        # =====================================================================

        self.addSeparator()

        # =====================================================================

        # Button and action to create a new AOVGroup from chosen items.
        self.new_group_button = QtGui.QToolButton(self)
        self.addWidget(self.new_group_button)

        new_group_action = QtGui.QAction(
            QtGui.QIcon(":ht/rsc/icons/aovs/create_group.png"),
            "Create a new group from chosen AOVs.",
            self,
            triggered=self.newGroupSignal.emit
        )

        self.new_group_button.setDefaultAction(new_group_action)
        self.new_group_button.setEnabled(False)

        # =====================================================================

        self.addSeparator()

        # =====================================================================

        # Button and action to load from a node.
        load_button = QtGui.QToolButton(self)
        self.addWidget(load_button)

        load_action = QtGui.QAction(
            hou.ui.createQtIcon("DATATYPES_node_path"),
            "Load AOVs from a node.",
            self,
            triggered=self.loadFromNode
        )

        load_button.setDefaultAction(load_action)

        # =====================================================================

        spacer = QtGui.QWidget()
        self.addWidget(spacer)

        spacer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        # =====================================================================

        # Button and action to clear all items from the tree.
        self.clear_button = QtGui.QToolButton(self)
        self.addWidget(self.clear_button)

        clear_action = QtGui.QAction(
            hou.ui.createQtIcon("BUTTONS_clear"),
            "Clear all AOVs.",
            self,
            triggered=self.clearAOVsSignal.emit
        )

        self.clear_button.setDefaultAction(clear_action)
        self.clear_button.setEnabled(False)

    # =========================================================================
    # METHODS
    # =========================================================================

    def loadFromNode(self, node=None):
        """Populate the tree with AOVs and AOVGroups assigned to selected
        nodes.

        """
        if node is not None:
            nodes = [node]

        else:
            nodes = utils.findSelectedMantraNodes()

        items = []

        for node in nodes:
            value = ""

            if node.parm("auto_aovs") is not None:
                value = node.evalParm("auto_aovs")

            names = utils.getAOVNamesFromMultiparm(node)

            if names:
                value = "{} {}".format(value, " ".join(names))

            items.extend(manager.MANAGER.getAOVsFromString(value))

        if items:
            self.installSignal.emit(items)


class AOVsToAddWidget(QtGui.QWidget):
    """This class represents the 'AOVs to Apply' widget."""

    updateEnabledSignal = QtCore.Signal()

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, node=None, parent=None):
        super(AOVsToAddWidget, self).__init__(parent)

        self.node = node

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        top_layout = QtGui.QHBoxLayout()
        layout.addLayout(top_layout)

        # =====================================================================

        label = QtGui.QLabel("AOVs to Apply")
        top_layout.addWidget(label)

        bold_font = QtGui.QFont()
        bold_font.setBold(True)

        label.setFont(bold_font)

        # =====================================================================

        top_layout.addStretch(1)

        # =====================================================================

        top_layout.addWidget(HelpButton("aov_manager"))

        # =====================================================================

        # Tree View
        self.tree = AOVsToAddTreeWidget(parent=self)
        layout.addWidget(self.tree)

        # =====================================================================

        # Tool bar
        self.toolbar = AOVsToAddToolBar(parent=self)
        layout.addWidget(self.toolbar)

        # =====================================================================

        self.toolbar.applyAtRenderTimeSignal.connect(self.applyAtRenderTime)
        self.toolbar.applyToParmsSignal.connect(self.applyAsParms)
        self.toolbar.newGroupSignal.connect(self.createGroup)
        self.toolbar.clearAOVsSignal.connect(self.clearAOVs)
        self.toolbar.installSignal.connect(self.installItems)

        self.tree.model().sourceModel().rowsInserted.connect(self.dataUpdatedHandler)
        self.tree.model().sourceModel().rowsRemoved.connect(self.dataUpdatedHandler)
        self.tree.model().sourceModel().modelReset.connect(self.dataClearedHandler)

    # =========================================================================
    # METHODS
    # =========================================================================

    def applyAsParms(self):
        """Apply AOVs and AOVGroups as multiparms."""
        if self.node is not None:
            nodes = [self.node]

        else:
            nodes = utils.findSelectedMantraNodes()

        if not nodes:
            return

        elements = self.tree.getElementsToAdd()

        utils.applyElementsAsParms(elements, nodes)

    def applyAtRenderTime(self):
        """Apply AOVs and AOVGroups at rendertime."""
        if self.node is not None:
            nodes = [self.node]

        else:
            nodes = utils.findSelectedMantraNodes()

        if not nodes:
            return

        elements = self.tree.getElementsToAdd()
        utils.applyElementsAsString(elements, nodes)

    def clearAOVs(self):
        """Clear all AOVs and AOVGroups in the tree."""
        self.tree.clearAll()

    def createGroup(self):
        """Create a new AOVGroup from items in the tree."""
        import ht.ui.aovs.dialogs

        aovs = utils.flattenList(self.tree.getElementsToAdd())

        ht.ui.aovs.dialogs.createNewGroup(aovs)

    def dataClearedHandler(self):
        """Handle the tree being cleared."""
        self.toolbar.apply_button.setEnabled(False)
        self.toolbar.apply_as_parms_button.setEnabled(False)
        self.toolbar.new_group_button.setEnabled(False)
        self.toolbar.clear_button.setEnabled(False)

        self.updateEnabledSignal.emit()

    def dataUpdatedHandler(self, index, start, end):
        """Handle the tree being updated."""
        enable = self.tree.numItemsToAdd() > 0

        self.toolbar.apply_button.setEnabled(enable)
        self.toolbar.apply_as_parms_button.setEnabled(enable)
        self.toolbar.new_group_button.setEnabled(enable)
        self.toolbar.clear_button.setEnabled(enable)

        self.updateEnabledSignal.emit()

    def installItems(self, items):
        """Install items into the tree."""
        self.tree.installItems(items)

    def installListener(self, nodes):
        """Listen for items to be installed."""
        items = []

        for node in nodes:
            if isinstance(node, models.FolderNode):
                items.extend(node.items)

            else:
                items.append(node.item)

        self.installItems(items)

    def uninstallListener(self, nodes):
        """Listen for items to be removed."""
        model = self.tree.model()

        for node in nodes:
            # Look for the index of the node to remove.
            index = self.tree.nodeIndexInModel(node)

            # If the node exists, remove its index from the source model
            if index is not None:
                model.removeIndex(index)

# =============================================================================
# New Group Widgets
# =============================================================================

class NewGroupAOVListWidget(QtGui.QListView):
    """This widget allows editing of group AOV membership."""

    def __init__(self, parent=None):
        super(NewGroupAOVListWidget, self).__init__(parent)

        self.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)

        model = models.AOVGroupEditListModel()

        self.proxy_model = QtGui.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(model)
        self.proxy_model.sort(QtCore.Qt.AscendingOrder)

        self.setModel(self.proxy_model)

        self.setAlternatingRowColors(True)

    def getSelectedAOVs(self):
        """Get a list of selected AOVs."""
        return self.proxy_model.sourceModel().checkedAOVs()

# =============================================================================
# Info Widgets
# =============================================================================

class InfoTableView(QtGui.QTableView):
    """This class represents a generic table view for information."""
    def __init__(self, parent=None):
        super(InfoTableView, self).__init__(parent)

        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.setWordWrap(False)

        h_header = self.horizontalHeader()
        h_header.setVisible(False)
        h_header.setStretchLastSection(True)
        h_header.resizeSection(0, 250)

    def contextMenuEvent(self, event):
        """Handle RMB menu clicks."""
        index = self.indexAt(event.pos())

        if not index.isValid():
            return

        row = index.row()
        column = index.column()

        # Create a menu.
        menu = QtGui.QMenu(self)

        # Create an entry to copy cells.
        copyAction = QtGui.QAction("Copy", self)
        menu.addAction(copyAction)

        copyAction.setShortcut(
            QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_C)
        )

        # Display the menu and get the choice..
        action = menu.exec_(event.globalPos())

        # Copy the cell.
        if action == copyAction:
            self.copyCell(index)

    def copyCell(self, index):
        """Copy the contents of a table cell to the clipboard."""
        result = self.model().data(index)

        if result is not None:
            clipboard = QtGui.QApplication.clipboard()
            clipboard.setText(result)


class AOVInfoTableView(InfoTableView):
    """This class represents the AOV information table."""
    def __init__(self, aov, parent=None):
        super(AOVInfoTableView, self).__init__(parent)

        model = models.AOVInfoTableModel()
        model.initDataFromAOV(aov)
        self.setModel(model)

class AOVGroupInfoTableWidget(InfoTableView):
    """This class represents the AOVGroup information table."""
    def __init__(self, group, parent=None):
        super(AOVGroupInfoTableWidget, self).__init__(parent)

        model = models.AOVGroupInfoTableModel()
        model.initDataFromGroup(group)
        self.setModel(model)

class GroupMemberListWidget(QtGui.QListView):
    """This widget is for displaying AOVGroup membership."""
    def __init__(self, group, parent=None):
        super(GroupMemberListWidget, self).__init__(parent)

        model = models.AOVGroupMemberListModel()

        self.proxy_model = QtGui.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(model)
        self.proxy_model.sort(QtCore.Qt.AscendingOrder)

        self.setModel(self.proxy_model)

        self.setAlternatingRowColors(True)

        model.initDataFromGroup(group)

# =============================================================================
# Generic Widgets
# =============================================================================

class CustomSpinBox(QtGui.QSpinBox):
    """A QSpinBox with a custom stylesheet."""

    def __init__(self, parent=None):
        super(CustomSpinBox, self).__init__(parent)

        self.setStyleSheet(uidata.CUSTOMSPINBOX_STYLE)


class FileChooser(QtGui.QWidget):
    """This class represents a file choosing widget."""

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, parent=None):
        super(FileChooser, self).__init__(parent)

        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)

        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # =====================================================================

        self.field = QtGui.QLineEdit()
        layout.addWidget(self.field)

        # =====================================================================

        self.button = QtGui.QPushButton(
            hou.ui.createQtIcon("BUTTONS_chooser_file"),
            ""
        )
        layout.addWidget(self.button)

        self.button.setFlat(True)
        self.button.setIconSize(QtCore.QSize(16, 16))
        self.button.setMaximumSize(QtCore.QSize(24, 24))

        self.button.clicked.connect(self.chooseFile)

    # =========================================================================
    # METHODS
    # =========================================================================

    def chooseFile(self):
        """Open the file chooser dialog."""
        current = self.getPath()

        start_directory = None
        default_value = None

        if current:
            start_directory = os.path.dirname(current)
            default_value = os.path.basename(current)

        path = hou.ui.selectFile(
            start_directory=start_directory,
            pattern="*.json",
            default_value=default_value,
            chooser_mode=hou.fileChooserMode.Write
        )

        if not path:
            return

        ext = os.path.splitext(path)[1]

        if not ext:
            path = "{0}.json".format(path)

        self.setPath(path)

    def enable(self, enable):
        """Set the UI element's enabled state."""
        self.field.setEnabled(enable)
        self.button.setEnabled(enable)

    def getPath(self):
        """Get the text."""
        return self.field.text()

    def setPath(self, path):
        """Set the path."""
        self.field.setText(path)


class FilterWidget(QtGui.QWidget):
    """This class represents a Filter widget."""

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, parent=None):
        super(FilterWidget, self).__init__(parent)

        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)

        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QtGui.QLabel("Filter"))

        self.field = QtGui.QLineEdit()
        layout.addWidget(self.field)

        self.field.setToolTip("Filter the list of AOVs by name.")


class HelpButton(QtGui.QPushButton):
    """Generic Help button."""

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, name, parent=None):
        super(HelpButton, self).__init__(
            hou.ui.createQtIcon("BUTTONS_help"),
            "",
            parent=parent
        )

        self._name = name

        self.setToolTip("Show Help.")
        self.setIconSize(QtCore.QSize(14, 14))
        self.setMaximumSize(QtCore.QSize(14, 14))
        self.setFlat(True)

        self.clicked.connect(self.displayHelp)

    # =========================================================================
    # METHODS
    # =========================================================================

    def displayHelp(self):
        """Display help page."""
        # Help browser pane.
        browser = None

        # Look for an existing, float help browser.
        for pane_tab in hou.ui.paneTabs():
            if isinstance(pane_tab, hou.HelpBrowser):
                if pane_tab.isFloating():
                    browser = pane_tab
                    break

        # Didn't find one, so create a new floating browser.
        else:
            desktop = hou.ui.curDesktop()
            browser = desktop.createFloatingPaneTab(hou.paneTabType.HelpBrowser)

        browser.displayHelpPath(os.path.join("aov_manager", self._name))


class MenuFieldMode(object):
    """Mode settings for MenuFields."""

    Replace = 0
    Toggle = 1


class MenuField(QtGui.QWidget):
    """This class represents a crappy attempt at a Replace/Toggle style
    string menu.

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, menu_items, mode=MenuFieldMode.Replace, parent=None):
        super(MenuField, self).__init__(parent)

        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)

        layout.setSpacing(1)
        layout.setContentsMargins(0, 0, 0, 0)

        # =====================================================================

        self.field = QtGui.QLineEdit()
        layout.addWidget(self.field)

        # =====================================================================

        button = QtGui.QPushButton()
        layout.addWidget(button)

        menu = QtGui.QMenu(button)

        for item in menu_items:
            label, value = item

            action = menu.addAction(label)

            if mode == MenuFieldMode.Replace:
                action.triggered.connect(
                    lambda value=value: self.set(value)
                )

            elif mode == MenuFieldMode.Toggle:
                action.triggered.connect(
                    lambda value=value: self.toggle(value)
                )

        button.setMenu(menu)

        button.setStyleSheet(uidata.MENUFIELD_STYLE)

    # =========================================================================
    # METHODS
    # =========================================================================

    def set(self, value):
        """Set the field to a value."""
        self.field.setText(value)

    def toggle(self, value):
        """Toggle a value in the field."""
        text = self.value()

        if value in text:
            text = text.replace(value, "")

            self.set(text.strip())

        else:
            if not text:
                text = value

            else:
                text = "{0} {1}".format(text, value)

            self.set(text)

    def value(self):
        """The field value."""
        return self.field.text()


class StatusMessageWidget(QtGui.QWidget):
    """This class represents an status notification widget."""

    Error = 0
    Warning = 1
    Info = 2

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, parent=None):
        super(StatusMessageWidget, self).__init__(parent)

        self._error_mappings = {}
        self._warning_mappings = {}
        self._info_mappings = {}

        self.setContentsMargins(0, 0, 0, 0)

        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)

        layout.setContentsMargins(0, 0, 0, 0)

        self.info_pixmap = hou.ui.createQtIcon("DIALOG_info").pixmap(24, 24)
        self.warning_pixmap = hou.ui.createQtIcon("DIALOG_warning").pixmap(24, 24)
        self.error_pixmap = hou.ui.createQtIcon("DIALOG_error").pixmap(24, 24)

        # =====================================================================

        self.icon = QtGui.QLabel()
        layout.addWidget(self.icon)

        self.icon.setFixedSize(24, 24)
        self.icon.setPixmap(self.info_pixmap)
        self.icon.hide()

        # =====================================================================

        self.display = QtGui.QLabel()
        layout.addWidget(self.display)

        self.setFixedHeight(24)

    # =========================================================================
    # METHODS
    # =========================================================================

    def addError(self, level, msg):
        """Add an error message at a specific level."""
        self._error_mappings[level] = msg
        self.updateDisplay()

    def addInfo(self, level, msg):
        """Add a display message at a specific level."""
        self._info_mappings[level] = msg
        self.updateDisplay()

    def addWarning(self, level, msg):
        """Add a warning message at a specific level."""
        self._warning_mappings[level] = msg
        self.updateDisplay()

    def clear(self, level):
        """Clear all notifications for a level."""
        self.clearError(level)
        self.clearWarning(level)
        self.clearInfo(level)

    def clearError(self, level):
        """Clear any error messages at a specific level."""
        if level in self._error_mappings:
            del self._error_mappings[level]

        self.updateDisplay()

    def clearInfo(self, level):
        """Clear any info messages at a specific level."""
        if level in self._info_mappings:
            del self._info_mappings[level]

        self.updateDisplay()

    def clearWarning(self, level):
        """Clear any warning messages at a specific level."""
        if level in self._warning_mappings:
            del self._warning_mappings[level]

        self.updateDisplay()

    def getMessage(self):
        """Get the current error/warning/info value, if any."""
        if self._error_mappings:
            highest = sorted(self._error_mappings.keys())[0]

            self.icon.setPixmap(self.error_pixmap)
            return self._error_mappings[highest]

        elif self._warning_mappings:
            highest = sorted(self._warning_mappings.keys())[0]

            self.icon.setPixmap(self.warning_pixmap)
            return self._warning_mappings[highest]

        elif self._info_mappings:
            highest = sorted(self._info_mappings.keys())[0]

            self.icon.setPixmap(self.info_pixmap)
            return self._info_mappings[highest]

        return ""

    def updateDisplay(self):
        """Update the display items."""
        error = self.getMessage()

        # Ensure everything is shown and the message is correct.
        if error:
            self.display.setText(error)
            self.display.show()
            self.icon.show()

        # Clear existing messages and hide the elements.
        else:
            self.display.clear()
            self.display.hide()
            self.icon.hide()


class AOVManagerDialog(QtGui.QDialog):
    """Dialog to display a floating AOV Manager."""

    def __init__(self, node=None, parent=None):
        super(AOVManagerDialog, self).__init__(parent)

        self.node = node

        title = "AOV Manager"

        if self.node is not None:
            title = "{} - {}".format(title, self.node.path())

        self.setWindowTitle(title)

        self.manager_widget = AOVManagerWidget(node=node)

        layout = QtGui.QVBoxLayout()

        layout.addWidget(self.manager_widget)

        self.setLayout(layout)

        self.button_box = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Close
        )
        layout.addWidget(self.button_box)

        self.button_box.rejected.connect(self.close)

        if self.node is not None:
            self.manager_widget.to_add_widget.toolbar.loadFromNode(self.node)

        self.resize(900, 800)

        self.show()

# =============================================================================
# FUNCTIONS
# =============================================================================

def openAOVEditor(node):
    """Open the AOV Manager dialog based on a node."""
    AOVManagerDialog(node=node, parent=hou.ui.mainQtWindow())

