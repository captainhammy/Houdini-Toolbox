"""This module defines an object interface to get and set Mantra render
properties.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
from collections import Iterable

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

    	values = mantra.property(self.name)

    	if len(values) == 1:
    	    value = values[0]

    	    if len(value.split()) > 2:
        		split_vals = value.split()

        		value = dict(zip(*[iter(split_vals)]*2))

    	    else:
                value = _parseString(value)

    	else:
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

        if value is None:
            value = []

        if not isinstance(value, Iterable):
            value = [value]

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

def setProperty(name, value):
    """Set a property to a value.

    This is a wrapper around the Property.value setter.

    """
    Property(name).value = value

