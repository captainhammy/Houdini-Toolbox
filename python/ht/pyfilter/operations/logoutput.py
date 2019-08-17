"""This module contains an operation to log Mantra output."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import logging

# Houdini Toolbox Imports
from ht.pyfilter.operations.operation import PyFilterOperation

# Name the _logger 'mantra' since we're logging Mantra output.
_logger = logging.getLogger("mantra")


# =============================================================================
# CLASSES
# =============================================================================

class LogOutput(PyFilterOperation):
    """Operation to log Mantra output."""

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def filterError(self, level, message, prefix):  # pylint: disable=no-self-use
        """Handle message outputting.

        :param level: The output level.
        :type level: int
        :param message: The output message.
        :type message: str
        :param prefix: Message prefix.
        :type prefix: str
        :return: Return True to indicate that we handled the output so Mantra
                 will not.
        :rtype: bool

        """
        # Split message by newlines so we can log each line.
        messages = message.split('\n')

        for msg in messages:
            # Verbosity of 0 is always for errors.
            if level == 0:
                _logger.error(msg)

            # Mantra also only seems to set the prefix if the message is an
            # error/warning.
            elif prefix:
                _logger.warning(msg)

            # Default verbosity level so we'll call that info.
            elif level == 1:
                _logger.info(msg)

            # Flag as debug.
            else:
                _logger.debug(msg)

        # Return True to let Mantra know that we handled message output so it
        # will not output it itself.
        return True
