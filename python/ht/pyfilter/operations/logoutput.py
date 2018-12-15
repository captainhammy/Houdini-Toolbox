"""This module contains an operation to log Mantra output."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import logging

# Houdini Toolbox Imports
from ht.pyfilter.operations.operation import PyFilterOperation

# =============================================================================
# CLASSES
# =============================================================================

class LogOutput(PyFilterOperation):
    """Operation to log Mantra output.

    :param manager: The manager this operation is registered with.
    :type manager: ht.pyfilter.manager.PyFilterManager

    """

    def __init__(self, manager):
        super(LogOutput, self).__init__(manager)

        # Get our custom mantra logger setup via config.
        self._logger = logging.getLogger("mantra")

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def logger(self):
        """logging.Logger: The logger to use when outputting."""
        return self._logger

    # =========================================================================
    # METHODS
    # =========================================================================

    def filterError(self, level, message, prefix):
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

        for message in messages:
            # Verbosity of 0 is always for errors.
            if level == 0:
                self.logger.error(message)

            # Mantra also only seems to set the prefix if the message is an
            # error/warning.
            elif prefix:
                self.logger.warning(message)

            # Default verbosity level so we'll call that info.
            elif level == 1:
                self.logger.info(message)

            # Flag as debug.
            else:
                self.logger.debug(message)

        # Return True to let Mantra know that we handled message output so it
        # will not output it itself.
        return True
