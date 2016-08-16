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

    def __init__(self, manager):
        super(SetDeepResolverPath, self).__init__(manager)

        self._beauty_only = False
        self._filepath = None

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def beauty_only(self):
        """Only modify deep resolver during beauty render."""
        return self._beauty_only

    @beauty_only.setter
    def beauty_only(self, beauty_only):
        self._beauty_only = beauty_only

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
    def buildArgString(path):
        return "-deeppath {}".format(path)

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

        parser.add_argument(
            "-deepbeautyonly",
            action="store_true",
            help="Only modify deep resolver for beauty renders."
        )

    # =========================================================================
    # METHODS
    # =========================================================================

    @logFilter
    def filterCamera(self):
        """Apply camera properties."""
        import mantra

        render_type = mantra.property("renderer:rendertype")[0]

        if self.beauty_only and render_type != "beauty":
            logger.warning("Not a beauty render, skipping deepresolver")
            return

        # Look for existing args.
        deepresolver = mantra.property("image:deepresolver")

        if deepresolver == ['']:
            logger.error("Cannot set deepresolver: deepresolver is not enabled")
            return

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

        if filter_args.deepbeautyonly is not None:
            self.beauty_only = filter_args.deepbeautyonly

    def shouldRun(self):
        """Only run if a target path was passed."""
        return self.filepath is not None

