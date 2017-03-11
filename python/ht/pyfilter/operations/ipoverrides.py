"""This module contains an operation to apply overrides when rendering to ip.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import math

# Houdini Toolbox Imports
from ht.pyfilter.logger import logger
from ht.pyfilter.operations.operation import PyFilterOperation, logFilter
from ht.pyfilter.property import setProperty

# =============================================================================
# CLASSES
# =============================================================================

class IpOverrides(PyFilterOperation):
    """Operation to set overrides when rendering to ip."""

    def __init__(self, manager):
        super(IpOverrides, self).__init__(manager)

        self._disable_aovs = False
        self._disable_blur = False
        self._disable_deep = False
        self._disable_displacement = False
        self._enabled = False
        self._res_scale = 1.0
        self._sample_scale = None

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def disable_aovs(self):
        """Disable all extra image planes."""
        return self._disable_aovs

    @disable_aovs.setter
    def disable_aovs(self, disable_aovs):
        self._disable_aovs = disable_aovs

    # =========================================================================

    @property
    def disable_blur(self):
        """Disable motion blur."""
        return self._disable_blur

    @disable_blur.setter
    def disable_blur(self, disable_blur):
        self._disable_blur = disable_blur

    # =========================================================================

    @property
    def disable_deep(self):
        """Disable deep image generation."""
        return self._disable_deep

    @disable_deep.setter
    def disable_deep(self, disable_deep):
        self._disable_deep = disable_deep

    # =========================================================================

    @property
    def disable_displacement(self):
        """Disable shader displacement."""
        return self._disable_displacement

    @disable_displacement.setter
    def disable_displacement(self, disable_displacement):
        self._disable_displacement = disable_displacement

    # =========================================================================

    @property
    def enabled(self):
        """Is this filter operation enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled

    # =========================================================================

    @property
    def res_scale(self):
        """Amount to scale the image resolution by."""
        return self._res_scale

    @res_scale.setter
    def res_scale(self, res_scale):
        self._res_scale = res_scale

    # =========================================================================

    @property
    def sample_scale(self):
        """Amount to scale the pixel sample count by."""
        return self._sample_scale

    @sample_scale.setter
    def sample_scale(self, sample_scale):
        self._sample_scale = sample_scale

    # =========================================================================
    # STATIC METHODS
    # =========================================================================

    @staticmethod
    def buildArgString(res_scale=None, sample_scale=None, disable_blur=False,
                       disable_aovs=False, disable_deep=False,
                       disable_displacement=False):
        """Construct an argument string based on values for this filter."""
        args = []

        if res_scale is not None:
            args.append("-ip_resscale {}".format(res_scale))

        if sample_scale is not None:
            args.append("-ip_samplescale {}".format(sample_scale))

        if disable_blur:
            args.append("-ip_disableblur")

        if disable_aovs:
            args.append("-ip_disableaovs")

        if disable_deep:
            args.append("-ip_disabledeep")

        if disable_displacement:
            args.append("-ip_disabledisplacement")

        return " ".join(args)

    @staticmethod
    def registerParserArgs(parser):
        """Register interested parser args for this operation."""
        parser.add_argument(
            "-ip_override",
            action="store_true",
            help="Enable modification of settings for ip."
        )

        parser.add_argument(
            "-ip_resscale",
            nargs="?",
            default=None,
            action="store",
            help="Scale image resolution by this value."
        )

        parser.add_argument(
            "-ip_samplescale",
            nargs="?",
            default=None,
            action="store",
            help="Scale pixel samples by this value."
        )

        parser.add_argument(
            "-ip_disableblur",
            action="store_true",
            help="Disable motion blur"
        )

        parser.add_argument(
            "-ip_disableaovs",
            action="store_true",
            help="Disable aovs"
        )

        parser.add_argument(
            "-ip_disabledeep",
            action="store_true",
            help="Disable deep output"
        )

        parser.add_argument(
            "-ip_disabledisplacement",
            action="store_true",
            help="Disable shader displacement"
        )

    # =========================================================================
    # METHODS
    # =========================================================================

    @logFilter
    def filterCamera(self):
        """Apply camera properties."""
        import mantra

        if self.res_scale is not None:
            resolution = mantra.property("image:resolution")

            new_res = [int(round(val * self.res_scale)) for val in resolution]

            setProperty("image:resolution", new_res)

        if self.sample_scale is not None:
            samples = mantra.property("image:samples")

            # Need to make sure our values are at least a minimum of 1.
            new_samples = [max(1, int(math.ceil(val * self.sample_scale))) for val in samples]

            setProperty("image:samples", new_samples)

        # Set the blurquality values to 0 to disable blur.
        if self.disable_blur:
            setProperty("renderer:blurquality", 0)
            setProperty("renderer:rayblurquality", 0)

        # Set the deepresolver to have no args, thus stopping it from running.
        if self.disable_deep:
            setProperty("image:deepresolver", [])

    @logFilter
    def filterInstance(self):
        """Modify object properties."""
        import mantra

        if self.disable_displacement:
            setProperty("object:displace", [])

    @logFilter
    def filterMaterial(self):
        """Modify material properties."""
        import mantra

        if self.disable_displacement:
            setProperty("object:displace", [])

    @logFilter
    def filterPlane(self):
        """Modify aov properties."""
        import mantra

        # We can't disable the main image plane or Mantra won't render.
        if self.disable_aovs and mantra.property("plane:variable")[0] != "Cf+Af":
            setProperty("plane:disable", 1)

    def processParsedArgs(self, filter_args):
        """Process any of our interested arguments if they were passed."""
        if filter_args.ip_resscale is not None:
            self.res_scale = float(filter_args.ip_resscale)

        if filter_args.ip_samplescale is not None:
            self.sample_scale = float(filter_args.ip_samplescale)

        self.disable_aovs = filter_args.ip_disableaovs
        self.disable_blur = filter_args.ip_disableblur
        self.disable_deep = filter_args.ip_disabledeep
        self.disable_displacement = filter_args.ip_disabledisplacement

        # Only enable ourself if something is set.
        if self.res_scale or self.disable_blur or self.sample_scale \
            or self.disable_aovs or self.disable_deep:

            self.enabled = True

    def shouldRun(self):
        """Only run if we are enabled AND rendering to ip."""
        import mantra

        return self.enabled and mantra.property("image:filename")[0] == "ip"

# =============================================================================
# FUNCTIONS
# =============================================================================

def buildArgStringFromNode(node):
    """Build an argument string from a Mantra node."""
    if not node.evalParm("enable_ip_override"):
        return ""

    res_scale = None

    if node.evalParm("ip_override_camerares"):
        res_scale = node.evalParm("ip_res_fraction")

    return IpOverrides.buildArgString(
        res_scale=res_scale,
        sample_scale=node.evalParm("ip_sample_scale"),
        disable_blur=node.evalParm("ip_disable_blur"),
        disable_aovs=node.evalParm("ip_disable_aovs"),
        disable_deep=node.evalParm("ip_disable_deep"),
        disable_displacement=node.evalParm("ip_disable_displacement"),
    )


def buildPixleSampleScaleDisplay(node):
    """Build a label to display the adjusted pixel samples."""
    sx, sy = node.evalParmTuple("vm_samples")

    sample_scale = node.evalParm("ip_sample_scale")

    sx = max(1, int(math.ceil(sx * sample_scale)))
    sy = max(1, int(math.ceil(sy * sample_scale)))

    return "{}x{}".format(sx, sy)


def buildResolutionScaleDisplay(node):
    """Build a label to display the adjusted image resolution."""
    # Need to find a valid camera to get the resolution from it.
    camera_path = node.evalParm("camera")
    camera = node.node(camera_path)

    # Nothing to do here.
    if camera is None:
        return ""

    # The resolution set on the camera.
    resx, resy = camera.evalParmTuple("res")

    # It's possible the Mantra ROP is overriding the resolution itself
    # so apply any ROP scaling first.
    if node.evalParm("override_camerares"):
        rop_res_scale = node.evalParm("res_fraction")

        # Explicitly setting the resolution so just use that.
        if rop_res_scale == "specific":
            resx, resy = node.evalParmTuple("res_override")

        else:
            resx = int(round(resx * float(rop_res_scale)))
            resy = int(round(resy * float(rop_res_scale)))


    res_scale = float(node.evalParm("ip_res_fraction"))

    # Scale based our override.
    resx = int(round(resx * res_scale))
    resy = int(round(resy * res_scale))

    return "{}x{}".format(resx, resy)


def buildPyFilterCommand(node):
    """Construct the mantra command with PyFilter."""
    import hou

    try:
        script_path = hou.findFile("pyfilter/customPyFilter.py")

    # If we can't find the script them log an error and return nothing.
    except hou.OperationFailed:
        logger.error("Could not find pyfilter/customPyFilter.py")

        return ""

    # Build the wrapped -P command with out script and arg string.
    cmd = '-P "{} {}"'.format(
        script_path,
        buildArgStringFromNode(node)
    )

    return cmd


def setMantraCommand(node):
    """Set the soho_pipecmd parameter to something that will render with our
    custom script and settings.

    """
    cmd = "mantra `pythonexprs(\"__import__('ht.pyfilter.operations', globals(), locals(), ['ipoverrides']).ipoverrides.buildPyFilterCommand(hou.pwd())\")`"

    node.parm("soho_pipecmd").set(cmd)

