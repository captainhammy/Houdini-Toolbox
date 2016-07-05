"""This script is run by Mantra to execute custom Python filtering of IFDs
before, during and after rendertime.

For more information, please see:
    http://www.sidefx.com/docs/houdini12.5/rendering/python

"""
__author__ = "Graham Thompson"
__email__ = "captainhammy@gmail.com"

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import logging

# Houdini Imports
import mantra

# Houdini Toolbox Imports
import ht.pyfilter.parser

# =============================================================================
# CONSTANTS
# =============================================================================

# Global map of all filter properties.
PROPERTIES = {}

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(asctime)s - %(filename)s:%(lineno)d - %(message)s",
    datefmt="%H:%M:%S %Y-%m-%d"
)

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
    logging.info("filterCamera")
    ht.pyfilter.parser.applyProperties(PROPERTIES, "camera")


def filterEndRender():
    """Perform actions just after the image has been rendered.

    Raises:
        N/A

    Returns:
        None

    """
    logging.info("filterEndRender")


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
    logging.info("filterError")
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
    logging.info("filterFog ({})".format(mantra.property("object:name")[0]))
    ht.pyfilter.parser.applyProperties(PROPERTIES, "fog")


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
    logging.info("filterGeometry")
    ht.pyfilter.parser.applyProperties(PROPERTIES, "geometry")


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
    logging.info("filterInstance ({})".format(mantra.property("object:name")[0]))
    ht.pyfilter.parser.applyProperties(PROPERTIES, "instance")


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
    logging.info("filterLight ({})".format(mantra.property("object:name")[0]))
    ht.pyfilter.parser.applyProperties(PROPERTIES, "light")


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
    logging.info("filterMaterial")
    ht.pyfilter.parser.applyProperties(PROPERTIES, "material")


def filterPlane():
    """Change query and modify image plane properties.

    Raises:
        N/A

    Returns:
        None

    """
    variable = mantra.property("plane:variable")[0]
    channel = mantra.property("plane:channel")[0]

    if variable == channel:
        logging.info("filterPlane ({})".format(variable))
    else:
        logging.info("filterPlane ({} -> {})".format(variable, channel))

    ht.pyfilter.parser.applyProperties(PROPERTIES, "plane")


def filterQuit():
    """Perform actions just before Mantra quits.

    Raises:
        N/A

    Returns:
        None

    """
    logging.info("filterQuit")


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
    logging.info("filterRender")
    ht.pyfilter.parser.applyProperties(PROPERTIES, "render")


def main():
    """Build the property information.

    Raises:
        N/A

    Returns:
        None

    """
    # Build the property information from the command line.
    PROPERTIES.update(ht.pyfilter.parser.buildPropertyInformation())

if __name__ == "__main__":
    main()

