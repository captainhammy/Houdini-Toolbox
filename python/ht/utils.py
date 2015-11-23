"""This module contains utility functions for the ht package.

Synopsis
--------

Functions:
    convertFromUnicode
	Convert any unicode members to normal strings.

"""
__author__ = "Graham Thompson"
__email__ = "captainhammy@gmail.com"

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "convertFromUnicode",
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

