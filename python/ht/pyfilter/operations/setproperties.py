"""This module contains an operation to set properties passed as a string or
file path.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
from builtins import object
import builtins

try:
    from collections.abc import Iterable

except ImportError:
    from collections import Iterable

import json
import logging

# Houdini Toolbox Imports
from ht.pyfilter.operations.operation import PyFilterOperation, log_filter_call
from ht.pyfilter.property import get_property, set_property

_logger = logging.getLogger(__name__)


# =============================================================================
# CLASSES
# =============================================================================


class PropertySetterManager(object):
    """Class for creating and managing PropertySetters."""

    def __init__(self):
        self._properties = {}

    # -------------------------------------------------------------------------
    # NON-PUBLIC METHODS
    # -------------------------------------------------------------------------

    def _load_from_data(self, data):
        """Build PropertySetter objects from data.

        :param data: A data dictionary.
        :type data: dict
        :return:

        """
        # Process each filter stage name and it's data.
        for stage_name, stage_data in list(data.items()):
            # A list of properties for this stage.
            properties = self.properties.setdefault(stage_name, [])

            # The data is stored by property name.
            for property_name, property_block in list(stage_data.items()):
                # Wrapping properties in a 'rendertype:type' block is supported
                # if the the name indicates that we have to modify the data.
                if property_name.startswith("rendertype:"):
                    # Get the rendertype name.
                    rendertype = property_name.split(":")[1]

                    _process_rendertype_block(
                        properties, stage_name, rendertype, property_block
                    )

                # Normal data.
                else:
                    _process_block(
                        properties, stage_name, property_name, property_block
                    )

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def properties(self):
        """dict: Dictionary containing properties."""
        return self._properties

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def load_from_file(self, file_path):
        """Load properties from a file.

        :param file_path: A file containing json property data.
        :type file_path: str
        :return:

        """
        _logger.debug("Reading properties from %s", file_path)

        # Load json data from the file.
        with builtins.open(file_path) as handle:
            data = json.load(handle)

        self._load_from_data(data)

    def parse_from_string(self, property_string):
        """Load properties from a string.

        :param property_string: A json string containing property data.
        :type property_string: str

        """
        data = json.loads(property_string)

        self._load_from_data(data)

    def set_properties(self, stage):
        """Apply properties.

        :param stage: The stage name.
        :type stage: str
        :return:

        """
        if stage in self.properties:
            for prop in self.properties[stage]:
                prop.set_property()


class PropertySetter(object):
    """An object representing a Mantra property being set by PyFilter.

    :param name: The property name.
    :type name: str
    :param property_block: Property data to set.
    :type property_block: dict

    """

    # -------------------------------------------------------------------------
    # CONSTRUCTORS
    # -------------------------------------------------------------------------

    def __init__(self, name, property_block):
        self._name = name

        # Store the raw value object.
        self._value = property_block["value"]

        self._find_file = property_block.get("findfile", False)
        self._rendertype = property_block.get("rendertype")

        if self.find_file:
            import hou

            self._value = hou.findFile(self.value)

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __repr__(self):
        value = self.value

        # Wrap string values in single quotes.
        if isinstance(value, str):
            value = "'{}'".format(value)

        return "<PropertySetter {}={}>".format(self.name, value)

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def find_file(self):
        """bool: Is the value the name of a file to find."""
        return self._find_file

    @property
    def name(self):
        """str: The name of the property to set."""
        return self._name

    @property
    def rendertype(self):
        """str: Apply to specific render types."""
        return self._rendertype

    @property
    def value(self):
        """object: The value to set the property."""
        return self._value

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def set_property(self):
        """Set the property to the value.

        :return:

        """
        import hou

        # Is this property being applied to a specific render type.
        if self.rendertype is not None:
            # Get the rendertype for the current pass.
            rendertype = get_property("renderer:rendertype")

            # If the type pattern doesn't match, abort.
            if not hou.patternMatch(self.rendertype, rendertype):
                return

        _logger.debug("Setting property '%s' to %s", self.name, self.value)

        # Update the property value.
        set_property(self.name, self.value)


class MaskedPropertySetter(PropertySetter):
    """A PropertySetter that supports masking against other properties.

    :param name: The name of the property to set.
    :type name: str
    :param property_block: Property data to set.
    :type property_block: dict
    :param mask_property_name: The name of the mask property.
    :type mask_property_name: str

    """

    # -------------------------------------------------------------------------
    # CONSTRUCTORS
    # -------------------------------------------------------------------------

    def __init__(self, name, property_block, mask_property_name):
        super(MaskedPropertySetter, self).__init__(name, property_block)

        # Look for a mask property.
        self._mask = property_block["mask"]

        self._mask_property_name = mask_property_name

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __repr__(self):
        value = self.value

        # Wrap string values in single quotes.
        if isinstance(value, str):
            value = "'{}'".format(value)

        return "<{} {}={} mask='{}'>".format(
            self.__class__.__name__, self.name, value, self.mask
        )

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def mask(self):
        """str: A mask value."""
        return self._mask

    @property
    def mask_property_name(self):
        """str: The property name to compare the mask against."""
        return self._mask_property_name

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def set_property(self):
        """Set the property under mantra.

        :return:

        """
        import hou

        # Is this property being applied using a name mask.
        if self.mask is not None:
            # Get the name of the item that is currently being filtered.
            property_value = get_property(self.mask_property_name)

            # If the mask pattern doesn't match, abort.
            if not hou.patternMatch(self.mask, property_value):
                return

        # Call the super class function to set the property.
        super(MaskedPropertySetter, self).set_property()


class SetProperties(PyFilterOperation):
    """Operation to set misc properties passed along as a string or file path.

    :param manager: The manager this operation is registered with.
    :type manager: ht.pyfilter.manager.PyFilterManager

    """

    def __init__(self, manager):
        super(SetProperties, self).__init__(manager)

        self._property_manager = PropertySetterManager()

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def property_manager(self):
        """PropertySetterManager: The property manager to use."""
        return self._property_manager

    # -------------------------------------------------------------------------
    # STATIC METHODS
    # -------------------------------------------------------------------------

    @staticmethod
    def build_arg_string(
        properties=None, properties_file=None
    ):  # pylint: disable=arguments-differ
        """Build an argument string for this operation.

        'properties' should be a json compatible dictionary.

        :param properties: The property data to set.
        :type properties: dict
        :param properties_file: A file to set property values from.
        :type properties_file: str
        :return: The constructed argument string.
        :rtype: str

        """
        args = []

        if properties is not None:
            args.append(
                '--properties="{}"'.format(json.dumps(properties).replace('"', '\\"'))
            )

        if properties_file is not None:
            args.append("--properties-file={}".format(properties_file))

        return " ".join(args)

    @staticmethod
    def register_parser_args(parser):
        """Register interested parser args for this operation.

        :param parser: The argument parser to attach arguments to.
        :type parser: argparse.ArgumentParser.
        :return:

        """
        parser.add_argument("--properties", nargs=1, action="store")

        parser.add_argument(
            "--properties-file", nargs="*", action="store", dest="properties_file"
        )

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    @log_filter_call
    def filter_camera(self):
        """Apply camera properties.

        :return:

        """
        self.property_manager.set_properties("camera")

    @log_filter_call("object:name")
    def filter_instance(self):
        """Apply object properties.

        :return:

        """
        self.property_manager.set_properties("instance")

    @log_filter_call("object:name")
    def filter_light(self):
        """Apply light properties.

        :return:

        """
        self.property_manager.set_properties("light")

    def process_parsed_args(self, filter_args):
        """Process any parsed args that the operation may be interested in.

        :param filter_args: The argparse namespace containing processed args.
        :type filter_args: argparse.Namespace
        :return:

        """
        if filter_args.properties is not None:
            for prop in filter_args.properties:
                self.property_manager.parse_from_string(prop)

        if filter_args.properties_file is not None:
            for file_path in filter_args.properties_file:
                self.property_manager.load_from_file(file_path)

    def should_run(self):
        """Determine whether or not this filter should be run.

        This operations runs if there are properties to set.

        :return: Whether or not this operation should run.
        :rtype: bool

        """
        return any(self.property_manager.properties)


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _create_property_setter(property_name, property_block, stage_name):
    """Create a PropertySetter based on data.

    :param property_name: The name of the property to set.
    :type property_name: str
    :param property_block: The property data to set.
    :type property_block: dict
    :param stage_name: The filter stage to run for.
    :type stage_name: str
    :return: A property setter object.
    :rtype: PropertySetter

    """
    # Handle masked properties.
    if "mask" in property_block:
        # Filter a plane.
        if stage_name == "plane":
            return MaskedPropertySetter(property_name, property_block, "plane:variable")

        # Something involving an actual object.
        if stage_name in ("fog", "light", "instance"):
            return MaskedPropertySetter(property_name, property_block, "object:name")

        # If masking is specified but we don't know how to handle it, log a
        # warning message.  We will still return a regular PropertySetter
        # object though.
        _logger.warning(
            "No masking available for %s:%s.", stage_name, property_name
        )

    # Generic property setter.
    return PropertySetter(property_name, property_block)


def _process_block(properties, stage_name, name, block):
    """Process a data block to add properties.

    :param properties: A list of property settings.
    :type properties: list
    :param stage_name: The filter stage to run for.
    :type stage_name: str
    :param name: The name of the property to set.
    :type name: str
    :param block: The property data to set.
    :type block: dict or list(dict)
    :return:

    """
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
            prop = _create_property_setter(name, property_elem, stage_name)

            properties.append(prop)


def _process_rendertype_block(properties, stage_name, rendertype, property_block):
    """Process a data block representing properties for a specific rendertype.

    :param properties: A list of property settings.
    :type properties: list
    :param stage_name: The filter stage to run for.
    :type stage_name: str
    :param rendertype: The render type.
    :type rendertype: str
    :param property_block: The property data to set.
    :type property_block: dict
    :return:

    """
    # Process each child property block.
    for name, block in list(property_block.items()):
        # If the child data is the standard dictionary of data
        # we can just insert the rendertype value into it.
        if isinstance(block, dict):
            block["rendertype"] = rendertype

        # If the child data is a list of dictionaries then
        # iterate over each one and insert the value.
        elif isinstance(block, list):
            for item in block:
                item["rendertype"] = rendertype

        else:
            raise TypeError("Must be dict or list, got {}".format(type(block)))

        # Process the child data block.
        _process_block(properties, stage_name, name, block)
