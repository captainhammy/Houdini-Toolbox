"""This module defines an object interface to get and set Mantra render
properties.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
from collections import Iterable
import json

# =============================================================================
# CLASSES
# =============================================================================


class Property(object):
    """This class respresents and interface for getting and setting
    Mantra properties.

    """

    def __init__(self, name):
        self._name = name
        self._value = None

        self._initData()

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _initData(self):
        """Init internal data."""
        import mantra

        # Get the value for this name from Mantra.
        values = mantra.property(self.name)

        # Value is a single value (really a single value list)
        if len(values) == 1:
            value = values[0]

            if isinstance(value, str):
                # Try to decode the string as a json object.
                try:
                    value = json.loads(value)

                # It can't be converted to a dict so we'll process it manually.
                except ValueError:
                    # Split the string.
                    split_vals = value.split()

                    # If there are multiple values we want to build a
                    # dictionary out of pairs.
                    if len(split_vals) > 2:
                        value = dict(zip(*[iter(split_vals)]*2))

                    # Not multiple values so do any additional processing.
                    else:
                        value = _parseString(value)

        # Value is a multi item list.
        else:
            # Try to convert all the items to json.
            try:
                value = [json.loads(val) for val in values]

            # Could not do that, so use value as is.
            except (TypeError, ValueError):
                value = values

        self._value = value

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def name(self):
        """The property name."""
        return self._name

    @property
    def value(self):
        """The property value."""
        return self._value

    @value.setter
    def value(self, value):
        import mantra

        # If the value is None then we should just set an empty list.
        if value is None:
            value = []

        # If the value is a string then it should be in a list.
        elif isinstance(value, (str, unicode)):
            value = [value]

        # If the value is a dictionary then we need to convert it to a json
        # string.
        elif isinstance(value, dict):
            value = [json.dumps(value)]

        # If the value isn't already in an iterable then it needs to be.
        elif not isinstance(value, Iterable):
            value = [value]

        # The value is already a list of something.
        else:
            # Check all the entries to see if they are dictionaries.
            if all([isinstance(val, dict) for val in value]):
                # If they are, try to convert them all to create a list
                # of json strings.
                try:
                    value = [json.dumps(val) for val in value]

                # Something bad occured, so just stick with the original.
                except (TypeError, ValueError):
                    pass

        mantra.setproperty(self.name, value)

        self._initData()

# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

def _parseString(value):
    """Process a string value looking for boolean values."""
    if value.lower() == "false":
        return False

    if value.lower() == "true":
        return True

    return value

# =============================================================================
# FUNCTIONS
# =============================================================================


def getProperty(name):
    """Get a property to a value.

    This is a wrapper around the Property.value.

    """
    return Property(name).value


def setProperty(name, value):
    """Set a property to a value.

    This is a wrapper around the Property.value setter.

    """
    Property(name).value = value

