"""This module contains utility functions for the ht package."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import contextlib
import time

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "convertFromUnicode",
    "timer",
    "updateMode",
]

# =============================================================================
# FUNCTIONS
# =============================================================================

def convertFromUnicode(data):
    """Convert any unicode members to normal strings.

    Args:
	data : (object)
              An object to convert.  This can be a dictionary, list, string or
	      raw value.

    Raises:
	N/A

    Returns:
	object
	    The object with any unicode members converted to strings.

    """
    # If the data is a dictionary we need to convert the key/value pairs
    # and return a new dictionary.
    if isinstance(data, dict):
        return {convertFromUnicode(key): convertFromUnicode(value)
                for key, value in data.iteritems()}

        # Python 2.6 compatible workaround for no dictionary comprehensions.
#        return dict(
#            [
#                (convertFromUnicode(key), convertFromUnicode(value))
#                 for key, value in data.iteritems()
#            ]
#        )

    # Convert any elements in a list.
    elif isinstance(data, list):
        return [convertFromUnicode(element) for element in data]

    # The data is a unicode string, so encode it to a regular one.
    elif isinstance(data, unicode):
        return data.encode('utf-8')

    # Return the untouched data.
    return data


@contextlib.contextmanager
def timer(label=None):
    """Context manager for outputting timing information.

>>> with ht.utils.timer("sleeping"):
...     time.sleep(2)
...
sleeping - 2.00206804276

    """
    # Start time.
    t = time.time()

    try:
        yield

    finally:
        duration = time.time() - t

        if label is not None:
            print "{} - {}".format(label, duration)
        else:
            print duration


@contextlib.contextmanager
def updateMode(update_mode):
    """Context manager for setting the interface's update mode.

    update_mode should be one of hou.updateMode

    """
    import hou

    # Get the current update mode so it can be restored.
    current = hou.updateModeSetting()

    # Set the desired mode.
    hou.ui.setUpdateMode(mode)

    try:
        yield

    finally:
        # Restore the update mode.
        hou.ui.setUpdateMode(current)

