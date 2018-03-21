"""This module contains an operation to set the deep resolver path."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.pyfilter.logger import logger
from ht.pyfilter.operations.operation import PyFilterOperation, logFilter
from ht.pyfilter.property import getProperty, setProperty

# =============================================================================
# CLASSES
# =============================================================================


class SetDeepImage(PyFilterOperation):
    """Operation to modify deep image generation,

    """

    ARG_LIST = {
        "path": "-deep_image_path",
        "all_passes": "-deep_all_passes",
        "disable": "-disable-deep_image",
        "resolver": "-deep_deepresolver",
        "compression": "-deep_compression",
        "compositing": "-deep_compositing",
        "planes": "-deep_depth_planes",
        "mipmaps": "-deep_mipmaps",
        "ofsize": "-deep_ofsize",
        "ofstorage": "-deep_ofstorage",
        "pzstorage": "-deep_pzstorage",
        "zbias": "-deep_zbias",
    }

    def __init__(self, manager=None):
        super(SetDeepImage, self).__init__(manager=manager)

        self._all_passes = False
        self._compostiting = None
        self._deepcompression = None
        self._deepresolver = None
        self._depth_planes = None
        self._disable_deep_image = False
        self._filename = None
        self._mipmaps = None
        self._ofsize = None
        self._ofstorage = None
        self._pzstorage = None
        self._zbias = None

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _modifyDeepArgs(self, deep_args):
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
    def deepresolver(self):
        return self._deepresolver

    @deepresolver.setter
    def deepresolver(self, deepresolver):
        self._deepresolver = deepresolver

    @property
    def compositing(self):
        return self._compostiting

    @compositing.setter
    def compositing(self, compositing):
        self._compostiting = compositing

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
    def zbias(self):
        return self._zbias

    @zbias.setter
    def zbias(self, zbias):
        self._zbias = zbias


    # =========================================================================
    # STATIC METHODS
    # =========================================================================

    @staticmethod
    def buildArgString(disable_deep_image=None, deep_all_passes=None,
                       deep_image_path=None, deepresolver=None, compositing=None,
                       deepcompression=None, depth_planes=None, mipmaps=None,
                       ofsize=None, ofstorage=None, pzstorage=None, zbias=None
                      ):
        """Build an argument string for this operation."""
        args = []

        if disable_deep_image:
            args.append(SetDeepImage.ARG_LIST["disable"])

        if deep_all_passes:
            args.append(SetDeepImage.ARG_LIST["all_passes"])

        if deep_image_path is not None:
            args.append("{}={}".format(SetDeepImage.ARG_LIST["path"], deep_image_path))

        if deepresolver is not None:
            args.append("{}={}".format(SetDeepImage.ARG_LIST["resolver"], deepresolver))

        if compositing is not None:
            args.append("{}={}".format(SetDeepImage.ARG_LIST["compositing"], compositing))

        if deepcompression is not None:
            args.append("{}={}".format(SetDeepImage.ARG_LIST["compression"], deepcompression))

        if depth_planes is not None:
            if not isinstance(depth_planes, str):
                depth_planes = ",".join(depth_planes)

            args.append("{}={}".format(SetDeepImage.ARG_LIST["planes"], depth_planes))

        if mipmaps is not None:
            args.append("{}={}".format(SetDeepImage.ARG_LIST["mipmaps"], mipmaps))

        if ofsize is not None:
            args.append("{}={}".format(SetDeepImage.ARG_LIST["ofsize"], ofsize))

        if ofstorage is not None:
            args.append("{}={}".format(SetDeepImage.ARG_LIST["ofstorage"], ofstorage))

        if pzstorage is not None:
            args.append("{}={}".format(SetDeepImage.ARG_LIST["pzstorage"], pzstorage))

        if zbias is not None:
            args.append("{}={}".format(SetDeepImage.ARG_LIST["zbias"], zbias))

        return " ".join(args)

    @staticmethod
    def registerParserArgs(parser):
        """Register interested parser args for this operation."""
        parser.add_argument(SetDeepImage.ARG_LIST["path"])

        parser.add_argument(SetDeepImage.ARG_LIST["all_passes"], action="store_true")

        parser.add_argument(SetDeepImage.ARG_LIST["disable"], action="store_true")

        parser.add_argument(SetDeepImage.ARG_LIST["resolver"], choices=("camera", "shadow"))

        parser.add_argument(SetDeepImage.ARG_LIST["compression"], type=int)

        parser.add_argument(SetDeepImage.ARG_LIST["compositing"], type=int)

        parser.add_argument(SetDeepImage.ARG_LIST["planes"])

        parser.add_argument(SetDeepImage.ARG_LIST["mipmaps"], type=int, choices=(0, 1))

        parser.add_argument(SetDeepImage.ARG_LIST["ofsize"], type=int, choices=(1, 3))

        parser.add_argument(
            SetDeepImage.ARG_LIST["ofstorage"],
            choices=("real16", "real32", "real64")
        )

        parser.add_argument(
            SetDeepImage.ARG_LIST["pzstorage"],
            choices=("real16", "real32", "real64")
        )

        parser.add_argument(SetDeepImage.ARG_LIST["zbias"], type=float)

    # =========================================================================
    # METHODS
    # =========================================================================

    @logFilter
    def filterCamera(self):
        """Apply camera properties."""
        render_type = getProperty("renderer:rendertype")

        if not self.all_passes and render_type != "beauty":
            logger.warning("Not a beauty render, skipping deepresolver")
            return False

        if self.disable_deep_image:
            logger.info("Disabling deep resolver")
            setProperty("image:deepresolver", [])

        else:
            # Look for existing args.
            deep_args = getProperty("image:deepresolver")

            # If deep rendering is not enabled the args will be empty.
            if not deep_args:
                # If a resolver type and filename was passed then we will create
                # args for the resolver type to enable deep output.
                if self.deepresolver and self.filename:
                    deep_args = [self.deepresolver]

                # Log an error and abort.
                else:
                    logger.error("Cannot set deepresolver: deep output is not enabled")

                    return False

            # Modify the args to include any passed along options.
            self._modifyDeepArgs(deep_args)

            logger.debug(
                "Setting 'image:deepresolver': {}".format(" ".join([str(arg) for arg in deep_args]))
            )

            setProperty("image:deepresolver", deep_args)

        return True

    def processParsedArgs(self, filter_args):
        """Process any of our interested arguments if they were passed."""
        if filter_args.disable_deep_image:
            self.disable_deep_image = True

        if filter_args.deep_all_passes:
            self.all_passes = True

        if filter_args.deep_image_path is not None:
            self.filename = filter_args.deep_image_path

        if filter_args.deep_deepresolver is not None:
            self.deepresolver = filter_args.deep_deepresolver

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

    def shouldRun(self):
        """Only run if a target path was passed."""
        if self.disable_deep_image:
            return True

        return any(
            (
                #self.all_passes (only controls application behavior)
                self.filename,
                self.deepresolver,
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
