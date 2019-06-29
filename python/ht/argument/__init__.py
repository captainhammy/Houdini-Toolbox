"""This module contains a custom version of argparse.ArgumentParser."""

# =============================================================================
# Import
# =============================================================================

# Python Imports
import argparse


# =============================================================================
# CLASSES
# =============================================================================

class ArgumentParser(argparse.ArgumentParser):
    """HoudiniToolbox version of the standard Python argument parser.

    This custom parser implements a future Python version patch that allows
    the disabling of argument abbreviations.  It also overrides the default
    help flags.

    See the Python argparse documentation for details:

    http://docs.python.org/library/argparse.html

    """

    def __init__(self, description=None, epilog=None, add_help=True, allow_abbrev=True, *args, **kwargs):  # pylint: disable=keyword-arg-before-vararg
        # Construct the base ArgumentParser object.  We don't want to allow
        # help since it will use flags we don't want.
        super(ArgumentParser, self).__init__(
            add_help=False,
            description=description,
            epilog=epilog,
            *args,
            **kwargs
        )

        # Store abbreviation information.
        self.allow_abbrev = allow_abbrev

        # Add help using our own flags.
        if add_help:
            self.add_argument(
                "-help", "--help",
                action="help",
                default=argparse.SUPPRESS,
                help="show this help message and exit"
            )

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _parse_optional(self, arg_string):  # pylint: disable=too-many-return-statements
        """Parse optional arguments."""
        # if it's an empty string, it was meant to be a positional
        if not arg_string:
            return None

        # if it doesn't start with a prefix, it was meant to be positional
        if not arg_string[0] in self.prefix_chars:
            return None

        # if the option string is present in the parser, return the action
        if arg_string in self._option_string_actions:
            action = self._option_string_actions[arg_string]
            return action, arg_string, None

        # if it's just a single character, it was meant to be positional
        if len(arg_string) == 1:
            return None

        # if the option string before the "=" is present, return the action
        if '=' in arg_string:
            option_string, explicit_arg = arg_string.split('=', 1)
            if option_string in self._option_string_actions:
                action = self._option_string_actions[option_string]
                return action, option_string, explicit_arg

        # http://bugs.python.org/issue14910
        if self.allow_abbrev:
            # search through all possible prefixes of the option string
            # and all actions in the parser for possible interpretations
            option_tuples = self._get_option_tuples(arg_string)

            # if multiple actions match, the option string was ambiguous
            if len(option_tuples) > 1:
                options = ', '.join(
                    [option_string for action, option_string, explicit_arg in option_tuples]
                )
                tup = arg_string, options
                self.error('ambiguous option: %s could match %s' % tup)

            # if exactly one action matched, this segmentation is good,
            # so return the parsed action
            elif len(option_tuples) == 1:
                option_tuple, = option_tuples  # pylint: disable=unbalanced-tuple-unpacking
                return option_tuple

        # if it was not found as an option, but it looks like a negative
        # number, it was meant to be positional
        # unless there are negative-number-like options
        if self._negative_number_matcher.match(arg_string):
            if not self._has_negative_number_optionals:
                return None

        # if it contains a space, it was meant to be a positional
        if ' ' in arg_string:
            return None

        # it was meant to be an optional but there is no such option
        # in this parser (though it might be a valid option in a sub-parser)
        return None, arg_string, None
