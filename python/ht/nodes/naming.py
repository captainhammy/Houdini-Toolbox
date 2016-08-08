"""This module contains functions to handle node naming."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import re

# Houdini Imports
import hou

# =============================================================================
# GLOBALS
# =============================================================================

DEFAULT_FMT = "{namespace}_{name}_v{iversion}_{opdigits}"

# =============================================================================
# FUNCTIONS
# =============================================================================

def isNamespacedType(node_type, require_version=True, require_namespace=True):
    """Determine if a node type is namespaced based on name components."""
    components = node_type.nameComponents()

    if require_version:
        if not components[-1]:
            return False

    if require_namespace:
        if not components[1]:
            return False

    return components[1] != "" or components[-1] != ""


def setNamespacedFormattedName(node, fmt=None):
    """Set a formatted name based on namespace information.

    Format string is based on Python's str.format() functionality.

    Allowable formatting values:
        scope: scope network type
        namespace: node type namespace
        base_namespace: namespace with any preceeding 'com.' removed
        name: node type name
        version: node type version
        iversion: integer version
        opdigits: last set of digits of a nodes name (hou.Node.digitsInName)


    Example:
        com.houdinitoolbox::foo::2.0

        fmt="{namespace}_{name}_v{iversion}_{opdigits}"

        foo1 -> com.houdinitoolbox_foo_v2_1

    """
    # Use default formatting string if none was passed.
    if fmt is None:
        fmt = DEFAULT_FMT

    node_type = node.type()

    scope, namespace, type_name, version = node_type.nameComponents()

    data = {
        "scope": scope,
        "namespace": namespace,
        "base_namespace": re.sub("(com\.)(.+)$", "\\2", namespace),
        "name": type_name,
        "version": version,
        "opdigits": node.digitsInName(),
    }

    # Handle possibility of no version value and int cast.
    try:
        data["iversion"] = int(float(version))
    except ValueError:
        data["iversion"] = ""

    name = fmt.format(**data)

    node.setName(name, unique_name=True)

