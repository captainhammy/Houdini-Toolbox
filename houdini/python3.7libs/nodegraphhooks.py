"""Custom network editor event handlers."""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Standard Library Imports
from __future__ import annotations
from typing import List, Tuple

# Houdini Toolbox Imports
from ht.ui import nodegraph, paste

# Houdini Imports
from canvaseventtypes import KeyboardEvent
import nodegraphdisplay


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
        # Check if this is supposed to be a normal Houdini paste event (h.paste)
        if nodegraph.is_houdini_paste_event(uievent):
            return nodegraph.handle_houdini_paste_event(uievent)

        editor = uievent.editor
        eventtype = uievent.eventtype
        key = uievent.key

        if nodegraphdisplay.setKeyPrompt(editor, key, "h.tool:copy_items", eventtype):
            return paste.copy_items_from_graph(editor)

        if nodegraphdisplay.setKeyPrompt(editor, key, "h.tool:paste_items", eventtype):
            return paste.paste_items_to_graph(eventtype, editor, uievent)

    return None, False
