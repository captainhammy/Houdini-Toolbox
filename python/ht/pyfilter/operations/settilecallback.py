"""This module contains an operation to set a tile callback."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.pyfilter.operations.operation import PyFilterOperation, log_filter
from ht.pyfilter.property import set_property

# =============================================================================
# CLASSES
# =============================================================================


class SetTileCallback(PyFilterOperation):
    """Operation to set a mantra tile callback.

    This operation creates and uses the --tilecallback arg.

    """

    def __init__(self, manager):
        super(SetTileCallback, self).__init__(manager)

        # This could also be hardcoded and we could not bother with
        # parsing args or anything like that.
        self._tilecallback = None

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def tilecallback(self):
        """str: The path to the tile callback."""
        return self._tilecallback

    @tilecallback.setter
    def tilecallback(self, tilecallback):
        self._tilecallback = tilecallback

    # =========================================================================
    # STATIC METHODS
    # =========================================================================

    @staticmethod
    def build_arg_string(path=None):
        args = []

        if path is not None:
            args.append("--tile-callback {}".format(path))

        return " ".join(args)

    @staticmethod
    def register_parser_args(parser):
        """Register interested parser args for this operation."""
        parser.add_argument("--tilecallback")

    # =========================================================================
    # METHODS
    # =========================================================================

    @log_filter
    def filterCamera(self):
        """Apply camera properties."""
        set_property("render:tilecallback", self.tilecallback)

    def processParsedArgs(self, filter_args):
        """Process any of our interested arguments if they were passed."""
        if filter_args.tilecallback is not None:
            self.tilecallback = filter_args.tilecallback

    def should_run(self):
        """Only run if a callback file path is set."""
        return self.tilecallback is not None
