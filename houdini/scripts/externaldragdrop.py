"""Perform tasks when external files are dropped onto the Houdini window."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import os
from typing import List

# Houdini Toolbox
from ht.events import SceneEvents, run_event

# =============================================================================
# FUNCTIONS
# =============================================================================


def dropAccept(file_paths: List[str]) -> bool:  # pylint: disable=invalid-name
    """Accept a list of files.

    This function is called by Houdini when files are dropped onto the UI.

    :param file_paths: A list of dropped files.
    :return: Whether or not the drop was handled.

    """
    # Let Houdini handle dropping .hip files.
    if any(
        file_path
        for file_path in file_paths
        if os.path.splitext(file_path)[1] == ".hip"
    ):
        return False

    scriptargs = {"file_paths": file_paths}

    run_event(SceneEvents.ExternalDragDrop, scriptargs)

    # Return whether or not the drop was accepted by the handler.
    return scriptargs.get("drop_accepted", False)
