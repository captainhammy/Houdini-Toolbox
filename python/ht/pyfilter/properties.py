"""This module defines objects used to set Mantra render properties."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import logging

# Houdini Imports
import hou
import mantra

# =============================================================================
# CLASSES
# =============================================================================


class PropertySetting(object):
    """An object representing a Mantra property being set by PyFilter.

    """

    def __init__(self, name, property_block):
        logging.debug("Creating property {}.".format(name))

        self._name = name

        # Store the raw value object.
        self._value = property_block["value"]

        self._enabled = True
        self._find_file = False

        if "find_file" in property_block:
            self.find_file = property_block["find_file"]

        if "enabled" in property_block:
            self.enabled = property_block["enabled"]

        # Perform any value cleanup.
        self._processValue()

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __repr__(self):
        value = self.value

        # Wrap string values in single quotes.
        if isinstance(value, str):
            value = "'{}'".format(value)

        return "<PropertySetting {}={}>".format(self.name, value)

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _processValue(self):
        """Perform any operations or cleanup on our data."""
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
        if self.find_file:
            self.value = hou.findFile(self.value)

        # Object is a list (possibly numbers or strings or both).
        if isinstance(self.value, list):
            # Does the list contain any strings.
            contains_strings = False

            for val in self.value:
                # If the value is a string, flag it.
                if isinstance(val, str):
                    contains_strings = True
                    break

            # If at least one value is a string then we need to convert them
            # all to strings.
            if contains_strings:
                self.value = [str(val) for val in self.value]

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def enabled(self):
        """Is the property setting enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled

    # =========================================================================

    @property
    def find_file(self):
        """Is the value the name of a file to find."""
        return self._find_file

    @find_file.setter
    def find_file(self, find_file):
        self._find_file = find_file

    # =========================================================================

    @property
    def name(self):
        """The name of the property to set."""
        return self._name

    # =========================================================================

    @property
    def value(self):
        """The value to set the property."""
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    # =========================================================================
    # METHODS
    # =========================================================================

    def setProperty(self):
        """Set the property to the value."""
        # Don't do anything if the property isn't enabled.
        if not self.enabled:
            return

        logging.debug(
            "Setting property '{}' to {}".format(self.name, self.value)
        )

        # Update the property value.
        mantra.setproperty(self.name, self.value)


class MaskedPropertySetting(PropertySetting):
    """A PropertySetting that supports masking against other properties.

    """

    def __init__(self, name, property_block, mask_property_name):
        super(MaskedPropertySetting, self).__init__(name, property_block)

        # Look for a mask property.
        self._mask = str(property_block["mask"])

        self._mask_property_name = mask_property_name

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __repr__(self):
        value = self.value

        # Wrap string values in single quotes.
        if isinstance(value, str):
            value = "'{}'".format(value)

        return "<{} {}={} mask='{}'>".format(
            self.__class__.__name__,
            self.name,
            value,
            self.mask
        )

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def mask(self):
        """A mask value."""
        return self._mask

    @property
    def mask_property_name(self):
        """The property name to compare the mask against."""
        return self._mask_property_name

    # =========================================================================
    # METHODS
    # =========================================================================

    def setProperty(self):
        # Is this property being applied using a name mask.
        if self.mask is not None:
            # Get the name of the item that is currently being filtered.
            filtered_item = mantra.property(self.mask_property_name)[0]

            # If the mask pattern doesn't match, abort.
            if not hou.patternMatch(self.mask, filtered_item):
                return

        # Call the super class function to set the property.
        super(MaskedPropertySetting, self).setProperty()

