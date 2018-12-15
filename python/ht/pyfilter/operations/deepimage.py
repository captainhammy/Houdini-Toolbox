"""This module contains an operation to set the deep resolver path."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.logger import logger
from ht.pyfilter.operations.operation import PyFilterOperation, log_filter
from ht.pyfilter.property import get_property, set_property

# =============================================================================
# CLASSES
# =============================================================================


class SetDeepImage(PyFilterOperation):
    """Operation to modify deep image generation,

    """

    def __init__(self, manager):
        super(SetDeepImage, self).__init__(manager)

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

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _modify_deep_args(self, deep_args):
        """Modify the args either in place or by adding to them."""
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

        for arg_name in arg_names:
            value = getattr(self, arg_name)

            if value is not None:
                if arg_name in deep_args:
                    idx = deep_args.index(arg_name)
                    deep_args[idx + 1] = value

                else:
                    deep_args.extend((arg_name, value))

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def all_passes(self):
        """Modify deep resolver during all render types."""
        return self._all_passes

    @all_passes.setter
    def all_passes(self, all_passes):
        self._all_passes = all_passes

    @property
    def compositing(self):
        return self._compositing

    @compositing.setter
    def compositing(self, compositing):
        self._compositing = compositing

    @property
    def deepcompression(self):
        return self._deepcompression

    @deepcompression.setter
    def deepcompression(self, deepcompression):
        self._deepcompression = deepcompression

    @property
    def depth_planes(self):
        return self._depth_planes

    @depth_planes.setter
    def depth_planes(self, depth_planes):
        self._depth_planes = depth_planes

    @property
    def disable_deep_image(self):
        """Disable deep image generation."""
        return self._disable_deep_image

    @disable_deep_image.setter
    def disable_deep_image(self, disable_deep_image):
        self._disable_deep_image = disable_deep_image

    @property
    def filename(self):
        """The deep image path to set."""
        return self._filename

    @filename.setter
    def filename(self, filename):
        self._filename = filename

    @property
    def mipmaps(self):
        return self._mipmaps

    @mipmaps.setter
    def mipmaps(self, mipmaps):
        self._mipmaps = mipmaps

    @property
    def ofsize(self):
        return self._ofsize

    @ofsize.setter
    def ofsize(self, ofsize):
        self._ofsize = ofsize

    @property
    def ofstorage(self):
        return self._ofstorage

    @ofstorage.setter
    def ofstorage(self, ofstorage):
        self._ofstorage = ofstorage

    @property
    def pzstorage(self):
        return self._pzstorage

    @pzstorage.setter
    def pzstorage(self, pzstorage):
        self._pzstorage = pzstorage

    @property
    def resolver(self):
        return self._resolver

    @resolver.setter
    def resolver(self, resolver):
        self._resolver = resolver

    @property
    def zbias(self):
        return self._zbias

    @zbias.setter
    def zbias(self, zbias):
        self._zbias = zbias

    # =========================================================================
    # STATIC METHODS
    # =========================================================================

    @staticmethod
    def build_arg_string(disable_deep_image=None, deep_all_passes=None,
                       deep_image_path=None, resolver=None, compositing=None,
                       compression=None, depth_planes=None, mipmaps=None,
                       ofsize=None, ofstorage=None, pzstorage=None, zbias=None
                      ):
        """Build an argument string for this operation."""
        args = []

        if disable_deep_image:
            args.append("--disable-deep-image")

        if deep_image_path is not None:
            args.append("--deep-image-path={}".format(deep_image_path))

        if resolver is not None:
            args.append("--deep-resolver={}".format(resolver))

        if compositing is not None:
            args.append("--deep-compositing={}".format(compositing))

        if compression is not None:
            args.append("--deep-compression={}".format(compression))

        if depth_planes is not None:
            if not isinstance(depth_planes, str):
                depth_planes = ",".join(depth_planes)

            args.append("--deep-depth-planes={}".format(depth_planes))

        if mipmaps is not None:
            args.append("--deep-mipmaps={}".format(mipmaps))

        if ofsize is not None:
            args.append("--deep-ofsize={}".format(ofsize))

        if ofstorage is not None:
            args.append("--deep-ofstorage={}".format(ofstorage))

        if pzstorage is not None:
            args.append("--deep-pzstorage={}".format(pzstorage))

        if zbias is not None:
            args.append("--deep-zbias={}".format(zbias))

        if deep_all_passes:
            args.append("--deep-all-passes")

        return " ".join(args)

    @staticmethod
    def register_parser_args(parser):
        """Register interested parser args for this operation."""
        parser.add_argument("--deep-image-path", dest="deep_image_path")

        parser.add_argument("--deep-all-passes", action="store_true", dest="deep_all_passes")

        parser.add_argument("--disable-deep-image", action="store_true", dest="disable_deep_image")

        parser.add_argument("--deep-resolver", choices=("camera", "shadow"), dest="deep_resolver")

        parser.add_argument("--deep-compression", type=int, dest="deep_compression")

        parser.add_argument("--deep-compositing", type=int, dest="deep_compositing")

        parser.add_argument("--deep-depth-planes", dest="deep_depth_planes")

        parser.add_argument("--deep-mipmaps", type=int, choices=(0, 1), dest="deep_mipmaps")

        parser.add_argument("--deep-ofsize", type=int, choices=(1, 3), dest="deep_ofsize")

        parser.add_argument(
            "--deep-ofstorage",
            choices=("real16", "real32", "real64"),
            dest="deep_ofstorage"
        )

        parser.add_argument(
            "--deep-pzstorage",
            choices=("real16", "real32", "real64"),
            dest="deep_pzstorage"
        )

        parser.add_argument("--deep-zbias", type=float, dest="deep_zbias")

    # =========================================================================
    # METHODS
    # =========================================================================

    @log_filter
    def filterCamera(self):
        """Apply camera properties."""
        render_type = get_property("renderer:rendertype")

        if not self.all_passes and render_type != "beauty":
            logger.warning("Not a beauty render, skipping deepresolver")
            return

        if self.disable_deep_image:
            logger.info("Disabling deep resolver")
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
                    logger.error("Cannot set deepresolver: deep output is not enabled")

                    return

            # Modify the args to include any passed along options.
            self._modify_deep_args(deep_args)

            logger.debug(
                "Setting 'image:deepresolver': {}".format(" ".join([str(arg) for arg in deep_args]))
            )

            set_property("image:deepresolver", deep_args)

    def process_parsed_args(self, filter_args):
        """Process any of our interested arguments if they were passed."""
        if filter_args.disable_deep_image:
            self.disable_deep_image = True

        if filter_args.deep_all_passes:
            self.all_passes = True

        if filter_args.deep_image_path is not None:
            self.filename = filter_args.deep_image_path

        if filter_args.deep_resolver is not None:
            self.resolver = filter_args.deep_resolver

        if filter_args.deep_compositing is not None:
            self.compositing = filter_args.deep_compositing

        if filter_args.deep_compression is not None:
            self.deepcompression = filter_args.deep_compression

        if filter_args.deep_depth_planes is not None:
            self.depth_planes = filter_args.deep_depth_planes

        if filter_args.deep_mipmaps is not None:
            self.mipmaps = filter_args.deep_mipmaps

        if filter_args.deep_ofsize is not None:
            self.ofsize = filter_args.deep_ofsize

        if filter_args.deep_ofstorage is not None:
            self.ofstorage = filter_args.deep_ofstorage

        if filter_args.deep_pzstorage is not None:
            self.pzstorage = filter_args.deep_pzstorage

        if filter_args.deep_zbias is not None:
            self.zbias = filter_args.deep_zbias

    def should_run(self):
        """Only run if a target path was passed."""
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
                self.zbias is not None
            )
        )
