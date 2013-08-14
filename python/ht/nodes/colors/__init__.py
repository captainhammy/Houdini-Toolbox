"""This module contains a class and functions for managing and applying node
colors in Houdini.

Synopsis
--------

Classes:
    ColorManager
        Manage and apply Houdini node colors.

Functions:
    colorNode()
        Color the node given its properties.

    colorNodeByName()
        Color the node given its name.

    createSessionColorManager()
        Create a session ColorManager object.

"""
__author__ = "Graham Thompson"
__email__ = "captainhammy@gmail.com"

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
import ht.nodes.colors.parser

# Houdini Imports
import hou

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ColorManager",
    "colorNode",
    "colorNodeByName",
    "createSessionColorManager",
]

# =============================================================================
# CLASSES
# =============================================================================

class ColorManager(object):
    """Manage and apply Houdini node colors.

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self):
        """Initialize a ColorManager object.

        Raises:
            N/A

        Returns:
            N/A

        """
	self._constants = {}
	self._names = {}
	self._nodes = {}
	self._tools = {}

        # Build mappings for this object.
        ht.nodes.colors.parser.buildMappings(self)

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __repr__(self):
        return "<ColorManager>"

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    # -------------------------------------------------------------------------
    #    Name: _getManagerGeneratorColor
    #    Args: nodeType : (hou.NodeType)
    #              The node type to get a node type flag match for.
    #  Raises: N/A
    # Returns: hou.Color|None
    #              Returns the matching color, if any, otherwise None.
    #    Desc: Look for a color match based on the node type being a manager
    #          or generator type.
    # -------------------------------------------------------------------------
    def _getManagerGeneratorColor(self, nodeType):
        # Try to get a color match for the exact node type and category.
        color = self._getManagerGeneratorEntry(nodeType)

        # Look for an entry in the generic category.
        if color is None:
            color = self._getManagerGeneratorEntry(nodeType, "all")

        return color

    # -------------------------------------------------------------------------
    #    Name: _getManagerGeneratorEntry
    #    Args: nodeType : (hou.NodeType)
    #              The node type to get a node type name match for.
    #          categoryName=None : (str)
    #              An optional node type category name.  If None, use the node
    #              type category from the node.
    #  Raises: N/A
    # Returns: hou.Color|None
    #              Returns the matching color, if any, otherwise None.
    #    Desc: Look for a color match based on the node type category being a
    #          manager or generator type.
    # -------------------------------------------------------------------------
    def _getManagerGeneratorEntry(self, nodeType, categoryName=None):
        # Get the category name from the node.
        if categoryName is None:
            categoryName = nodeType.category().name()

        # Check if the category has any entries.
        if categoryName in self.nodes:
            categoryEntries = self.nodes[categoryName]

            # The node type is a manager.
            if nodeType.isManager():
                # Check for a manager entry under the category.
                if "manager" in categoryEntries:
                    return categoryEntries["manager"]

            # The node type is a generator.
            elif nodeType.isGenerator():
                # Check for a generator entry under the category.
                if "generator" in categoryEntries:
                    return categoryEntries["generator"]

        return None

    # -------------------------------------------------------------------------
    #    Name: _getNameEntry
    #    Args: node: (hou.Node)
    #              The node to look for a name match for.
    #          categoryName=None : (str)
    #              An optional node type category name.  If None, use the node
    #              type category from the node.
    #  Raises: N/A
    # Returns: hou.Color|None
    #              Returns the matching color, if any, otherwise None.
    #    Desc: Look for a color match based on the node name.
    # -------------------------------------------------------------------------
    def _getNameEntry(self, node, categoryName=None):
        # Get the category name from the node.
        if categoryName is None:
            categoryName = node.type().category().name()

        # The node name.
        name = node.name()

        # Check for entries for the node type category.
        if categoryName in self.names:
            # Check if the node name is in the mapping.
            if name in self.names[categoryName]:
                # Return the found object's color object.
                return self.names[categoryName][name]

        return None

    # -------------------------------------------------------------------------
    #    Name: _getToolColor
    #    Args: nodeType : (hou.NodeType)
    #              The node type to get a tool menu location match for.
    #  Raises: N/A
    # Returns: hou.Color|None
    #              Returns the matching color, if any, otherwise None.
    #    Desc: Look for a color match based on the node type's Tab menu
    #          locations.
    # -------------------------------------------------------------------------
    def _getToolColor(self, nodeType):
        # Try to get a color match for the exact node type and category.
        color = self._getToolEntry(nodeType)

        # Look for an entry in the generic category.
        if color is None:
            color = self._getToolEntry(nodeType, "all")

        return color

    # -------------------------------------------------------------------------
    #    Name: _getToolEntry
    #    Args: nodeType : (hou.NodeType)
    #              The node type to get a tool menu location match for.
    #          categoryName=None : (str)
    #              An optional node type category name.  If None, use the node
    #              type category from the node.
    #  Raises: N/A
    # Returns: hou.Color|None
    #              Returns the matching color, if any, otherwise None.
    #    Desc: Look for a color match based on the node type's category and
    #          Tab menu locations.
    # -------------------------------------------------------------------------
    def _getToolEntry(self, nodeType, categoryName=None):
        # Get the category name from the node.
        if categoryName is None:
            categoryName = nodeType.category().name()

        # Check for entries for the node type category.
        if categoryName in self.tools:
            # Get any Tab menu locations the node type might show up in.
            menuLocations = _getToolMenuLocations(nodeType)

            # Process the locations, looking for the first match.
            for location in menuLocations:
                # Check if the node name is in the mapping.
                if location in self.tools[categoryName]:
                    # Return the found object's color object.
                    return self.tools[categoryName][location]

        return None

    # -------------------------------------------------------------------------
    #    Name: _getTypeColor
    #    Args: nodeType : (hou.NodeType)
    #              The node type to get a node type name match for.
    #  Raises: N/A
    # Returns: hou.Color|None
    #              Returns the matching color, if any, otherwise None.
    #    Desc: Look for a color match based on the node type's name.
    # -------------------------------------------------------------------------
    def _getTypeColor(self, nodeType):
        # Try to get a color match for the exact node type and category.
        color = self._getTypeEntry(nodeType)

        # Look for an entry in the generic category.
        if color is None:
            color = self._getTypeEntry(nodeType, "all")

        return color

    # -------------------------------------------------------------------------
    #    Name: _getTypeEntry
    #    Args: nodeType : (hou.NodeType)
    #              The node type to get a node type name match for.
    #          categoryName=None : (str)
    #              An optional node type category name.  If None, use the node
    #              type category from the node.
    #  Raises: N/A
    # Returns: hou.Color|None
    #              Returns the matching color, if any, otherwise None.
    #    Desc: Look for a color match based on the node type's category and
    #          name.
    # -------------------------------------------------------------------------
    def _getTypeEntry(self, nodeType, categoryName=None):
        # Get the category name from the node.
        if categoryName is None:
            categoryName = nodeType.category().name()

        typeName = nodeType.name()

        # Check if the category has any entries.
        if categoryName in self.nodes:
            # Check if the node type name is in the category entries.
            if typeName in self.nodes[categoryName]:
                # Return the found color.
                return self.nodes[categoryName][typeName]

        return None

    # =========================================================================
    # INSTANCE PROPERTIES
    # =========================================================================

    @property
    def constants(self):
        """(dict) A dictionary of constant colors."""
	return self._constants

    @property
    def names(self):
        """(dict) A dictionary of node name colors."""
	return self._names

    @property
    def nodes(self):
        """(dict) A dictionary of node type name colors."""
	return self._nodes

    @property
    def tools(self):
        """(dict) A dictionary of tool menu location colors."""
	return self._tools

    # =========================================================================
    # METHODS
    # =========================================================================

    def colorNodeByName(self, node):
        """Color the node given its name.

        Args:
            node : (hou.Node)
                The node to color.

        Raises:
            N/A

        Returns:
            None

        """
        # Look for a name entry for the node's type category.
        color = self._getNameEntry(node)

        # Look for a name entry in the generic category.
        if color is None:
            color = self._getNameEntry(node, "all")

        # If a color was found, set the node to it.
        if color is not None:
            node.setColor(color)

    def colorNode(self, node):
        """Color the node given its properties.

        Args:
            node : (hou.Node)
                The node to color.

        Raises:
            N/A

        Returns:
            None

        This function will attempt to color the node by first matching its
        node type name, then the tab menu location and the whether or not it
        is a manager or generator type.

        """
        nodeType = node.type()

        # Look for a match with the node type name.
        color = self._getTypeColor(nodeType)

        # Look for a match given the node's Tab menu entries.
        if color is None:
            color = self._getToolColor(nodeType)

        # Check if the node is a manager or generator.
        if color is None:
            color = self._getManagerGeneratorColor(nodeType)

        # If a color was found, set it.
        if color is not None:
            node.setColor(color)


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

# -----------------------------------------------------------------------------
#    Name: _findSessionColorManager
#  Raises: N/A
# Returns: ColorManager|None
#              Returns the found color manager, if any, otherwise None.
#    Desc: Look at hou.session for a ColorManager stored as a 'colorManager'
#          attribute.  If the manager exists, return it.
# -----------------------------------------------------------------------------
def _findSessionColorManager():
    manager = None

    # Check to see if the manager exists.  If so, retrieve it.
    if hasattr(hou.session, "colorManager"):
        manager = hou.session.colorManager

    return manager

# -----------------------------------------------------------------------------
#    Name: _getToolMenuLocations
#    Args: nodeType : (hou.NodeType)
#              The node type to get tool menu locations for.
#  Raises: N/A
# Returns: (str)
#              A tuple of tool menu locations.
#    Desc: Get any Tab menu locations the tool for the node type lives in.
# -----------------------------------------------------------------------------
def _getToolMenuLocations(nodeType):
    # Need to get all of Houdini's tools.
    tools = hou.shelves.tools()

    # Figure out what the tool name should be for the give node type
    # information.
    toolName = hou.shelves.defaultToolName(
        nodeType.category().name(),
        nodeType.name()
    )

    # Check the tool name corresponds to a valid tool.
    if toolName in tools:
        tool = tools[toolName]

        # Return the menu locations.
        return tool.toolMenuLocations()

    return ()

# =============================================================================
# FUNCTIONS
# =============================================================================

def colorNode(node):
    """Color the node given its properties.

    Args:
        node : (hou.Node)
            The node to color.

    Raises:
        N/A

    Returns:
        None

    This function will attempt to color the node by first matching its
    node type name, then the tab menu location and the whether or not it
    is a manager or generator type.

    """
    # Try to find the session color manager.
    manager = _findSessionColorManager()

    # If one exists, use it to try to color the node.
    if manager is not None:
        manager.colorNode(node)


def colorNodeByName(node):
    """Color the node given its name.

    Args:
        node : (hou.Node)
            The node to color.

    Raises:
        N/A

    Returns:
        None

    """
    # Try to find the session color manager.
    manager = _findSessionColorManager()

    # If one exists, use it to try to color the node.
    if manager is not None:
        manager.colorNodeByName(node)


def createSessionColorManager():
    """Create a session ColorManager object.

    Raises:
        N/A

    Returns:
        None

    Create a new ColorManager object and store it in hou.session.colorManager.

    """
    manager = ColorManager()
    hou.session.colorManager = manager

