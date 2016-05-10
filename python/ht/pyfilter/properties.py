"""This module defines objects used to set Mantra render properties."""

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

# =============================================================================
# CLASSES
# =============================================================================

class PropertySetterManager(object):


    def __init__(self):
        self._properties = {}

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _loadFromData(self, data):
        """Build PropertySetter objects from data."""
        # Process each filter stage name and it's data.
        for stage_name, stage_data in data.iteritems():
            # A list of properties for this stage.
            properties = self.properties.setdefault(stage_name, [])

            # Check if the stage should be disabled.
            if "disabled" in stage_data:
                if stage_data["disabled"]:
                    logger.debug(
                        "Stage entry disabled: {0}".format(stage_name)
                    )

                    continue

                # If not, remove the disabled entry.
                del(stage_data["disabled"])

            # The data is stored by property name.
            for property_name, property_block in stage_data.iteritems():
                # If we want to set the same property with different
                # settings multiple times (eg. different masks) we can
                # have a list of objects instead.  In the case where we
                # just have a single one (really a dictionary) then add it
                # to a list so we can process it in a loop.
                if isinstance(property_block, dict):
                    property_block = [property_block]

                if isinstance(property_block, Iterable):
                    # Process any properties in the block.
                    for property_elem in property_block:
                        prop = _createPropertySetter(
                            stage_name,
                            property_name,
                            property_elem
                        )

                        properties.append(prop)

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def properties(self):
        """Dictionary containing properties."""
        return self._properties

    # =========================================================================
    # METHODS
    # =========================================================================

    def loadFromFile(self, filepath):
        """Load properties from a file."""
        logger.debug("Reading properties from {0}".format(filepath))

        # Load json data from the file.
        with open(filepath) as f:
            data = json.load(f, object_hook=ht.utils.convertFromUnicode)

        self._loadFromData(data)

    def parseFromString(self, property_string):
        """Load properties from a string."""
        data = json.loads(property_string, object_hook=ht.utils.conveertFromUnicode)

        self._loadFromData(data)

    def setProperties(self, stage):
        """Apply properties."""
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

    def __init__(self, name, property_block):
        self._name = name

        # Store the raw value object.
        self._value = property_block["value"]

        self._enabled = True
        self._find_file = False

        if "findFile" in property_block:
            self.find_file = property_block["findFile"]

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
            value = "'{0}'".format(value)

        return "<PropertySetter {0}={1}>".format(self.name, value)

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _processValue(self):
        """Perform operations and cleanup of the value data."""
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
            contains_string = False

            for val in self.value:
                # If the value is a string, flag it.
                if isinstance(val, str):
                    contains_string = True
                    break

            # If at least one value is a string then we need to convert them
            # all to strings.
            if contains_string:
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

    @property
    def find_file(self):
        """Is the value the name of a file to find."""
        return self._find_file

    @find_file.setter
    def find_file(self, find_file):
        self._find_file = find_file

    @property
    def name(self):
        """The name of the property to set."""
        return self._name

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

        logger.debug(
            "Setting property '{0}' to {1}".format(self.name, self.value)
        )

        # Update the property value.
        import mantra
        mantra.setproperty(self.name, self.value)

# =============================================================================

class MaskedPropertySetter(PropertySetter):
    """A PropertySetter that supports masking againt other properties.

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, name, property_block, mask_property_name):
        super(MaskedPropertySetter, self).__init__(name, property_block)

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
            value = "'{0}'".format(value)

        return "<{0} {1}={2} mask='{3}'>".format(
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
        """Set the property under mantra."""
        import mantra

        # Is this property being applied using a name mask.
        if self.mask is not None:
            # Get the name of the item that is currently being filtered.
            filtered_item = mantra.property(self.mask_property_name)[0]

            # If the mask pattern doesn't match, abort.
            if not hou.patternMatch(self.mask, filtered_item):
                return

        # Call the super class function to set the property.
        super(MaskedPropertySetter, self).setProperty()

# =============================================================================
# FUNCTIONS
# =============================================================================

def _createPropertySetter(stage_name, property_name, property_block):
    """Create a PropertySetter based on data."""
    # Handle masked properties.
    if "mask" in property_block:
        # Filter a plane.
        if stage_name == "plane":
            return MaskedPropertySetter(
                property_name,
                property_block,
                "plane:variable"
            )

        # Something involving an actual object.
        elif stage_name in ("fog", "light", "instance"):
            return MaskedPropertySetter(
                property_name,
                property_block,
                "object:name"
            )

        # If masking is specified but we don't know how to handle it, log a
        # warning message.  We will still return a regular PropertySetter
        # object though.
        else:
            logger.warning(
                "No masking available for {0}:{1}.".format(
                    stage_name,
                    property_name
                )
            )

    # Generic property setter.
    return PropertySetter(property_name, property_block)
