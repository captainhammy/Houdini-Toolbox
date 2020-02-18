"""Tests for ht.logging.adapters module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
from __future__ import absolute_import
import logging

# Third Party Imports
import pytest

# Houdini Toolbox Imports
import ht.logging.adapters

# Houdini Imports
import hou


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def init_adapter(mocker):
    """Fixture to initialize an adapter."""
    mocker.patch.object(
        ht.logging.adapters.HoudiniLoggerAdapter, "__init__", lambda x, y: None
    )

    def _create():
        return ht.logging.adapters.HoudiniLoggerAdapter(None)

    return _create


# =============================================================================
# TESTS
# =============================================================================


class Test_HoudiniLoggerAdapter(object):
    """Test ht.logging.adapters.HoudiniLoggerAdapter."""

    def test___init__(self, mocker):
        """Test object initialization."""
        mock_super_init = mocker.patch.object(
            ht.logging.adapters.logging.LoggerAdapter, "__init__"
        )

        mock_base_logger = mocker.MagicMock(spec=logging.Logger)
        mock_dialog = mocker.MagicMock(spec=bool)
        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_status_bar = mocker.MagicMock(spec=bool)

        log = ht.logging.adapters.HoudiniLoggerAdapter(
            mock_base_logger, mock_dialog, mock_node, mock_status_bar
        )

        mock_super_init.assert_called_with(mock_base_logger, {})

        assert log._dialog == mock_dialog
        assert log._node == mock_node
        assert log._status_bar == mock_status_bar

    def test___new__(self, mocker):
        """Test object creation."""
        mock_super_new = mocker.patch.object(
            ht.logging.adapters.logging.LoggerAdapter, "__new__"
        )
        mock_callable = mocker.patch(
            "ht.logging.adapters.callable", side_effect=(True, False)
        )
        mock_wrap = mocker.patch("ht.logging.adapters._wrap_logger")

        mock_base_logger = mocker.MagicMock(spec=logging.Logger)
        mock_dialog = mocker.MagicMock(spec=bool)

        mock_inst = mocker.MagicMock(spec=ht.logging.adapters.HoudiniLoggerAdapter)

        orig_info = mock_inst.info

        mock_super_new.return_value = mock_inst

        cls = ht.logging.adapters.HoudiniLoggerAdapter

        wrap_dict = {
            "info": hou.severityType.ImportantMessage,
            "warning": None,
            "foobles": None,
        }

        mocker.patch.dict(ht.logging.adapters._TO_WRAP, wrap_dict, clear=True)
        result = cls.__new__(cls, mock_base_logger, dialog=mock_dialog)

        assert result == mock_inst
        mock_super_new.assert_called_with(cls)

        mock_callable.assert_has_calls(
            [mocker.call(orig_info), mocker.call(mock_inst.warning)]
        )

        mock_wrap.assert_called_with(orig_info, hou.severityType.ImportantMessage)

        assert mock_inst.info == mock_wrap.return_value

    # Properties

    def test_dialog(self, init_adapter, mocker):
        """Test the 'dialog' property."""
        adapter = init_adapter()

        mock_value1 = mocker.MagicMock(spec=bool)
        adapter._dialog = mock_value1

        assert adapter.dialog == mock_value1

        mock_value2 = mocker.MagicMock(spec=bool)
        adapter.dialog = mock_value2
        assert adapter._dialog == mock_value2

    def test_node(self, init_adapter, mocker):
        """Test the 'node' property."""
        adapter = init_adapter()

        mock_value1 = mocker.MagicMock(spec=hou.Node)
        adapter._node = mock_value1
        assert adapter.node == mock_value1

        mock_value2 = mocker.MagicMock(spec=hou.Node)
        adapter.node = mock_value2
        assert adapter._node == mock_value2

    def test_status_bar(self, init_adapter, mocker):
        """Test the 'status_bar' property."""
        adapter = init_adapter()

        mock_value1 = mocker.MagicMock(spec=bool)
        adapter._status_bar = mock_value1
        assert adapter.status_bar == mock_value1

        mock_value2 = mocker.MagicMock(spec=bool)
        adapter.status_bar = mock_value2
        assert adapter._status_bar == mock_value2

    # Methods

    # process

    def test_process__node_arg(self, init_adapter, mocker):
        """Test when passing a node."""
        mocker.patch.dict(ht.logging.adapters._TO_WRAP, {}, clear=True)
        mocker.patch.object(
            ht.logging.adapters.HoudiniLoggerAdapter,
            "node",
            new_callable=mocker.PropertyMock,
        )
        mocker.patch.object(
            ht.logging.adapters.HoudiniLoggerAdapter,
            "dialog",
            new_callable=mocker.PropertyMock(return_value=False),
        )
        mocker.patch.object(
            ht.logging.adapters.HoudiniLoggerAdapter,
            "status_bar",
            new_callable=mocker.PropertyMock(return_value=False),
        )
        mocker.patch("ht.logging.adapters.hou.isUIAvailable", return_value=False)

        mock_message = mocker.MagicMock(spec=str)

        mock_node = mocker.MagicMock(spec=hou.Node)

        kwargs = {"extra": {"node": mock_node}}

        log = init_adapter()

        result = log.process(mock_message, kwargs)

        assert result == (
            "{} - {}".format(mock_node.path.return_value, mock_message),
            kwargs,
        )

        mock_node.path.assert_called()

    def test_process__node_property(self, init_adapter, mocker):
        """Test when using the 'node' property."""
        mocker.patch.dict(ht.logging.adapters._TO_WRAP, {}, clear=True)
        mock_node_prop = mocker.patch.object(
            ht.logging.adapters.HoudiniLoggerAdapter,
            "node",
            new_callable=mocker.PropertyMock,
        )
        mocker.patch.object(
            ht.logging.adapters.HoudiniLoggerAdapter,
            "dialog",
            new_callable=mocker.PropertyMock(return_value=False),
        )
        mocker.patch.object(
            ht.logging.adapters.HoudiniLoggerAdapter,
            "status_bar",
            new_callable=mocker.PropertyMock(return_value=False),
        )
        mocker.patch("ht.logging.adapters.hou.isUIAvailable", return_value=False)

        mock_message = mocker.MagicMock(spec=str)

        kwargs = {"extra": {}}

        log = init_adapter()

        result = log.process(mock_message, kwargs)

        assert result == (
            "{} - {}".format(
                mock_node_prop.return_value.path.return_value, mock_message
            ),
            kwargs,
        )

        mock_node_prop.return_value.path.assert_called()

    def test_process__ui_passed_no_severity_no_title(
        self, init_adapter, mocker, mock_hou_ui
    ):
        """Test passing 'dialog' and 'status_bar' via extra dict with no severity or title."""
        mocker.patch.dict(ht.logging.adapters._TO_WRAP, {}, clear=True)
        mocker.patch.object(
            ht.logging.adapters.HoudiniLoggerAdapter,
            "node",
            new_callable=mocker.PropertyMock(return_value=None),
        )
        mocker.patch.object(
            ht.logging.adapters.HoudiniLoggerAdapter,
            "dialog",
            new_callable=mocker.PropertyMock(return_value=False),
        )
        mocker.patch.object(
            ht.logging.adapters.HoudiniLoggerAdapter,
            "status_bar",
            new_callable=mocker.PropertyMock(return_value=False),
        )

        mock_message = mocker.MagicMock(spec=str)

        kwargs = {"extra": {"dialog": True, "status_bar": True}}

        log = init_adapter()

        result = log.process(mock_message, kwargs)

        assert result == (mock_message, kwargs)

        mock_hou_ui.displayMessage.assert_called_with(
            mock_message, severity=hou.severityType.Message, title=None
        )
        mock_hou_ui.setStatusMessage.assert_called_with(
            mock_message, severity=hou.severityType.Message
        )

    def test_process__ui_properties_with_severity_and_title(
        self, init_adapter, mocker, mock_hou_ui
    ):
        """Test passing 'dialog' and 'status_bar' via properties with a severity and title."""
        mocker.patch.dict(ht.logging.adapters._TO_WRAP, {}, clear=True)
        mocker.patch.object(
            ht.logging.adapters.HoudiniLoggerAdapter,
            "node",
            new_callable=mocker.PropertyMock(return_value=None),
        )
        mocker.patch.object(
            ht.logging.adapters.HoudiniLoggerAdapter,
            "dialog",
            new_callable=mocker.PropertyMock(return_value=True),
        )
        mocker.patch.object(
            ht.logging.adapters.HoudiniLoggerAdapter,
            "status_bar",
            new_callable=mocker.PropertyMock(return_value=True),
        )

        mock_message = mocker.MagicMock(spec=str)
        mock_title = mocker.MagicMock(spec=str)

        kwargs = {"extra": {"severity": hou.severityType.Error, "title": mock_title}}

        log = init_adapter()

        result = log.process(mock_message, kwargs)

        assert result == (mock_message, kwargs)

        mock_hou_ui.displayMessage.assert_called_with(
            mock_message, severity=hou.severityType.Error, title=mock_title
        )
        mock_hou_ui.setStatusMessage.assert_called_with(
            mock_message, severity=hou.severityType.Error
        )

    def test_process__message_args(self, init_adapter, mocker, mock_hou_ui):
        """Test passing along 'message_args'."""
        mocker.patch.dict(ht.logging.adapters._TO_WRAP, {}, clear=True)
        mocker.patch.object(
            ht.logging.adapters.HoudiniLoggerAdapter,
            "node",
            new_callable=mocker.PropertyMock(return_value=None),
        )
        mocker.patch.object(
            ht.logging.adapters.HoudiniLoggerAdapter,
            "dialog",
            new_callable=mocker.PropertyMock(return_value=True),
        )
        mocker.patch.object(
            ht.logging.adapters.HoudiniLoggerAdapter,
            "status_bar",
            new_callable=mocker.PropertyMock(return_value=False),
        )

        mock_message = mocker.MagicMock(spec=str)
        mock_arg = mocker.MagicMock(spec=str)

        kwargs = {"extra": {"message_args": (mock_arg,)}}

        log = init_adapter()

        result = log.process(mock_message, kwargs)

        assert result == (mock_message, kwargs)

        mock_hou_ui.displayMessage.assert_called_with(
            mock_message.__mod__.return_value,
            severity=hou.severityType.Message,
            title=None,
        )

        mock_message.__mod__.assert_called_with((mock_arg,))

    def test_process__message_args_no_display(self, init_adapter, mocker, mock_hou_ui):
        """Test passing along 'message_args' but not displaying them."""
        mocker.patch.dict(ht.logging.adapters._TO_WRAP, {}, clear=True)
        mocker.patch.object(
            ht.logging.adapters.HoudiniLoggerAdapter,
            "node",
            new_callable=mocker.PropertyMock(return_value=None),
        )
        mocker.patch.object(
            ht.logging.adapters.HoudiniLoggerAdapter,
            "dialog",
            new_callable=mocker.PropertyMock(return_value=False),
        )
        mocker.patch.object(
            ht.logging.adapters.HoudiniLoggerAdapter,
            "status_bar",
            new_callable=mocker.PropertyMock(return_value=False),
        )
        mocker.patch("ht.logging.adapters.hou.hipFile.basename")

        mock_message = mocker.MagicMock(spec=str)
        mock_arg = mocker.MagicMock(spec=str)

        kwargs = {"extra": {"message_args": (mock_arg,)}}

        log = init_adapter()

        result = log.process(mock_message, kwargs)

        assert result == (mock_message, kwargs)

        mock_hou_ui.displayMessage.assert_not_called()

        mock_message.__mod__.assert_called_with((mock_arg,))

    def test_process__no_extra(self, init_adapter, mocker):
        """Test passing along an empty kwargs dict."""
        mocker.patch.dict(ht.logging.adapters._TO_WRAP, {}, clear=True)
        mock_node_prop = mocker.patch.object(
            ht.logging.adapters.HoudiniLoggerAdapter,
            "node",
            new_callable=mocker.PropertyMock,
        )
        mocker.patch.object(
            ht.logging.adapters.HoudiniLoggerAdapter,
            "dialog",
            new_callable=mocker.PropertyMock(return_value=False),
        )
        mocker.patch.object(
            ht.logging.adapters.HoudiniLoggerAdapter,
            "status_bar",
            new_callable=mocker.PropertyMock(return_value=False),
        )
        mocker.patch("ht.logging.adapters.hou.hipFile.basename")

        mock_message = mocker.MagicMock(spec=str)

        kwargs = {}

        log = init_adapter()

        result = log.process(mock_message, kwargs)

        assert result == (mock_message, kwargs)

        mock_node_prop.assert_not_called()


class Test__wrap_logger(object):
    """Test ht.logging.adapters._wrap_logger."""

    def test_all_kwargs(self, mocker):
        """Test with passing all optional kwarg args."""
        # A fake function to wrap.
        mock_func = mocker.MagicMock(spec=str)
        mock_func.__name__ = "test"

        # Wrap the test function up.
        func = ht.logging.adapters._wrap_logger(mock_func, hou.severityType.Error)

        # Extra dictionary that will get the logger data added to it.
        extra = {}

        # Mock function args.
        mock_arg1 = mocker.MagicMock()
        mock_arg2 = mocker.MagicMock()

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_dialog = mocker.MagicMock(spec=bool)
        mock_status_bar = mocker.MagicMock(spec=bool)
        mock_title = mocker.MagicMock(spec=str)

        # Call the function.
        func(
            mock_arg1,
            mock_arg2,
            extra=extra,
            dialog=mock_dialog,
            node=mock_node,
            status_bar=mock_status_bar,
            title=mock_title,
        )

        # The expected extra dict values.
        expected = {
            "node": mock_node,
            "dialog": mock_dialog,
            "status_bar": mock_status_bar,
            "severity": hou.severityType.Error,
            "title": mock_title,
            "message_args": (mock_arg2,),
        }

        assert extra == expected

        # Verify that the wrapped function was called with the expected data.
        mock_func.assert_called_with(mock_arg1, mock_arg2, extra=expected)

    def test_no_kwargs(self, mocker):
        """Test with passing none of the optional kwarg args."""
        # A fake function to wrap.
        mock_func = mocker.MagicMock(spec=str)
        mock_func.__name__ = "test"

        # Wrap the test function up.
        func = ht.logging.adapters._wrap_logger(mock_func, hou.severityType.Error)

        # Extra dictionary that will get the logger data added to it.
        extra = {}

        # Mock function arg.
        mock_arg = mocker.MagicMock()

        # Call the function.
        func(mock_arg, extra=extra)

        # The expected extra dict values.
        expected = {"severity": hou.severityType.Error}

        assert extra == expected

        # Verify that the wrapped function was called with the expected data.
        mock_func.assert_called_with(mock_arg, extra=expected)
