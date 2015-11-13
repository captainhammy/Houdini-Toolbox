"""This module defines objects used to set Mantra render properties.

Synopsis
--------

Classes:
    MaskedPropertySetter
        A PropertySetter that supports masking againt other properties.

    PropertySetter
        An object representing a Mantra property being set by PyFilter.

"""
__author__ = "Graham Thompson"
__email__ = "captainhammy@gmail.com"

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import json
from collections import Iterable

# Houdini Toolbox Imports
import ht.utils
from ht.pyfilter.logger import logger

# Houdini Imports
import hou
#import mantra

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MaskedPropertySetter",
    "PropertySetter",
]

# =============================================================================
# CLASSES
# =============================================================================

class PropertySetterManager(object):


    def __init__(self):
        self._properties = {}

    # =========================================================================

    def _loadFromData(self, data):
        # Process each filter stage name and it's data.
        for stageName, stageData in data.iteritems():
            # A list of properties for this stage.
            properties = self.properties.setdefault(stageName, [])

            # Check if the stage should be disabled.
            if "disabled" in stageData:
                if stageData["disabled"]:
                    logger.debug(
                        "Stage entry disabled: {0}".format(stageName)
                    )

                    continue

                # If not, remove the disabled entry.
                del(stageData["disabled"])

            # The data is stored by property name.
            for propertyName, propertyBlock in stageData.iteritems():
                # If we want to set the same property with different
                # settings multiple times (eg. different masks) we can
                # have a list of objects instead.  In the case where we
                # just have a single one (really a dictionary) then add it
                # to a list so we can process it in a loop.
                if isinstance(propertyBlock, dict):
                    propertyBlock = [propertyBlock]

                if isinstance(propertyBlock, Iterable):
                    # Process any properties in the block.
                    for propertyElem in propertyBlock:
                        prop = _createPropertySetter(
                            stageName,
                            propertyName,
                            propertyElem
                        )

                        properties.append(prop)

    # =========================================================================

    @property
    def properties(self):
        return self._properties

    # =========================================================================

    def loadFromFile(self, filepath):
        logger.debug("Reading properties from {0}".format(filepath))

        # Load json data from the file.
        with open(filepath) as f:
            data = json.load(f, object_hook=ht.utils.convertFromUnicode)

        self._loadFromData(data)


    def parseFromString(self, property_string):
        data = json.loads(property_string, object_hook=ht.utils.conveertFromUnicode)

        self._loadFromData(data)


    def setProperties(self, stage):
        if stage in self.properties:
            for prop in self.properties[stage]:
                prop.setProperty()


# =============================================================================

class PropertySetter(object):
    """An object representing a Mantra property being set by PyFilter.

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, name, propertyBlock):
        """Initialize a PropertySetter object.

        Args:
            name : (str)
                The name of the property.

            propertyBlock : (dict)
                A dictionary containing property settings.

        Raises:
            N/A

        Returns:
            N/A

        """
        self._name = name

        # Store the raw value object.
        self._value = propertyBlock["value"]

        self._enabled = True
        self._findFile = False

        if "findFile" in propertyBlock:
            self.findFile = propertyBlock["findFile"]

        if "enabled" in propertyBlock:
            self.enabled = propertyBlock["enabled"]

        # Perform any value cleanup.
        self._processValue()

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __repr__(self):
        value = self.value

        # Wrap string values in single quotes.
        if isinstance(value, str):
            value = "'{0}'".format(value)

        return "<PropertySetter {0}={1}>".format(self.name, value)

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    # -------------------------------------------------------------------------
    #    Name: _processValue
    #  Raises: N/A
    # Returns: None
    #    Desc: Perform any operations or cleanup on our data.
    # -------------------------------------------------------------------------
    def _processValue(self):
        # Skip normal types.
        if isinstance(self.value, (bool, float, int)):
            return

        # Don't do anything if the property isn't enabled.
        if not self.enabled:
            return

        # If the object is a list of only one entry, extract it.
        if len(self.value) == 1:
            self.value = self.value[0]

        # If the value is actually a relative file, search for it in the
        # Houdini path.
        if self.findFile:
            self.value = hou.findFile(self.value)

        # Object is a list (possibly numbers or strings or both).
        if isinstance(self.value, list):
            # Does the list contain any strings.
            containsStrings = False

            for val in self.value:
                # If the value is a string, flag it.
                if isinstance(val, str):
                    containsStrings = True
                    break

            # If at least one value is a string then we need to convert them
            # all to strings.
            if containsStrings:
                self.value = [str(val) for val in self.value]

    # =========================================================================
    # INSTANCE ATTRIBUTES
    # =========================================================================

    @property
    def enabled(self):
        """(bool) Is the property setting enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled

    @property
    def findFile(self):
        """(bool) Is the value the name of a file to find."""
        return self._findFile

    @findFile.setter
    def findFile(self, findFile):
        self._findFile = findFile

    @property
    def name(self):
        """(str) The name of the property to set."""
        return self._name

    @property
    def value(self):
        """(str|[str]|[int]|[float]) The value to set the property."""
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    # =========================================================================
    # METHODS
    # =========================================================================

    def setProperty(self):
        """Set the property to the value.

        Raises:
            N/A

        Returns:
            None

        """
        # Don't do anything if the property isn't enabled.
        if not self.enabled:
            return

        logger.debug(
            "Setting property '{0}' to {1}".format(self.name, self.value)
        )

        # Update the property value.
        import mantra
        mantra.setproperty(self.name, self.value)


class MaskedPropertySetter(PropertySetter):
    """A PropertySetter that supports masking againt other properties.

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, name, propertyBlock, maskPropertyName):
        """Initialize a MaskedPropertySetter object.

        Args:
            name : (str)
                The name of the property.

            propertyBlock : (dict)
                A dictionary containing property settings.

            maskPropertyName : (str)
                A property name to compare a mask value against.

        Raises:
            N/A

        Returns:
            N/A

        """
        super(MaskedPropertySetter, self).__init__(name, propertyBlock)

        # Look for a mask property.
        self._mask = str(propertyBlock["mask"])

        self._maskPropertyName = maskPropertyName


    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __repr__(self):
        value = self.value

        # Wrap string values in single quotes.
        if isinstance(value, str):
            value = "'{0}'".format(value)

        return "<{0} {1}={2} mask='{3}'>".format(
            self.__class__.__name__,
            self.name,
            value,
            self.mask
        )

    # =========================================================================
    # INSTANCE ATTRIBUTES
    # =========================================================================

    @property
    def mask(self):
        """(str) A mask value."""
        return self._mask

    @property
    def maskPropertyName(self):
        """(str) The property name to compare the mask against."""
        return self._maskPropertyName

    # =========================================================================
    # METHODS
    # =========================================================================

    def setProperty(self):
        import mantra

        # Is this property being applied using a name mask.
        if self.mask is not None:
            # Get the name of the item that is currently being filtered.
            filteredItem = mantra.property(self.maskPropertyName)[0]

            # If the mask pattern doesn't match, abort.
            if not hou.patternMatch(self.mask, filteredItem):
                return

        # Call the super class function to set the property.
        super(MaskedPropertySetter, self).setProperty()


# =============================================================================
# FUNCTIONS
# =============================================================================

def _createPropertySetter(stageName, propertyName, propertyBlock):
    # Handle masked properties.
    if "mask" in propertyBlock:
        # Filter a plane.
        if stageName == "plane":
            return MaskedPropertySetter(
                propertyName,
                propertyBlock,
                "plane:variable"
            )

        # Something involving an actual object.
        elif stageName in ("fog", "light", "instance"):
            return MaskedPropertySetter(
                propertyName,
                propertyBlock,
                "object:name"
            )

        # If masking is specified but we don't know how to handle it, log a
        # warning message.  We will still return a regular PropertySetter
        # object though.
        else:
            logger.warning(
                "No masking available for {0}:{1}.".format(
                    stageName,
                    propertyName
                )
            )

    # Generic property setter.
    return PropertySetter(propertyName, propertyBlock)

