"""Test the ht.pyfilter.property module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import json

# Third Party Imports
from mock import MagicMock, patch

# Houdini Toolbox Imports
from ht.pyfilter import property as prop


# =============================================================================
# CLASSES
# =============================================================================

class Test__parse_string_for_bool(object):
    """Test ht.pyfilter.property._parse_string_for_bool."""

    def test_false(self):
        assert not prop._parse_string_for_bool("False")
        assert not prop._parse_string_for_bool("false")

    def test_true(self):
        assert prop._parse_string_for_bool("True")
        assert prop._parse_string_for_bool("true")

    def test_passthrough(self):
        assert prop._parse_string_for_bool("test") == "test"


class Test__prep_value_to_set(object):
    """Test ht.pyfilter.property._prep_value_to_set."""

    def test_None(self):
        result = prop._prep_value_to_set(None)

        assert result == []

    def test_str(self):
        value = "value"

        result = prop._prep_value_to_set(value)

        assert result == [value]

    def test_unicode(self):
        value = u"value"

        result = prop._prep_value_to_set(value)

        assert result == [value]

    def test_dict(self):
        value = {
            "key1": "value1",
            "key2": "value2",
        }

        result = prop._prep_value_to_set(value)

        expected = json.dumps(value)

        assert result == [expected]

    def test_non_iterable(self):
        value = 123

        result = prop._prep_value_to_set(value)

        assert result == [value]

    def test_list_of_dicts(self):
        dict1 = {
            "key1": "value1",
            "key2": "value2",
        }

        value = [dict1]

        result = prop._prep_value_to_set(value)

        expected = json.dumps(dict1)

        assert result == [expected]

    @patch("ht.pyfilter.property.json.dumps")
    def test_list_of_dicts_TypeError(self, mock_dumps):
        mock_dumps.side_effect = TypeError
        dict1 = {
            "key1": "value1",
            "key2": "value2",
        }

        value = [dict1]

        result = prop._prep_value_to_set(value)

        assert result == value

    @patch("ht.pyfilter.property.json.dumps")
    def test_list_of_dicts_ValueError(self, mock_dumps):
        mock_dumps.side_effect = ValueError
        dict1 = {
            "key1": "value1",
            "key2": "value2",
        }

        value = [dict1]

        result = prop._prep_value_to_set(value)

        assert result == value

    def test_list_of_non_dicts(self):
        dict1 = {
            "key1": "value1",
            "key2": "value2",
        }

        value = [dict1, 3]

        result = prop._prep_value_to_set(value)

        assert result == value


class Test__transform_values(object):
    """Test ht.pyfilter.property._transform_values."""

    def test_None(self):
        result = prop._transform_values(None)

        assert result is None

    def test_single_json_string(self):
        expected = 123

        value = json.dumps(expected)

        result = prop._transform_values([value])

        assert result == expected

    def test_single_string_json(self):
        expected = 123

        value = json.dumps(expected)

        result = prop._transform_values([value])

        assert result == expected

    def test_single_string_non_json_dict(self):
        expected = {"comp1": "comp2", "comp3": "comp4"}

        result = prop._transform_values(["comp1 comp2 comp3 comp4"])

        assert result == expected

    @patch("ht.pyfilter.property._parse_string_for_bool")
    def test_single_string_value(self, mock_parse):
        expected = "value"

        result = prop._transform_values([expected])

        assert result == mock_parse.return_value

        mock_parse.assert_called_with(expected)

    def test_single_non_str(self):
        value = 123

        result = prop._transform_values([value])

        assert result == value

    def test_multiple_json_values(self):
        values = [1, 2]

        result = prop._transform_values([str(val) for val in values])

        assert result == values

    def test_multiple_non_json_values(self):
        values = [1, "2"]

        result = prop._transform_values(values)

        assert result == values


class Test_get_property(object):
    """Test ht.pyfilter.property.get_property."""

    @patch("ht.pyfilter.property._transform_values")
    def test(self, mock_transform, patch_soho):
        mock_name = MagicMock(spec=str)

        result = prop.get_property(mock_name)

        assert result == mock_transform.return_value

        mock_transform.assert_called_with(patch_soho["mantra"].property.return_value)


class Test_set_property(object):
    """Test ht.pyfilter.property.set_property."""

    @patch("ht.pyfilter.property._prep_value_to_set")
    def test(self, mock_prep, patch_soho):
        mock_name = MagicMock(spec=str)
        mock_value = MagicMock(spec=int)

        prop.set_property(mock_name, mock_value)

        mock_prep.assert_called_with(mock_value)
        patch_soho["mantra"].setproperty.assert_called_with(mock_name, mock_prep.return_value)
