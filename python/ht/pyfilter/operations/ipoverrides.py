"""This module contains an operation to apply overrides when rendering to ip."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import math

# Houdini Toolbox Imports
from ht.pyfilter.operations.operation import PyFilterOperation, log_filter_call
from ht.pyfilter.property import get_property, set_property
from ht.pyfilter.utils import build_pyfilter_command


# =============================================================================
# CLASSES
# =============================================================================

class IpOverrides(PyFilterOperation):
    """Operation to set overrides when rendering to ip.

    :param manager: The manager this operation is registered with.
    :type manager: ht.pyfilter.manager.PyFilterManager

    """

    def __init__(self, manager):
        super(IpOverrides, self).__init__(manager)

        self._bucket_size = None
        self._disable_aovs = False
        self._disable_blur = False
        self._disable_deep = False
        self._disable_displacement = False
        self._disable_matte = False
        self._disable_subd = False
        self._disable_tilecallback = False
        self._res_scale = None
        self._sample_scale = None
        self._transparent_samples = None

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def bucket_size(self):
        """int: Set the bucket rendering size."""
        return self._bucket_size

    @bucket_size.setter
    def bucket_size(self, bucket_size):
        self._bucket_size = bucket_size

    # -------------------------------------------------------------------------

    @property
    def disable_aovs(self):
        """bool: Disable all extra image planes."""
        return self._disable_aovs

    @disable_aovs.setter
    def disable_aovs(self, disable_aovs):
        self._disable_aovs = disable_aovs

    # -------------------------------------------------------------------------

    @property
    def disable_blur(self):
        """bool: Disable motion blur."""
        return self._disable_blur

    @disable_blur.setter
    def disable_blur(self, disable_blur):
        self._disable_blur = disable_blur

    # -------------------------------------------------------------------------

    @property
    def disable_deep(self):
        """bool: Disable deep image generation."""
        return self._disable_deep

    @disable_deep.setter
    def disable_deep(self, disable_deep):
        self._disable_deep = disable_deep

    # -------------------------------------------------------------------------

    @property
    def disable_displacement(self):
        """bool: Disable shader displacement."""
        return self._disable_displacement

    @disable_displacement.setter
    def disable_displacement(self, disable_displacement):
        self._disable_displacement = disable_displacement

    # -------------------------------------------------------------------------

    @property
    def disable_matte(self):
        """bool: Disable matte and phantom objects."""
        return self._disable_matte

    @disable_matte.setter
    def disable_matte(self, disable_matte):
        self._disable_matte = disable_matte

    # -------------------------------------------------------------------------

    @property
    def disable_subd(self):
        """bool: Disable subdivision."""
        return self._disable_subd

    @disable_subd.setter
    def disable_subd(self, disable_subd):
        self._disable_subd = disable_subd

    # -------------------------------------------------------------------------

    @property
    def disable_tilecallback(self):
        """bool: Disable any tile callback."""
        return self._disable_tilecallback

    @disable_tilecallback.setter
    def disable_tilecallback(self, disable_tilecallback):
        self._disable_tilecallback = disable_tilecallback

    # -------------------------------------------------------------------------

    @property
    def res_scale(self):
        """float: Amount to scale the image resolution by."""
        return self._res_scale

    @res_scale.setter
    def res_scale(self, res_scale):
        self._res_scale = res_scale

    # -------------------------------------------------------------------------

    @property
    def sample_scale(self):
        """float: Amount to scale the pixel sample count by."""
        return self._sample_scale

    @sample_scale.setter
    def sample_scale(self, sample_scale):
        self._sample_scale = sample_scale

    # -------------------------------------------------------------------------

    @property
    def transparent_samples(self):
        """int: Number of transparent samples."""
        return self._transparent_samples

    @transparent_samples.setter
    def transparent_samples(self, value):
        self._transparent_samples = value

    # -------------------------------------------------------------------------
    # STATIC METHODS
    # -------------------------------------------------------------------------

    @staticmethod
    def build_arg_string(res_scale=None, sample_scale=None, disable_blur=False,  # pylint: disable=arguments-differ
                         disable_aovs=False, disable_deep=False,
                         disable_displacement=False, disable_subd=False,
                         disable_tilecallback=False, bucket_size=None,
                         transparent_samples=None, disable_matte=False):
        """Build an argument string for this operation.

        :param res_scale: The resolution scale.
        :type res_scale: float
        :param sample_scale: The pixel sample scale.
        :type sample_scale: float
        :param disable_blur: Whether or not to disable blur.
        :type disable_blur: bool
        :param disable_aovs: Whether or not to disable any AOVs.
        :type disable_aovs: bool
        :param disable_deep: Whether or not to disable deep images.
        :type disable_deep: bool
        :param disable_displacement: Whether or not to disable displacement.
        :type disable_displacement: bool
        :param disable_subd: Whether or not to disable subdivision surfaces.
        :type disable_subd: bool
        :param disable_tilecallback: Whether or not to disable any tile callback.
        :type disable_tilecallback: bool
        :param bucket_size: Override the render bucket size.
        :type bucket_size: int
        :parameter transparent_samples: Override the number of transparent samples.
        :type transparent_samples: int
        :param disable_matte: Whether or not to disable matte and phantom objects.
        :type disable_matte: bool
        :return: The constructed argument string.
        :rtype: str

        """
        args = []

        if res_scale is not None:
            args.append("--ip-res-scale={}".format(res_scale))

        if sample_scale is not None:
            args.append("--ip-sample-scale={}".format(sample_scale))

        if disable_blur:
            args.append("--ip-disable-blur")

        if disable_aovs:
            args.append("--ip-disable-aovs")

        if disable_deep:
            args.append("--ip-disable-deep")

        if disable_displacement:
            args.append("--ip-disable-displacement")

        if disable_subd:
            args.append("--ip-disable-subd")

        if disable_tilecallback:
            args.append("--ip-disable-tilecallback")

        if bucket_size is not None:
            args.append("--ip-bucket-size={}".format(bucket_size))

        if transparent_samples is not None:
            args.append("--ip-transparent-samples={}".format(transparent_samples))

        if disable_matte:
            args.append("--ip-disable-matte")

        return " ".join(args)

    @staticmethod
    def register_parser_args(parser):
        """Register interested parser args for this operation.

        :param parser: The argument parser to attach arguments to.
        :type parser: argparse.ArgumentParser.
        :return:

        """
        parser.add_argument("--ip-res-scale", default=None, type=float, dest="ip_res_scale")

        parser.add_argument("--ip-sample-scale", default=None, type=float, dest="ip_sample_scale")

        parser.add_argument("--ip-disable-blur", action="store_true", dest="ip_disable_blur")

        parser.add_argument("--ip-disable-aovs", action="store_true", dest="ip_disable_aovs")

        parser.add_argument("--ip-disable-deep", action="store_true", dest="ip_disable_deep")

        parser.add_argument("--ip-disable-displacement", action="store_true", dest="ip_disable_displacement")

        parser.add_argument("--ip-disable-subd", action="store_true", dest="ip_disable_subd")

        parser.add_argument("--ip-disable-tilecallback", action="store_true", dest="ip_disable_tilecallback")

        parser.add_argument("--ip-disable-matte", action="store_true", dest="ip_disable_matte")

        parser.add_argument("--ip-bucket-size", nargs="?", default=None, type=int, dest="ip_bucket_size", action="store")

        parser.add_argument("--ip-transparent-samples", nargs="?", default=None, type=int, action="store", dest="ip_transparent_samples")

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    @log_filter_call
    def filterCamera(self):
        """Apply camera properties.

        :return:

        """
        if self.res_scale is not None:
            resolution = get_property("image:resolution")

            resolution = _scale_resolution(resolution, self.res_scale)

            set_property("image:resolution", resolution)

        if self.sample_scale is not None:
            samples = get_property("image:samples")

            samples = _scale_samples(samples, self.sample_scale)

            set_property("image:samples", samples)

        if self.bucket_size is not None:
            set_property("image:bucket", self.bucket_size)

        # Set the blurquality values to 0 to disable blur.
        if self.disable_blur:
            set_property("renderer:blurquality", 0)
            set_property("renderer:rayblurquality", 0)

        # Set the deepresolver to have no args, thus stopping it from running.
        if self.disable_deep:
            set_property("image:deepresolver", [])

        if self.disable_tilecallback:
            set_property("render:tilecallback", "")

        if self.transparent_samples:
            set_property("image:transparentsamples", self.transparent_samples)

    @log_filter_call
    def filterInstance(self):
        """Modify object properties.

        :return:

        """
        if self.disable_displacement:
            set_property("object:displace", [])

        if self.disable_subd:
            set_property("object:rendersubd", 0)

        if self.disable_matte:
            if get_property("object:matte") or get_property("object:phantom"):
                set_property("object:renderable", False)

            elif get_property("object:surface") == "opdef:/Shop/v_matte":
                set_property("object:renderable", False)

    @log_filter_call
    def filterMaterial(self):
        """Modify material properties.

        :return:

        """
        if self.disable_displacement:
            set_property("object:displace", [])

    @log_filter_call
    def filterPlane(self):
        """Modify aov properties.

        :return:

        """
        # We can't disable the main image plane or Mantra won't render.
        if self.disable_aovs and get_property("plane:variable") != "Cf+Af":
            set_property("plane:disable", 1)

    def process_parsed_args(self, filter_args):
        """Process any parsed args that the operation may be interested in.

        :param filter_args: The argparse namespace containing processed args.
        :type filter_args: argparse.Namespace
        :return:

        """
        if filter_args.ip_res_scale is not None:
            self.res_scale = filter_args.ip_res_scale

        if filter_args.ip_sample_scale is not None:
            self.sample_scale = filter_args.ip_sample_scale

        self.disable_aovs = filter_args.ip_disable_aovs
        self.disable_blur = filter_args.ip_disable_blur
        self.disable_deep = filter_args.ip_disable_deep
        self.disable_displacement = filter_args.ip_disable_displacement
        self.disable_matte = filter_args.ip_disable_matte
        self.disable_subd = filter_args.ip_disable_subd
        self.disable_tilecallback = filter_args.ip_disable_tilecallback

        if filter_args.ip_bucket_size is not None:
            self.bucket_size = filter_args.ip_bucket_size

        if filter_args.ip_transparent_samples is not None:
            self.transparent_samples = filter_args.ip_transparent_samples

    def should_run(self):
        """Determine whether or not this filter should be run.

        This operation will run if we are rendering to ip and have something to set.

        :return: Whether or not this operation should run.
        :rtype: bool

        """
        if get_property("image:filename") != "ip":
            return False

        # Only enable the operation if something is set.
        return any(
            (
                self.res_scale,
                self.sample_scale,
                self.disable_aovs,
                self.disable_blur,
                self.disable_deep,
                self.disable_displacement,
                self.disable_matte,
                self.disable_subd,
                self.disable_tilecallback,
                self.bucket_size,
                self.transparent_samples,
            )
        )


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

def _scale_resolution(resolution, scale):
    """Scale a resolution value.

    :param resolution: The resolution values to scale.
    :type resolution: list(int)
    :return: The scaled resolution.
    :rtype: list(int)

    """
    return [int(round(value * scale)) for value in resolution]


def _scale_samples(samples, scale):
    """Scale a sample value, ensuring it remains >= 1.

    :param samples: The sample values to scale.
    :type samples: list(int)
    :return: The scale samples.
    :rtype: list(int)

    """
    return [max(1, int(math.ceil(value * scale))) for value in samples]


# =============================================================================
# FUNCTIONS
# =============================================================================

def build_arg_string_from_node(node):
    """Build an argument string from a Mantra node.

    :param node: The node to build an arg string from.
    :type node: hou.RopNode
    :return: An argument string.
    :rtype: str

    """
    if not node.evalParm("enable_ip_override"):
        return ""

    res_scale = None
    transparent_samples = None

    if node.evalParm("ip_override_camerares"):
        res_scale = node.evalParm("ip_res_fraction")

    if node.evalParm("ip_transparent"):
        transparent_samples = node.evalParm("ip_transparent_samples")

    return IpOverrides.build_arg_string(
        res_scale=res_scale,
        sample_scale=node.evalParm("ip_sample_scale"),
        disable_blur=node.evalParm("ip_disable_blur"),
        disable_aovs=node.evalParm("ip_disable_aovs"),
        disable_deep=node.evalParm("ip_disable_deep"),
        disable_displacement=node.evalParm("ip_disable_displacement"),
        disable_subd=node.evalParm("ip_disable_subd"),
        disable_tilecallback=node.evalParm("ip_disable_tilecallback"),
        bucket_size=node.evalParm("ip_bucket_size"),
        transparent_samples=transparent_samples,
        disable_matte=node.evalParm("ip_disable_matte")

    )


def build_pixel_sample_scale_display(node):
    """Build a label to display the adjusted pixel samples.

    :param node: The node to build the display for.
    :type node: hou.RopNode
    :return: The display scale.
    :rtype: str

    """
    samples = node.evalParmTuple("vm_samples")

    sample_scale = node.evalParm("ip_sample_scale")

    sx, sy = _scale_samples(samples, sample_scale)

    return "{}x{}".format(sx, sy)


def build_resolution_scale_display(node):
    """Build a label to display the adjusted image resolution.

    :param node: The node to build the display for.
    :type node: hou.RopNode
    :return: The display scale.
    :rtype: str

    """
    # Need to find a valid camera to get the resolution from it.
    camera = node.parm("camera").evalAsNode()

    # Nothing to do here.
    if camera is None:
        return ""

    # The resolution set on the camera.
    resolution = camera.evalParmTuple("res")

    # It's possible the Mantra ROP is overriding the resolution itself
    # so apply any ROP scaling first.
    if node.evalParm("override_camerares"):
        rop_res_scale = node.evalParm("res_fraction")

        # Explicitly setting the resolution so just use that.
        if rop_res_scale == "specific":
            resolution = node.evalParmTuple("res_override")

        else:
            resolution = _scale_resolution(resolution, float(rop_res_scale))

    res_scale = float(node.evalParm("ip_res_fraction"))

    # Scale based our override.
    resx, resy = _scale_resolution(resolution, res_scale)

    return "{}x{}".format(resx, resy)


def build_pyfilter_command_from_node(node):
    """Construct the mantra command with PyFilter.

    :param node: The node to build a command from.
    :type node: hou.RopNode
    :return: The filter command.
    :rtype: str

    """
    args = build_arg_string_from_node(node)

    cmd = build_pyfilter_command(args.split())

    return cmd


def set_mantra_command(node):
    """Set the soho_pipecmd parameter to something that will render with our
    custom script and settings.

    :param node: The node to set the command on.
    :type node: hou.RopNode
    :return:

    """
    cmd = "mantra `pythonexprs(\"__import__('ht.pyfilter.operations', globals(), locals(), ['ipoverrides']).ipoverrides.build_pyfilter_command_from_node(hou.pwd())\")`"

    node.parm("soho_pipecmd").set(cmd)
