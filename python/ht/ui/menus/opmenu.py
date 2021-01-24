"""This module contains functions supporting custom OPmenu.xml entries."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.ui.paste import copy_item


# =============================================================================
# FUNCTIONS
# =============================================================================


def create_absolute_reference_copy(scriptargs: dict):
    """Create an absolute reference copy of a node.

    :param scriptargs: kwargs dict from OPmenu entry.
    :return:

    """
    node = scriptargs["node"]

    node.parent().copyItems(
        [node], channel_reference_originals=True, relative_references=False
    )


def save_item_to_file(scriptargs: dict):
    """Save the item to a file.

    :param scriptargs: kwargs dict from OPmenu entry.
    :return:

    """
    copy_item(scriptargs["node"])
