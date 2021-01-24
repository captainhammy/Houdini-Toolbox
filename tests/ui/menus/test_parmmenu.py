"""Tests for ht.ui.menus.parmmenu module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Third Party Imports
import pytest

# Houdini Toolbox Imports
import ht.ui.menus.parmmenu

# Houdini Imports
import hou


# =============================================================================
# TESTS
# =============================================================================


class Test__valid_to_convert_to_absolute_reference:
    """Test ht.ui.menus.parmmenu._valid_to_convert_to_absolute_reference."""

    def test_empty_string(self, mocker):
        """Test when the path is an empty string."""
        mock_template = mocker.MagicMock(spec=hou.StringParmTemplate)
        mock_template.stringType.return_value = hou.stringParmType.NodeReference

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = mocker.MagicMock(spec=str)
        mock_parm.parmTemplate.return_value = mock_template

        result = ht.ui.menus.parmmenu._valid_to_convert_to_absolute_reference(mock_parm)

        assert not result

        mock_parm.keyframes.assert_not_called()

    def test_not_relative(self, mocker):
        """Test when the path does not seem to be relative."""
        mock_template = mocker.MagicMock(spec=hou.StringParmTemplate)
        mock_template.stringType.return_value = hou.stringParmType.NodeReference

        mock_path = mocker.MagicMock(spec=str)
        mock_path.__len__.return_value = 1
        mock_path.startswith.return_value = False

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = mock_path
        mock_parm.parmTemplate.return_value = mock_template

        result = ht.ui.menus.parmmenu._valid_to_convert_to_absolute_reference(mock_parm)

        assert not result

        mock_path.startswith.assert_called_with("..")
        mock_parm.keyframes.assert_not_called()

    def test_keyframes(self, mocker):
        """Test when the parameter has keyframes."""
        mock_template = mocker.MagicMock(spec=hou.StringParmTemplate)
        mock_template.stringType.return_value = hou.stringParmType.NodeReference

        mock_path = mocker.MagicMock(spec=str)
        mock_path.__len__.return_value = 1
        mock_path.startswith.return_value = True

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = mock_path
        mock_parm.parmTemplate.return_value = mock_template

        result = ht.ui.menus.parmmenu._valid_to_convert_to_absolute_reference(mock_parm)

        assert not result

        mock_path.startswith.assert_called_with("..")
        mock_parm.keyframes.assert_called()
        mock_parm.unexpandedString.assert_not_called()

    def test(self, mocker):
        """Test when the path can be converted to an absolute path."""
        mock_template = mocker.MagicMock(spec=hou.StringParmTemplate)
        mock_template.stringType.return_value = hou.stringParmType.NodeReference

        mock_path = mocker.MagicMock(spec=str)
        mock_path.__len__.return_value = 1
        mock_path.startswith.return_value = True

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = mock_path
        mock_parm.keyframes.return_value = ()
        mock_parm.unexpandedString.return_value = mock_path
        mock_parm.parmTemplate.return_value = mock_template
        mock_parm.evalAsNode.return_value = mocker.MagicMock(spec=hou.Node)

        result = ht.ui.menus.parmmenu._valid_to_convert_to_absolute_reference(mock_parm)

        assert result

        mock_path.startswith.assert_called_with("..")
        mock_parm.keyframes.assert_called()
        mock_parm.evalAsNode.assert_called()

    def test_invalid_path(self, mocker):
        """Test when the path does not point to a valid node."""
        mock_template = mocker.MagicMock(spec=hou.StringParmTemplate)
        mock_template.stringType.return_value = hou.stringParmType.NodeReference

        mock_path = mocker.MagicMock(spec=str)
        mock_path.__len__.return_value = 1
        mock_path.startswith.return_value = True

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = mock_path
        mock_parm.keyframes.return_value = ()
        mock_parm.unexpandedString.return_value = mock_path
        mock_parm.parmTemplate.return_value = mock_template
        mock_parm.evalAsNode.return_value = None

        result = ht.ui.menus.parmmenu._valid_to_convert_to_absolute_reference(mock_parm)

        assert not result

        mock_path.startswith.assert_called_with("..")
        mock_parm.keyframes.assert_called()
        mock_parm.evalAsNode.assert_called()

    def test_expression(self, mocker):
        """Test when the path does not match the unexpanded string (is an expression)."""
        mock_template = mocker.MagicMock(spec=hou.StringParmTemplate)
        mock_template.stringType.return_value = hou.stringParmType.NodeReference

        mock_path = mocker.MagicMock(spec=str)
        mock_path.__len__.return_value = 1
        mock_path.startswith.return_value = True

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = mock_path
        mock_parm.keyframes.return_value = ()
        mock_parm.unexpandedString.return_value = mocker.MagicMock(spec=str)
        mock_parm.parmTemplate.return_value = mock_template

        result = ht.ui.menus.parmmenu._valid_to_convert_to_absolute_reference(mock_parm)

        assert not result

        mock_path.startswith.assert_called_with("..")
        mock_parm.keyframes.assert_called()
        mock_parm.evalAsNode.assert_not_called()

    def test_not_node_reference(self, mocker):
        """Test when the string parameter is not a node reference."""
        mock_template = mocker.MagicMock(spec=hou.StringParmTemplate)
        mock_template.stringType.return_value = mocker.MagicMock(
            spec=hou.stringParmType
        )

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.parmTemplate.return_value = mock_template

        result = ht.ui.menus.parmmenu._valid_to_convert_to_absolute_reference(mock_parm)

        assert not result

        mock_parm.eval.assert_not_called()

    def test_not_string_parm(self, mocker):
        """Test when the string parameter is not a node reference."""
        mock_template = mocker.MagicMock(spec=hou.ParmTemplate)

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.parmTemplate.return_value = mock_template

        result = ht.ui.menus.parmmenu._valid_to_convert_to_absolute_reference(mock_parm)

        assert not result


class Test__valid_to_convert_to_relative_reference:
    """Test ht.ui.menus.parmmenu._valid_to_convert_to_relative_reference."""

    def test_empty_string(self, mocker):
        """Test when the path is an empty string."""
        mock_template = mocker.MagicMock(spec=hou.StringParmTemplate)
        mock_template.stringType.return_value = hou.stringParmType.NodeReference

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = mocker.MagicMock(spec=str)
        mock_parm.parmTemplate.return_value = mock_template

        result = ht.ui.menus.parmmenu._valid_to_convert_to_relative_reference(mock_parm)

        assert not result

        mock_parm.keyframes.assert_not_called()

    def test_not_absolute(self, mocker):
        """Test when the path does not seem to be absolute."""
        mock_template = mocker.MagicMock(spec=hou.StringParmTemplate)
        mock_template.stringType.return_value = hou.stringParmType.NodeReference

        mock_path = mocker.MagicMock(spec=str)
        mock_path.__len__.return_value = 1
        mock_path.startswith.return_value = False

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = mock_path
        mock_parm.parmTemplate.return_value = mock_template

        result = ht.ui.menus.parmmenu._valid_to_convert_to_relative_reference(mock_parm)

        assert not result

        mock_path.startswith.assert_called_with("/")
        mock_parm.keyframes.assert_not_called()

    def test_keyframes(self, mocker):
        """Test when the parameter has keyframes."""
        mock_template = mocker.MagicMock(spec=hou.StringParmTemplate)
        mock_template.stringType.return_value = hou.stringParmType.NodeReference

        mock_path = mocker.MagicMock(spec=str)
        mock_path.__len__.return_value = 1
        mock_path.startswith.return_value = True

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = mock_path
        mock_parm.parmTemplate.return_value = mock_template

        result = ht.ui.menus.parmmenu._valid_to_convert_to_relative_reference(mock_parm)

        assert not result

        mock_path.startswith.assert_called_with("/")
        mock_parm.keyframes.assert_called()
        mock_parm.unexpandedString.assert_not_called()

    def test(self, mocker):
        """Test when the path can be converted to a relative path."""
        mock_template = mocker.MagicMock(spec=hou.StringParmTemplate)
        mock_template.stringType.return_value = hou.stringParmType.NodeReference

        mock_path = mocker.MagicMock(spec=str)
        mock_path.__len__.return_value = 1
        mock_path.startswith.return_value = True

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = mock_path
        mock_parm.keyframes.return_value = ()
        mock_parm.unexpandedString.return_value = mock_path
        mock_parm.parmTemplate.return_value = mock_template
        mock_parm.evalAsNode.return_value = mocker.MagicMock(spec=hou.Node)

        result = ht.ui.menus.parmmenu._valid_to_convert_to_relative_reference(mock_parm)

        assert result

        mock_path.startswith.assert_called_with("/")
        mock_parm.keyframes.assert_called()
        mock_parm.evalAsNode.assert_called()

    def test_invalid_path(self, mocker):
        """Test when the path does not point to a valid node."""
        mock_template = mocker.MagicMock(spec=hou.StringParmTemplate)
        mock_template.stringType.return_value = hou.stringParmType.NodeReference

        mock_path = mocker.MagicMock(spec=str)
        mock_path.__len__.return_value = 1
        mock_path.startswith.return_value = True

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = mock_path
        mock_parm.keyframes.return_value = ()
        mock_parm.unexpandedString.return_value = mock_path
        mock_parm.parmTemplate.return_value = mock_template
        mock_parm.evalAsNode.return_value = None

        result = ht.ui.menus.parmmenu._valid_to_convert_to_relative_reference(mock_parm)

        assert not result

        mock_path.startswith.assert_called_with("/")
        mock_parm.keyframes.assert_called()
        mock_parm.evalAsNode.assert_called()

    def test_expression(self, mocker):
        """Test when the path does not match the unexpanded string (is an expression)."""
        mock_template = mocker.MagicMock(spec=hou.StringParmTemplate)
        mock_template.stringType.return_value = hou.stringParmType.NodeReference

        mock_path = mocker.MagicMock(spec=str)
        mock_path.__len__.return_value = 1
        mock_path.startswith.return_value = True

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = mock_path
        mock_parm.keyframes.return_value = ()
        mock_parm.unexpandedString.return_value = mocker.MagicMock(spec=str)
        mock_parm.parmTemplate.return_value = mock_template

        result = ht.ui.menus.parmmenu._valid_to_convert_to_relative_reference(mock_parm)

        assert not result

        mock_path.startswith.assert_called_with("/")
        mock_parm.keyframes.assert_called()
        mock_parm.evalAsNode.assert_not_called()

    def test_not_node_reference(self, mocker):
        """Test when the string parameter is not a node reference."""
        mock_template = mocker.MagicMock(spec=hou.StringParmTemplate)
        mock_template.stringType.return_value = mocker.MagicMock(
            spec=hou.stringParmType
        )

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.parmTemplate.return_value = mock_template

        result = ht.ui.menus.parmmenu._valid_to_convert_to_relative_reference(mock_parm)

        assert not result

        mock_parm.eval.assert_not_called()

    def test_not_string_parm(self, mocker):
        """Test when the string parameter is not a node reference."""
        mock_template = mocker.MagicMock(spec=hou.ParmTemplate)

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.parmTemplate.return_value = mock_template

        result = ht.ui.menus.parmmenu._valid_to_convert_to_relative_reference(mock_parm)

        assert not result


class Test_convert_absolute_to_relative_path_context:
    """Test ht.ui.menus.parmmenu.convert_absolute_to_relative_path_context."""

    def test_none(self, mocker):
        """Test converting when no parms are suitable to convert."""
        mock_valid = mocker.patch(
            "ht.ui.menus.parmmenu._valid_to_convert_to_relative_reference",
            return_value=False,
        )

        mock_parm1 = mocker.MagicMock(spec=hou.Parm)
        mock_parm2 = mocker.MagicMock(spec=hou.Parm)

        scriptargs = {"parms": (mock_parm1, mock_parm2)}

        result = ht.ui.menus.parmmenu.convert_absolute_to_relative_path_context(
            scriptargs
        )

        assert not result

        mock_valid.assert_has_calls([mocker.call(mock_parm1), mocker.call(mock_parm2)])

    def test_some(self, mocker):
        """Test converting when at least one parm is suitable to convert."""
        mock_valid = mocker.patch(
            "ht.ui.menus.parmmenu._valid_to_convert_to_relative_reference",
            side_effect=(False, True),
        )

        mock_parm1 = mocker.MagicMock(spec=hou.Parm)
        mock_parm2 = mocker.MagicMock(spec=hou.Parm)

        scriptargs = {"parms": (mock_parm1, mock_parm2)}

        result = ht.ui.menus.parmmenu.convert_absolute_to_relative_path_context(
            scriptargs
        )

        assert result

        mock_valid.assert_has_calls([mocker.call(mock_parm1), mocker.call(mock_parm2)])


def test_convert_absolute_to_relative_path(mocker):
    """Test converting an absolute to relative path."""
    mock_valid = mocker.patch(
        "ht.ui.menus.parmmenu._valid_to_convert_to_relative_reference",
        side_effect=(False, True),
    )

    mock_parm1 = mocker.MagicMock(spec=hou.Parm)
    mock_parm2 = mocker.MagicMock(spec=hou.Parm)

    scriptargs = {"parms": (mock_parm1, mock_parm2)}

    ht.ui.menus.parmmenu.convert_absolute_to_relative_path(scriptargs)

    mock_valid.assert_has_calls([mocker.call(mock_parm1), mocker.call(mock_parm2)])

    mock_parm1.evalAsNode.assert_not_called()

    mock_parm2.evalAsNode.assert_called()
    mock_parm2.set.assert_called_with(
        mock_parm2.node.return_value.relativePathTo.return_value
    )
    mock_parm2.node.return_value.relativePathTo.assert_called_with(
        mock_parm2.evalAsNode.return_value
    )


class Test_convert_relative_to_absolute_path_context:
    """Test ht.ui.menus.parmmenu.convert_relative_to_absolute_path_context."""

    def test_none(self, mocker):
        """Test converting when no parms are suitable to convert."""
        mock_valid = mocker.patch(
            "ht.ui.menus.parmmenu._valid_to_convert_to_absolute_reference",
            return_value=False,
        )

        mock_parm1 = mocker.MagicMock(spec=hou.Parm)
        mock_parm2 = mocker.MagicMock(spec=hou.Parm)

        scriptargs = {"parms": (mock_parm1, mock_parm2)}

        result = ht.ui.menus.parmmenu.convert_relative_to_absolute_path_context(
            scriptargs
        )

        assert not result

        mock_valid.assert_has_calls([mocker.call(mock_parm1), mocker.call(mock_parm2)])

    def test_some(self, mocker):
        """Test converting when at least one parm is suitable to convert."""
        mock_valid = mocker.patch(
            "ht.ui.menus.parmmenu._valid_to_convert_to_absolute_reference",
            side_effect=(False, True),
        )

        mock_parm1 = mocker.MagicMock(spec=hou.Parm)
        mock_parm2 = mocker.MagicMock(spec=hou.Parm)

        scriptargs = {"parms": (mock_parm1, mock_parm2)}

        result = ht.ui.menus.parmmenu.convert_relative_to_absolute_path_context(
            scriptargs
        )

        assert result

        mock_valid.assert_has_calls([mocker.call(mock_parm1), mocker.call(mock_parm2)])


def test_convert_relative_to_absolute_path(mocker):
    """Test ht.ui.menus.parmmenu.convert_relative_to_absolute_path."""
    mock_valid = mocker.patch(
        "ht.ui.menus.parmmenu._valid_to_convert_to_absolute_reference",
        side_effect=(False, True),
    )

    mock_parm1 = mocker.MagicMock(spec=hou.Parm)
    mock_parm2 = mocker.MagicMock(spec=hou.Parm)

    scriptargs = {"parms": (mock_parm1, mock_parm2)}

    ht.ui.menus.parmmenu.convert_relative_to_absolute_path(scriptargs)

    mock_valid.assert_has_calls([mocker.call(mock_parm1), mocker.call(mock_parm2)])

    mock_parm1.evalAsNode.assert_not_called()

    mock_parm2.evalAsNode.assert_called()
    mock_parm2.set.assert_called_with(
        mock_parm2.evalAsNode.return_value.path.return_value
    )


class Test_promote_parameter_to_node:
    """Test ht.ui.menus.parmmenu.promote_parameter_to_node."""

    def test_target_is_source(self, mocker, mock_hou_ui):
        """Test when trying to promote to the node containing the parms to promote."""
        mock_hou_node = mocker.patch("ht.ui.menus.parmmenu.hou.node")

        mock_node1 = mocker.MagicMock(spec=hou.Node)

        mock_parm_tuple1 = mocker.MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple1.__len__.return_value = 1
        mock_parm_tuple1.node.return_value = mock_node1

        mock_parm1 = mocker.MagicMock(spec=hou.Parm)
        mock_parm1.tuple.return_value = mock_parm_tuple1

        mock_hou_node.return_value = mock_node1

        scriptargs = {"parms": (mock_parm1,)}

        with pytest.raises(hou.OperationFailed):
            ht.ui.menus.parmmenu.promote_parameter_to_node(scriptargs)

        mock_hou_ui.selectNode.assert_called_with(
            initial_node=mock_node1.parent.return_value
        )
        mock_hou_node.assert_called_with(mock_hou_ui.selectNode.return_value)

    def test_parm_exists_no_set(self, mocker, mock_hou_ui):
        """Test when the target exists and we don't want to set the target value to the
        current value before promoting.

        """
        mock_hou_node = mocker.patch("ht.ui.menus.parmmenu.hou.node")

        mock_node1 = mocker.MagicMock(spec=hou.Node)

        mock_parm_tuple1 = mocker.MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple1.__len__.return_value = 1
        mock_parm_tuple1.node.return_value = mock_node1

        mock_parm1 = mocker.MagicMock(spec=hou.Parm)
        mock_parm1.tuple.return_value = mock_parm_tuple1

        mock_target_parm1 = mocker.MagicMock(spec=hou.Parm)

        mock_target_node = mocker.MagicMock(spec=hou.Node)
        mock_target_node.parmTuple.return_value = mocker.MagicMock(spec=hou.ParmTuple)
        mock_target_node.parm.return_value = mock_target_parm1

        mock_hou_node.return_value = mock_target_node

        mock_hou_ui.displayMessage.return_value = 0

        scriptargs = {"parms": (mock_parm1,)}

        ht.ui.menus.parmmenu.promote_parameter_to_node(scriptargs)

        mock_hou_ui.selectNode.assert_called_with(
            initial_node=mock_node1.parent.return_value
        )
        mock_hou_node.assert_called_with(mock_hou_ui.selectNode.return_value)

        mock_target_node.parmTuple.assert_called_with(
            mock_parm_tuple1.name.return_value
        )

        mock_target_node.parm.assert_called_with(mock_parm1.name.return_value)
        mock_target_parm1.set.assert_not_called()

        mock_parm1.set.assert_called_with(mock_target_parm1)

    def test_parm_exists_set_value(self, mocker, mock_hou_ui):
        """Test when the target exists and we want to set the target value to the current
        value before promoting.

        """
        mock_hou_node = mocker.patch("ht.ui.menus.parmmenu.hou.node")

        mock_node1 = mocker.MagicMock(spec=hou.Node)

        mock_parm_tuple1 = mocker.MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple1.__len__.return_value = 1
        mock_parm_tuple1.node.return_value = mock_node1

        mock_parm1 = mocker.MagicMock(spec=hou.Parm)
        mock_parm1.tuple.return_value = mock_parm_tuple1

        mock_target_parm1 = mocker.MagicMock(spec=hou.Parm)

        mock_target_node = mocker.MagicMock(spec=hou.Node)
        mock_target_node.parmTuple.return_value = mocker.MagicMock(spec=hou.ParmTuple)
        mock_target_node.parm.return_value = mock_target_parm1

        mock_hou_node.return_value = mock_target_node

        mock_hou_ui.displayMessage.return_value = 1

        scriptargs = {"parms": (mock_parm1,)}

        ht.ui.menus.parmmenu.promote_parameter_to_node(scriptargs)

        mock_hou_ui.selectNode.assert_called_with(
            initial_node=mock_node1.parent.return_value
        )
        mock_hou_node.assert_called_with(mock_hou_ui.selectNode.return_value)

        mock_target_node.parmTuple.assert_called_with(
            mock_parm_tuple1.name.return_value
        )

        mock_target_node.parm.assert_called_with(mock_parm1.name.return_value)
        mock_target_parm1.set.assert_called_with(mock_parm1.eval.return_value)

        mock_parm1.set.assert_called_with(mock_target_parm1)

    def test_parm_exists_cancel(self, mocker, mock_hou_ui):
        """Test when the target exists and we want to cancel."""
        mock_hou_node = mocker.patch("ht.ui.menus.parmmenu.hou.node")

        mock_node1 = mocker.MagicMock(spec=hou.Node)

        mock_parm_tuple1 = mocker.MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple1.__len__.return_value = 1
        mock_parm_tuple1.node.return_value = mock_node1

        mock_parm1 = mocker.MagicMock(spec=hou.Parm)
        mock_parm1.tuple.return_value = mock_parm_tuple1

        mock_target_parm1 = mocker.MagicMock(spec=hou.Parm)

        mock_target_node = mocker.MagicMock(spec=hou.Node)
        mock_target_node.parmTuple.return_value = mocker.MagicMock(spec=hou.ParmTuple)
        mock_target_node.parm.return_value = mock_target_parm1

        mock_hou_node.return_value = mock_target_node

        mock_hou_ui.displayMessage.return_value = 2

        scriptargs = {"parms": (mock_parm1,)}

        ht.ui.menus.parmmenu.promote_parameter_to_node(scriptargs)

        mock_hou_ui.selectNode.assert_called_with(
            initial_node=mock_node1.parent.return_value
        )
        mock_hou_node.assert_called_with(mock_hou_ui.selectNode.return_value)

        mock_target_node.parmTuple.assert_called_with(
            mock_parm_tuple1.name.return_value
        )

        mock_target_node.parm.assert_not_called()

    def test_no_existing_single_component(
        self, mocker, mock_hou_ui
    ):
        """Test when there is no existing parm and we want to promote a single parm from the tuple."""
        mock_hou_node = mocker.patch("ht.ui.menus.parmmenu.hou.node")

        mock_node1 = mocker.MagicMock(spec=hou.Node)

        mock_parm_template1 = mocker.MagicMock(spec=hou.ParmTemplate)

        mock_parm_tuple1 = mocker.MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple1.parmTemplate.return_value = mock_parm_template1
        mock_parm_tuple1.__len__.return_value = 3
        mock_parm_tuple1.node.return_value = mock_node1

        mock_parm1 = mocker.MagicMock(spec=hou.Parm)
        mock_parm1.tuple.return_value = mock_parm_tuple1

        mock_target_parm1 = mocker.MagicMock(spec=hou.Parm)

        mock_ptg = mocker.MagicMock(spec=hou.ParmTemplateGroup)

        mock_target_node = mocker.MagicMock(spec=hou.Node)
        mock_target_node.parmTemplateGroup.return_value = mock_ptg
        mock_target_node.parmTuple.return_value = None
        mock_target_node.parm.return_value = mock_target_parm1

        mock_hou_node.return_value = mock_target_node

        scriptargs = {"parms": (mock_parm1,)}

        ht.ui.menus.parmmenu.promote_parameter_to_node(scriptargs)

        mock_hou_ui.selectNode.assert_called_with(
            initial_node=mock_node1.parent.return_value
        )
        mock_hou_node.assert_called_with(mock_hou_ui.selectNode.return_value)

        mock_target_node.parmTuple.assert_called_with(
            mock_parm_tuple1.name.return_value
        )

        mock_parm_template1.setNumComponents.assert_called_with(1)
        mock_parm_template1.setName.assert_called_with(mock_parm1.name.return_value)

        mock_ptg.addParmTemplate.assert_called_with(mock_parm_template1)
        mock_target_node.setParmTemplateGroup.assert_called_with(mock_ptg)

        mock_target_node.parm.assert_called_with(mock_parm1.name.return_value)
        mock_target_parm1.set.assert_called_with(mock_parm1.eval.return_value)

        mock_parm1.set.assert_called_with(mock_target_parm1)

    def test_no_existing_multiple_components(
        self, mocker, mock_hou_ui
    ):
        """Test when there is no existing parm and we want to promote a full tuple."""
        mock_hou_node = mocker.patch("ht.ui.menus.parmmenu.hou.node")

        mock_node1 = mocker.MagicMock(spec=hou.Node)

        mock_parm_template1 = mocker.MagicMock(spec=hou.ParmTemplate)

        mock_parm_tuple1 = mocker.MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple1.parmTemplate.return_value = mock_parm_template1
        mock_parm_tuple1.__len__.return_value = 3
        mock_parm_tuple1.node.return_value = mock_node1

        mock_parm1 = mocker.MagicMock(spec=hou.Parm)
        mock_parm1.tuple.return_value = mock_parm_tuple1

        mock_parm2 = mocker.MagicMock(spec=hou.Parm)
        mock_parm2.tuple.return_value = mock_parm_tuple1

        mock_parm3 = mocker.MagicMock(spec=hou.Parm)
        mock_parm3.tuple.return_value = mock_parm_tuple1

        mock_target_parm1 = mocker.MagicMock(spec=hou.Parm)
        mock_target_parm2 = mocker.MagicMock(spec=hou.Parm)
        mock_target_parm3 = mocker.MagicMock(spec=hou.Parm)

        mock_ptg = mocker.MagicMock(spec=hou.ParmTemplateGroup)

        mock_target_node = mocker.MagicMock(spec=hou.Node)
        mock_target_node.parmTemplateGroup.return_value = mock_ptg
        mock_target_node.parmTuple.return_value = None
        mock_target_node.parm.side_effect = (
            mock_target_parm1,
            mock_target_parm2,
            mock_target_parm3,
        )

        mock_hou_node.return_value = mock_target_node

        scriptargs = {"parms": (mock_parm1, mock_parm2, mock_parm3)}

        ht.ui.menus.parmmenu.promote_parameter_to_node(scriptargs)

        mock_hou_ui.selectNode.assert_called_with(
            initial_node=mock_node1.parent.return_value
        )
        mock_hou_node.assert_called_with(mock_hou_ui.selectNode.return_value)

        mock_target_node.parmTuple.assert_called_with(
            mock_parm_tuple1.name.return_value
        )

        mock_parm_template1.setNumComponents.assert_not_called()

        mock_ptg.addParmTemplate.assert_called_with(mock_parm_template1)
        mock_target_node.setParmTemplateGroup.assert_called_with(mock_ptg)

        mock_target_node.parm.assert_has_calls(
            [
                mocker.call(mock_parm1.name.return_value),
                mocker.call(mock_parm2.name.return_value),
                mocker.call(mock_parm3.name.return_value),
            ]
        )

        mock_target_parm1.set.assert_called_with(mock_parm1.eval.return_value)
        mock_target_parm2.set.assert_called_with(mock_parm2.eval.return_value)
        mock_target_parm3.set.assert_called_with(mock_parm3.eval.return_value)

        mock_parm1.set.assert_called_with(mock_target_parm1)

    def test_no_selection(self, mocker, mock_hou_ui):
        """Test when no target node is selected."""
        mock_hou_node = mocker.patch("ht.ui.menus.parmmenu.hou.node")

        mock_node1 = mocker.MagicMock(spec=hou.Node)

        mock_parm_template1 = mocker.MagicMock(spec=hou.ParmTemplate)

        mock_parm_tuple1 = mocker.MagicMock(spec=hou.ParmTuple)
        mock_parm_tuple1.parmTemplate.return_value = mock_parm_template1
        mock_parm_tuple1.__len__.return_value = 3
        mock_parm_tuple1.node.return_value = mock_node1

        mock_parm1 = mocker.MagicMock(spec=hou.Parm)
        mock_parm1.tuple.return_value = mock_parm_tuple1

        mock_target_parm1 = mocker.MagicMock(spec=hou.Parm)

        mock_ptg = mocker.MagicMock(spec=hou.ParmTemplateGroup)

        mock_target_node = mocker.MagicMock(spec=hou.Node)
        mock_target_node.parmTemplateGroup.return_value = mock_ptg
        mock_target_node.parmTuple.return_value = None
        mock_target_node.parm.return_value = mock_target_parm1

        mock_hou_node.return_value = None

        scriptargs = {"parms": (mock_parm1,)}

        ht.ui.menus.parmmenu.promote_parameter_to_node(scriptargs)

        mock_hou_ui.selectNode.assert_called_with(
            initial_node=mock_node1.parent.return_value
        )
        mock_hou_node.assert_called_with(mock_hou_ui.selectNode.return_value)
