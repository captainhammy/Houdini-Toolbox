"""This module contains an operation to set properties passed as a string or
file path.

"""

__author__ = "Graham Thompson"
__email__ = "captainhammy@gmail.com"

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.pyfilter.operations.operation import PyFilterOperation, logFilter
from ht.pyfilter.properties import PropertySetterManager

# =============================================================================
# CLASSES
# =============================================================================

class SetProperties(PyFilterOperation):
    """Operation to set misc properties passed along as a string or file path.

    This operation creates and uses the -properties and -propertiesfile args.

    """

    def __init__(self, manager):
        super(SetProperties, self).__init__(manager)

        self._property_manager = PropertySetterManager()

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def property_manager(self):
        """Get the property manager."""
        return self._property_manager

   # =========================================================================
   # STATIC METHODS
   # =========================================================================

    @staticmethod
    def buildArgString(properties=None, properties_file=None):
        arg_string = ""

        if properties is not None:
            arg_string += "-properties {} ".format(
                json.dumps(properties)
            )

        if properties_file is not None:
            arg_string += "-propertiesfile {}".format(properties_file)

        return arg_string

    @staticmethod
    def registerParserArgs(parser):
        """Register interested parser args for this operation."""
        parser.add_argument(
            "-properties",
            nargs=1,
            action="store",
            help="Specify a property dictionary on the command line."
        )

        parser.add_argument(
            "-propertiesfile",
            nargs=1,
            action="store",
            help="Use a file to define render properties to override.",
        )

    # =========================================================================
    # METHODS
    # =========================================================================

    @logFilter
    def filterCamera(self):
        """Apply camera properties."""
        self.property_manager.setProperties("camera")

    @logFilter("object:name")
    def filterInstance(self):
        """Apply object properties."""
        self.property_manager.setProperties("instance")

    @logFilter("object:name")
    def filterLight(self):
        """Apply light properties."""
        self.property_manager.setProperties("light")

    def processParsedArgs(self, filter_args):
        """Process any of our interested arguments if they were passed."""
        if filter_args.properties is not None:
            for prop in filter_args.properties:
                self.property_manager.loadFromString(prop)

        if filter_args.propertiesfile is not None:
            for filepath in filter_args.propertiesfile:
                self.property_manager.loadFromFile(filepath)

