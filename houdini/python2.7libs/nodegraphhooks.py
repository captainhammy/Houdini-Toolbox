"""Custom network editor event handlers"""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Houdini Toolbox Imports
from ht.ui.paste import dialogs

# Houdini Imports
from canvaseventtypes import KeyboardEvent
import hou
from nodegraphdisplay import setKeyPrompt

# ==============================================================================
# FUNCTIONS
# ==============================================================================

def createEventHandler(uievent, pending_actions):
    """Create an event handler for Houdini's network editor."""

    if isinstance(uievent, KeyboardEvent) and uievent.eventtype in ('keyhit', 'menukeyhit', 'parentkeyhit'):
        editor = uievent.editor
        eventtype = uievent.eventtype
        key = uievent.key

        if setKeyPrompt(editor, key, "h.tool:copy_items", eventtype):
            parent = editor.pwd()

            items = parent.selectedItems(True, True)

            # If there are no items selected then display an error and abort.
            if not items:
                hou.ui.displayMessage(
                    "Could not copy selected items",
                    help="Nothing was selected",
                    severity=hou.severityType.Error,
                )

                return None, True

            dialog = dialogs.CopyItemsDialog(items, parent, parent=hou.qt.mainWindow())
            dialog.exec_()

            # This is a one off event so we don't care what happens after this.
            return None, True

        elif setKeyPrompt(editor, key, "h.tool:paste_items", eventtype):
            if eventtype == "keyhit":
                mousepos = uievent.mousepos

            elif eventtype == "menukeyhit":
                mousepos = editor.screenBounds().center()

            else:
                mousepos = None

            if mousepos is not None:
                pos = editor.posFromScreen(mousepos)

            else:
                pos = None

            dialog = dialogs.PasteItemsDialog(editor, pos, mousepos, parent=hou.qt.mainWindow())
            dialog.exec_()

            # This is a one off event so we don't care what happens after this.
            return None, True

    return None, False
