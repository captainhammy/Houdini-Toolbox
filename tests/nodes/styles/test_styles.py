"""Tests for ht.nodes.styles.styles module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import imp

# Third Party Imports
from mock import MagicMock, PropertyMock, patch

# Houdini Toolbox Imports
from ht.nodes.styles import styles

# Houdini Imports
import hou

# Reload the module to test to capture load evaluation since it has already
# been loaded.
imp.reload(styles)


# =============================================================================
# CLASSES
# =============================================================================

class Test_StyleConstant(object):
    """Test ht.nodes.styles.styles.StyleConstant."""

    def test___init__(self):
        """Test the constructor"""
        mock_name = MagicMock(spec=str)
        mock_color = MagicMock(spec=hou.Color)
        mock_color_type = MagicMock(spec=str)
        mock_shape = MagicMock(spec=str)
        mock_file_path = MagicMock(spec=str)

        constant = styles.StyleConstant(mock_name, mock_color, mock_color_type, mock_shape, mock_file_path)

        assert constant._name == mock_name
        assert constant._color == mock_color
        assert constant._color_type == mock_color_type
        assert constant._shape == mock_shape
        assert constant._file_path == mock_file_path

    @patch.object(styles.StyleConstant, "name", new_callable=PropertyMock)
    @patch.object(styles.StyleConstant, "__init__", lambda x, y, z, u, v: None)
    def test___eq__(self, mock_name_prop):
        """Test the equality operator."""
        mock_name_prop.return_value = "name1"

        constant = styles.StyleConstant(None, None, None, None)

        mock_constant = MagicMock(spec=styles.StyleConstant)
        mock_constant.name = "name2"

        assert constant != mock_constant

        mock_name_prop.return_value = "name"
        mock_constant.name = "name"

        assert constant == mock_constant

        result = constant.__eq__(MagicMock())
        assert result == NotImplemented

    @patch.object(styles.StyleConstant, "name", new_callable=PropertyMock)
    @patch.object(styles.StyleConstant, "__init__", lambda x, y, z, u, v: None)
    def test___hash__(self, mock_name_prop):
        """Test the hash operator."""
        constant = styles.StyleConstant(None, None, None, None)

        result = constant.__hash__()

        assert result == hash(constant.name)

        assert hash(constant) == hash(constant.name)

    # ne

    @patch.object(styles.StyleConstant, "__eq__")
    @patch.object(styles.StyleConstant, "__init__", lambda x, y, z, u, v: None)
    def test___ne__(self, mock_eq):
        """Test the ne operator."""
        constant = styles.StyleConstant(None, None, None, None)

        mock_constant = MagicMock(spec=styles.StyleConstant)

        result = constant.__ne__(mock_constant)

        assert result != mock_eq.return_value

    @patch.object(styles.StyleConstant, "__eq__")
    @patch.object(styles.StyleConstant, "__init__", lambda x, y, z, u, v: None)
    def test___ne___different_type(self, mock_eq):
        """Test the ne operator when the other item isn't a StyleConstant."""
        constant = styles.StyleConstant(None, None, None, None)

        result = constant.__ne__(MagicMock())

        assert result == NotImplemented

    # Properties

    @patch.object(styles.StyleConstant, "__init__", lambda x, y, z, u, v: None)
    def test_color(self):
        """Test the 'color' property."""
        mock_color1 = MagicMock(spec=hou.Color)

        constant = styles.StyleConstant(None, None, None, None)
        constant._color = mock_color1

        assert constant.color == mock_color1

    @patch.object(styles.StyleConstant, "__init__", lambda x, y, z, u, v: None)
    def test_color_type(self):
        """Test the 'color_type' property."""
        value1 = MagicMock(spec=str)
        constant = styles.StyleConstant(None, None, None, None)
        constant._color_type = value1

        assert constant.color_type == value1

    @patch.object(styles.StyleConstant, "__init__", lambda x, y, z, u, v: None)
    def test_file_path(self):
        """Test the 'file_path' property."""
        value = MagicMock(spec=str)
        constant = styles.StyleConstant(None, None, None, None)
        constant._file_path = value

        assert constant.file_path == value

    @patch.object(styles.StyleConstant, "__init__", lambda x, y, z, u, v: None)
    def test_name(self):
        """Test the 'name' property."""
        value = MagicMock(spec=str)
        constant = styles.StyleConstant(None, None, None, None)
        constant._name = value

        assert constant.name == value

    @patch.object(styles.StyleConstant, "__init__", lambda x, y, z, u, v: None)
    def test_shape(self):
        """Test the 'shape' property."""
        value1 = MagicMock(spec=str)
        constant = styles.StyleConstant(None, None, None, None)
        constant._shape = value1

        assert constant.shape == value1

    # Methods

    # apply_to_node

    @patch.object(styles.StyleConstant, "shape", new_callable=PropertyMock)
    @patch.object(styles.StyleConstant, "color", new_callable=PropertyMock)
    @patch.object(styles.StyleConstant, "__init__", lambda x, y, z, u, v: None)
    def test_apply_to_node__both(self, mock_color_prop, mock_shape_prop):
        """Test applying everything to a node."""
        mock_node = MagicMock(spec=hou.Node)

        constant = styles.StyleConstant(None, None, None, None)

        constant.apply_to_node(mock_node)

        mock_node.setColor.assert_called_with(mock_color_prop.return_value)
        mock_node.setUserData.assert_called_with("nodeshape", mock_shape_prop.return_value)

    @patch.object(styles.StyleConstant, "shape", new_callable=PropertyMock(return_value=None))
    @patch.object(styles.StyleConstant, "color", new_callable=PropertyMock(return_value=None))
    @patch.object(styles.StyleConstant, "__init__", lambda x, y, z, u, v: None)
    def test_apply_to_node__none(self, mock_color, mock_shape):
        """Test applying to a node when no values will be set."""
        mock_node = MagicMock(spec=hou.Node)

        constant = styles.StyleConstant(None, None, None, None)

        constant.apply_to_node(mock_node)

        mock_node.setColor.assert_not_called()
        mock_node.setUserData.assert_not_called()


class Test_StyleRule(object):
    """Test ht.nodes.styles.styles.StyleRule."""

    def test___init__(self):
        """Test the constructor."""
        mock_name = MagicMock(spec=str)
        mock_color = MagicMock(spec=hou.Color)
        mock_color_type = MagicMock(spec=str)
        mock_shape = MagicMock(spec=str)
        mock_file_path = MagicMock(spec=str)

        rule = styles.StyleRule(mock_name, mock_color, mock_color_type, mock_shape, mock_file_path)

        assert rule._name == mock_name
        assert rule._color == mock_color
        assert rule._color_type == mock_color_type
        assert rule._shape == mock_shape
        assert rule._file_path == mock_file_path

    @patch.object(styles.StyleRule, "name", new_callable=PropertyMock(return_value="name"))
    @patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)
    def test___eq__(self, mock_name_prop):
        """Test the equality operator."""
        rule = styles.StyleRule(None, None, None, None)

        mock_rule = MagicMock(spec=styles.StyleRule)
        mock_rule.name = "different_name"

        assert rule != mock_rule

        mock_rule.name = "name"
        assert rule == mock_rule

        result = rule.__eq__(MagicMock())
        assert result == NotImplemented

    @patch.object(styles.StyleRule, "name", new_callable=PropertyMock(return_value="name"))
    @patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)
    def test___hash__(self, mock_name_prop):
        """Test the hash operator."""
        rule = styles.StyleRule(None, None, None, None)

        result = rule.__hash__()

        assert result == hash(rule.name)

        assert hash(rule) == hash(rule.name)

    # ne

    @patch.object(styles.StyleRule, "__eq__")
    @patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)
    def test___ne__(self, mock_eq):
        """Test the ne operator."""
        rule = styles.StyleRule(None, None, None, None)

        mock_rule = MagicMock(spec=styles.StyleRule)

        result = rule.__ne__(mock_rule)

        assert result != mock_eq.return_value

    @patch.object(styles.StyleRule, "__eq__")
    @patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)
    def test___ne___different_type(self, mock_eq):
        """Test the ne operator when the other item isn't a StyleConstant."""
        rule = styles.StyleRule(None, None, None, None)

        result = rule.__ne__(MagicMock())

        assert result == NotImplemented

    @patch.object(styles.StyleRule, "_get_typed_color_value")
    @patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)
    def test___str__(self, mock_typed):
        """Test converting the object to a string."""
        mock_typed.return_value = (0.46700000762939453, 1.0, 0.5)

        rule = styles.StyleRule(None, None, None, None)

        assert str(rule) == "(0.467, 1, 0.5)"

    # Properties

    @patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)
    def test_color(self):
        """Test the 'color' property."""
        mock_color = MagicMock(spec=hou.Color)

        rule = styles.StyleRule(None, None, None, None)
        rule._color = mock_color

        assert rule.color == mock_color

    @patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)
    def test_color_type(self):
        """Test the 'color_type' property."""
        value = MagicMock(spec=str)
        rule = styles.StyleRule(None, None, None, None)
        rule._color_type = value

        assert rule.color_type == value

    @patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)
    def test_file_path(self):
        """Test the 'file_path' property."""
        value = MagicMock(spec=str)
        rule = styles.StyleRule(None, None, None, None)
        rule._file_path = value

        assert rule.file_path == value

    @patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)
    def test_name(self):
        """Test the 'name' property."""
        value = MagicMock(spec=str)
        rule = styles.StyleRule(None, None, None, None)
        rule._name = value

        assert rule.name == value

    @patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)
    def test_shape(self):
        """Test the 'shape' property."""
        value = MagicMock(spec=str)
        rule = styles.StyleRule(None, None, None, None)
        rule._shape = value

        assert rule.shape == value

    # Methods

    # _get_typed_color_value

    @patch.object(styles.StyleRule, "color_type", new_callable=PropertyMock(return_value="HSV"))
    @patch.object(styles.StyleRule, "color", new_callable=PropertyMock)
    @patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)
    def test__get_typed_color_value(self, mock_color_prop, mock_color_type_prop):
        """Test getting a typed color value."""
        value = (1, 2, 3)

        mock_color = MagicMock(spec=hou.Color)
        mock_color.hsv.return_value = value

        mock_color_prop.return_value = mock_color

        rule = styles.StyleRule(None, None, None, None)

        result = rule._get_typed_color_value()
        assert result == value

    # apply_to_node

    @patch.object(styles.StyleRule, "shape", new_callable=PropertyMock)
    @patch.object(styles.StyleRule, "color", new_callable=PropertyMock)
    @patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)
    def test_apply_to_node__both(self, mock_color_prop,  mock_shape_prop):
        """Test applying everything to a node."""
        mock_node = MagicMock(spec=hou.Node)

        rule = styles.StyleRule(None, None, None, None)

        rule.apply_to_node(mock_node)

        mock_node.setColor.assert_called_with(mock_color_prop.return_value)
        mock_node.setUserData.assert_called_with("nodeshape", mock_shape_prop.return_value)

    @patch.object(styles.StyleRule, "shape", new_callable=PropertyMock(return_value=None))
    @patch.object(styles.StyleRule, "color", new_callable=PropertyMock(return_value=None))
    @patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)
    def test_apply_to_node__none(self, mock_color_prop, mock_shape_prop):
        """Test applying to a node when no values will be set."""
        mock_node = MagicMock(spec=hou.Node)

        rule = styles.StyleRule(None, None, None, None)

        rule.apply_to_node(mock_node)

        mock_node.setColor.assert_not_called()
        mock_node.setUserData.assert_not_called()


class Test_ConstantRule(object):
    """Test ht.nodes.styles.styles.ConstantRule."""

    def test___init__(self):
        """Test the constructor."""
        mock_name = MagicMock(spec=str)
        mock_constant_name = MagicMock(spec=str)
        mock_file_path = MagicMock(spec=str)

        rule = styles.ConstantRule(mock_name, mock_constant_name, mock_file_path)

        assert rule._name == mock_name
        assert rule._constant_name == mock_constant_name
        assert rule._file_path == mock_file_path

    @patch.object(styles.ConstantRule, "name", new_callable=PropertyMock)
    @patch.object(styles.ConstantRule, "__init__", lambda x, y, z: None)
    def test___eq__(self, mock_name_prop):
        """Test the equality operator."""
        constant = styles.ConstantRule(None, None)

        mock_name_prop.return_value = "name1"

        mock_constant = MagicMock(spec=styles.ConstantRule)
        mock_constant.name = "name2"

        assert constant != mock_constant

        mock_name_prop.return_value = "name"
        mock_constant.name = "name"

        assert constant == mock_constant

        result = constant.__eq__(MagicMock())
        assert result  == NotImplemented

    @patch.object(styles.ConstantRule, "constant_name", new_callable=PropertyMock)
    @patch.object(styles.ConstantRule, "name", new_callable=PropertyMock)
    @patch.object(styles.ConstantRule, "__init__", lambda x, y, z: None)
    def test___hash__(self, mock_name_prop, mock_constant_prop):
        """Test the hash operator."""
        constant = styles.ConstantRule(None, None)

        result = constant.__hash__()

        assert result == hash((constant.constant_name, constant.name))

        assert hash(constant) == hash((constant.constant_name, constant.name))

    # ne

    @patch.object(styles.ConstantRule, "__eq__")
    @patch.object(styles.ConstantRule, "__init__", lambda x, y, z: None)
    def test___ne__(self, mock_eq):
        """Test the ne operator."""
        constant = styles.ConstantRule(None, None)
        mock_constant = MagicMock(spec=styles.ConstantRule)

        result = constant.__ne__(mock_constant)

        assert result != mock_eq.return_value

    @patch.object(styles.ConstantRule, "__eq__")
    @patch.object(styles.ConstantRule, "__init__", lambda x, y, z: None)
    def test___ne___different_type(self, mock_eq):
        """Test the ne operator when the other item isn't a StyleConstant."""
        constant = styles.ConstantRule(None, None)

        result = constant.__ne__(MagicMock())

        assert result == NotImplemented

    # Properties

    @patch.object(styles.ConstantRule, "__init__", lambda x, y, z: None)
    def test_constant_name(self):
        """Test the 'constant_name' property."""
        value = MagicMock(spec=str)
        rule = styles.ConstantRule(None, None)
        rule._constant_name = value

        assert rule.constant_name == value

    @patch.object(styles.ConstantRule, "__init__", lambda x, y, z: None)
    def test_file_path(self):
        "Test the 'file_path' property."
        value = MagicMock(spec=str)
        rule = styles.ConstantRule(None, None)
        rule._file_path = value

        assert rule.file_path == value

    @patch.object(styles.ConstantRule, "__init__", lambda x, y, z: None)
    def test_name(self):
        """Test the 'name' property."""
        value = MagicMock(spec=str)
        rule = styles.ConstantRule(None, None)
        rule._name = value

        assert rule.name  == value
