"""This module provides functions to get and set Mantra render properties."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
from collections.abc import Iterable
import json
from typing import Any, List, Optional, Union


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _parse_string_for_bool(value: str) -> Union[bool, str]:
    """Process a string value, converting string booleans to real booleans.

    - Returns True if the value is 'True' or 'true'.
    - Returns False if the value is 'False' or 'false'.
    - Otherwise return the unaltered value.

    :param value: The value to parse.
    :return: A possible converted value.

    """
    if value.lower() == "false":
        return False

    if value.lower() == "true":
        return True

    return value


def _prep_value_to_set(value: Any) -> List:
    """Prepare a value into a form suitable for Mantra.

    :param value: The value to prepare.
    :return: The transformed values.

    """
    # Convert to empty list.
    if value is None:
        value = []

    # Convert to a list of a single string value.
    elif isinstance(value, str):
        value = [value]

    elif isinstance(value, dict):
        value = [json.dumps(value)]

    # If the value is not an iterable then convert it to a list.
    elif not isinstance(value, Iterable):
        value = [value]

    # The value is already a list/tuple.
    else:
        # Check all the values to see if any are dicts.
        if all([isinstance(val, dict) for val in value]):
            # If they are, try to convert them to strings.
            try:
                value = [json.dumps(val) for val in value]

            # In the event it is not possible we'll just continue on with
            # the data as-is.
            except (TypeError, ValueError):
                pass

    return value


def _transform_values(values: Optional[List[Any]]) -> Any:
    """Transform values from Mantra into more useful forms.

    :param values: Values to transform.
    :return: The transformed values.

    """
    if values is None:
        return None

    # The value is a single value (really a single value in a list)
    if len(values) == 1:
        value = values[0]

        if isinstance(value, str):
            # Try to decode the string as a json object.
            try:
                value = json.loads(value)

            # It can't be converted to an object so we'll process it manually.
            except ValueError:
                # Split the string.
                value_components = value.split()

                # If there are multiple values we want to build a
                # dictionary out of pairs.
                if len(value_components) > 2:
                    value = dict(tuple(zip(*[iter(value_components)] * 2)))

                # Not multiple values so perform additional processing.
                else:
                    value = _parse_string_for_bool(value)

    # The value is a multiple item list.
    else:
        # Try to convert all the items to json.
        try:
            value = [json.loads(val) for val in values]

        # If that is not possible, use the values as-is.
        except (TypeError, ValueError):
            value = values

    return value


# =============================================================================
# FUNCTIONS
# =============================================================================


def get_property(name: str) -> Any:
    """Get a property value.

    :param name: The property name.
    :return: The value.

    """
    import mantra

    values = mantra.property(name)

    return _transform_values(values)


def set_property(name: str, value: Any):
    """Set a property value.

    :param name: The property name.
    :param value: The value to set.
    :return:

    """
    import mantra

    value = _prep_value_to_set(value)

    mantra.setproperty(name, value)
