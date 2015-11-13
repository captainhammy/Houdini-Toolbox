


from ht.pyfilter.operations.operation import PyFilterOperation, logFilter
from ht.pyfilter.properties import PropertySetterManager

#from ht.pyfilter.properties import Proper


class SetProperties(PyFilterOperation):

    def __init__(self):
        super(SetProperties, self).__init__()

        self._property_manager = PropertySetterManager()

    @property
    def property_manager(self):
	return self._property_manager

    @logFilter
    def filterCamera(self):
	self.property_manager.setProperties("camera")

    @logFilter("object:name")
    def filterInstance(self):
	self.property_manager.setProperties("instance")

    @logFilter("object:name")
    def filterLight(self):
	self.property_manager.setProperties("light")

    @staticmethod
    def registerParserArgs(parser):
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

    def processParsedArgs(self, filter_args):

        if filter_args.properties is not None:
            self.property_manager.loadFromString(filter_args.properties)

        if filter_args.propertiesfile is not None:
            for filepath in filter_args.propertiesfile:
                self.property_manager.loadFromFile(filepath)

