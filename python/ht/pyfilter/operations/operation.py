"""This module contains the base class for runnable PyFilter operations."""

__author__ = "Graham Thompson"
__email__ = "captainhammy@gmail.com"

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
from functools import wraps

# Houdini Toolbox Imports
from ht.pyfilter.logger import logger

# =============================================================================
# CLASSES
# =============================================================================

class PyFilterOperation(object):
    """Base class of operations for PyFilter."""

    def __init__(self, manager):
        self._data = {}
        self._manager = manager

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __repr__(self):
        return "<PyFilterOperation: {}>".format(
            self.__class__.__name__
        )

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def data(self):
        """Data dictionary for sharing between stages and filter calls."""
        return self._data

    @property
    def manager(self):
        """Reference to the PyFilterManager this operation is registered with.

        """
        return self._manager

    # =========================================================================
    # STATIC METHODS
    # =========================================================================

    @staticmethod
    def buildArgString(*args, **kwargs):
        pass

    @staticmethod
    def registerParserArgs(parser):
        """Register any argument parser args this filter cares about."""
        pass

    # =========================================================================
    # METHODS
    # =========================================================================

    def processParsedArgs(filter_args):
        """Process any parsed args that the operation may be interested in."""
        pass

    def shouldRun(self):
        """Determine whether or not this filter should be run."""
        return True

# =============================================================================
# FUNCTIONS
# =============================================================================

def logFilter(method_or_name):
    """Custom filter logging decorator.

    You can decorate each filter* method of a PyFilterOperation class to
    provide basic logging on call.

    """
    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            class_name = args[0].__class__.__name__

            msg = "{}.{}()".format(class_name, func_name)

            if isinstance(method_or_name, str):
                import mantra

                msg = "{} ({})".format(
                    msg,
                    mantra.property(method_or_name)[0]
                )

            logger.debug(msg)

            func(*args, **kwargs)

        return wrapper

    if callable(method_or_name):
        return decorator(method_or_name)

    return decorator

