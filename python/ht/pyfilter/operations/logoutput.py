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

    def filter_error( # pylint: disable=no-self-use
        self, level: int, message: str, prefix: str
    ) -> bool:
        """Handle message outputting.

        :param level: The output level.
        :param message: The output message.
        :param prefix: Message prefix.
        :return: Return True to indicate that we handled the output so Mantra will not.

        """
        # Split message by newlines so we can log each line.
        messages = message.split("\n")

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
