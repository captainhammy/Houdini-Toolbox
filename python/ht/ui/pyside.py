
"""This module contains classes and methods supporting PySide dialogs in
Houdini.

Synopsis
--------

Classes:
    IntegratedEventLoop
        This class is used to run PySide dialogs in Houdini's event loop.

Functions:
    anyQtWindowsAreOpen()
        Detect if there are any PySide windows open.

    findOrCreateEventLoop()
        Find or create an IntegratedEventLoop in hou.session.

"""
__author__ = "Graham Thompson"
__email__ = "captainhammy@gmail.com"

# =============================================================================
# IMPORTS
# =============================================================================

from PySide import QtCore, QtGui

# Houdini Imports
import hou

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "IntegratedEventLoop",
    "anyQtWindowsAreOpen",
    "findOrCreateEventLoop",
]

# =============================================================================
# CLASSES
# =============================================================================

class IntegratedEventLoop(object):
    """This class is used to run PySide dialogs in Houdini's event loop.

    This class is based on the example in Houdini's HOM Cookbook.

    """

    def __init__(self, application, dialog):
        """Initialize an IntegratedEventLoop object.

        Args:
            application : (QtGui.QApplication)
                The PySide application.

            dialog : (QtGui.QWidget)
                The widget to display.

        Raises:
            N/A

        Returns
            N/A

        """
        # The PySide application.
        self._application = application

        # The dialog to display.
        self._dialog = dialog

        # Stash a new version of the PySide event loop.
        self._eventLoop = QtCore.QEventLoop()

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __repr__(self):
        return "<IntegratedEventLoop>"

    # =========================================================================
    # INSTANCE PROPERTIES
    # =========================================================================

    @property
    def application(self):
        """(QtGui.QApplication) The PySide application."""
        return self._application

    @property
    def dialog(self):
        """(QtGui.QWidget) A PySide widget."""
        return self._dialog

    @dialog.setter
    def dialog(self, dialog):
        self._dialog = dialog

    @property
    def eventLoop(self):
        """(QtCore.QEventLoop) The PySide event loop."""
        return self._eventLoop

    # =========================================================================
    # METHODS
    # =========================================================================

    def exec_(self):
        """Add the process events function to Houdini's event loop.

        Raises:
            N/A

        Returns:
            None

        """
        hou.ui.addEventLoopCallback(self.processEvents)

    def processEvents(self):
        """This function runs the QEventLoop.

        Raises:
            N/A

        Returns:
            None

        """
        # If there aren't any Qt windows open we need to remove ourself
        # from the event loop callback list.
        if not anyQtWindowsAreOpen():
            hou.ui.removeEventLoopCallback(self.processEvents)

        self.eventLoop.processEvents()
        self.application.sendPostedEvents(self.dialog, 0)

# =============================================================================
# FUNCTIONS
# =============================================================================

def anyQtWindowsAreOpen():
    """Detect if there are any PySide windows open.

    Raises:
        N/A

    Returns:
        bool
            Returns True if there are any Qt widgets visible, otherwise False.

    """
    return any(w.isVisible() for w in QtGui.QApplication.topLevelWidgets())


def findOrCreateEventLoop(loopName, dialog=None):
    """Find or create an IntegratedEventLoop in hou.session.

    Args:
        loopName : (str)
            The name of the loop to find or create.

        dialog=None : (QtGui.QWidget)
            A dialog to display in the loop.

    Raises:
        N/A

    Returns:
        IntegratedEventLoop
            The found or newly created loop.

    """
    # Check if a loop by that name already exists.  If not, create one.
    if not hasattr(hou.session, loopName):
        # Try to find an existing QApplication.
        app = QtGui.QApplication.instance()

        # If no application exists, create one.
        if app is None:
            app = QtGui.QApplication(["houdini"])

        # Create a new loop with the application and dialog.
        loop = IntegratedEventLoop(app, dialog)

        # Store the loop in hou.session.
        setattr(hou.session, loopName, loop)

    # The loop already exists so just use it.
    else:
        loop = getattr(hou.session, loopName)

    return loop

