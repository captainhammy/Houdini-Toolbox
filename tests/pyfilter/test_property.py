"""Test the ht.pyfilter.property module."""

# =============================================================================
# IMPORTS
# =============================================================================

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

    def test_none(self):
        result = prop._prep_value_to_set(None)

        assert result == []

    def test_str(self, mocker):
        mock_value = mocker.MagicMock(spec=str)

        result = prop._prep_value_to_set(mock_value)

        assert result == [mock_value]

    def test_unicode(self, mocker):
        mock_value = mocker.MagicMock(spec=unicode)

        result = prop._prep_value_to_set(mock_value)

        assert result == [mock_value]

    def test_dict(self, mocker):
        mock_dumps = mocker.patch("ht.pyfilter.property.json.dumps")

        mock_value = mocker.MagicMock(spec=dict)

        result = prop._prep_value_to_set(mock_value)

        assert result == [mock_dumps.return_value]

        mock_dumps.assert_called_with(mock_value)

    def test_non_iterable(self, mocker):
        mock_value = mocker.MagicMock(spec=int)

        result = prop._prep_value_to_set(mock_value)

        assert result == [mock_value]

    def test_list_of_dicts(self, mocker):
        mock_dumps = mocker.patch("ht.pyfilter.property.json.dumps")

        mock_value = mocker.MagicMock(spec=dict)

        result = prop._prep_value_to_set([mock_value])

        assert result == [mock_dumps.return_value]

    def test_list_of_dicts__typeerror(self, mocker):
        mocker.patch("ht.pyfilter.property.json.dumps", side_effect=TypeError)

        mock_value = mocker.MagicMock(spec=dict)

        value = [mock_value]

        result = prop._prep_value_to_set(value)

        assert result == value

    def test_list_of_dicts__valueerror(self, mocker):
        mocker.patch("ht.pyfilter.property.json.dumps", side_effect=ValueError)

        mock_value = mocker.MagicMock(spec=dict)

        value = [mock_value]

        result = prop._prep_value_to_set(value)

        assert result == value

    def test_list_of_non_dicts(self, mocker):
        mock_dict = mocker.MagicMock(spec=dict)
        mock_int = mocker.MagicMock(spec=int)

        value = [mock_dict, mock_int]

        result = prop._prep_value_to_set(value)

        assert result == value


class Test__transform_values(object):
    """Test ht.pyfilter.property._transform_values."""

    def test_none(self):
        result = prop._transform_values(None)

        assert result is None

    def test_single_string(self, mocker):
        mock_loads = mocker.patch("ht.pyfilter.property.json.loads")
        mock_value = mocker.MagicMock(spec=str)

        result = prop._transform_values([mock_value])

        assert result == mock_loads.return_value

    def test_single_string_dict_value(self, mocker):
        mock_loads = mocker.patch("ht.pyfilter.property.json.loads")
        mock_loads.side_effect = ValueError

        mock_key1 = mocker.MagicMock(spec=str)
        mock_key2 = mocker.MagicMock(spec=str)
        mock_value1 = mocker.MagicMock(spec=str)
        mock_value2 = mocker.MagicMock(spec=str)

        mock_value = mocker.MagicMock(spec=str)
        mock_value.split.return_value = [mock_key1, mock_value1, mock_key2, mock_value2]

        result = prop._transform_values([mock_value])

        assert result == {mock_key1: mock_value1, mock_key2: mock_value2}

        mock_loads.assert_called_with(mock_value)

    def test_single_string_value(self, mocker):
        mock_loads = mocker.patch("ht.pyfilter.property.json.loads")
        mock_loads.side_effect = ValueError

        mock_parse = mocker.patch("ht.pyfilter.property._parse_string_for_bool")

        mock_value = mocker.MagicMock(spec=str)
        mock_value.split.return_value.__len__.return_value = 2

        result = prop._transform_values([mock_value])

        assert result == mock_parse.return_value

        mock_loads.assert_called_with(mock_value)

        mock_parse.assert_called_with(mock_value)

    def test_single_int(self, mocker):
        mock_loads = mocker.patch("ht.pyfilter.property.json.loads")
        mock_value = mocker.MagicMock(spec=int)

        result = prop._transform_values([mock_value])

        assert result == mock_value

        mock_loads.assert_not_called()

    def test_multiple_values(self, mocker):
        mock_loads = mocker.patch("ht.pyfilter.property.json.loads")

        mock_values = [mocker.MagicMock(spec=str), mocker.MagicMock(spec=str)]

        result = prop._transform_values(mock_values)

        assert result == [mock_loads.return_value, mock_loads.return_value]

    def test_multiple_values__type_error(self, mocker):
        mock_loads = mocker.patch("ht.pyfilter.property.json.loads")
        mock_loads.side_effect = TypeError

        mock_values = [mocker.MagicMock(spec=str), mocker.MagicMock(spec=str)]

        result = prop._transform_values(mock_values)

        assert result == mock_values

    def test_multiple_values__value_error(self, mocker):
        mock_loads = mocker.patch("ht.pyfilter.property.json.loads")
        mock_loads.side_effect = ValueError

        mock_values = [mocker.MagicMock(spec=str), mocker.MagicMock(spec=str)]

        result = prop._transform_values(mock_values)

        assert result == mock_values


def test_get_property(mocker, patch_soho):
    """Test ht.pyfilter.property.get_property."""
    mock_transform = mocker.patch("ht.pyfilter.property._transform_values")

    mock_name = mocker.MagicMock(spec=str)

    result = prop.get_property(mock_name)

    assert result == mock_transform.return_value

    mock_transform.assert_called_with(patch_soho.mantra.property.return_value)


def test_set_property(mocker, patch_soho):
    """Test ht.pyfilter.property.set_property."""
    mock_prep = mocker.patch("ht.pyfilter.property._prep_value_to_set")

    mock_name = mocker.MagicMock(spec=str)
    mock_value = mocker.MagicMock(spec=int)

    prop.set_property(mock_name, mock_value)

    mock_prep.assert_called_with(mock_value)
    patch_soho.mantra.setproperty.assert_called_with(mock_name, mock_prep.return_value)
