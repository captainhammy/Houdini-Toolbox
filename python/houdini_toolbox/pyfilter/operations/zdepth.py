"""This module contains an operation to force a zdepth pass."""

# =============================================================================
# IMPORTS
# =============================================================================

# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING

# Houdini Toolbox
from houdini_toolbox.pyfilter.operations.operation import (
    PyFilterOperation,
    log_filter_call,
)
from houdini_toolbox.pyfilter.property import get_property, set_property

if TYPE_CHECKING:
    import argparse

    from houdini_toolbox.pyfilter.manager import PyFilterManager


# =============================================================================
# CLASSES
# =============================================================================


class ZDepthPass(PyFilterOperation):
    """Force the render to only contain C and Pz planes.

    As long as there is an extra image plane that is not C or Of this operation
    will remap an extra image plane to be Pz and disable the rest.

    :param manager: The manager this operation is registered with.

    """

    CONST_SHADER = "opdef:/Shop/v_constant clr 0 0 0"

    def __init__(self, manager: PyFilterManager) -> None:
        super().__init__(manager)

        # Should the operation be run.
        self._active = False

        # We have not set the Pz plane yet.
        self._data["set_pz"] = False

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def active(self) -> bool:
        """Whether the operation is active."""
        return self._active

    # -------------------------------------------------------------------------
    # STATIC METHODS
    # -------------------------------------------------------------------------

    @staticmethod
    def build_arg_string(  # pylint: disable=arguments-differ
        active: bool = False,
    ) -> str:
        """Build an argument string for this operation.

        :param active: Whether to run the operation.
        :return: The constructed argument string.

        """
        args = []

        if active:
            args.append("--zdepth")

        return " ".join(args)

    @staticmethod
    def register_parser_args(parser: argparse.ArgumentParser) -> None:
        """Register interested parser args for this operation.

        :param parser: The argument parser to attach arguments to.
        :return:

        """
        parser.add_argument("--zdepth", action="store_true")

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    @log_filter_call("object:name")
    def filter_instance(self) -> None:
        """Apply constant black shader to objects.

        :return:

        """
        matte = get_property("object:matte")
        phantom = get_property("object:phantom")
        surface = get_property("object:surface")

        set_property("object:overridedetail", True)

        if matte or phantom or surface == "matte":
            set_property("object:phantom", 1)

        else:
            set_property("object:surface", self.CONST_SHADER.split())
            set_property("object:displace", None)

    @log_filter_call("plane:variable")
    def filter_plane(self) -> None:
        """Modify image planes to ensure one will output Pz.

        This will disable all planes that are not C and Pz.

        :return:

        """
        channel = get_property("plane:channel")

        if channel == "Pz":
            # If the channel is Pz but we've already forcibly set one to Pz
            # then we need to disable the plane.
            if self.data["set_pz"]:
                set_property("plane:disable", True)

                return

            # The plane is Pz and we have yet to indicate we've got a Pz so
            # store the data.
            self.data["set_pz"] = True

            return

        # If we haven't found a Pz plane yet and this channel isn't a primary
        # output channel then we will force it to be Pz.
        if not self.data["set_pz"] and channel not in ("C", "Of"):
            set_property("plane:variable", "Pz")
            set_property("plane:vextype", "float")
            set_property("plane:channel", "Pz")
            set_property("plane:pfilter", "minmax min")
            set_property("plane:quantize", None)
            self.data["set_pz"] = True

        # Disable any other planes.
        elif channel not in ("C",):
            set_property("plane:disable", True)

    def process_parsed_args(self, filter_args: argparse.Namespace) -> None:
        """Process any parsed args that the operation may be interested in.

        :param filter_args: The argparse namespace containing processed args.
        :return:

        """
        if filter_args.zdepth is not None:
            self._active = filter_args.zdepth

    def should_run(self) -> bool:
        """Determine whether this filter should be run.

        This operation will run if the 'active' flag was passed.

        :return: Whether this operation should run.

        """
        return self._active
