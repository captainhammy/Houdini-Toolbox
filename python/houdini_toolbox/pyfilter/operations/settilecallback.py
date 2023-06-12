"""This module contains an operation to set a tile callback."""

# =============================================================================
# IMPORTS
# =============================================================================

# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING, Optional

# Houdini Toolbox
from houdini_toolbox.pyfilter.operations.operation import (
    PyFilterOperation,
    log_filter_call,
)
from houdini_toolbox.pyfilter.property import set_property

if TYPE_CHECKING:
    import argparse

    from houdini_toolbox.pyfilter.manager import PyFilterManager

# =============================================================================
# CLASSES
# =============================================================================


class SetTileCallback(PyFilterOperation):
    """Operation to set a mantra tile callback.

    :param manager: The manager this operation is registered with.

    """

    def __init__(self, manager: PyFilterManager) -> None:
        super().__init__(manager)

        # This could also be hardcoded, and we could not bother with
        # parsing args or anything like that.
        self._tilecallback = None

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def tilecallback(self) -> Optional[str]:
        """The path to the tile callback."""
        return self._tilecallback

    # -------------------------------------------------------------------------
    # STATIC METHODS
    # -------------------------------------------------------------------------

    @staticmethod
    def build_arg_string(  # pylint: disable=arguments-differ
        path: Optional[str] = None,
    ) -> str:
        """Build an argument string for this operation.

        :param path: The path to the tile callback.
        :return: The constructed argument string.

        """
        args = []

        if path is not None:
            args.append(f"--tile-callback={path}")

        return " ".join(args)

    @staticmethod
    def register_parser_args(parser: argparse.ArgumentParser) -> None:
        """Register interested parser args for this operation.

        :param parser: The argument parser to attach arguments to.
        :return:

        """
        parser.add_argument("--tile-callback", dest="tilecallback")

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    @log_filter_call
    def filter_camera(self) -> None:
        """Apply camera properties.

        :return:

        """
        set_property("render:tilecallback", self.tilecallback)

    def process_parsed_args(self, filter_args: argparse.Namespace) -> None:
        """Process any parsed args that the operation may be interested in.

        :param filter_args: The argparse namespace containing processed args.
        :return:

        """
        if filter_args.tilecallback is not None:
            self._tilecallback = filter_args.tilecallback

    def should_run(self) -> bool:
        """Determine whether this filter should be run.

        This operation runs if the callback file path is set.

        :return: Whether this operation should run.

        """
        return self.tilecallback is not None
