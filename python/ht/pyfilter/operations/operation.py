"""This module contains the base class for runnable PyFilter operations."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
from builtins import object
from functools import wraps
import logging

_logger = logging.getLogger(__name__)


# =============================================================================
# CLASSES
# =============================================================================


class PyFilterOperation(object):
    """Base class of operations for PyFilter.

    :param manager: The manager this operation is registered with.
    :type manager: ht.pyfilter.manager.PyFilterManager

    """

    def __init__(self, manager):
        self._data = {}
        self._manager = manager

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __repr__(self):
        return "<PyFilterOperation: {}>".format(self.__class__.__name__)

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def data(self):
        """dict: Data dictionary for sharing between stages and filter calls."""
        return self._data

    @property
    def manager(self):
        """ht.pyfilter.manager.PyFilterManager: Reference to the PyFilterManager
        this operation is registered with.

        """
        return self._manager

    # -------------------------------------------------------------------------
    # STATIC METHODS
    # -------------------------------------------------------------------------

    @staticmethod
    def build_arg_string(*args, **kwargs):
        """Build an argument string for this operation.

        :return: The constructed argument string.
        :rtype: str

        """
        pass

    @staticmethod
    def register_parser_args(parser):
        """Register interested parser args for this operation.

        :param parser: The argument parser to attach arguments to.
        :type parser: argparse.ArgumentParser.
        :return:

        """
        pass

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def process_parsed_args(self, filter_args):
        """Process any parsed args that the operation may be interested in.

        :param filter_args: The argparse namespace containing processed args.
        :type filter_args: argparse.Namespace
        :return:

        """
        pass

    def should_run(self):  # pylint: disable=no-self-use
        """Determine whether or not this filter should be run.

        :return: Whether or not this operation should run.
        :rtype: bool

        """
        return True


# =============================================================================
# FUNCTIONS
# =============================================================================


def log_filter_call(method_or_name):
    """Custom filter logging decorator.

    You can decorate each filter* method of a PyFilterOperation class to
    provide basic logging on call.

    If you pass in a string then the evaluated mantra property will be added to
    the output.

    :param method_or_name: A method or  property name.
    :type method_or_name: function or str
    :return: A wrapped function.
    :rtype: function

    """

    def decorator(func):  # pylint: disable=missing-docstring
        @wraps(func)
        def wrapper(*args, **kwargs):  # pylint: disable=missing-docstring
            func_name = func.__name__
            class_name = args[0].__class__.__name__

            msg = "{}.{}()".format(class_name, func_name)

            if isinstance(method_or_name, str):
                import mantra

                msg = "{} ({})".format(msg, mantra.property(method_or_name)[0])

            _logger.debug(msg)

            func(*args, **kwargs)

        return wrapper

    if callable(method_or_name):
        return decorator(method_or_name)

    return decorator
