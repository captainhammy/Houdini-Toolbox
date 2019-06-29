"""This module contains an operation to set a tile callback."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.pyfilter.operations.operation import PyFilterOperation, log_filter_call
from ht.pyfilter.property import set_property


# =============================================================================
# CLASSES
# =============================================================================

class SetTileCallback(PyFilterOperation):
    """Operation to set a mantra tile callback.

    :param manager: The manager this operation is registered with.
    :type manager: ht.pyfilter.manager.PyFilterManager

    """

    def __init__(self, manager):
        super(SetTileCallback, self).__init__(manager)

        # This could also be hardcoded and we could not bother with
        # parsing args or anything like that.
        self._tilecallback = None

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def tilecallback(self):
        """str: The path to the tile callback."""
        return self._tilecallback

    # -------------------------------------------------------------------------
    # STATIC METHODS
    # -------------------------------------------------------------------------

    @staticmethod
    def build_arg_string(path=None):  # pylint: disable=arguments-differ
        """Build an argument string for this operation.

        :param path: The path to the tile callback.
        :type path: str
        :return: The constructed argument string.
        :rtype: str

        """
        args = []

        if path is not None:
            args.append("--tile-callback={}".format(path))

        return " ".join(args)

    @staticmethod
    def register_parser_args(parser):
        """Register interested parser args for this operation.

        :param parser: The argument parser to attach arguments to.
        :type parser: argparse.ArgumentParser.
        :return:

        """
        parser.add_argument("--tile-callback", dest="tilecallback")

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    @log_filter_call
    def filterCamera(self):
        """Apply camera properties.

        :return:

        """
        set_property("render:tilecallback", self.tilecallback)

    def process_parsed_args(self, filter_args):
        """Process any parsed args that the operation may be interested in.

        :param filter_args: The argparse namespace containing processed args.
        :type filter_args: argparse.Namespace
        :return:

        """
        if filter_args.tilecallback is not None:
            self._tilecallback = filter_args.tilecallback

    def should_run(self):
        """Determine whether or not this filter should be run.

        This operation runs if the callback file path is set.

        :return: Whether or not this operation should run.
        :rtype: bool

        """
        return self.tilecallback is not None
