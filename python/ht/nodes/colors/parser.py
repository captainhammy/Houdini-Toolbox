"""Functions to read color information from .json files.

Synopsis
--------

Classes:
    ColorEntry
        This class represents a color bound to a name.

Exceptions:
    ConstantDoesNotExistError
        Exception raised when a color attempts to reference a non-existent
        constant.

    InvalidColorTypeError
        Exception raised when a color is not a valid type defined in
        hou.colorType.

Functions:
    buildColor()
        Build a hou.Color object from data.

    buildMappings()
        Build mappings into a ColorManager.

"""
__author__ = "Graham Thompson"
__email__ = "captainhammy@gmail.com"

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import json

# Houdini Toolbox Imports
import ht.utils

# Houdini Imports
import hou

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ColorEntry",
    "ConstantDoesNotExistError",
    "InvalidColorTypeError",
    "buildColor",
    "buildMappings",
]

# =============================================================================
# CLASSES
# =============================================================================

class ColorEntry(object):
    """This class represents a color bound to a name.

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, name, color):
        """Initialize a ColorEntry object.

        Args:
            name : (str)
                The name the color is mapped to.

            color : (hou.Color)
                The color.

        Raises:
            N/A

        Returns:
            N/A

        """
        self._name = name
        self._color = color

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __eq__(self, entry):
        # For our purposes we only care if the names match.
        return self.name == entry.name

    def __repr__(self):
        return "<ColorEntry {name} ({color})>".format(
            name=self.name,
            color=self.color
        )

    # =========================================================================
    # INSTANCE PROPERTIES
    # =========================================================================

    @property
    def color(self):
        """(hou.Color) The mapped color."""
        return self._color

    @property
    def name(self):
        """(str) The name the color is mapped to."""
        return self._name


# =============================================================================
# EXCEPTIONS
# =============================================================================

class ConstantDoesNotExistError(Exception):
    """Exception raised when a color attempts to reference a non-existent
    constant.

    """

    def __init__(self, constantName):
        self.constantName = constantName

    def __str__(self):
        return "Constant {constant} does not exist.".format(
            constant=self.constantName
        )


class InvalidColorTypeError(Exception):
    """Exception raised when a color is not a valid type defined in
    hou.colorType.

    """

    def __init__(self, colorType):
        self.colorType = colorType

    def __str__(self):
        return "Invalid color type {type}".format(type=self.colorType)

# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

# -----------------------------------------------------------------------------
#    Name: _findFile
#  Raises: N/A
# Returns: str|None
#              The found .json file.
#    Desc: Find a .json file containing color information.
# -----------------------------------------------------------------------------
def _findFile():
    # Try to find the file.
    try:
        filePath = hou.findFile("config/gcs.json")

    # Catch the exception if the file couldn't be found and use None.
    except hou.OperationFailed:
        filePath = None

    return filePath


# -----------------------------------------------------------------------------
#    Name: _readFile
#  Raises: N/A
# Returns: (dict)
#              A dictionary of json color data.
#    Desc: Read color data from a .json file.
# -----------------------------------------------------------------------------
def _readFile():
    # Get the file to open.
    path = _findFile()

    # If the path doesn't exist, return an empty dictionary.
    if path is None:
        return {}

    # Open the target file.
    with open(path) as f:
        # Load the json data and convert the data from unicde.
        data = json.load(f, object_hook=ht.utils.convertFromUnicode)

    return data

# =============================================================================
# FUNCTIONS
# =============================================================================

def buildColor(data):
    """Build a hou.Color object from data.

    Args:
        data : (dict)
            A dictionary containing color information.

    Raises:
        InvalidColorTypeError
            This exception is raised if the 'type' data does not correspond
            to an available color type defined in hou.colorType.

    Returns:
        hou.Color
            The created hou.Color object.

    """
    value = data["color"]

    # Create an empty color value since we don't know the color format yet.
    color = hou.Color()

    # Try to get the associated hou.colorType object from the type.
    try:
        colorType = getattr(hou.colorType, data["type"])

    # Catch the AttributeError generated by invalid types and raise an
    # InvalidColorTypeError instead.
    except AttributeError:
        raise InvalidColorTypeError(data["type"])

    # Set the color value given the specified type.
    if colorType == hou.colorType.RGB:
        # We support defining RGB colors with just a single value for grey
        # shades.  If one is detected, create at tuple from it.
        if not isinstance(value, list):
            value = [value] * 3

        color.setRGB(value)

    elif colorType == hou.colorType.HSL:
        color.setHSL(value)

    elif colorType == hou.colorType.HSV:
        color.setHSV(value)

    elif colorType == hou.colorType.LAB:
        color.setLAB(value)

    elif colorType == hou.colorType.XYZ:
        color.setXYZ(value)

    return color


def buildMappings(manager):
    """Build mappings into a ColorManager.

    Args:
        manager : (ht.nodes.colors.ColorManager)
            The ColorManager to build mappings for.

    Raises:
        N/A

    Returns:
        None

    """
    # Read data from the file.
    data = _readFile()

    # Process any constants first so they can be used by assignments.
    if "constants" in data:
        for name, entry in data["constants"].iteritems():
            # Get the color from the info.
            color = buildColor(entry)

            # Store the constant under its name.
            manager.constants[name] = color

    # Process each of the different types of color assignments.
    for assignmentType in ("names", "nodes", "tools"):
        # Ensure the type exists in the data.
        if assignmentType in data:
            # Get the mapping dictionary from the manager.
            colorTypeMap = getattr(manager, assignmentType)

            # Process each category in the data.
            for categoryName, entries in data[assignmentType].iteritems():
                # Get a mapping list for the category name.
                categoryList = colorTypeMap.setdefault(categoryName, [])

                # Process each entry.  The entry name can be a node type name,
                # Tab menu folder name, or manager/generator.
                for entry in entries:
                    # Get the entry name and remove it from the data.
                    entryName = entry.pop("name")

                    # Is the color type a constant?
                    if entry["type"] == "constant":
                        # Get the constant name.
                        constantName = entry["constant"]

                        # Ensure the constant exists.  If not, raise an
                        # exception.
                        if constantName not in manager.constants:
                            raise ConstantDoesNotExistError(constantName)

                        color = manager.constants[constantName]

                    # Build the color from the raw data.
                    else:
                        color = buildColor(entry)

                    # Add a ColorEntry to the list.
                    categoryList.append(ColorEntry(entryName, color))

        # Look for "all" entries.  If there are any then we want to integrate
        # them into all categories if they don't exist there already.
        if "all" in colorTypeMap:
            # Remove the entries from the map.
            allEntries = colorTypeMap.pop("all")

            # Process each available node type category.
            for categoryName in hou.nodeTypeCategories():
                # Get the list of the category.
                categoryList = colorTypeMap.setdefault(categoryName, [])

                # Process each of the all entries for the current category.
                # If no entry with the same name exists, add the color to the
                # category.
                for entry in allEntries:
                    if entry not in categoryList:
                        categoryList.append(entry)

