"""Utilities for parameters."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import re
from typing import Callable, Tuple

# Houdini
import hou

# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _find_parameters_with_value(
    target_value: str, check_func: Callable
) -> Tuple[hou.Parm, ...]:
    """Find parameters which contain the target value.

    :param target_value: The string value to search for.
    :return: A tuple of parameters which contain the value.

    """
    # Use 'opfind' hscript command to find all the nodes which have parameters
    # containing our value.
    paths = hou.hscript("opfind '{}'".format(target_value))[0].split()

    parms_with_value = []

    for path in paths:
        node = hou.node(path)

        for parm in node.parms():
            value = None

            # Check string parameters via unexpandedString()
            try:
                value = parm.unexpandedString()

            # Fails on non-string parameters.
            except hou.OperationFailed:
                # In that case, check for any expressions.
                try:
                    value = parm.expression()

                except hou.OperationFailed:
                    pass

            # If we got a value and the checking function detects a match then
            # we'll return that parameter
            if value and check_func(value, target_value):
                parms_with_value.append(parm)

    return tuple(parms_with_value)


# =============================================================================
# FUNCTIONS
# =============================================================================


def find_parameters_using_variable(variable: str) -> Tuple[hou.Parm, ...]:
    """Find parameters which contain a variable.

    This only works for string parameters

    The variable name can be supplied with or without a $.

    This will match only the exact usage.  For example, if you
    search for $HIP the result would not include any parameters
    using $HIPNAME or $HIPFILE.

    :param variable: The variable name to search for.
    :return: A tuple of parameters which contain the variable.

    """
    search_variable = variable

    # If the variable doesn't start with $ we need to add it.
    if not variable.startswith("$"):
        search_variable = "$" + search_variable

    def _checker(value, target_variable):
        # We need to escape the $ since it's a special regex character.
        var = "\\" + target_variable

        # Regex to match the variable string but ensuring that it matches exactly.
        # For example of you are looking for $HIP you want to ensure you don't also
        # match $HIPNAME or $HIPFILE
        return bool(re.search("(?=.*{}(?![a-zA-Z]))".format(var), value))

    return _find_parameters_with_value(search_variable, _checker)


def find_parameters_with_value(target_value: str) -> Tuple[hou.Parm, ...]:
    """Find parameters which contain the target value.

    This only works for string parameters.

    :param target_value: The value to search for.
    :return: A tuple of parameters which contain the value.

    """

    def _checker(value, target):
        # Simply check that the target value is in the value.
        return target in value

    return _find_parameters_with_value(target_value, _checker)
