"""Custom network editor event handlers."""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Standard Library Imports
from typing import List, Tuple

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
    uievent: KeyboardEvent, pending_actions: List
) -> Tuple[None, bool]:  # pylint: disable=invalid-name,unused-argument
    """Create an event handler for Houdini's network editor.

    :param uievent: The occurring event.
    :param pending_actions: Pending actions.
    :return: Handler event information.

    """

    if isinstance(uievent, KeyboardEvent) and uievent.eventtype in KEY_HIT_TYPES:
        editor = uievent.editor
        eventtype = uievent.eventtype
        key = uievent.key

        if setKeyPrompt(editor, key, "h.tool:copy_items", eventtype):
            return paste.copy_items_from_graph(editor)

        if setKeyPrompt(editor, key, "h.tool:paste_items", eventtype):
            return paste.paste_items_to_graph(eventtype, editor, uievent)

    return None, False
