"""Custom network editor event handlers."""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Houdini Toolbox Imports
from ht.ui import paste

# Houdini Imports
from canvaseventtypes import KeyboardEvent
from nodegraphdisplay import setKeyPrompt


# ==============================================================================
# GLOBALS
# ==============================================================================

KEY_HIT_TYPES = ("keyhit", "menukeyhit", "parentkeyhit")


# ==============================================================================
# FUNCTIONS
# ==============================================================================


def createEventHandler(
    uievent, pending_actions
):  # pylint: disable=invalid-name,unused-argument
    """Create an event handler for Houdini's network editor.

    :param uievent: The occurring event.
    :type uievent: canvaseventtypes.KeyboardEvent
    :param pending_actions: Pending actions.
    :type pending_actions: list
    :return: Handler event information.
    :rtype: tuple

    """

    if isinstance(uievent, KeyboardEvent) and uievent.eventtype in KEY_HIT_TYPES:
        editor = uievent.editor
        eventtype = uievent.eventtype
        key = uievent.key

        if setKeyPrompt(editor, key, "h.tool:copy_items", eventtype):
            return paste.copy_items_from_graph(editor)

        elif setKeyPrompt(editor, key, "h.tool:paste_items", eventtype):
            return paste.paste_items_to_graph(eventtype, editor, uievent)

    return None, False
