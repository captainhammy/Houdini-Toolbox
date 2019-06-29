"""Tests for ht.nodes.styles.styles module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
from mock import MagicMock, PropertyMock, patch
import unittest

# Houdini Toolbox Imports
from ht.nodes.styles import styles

# Houdini Imports
import hou

reload(styles)


# =============================================================================
# CLASSES
# =============================================================================

class Test_StyleConstant(unittest.TestCase):
    """Test ht.nodes.styles.styles.StyleConstant."""

    def test___init__(self):
        """Test the constructor"""
        mock_name = MagicMock(spec=str)
        mock_color = MagicMock(spec=hou.Color)
        mock_color_type = MagicMock(spec=str)
        mock_shape = MagicMock(spec=str)
        mock_file_path = MagicMock(spec=str)

        constant = styles.StyleConstant(mock_name, mock_color, mock_color_type, mock_shape, mock_file_path)

        self.assertEqual(constant._name, mock_name)
        self.assertEqual(constant._color, mock_color)
        self.assertEqual(constant._color_type, mock_color_type)
        self.assertEqual(constant._shape, mock_shape)
        self.assertEqual(constant._file_path, mock_file_path)

    @patch.object(styles.StyleConstant, "name", new_callable=PropertyMock)
    @patch.object(styles.StyleConstant, "__init__", lambda x, y, z, u, v: None)
    def test___eq__(self, mock_name_prop):
        """Test the equality operator."""
        mock_name_prop.return_value = "name1"

        constant = styles.StyleConstant(None, None, None, None)

        mock_constant = MagicMock(spec=styles.StyleConstant)
        mock_constant.name = "name2"

        self.assertNotEqual(constant, mock_constant)

        mock_name_prop.return_value = "name"
        mock_constant.name = "name"

        self.assertEqual(constant, mock_constant)

        result = constant.__eq__(MagicMock())
        self.assertEqual(result, NotImplemented)

    @patch.object(styles.StyleConstant, "name", new_callable=PropertyMock)
    @patch.object(styles.StyleConstant, "__init__", lambda x, y, z, u, v: None)
    def test___hash__(self, mock_name_prop):
        """Test the hash operator."""
        constant = styles.StyleConstant(None, None, None, None)

        result = constant.__hash__()

        self.assertEqual(result, hash(constant.name))

        self.assertEqual(hash(constant), hash(constant.name))

    # ne

    @patch.object(styles.StyleConstant, "__eq__")
    @patch.object(styles.StyleConstant, "__init__", lambda x, y, z, u, v: None)
    def test___ne__(self, mock_eq):
        """Test the ne operator."""
        constant = styles.StyleConstant(None, None, None, None)

        mock_constant = MagicMock(spec=styles.StyleConstant)

        result = constant.__ne__(mock_constant)

        self.assertEqual(result, not mock_eq.return_value)

    @patch.object(styles.StyleConstant, "__eq__")
    @patch.object(styles.StyleConstant, "__init__", lambda x, y, z, u, v: None)
    def test___ne___different_type(self, mock_eq):
        """Test the ne operator when the other item isn't a StyleConstant."""
        constant = styles.StyleConstant(None, None, None, None)

        result = constant.__ne__(MagicMock())

        self.assertEqual(result, NotImplemented)

    # Properties

    @patch.object(styles.StyleConstant, "__init__", lambda x, y, z, u, v: None)
    def test_color(self):
        """Test the 'color' property."""
        mock_color1 = MagicMock(spec=hou.Color)

        constant = styles.StyleConstant(None, None, None, None)
        constant._color = mock_color1

        self.assertEqual(constant.color, mock_color1)

    @patch.object(styles.StyleConstant, "__init__", lambda x, y, z, u, v: None)
    def test_color_type(self):
        """Test the 'color_type' property."""
        value1 = MagicMock(spec=str)
        constant = styles.StyleConstant(None, None, None, None)
        constant._color_type = value1

        self.assertEqual(constant.color_type, value1)

    @patch.object(styles.StyleConstant, "__init__", lambda x, y, z, u, v: None)
    def test_file_path(self):
        """Test the 'file_path' property."""
        value = MagicMock(spec=str)
        constant = styles.StyleConstant(None, None, None, None)
        constant._file_path = value

        self.assertEqual(constant.file_path, value)

    @patch.object(styles.StyleConstant, "__init__", lambda x, y, z, u, v: None)
    def test_name(self):
        """Test the 'name' property."""
        value = MagicMock(spec=str)
        constant = styles.StyleConstant(None, None, None, None)
        constant._name = value

        self.assertEqual(constant.name, value)

    @patch.object(styles.StyleConstant, "__init__", lambda x, y, z, u, v: None)
    def test_shape(self):
        """Test the 'shape' property."""
        value1 = MagicMock(spec=str)
        constant = styles.StyleConstant(None, None, None, None)
        constant._shape = value1

        self.assertEqual(constant.shape, value1)

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


class Test_StyleRule(unittest.TestCase):
    """Test ht.nodes.styles.styles.StyleRule."""

    def test___init__(self):
        """Test the constructor."""
        mock_name = MagicMock(spec=str)
        mock_color = MagicMock(spec=hou.Color)
        mock_color_type = MagicMock(spec=str)
        mock_shape = MagicMock(spec=str)
        mock_file_path = MagicMock(spec=str)

        rule = styles.StyleRule(mock_name, mock_color, mock_color_type, mock_shape, mock_file_path)

        self.assertEqual(rule._name, mock_name)
        self.assertEqual(rule._color, mock_color)
        self.assertEqual(rule._color_type, mock_color_type)
        self.assertEqual(rule._shape, mock_shape)
        self.assertEqual(rule._file_path, mock_file_path)

    @patch.object(styles.StyleRule, "name", new_callable=PropertyMock(return_value="name"))
    @patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)
    def test___eq__(self, mock_name_prop):
        """Test the equality operator."""
        rule = styles.StyleRule(None, None, None, None)

        mock_rule = MagicMock(spec=styles.StyleRule)
        mock_rule.name = "different_name"

        self.assertNotEqual(rule, mock_rule)

        mock_rule.name = "name"
        self.assertEqual(rule, mock_rule)

        result = rule.__eq__(MagicMock())
        self.assertEqual(result, NotImplemented)

    @patch.object(styles.StyleRule, "name", new_callable=PropertyMock(return_value="name"))
    @patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)
    def test___hash__(self, mock_name_prop):
        """Test the hash operator."""
        rule = styles.StyleRule(None, None, None, None)

        result = rule.__hash__()

        self.assertEqual(result, hash(rule.name))

        self.assertEqual(hash(rule), hash(rule.name))

    # ne

    @patch.object(styles.StyleRule, "__eq__")
    @patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)
    def test___ne__(self, mock_eq):
        """Test the ne operator."""
        rule = styles.StyleRule(None, None, None, None)

        mock_rule = MagicMock(spec=styles.StyleRule)

        result = rule.__ne__(mock_rule)

        self.assertEqual(result, not mock_eq.return_value)

    @patch.object(styles.StyleRule, "__eq__")
    @patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)
    def test___ne___different_type(self, mock_eq):
        """Test the ne operator when the other item isn't a StyleConstant."""
        rule = styles.StyleRule(None, None, None, None)

        result = rule.__ne__(MagicMock())

        self.assertEqual(result, NotImplemented)

    @patch.object(styles.StyleRule, "_get_typed_color_value")
    @patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)
    def test___str__(self, mock_typed):
        """Test converting the object to a string."""
        mock_typed.return_value = (0.46700000762939453, 1.0, 0.5)

        rule = styles.StyleRule(None, None, None, None)

        self.assertEqual(str(rule), "(0.467, 1, 0.5)")

    # Properties

    @patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)
    def test_color(self):
        """Test the 'color' property."""
        mock_color = MagicMock(spec=hou.Color)

        rule = styles.StyleRule(None, None, None, None)
        rule._color = mock_color

        self.assertEqual(rule.color, mock_color)

    @patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)
    def test_color_type(self):
        """Test the 'color_type' property."""
        value = MagicMock(spec=str)
        rule = styles.StyleRule(None, None, None, None)
        rule._color_type = value

        self.assertEqual(rule.color_type, value)

    @patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)
    def test_file_path(self):
        """Test the 'file_path' property."""
        value = MagicMock(spec=str)
        rule = styles.StyleRule(None, None, None, None)
        rule._file_path = value

        self.assertEqual(rule.file_path, value)

    @patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)
    def test_name(self):
        """Test the 'name' property."""
        value = MagicMock(spec=str)
        rule = styles.StyleRule(None, None, None, None)
        rule._name = value

        self.assertEqual(rule.name, value)

    @patch.object(styles.StyleRule, "__init__", lambda x, y, z, u, v: None)
    def test_shape(self):
        """Test the 'shape' property."""
        value = MagicMock(spec=str)
        rule = styles.StyleRule(None, None, None, None)
        rule._shape = value

        self.assertEqual(rule.shape, value)

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
        self.assertEqual(result, value)

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


class Test_ConstantRule(unittest.TestCase):
    """Test ht.nodes.styles.styles.ConstantRule."""

    def test___init__(self):
        """Test the constructor."""
        mock_name = MagicMock(spec=str)
        mock_constant_name = MagicMock(spec=str)
        mock_file_path = MagicMock(spec=str)

        rule = styles.ConstantRule(mock_name, mock_constant_name, mock_file_path)

        self.assertEqual(rule._name, mock_name)
        self.assertEqual(rule._constant_name, mock_constant_name)
        self.assertEqual(rule._file_path, mock_file_path)

    @patch.object(styles.ConstantRule, "name", new_callable=PropertyMock)
    @patch.object(styles.ConstantRule, "__init__", lambda x, y, z: None)
    def test___eq__(self, mock_name_prop):
        """Test the equality operator."""
        constant = styles.ConstantRule(None, None)

        mock_name_prop.return_value = "name1"

        mock_constant = MagicMock(spec=styles.ConstantRule)
        mock_constant.name = "name2"

        self.assertNotEqual(constant, mock_constant)

        mock_name_prop.return_value = "name"
        mock_constant.name = "name"

        self.assertEqual(constant, mock_constant)

        result = constant.__eq__(MagicMock())
        self.assertEqual(result, NotImplemented)

    @patch.object(styles.ConstantRule, "constant_name", new_callable=PropertyMock)
    @patch.object(styles.ConstantRule, "name", new_callable=PropertyMock)
    @patch.object(styles.ConstantRule, "__init__", lambda x, y, z: None)
    def test___hash__(self, mock_name_prop, mock_constant_prop):
        """Test the hash operator."""
        constant = styles.ConstantRule(None, None)

        result = constant.__hash__()

        self.assertEqual(result, hash((constant.constant_name, constant.name)))

        self.assertEqual(hash(constant), hash((constant.constant_name, constant.name)))

    # ne

    @patch.object(styles.ConstantRule, "__eq__")
    @patch.object(styles.ConstantRule, "__init__", lambda x, y, z: None)
    def test___ne__(self, mock_eq):
        """Test the ne operator."""
        constant = styles.ConstantRule(None, None)
        mock_constant = MagicMock(spec=styles.ConstantRule)

        result = constant.__ne__(mock_constant)

        self.assertEqual(result, not mock_eq.return_value)

    @patch.object(styles.ConstantRule, "__eq__")
    @patch.object(styles.ConstantRule, "__init__", lambda x, y, z: None)
    def test___ne___different_type(self, mock_eq):
        """Test the ne operator when the other item isn't a StyleConstant."""
        constant = styles.ConstantRule(None, None)

        result = constant.__ne__(MagicMock())

        self.assertEqual(result, NotImplemented)

    # Properties

    @patch.object(styles.ConstantRule, "__init__", lambda x, y, z: None)
    def test_constant_name(self):
        """Test the 'constant_name' property."""
        value = MagicMock(spec=str)
        rule = styles.ConstantRule(None, None)
        rule._constant_name = value

        self.assertEqual(rule.constant_name, value)

    @patch.object(styles.ConstantRule, "__init__", lambda x, y, z: None)
    def test_file_path(self):
        "Test the 'file_path' property."
        value = MagicMock(spec=str)
        rule = styles.ConstantRule(None, None)
        rule._file_path = value

        self.assertEqual(rule.file_path, value)

    @patch.object(styles.ConstantRule, "__init__", lambda x, y, z: None)
    def test_name(self):
        """Test the 'name' property."""
        value = MagicMock(spec=str)
        rule = styles.ConstantRule(None, None)
        rule._name = value

        self.assertEqual(rule.name, value)


# =============================================================================

if __name__ == '__main__':
    unittest.main()
