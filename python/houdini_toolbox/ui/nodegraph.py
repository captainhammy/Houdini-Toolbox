"""Code related to the node graph."""

# ==============================================================================
# IMPORTS
# ==============================================================================

# Future
from __future__ import annotations

# Standard Library
from typing import Tuple

# Houdini Toolbox
from houdini_toolbox.events.manager import EVENT_MANAGER
from houdini_toolbox.events.types import KeyboardEvents

# Houdini
import hou
import nodegraphutils  # type: ignore
from canvaseventtypes import KeyboardEvent  # type: ignore
from nodegraphdisplay import setKeyPrompt  # type: ignore

# ==============================================================================
# FUNCTIONS
# ==============================================================================


def handle_houdini_paste_event(uievent: KeyboardEvent) -> Tuple[None, bool]:
    """Handle item pasting and post-event running.

    :param uievent: The occurring keyboard event.
    :return: Returns indicating that the event was handled successfully.

    """
    editor = uievent.editor
    eventtype = uievent.eventtype

    # Group everything under an undo block so all associated actions
    # can be undone at once.
    with hou.undos.group("Paste from clipboard"):
        # Paste the items to the editor.
        nodegraphutils.pasteItems(editor)

        if eventtype != "parentkeyhit":
            # If the paste was invoked from the menu we'll paste the items in
            # the center.
            if eventtype == "menukeyhit":
                mousepos = editor.screenBounds().center()

            # Otherwise use the mouse position.
            else:
                mousepos = uievent.mousepos

            pos = editor.posFromScreen(mousepos)

            # Move the items to the correct place.
            nodegraphutils.moveItemsToLocation(editor, pos, mousepos)

        nodegraphutils.updateCurrentItem(editor)

        scriptargs = {"items": editor.pwd().selectedItems(), "uievent": uievent}

        # Run any post-paste events.
        EVENT_MANAGER.run_event(KeyboardEvents.PostPasteEvent, scriptargs)

    return None, True


def is_houdini_paste_event(uievent: KeyboardEvent) -> bool:
    """Check whether the event is an item paste event.

    :param uievent: The occurring keyboard event.
    :return: Whether the event is a paste event (h.paste).

    """
    return setKeyPrompt(uievent.editor, uievent.key, "h.paste", uievent.eventtype)
