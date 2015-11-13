
from ht.pyfilter.operations.operation import PyFilterOperation, logFilter
from ht.pyfilter.property import Property, setProperty

from ht.pyfilter.logger import logger

import mantra

class ZDepthPass(PyFilterOperation):

    def __init__(self):
	super(ZDepthPass, self).__init__()

	self._active = False

	self.data["set_pz"] = False

    @staticmethod
    def registerParserArgs(parser):
	parser.add_argument(
	    "-zdepth",
	    nargs="?",
	    default=None,
	    action="store",
	    help=""
	)

    def processParsedArgs(self, filter_args):
	if filter_args.zdepth is not None:
	    self._active = filter_args.zdepth

    def shouldRun(self):
	return self._active

    @logFilter
    def filterCamera(self):
	# Redirect output image?
	pass

    @logFilter("object:name")
    def filterInstance(self):
        matte = Property("object:matte").value
        phantom = Property("object:phantom").value
        surface = Property("object:surface").value

        print matte, phantom, surface

	surface = mantra.property("object:surface")[0]

        setProperty("object:overridedetail", True)

	shader = "opdef:/Shop/v_constant clr 0 0 0".split()

	if matte == "true" or surface == "matte" or phantom == "true":
	    setProperty("object:phantom", 1)

	else:
	    setProperty("object:surface", shader)
	    setProperty("object:displace", None)

    @logFilter("plane:variable")
    def filterPlane(self):
        channel = Property("plane:channel").value

	if channel == "Pz":
	    self.data["set_pz"] = True

	if not self.data["set_pz"] and channel not in ("C", "Of"):
            setProperty("plane:variable", "Pz")
            setProperty("plane:vextype", "float")
            setProperty("plane:channel", "Pz")
            setProperty("plane:pfilter", "minmax min")
            setProperty("plane:quantize", None)
	    self.data["set_pz"] = True

	elif channel not in ("C", "Pz"):
            setProperty("plane:disable", True)

