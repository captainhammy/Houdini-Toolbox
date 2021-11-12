"""This module contains an operation to set the primary image path."""

# =============================================================================
# IMPORTS
# =============================================================================

from __future__ import annotations

# Standard Library
import logging
from typing import TYPE_CHECKING, Optional

# Houdini Toolbox
from ht.pyfilter.operations.operation import PyFilterOperation, log_filter_call
from ht.pyfilter.property import set_property

if TYPE_CHECKING:
    import argparse

    from ht.pyfilter.manager import PyFilterManager

_logger = logging.getLogger(__name__)


# =============================================================================
# CLASSES
# =============================================================================


class SetPrimaryImage(PyFilterOperation):
    """Operation to modify the primary image path.

    :param manager: The manager this operation is registered with.

    """

    def __init__(self, manager: PyFilterManager):
        super().__init__(manager)

        self._disable_primary_image = False
        self._primary_image_path = None

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def disable_primary_image(self) -> bool:
        """Disable primary image generation."""
        return self._disable_primary_image

    @property
    def primary_image_path(self) -> Optional[str]:
        """The primary image path to set."""
        return self._primary_image_path

    # -------------------------------------------------------------------------
    # STATIC METHODS
    # -------------------------------------------------------------------------

    @staticmethod
    def build_arg_string(  # pylint: disable=arguments-differ
        primary_image_path: Optional[str] = None, disable_primary_image: bool = False
    ) -> str:
        """Build an argument string for this operation.

        :param primary_image_path: The primary image path to set.
        :param disable_primary_image: Whether or not to disable the primary image.
        :return: The constructed argument string.

        """
        args = []

        if primary_image_path is not None:
            args.append(f"--primary-image-path={primary_image_path}")

        if disable_primary_image:
            args.append("--disable-primary-image")

        return " ".join(args)

    @staticmethod
    def register_parser_args(parser: argparse.ArgumentParser):
        """Register interested parser args for this operation.

        :param parser: The argument parser to attach arguments to.
        :return:

        """
        parser.add_argument("--primary-image-path", dest="primary_image_path")

        parser.add_argument(
            "--disable-primary-image", action="store_true", dest="disable_primary_image"
        )

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    @log_filter_call
    def filter_camera(self):
        """Apply camera properties.

        :return:

        """
        if self.disable_primary_image:
            _logger.info("Disabling primary image")
            set_property("image:filename", "null:")

        elif self.primary_image_path is not None:
            set_property("image:filename", self.primary_image_path)

    def process_parsed_args(self, filter_args: argparse.Namespace):
        """Process any parsed args that the operation may be interested in.

        :param filter_args: The argparse namespace containing processed args.
        :return:

        """
        if filter_args.disable_primary_image:
            self._disable_primary_image = True

        if filter_args.primary_image_path is not None:
            self._primary_image_path = filter_args.primary_image_path

    def should_run(self) -> bool:
        """Determine whether or not this filter should be run.

        This operation will run if it is disabling the primary image or needs
        to set the image path.

        :return: Whether or not this operation should run.

        """
        return self.disable_primary_image or self.primary_image_path is not None
