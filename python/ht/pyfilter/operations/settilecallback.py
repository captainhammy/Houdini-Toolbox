"""This module contains an operation to set a tile callback."""

__author__ = "Graham Thompson"
__email__ = "captainhammy@gmail.com"

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.pyfilter.operations.operation import PyFilterOperation, logFilter
from ht.pyfilter.property import setProperty

# =============================================================================
# CLASSES
# =============================================================================

class SetTileCallback(PyFilterOperation):
    """Operation to set a mantra tile callback.

    This operation creates and uses the -tilecallback arg.

    """

    def __init__(self):
	    super(SetTileCallback, self).__init__()

        # This could also be hardcoded and we could not bother with
        # parsing args or anything like that.
        self._callback_path = None

    # =========================================================================
    # STATIC METHODS
    # =========================================================================

    @staticmethod
    def registerParserArgs(parser):
        """Register interested parser args for this operation."""
    	parser.add_argument(
    	    "-tilecallback",
    	    nargs="?",
    	    default=None,
    	    action="store",
    	    help=""
    	)

    # =========================================================================
    # METHODS
    # =========================================================================

    @logFilter
    def filterCamera(self):
        """Apply camera properties."""
	    setProperty("render:tilecallback", self._callback_path)

    def processParsedArgs(self, filter_args):
        """Process any of our interested arguments if they were passed."""
    	if filter_args.tilecallback is not None:
    	    self._callback_path = filter_args.tilecallback

    def shouldRun(self):
        """Only run if a callback file path is set."""
	    self._callback_path is not None
