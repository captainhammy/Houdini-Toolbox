"""This script is run by Mantra to execute custom Python filtering of IFDs
before, during and after rendertime.

For more information, please see:
    http://www.sidefx.com/docs/houdini15.0/rendering/python

"""
__author__ = "Graham Thompson"
__email__ = "captainhammy@gmail.com"

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Imports
import mantra

# Houdini Toolbox Imports
from ht.pyfilter.logger import logger
from ht.pyfilter.manager import PyFilterManager

# =============================================================================
# CONSTANTS
# =============================================================================

PYFILTER_MANAGER = None

# =============================================================================
# FUNCTIONS
# =============================================================================

def filterCamera():
    """Modify image related properties.

    Raises:
        N/A

    Returns:
        None

    Called just before the global properties are locked off for the render.
    This is usually prior to the declaration of any objects in the IFD.  If you
    change global properties after this, they probably will have no effect.

    Since mantra calls this function before any lights or instances are
    declared, you can set default light or instance properties here.  Mantra
    will apply any Instance/Light properties you set here to any objects which
    don't declare the property explicitly.

    """
    logger.info("filterCamera")

    PYFILTER_MANAGER.runFilters("filterCamera")


def filterCameraSegment():
    """Modify properties for a camera motion segment.

    Raises:
        N/A

    Returns:
        None

        Called just prior to the ray_end statement locking the settings for
        a camera motion segment.

    """
    logger.info("filterCameraSegment")

    PYFILTER_MANAGER.runFilters("filterCameraSegment")


def filterEndRender():
    """Perform actions just after the image has been rendered.

    Raises:
        N/A

    Returns:
        None

    """
    logger.info("filterEndRender")

    PYFILTER_MANAGER.runFilters("filterEndRender")


def filterError(level, message, prefix=""):
    """Process information, warning or error messages printed by Mantra.

    Args:
        level : (int)
            The verbosity level of the message.

        message : (str)
            The message from Mantra.

        prefix="" : (str)
            A prefix for the message.

    Raises:
        N/A

    Returns:
        bool
            Returning True will tell Mantra that the error has been handled by
            the filter method and mantra will not print out the message itself.

    This function allows you to disable the printing of messages.

    """
    logger.info("filterError")

    PYFILTER_MANAGER.runFilters("filterError")

    return False


def filterFog():
    """Modify fog related properties.

    Raises:
        N/A

    Returns:
        None

    Called just prior to the ray_end statement which locks off the settings for
    a fog object. The function can query fog: settings and possibly alter them.

    """
    logger.info("filterFog ({0})".format(mantra.property("object:name")[0]))

    PYFILTER_MANAGER.runFilters("filterFog")


def filterGeometry():
    """Modify geometry related properties.

    Raises:
        N/A

    Returns:
        None

    Called just prior to the ray_end statement which locks off a geometry
    object. This allows the program to query geometry: settings and possibly
    alter them.

    """
    logger.info("filterGeometry")

    PYFILTER_MANAGER.runFilters("filterGeometry")


def filterInstance():
    """Modify object related properties.

    Raises:
        N/A

    Returns:
        None

    Called just prior to the ray_end statement which locks off the settings for
    an instance object.  The function can query object: settings and possibly
    alter them.

    """
    logger.info("filterInstance ({0})".format(mantra.property("object:name")[0]))
    PYFILTER_MANAGER.runFilters("filterInstance")


def filterLight():
    """Modify light related properties.

    Raises:
        N/A

    Returns:
        None

    Called just prior to the ray_end statement which locks off the settings for
    a light object.  The function can query light: settings and possibly alter
    them.

    """
    logger.info("filterLight ({0})".format(mantra.property("object:name")[0]))

    PYFILTER_MANAGER.runFilters("filterLight")


def filterMaterial():
    """Modify material related properties.

    Raises:
        N/A

    Returns:
        None

    Mantra has material blocks which can be applied on a per-primitive basis.
    This function is called before a material is locked off. The function can
    add or change properties on the material.

    """
    logger.info("filterMaterial")

    PYFILTER_MANAGER.runFilters("filterMaterial")


def filterOutputAssets(assets):
    """Filter assets generated by Mantra.

    Args:
        assets : (dict)
            Dictionary of output asset information.

    Raises:
        N/A

    Returns:
        None

    Called after the render completes, and is passed a list of assets
    generated during the render.

    """
    logger.info("filterOutputAssets")

    PYFILTER_MANAGER.runFilters("filterOutputAssets")


def filterPlane():
    """Change query and modify image plane properties.

    Raises:
        N/A

    Returns:
        None

    """
    variable = mantra.property("plane:variable")[0]
    channel = mantra.property("plane:channel")[0]

    if variable == channel or channel == "":
        logger.info("filterPlane ({0})".format(variable))
    else:
        logger.info("filterPlane ({0} -> {1})".format(variable, channel))

    PYFILTER_MANAGER.runFilters("filterPlane")


def filterQuit():
    """Perform actions just before Mantra quits.

    Raises:
        N/A

    Returns:
        None

    """
    logger.info("filterQuit")

    PYFILTER_MANAGER.runFilters("filterQuit")


def filterRender():
    """Query render related properties.

    Raises:
        N/A

    Returns:
        None

    Called just before the ray_raytrace command.  It's not possible to change
    any properties at this time in the IFD processing.  However, for
    statistics or validation, it might be useful to have this method available.

    """
    logger.info("filterRender")

    PYFILTER_MANAGER.runFilters("filterRender")


def main():
    """Build the property information.

    Raises:
        N/A

    Returns:
        None

    """
    global PYFILTER_MANAGER

    PYFILTER_MANAGER = PyFilterManager()

# =============================================================================

if __name__ == "__main__":
    main()

