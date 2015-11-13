
from ht.pyfilter.operations.operation import PyFilterOperation, logFilter

from ht.pyfilter.property import setProperty

from ht.pyfilter.logger import logger

class SetDeepResolverPath(PyFilterOperation):

    def __init__(self):
	super(SetDeepResolverPath, self).__init__()

	self._filepath = None

    @property
    def filepath(self):
	return self._filepath

    @filepath.setter
    def filepath(self, filepath):
	self._filepath = filepath


    @staticmethod
    def registerParserArgs(parser):
	parser.add_argument(
	    "-deeppath",
	    nargs="?",
	    default=None,
	    action="store",
	    help="Specify the deepresolver filepath."
	)


    def processParsedArgs(self, filter_args):
	if filter_args.deeppath is not None:
	    self.filepath = filter_args.deeppath

    def shouldRun(self):
	return self.filepath is not None

    @logFilter
    def filterCamera(self):
	import mantra

	# Look for existing args.
	deepresolver = mantra.property("image:deepresolver")

        print mantra.property("image:deepresolver")
        print mantra.property("image:filename")

	if deepresolver:
	    args = list(deepresolver[0].split())

	    try:
		idx = args.index("filename")

	    except ValueError as inst:
		logger.exception(inst)

	    else:
		args[idx + 1] = self.filepath

		# Set the new list as the property value
		setProperty("image:deepresolver", args)

