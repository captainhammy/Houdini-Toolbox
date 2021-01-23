"""Tests for ht.nodes.styles.styles module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Third Party Imports
import pytest

# Houdini Toolbox Imports
from ht.nodes.styles import styles

# Houdini Imports
import hou


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def init_constant_rule(mocker):
    """Fixture to initialize a style constant."""
    mocker.patch.object(styles.ConstantRule, "__init__", lambda x, y, z: None)

    def _create():
        return styles.ConstantRule(None, None)

    return _create


@pytest.fixture
def init_style_constant(mocker):
    """Fixture to initialize a style constant."""
    mocker.patch.object(styles.StyleConstant, "__init__", lambda x, y, z, u, v: None)

    def _create():
        return styles.StyleConstant(None, None, None, None)

    return _create


@pytest.fixture
def init_style_rule(mocker):
    """Fixture to initialize a style rule."""
    mocker.patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)

    def _create():
        return styles.StyleRule(None, None, None, None)

    return _create


# =============================================================================
# TESTS
# =============================================================================


class Test_StyleConstant:
    """Test ht.nodes.styles.styles.StyleConstant."""

    def test___init__(self, mocker):
        """Test object initialization."""
        mock_name = mocker.MagicMock(spec=str)
        mock_color = mocker.MagicMock(spec=hou.Color)
        mock_color_type = mocker.MagicMock(spec=str)
        mock_shape = mocker.MagicMock(spec=str)
        mock_file_path = mocker.MagicMock(spec=str)

        constant = styles.StyleConstant(
            mock_name, mock_color, mock_color_type, mock_shape, mock_file_path
        )

        assert constant._name == mock_name
        assert constant._color == mock_color
        assert constant._color_type == mock_color_type
        assert constant._shape == mock_shape
        assert constant._file_path == mock_file_path

    def test___eq__(self, init_style_constant, mocker):
        """Test the equality operator."""
        mock_name_prop = mocker.patch.object(
            styles.StyleConstant, "name", new_callable=mocker.PropertyMock
        )

        mock_name_prop.return_value = "name1"

        constant = init_style_constant()

        mock_constant = mocker.MagicMock(spec=styles.StyleConstant)
        mock_constant.name = "name2"

        assert constant != mock_constant

        mock_name_prop.return_value = "name"
        mock_constant.name = "name"

        assert constant == mock_constant

        result = constant.__eq__(mocker.MagicMock())
        assert result == NotImplemented

    def test___hash__(self, init_style_constant, mocker):
        """Test the hash operator."""
        mocker.patch.object(
            styles.StyleConstant, "name", new_callable=mocker.PropertyMock
        )

        constant = init_style_constant()

        result = constant.__hash__()

        assert result == hash(constant.name)

        assert hash(constant) == hash(constant.name)

    # ne

    def test___ne__(self, init_style_constant, mocker):
        """Test the __ne__ operator."""
        mock_eq = mocker.patch.object(styles.StyleConstant, "__eq__")

        constant = init_style_constant()

        mock_constant = mocker.MagicMock(spec=styles.StyleConstant)

        result = constant.__ne__(mock_constant)

        assert result != mock_eq.return_value

    def test___ne___different_type(self, init_style_constant, mocker):
        """Test the __ne__ operator when the other item isn't a StyleConstant."""
        constant = init_style_constant()

        result = constant.__ne__(mocker.MagicMock())

        assert result == NotImplemented

    # Properties

    def test_color(self, init_style_constant, mocker):
        """Test the 'color' property."""
        mock_value = mocker.MagicMock(spec=hou.Color)

        constant = init_style_constant()
        constant._color = mock_value
        assert constant.color == mock_value

    def test_color_type(self, init_style_constant, mocker):
        """Test the 'color_type' property."""
        value1 = mocker.MagicMock(spec=str)

        constant = init_style_constant()
        constant._color_type = value1
        assert constant.color_type == value1

    def test_file_path(self, init_style_constant, mocker):
        """Test the 'file_path' property."""
        mock_value = mocker.MagicMock(spec=str)

        constant = init_style_constant()
        constant._file_path = mock_value
        assert constant.file_path == mock_value

    def test_name(self, init_style_constant, mocker):
        """Test the 'name' property."""
        mock_value = mocker.MagicMock(spec=str)

        constant = init_style_constant()
        constant._name = mock_value
        assert constant.name == mock_value

    def test_shape(self, init_style_constant, mocker):
        """Test the 'shape' property."""
        mock_value = mocker.MagicMock(spec=str)

        constant = init_style_constant()
        constant._shape = mock_value
        assert constant.shape == mock_value

    # Methods

    # apply_to_node

    def test_apply_to_node__both(self, init_style_constant, mocker):
        """Test applying everything to a node."""
        mock_color_prop = mocker.patch.object(
            styles.StyleConstant, "color", new_callable=mocker.PropertyMock
        )
        mock_shape_prop = mocker.patch.object(
            styles.StyleConstant, "shape", new_callable=mocker.PropertyMock
        )

        mock_node = mocker.MagicMock(spec=hou.Node)

        constant = init_style_constant()

        constant.apply_to_node(mock_node)

        mock_node.setColor.assert_called_with(mock_color_prop.return_value)
        mock_node.setUserData.assert_called_with(
            "nodeshape", mock_shape_prop.return_value
        )

    def test_apply_to_node__none(self, init_style_constant, mocker):
        """Test applying to a node when no values will be set."""
        mocker.patch.object(
            styles.StyleConstant,
            "color",
            new_callable=mocker.PropertyMock(return_value=None),
        )
        mocker.patch.object(
            styles.StyleConstant,
            "shape",
            new_callable=mocker.PropertyMock(return_value=None),
        )

        mock_node = mocker.MagicMock(spec=hou.Node)

        constant = init_style_constant()

        constant.apply_to_node(mock_node)

        mock_node.setColor.assert_not_called()
        mock_node.setUserData.assert_not_called()


class Test_StyleRule:
    """Test ht.nodes.styles.styles.StyleRule."""

    def test___init__(self, mocker):
        """Test the constructor."""
        mock_name = mocker.MagicMock(spec=str)
        mock_color = mocker.MagicMock(spec=hou.Color)
        mock_color_type = mocker.MagicMock(spec=str)
        mock_shape = mocker.MagicMock(spec=str)
        mock_file_path = mocker.MagicMock(spec=str)

        rule = styles.StyleRule(
            mock_name, mock_color, mock_color_type, mock_shape, mock_file_path
        )

        assert rule._name == mock_name
        assert rule._color == mock_color
        assert rule._color_type == mock_color_type
        assert rule._shape == mock_shape
        assert rule._file_path == mock_file_path

    def test___eq__(self, init_style_rule, mocker):
        """Test the equality operator."""
        mocker.patch.object(
            styles.StyleRule,
            "name",
            new_callable=mocker.PropertyMock(return_value="name"),
        )

        rule = init_style_rule()

        mock_rule = mocker.MagicMock(spec=styles.StyleRule)
        mock_rule.name = "different_name"

        assert rule != mock_rule

        mock_rule.name = "name"
        assert rule == mock_rule

        result = rule.__eq__(mocker.MagicMock())
        assert result == NotImplemented

    def test___hash__(self, init_style_rule, mocker):
        """Test the hash operator."""
        mocker.patch.object(
            styles.StyleRule,
            "name",
            new_callable=mocker.PropertyMock(return_value="name"),
        )

        rule = init_style_rule()

        result = rule.__hash__()

        assert result == hash(rule.name)

        assert hash(rule) == hash(rule.name)

    # ne

    def test___ne__(self, init_style_rule, mocker):
        """Test the __ne__ operator."""
        mock_eq = mocker.patch.object(styles.StyleRule, "__eq__")

        rule = init_style_rule()

        mock_rule = mocker.MagicMock(spec=styles.StyleRule)

        result = rule.__ne__(mock_rule)

        assert result != mock_eq.return_value

    def test___ne___different_type(self, init_style_rule, mocker):
        """Test the __ne__ operator when the other item isn't a StyleConstant."""
        mocker.patch.object(styles.StyleRule, "__eq__")

        rule = init_style_rule()

        result = rule.__ne__(mocker.MagicMock())

        assert result == NotImplemented

    def test___str__(self, init_style_rule, mocker):
        """Test converting the object to a string."""
        mock_typed = mocker.patch.object(styles.StyleRule, "_get_typed_color_value")

        mock_typed.return_value = (0.46700000762939453, 1.0, 0.5)

        rule = init_style_rule()

        assert str(rule) == "(0.467, 1, 0.5)"

    # Properties

    def test_color(self, init_style_rule, mocker):
        """Test the 'color' property."""
        mock_value = mocker.MagicMock(spec=hou.Color)

        rule = init_style_rule()
        rule._color = mock_value

        assert rule.color == mock_value

    def test_color_type(self, init_style_rule, mocker):
        """Test the 'color_type' property."""
        mock_value = mocker.MagicMock(spec=str)

        rule = init_style_rule()
        rule._color_type = mock_value
        assert rule.color_type == mock_value

    def test_file_path(self, init_style_rule, mocker):
        """Test the 'file_path' property."""
        mock_value = mocker.MagicMock(spec=str)

        rule = init_style_rule()
        rule._file_path = mock_value
        assert rule.file_path == mock_value

    def test_name(self, init_style_rule, mocker):
        """Test the 'name' property."""
        mock_value = mocker.MagicMock(spec=str)

        rule = init_style_rule()
        rule._name = mock_value
        assert rule.name == mock_value

    def test_shape(self, init_style_rule, mocker):
        """Test the 'shape' property."""
        mock_value = mocker.MagicMock(spec=str)

        rule = init_style_rule()
        rule._shape = mock_value
        assert rule.shape == mock_value

    # Methods

    # _get_typed_color_value

    def test__get_typed_color_value(self, init_style_rule, mocker):
        """Test getting a typed color value."""
        mock_color_prop = mocker.patch.object(
            styles.StyleRule, "color", new_callable=mocker.PropertyMock
        )
        mocker.patch.object(
            styles.StyleRule,
            "color_type",
            new_callable=mocker.PropertyMock(return_value="HSV"),
        )

        mock_color = mocker.MagicMock(spec=hou.Color)
        mock_color_prop.return_value = mock_color

        rule = init_style_rule()

        result = rule._get_typed_color_value()
        assert result == mock_color.hsv.return_value

    # apply_to_node

    def test_apply_to_node__both(self, init_style_rule, mocker):
        """Test applying everything to a node."""
        mock_color_prop = mocker.patch.object(
            styles.StyleRule, "color", new_callable=mocker.PropertyMock
        )
        mock_shape_prop = mocker.patch.object(
            styles.StyleRule, "shape", new_callable=mocker.PropertyMock
        )
        mock_node = mocker.MagicMock(spec=hou.Node)

        rule = init_style_rule()

        rule.apply_to_node(mock_node)

        mock_node.setColor.assert_called_with(mock_color_prop.return_value)
        mock_node.setUserData.assert_called_with(
            "nodeshape", mock_shape_prop.return_value
        )

    def test_apply_to_node__none(self, init_style_rule, mocker):
        """Test applying to a node when no values will be set."""
        mocker.patch.object(
            styles.StyleRule,
            "color",
            new_callable=mocker.PropertyMock(return_value=None),
        )
        mocker.patch.object(
            styles.StyleRule,
            "shape",
            new_callable=mocker.PropertyMock(return_value=None),
        )

        mock_node = mocker.MagicMock(spec=hou.Node)

        rule = init_style_rule()

        rule.apply_to_node(mock_node)

        mock_node.setColor.assert_not_called()
        mock_node.setUserData.assert_not_called()


class Test_ConstantRule:
    """Test ht.nodes.styles.styles.ConstantRule."""

    def test___init__(self, mocker):
        """Test the constructor."""
        mock_name = mocker.MagicMock(spec=str)
        mock_constant_name = mocker.MagicMock(spec=str)
        mock_file_path = mocker.MagicMock(spec=str)

        rule = styles.ConstantRule(mock_name, mock_constant_name, mock_file_path)

        assert rule._name == mock_name
        assert rule._constant_name == mock_constant_name
        assert rule._file_path == mock_file_path

    def test___eq__(self, init_constant_rule, mocker):
        """Test the equality operator."""
        mock_name_prop = mocker.patch.object(
            styles.ConstantRule, "name", new_callable=mocker.PropertyMock
        )

        constant = init_constant_rule()

        mock_name_prop.return_value = "name1"

        mock_constant = mocker.MagicMock(spec=styles.ConstantRule)
        mock_constant.name = "name2"

        assert constant != mock_constant

        mock_name_prop.return_value = "name"
        mock_constant.name = "name"

        assert constant == mock_constant

        result = constant.__eq__(mocker.MagicMock())
        assert result == NotImplemented

    def test___hash__(self, init_constant_rule, mocker):
        """Test the hash operator."""
        mocker.patch.object(
            styles.ConstantRule, "name", new_callable=mocker.PropertyMock
        )
        mocker.patch.object(
            styles.ConstantRule, "constant_name", new_callable=mocker.PropertyMock
        )

        constant = init_constant_rule()

        result = constant.__hash__()

        assert result == hash((constant.constant_name, constant.name))

        assert hash(constant) == hash((constant.constant_name, constant.name))

    # ne

    def test___ne__(self, init_constant_rule, mocker):
        """Test the ne operator."""
        mock_eq = mocker.patch.object(styles.ConstantRule, "__eq__")

        constant = init_constant_rule()
        mock_constant = mocker.MagicMock(spec=styles.ConstantRule)

        result = constant.__ne__(mock_constant)

        assert result != mock_eq.return_value

    def test___ne___different_type(self, init_constant_rule, mocker):
        """Test the ne operator when the other item isn't a StyleConstant."""
        mocker.patch.object(styles.ConstantRule, "__eq__")

        constant = init_constant_rule()

        result = constant.__ne__(mocker.MagicMock())

        assert result == NotImplemented

    # Properties

    def test_constant_name(self, init_constant_rule, mocker):
        """Test the 'constant_name' property."""
        mock_value = mocker.MagicMock(spec=str)
        constant = init_constant_rule()
        constant._constant_name = mock_value

        assert constant.constant_name == mock_value

    def test_file_path(self, init_constant_rule, mocker):
        """Test the 'file_path' property."""
        mock_value = mocker.MagicMock(spec=str)
        constant = init_constant_rule()
        constant._file_path = mock_value

        assert constant.file_path == mock_value

    def test_name(self, init_constant_rule, mocker):
        """Test the 'name' property."""
        mock_value = mocker.MagicMock(spec=str)
        constant = init_constant_rule()
        constant._name = mock_value

        assert constant.name == mock_value
