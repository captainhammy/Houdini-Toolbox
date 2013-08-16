"""This module defines objects used to set Mantra render properties.

Synopsis
--------

Classes:
    MaskedPropertySetting
        A PropertySetting that supports masking againt other properties.

    PropertySetting
        An object representing a Mantra property being set by PyFilter.

"""
__author__ = "Graham Thompson"
__email__ = "captainhammy@gmail.com"

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import logging

# Houdini Imports
import hou
import mantra

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MaskedPropertySetting",
    "PropertySetting",
]

# =============================================================================
# CLASSES
# =============================================================================

class PropertySetting(object):
    """An object representing a Mantra property being set by PyFilter.

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, name, propertyBlock):
        """Initialize a PropertySetting object.

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
        logging.debug("Creating property {0}.".format(name))

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

        return "<PropertySetting {0}={1}>".format(self.name, value)

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

        logging.debug(
            "Setting property '{0}' to {1}".format(self.name, self.value)
        )

        # Update the property value.
        mantra.setproperty(self.name, self.value)


class MaskedPropertySetting(PropertySetting):
    """A PropertySetting that supports masking againt other properties.

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, name, propertyBlock, maskPropertyName):
        """Initialize a MaskedPropertySetting object.

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
        super(MaskedPropertySetting, self).__init__(name, propertyBlock)

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
        # Is this property being applied using a name mask.
        if self.mask is not None:
            # Get the name of the item that is currently being filtered.
            filteredItem = mantra.property(self.maskPropertyName)[0]

            # If the mask pattern doesn't match, abort.
            if not hou.patternMatch(self.mask, filteredItem):
                return

        # Call the super class function to set the property.
        super(MaskedPropertySetting, self).setProperty()

