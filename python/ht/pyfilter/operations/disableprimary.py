"""This module contains an operation to set the deep resolver path."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.pyfilter.operations.operation import PyFilterOperation, logFilter
from ht.pyfilter.property import setProperty

# =============================================================================
# CLASSES
# =============================================================================

class DisablePrimaryImage(PyFilterOperation):
    """Operation to disable the primary image output.

    """

    def __init__(self, manager):
        super(DisablePrimaryImage, self).__init__(manager)

        self._disableprimary = False

    # =========================================================================
    # STATIC METHODS
    # =========================================================================

    @staticmethod
    def buildArgString():
        return "-disableprimary"

    @staticmethod
    def registerParserArgs(parser):
        """Register interested parser args for this operation."""

        parser.add_argument(
            "-disableprimary",
            action="store_true",
            help="Disable primary image output."
        )

    # =========================================================================
    # METHODS
    # =========================================================================

    @logFilter
    def filterCamera(self):
        """Apply camera properties."""
        # Disable primary image output by setting the output picture to "null:"
        setProperty("image:filename", "null:")

    def processParsedArgs(self, filter_args):
        """Process any of our interested arguments if they were passed."""
        if filter_args.disableprimary is not None:
            self._disableprimary = filter_args.disableprimary

    def shouldRun(self):
        """Only run if a target path was passed."""
        return self._disableprimary

