"""Custom network editor event handlers"""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Houdini Toolbox Imports
from ht.ui import paste

# Houdini Imports
from canvaseventtypes import KeyboardEvent
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
            return paste.copy_items_from_graph(editor)

        elif setKeyPrompt(editor, key, "h.tool:paste_items", eventtype):
            return paste.paste_items_to_graph(eventtype, editor, uievent)

    return None, False
