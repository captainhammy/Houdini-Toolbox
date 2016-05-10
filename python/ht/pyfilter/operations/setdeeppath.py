"""This module contains an operation to set the deep resolver path."""

__author__ = "Graham Thompson"
__email__ = "captainhammy@gmail.com"

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.pyfilter.logger import logger
from ht.pyfilter.operations.operation import PyFilterOperation, logFilter
from ht.pyfilter.property import setProperty

# =============================================================================
# CLASSES
# =============================================================================

class SetDeepResolverPath(PyFilterOperation):
    """Operation to set the deepresolver path.

    This operation creates and uses the -deeppath arg.

    """

    def __init__(self):
    	super(SetDeepResolverPath, self).__init__()

    	self._filepath = None

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def filepath(self):
        """The path to set to."""
        return self._filepath

    @filepath.setter
    def filepath(self, filepath):
        self._filepath = filepath

    # =========================================================================
    # STATIC METHODS
    # =========================================================================

    @staticmethod
    def registerParserArgs(parser):
        """Register interested parser args for this operation."""
        parser.add_argument(
            "-deeppath",
            nargs="?",
            default=None,
            action="store",
            help="Specify the deepresolver filepath."
        )

    # =========================================================================
    # METHODS
    # =========================================================================

    @logFilter
    def filterCamera(self):
        """Apply camera properties."""
        import mantra

        # Look for existing args.
        deepresolver = mantra.property("image:deepresolver")

        if deepresolver:
            args = list(deepresolver[0].split())

            try:
        	    idx = args.index("filename")

            except ValueError as inst:
        	    logger.exception(inst)
                return

            else:
        	    args[idx + 1] = self.filepath

        	# Set the new list as the property value
        	setProperty("image:deepresolver", args)

    def processParsedArgs(self, filter_args):
        """Process any of our interested arguments if they were passed."""
        if filter_args.deeppath is not None:
            self.filepath = filter_args.deeppath

    def shouldRun(self):
        """Only run if a target path was passed."""
	    return self.filepath is not None
