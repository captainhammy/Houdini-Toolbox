"""This module defines objects used to set Mantra render properties."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
from collections import Iterable
import json

# Houdini Toolbox Imports
from ht.pyfilter.logger import logger
import ht.utils

# Houdini Imports
import hou

# =============================================================================
# CLASSES
# =============================================================================

class PropertySetterManager(object):
    """Class for creating and managing PropertySetters.

    """

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
                        "Stage entry disabled: {}".format(stage_name)
                    )

                    continue

                # If not, remove the disabled entry.
                del(stage_data["disabled"])

            # The data is stored by property name.
            for property_name, property_block in stage_data.iteritems():

                # Wrapping properties in a 'rendertype:type' block is supported
                # if the the name indicates that we have to modify the data.
                if property_name.startswith("rendertype:"):
                    # Get the rendertype name.
                    rendertype = property_name.split(":")[1]

                    # Process each child property block.
                    for name, block in property_block.iteritems():
                        # If the child data is the standard dictionary of data
                        # we can just insert the rendertype value into it.
                        if isinstance(block, dict):
                            block["rendertype"] = rendertype

                        # If the child data is a list of dictionaries then
                        # iterate over each one and insert the value.
                        elif isinstance(block, list):
                            for item in block:
                                item["rendertype"] = rendertype

                        # Process the child data block.
                        self._processBlock(
                            properties, stage_name, name, block
                        )

                # Normal data.
                else:
                    self._processBlock(
                        properties, stage_name, property_name, property_block
                    )

    def _processBlock(self, properties, stage_name, name, block):
        """Process a data block to add properties."""
        # If we want to set the same property with different settings multiple
        # times (eg. different masks) we can have a list of objects instead.
        # In the case where we just have a single one (really a dictionary)
        # then add it to a list so we can process it in a loop.
        if isinstance(block, dict):
            block = [block]

        # (Can't remember why this check is here. Shouldn't be needed, right?)
        if isinstance(block, Iterable):
            # Process any properties in the block.
            for property_elem in block:
                prop = _createPropertySetter(
                    stage_name,
                    name,
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
        logger.debug("Reading properties from {}".format(filepath))

        # Load json data from the file.
        with open(filepath) as f:
            data = json.load(f, object_hook=ht.utils.convertFromUnicode)

        self._loadFromData(data)

    def parseFromString(self, property_string):
        """Load properties from a string."""
        data = json.loads(
            property_string,
            object_hook=ht.utils.convertFromUnicode
        )

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
        self._rendertype = None

        if "findFile" in property_block:
            self.find_file = property_block["findFile"]

        if "enabled" in property_block:
            self.enabled = property_block["enabled"]

        if "rendertype" in property_block:
            self.rendertype = property_block["rendertype"]

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

        return "<PropertySetter {}={}>".format(self.name, value)

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

    # =========================================================================

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

    # =========================================================================

    @property
    def rendertype(self):
        """Apply to specific render types."""
        return self._rendertype

    @rendertype.setter
    def rendertype(self, rendertype):
        self._rendertype = rendertype

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

        import mantra

        # Is this property being applied to a specific render type.
        if self.rendertype is not None:
            # Get the rendertype for the current pass.
            rendertype = mantra.property("renderer:rendertype")[0]

            # If the type pattern doesn't match, abort.
            if not hou.patternMatch(self.rendertype, rendertype):
                return

        logger.debug(
            "Setting property '{}' to {}".format(self.name, self.value)
        )

        # Update the property value.
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
                "No masking available for {}:{}.".format(
                    stage_name,
                    property_name
                )
            )

    # Generic property setter.
    return PropertySetter(property_name, property_block)

