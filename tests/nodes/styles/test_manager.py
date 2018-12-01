"""Tests for ht.nodes.styles.module module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
from mock import MagicMock, PropertyMock, call, mock_open, patch
import os
import unittest

# Houdini Toolbox Imports
from ht.nodes.styles import constants as consts
from ht.nodes.styles import manager

# Houdini Imports
import hou

reload(manager)

# =============================================================================
# CLASSES
# =============================================================================

class Test_StyleManager(unittest.TestCase):
    """Test ht.nodes.styles.manager.StyleManager."""

    @patch.object(manager.StyleManager, "_build")
    def test___init__(self, mock_build):
        """Test the constructor."""
        mgr = manager.StyleManager()

        self.assertEqual(mgr._constants, {})
        self.assertEqual(mgr._name_rules, {})
        self.assertEqual(mgr._node_type_rules, {})
        self.assertEqual(mgr._tool_rules, {})

        mock_build.assert_called()

    # Properties

    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test_constants(self):
        """Test the 'constants' property."""
        data = MagicMock(spec=dict)
        mgr = manager.StyleManager()

        mgr._constants = data
        self.assertEqual(mgr.constants, data)

    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test_name_rules(self):
        """Test the 'name_rules' property."""
        data = MagicMock(spec=dict)
        mgr = manager.StyleManager()

        mgr._name_rules = data
        self.assertEqual(mgr.name_rules, data)

    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test_node_type_rules(self):
        """Test the 'node_type_rules' property."""
        data = MagicMock(spec=dict)
        mgr = manager.StyleManager()

        mgr._node_type_rules = data
        self.assertEqual(mgr.node_type_rules, data)

    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test_tool_rules(self):
        """Test the 'tool_rules' property."""
        data = MagicMock(spec=dict)
        mgr = manager.StyleManager()

        mgr._tool_rules = data
        self.assertEqual(mgr.tool_rules, data)

    # Non-Public Methods

    # _build

    @patch.object(manager.StyleManager, "_build_rules_from_data")
    @patch.object(manager.StyleManager, "_build_constants_from_data")
    @patch("ht.nodes.styles.manager.json.load")
    @patch("ht.nodes.styles.manager._find_files")
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test__build(self, mock_find, mock_load, mock_build_consts, mock_build_rules):
        """Test building all the data from files."""
        path1 = MagicMock(spec=str)
        path2 = MagicMock(spec=str)

        # Put files in reversed alphabetical order so they will be sorted
        # opposite of their current order in the function.
        mock_files = (path2, path1)
        mock_find.return_value = mock_files

        mgr = manager.StyleManager()

        mock_load.side_effect = ({"key1": "value1"}, {"key2": "value2"})

        expected_data = [
            {"key1": "value1", consts.PATH_KEY: path1},
            {"key2": "value2", consts.PATH_KEY: path2},
        ]

        m = mock_open()

        with patch("__builtin__.open", m):
            mgr._build()

            mock_load.assert_called_with(m())

            m.assert_any_call(path1)
            m.assert_any_call(path2)

        mock_build_consts.assert_called_with(expected_data)
        mock_build_rules.assert_called_with(expected_data)

    # _build_constants_from_data

    @patch.object(manager.StyleManager, "constants", new_callable=PropertyMock)
    @patch("ht.nodes.styles.manager.StyleConstant", autospec=True)
    @patch("ht.nodes.styles.manager._build_shape")
    @patch("ht.nodes.styles.manager._build_color")
    @patch.object(manager.StyleManager, "_build", lambda x: None)
    def test__build_constants_from_data(self, mock_build_color, mock_build_shape, mock_constant, mock_constants):
        """Test building StyleConstants from data."""
        constants = {}
        mock_constants.return_value = constants

        mock_rule1 = MagicMock(spec=dict)
        mock_rule2 = MagicMock(spec=dict)

        mock_color1 = MagicMock(spec=hou.Color)
        mock_color2 = MagicMock(spec=hou.Color)

        color_type1 = MagicMock(spec=str)
        color_type2 = MagicMock(spec=str)

        colors = {
            mock_rule1: (mock_color1, color_type1),
            mock_rule2: (mock_color2, color_type2)
        }

        mock_build_color.side_effect = lambda e: colors[e]

        shape1 = MagicMock(spec=str)
        shape2 = MagicMock(spec=str)

        shapes = {
            mock_rule1: shape1,
            mock_rule2: shape2
        }

        mock_build_shape.side_effect = lambda e: shapes[e]

        path = MagicMock(spec=str)
        name1 = MagicMock(spec=str)
        name2 = MagicMock(spec=str)

        all_data = [
            {
                consts.PATH_KEY: path,
                consts.CONSTANT_DEFINITION_KEY: {
                    name1: mock_rule1,
                    name2: mock_rule2,
                }
            }
        ]

        mgr = manager.StyleManager()

        mgr._build_constants_from_data(all_data)

        mock_build_color.assert_has_calls([call(mock_rule1), call(mock_rule2)], any_order=True)
        mock_build_shape.assert_has_calls([call(mock_rule1), call(mock_rule2)], any_order=True)

        calls = [
            call(name1, mock_color1, color_type1, shape1, path),
            call(name2, mock_color2, color_type2, shape2, path),
        ]

        mock_constant.assert_has_calls(calls, any_order=True)

        self.assertEqual(constants[name1], mock_constant.return_value)
        self.assertEqual(constants[name2], mock_constant.return_value)

    @patch("ht.nodes.styles.manager.StyleConstant", autospec=True)
    @patch("ht.nodes.styles.manager._build_shape")
    @patch("ht.nodes.styles.manager._build_color")
    @patch.object(manager.StyleManager, "_build", lambda x: None)
    def test__build_constants_from_data__no_constants(self, mock_build_color, mock_build_shape, mock_constant):
        """Test building StyleConstants from data when there are no constant definitions."""
        all_data = [{consts.PATH_KEY: MagicMock(spec=str)}]

        mgr = manager.StyleManager()

        mgr._build_constants_from_data(all_data)

        mock_build_color.assert_not_called()
        mock_build_shape.assert_not_called()
        mock_constant.assert_not_called()

    # _build_rules_from_data

    @patch("ht.nodes.styles.manager._build_category_rules")
    @patch.object(manager.StyleManager, "_build", lambda x: None)
    def test__build_rules_from_data__no_rules(self, mock_build):
        """Test building rules from data when the data contains no rules."""
        all_data = [{consts.PATH_KEY: MagicMock(spec=str)}]

        mgr = manager.StyleManager()
        mgr._build_rules_from_data(all_data)

        mock_build.assert_not_called()

    @patch.object(manager.StyleManager, "constants", new_callable=PropertyMock)
    @patch("ht.nodes.styles.manager._build_category_rules")
    @patch.object(manager.StyleManager, "_build", lambda x: None)
    def test__build_rules_from_data__names(self, mock_build, mock_constants):
        """Test building rules from data when the data contains name rules."""
        mock_rule1 = MagicMock(spec=dict)
        mock_rule2 = MagicMock(spec=dict)

        path = MagicMock(spec=str)
        all_data = [
            {
                consts.PATH_KEY: path,
                consts.RULES_KEY: {
                    "name_rules": {"Sop": [mock_rule1, mock_rule2]},
                }
            }
        ]

        mgr = manager.StyleManager()

        mgr._build_rules_from_data(all_data)

        self.assertEqual(mgr.name_rules["Sop"], {})

        mock_build.assert_called_with([mock_rule1, mock_rule2], {}, path, mock_constants.return_value)

    @patch.object(manager.StyleManager, "constants", new_callable=PropertyMock)
    @patch("ht.nodes.styles.manager._build_category_rules")
    @patch.object(manager.StyleManager, "_build", lambda x: None)
    def test__build_rules_from_data__nodes(self, mock_build, mock_constants):
        """Test building rules from data when the data contains node type rules."""
        mock_rule1 = MagicMock(spec=dict)
        mock_rule2 = MagicMock(spec=dict)

        path = MagicMock(spec=str)
        all_data = [
            {
                consts.PATH_KEY: path,
                consts.RULES_KEY: {
                    "node_type_rules": {"Sop": [mock_rule1, mock_rule2]},
                }
            }
        ]

        mgr = manager.StyleManager()

        mgr._build_rules_from_data(all_data)

        self.assertEqual(mgr.node_type_rules["Sop"], {})

        mock_build.assert_called_with([mock_rule1, mock_rule2], {}, path, mock_constants.return_value)

    @patch.object(manager.StyleManager, "constants", new_callable=PropertyMock)
    @patch("ht.nodes.styles.manager._build_category_rules")
    @patch.object(manager.StyleManager, "_build", lambda x: None)
    def test__build_rules_from_data__tools(self, mock_build, mock_constants):
        """Test building rules from data when the data contains tool rules."""
        mock_rule1 = MagicMock(spec=dict)
        mock_rule2 = MagicMock(spec=dict)

        path = MagicMock(spec=str)
        all_data = [
            {
                consts.PATH_KEY: path,
                consts.RULES_KEY: {"tool_rules": {"Sop": [mock_rule1, mock_rule2]}}
            }
        ]

        mgr = manager.StyleManager()

        mgr._build_rules_from_data(all_data)

        self.assertEqual(mgr.tool_rules["Sop"], {})

        mock_build.assert_called_with([mock_rule1, mock_rule2], {}, path, mock_constants.return_value)

    # _get_manager_generator_style

    @patch.object(manager.StyleManager, "_resolve_rule")
    @patch.object(manager.StyleManager, "node_type_rules", new_callable=PropertyMock)
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test__get_manager_generator_style_manager__none(self, mock_rules, mock_resolve):
        """Test getting a style for a manager when no style exists."""
        mock_rules.return_value = {"Sop": {}}

        mock_category = MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category
        mock_type.isManager.return_value = True

        mgr = manager.StyleManager()

        result = mgr._get_manager_generator_style(mock_type)

        self.assertIsNone(result)

        mock_resolve.assert_not_called()

    @patch.object(manager.StyleManager, "_resolve_rule")
    @patch.object(manager.StyleManager, "node_type_rules", new_callable=PropertyMock)
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test__get_manager_generator_style_manager__category(self, mock_rules, mock_resolve):
        """Test getting a style for a manager where a specific category style exists."""
        mock_rule = MagicMock()

        mock_rules.return_value = {"Sop": {consts.MANAGER_TYPE_KEY: mock_rule}}

        mock_category = MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category
        mock_type.isManager.return_value = True
        mock_type.isGenerator.return_value = False

        mgr = manager.StyleManager()

        result = mgr._get_manager_generator_style(mock_type)

        self.assertEqual(result, mock_resolve.return_value)

        mock_resolve.assert_called_with(mock_rule)

    @patch.object(manager.StyleManager, "_resolve_rule")
    @patch.object(manager.StyleManager, "node_type_rules", new_callable=PropertyMock)
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test__get_manager_generator_style__manager_all(self, mock_rules, mock_resolve):
        """Test getting a style for a manager where a generic 'all' style exists."""
        mock_rule = MagicMock()

        mock_rules.return_value = {"all": {consts.MANAGER_TYPE_KEY: mock_rule}}

        mock_category = MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category
        mock_type.isManager.return_value = True
        mock_type.isGenerator.return_value = False

        mgr = manager.StyleManager()

        result = mgr._get_manager_generator_style(mock_type)

        self.assertEqual(result, mock_resolve.return_value)

        mock_resolve.assert_called_with(mock_rule)

    @patch.object(manager.StyleManager, "_resolve_rule")
    @patch.object(manager.StyleManager, "node_type_rules", new_callable=PropertyMock)
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test__get_manager_generator_style__generator_none(self, mock_rules, mock_resolve):
        """Test getting a style for a generator when no style exists."""
        mock_rules.return_value = {"Sop": {}}

        mock_category = MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category
        mock_type.isGenerator.return_value = True
        mock_type.isManager.return_value = False

        mgr = manager.StyleManager()

        result = mgr._get_manager_generator_style(mock_type)

        self.assertIsNone(result)

        mock_resolve.assert_not_called()

    @patch.object(manager.StyleManager, "_resolve_rule")
    @patch.object(manager.StyleManager, "node_type_rules", new_callable=PropertyMock)
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test__get_manager_generator_style__generator_category(self, mock_rules, mock_resolve):
        """Test getting a style for a generator where a specific category style exists."""
        mock_rule = MagicMock()

        mock_rules.return_value = {"Sop": {consts.GENERATOR_TYPE_KEY: mock_rule}}

        mock_category = MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category
        mock_type.isGenerator.return_value = True
        mock_type.isManager.return_value = False

        mgr = manager.StyleManager()

        result = mgr._get_manager_generator_style(mock_type)

        self.assertEqual(result, mock_resolve.return_value)

        mock_resolve.assert_called_with(mock_rule)

    @patch.object(manager.StyleManager, "_resolve_rule")
    @patch.object(manager.StyleManager, "node_type_rules", new_callable=PropertyMock)
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test__get_manager_generator_style__generator_all(self, mock_rules, mock_resolve):
        """Test getting a style for a generator where a generic 'all' style exists."""
        mock_rule = MagicMock()

        mock_rules.return_value = {consts.ALL_CATEGORY_KEY: {consts.GENERATOR_TYPE_KEY: mock_rule}}

        mock_category = MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category
        mock_type.isGenerator.return_value = True
        mock_type.isManager.return_value = False

        mgr = manager.StyleManager()

        result = mgr._get_manager_generator_style(mock_type)

        self.assertEqual(result, mock_resolve.return_value)

        mock_resolve.assert_called_with(mock_rule)

    @patch.object(manager.StyleManager, "node_type_rules", new_callable=PropertyMock)
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test__get_manager_generator_style__error(self, mock_rules):
        """Test getting a style when the node type is neither a manager or generator."""
        mock_rule = MagicMock()

        mock_rules.return_value = {consts.ALL_CATEGORY_KEY: {consts.GENERATOR_TYPE_KEY: mock_rule}}

        mock_category = MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category
        mock_type.isGenerator.return_value = False
        mock_type.isManager.return_value = False

        mgr = manager.StyleManager()

        with self.assertRaises(hou.OperationFailed):
            mgr._get_manager_generator_style(mock_type)

    # _get_name_style

    @patch.object(manager.StyleManager, "_resolve_rule")
    @patch("hou.patternMatch", return_value=True)
    @patch.object(manager.StyleManager, "name_rules", new_callable=PropertyMock)
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test__get_name_style__category(self, mock_name_rules, mock_match, mock_resolve):
        """Test getting a node name style which matches a specific category."""
        style_name = MagicMock(spec=str)

        node_name = MagicMock(spec=str)

        mock_rule = MagicMock(spec=manager.StyleRule)
        type(mock_rule).name = PropertyMock(return_value=style_name)

        mock_name_rules.return_value = {"Sop": {node_name: mock_rule}}

        mock_category = MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category

        mock_node = MagicMock(spec=hou.Node)
        mock_node.name.return_value = node_name
        mock_node.type.return_value = mock_type

        mgr = manager.StyleManager()

        result = mgr._get_name_style(mock_node)

        self.assertEqual(result, mock_resolve.return_value)
        mock_match.assert_called_with(style_name, node_name)

        mock_resolve.assert_called_with(mock_rule)

    @patch.object(manager.StyleManager, "_resolve_rule")
    @patch("hou.patternMatch", return_value=True)
    @patch.object(manager.StyleManager, "name_rules", new_callable=PropertyMock)
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test__get_name_style__all(self, mock_name_rules, mock_match, mock_resolve):
        """Test getting a node name style which matches the generic 'all' category."""
        style_name = MagicMock(spec=str)

        node_name = MagicMock(spec=str)

        mock_rule = MagicMock(spec=manager.StyleRule)
        type(mock_rule).name = PropertyMock(return_value=style_name)

        mock_name_rules.return_value = {consts.ALL_CATEGORY_KEY: {node_name: mock_rule}}

        mock_category = MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category

        mock_node = MagicMock(spec=hou.Node)
        mock_node.name.return_value = node_name
        mock_node.type.return_value = mock_type

        mgr = manager.StyleManager()

        result = mgr._get_name_style(mock_node)

        self.assertEqual(result, mock_resolve.return_value)
        mock_match.assert_called_with(style_name, node_name)

        mock_resolve.assert_called_with(mock_rule)

    @patch.object(manager.StyleManager, "_resolve_rule")
    @patch("hou.patternMatch", return_value=False)
    @patch.object(manager.StyleManager, "name_rules", new_callable=PropertyMock)
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test__get_name_style__no_match(self, mock_name_rules, mock_match, mock_resolve):
        """Test getting a node name style that does not match any rules."""
        style_name = MagicMock(spec=str)

        node_name = MagicMock(spec=str)

        mock_rule = MagicMock(spec=manager.StyleRule)
        type(mock_rule).name = PropertyMock(return_value=style_name)

        mock_name_rules.return_value = {consts.ALL_CATEGORY_KEY: {node_name: mock_rule}}

        mock_category = MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category

        mock_node = MagicMock(spec=hou.Node)
        mock_node.name.return_value = node_name
        mock_node.type.return_value = mock_type

        mgr = manager.StyleManager()

        result = mgr._get_name_style(mock_node)

        self.assertIsNone(result)
        mock_match.assert_called_with(style_name, node_name)

        mock_resolve.assert_not_called()

    # _get_node_type_style

    @patch.object(manager.StyleManager, "_resolve_rule")
    @patch("hou.patternMatch", return_value=True)
    @patch.object(manager.StyleManager, "node_type_rules", new_callable=PropertyMock)
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test__get_node_type_style__category(self, mock_node_type_rules, mock_match, mock_resolve):
        """Test getting a node type style which matches a specific category."""
        style_name = MagicMock(spec=str)

        node_type_name = MagicMock(spec=str)

        mock_rule = MagicMock(spec=manager.StyleRule)
        type(mock_rule).name = PropertyMock(return_value=style_name)

        mock_node_type_rules.return_value = {"Sop": {node_type_name: mock_rule}}

        mock_category = MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category
        mock_type.nameComponents.return_value = ("", "", node_type_name, "1")

        mgr = manager.StyleManager()

        result = mgr._get_node_type_style(mock_type)

        self.assertEqual(result, mock_resolve.return_value)
        mock_match.assert_called_with(style_name, node_type_name)

        mock_resolve.assert_called_with(mock_rule)

    @patch.object(manager.StyleManager, "_resolve_rule")
    @patch("hou.patternMatch", return_value=True)
    @patch.object(manager.StyleManager, "node_type_rules", new_callable=PropertyMock)
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test__get_node_type_style__all(self, mock_node_type_rules, mock_match, mock_resolve):
        """Test getting a node type style which matches the generic 'all' category."""
        style_name = MagicMock(spec=str)

        node_type_name = MagicMock(spec=str)

        mock_rule = MagicMock(spec=manager.StyleRule)
        type(mock_rule).name = PropertyMock(return_value=style_name)

        mock_node_type_rules.return_value = {consts.ALL_CATEGORY_KEY: {node_type_name: mock_rule}}

        mock_category = MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category
        mock_type.nameComponents.return_value = ("", "", node_type_name, "1")

        mgr = manager.StyleManager()

        result = mgr._get_node_type_style(mock_type)

        self.assertEqual(result, mock_resolve.return_value)
        mock_match.assert_called_with(style_name, node_type_name)

        mock_resolve.assert_called_with(mock_rule)

    @patch.object(manager.StyleManager, "_resolve_rule")
    @patch("hou.patternMatch", return_value=False)
    @patch.object(manager.StyleManager, "node_type_rules", new_callable=PropertyMock)
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test__get_node_type_style__no_match(self, mock_node_type_rules, mock_match, mock_resolve):
        """Test getting a node type style that does not match any rules."""
        style_name = MagicMock(spec=str)

        node_type_name = MagicMock(spec=str)

        mock_rule = MagicMock(spec=manager.StyleRule)
        type(mock_rule).name = PropertyMock(return_value=style_name)

        mock_node_type_rules.return_value = {consts.ALL_CATEGORY_KEY: {node_type_name: mock_rule}}

        mock_category = MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category
        mock_type.nameComponents.return_value = ("", "", node_type_name, "1")

        mgr = manager.StyleManager()

        result = mgr._get_node_type_style(mock_type)

        self.assertEqual(result, None)

        mock_match.assert_called_with(style_name, node_type_name)

        mock_resolve.assert_not_called()

    # _get_tool_style

    @patch.object(manager.StyleManager, "_resolve_rule")
    @patch("hou.patternMatch", return_value=True)
    @patch.object(manager.StyleManager, "tool_rules", new_callable=PropertyMock)
    @patch("ht.nodes.styles.manager._get_tool_menu_locations")
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test__get_tool_style__category(self, mock_get_locations, mock_tool_rules, mock_match, mock_resolve):
        """Test getting a tool style which matches a specific category."""
        location = MagicMock(spec=str)

        locations = (location, )
        mock_get_locations.return_value = locations

        style_name = MagicMock(spec=str)

        mock_rule = MagicMock(spec=manager.StyleRule)
        type(mock_rule).name = PropertyMock(return_value=style_name)

        mock_tool_rules.return_value = {"Sop": {location: mock_rule}}

        mock_category = MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category

        mgr = manager.StyleManager()

        result = mgr._get_tool_style(mock_type)

        self.assertEqual(result, mock_resolve.return_value)

        mock_get_locations.assert_called_with(mock_type)

        mock_match.assert_called_with(style_name, location)

        mock_resolve.assert_called_with(mock_rule)

    @patch.object(manager.StyleManager, "_resolve_rule")
    @patch("hou.patternMatch")
    @patch.object(manager.StyleManager, "tool_rules", new_callable=PropertyMock)
    @patch("ht.nodes.styles.manager._get_tool_menu_locations")
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test__get_tool_style__all(self, mock_get_locations, mock_tool_rules, mock_match, mock_resolve):
        """Test getting a tool style which matches the generic 'all' category."""
        location = MagicMock(spec=str)
        mock_get_locations.return_value = (location, )

        style_name = MagicMock(spec=str)

        mock_rule = MagicMock(spec=manager.StyleRule)
        type(mock_rule).name = PropertyMock(return_value=style_name)

        mock_tool_rules.return_value = {consts.ALL_CATEGORY_KEY: {location: mock_rule}}

        mock_category = MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category

        mgr = manager.StyleManager()

        mock_match.return_value = True

        result = mgr._get_tool_style(mock_type)

        self.assertEqual(result, mock_resolve.return_value)

        mock_get_locations.assert_called_with(mock_type)

        mock_match.assert_called_with(style_name, location)

        mock_resolve.assert_called_with(mock_rule)

    @patch.object(manager.StyleManager, "_resolve_rule")
    @patch("hou.patternMatch", return_value=False)
    @patch.object(manager.StyleManager, "tool_rules", new_callable=PropertyMock)
    @patch("ht.nodes.styles.manager._get_tool_menu_locations")
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test__get_tool_style__no_match(self, mock_get_locations, mock_tool_rules, mock_match, mock_resolve):
        """Test getting a tool style that does not match any rules."""
        location = MagicMock(spec=str)
        mock_locations = (location, )
        mock_get_locations.return_value = mock_locations

        style_name = MagicMock(spec=str)

        mock_rule = MagicMock(spec=manager.StyleRule)
        type(mock_rule).name = PropertyMock(return_value=style_name)

        mock_tool_rules.return_value = {consts.ALL_CATEGORY_KEY: {location: mock_rule}}

        mock_category = MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category

        mgr = manager.StyleManager()

        result = mgr._get_tool_style(mock_type)

        self.assertIsNone(result)

        mock_get_locations.assert_called_with(mock_type)

        mock_match.assert_called_with(style_name, location)

        mock_resolve.assert_not_called()

    # _resolve_rule

    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test__resolve_rule__style(self):
        """Test resolving a rule which is a StyleRule."""
        mock_rule = MagicMock(spec=manager.StyleRule)

        mgr = manager.StyleManager()

        result = mgr._resolve_rule(mock_rule)

        self.assertEqual(result, mock_rule)

    @patch.object(manager.StyleManager, "constants", new_callable=PropertyMock)
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test__resolve_rule__constant(self, mock_constants):
        """Test resolving a rule which is a ConstantRule."""
        constant_name = MagicMock(spec=str)

        mock_constant = MagicMock(spec=manager.StyleConstant)
        mock_constants.return_value = {constant_name: mock_constant}

        mock_rule = MagicMock(spec=manager.ConstantRule)
        type(mock_rule).constant_name = PropertyMock(return_value=constant_name)

        mgr = manager.StyleManager()

        result = mgr._resolve_rule(mock_rule)

        self.assertEqual(result, mock_constant)

    # style_node

    @patch.object(manager.StyleManager, "_get_tool_style")
    @patch.object(manager.StyleManager, "_get_node_type_style")
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test_style_node__by_type(self, mock_get_type, mock_get_tool):
        """Style a node by the node type."""
        mock_style = MagicMock(spec=manager.StyleRule)
        mock_get_type.return_value = mock_style

        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.isGenerator.return_value = False
        mock_type.isManager.return_value = False

        mock_node = MagicMock(spec=hou.Node)
        mock_node.type.return_value = mock_type

        mgr = manager.StyleManager()

        mgr.style_node(mock_node)

        mock_style.apply_to_node.assert_called_with(mock_node)

        mock_get_type.assert_called_with(mock_type)

        mock_get_tool.assert_not_called()
        mock_type.isManager.assert_not_called()

    @patch.object(manager.StyleManager, "_get_tool_style")
    @patch.object(manager.StyleManager, "_get_node_type_style", return_value=None)
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test_style_node__by_tool(self, mock_get_type, mock_get_tool):
        """Style a node by the tool menu location."""
        mock_style = MagicMock(spec=manager.StyleRule)
        mock_get_tool.return_value = mock_style

        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.isGenerator.return_value = False
        mock_type.isManager.return_value = False

        mock_node = MagicMock(spec=hou.Node)
        mock_node.type.return_value = mock_type

        mgr = manager.StyleManager()

        mgr.style_node(mock_node)

        mock_style.apply_to_node.assert_called_with(mock_node)

        mock_get_type.assert_called_with(mock_type)
        mock_get_tool.assert_called_with(mock_type)

        mock_type.isManager.assert_not_called()

    @patch.object(manager.StyleManager, "_get_manager_generator_style")
    @patch.object(manager.StyleManager, "_get_tool_style", return_value=None)
    @patch.object(manager.StyleManager, "_get_node_type_style", return_value=None)
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test_style_node__by_manager(self, mock_get_type, mock_get_tool, mock_get_manager):
        """Style a node because it is a manager."""
        mock_style = MagicMock(spec=manager.StyleRule)
        mock_get_manager.return_value = mock_style

        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.isGenerator.return_value = False
        mock_type.isManager.return_value = True

        mock_node = MagicMock(spec=hou.Node)
        mock_node.type.return_value = mock_type

        mgr = manager.StyleManager()

        mgr.style_node(mock_node)

        mock_style.apply_to_node.assert_called_with(mock_node)

        mock_get_type.assert_called_with(mock_type)
        mock_get_tool.assert_called_with(mock_type)

        mock_type.isGenerator.assert_not_called()

        mock_get_manager.assert_called_with(mock_type)

    @patch.object(manager.StyleManager, "_get_manager_generator_style")
    @patch.object(manager.StyleManager, "_get_tool_style", return_value=None)
    @patch.object(manager.StyleManager, "_get_node_type_style", return_value=None)
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test_style_node__by_generator(self, mock_get_type, mock_get_tool, mock_get_manager):
        """Style a node because it is a generator."""
        mock_style = MagicMock(spec=manager.StyleRule)
        mock_get_manager.return_value = mock_style

        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.isGenerator.return_value = True
        mock_type.isManager.return_value = False

        mock_node = MagicMock(spec=hou.Node)
        mock_node.type.return_value = mock_type

        mgr = manager.StyleManager()

        mgr.style_node(mock_node)

        mock_style.apply_to_node.assert_called_with(mock_node)

        mock_get_type.assert_called_with(mock_type)
        mock_get_tool.assert_called_with(mock_type)
        mock_get_manager.assert_called_with(mock_type)

    @patch.object(manager.StyleManager, "_get_manager_generator_style")
    @patch.object(manager.StyleManager, "_get_tool_style", return_value=None)
    @patch.object(manager.StyleManager, "_get_node_type_style", return_value=None)
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test_style_node__no_match(self, mock_get_type, mock_get_tool, mock_get_manager):
        """Try to style a node but do not match any rule types."""
        mock_style = MagicMock(spec=manager.StyleRule)
        mock_get_manager.return_value = mock_style

        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.isGenerator.return_value = False
        mock_type.isManager.return_value = False

        mock_node = MagicMock(spec=hou.Node)
        mock_node.type.return_value = mock_type

        mgr = manager.StyleManager()

        mgr.style_node(mock_node)

        mock_get_type.assert_called_with(mock_type)
        mock_get_tool.assert_called_with(mock_type)
        mock_get_manager.assert_not_called()

    # style_node_by_name

    @patch.object(manager.StyleManager, "_get_name_style")
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test_style_node_by_name(self, mock_get_name):
        """Style a node by its name."""
        mock_style = MagicMock(spec=manager.StyleRule)

        mock_get_name.return_value = mock_style

        mock_node = MagicMock(spec=hou.Node)

        mgr = manager.StyleManager()

        mgr.style_node_by_name(mock_node)

        mock_style.apply_to_node.assert_called_with(mock_node)

        mock_get_name.assert_called_with(mock_node)

    @patch.object(manager.StyleManager, "_get_name_style", return_value=None)
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test_style_node_by_name__no_match(self, mock_get_name):
        """Try to style a node by its name but do not match any rules."""
        mock_node = MagicMock(spec=hou.Node)

        mgr = manager.StyleManager()

        mgr.style_node_by_name(mock_node)

        mock_get_name.assert_called_with(mock_node)

    # reload

    @patch.object(manager.StyleManager, "_build")
    @patch.object(manager.StyleManager, "tool_rules", new_callable=PropertyMock)
    @patch.object(manager.StyleManager, "node_type_rules", new_callable=PropertyMock)
    @patch.object(manager.StyleManager, "name_rules", new_callable=PropertyMock)
    @patch.object(manager.StyleManager, "constants",  new_callable=PropertyMock)
    @patch.object(manager.StyleManager, "__init__", lambda x: None)
    def test_reload(self, mock_constants, mock_name_rules, mock_node_type_rules, mock_tool_rules, mock_build):
        """Test reloading all the data."""
        mgr = manager.StyleManager()

        mock_constants.return_value = MagicMock(spec=dict)
        mock_name_rules.return_value = MagicMock(spec=dict)
        mock_node_type_rules.return_value = MagicMock(spec=dict)
        mock_tool_rules.return_value = MagicMock(spec=dict)

        mgr.reload()

        mgr.constants.clear.assert_called_once()
        mgr.name_rules.clear.assert_called_once()
        mgr.node_type_rules.clear.assert_called_once()
        mgr.tool_rules.clear.assert_called_once()

        mock_build.assert_called()


class Test__build_category_rules(unittest.TestCase):
    """Test ht.nodes.styles.manager._build_category_rules."""

    def test_invalid_constant(self):
        """Test building with an invalid constant."""
        path = MagicMock(spec=str)
        constants = {}

        rules = [
            {
                consts.RULE_NAME_KEY: MagicMock(spec=str),
                consts.RULE_CONSTANT_KEY: MagicMock(spec=str)
            }
        ]

        with self.assertRaises(manager.ConstantDoesNotExistError):
            manager._build_category_rules(rules, {}, path, constants)

    @patch("ht.nodes.styles.manager.ConstantRule", autospec=True)
    @patch("ht.nodes.styles.manager._build_color")
    def test_constant(self, mock_build_color, mock_const_rule):
        """Test building a ConstantRule."""
        constant_name = MagicMock(spec=str)

        category_map = {}

        path = MagicMock(spec=str)
        constants = {constant_name: MagicMock(spec=manager.StyleConstant)}

        rule_name = MagicMock(spec=str)

        rules = [
            {
                consts.RULE_NAME_KEY: rule_name,
                consts.RULE_CONSTANT_KEY: constant_name
            }
        ]

        manager._build_category_rules(rules, category_map, path, constants)

        self.assertEqual(category_map, {rule_name: mock_const_rule.return_value})

        mock_const_rule.assert_called_with(rule_name, constant_name, path)

        mock_build_color.assert_not_called()

    @patch("ht.nodes.styles.manager.StyleRule", autospec=True)
    @patch("ht.nodes.styles.manager.ConstantRule", autospec=True)
    @patch("ht.nodes.styles.manager._build_shape")
    @patch("ht.nodes.styles.manager._build_color")
    def test_style(self, mock_build_color, mock_build_shape, mock_const_rule, mock_style_rule):
        """Test building a StyleRule."""
        mock_color = MagicMock(spec=hou.Color)
        color_type = MagicMock(spec=str)
        mock_build_color.return_value = (mock_color, color_type)

        shape = MagicMock(spec=str)
        mock_build_shape.return_value = shape

        category_map = {}
        path = MagicMock(spec=str)

        rule_name = MagicMock(spec=str)

        data = {consts.RULE_NAME_KEY: rule_name}

        rules = [data]

        manager._build_category_rules(rules, category_map, path, {})

        self.assertEqual(category_map, {rule_name: mock_style_rule.return_value})

        mock_style_rule.assert_called_with(rule_name, mock_color, color_type, shape, path)

        mock_const_rule.assert_not_called()


class Test__build_color(unittest.TestCase):
    """Test ht.nodes.styles.manager._build_color."""

    def test_no_data(self):
        """Test building a color when there is no data."""
        result = manager._build_color({})

        self.assertEqual(result, (None, None))

    @patch("hou.colorType")
    def test_invalid_color_type(self, mock_type):
        """Test building a color when the type is invalid."""
        del mock_type.foo

        data = {consts.RULE_COLOR_KEY: {consts.RULE_COLOR_TYPE_KEY: "foo"}}

        with self.assertRaises(manager.InvalidColorTypeError):
            manager._build_color(data)

    @patch("hou.Color", autospec=True)
    def test_rgb_single(self, mock_color):
        """Test building an RGB color with a single float value."""
        color_type = "RGB"
        value = 0.3
        data = {consts.RULE_COLOR_KEY: {consts.RULE_COLOR_TYPE_KEY: color_type, consts.RULE_COLOR_VALUE_KEY: value}}

        result = manager._build_color(data)

        self.assertEqual(result, (mock_color(), color_type))

        mock_color().setRGB.assert_called_with([value] * 3)

    @patch("hou.Color", autospec=True)
    def test_rgb(self, mock_color):
        """Test building an RGB color with 3 float values."""
        color_type = "RGB"
        value = [0.3, 0.1, 0.6]
        data = {consts.RULE_COLOR_KEY: {consts.RULE_COLOR_TYPE_KEY: color_type, consts.RULE_COLOR_VALUE_KEY: value}}

        result = manager._build_color(data)

        self.assertEqual(result, (mock_color(), color_type))

        mock_color().setRGB.assert_called_with(value)

    @patch("hou.Color", autospec=True)
    def test_hsl(self, mock_color):
        """Test building an HSL color."""
        color_type = "HSL"
        value = [0.3, 0.1, 0.6]
        data = {consts.RULE_COLOR_KEY: {consts.RULE_COLOR_TYPE_KEY: color_type, consts.RULE_COLOR_VALUE_KEY: value}}

        result = manager._build_color(data)

        self.assertEqual(result, (mock_color(), color_type))

        mock_color().setHSL.assert_called_with(value)

    @patch("hou.Color", autospec=True)
    def test_hsv(self, mock_color):
        """Test building an HSV color."""
        color_type = "HSV"
        value = [0.3, 0.1, 0.6]
        data = {consts.RULE_COLOR_KEY: {consts.RULE_COLOR_TYPE_KEY: color_type, consts.RULE_COLOR_VALUE_KEY: value}}

        result = manager._build_color(data)

        self.assertEqual(result, (mock_color(), color_type))

        mock_color().setHSV.assert_called_with(value)

    @patch("hou.Color", autospec=True)
    def test_lab(self, mock_color):
        """Test building a LAB color."""
        color_type = "LAB"
        value = [0.3, 0.1, 0.6]
        data = {consts.RULE_COLOR_KEY: {consts.RULE_COLOR_TYPE_KEY: color_type, consts.RULE_COLOR_VALUE_KEY: value}}

        result = manager._build_color(data)

        self.assertEqual(result, (mock_color(), color_type))

        mock_color().setLAB.assert_called_with(value)

    @patch("hou.Color", autospec=True)
    def test_xyz(self, mock_color):
        """Test building an XYZ color."""
        color_type = "XYZ"
        value = [0.3, 0.1, 0.6]
        data = {consts.RULE_COLOR_KEY: {consts.RULE_COLOR_TYPE_KEY: color_type, consts.RULE_COLOR_VALUE_KEY: value}}

        result = manager._build_color(data)

        self.assertEqual(result, (mock_color(), color_type))

        mock_color().setXYZ.assert_called_with(value)


class Test__build_shape(unittest.TestCase):
    """Test ht.nodes.styles.manager._build_shape."""

    def test(self):
        """Test building a shape where there is a shape key."""
        shape = "shape"
        mock_rule = {consts.RULE_SHAPE_KEY: shape}

        result = manager._build_shape(mock_rule)

        self.assertEqual(result, shape)

    def test_no_rule(self):
        """Test building a shape where there is not a shape key."""
        result = manager._build_shape({})

        self.assertIsNone(result)


class Test__find_files(unittest.TestCase):
    """Test ht.nodes.styles.manager._find_files."""

    @patch("ht.nodes.styles.manager.glob.glob")
    @patch("hou.findDirectories")
    def test_no_dirs(self, mock_find, mock_glob):
        """Test finding files where there are no config/styles folders in the HOUDINI_PATH."""
        def raise_error(*args, **kwargs):
            raise hou.OperationFailed()

        mock_find.side_effect = raise_error

        result = manager._find_files()

        self.assertEqual(result, ())

        mock_glob.assert_not_called()

    @patch("ht.nodes.styles.manager.glob.glob")
    @patch("hou.findDirectories")
    def test(self, mock_find, mock_glob):
        """Test finding files where there are valid config/styles folders in the HOUDINI_PATH."""
        dir1 = os.path.join("/", "some", "dir1")
        dir2 = os.path.join("/", "some", "dir2")

        file1 = os.path.join(dir1, "file1.json")
        file2 = os.path.join(dir1, "file2.json")
        file3 = os.path.join(dir2, "file3.json")

        mock_find.return_value = (dir1, dir2)

        mock_glob.side_effect = ((file1, file2), (file3,))

        expected = (file1, file2, file3)
        result = manager._find_files()

        self.assertEqual(result, expected)

        calls = [call(os.path.join(dir1, "*.json")), call(os.path.join(dir2, "*.json"))]

        mock_glob.assert_has_calls(calls)


class Test__get_tool_menu_locations(unittest.TestCase):
    """Test ht.nodes.styles.manager._get_tool_menu_locations."""

    @patch("hou.shelves.defaultToolName")
    @patch("hou.shelves.tools", return_value={})
    def test_no_match(self, mock_get_tools, mock_default_name):
        """Test getting tab menu locations when no default tool exists."""
        mock_category = MagicMock(hou.NodeTypeCategory)

        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category

        result = manager._get_tool_menu_locations(mock_type)

        self.assertEqual(result, ())

        mock_default_name.assert_called_with(
            mock_category.name.return_value,
            mock_type.name.return_value
        )

    @patch("hou.shelves.defaultToolName")
    @patch("hou.shelves.tools")
    def test(self, mock_get_tools, mock_default_name):
        """Test getting tab menu locations when the default tool exists."""
        mock_tool = MagicMock(spec=hou.Tool)

        mock_get_tools.return_value = {mock_default_name.return_value: mock_tool}

        mock_category = MagicMock(hou.NodeTypeCategory)

        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category

        result = manager._get_tool_menu_locations(mock_type)

        self.assertEqual(result, mock_tool.toolMenuLocations.return_value)

        mock_default_name.assert_called_with(
            mock_category.name.return_value,
            mock_type.name.return_value
        )

# =============================================================================

if __name__ == '__main__':
    unittest.main()
