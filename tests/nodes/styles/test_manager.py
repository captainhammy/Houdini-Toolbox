"""Tests for ht.nodes.styles.module module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import os

# Third Party Imports
import pytest

# Houdini Toolbox Imports
from ht.nodes.styles import constants as consts
from ht.nodes.styles import manager

# Houdini Imports
import hou


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def init_manager(mocker):
    """Fixture to initialize a style constant."""
    mocker.patch.object(manager.StyleManager, "__init__", lambda x: None)

    def _create():
        return manager.StyleManager()

    return _create


# =============================================================================
# TESTS
# =============================================================================


class Test_StyleManager:
    """Test ht.nodes.styles.manager.StyleManager."""

    def test___init__(self, mocker):
        """Test the constructor."""
        mock_build = mocker.patch.object(manager.StyleManager, "_build")

        mgr = manager.StyleManager()

        assert mgr._constants == {}
        assert mgr._name_rules == {}
        assert mgr._node_type_rules == {}
        assert mgr._tool_rules == {}

        mock_build.assert_called()

    # Properties

    def test_constants(self, init_manager, mocker):
        """Test the 'constants' property."""
        mock_value = mocker.MagicMock(spec=dict)

        mgr = init_manager()
        mgr._constants = mock_value
        assert mgr.constants == mock_value

    def test_name_rules(self, init_manager, mocker):
        """Test the 'name_rules' property."""
        mock_value = mocker.MagicMock(spec=dict)

        mgr = init_manager()
        mgr._name_rules = mock_value
        assert mgr.name_rules == mock_value

    def test_node_type_rules(self, init_manager, mocker):
        """Test the 'node_type_rules' property."""
        mock_value = mocker.MagicMock(spec=dict)

        mgr = init_manager()
        mgr._node_type_rules = mock_value
        assert mgr.node_type_rules == mock_value

    def test_tool_rules(self, init_manager, mocker):
        """Test the 'tool_rules' property."""
        mock_value = mocker.MagicMock(spec=dict)

        mgr = init_manager()
        mgr._tool_rules = mock_value
        assert mgr.tool_rules == mock_value

    # Non-Public Methods

    # _build

    def test__build(self, init_manager, mocker):
        """Test building all the data from files."""
        mock_find = mocker.patch("ht.nodes.styles.manager._find_files")
        mock_load = mocker.patch("ht.nodes.styles.manager.json.load")
        mock_build_consts = mocker.patch.object(
            manager.StyleManager, "_build_constants_from_data"
        )
        mock_build_rules = mocker.patch.object(
            manager.StyleManager, "_build_rules_from_data"
        )

        path1 = mocker.MagicMock(spec=str)
        path2 = mocker.MagicMock(spec=str)

        # Put files in reversed alphabetical order so they will be sorted
        # opposite of their current order in the function.
        mock_files = (path2, path1)
        mock_find.return_value = mock_files

        mgr = init_manager()

        mock_load.side_effect = ({"key1": "value1"}, {"key2": "value2"})

        expected_data = [
            {"key1": "value1", consts.PATH_KEY: path1},
            {"key2": "value2", consts.PATH_KEY: path2},
        ]

        mock_handle = mocker.mock_open()

        mocker.patch("builtins.open", mock_handle)
        mgr._build()

        mock_load.assert_called_with(mock_handle())

        mock_handle.assert_any_call(path1)
        mock_handle.assert_any_call(path2)

        mock_build_consts.assert_called_with(expected_data)
        mock_build_rules.assert_called_with(expected_data)

    # _build_constants_from_data

    def test__build_constants_from_data(self, init_manager, mocker):
        """Test building StyleConstants from data."""
        mock_build_color = mocker.patch("ht.nodes.styles.manager._build_color")
        mock_build_shape = mocker.patch("ht.nodes.styles.manager._build_shape")
        mock_constant = mocker.patch(
            "ht.nodes.styles.manager.StyleConstant", autospec=True
        )

        mock_rule1 = mocker.MagicMock(spec=dict)
        mock_rule2 = mocker.MagicMock(spec=dict)

        mock_color1 = mocker.MagicMock(spec=hou.Color)
        mock_color2 = mocker.MagicMock(spec=hou.Color)

        color_type1 = mocker.MagicMock(spec=str)
        color_type2 = mocker.MagicMock(spec=str)

        colors = {
            mock_rule1: (mock_color1, color_type1),
            mock_rule2: (mock_color2, color_type2),
        }

        mock_build_color.side_effect = lambda e: colors[e]

        shape1 = mocker.MagicMock(spec=str)
        shape2 = mocker.MagicMock(spec=str)

        shapes = {mock_rule1: shape1, mock_rule2: shape2}

        mock_build_shape.side_effect = lambda e: shapes[e]

        path = mocker.MagicMock(spec=str)
        name1 = mocker.MagicMock(spec=str)
        name2 = mocker.MagicMock(spec=str)

        all_data = [
            {
                consts.PATH_KEY: path,
                consts.CONSTANT_DEFINITION_KEY: {name1: mock_rule1, name2: mock_rule2},
            }
        ]

        constants = {}

        mocker.patch.object(
            manager.StyleManager,
            "constants",
            new_callable=mocker.PropertyMock(return_value=constants),
        )

        mgr = init_manager()

        mgr._build_constants_from_data(all_data)

        mock_build_color.assert_has_calls(
            [mocker.call(mock_rule1), mocker.call(mock_rule2)], any_order=True
        )
        mock_build_shape.assert_has_calls(
            [mocker.call(mock_rule1), mocker.call(mock_rule2)], any_order=True
        )

        calls = [
            mocker.call(name1, mock_color1, color_type1, shape1, path),
            mocker.call(name2, mock_color2, color_type2, shape2, path),
        ]

        mock_constant.assert_has_calls(calls, any_order=True)

        assert constants[name1] == mock_constant.return_value
        assert constants[name2] == mock_constant.return_value

    def test__build_constants_from_data__no_constants(self, init_manager, mocker):
        """Test building StyleConstants from data when there are no constant definitions."""
        mock_build_color = mocker.patch("ht.nodes.styles.manager._build_color")
        mock_build_shape = mocker.patch("ht.nodes.styles.manager._build_shape")
        mock_constant = mocker.patch(
            "ht.nodes.styles.manager.StyleConstant", autospec=True
        )

        all_data = [{consts.PATH_KEY: mocker.MagicMock(spec=str)}]

        mgr = init_manager()

        mgr._build_constants_from_data(all_data)

        mock_build_color.assert_not_called()
        mock_build_shape.assert_not_called()
        mock_constant.assert_not_called()

    # _build_rules_from_data

    def test__build_rules_from_data__no_rules(self, init_manager, mocker):
        """Test building rules from data when the data contains no rules."""
        mock_build = mocker.patch("ht.nodes.styles.manager._build_category_rules")

        all_data = [{consts.PATH_KEY: mocker.MagicMock(spec=str)}]

        mgr = init_manager()
        mgr._build_rules_from_data(all_data)

        mock_build.assert_not_called()

    def test__build_rules_from_data__names(self, init_manager, mocker):
        """Test building rules from data when the data contains name rules."""
        mock_build = mocker.patch("ht.nodes.styles.manager._build_category_rules")
        mock_constants = mocker.patch.object(
            manager.StyleManager, "constants", new_callable=mocker.PropertyMock
        )

        mock_rule1 = mocker.MagicMock(spec=dict)
        mock_rule2 = mocker.MagicMock(spec=dict)

        path = mocker.MagicMock(spec=str)
        all_data = [
            {
                consts.PATH_KEY: path,
                consts.RULES_KEY: {"name_rules": {"Sop": [mock_rule1, mock_rule2]}},
            }
        ]

        mgr = init_manager()
        mgr._name_rules = {}

        mgr._build_rules_from_data(all_data)

        assert mgr.name_rules["Sop"] == {}

        mock_build.assert_called_with(
            [mock_rule1, mock_rule2], {}, path, mock_constants.return_value
        )

    def test__build_rules_from_data__nodes(self, init_manager, mocker):
        """Test building rules from data when the data contains node type rules."""
        mock_build = mocker.patch("ht.nodes.styles.manager._build_category_rules")
        mock_constants = mocker.patch.object(
            manager.StyleManager, "constants", new_callable=mocker.PropertyMock
        )

        mock_rule1 = mocker.MagicMock(spec=dict)
        mock_rule2 = mocker.MagicMock(spec=dict)

        path = mocker.MagicMock(spec=str)
        all_data = [
            {
                consts.PATH_KEY: path,
                consts.RULES_KEY: {
                    "node_type_rules": {"Sop": [mock_rule1, mock_rule2]}
                },
            }
        ]

        mgr = init_manager()
        mgr._node_type_rules = {}

        mgr._build_rules_from_data(all_data)

        assert mgr.node_type_rules["Sop"] == {}

        mock_build.assert_called_with(
            [mock_rule1, mock_rule2], {}, path, mock_constants.return_value
        )

    def test__build_rules_from_data__tools(self, init_manager, mocker):
        """Test building rules from data when the data contains tool rules."""
        mock_build = mocker.patch("ht.nodes.styles.manager._build_category_rules")
        mock_constants = mocker.patch.object(
            manager.StyleManager, "constants", new_callable=mocker.PropertyMock
        )

        mock_rule1 = mocker.MagicMock(spec=dict)
        mock_rule2 = mocker.MagicMock(spec=dict)

        path = mocker.MagicMock(spec=str)
        all_data = [
            {
                consts.PATH_KEY: path,
                consts.RULES_KEY: {"tool_rules": {"Sop": [mock_rule1, mock_rule2]}},
            }
        ]

        mgr = init_manager()
        mgr._tool_rules = {}

        mgr._build_rules_from_data(all_data)

        assert mgr.tool_rules["Sop"] == {}

        mock_build.assert_called_with(
            [mock_rule1, mock_rule2], {}, path, mock_constants.return_value
        )

    # _get_manager_generator_style

    def test__get_manager_generator_style_manager__none(self, init_manager, mocker):
        """Test getting a style for a manager when no style exists."""
        mock_rules = mocker.patch.object(
            manager.StyleManager, "node_type_rules", new_callable=mocker.PropertyMock
        )
        mock_resolve = mocker.patch.object(manager.StyleManager, "_resolve_rule")

        mock_rules.return_value = {"Sop": {}}

        mock_category = mocker.MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category
        mock_type.isManager.return_value = True

        mgr = init_manager()

        result = mgr._get_manager_generator_style(mock_type)

        assert result is None

        mock_resolve.assert_not_called()

    def test__get_manager_generator_style_manager__category(self, init_manager, mocker):
        """Test getting a style for a manager where a specific category style exists."""
        mock_rules = mocker.patch.object(
            manager.StyleManager, "node_type_rules", new_callable=mocker.PropertyMock
        )
        mock_resolve = mocker.patch.object(manager.StyleManager, "_resolve_rule")

        mock_rule = mocker.MagicMock()

        mock_rules.return_value = {"Sop": {consts.MANAGER_TYPE_KEY: mock_rule}}

        mock_category = mocker.MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category
        mock_type.isManager.return_value = True
        mock_type.isGenerator.return_value = False

        mgr = init_manager()

        result = mgr._get_manager_generator_style(mock_type)

        assert result == mock_resolve.return_value

        mock_resolve.assert_called_with(mock_rule)

    def test__get_manager_generator_style__manager_all(self, init_manager, mocker):
        """Test getting a style for a manager where a generic 'all' style exists."""
        mock_rules = mocker.patch.object(
            manager.StyleManager, "node_type_rules", new_callable=mocker.PropertyMock
        )
        mock_resolve = mocker.patch.object(manager.StyleManager, "_resolve_rule")

        mock_rule = mocker.MagicMock()

        mock_rules.return_value = {"all": {consts.MANAGER_TYPE_KEY: mock_rule}}

        mock_category = mocker.MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category
        mock_type.isManager.return_value = True
        mock_type.isGenerator.return_value = False

        mgr = init_manager()

        result = mgr._get_manager_generator_style(mock_type)

        assert result == mock_resolve.return_value

        mock_resolve.assert_called_with(mock_rule)

    def test__get_manager_generator_style__generator_none(self, init_manager, mocker):
        """Test getting a style for a generator when no style exists."""
        mock_rules = mocker.patch.object(
            manager.StyleManager, "node_type_rules", new_callable=mocker.PropertyMock
        )
        mock_resolve = mocker.patch.object(manager.StyleManager, "_resolve_rule")

        mock_rules.return_value = {"Sop": {}}

        mock_category = mocker.MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category
        mock_type.isGenerator.return_value = True
        mock_type.isManager.return_value = False

        mgr = init_manager()

        result = mgr._get_manager_generator_style(mock_type)

        assert result is None

        mock_resolve.assert_not_called()

    def test__get_manager_generator_style__generator_category(
        self, init_manager, mocker
    ):
        """Test getting a style for a generator where a specific category style exists."""
        mock_rules = mocker.patch.object(
            manager.StyleManager, "node_type_rules", new_callable=mocker.PropertyMock
        )
        mock_resolve = mocker.patch.object(manager.StyleManager, "_resolve_rule")

        mock_rule = mocker.MagicMock()

        mock_rules.return_value = {"Sop": {consts.GENERATOR_TYPE_KEY: mock_rule}}

        mock_category = mocker.MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category
        mock_type.isGenerator.return_value = True
        mock_type.isManager.return_value = False

        mgr = init_manager()

        result = mgr._get_manager_generator_style(mock_type)

        assert result == mock_resolve.return_value

        mock_resolve.assert_called_with(mock_rule)

    def test__get_manager_generator_style__generator_all(self, init_manager, mocker):
        """Test getting a style for a generator where a generic 'all' style exists."""
        mock_rules = mocker.patch.object(
            manager.StyleManager, "node_type_rules", new_callable=mocker.PropertyMock
        )
        mock_resolve = mocker.patch.object(manager.StyleManager, "_resolve_rule")

        mock_rule = mocker.MagicMock()

        mock_rules.return_value = {
            consts.ALL_CATEGORY_KEY: {consts.GENERATOR_TYPE_KEY: mock_rule}
        }

        mock_category = mocker.MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category
        mock_type.isGenerator.return_value = True
        mock_type.isManager.return_value = False

        mgr = init_manager()

        result = mgr._get_manager_generator_style(mock_type)

        assert result == mock_resolve.return_value

        mock_resolve.assert_called_with(mock_rule)

    def test__get_manager_generator_style__error(self, init_manager, mocker):
        """Test getting a style when the node type is neither a manager or generator."""
        mock_rules = mocker.patch.object(
            manager.StyleManager, "node_type_rules", new_callable=mocker.PropertyMock
        )

        mock_rule = mocker.MagicMock()

        mock_rules.return_value = {
            consts.ALL_CATEGORY_KEY: {consts.GENERATOR_TYPE_KEY: mock_rule}
        }

        mock_category = mocker.MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category
        mock_type.isGenerator.return_value = False
        mock_type.isManager.return_value = False

        mgr = init_manager()

        with pytest.raises(ValueError):
            mgr._get_manager_generator_style(mock_type)

    # _get_name_style

    def test__get_name_style__category(self, init_manager, mocker):
        """Test getting a node name style which matches a specific category."""
        mock_name_rules = mocker.patch.object(
            manager.StyleManager, "name_rules", new_callable=mocker.PropertyMock
        )
        mock_match = mocker.patch("hou.patternMatch", return_value=True)
        mock_resolve = mocker.patch.object(manager.StyleManager, "_resolve_rule")

        style_name = mocker.MagicMock(spec=str)

        node_name = mocker.MagicMock(spec=str)

        mock_rule = mocker.MagicMock(spec=manager.StyleRule)
        type(mock_rule).name = mocker.PropertyMock(return_value=style_name)

        mock_name_rules.return_value = {"Sop": {node_name: mock_rule}}

        mock_category = mocker.MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.name.return_value = node_name
        mock_node.type.return_value = mock_type

        mgr = init_manager()

        result = mgr._get_name_style(mock_node)

        assert result == mock_resolve.return_value
        mock_match.assert_called_with(style_name, node_name)

        mock_resolve.assert_called_with(mock_rule)

    def test__get_name_style__all(self, init_manager, mocker):
        """Test getting a node name style which matches the generic 'all' category."""
        mock_name_rules = mocker.patch.object(
            manager.StyleManager, "name_rules", new_callable=mocker.PropertyMock
        )
        mock_match = mocker.patch("hou.patternMatch", return_value=True)
        mock_resolve = mocker.patch.object(manager.StyleManager, "_resolve_rule")

        style_name = mocker.MagicMock(spec=str)

        node_name = mocker.MagicMock(spec=str)

        mock_rule = mocker.MagicMock(spec=manager.StyleRule)
        type(mock_rule).name = mocker.PropertyMock(return_value=style_name)

        mock_name_rules.return_value = {consts.ALL_CATEGORY_KEY: {node_name: mock_rule}}

        mock_category = mocker.MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.name.return_value = node_name
        mock_node.type.return_value = mock_type

        mgr = init_manager()

        result = mgr._get_name_style(mock_node)

        assert result == mock_resolve.return_value
        mock_match.assert_called_with(style_name, node_name)

        mock_resolve.assert_called_with(mock_rule)

    def test__get_name_style__no_match(self, init_manager, mocker):
        """Test getting a node name style that does not match any rules."""
        mock_name_rules = mocker.patch.object(
            manager.StyleManager, "name_rules", new_callable=mocker.PropertyMock
        )
        mock_match = mocker.patch("hou.patternMatch", return_value=False)
        mock_resolve = mocker.patch.object(manager.StyleManager, "_resolve_rule")

        style_name = mocker.MagicMock(spec=str)

        node_name = mocker.MagicMock(spec=str)

        mock_rule = mocker.MagicMock(spec=manager.StyleRule)
        type(mock_rule).name = mocker.PropertyMock(return_value=style_name)

        mock_name_rules.return_value = {consts.ALL_CATEGORY_KEY: {node_name: mock_rule}}

        mock_category = mocker.MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.name.return_value = node_name
        mock_node.type.return_value = mock_type

        mgr = init_manager()

        result = mgr._get_name_style(mock_node)

        assert result is None
        mock_match.assert_called_with(style_name, node_name)

        mock_resolve.assert_not_called()

    # _get_node_type_style

    def test__get_node_type_style__category(self, init_manager, mocker):
        """Test getting a node type style which matches a specific category."""
        mock_node_type_rules = mocker.patch.object(
            manager.StyleManager, "node_type_rules", new_callable=mocker.PropertyMock
        )
        mock_match = mocker.patch("hou.patternMatch", return_value=True)
        mock_resolve = mocker.patch.object(manager.StyleManager, "_resolve_rule")

        style_name = mocker.MagicMock(spec=str)

        node_type_name = mocker.MagicMock(spec=str)

        mock_rule = mocker.MagicMock(spec=manager.StyleRule)
        type(mock_rule).name = mocker.PropertyMock(return_value=style_name)

        mock_node_type_rules.return_value = {"Sop": {node_type_name: mock_rule}}

        mock_category = mocker.MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category
        mock_type.nameComponents.return_value = ("", "", node_type_name, "1")

        mgr = init_manager()

        result = mgr._get_node_type_style(mock_type)

        assert result == mock_resolve.return_value
        mock_match.assert_called_with(style_name, node_type_name)

        mock_resolve.assert_called_with(mock_rule)

    def test__get_node_type_style__all(self, init_manager, mocker):
        """Test getting a node type style which matches the generic 'all' category."""
        mock_node_type_rules = mocker.patch.object(
            manager.StyleManager, "node_type_rules", new_callable=mocker.PropertyMock
        )
        mock_match = mocker.patch("hou.patternMatch", return_value=True)
        mock_resolve = mocker.patch.object(manager.StyleManager, "_resolve_rule")

        style_name = mocker.MagicMock(spec=str)

        node_type_name = mocker.MagicMock(spec=str)

        mock_rule = mocker.MagicMock(spec=manager.StyleRule)
        type(mock_rule).name = mocker.PropertyMock(return_value=style_name)

        mock_node_type_rules.return_value = {
            consts.ALL_CATEGORY_KEY: {node_type_name: mock_rule}
        }

        mock_category = mocker.MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category
        mock_type.nameComponents.return_value = ("", "", node_type_name, "1")

        mgr = init_manager()

        result = mgr._get_node_type_style(mock_type)

        assert result == mock_resolve.return_value
        mock_match.assert_called_with(style_name, node_type_name)

        mock_resolve.assert_called_with(mock_rule)

    def test__get_node_type_style__no_match(self, init_manager, mocker):
        """Test getting a node type style that does not match any rules."""
        mock_node_type_rules = mocker.patch.object(
            manager.StyleManager, "node_type_rules", new_callable=mocker.PropertyMock
        )
        mock_match = mocker.patch("hou.patternMatch", return_value=False)
        mock_resolve = mocker.patch.object(manager.StyleManager, "_resolve_rule")

        style_name = mocker.MagicMock(spec=str)

        node_type_name = mocker.MagicMock(spec=str)

        mock_rule = mocker.MagicMock(spec=manager.StyleRule)
        type(mock_rule).name = mocker.PropertyMock(return_value=style_name)

        mock_node_type_rules.return_value = {
            consts.ALL_CATEGORY_KEY: {node_type_name: mock_rule}
        }

        mock_category = mocker.MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category
        mock_type.nameComponents.return_value = ("", "", node_type_name, "1")

        mgr = init_manager()

        result = mgr._get_node_type_style(mock_type)

        assert result is None

        mock_match.assert_called_with(style_name, node_type_name)

        mock_resolve.assert_not_called()

    # _get_tool_style

    def test__get_tool_style__category(self, init_manager, mocker):
        """Test getting a tool style which matches a specific category."""
        mock_get_locations = mocker.patch(
            "ht.nodes.styles.manager._get_tool_menu_locations"
        )
        mock_tool_rules = mocker.patch.object(
            manager.StyleManager, "tool_rules", new_callable=mocker.PropertyMock
        )
        mock_match = mocker.patch("hou.patternMatch", return_value=True)
        mock_resolve = mocker.patch.object(manager.StyleManager, "_resolve_rule")

        location = mocker.MagicMock(spec=str)

        locations = (location,)
        mock_get_locations.return_value = locations

        style_name = mocker.MagicMock(spec=str)

        mock_rule = mocker.MagicMock(spec=manager.StyleRule)
        type(mock_rule).name = mocker.PropertyMock(return_value=style_name)

        mock_tool_rules.return_value = {"Sop": {location: mock_rule}}

        mock_category = mocker.MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category

        mgr = init_manager()

        result = mgr._get_tool_style(mock_type)

        assert result == mock_resolve.return_value

        mock_get_locations.assert_called_with(mock_type)

        mock_match.assert_called_with(style_name, location)

        mock_resolve.assert_called_with(mock_rule)

    def test__get_tool_style__all(self, init_manager, mocker):
        """Test getting a tool style which matches the generic 'all' category."""
        mock_get_locations = mocker.patch(
            "ht.nodes.styles.manager._get_tool_menu_locations"
        )
        mock_tool_rules = mocker.patch.object(
            manager.StyleManager, "tool_rules", new_callable=mocker.PropertyMock
        )
        mock_match = mocker.patch("hou.patternMatch", return_value=True)
        mock_resolve = mocker.patch.object(manager.StyleManager, "_resolve_rule")

        location = mocker.MagicMock(spec=str)
        mock_get_locations.return_value = (location,)

        style_name = mocker.MagicMock(spec=str)

        mock_rule = mocker.MagicMock(spec=manager.StyleRule)
        type(mock_rule).name = mocker.PropertyMock(return_value=style_name)

        mock_tool_rules.return_value = {consts.ALL_CATEGORY_KEY: {location: mock_rule}}

        mock_category = mocker.MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category

        mgr = init_manager()

        mock_match.return_value = True

        result = mgr._get_tool_style(mock_type)

        assert result == mock_resolve.return_value

        mock_get_locations.assert_called_with(mock_type)

        mock_match.assert_called_with(style_name, location)

        mock_resolve.assert_called_with(mock_rule)

    def test__get_tool_style__no_match(self, init_manager, mocker):
        """Test getting a tool style that does not match any rules."""
        mock_get_locations = mocker.patch(
            "ht.nodes.styles.manager._get_tool_menu_locations"
        )
        mock_tool_rules = mocker.patch.object(
            manager.StyleManager, "tool_rules", new_callable=mocker.PropertyMock
        )
        mock_match = mocker.patch("hou.patternMatch", return_value=False)
        mock_resolve = mocker.patch.object(manager.StyleManager, "_resolve_rule")

        location = mocker.MagicMock(spec=str)
        mock_locations = (location,)
        mock_get_locations.return_value = mock_locations

        style_name = mocker.MagicMock(spec=str)

        mock_rule = mocker.MagicMock(spec=manager.StyleRule)
        type(mock_rule).name = mocker.PropertyMock(return_value=style_name)

        mock_tool_rules.return_value = {consts.ALL_CATEGORY_KEY: {location: mock_rule}}

        mock_category = mocker.MagicMock(spec=hou.NodeTypeCategory)
        mock_category.name.return_value = "Sop"

        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category

        mgr = init_manager()

        result = mgr._get_tool_style(mock_type)

        assert result is None

        mock_get_locations.assert_called_with(mock_type)

        mock_match.assert_called_with(style_name, location)

        mock_resolve.assert_not_called()

    # _resolve_rule

    def test__resolve_rule__style(self, init_manager, mocker):
        """Test resolving a rule which is a StyleRule."""
        mock_rule = mocker.MagicMock(spec=manager.StyleRule)

        mgr = init_manager()

        result = mgr._resolve_rule(mock_rule)

        assert result == mock_rule

    def test__resolve_rule__constant(self, init_manager, mocker):
        """Test resolving a rule which is a ConstantRule."""
        mock_constants = mocker.patch.object(
            manager.StyleManager, "constants", new_callable=mocker.PropertyMock
        )

        constant_name = mocker.MagicMock(spec=str)

        mock_constant = mocker.MagicMock(spec=manager.StyleConstant)
        mock_constants.return_value = {constant_name: mock_constant}

        mock_rule = mocker.MagicMock(spec=manager.ConstantRule)
        type(mock_rule).constant_name = mocker.PropertyMock(return_value=constant_name)

        mgr = init_manager()

        result = mgr._resolve_rule(mock_rule)

        assert result == mock_constant

    # style_node

    def test_style_node__by_type(self, init_manager, mocker):
        """Style a node by the node type."""
        mock_get_type = mocker.patch.object(
            manager.StyleManager, "_get_node_type_style"
        )
        mock_get_tool = mocker.patch.object(manager.StyleManager, "_get_tool_style")

        mock_style = mocker.MagicMock(spec=manager.StyleRule)
        mock_get_type.return_value = mock_style

        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.isGenerator.return_value = False
        mock_type.isManager.return_value = False

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.type.return_value = mock_type

        mgr = init_manager()

        mgr.style_node(mock_node)

        mock_style.apply_to_node.assert_called_with(mock_node)

        mock_get_type.assert_called_with(mock_type)

        mock_get_tool.assert_not_called()
        mock_type.isManager.assert_not_called()

    def test_style_node__by_tool(self, init_manager, mocker):
        """Style a node by the tool menu location."""
        mock_get_type = mocker.patch.object(
            manager.StyleManager, "_get_node_type_style", return_value=None
        )
        mock_get_tool = mocker.patch.object(manager.StyleManager, "_get_tool_style")

        mock_style = mocker.MagicMock(spec=manager.StyleRule)
        mock_get_tool.return_value = mock_style

        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.isGenerator.return_value = False
        mock_type.isManager.return_value = False

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.type.return_value = mock_type

        mgr = init_manager()

        mgr.style_node(mock_node)

        mock_style.apply_to_node.assert_called_with(mock_node)

        mock_get_type.assert_called_with(mock_type)
        mock_get_tool.assert_called_with(mock_type)

        mock_type.isManager.assert_not_called()

    def test_style_node__by_manager(self, init_manager, mocker):
        """Style a node because it is a manager."""
        mock_get_type = mocker.patch.object(
            manager.StyleManager, "_get_node_type_style", return_value=None
        )
        mock_get_tool = mocker.patch.object(
            manager.StyleManager, "_get_tool_style", return_value=None
        )
        mock_get_manager = mocker.patch.object(
            manager.StyleManager, "_get_manager_generator_style"
        )

        mock_style = mocker.MagicMock(spec=manager.StyleRule)
        mock_get_manager.return_value = mock_style

        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.isGenerator.return_value = False
        mock_type.isManager.return_value = True

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.type.return_value = mock_type

        mgr = init_manager()

        mgr.style_node(mock_node)

        mock_style.apply_to_node.assert_called_with(mock_node)

        mock_get_type.assert_called_with(mock_type)
        mock_get_tool.assert_called_with(mock_type)

        mock_type.isGenerator.assert_not_called()

        mock_get_manager.assert_called_with(mock_type)

    def test_style_node__by_generator(self, init_manager, mocker):
        """Style a node because it is a generator."""
        mock_get_type = mocker.patch.object(
            manager.StyleManager, "_get_node_type_style", return_value=None
        )
        mock_get_tool = mocker.patch.object(
            manager.StyleManager, "_get_tool_style", return_value=None
        )
        mock_get_manager = mocker.patch.object(
            manager.StyleManager, "_get_manager_generator_style"
        )

        mock_style = mocker.MagicMock(spec=manager.StyleRule)
        mock_get_manager.return_value = mock_style

        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.isGenerator.return_value = True
        mock_type.isManager.return_value = False

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.type.return_value = mock_type

        mgr = init_manager()

        mgr.style_node(mock_node)

        mock_style.apply_to_node.assert_called_with(mock_node)

        mock_get_type.assert_called_with(mock_type)
        mock_get_tool.assert_called_with(mock_type)
        mock_get_manager.assert_called_with(mock_type)

    def test_style_node__no_match(self, init_manager, mocker):
        """Try to style a node but do not match any rule types."""
        mock_get_type = mocker.patch.object(
            manager.StyleManager, "_get_node_type_style", return_value=None
        )
        mock_get_tool = mocker.patch.object(
            manager.StyleManager, "_get_tool_style", return_value=None
        )
        mock_get_manager = mocker.patch.object(
            manager.StyleManager, "_get_manager_generator_style"
        )

        mock_style = mocker.MagicMock(spec=manager.StyleRule)
        mock_get_manager.return_value = mock_style

        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.isGenerator.return_value = False
        mock_type.isManager.return_value = False

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.type.return_value = mock_type

        mgr = init_manager()

        mgr.style_node(mock_node)

        mock_get_type.assert_called_with(mock_type)
        mock_get_tool.assert_called_with(mock_type)
        mock_get_manager.assert_not_called()

    # style_node_by_name

    def test_style_node_by_name(self, init_manager, mocker):
        """Style a node by its name."""
        mock_get_name = mocker.patch.object(manager.StyleManager, "_get_name_style")

        mock_style = mocker.MagicMock(spec=manager.StyleRule)

        mock_get_name.return_value = mock_style

        mock_node = mocker.MagicMock(spec=hou.Node)

        mgr = init_manager()

        mgr.style_node_by_name(mock_node)

        mock_style.apply_to_node.assert_called_with(mock_node)

        mock_get_name.assert_called_with(mock_node)

    def test_style_node_by_name__no_match(self, init_manager, mocker):
        """Try to style a node by its name but do not match any rules."""
        mock_get_name = mocker.patch.object(
            manager.StyleManager, "_get_name_style", return_value=None
        )

        mock_node = mocker.MagicMock(spec=hou.Node)

        mgr = init_manager()

        mgr.style_node_by_name(mock_node)

        mock_get_name.assert_called_with(mock_node)

    # reload

    def test_reload(self, init_manager, mocker):
        """Test reloading all the data."""
        mock_constants = mocker.patch.object(
            manager.StyleManager, "constants", new_callable=mocker.PropertyMock
        )
        mock_name_rules = mocker.patch.object(
            manager.StyleManager, "name_rules", new_callable=mocker.PropertyMock
        )
        mock_node_type_rules = mocker.patch.object(
            manager.StyleManager, "node_type_rules", new_callable=mocker.PropertyMock
        )
        mock_tool_rules = mocker.patch.object(
            manager.StyleManager, "tool_rules", new_callable=mocker.PropertyMock
        )
        mock_build = mocker.patch.object(manager.StyleManager, "_build")

        mgr = init_manager()

        mock_constants.return_value = mocker.MagicMock(spec=dict)
        mock_name_rules.return_value = mocker.MagicMock(spec=dict)
        mock_node_type_rules.return_value = mocker.MagicMock(spec=dict)
        mock_tool_rules.return_value = mocker.MagicMock(spec=dict)

        mgr.reload()

        mgr.constants.clear.assert_called_once()
        mgr.name_rules.clear.assert_called_once()
        mgr.node_type_rules.clear.assert_called_once()
        mgr.tool_rules.clear.assert_called_once()

        mock_build.assert_called()


class Test__build_category_rules:
    """Test ht.nodes.styles.manager._build_category_rules."""

    def test_invalid_constant(self, mocker):
        """Test building with an invalid constant."""
        path = mocker.MagicMock(spec=str)
        constants = {}

        rules = [
            {
                consts.RULE_NAME_KEY: mocker.MagicMock(spec=str),
                consts.RULE_CONSTANT_KEY: mocker.MagicMock(spec=str),
            }
        ]

        with pytest.raises(manager.ConstantDoesNotExistError):
            manager._build_category_rules(rules, {}, path, constants)

    def test_constant(self, mocker):
        """Test building a ConstantRule."""
        mock_build_color = mocker.patch("ht.nodes.styles.manager._build_color")
        mock_const_rule = mocker.patch(
            "ht.nodes.styles.manager.ConstantRule", autospec=True
        )

        constant_name = mocker.MagicMock(spec=str)

        category_map = {}

        path = mocker.MagicMock(spec=str)
        constants = {constant_name: mocker.MagicMock(spec=manager.StyleConstant)}

        rule_name = mocker.MagicMock(spec=str)

        rules = [
            {consts.RULE_NAME_KEY: rule_name, consts.RULE_CONSTANT_KEY: constant_name}
        ]

        manager._build_category_rules(rules, category_map, path, constants)

        assert category_map == {rule_name: mock_const_rule.return_value}

        mock_const_rule.assert_called_with(rule_name, constant_name, path)

        mock_build_color.assert_not_called()

    def test_style(self, mocker):
        """Test building a StyleRule."""
        mock_build_color = mocker.patch("ht.nodes.styles.manager._build_color")
        mock_build_shape = mocker.patch("ht.nodes.styles.manager._build_shape")
        mock_const_rule = mocker.patch(
            "ht.nodes.styles.manager.ConstantRule", autospec=True
        )
        mock_style_rule = mocker.patch(
            "ht.nodes.styles.manager.StyleRule", autospec=True
        )

        mock_color = mocker.MagicMock(spec=hou.Color)
        color_type = mocker.MagicMock(spec=str)
        mock_build_color.return_value = (mock_color, color_type)

        shape = mocker.MagicMock(spec=str)
        mock_build_shape.return_value = shape

        category_map = {}
        path = mocker.MagicMock(spec=str)

        rule_name = mocker.MagicMock(spec=str)

        data = {consts.RULE_NAME_KEY: rule_name}

        rules = [data]

        manager._build_category_rules(rules, category_map, path, {})

        assert category_map == {rule_name: mock_style_rule.return_value}

        mock_style_rule.assert_called_with(
            rule_name, mock_color, color_type, shape, path
        )

        mock_const_rule.assert_not_called()


class Test__build_color:
    """Test ht.nodes.styles.manager._build_color."""

    def test_no_data(self):
        """Test building a color when there is no data."""
        result = manager._build_color({})

        assert result == (None, None)

    def test_invalid_color_type(self, mocker):
        """Test building a color when the type is invalid."""
        mock_type = mocker.patch("hou.colorType")

        del mock_type.foo

        data = {consts.RULE_COLOR_KEY: {consts.RULE_COLOR_TYPE_KEY: "foo"}}

        with pytest.raises(manager.InvalidColorTypeError):
            manager._build_color(data)

    def test_rgb_single(self, mocker):
        """Test building an RGB color with a single float value."""
        mock_color = mocker.patch("hou.Color", autospec=True)

        color_type = "RGB"
        mock_value = mocker.MagicMock(spec=float)
        data = {
            consts.RULE_COLOR_KEY: {
                consts.RULE_COLOR_TYPE_KEY: color_type,
                consts.RULE_COLOR_VALUE_KEY: mock_value,
            }
        }

        result = manager._build_color(data)

        assert result == (mock_color(), color_type)

        mock_color().setRGB.assert_called_with([mock_value] * 3)

    def test_rgb(self, mocker):
        """Test building an RGB color with 3 float values."""
        mock_color = mocker.patch("hou.Color", autospec=True)

        color_type = "RGB"
        mock_value = mocker.MagicMock(spec=list)
        data = {
            consts.RULE_COLOR_KEY: {
                consts.RULE_COLOR_TYPE_KEY: color_type,
                consts.RULE_COLOR_VALUE_KEY: mock_value,
            }
        }

        result = manager._build_color(data)

        assert result == (mock_color(), color_type)

        mock_color().setRGB.assert_called_with(mock_value)

    def test_hsl(self, mocker):
        """Test building an HSL color."""
        mock_color = mocker.patch("hou.Color", autospec=True)

        color_type = "HSL"
        mock_value = mocker.MagicMock(spec=list)
        data = {
            consts.RULE_COLOR_KEY: {
                consts.RULE_COLOR_TYPE_KEY: color_type,
                consts.RULE_COLOR_VALUE_KEY: mock_value,
            }
        }

        result = manager._build_color(data)

        assert result == (mock_color(), color_type)

        mock_color().setHSL.assert_called_with(mock_value)

    def test_hsv(self, mocker):
        """Test building an HSV color."""
        mock_color = mocker.patch("hou.Color", autospec=True)

        color_type = "HSV"
        mock_value = mocker.MagicMock(spec=list)
        data = {
            consts.RULE_COLOR_KEY: {
                consts.RULE_COLOR_TYPE_KEY: color_type,
                consts.RULE_COLOR_VALUE_KEY: mock_value,
            }
        }

        result = manager._build_color(data)

        assert result == (mock_color(), color_type)

        mock_color().setHSV.assert_called_with(mock_value)

    def test_lab(self, mocker):
        """Test building a LAB color."""
        mock_color = mocker.patch("hou.Color", autospec=True)

        color_type = "LAB"
        mock_value = mocker.MagicMock(spec=list)
        data = {
            consts.RULE_COLOR_KEY: {
                consts.RULE_COLOR_TYPE_KEY: color_type,
                consts.RULE_COLOR_VALUE_KEY: mock_value,
            }
        }

        result = manager._build_color(data)

        assert result == (mock_color(), color_type)

        mock_color().setLAB.assert_called_with(mock_value)

    def test_xyz(self, mocker):
        """Test building an XYZ color."""
        mock_color = mocker.patch("hou.Color", autospec=True)

        color_type = "XYZ"
        mock_value = mocker.MagicMock(spec=list)
        data = {
            consts.RULE_COLOR_KEY: {
                consts.RULE_COLOR_TYPE_KEY: color_type,
                consts.RULE_COLOR_VALUE_KEY: mock_value,
            }
        }

        result = manager._build_color(data)

        assert result == (mock_color(), color_type)

        mock_color().setXYZ.assert_called_with(mock_value)


class Test__build_shape:
    """Test ht.nodes.styles.manager._build_shape."""

    def test(self):
        """Test building a shape where there is a shape key."""
        shape = "shape"
        mock_rule = {consts.RULE_SHAPE_KEY: shape}

        result = manager._build_shape(mock_rule)

        assert result == shape

    def test_no_rule(self):
        """Test building a shape where there is not a shape key."""
        result = manager._build_shape({})

        assert result is None


class Test__find_files:
    """Test ht.nodes.styles.manager._find_files."""

    def test_no_dirs(self, mocker, fix_hou_exceptions):
        """Test finding files where there are no config/styles folders in the HOUDINI_PATH."""
        mocker.patch("hou.findDirectories", side_effect=hou.OperationFailed)
        mock_glob = mocker.patch("glob.glob")

        result = manager._find_files()

        assert result == ()

        mock_glob.assert_not_called()

    def test(self, mocker):
        """Test finding files where there are valid config/styles folders in the HOUDINI_PATH."""
        mock_find = mocker.patch("hou.findDirectories")
        mock_glob = mocker.patch("glob.glob")

        dir1 = "/dir1"
        dir2 = "/dir2"

        mock_file1 = mocker.MagicMock(spec=str)
        mock_file2 = mocker.MagicMock(spec=str)
        mock_file3 = mocker.MagicMock(spec=str)

        mock_find.return_value = (dir1, dir2)

        mock_glob.side_effect = ((mock_file1, mock_file2), (mock_file3,))

        expected = (mock_file1, mock_file2, mock_file3)
        result = manager._find_files()

        assert result == expected

        calls = [
            mocker.call(os.path.join(dir1, "*.json")),
            mocker.call(os.path.join(dir2, "*.json")),
        ]

        mock_glob.assert_has_calls(calls)


class Test__get_tool_menu_locations:
    """Test ht.nodes.styles.manager._get_tool_menu_locations."""

    def test_no_match(self, mocker):
        """Test getting tab menu locations when no default tool exists."""
        mocker.patch("hou.shelves.tools", return_value={})
        mock_default_name = mocker.patch("hou.shelves.defaultToolName")

        mock_category = mocker.MagicMock(hou.NodeTypeCategory)

        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category

        result = manager._get_tool_menu_locations(mock_type)

        assert result == ()

        mock_default_name.assert_called_with(
            mock_category.name.return_value, mock_type.name.return_value
        )

    def test(self, mocker):
        """Test getting tab menu locations when the default tool exists."""
        mock_get_tools = mocker.patch("hou.shelves.tools")
        mock_default_name = mocker.patch("hou.shelves.defaultToolName")

        mock_tool = mocker.MagicMock(spec=hou.Tool)

        mock_get_tools.return_value = {mock_default_name.return_value: mock_tool}

        mock_category = mocker.MagicMock(hou.NodeTypeCategory)

        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.category.return_value = mock_category

        result = manager._get_tool_menu_locations(mock_type)

        assert result == mock_tool.toolMenuLocations.return_value

        mock_default_name.assert_called_with(
            mock_category.name.return_value, mock_type.name.return_value
        )
