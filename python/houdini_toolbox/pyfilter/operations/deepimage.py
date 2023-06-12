"""This module contains an operation to set the deep resolver path."""

# =============================================================================
# IMPORTS
# =============================================================================

# Future
from __future__ import annotations

# Standard Library
import logging
from typing import TYPE_CHECKING, List, Optional, Union

# Houdini Toolbox
from houdini_toolbox.pyfilter.operations.operation import (
    PyFilterOperation,
    log_filter_call,
)
from houdini_toolbox.pyfilter.property import get_property, set_property

if TYPE_CHECKING:
    import argparse

    from houdini_toolbox.pyfilter.manager import PyFilterManager

_logger = logging.getLogger(__name__)


# =============================================================================
# CLASSES
# =============================================================================


class SetDeepImage(PyFilterOperation):
    """Operation to modify deep image generation.

    :param manager: The manager this operation is registered with.

    """

    def __init__(self, manager: PyFilterManager) -> None:
        super().__init__(manager)

        self._all_passes = False
        self._disable_deep_image = False

        self._resolver = None
        self._filename = None
        self._compositing = None
        self._deepcompression = None
        self._depth_planes = None
        self._mipmaps = None
        self._ofsize = None
        self._ofstorage = None
        self._pzstorage = None
        self._zbias = None

    # -------------------------------------------------------------------------
    # NON-PUBLIC METHODS
    # -------------------------------------------------------------------------

    def _modify_deep_args(self, deep_args: List[str]) -> None:
        """Modify the args either in place or by adding to them.

        :param deep_args: The list of deep resolver args.
        :return:

        """
        arg_names = (
            "filename",
            "compositing",
            "deepcompression",
            "depth_planes",
            "mipmaps",
            "ofsize",
            "ofstorage",
            "pzstorage",
            "zbias",
        )

        # Look for each of our known args.
        for arg_name in arg_names:
            # Try to get the equivalent property on this object.
            value = getattr(self, arg_name)

            # Found a value we might be able to set.
            if value is not None:
                # The arg is already in the list so we need to modify the
                # existing value with our value.
                if arg_name in deep_args:
                    # The value is the next item in the list so get the index
                    # and modify the next one.
                    idx = deep_args.index(arg_name)
                    deep_args[idx + 1] = value

                # The arg is not currently in the args so add the name and value.
                else:
                    deep_args.extend((arg_name, value))

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def all_passes(self) -> bool:
        """Modify deep resolver during all render types."""
        return self._all_passes

    @property
    def compositing(self) -> Optional[int]:
        """Pre-composite the samples."""
        return self._compositing

    @property
    def deepcompression(self) -> Optional[int]:
        """Compression value."""
        return self._deepcompression

    @property
    def depth_planes(self) -> Optional[str]:
        """Special planes."""
        return self._depth_planes

    @property
    def disable_deep_image(self) -> bool:
        """Disable deep image generation."""
        return self._disable_deep_image

    @property
    def filename(self) -> Optional[str]:
        """The deep image path to set."""
        return self._filename

    @property
    def mipmaps(self) -> Optional[int]:
        """Create MIP mapped images."""
        return self._mipmaps

    @property
    def ofsize(self) -> Optional[int]:
        """The opacity storage size."""
        return self._ofsize

    @property
    def ofstorage(self) -> Optional[str]:
        """The opacity bit depth."""
        return self._ofstorage

    @property
    def pzstorage(self) -> Optional[str]:
        """The depth bit depth."""
        return self._pzstorage

    @property
    def resolver(self) -> Optional[str]:
        """The type of deep to generate."""
        return self._resolver

    @property
    def zbias(self) -> Optional[float]:
        """Compression bias."""
        return self._zbias

    # -------------------------------------------------------------------------
    # STATIC METHODS
    # -------------------------------------------------------------------------

    @staticmethod
    def build_arg_string(  # pylint: disable=arguments-differ,too-many-arguments
        disable_deep_image: bool = False,
        deep_all_passes: bool = False,
        deep_image_path: Optional[str] = None,
        resolver: Optional[str] = None,
        compositing: Optional[bool] = None,
        compression: Optional[int] = None,
        depth_planes: Optional[Union[List[str], str]] = None,
        mipmaps: Optional[bool] = None,
        ofsize: Optional[int] = None,
        ofstorage: Optional[str] = None,
        pzstorage: Optional[str] = None,
        zbias: Optional[float] = None,
    ) -> str:
        """Build an argument string for this operation.

        :param disable_deep_image: Whether to disable the deep image.
        :param deep_all_passes: Whether to modify the deep resolver
                                during all render types.
        :param deep_image_path: The path to the output deep image.
        :param resolver: The deep resolver to run.
        :param compositing: Whether to pre-composite the values.
        :param compression: The compression value.
        :param depth_planes: A list of special planes.
        :param mipmaps: Whether to create MIP mapped images.
        :param ofsize: The opacity size (float vs vector).
        :param ofstorage: The opacity bit depth:
        :param pzstorage: The Z depth bit depth:
        :param zbias: The compression bias.
        :return: The constructed argument string.

        """
        args = []

        if disable_deep_image:
            args.append("--disable-deep-image")

        if deep_image_path is not None:
            args.append(f"--deep-image-path={deep_image_path}")

        if resolver is not None:
            args.append(f"--deep-resolver={resolver}")

        if compositing is not None:
            args.append(f"--deep-compositing={compositing}")

        if compression is not None:
            args.append(f"--deep-compression={compression}")

        if depth_planes is not None:
            if not isinstance(depth_planes, str):
                depth_planes = ",".join(depth_planes)

            args.append(f"--deep-depth-planes={depth_planes}")

        if mipmaps is not None:
            args.append(f"--deep-mipmaps={mipmaps}")

        if ofsize is not None:
            args.append(f"--deep-ofsize={ofsize}")

        if ofstorage is not None:
            args.append(f"--deep-ofstorage={ofstorage}")

        if pzstorage is not None:
            args.append(f"--deep-pzstorage={pzstorage}")

        if zbias is not None:
            args.append(f"--deep-zbias={zbias}")

        if deep_all_passes:
            args.append("--deep-all-passes")

        return " ".join(args)

    @staticmethod
    def register_parser_args(parser: argparse.ArgumentParser) -> None:
        """Register interested parser args for this operation.

        :param parser: The argument parser to attach arguments to.
        :return:

        """
        parser.add_argument("--deep-image-path", dest="deep_image_path")

        parser.add_argument(
            "--deep-all-passes", action="store_true", dest="deep_all_passes"
        )

        parser.add_argument(
            "--disable-deep-image", action="store_true", dest="disable_deep_image"
        )

        parser.add_argument(
            "--deep-resolver", choices=("camera", "shadow"), dest="deep_resolver"
        )

        parser.add_argument("--deep-compression", type=int, dest="deep_compression")

        parser.add_argument("--deep-compositing", type=int, dest="deep_compositing")

        parser.add_argument("--deep-depth-planes", dest="deep_depth_planes")

        parser.add_argument(
            "--deep-mipmaps", type=int, choices=(0, 1), dest="deep_mipmaps"
        )

        parser.add_argument(
            "--deep-ofsize", type=int, choices=(1, 3), dest="deep_ofsize"
        )

        parser.add_argument(
            "--deep-ofstorage",
            choices=("real16", "real32", "real64"),
            dest="deep_ofstorage",
        )

        parser.add_argument(
            "--deep-pzstorage",
            choices=("real16", "real32", "real64"),
            dest="deep_pzstorage",
        )

        parser.add_argument("--deep-zbias", type=float, dest="deep_zbias")

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    @log_filter_call
    def filter_camera(self) -> None:
        """Apply camera properties.

        :return:

        """
        render_type = get_property("renderer:rendertype")

        if not self.all_passes and render_type != "beauty":
            _logger.warning("Not a beauty render, skipping deepresolver")
            return

        if self.disable_deep_image:
            _logger.info("Disabling deep resolver")
            set_property("image:deepresolver", [])

        else:
            # Look for existing args.
            deep_args = get_property("image:deepresolver")

            # If deep rendering is not enabled the args will be empty.
            if not deep_args:
                # If a resolver type and filename was passed then we will create
                # args for the resolver type to enable deep output.
                if self.resolver and self.filename:
                    deep_args = [self.resolver]

                # Log an error and abort.
                else:
                    _logger.error("Cannot set deepresolver: deep output is not enabled")

                    return

            # Modify the args to include any passed along options.
            self._modify_deep_args(deep_args)

            _logger.debug(
                "Setting 'image:deepresolver': %s",
                " ".join([str(arg) for arg in deep_args]),
            )

            set_property("image:deepresolver", deep_args)

    def process_parsed_args(self, filter_args: argparse.Namespace) -> None:
        """Process any parsed args that the operation may be interested in.

        :param filter_args: The argparse namespace containing processed args.
        :return:

        """
        if filter_args.disable_deep_image:
            self._disable_deep_image = True

        if filter_args.deep_all_passes:
            self._all_passes = True

        if filter_args.deep_image_path is not None:
            self._filename = filter_args.deep_image_path

        if filter_args.deep_resolver is not None:
            self._resolver = filter_args.deep_resolver

        if filter_args.deep_compositing is not None:
            self._compositing = filter_args.deep_compositing

        if filter_args.deep_compression is not None:
            self._deepcompression = filter_args.deep_compression

        if filter_args.deep_depth_planes is not None:
            self._depth_planes = filter_args.deep_depth_planes

        if filter_args.deep_mipmaps is not None:
            self._mipmaps = filter_args.deep_mipmaps

        if filter_args.deep_ofsize is not None:
            self._ofsize = filter_args.deep_ofsize

        if filter_args.deep_ofstorage is not None:
            self._ofstorage = filter_args.deep_ofstorage

        if filter_args.deep_pzstorage is not None:
            self._pzstorage = filter_args.deep_pzstorage

        if filter_args.deep_zbias is not None:
            self._zbias = filter_args.deep_zbias

    def should_run(self) -> bool:
        """Determine whether this operation should be run.

        This operation will run if the disable option is set or any of the
        other options which would modify the args are set.

        :return: Whether this operation should run.

        """
        if self.disable_deep_image:
            return True

        return any(
            (
                self.filename,
                self.resolver,
                self.compositing is not None,
                self.deepcompression is not None,
                self.depth_planes,
                self.mipmaps is not None,
                self.ofsize is not None,
                self.ofstorage,
                self.pzstorage,
                self.zbias is not None,
            )
        )
