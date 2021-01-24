"""This module contains functions supporting custom PARMmenu.xml entries."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Imports
import hou


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _valid_to_convert_to_absolute_reference(parm: hou.Parm) -> bool:
    """Check if a parameter is valid to convert to an absolute reference.

    A parameter is valid if it is a node reference string parameter with a raw
    value appears to be a relative path and points to a valid node.

    :param parm: There parameter to check.
    :return: Whether or not the parm can be converted.

    """
    parm_template = parm.parmTemplate()

    # Check if the parameter is a string parameter.
    if isinstance(parm_template, hou.StringParmTemplate):
        # Check if the string parameter is a node reference.
        if parm_template.stringType() == hou.stringParmType.NodeReference:
            # Need to test values to decide whether to show up or not.
            path = parm.eval()

            # Ignore empty strings.
            if not path:
                return False

            # Ignore paths which already seem to be absolute.
            if not path.startswith(".."):
                return False

            # Can't convert parameters with keyframes/expressions.
            if parm.keyframes():
                return False

            # If the path is the same as the raw path then we can say that we
            # can show the menu item.  If the path is not the same as the
            # unexpanded we won't say yes because it would be some sort of an
            # expression which we don't want to mess with.
            if path == parm.unexpandedString():
                if parm.evalAsNode() is not None:
                    return True

    return False


def _valid_to_convert_to_relative_reference(parm: hou.Parm) -> bool:
    """Check if a parameter is valid to convert to a relative reference.

    A parameter is valid if it is a node reference string parameter with a raw
    value appears to be an absolute path and points to a valid node.

    :param parm: There parameter to check.
    :return: Whether or not the parm can be converted.

    """
    parm_template = parm.parmTemplate()

    # Check if the parameter is a string parameter.
    if isinstance(parm_template, hou.StringParmTemplate):
        # Check if the string parameter is a node reference.
        if parm_template.stringType() == hou.stringParmType.NodeReference:
            # Need to test values to decide whether to show up or not.
            path = parm.eval()

            # Ignore empty strings.
            if not path:
                return False

            # Ignore paths which already seem to be relative.
            if not path.startswith("/"):
                return False

            # Can't convert parameters with keyframes/expressions.
            if parm.keyframes():
                return False

            # If the path is the same as the raw path then we can say that we
            # can show the menu item.  If the path is not the same as the
            # unexpanded we won't say yes because it would be some sort of an
            # expression which we don't want to mess with.
            if path == parm.unexpandedString():
                if parm.evalAsNode() is not None:
                    return True

    return False


# =============================================================================
# FUNCTIONS
# =============================================================================


def convert_absolute_to_relative_path_context(scriptargs: dict) -> bool:
    """Context script for converting any absolute node paths to relative paths.

    The menu entry will be shown if there are node reference string parameters
    whose values are absolute paths.

    :param scriptargs: kwargs dict from PARMmenu entry.
    :return: Whether or not to show the menu entry.

    """
    parms = scriptargs["parms"]

    return any([_valid_to_convert_to_relative_reference(parm) for parm in parms])


def convert_absolute_to_relative_path(scriptargs: dict):
    """Convert any absolute node paths to relative paths.

    :param scriptargs: kwargs dict from PARMmenu entry.
    :return:

    """
    parms = scriptargs["parms"]

    for parm in parms:
        if _valid_to_convert_to_relative_reference(parm):
            target_node = parm.evalAsNode()

            parm.set(parm.node().relativePathTo(target_node))


def convert_relative_to_absolute_path_context(scriptargs: dict) -> bool:
    """Context script for converting any relative node paths to absolute paths.

    The menu entry will be shown if there are node reference string parameters
    whose values are relative paths.

    :param scriptargs: kwargs dict from PARMmenu entry.
    :return: Whether or not to show the menu entry.

    """
    parms = scriptargs["parms"]

    return any([_valid_to_convert_to_absolute_reference(parm) for parm in parms])


def convert_relative_to_absolute_path(scriptargs: dict):
    """Convert any absolute node paths to absolute paths.

      :param scriptargs: kwargs dict from PARMmenu entry.
      :return:

      """
    parms = scriptargs["parms"]

    for parm in parms:
        if _valid_to_convert_to_absolute_reference(parm):
            target_node = parm.evalAsNode()

            parm.set(target_node.path())


def promote_parameter_to_node(scriptargs: dict):  # pylint: disable=too-many-locals
    """Promote a parameter to a target node.

    :param scriptargs: kwargs dict from PARMmenu entry.
    :return:

    """
    # Get the parms to act on.
    parms = scriptargs["parms"]

    # The start node for the node chooser prompt
    start_node = None

    parm_tuple = None
    parm_tuple_map = {}
    parm_tuple_nodes = []

    # Process all the selected parms, partitioning by parm tuple.
    for parm in parms:
        parm_tuple = parm.tuple()

        # Get or create a list of parms for this tuple.
        parms_for_tuple = parm_tuple_map.setdefault(parm_tuple, [])

        parms_for_tuple.append(parm)

        node = parm_tuple.node()
        parm_tuple_nodes.append(node)

        # Update the start node to be the parent of this tuple's node.
        start_node = node.parent()

    # The number of parms in the tuple.
    num_components = len(parm_tuple)

    # Determine how many components of the tuple we will set.
    num_components_to_set = max([len(value) for value in list(parm_tuple_map.values())])

    # Prompt for a target node.  Start at the parent (the most logical choice?)
    result = hou.ui.selectNode(initial_node=start_node)

    # Try to find ths selected node.
    target_node = hou.node(result)

    if target_node is not None:
        # Can't promote to a selected node.
        if target_node in parm_tuple_nodes:
            raise hou.OperationFailed("Cannot promote to a source node.")

        # Should the target parm will be set to the source value?
        set_value = True

        # The target node already has a parm tuple with the desired name so we
        # should prompt to use it.
        if target_node.parmTuple(parm_tuple.name()) is not None:
            choice = hou.ui.displayMessage(
                "Parameter already exists on {}.  Link to existing parameter?".format(
                    target_node.path()
                ),
                buttons=(
                    "Yes and keep current value",
                    "Yes and update value",
                    "Cancel",
                ),
                severity=hou.severityType.ImportantMessage,
            )

            # Use parm but keep value, so don't set.
            if choice == 0:
                set_value = False

            # Use parm and update value.
            elif choice == 1:
                set_value = True

            # Bail out since we're cancelling.
            else:
                return

        # No existing parameter so we'll have to create one.
        else:
            # Get the target node's parm interface.
            target_ptg = target_node.parmTemplateGroup()

            # The parameter definition for the parm we are trying to link.
            parm_template = parm_tuple.parmTemplate()

            # If we are trying to link a single parm inside a tuple then modify
            # the parm definition to represent that single parm.
            if num_components_to_set != num_components:
                parm_template.setNumComponents(1)

                # Since we're just setting a single component the parms should all
                # have the same name so just grab the first.
                parm_template.setName(parms[0].name())

            # Add the parameter definition to the parm list.
            target_ptg.addParmTemplate(parm_template)

            # Update the interface with the new definition.
            target_node.setParmTemplateGroup(target_ptg)

        # Process each parm to set.
        for parm in parms:
            # Get the target parm.
            target_parm = target_node.parm(parm.name())

            # Set the target parm to the current value if required.
            if set_value:
                target_parm.set(parm.eval())

            # Create the channel reference.
            parm.set(target_parm)
