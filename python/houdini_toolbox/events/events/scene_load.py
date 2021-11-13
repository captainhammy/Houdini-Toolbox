"""This module contains an event to perform actions on scene load."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini
import hou

# =============================================================================
# FUNCTIONS
# =============================================================================


def clear_session_settings(scriptargs: dict):  # pylint: disable=unused-argument
    """Clear out potentially annoying/bad settings.

    :param scriptargs: Event data.
    :return:

    """
    # Remove an icon cache directory variable if it exists.
    hou.hscript("set -u HOUDINI_ICON_CACHE_DIR")
