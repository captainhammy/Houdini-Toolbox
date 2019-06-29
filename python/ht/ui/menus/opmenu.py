"""This module contains functions supporting custom OPmenu.xml entries."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.ui.paste import copy_item


# =============================================================================
# FUNCTIONS
# =============================================================================

def create_absolute_reference_copy(scriptargs):
    """Create an absolute reference copy of a node.

    :param scriptargs: kwargs dict from OPmenu entry.
    :type scriptargs: dict
    :return:

    """
    node = scriptargs['node']

    node.parent().copyItems([node], channel_reference_originals=True, relative_references=False)


def save_item_to_file(scriptargs):
    """Save the item to a file.

    :param scriptargs: kwargs dict from OPmenu entry.
    :type scriptargs: dict
    :return:

    """
    copy_item(scriptargs['node'])

