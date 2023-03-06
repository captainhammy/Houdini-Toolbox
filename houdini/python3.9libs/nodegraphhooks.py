"""Custom network editor event handlers."""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Future
from __future__ import annotations

# Standard Library
from typing import List, Tuple

# Houdini Toolbox
from houdini_toolbox.ui import nodegraph, paste

# Houdini
import nodegraphdisplay
from canvaseventtypes import KeyboardEvent

# ==============================================================================
# GLOBALS
# ==============================================================================

KEY_HIT_TYPES = ("keyhit", "menukeyhit", "parentkeyhit")


# ==============================================================================
# FUNCTIONS
# ==============================================================================


def createEventHandler(  # pylint: disable=invalid-name,unused-argument
    uievent: KeyboardEvent, pending_actions: List
) -> Tuple[None, bool]:
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
