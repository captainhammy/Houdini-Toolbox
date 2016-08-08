"""This module contains a class for custom text output."""

# =============================================================================
# CLASSES
# =============================================================================


class ShellOutput(object):
    """A simple class for outputting styled text to a shell.

    This class contains a number of static methods that can be used to wrap
    text in ANSI compatible coloring tags.

    """

    # =========================================================================
    # METHODS
    # =========================================================================

    @staticmethod
    def black(value):
        """Color the text black."""
        return "\x1b[0;30m{}\x1b[0;m".format(value)

    @staticmethod
    def blue(value):
        """Color the text blue."""
        return "\x1b[1;34m{}\x1b[0;m".format(value)

    @staticmethod
    def bold(value):
        """Make the text bold."""
        return "\x1b[0;1m{}\x1b[0;m".format(value)

    @staticmethod
    def cyan(value):
        """Color the text cyan."""
        return "\x1b[1;36m{}\x1b[0;m".format(value)

    @staticmethod
    def darkblue(value):
        """Color the text dark blue."""
        return "\x1b[0;34m{}\x1b[0;m".format(value)

    @staticmethod
    def darkcyan(value):
        """Color the text dark cyan."""
        return "\x1b[0;36m{}\x1b[0;m".format(value)

    @staticmethod
    def darkgreen(value):
        """Color the text dark green."""
        return "\x1b[0;32m{}\x1b[0;m".format(value)

    @staticmethod
    def darkmagenta(value):
        """Color the text dark magenta."""
        return "\x1b[0;35m{}\x1b[0;m".format(value)

    @staticmethod
    def darkred(value):
        """Color the text dark red."""
        return "\x1b[0;31m{}\x1b[0;m".format(value)

    @staticmethod
    def darkwhite(value):
        """Color the text dark white."""
        return "\x1b[0;37m{}\x1b[0;m".format(value)

    @staticmethod
    def darkyellow(value):
        """Color the text dark yellow."""
        return "\x1b[0;33m{}\x1b[0;m".format(value)

    @staticmethod
    def green(value):
        """Color the text green."""
        return "\x1b[1;32m{}\x1b[0;m".format(value)

    @staticmethod
    def grey(value):
        """Color the text grey."""
        return "\x1b[1;30m{}\x1b[0;m".format(value)

    @staticmethod
    def magenta(value):
        """Color the text magentra."""
        return "\x1b[1;35m{}\x1b[0;m".format(value)

    @staticmethod
    def red(value):
        """Color the text red."""
        return "\x1b[1;31m{}\x1b[0;m".format(value)

    @staticmethod
    def white(value):
        """Color the text white."""
        return "\x1b[1;37m{}\x1b[0;m".format(value)

    @staticmethod
    def yellow(value):
        """Color the text yellow."""
        return "\x1b[1;33m{}\x1b[0;m".format(value)

