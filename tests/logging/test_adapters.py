"""Tests for houdini_toolbox.logging.adapters module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import logging

# Third Party
import pytest

# Houdini Toolbox
import houdini_toolbox.logging.adapters

# Houdini
import hou

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def init_adapter(mocker):
    """Fixture to initialize an adapter."""
    mocker.patch.object(
        houdini_toolbox.logging.adapters.HoudiniLoggerAdapter, "__init__", lambda x, y: None
    )

    def _create():
        return houdini_toolbox.logging.adapters.HoudiniLoggerAdapter(None)

    return _create


# =============================================================================
# TESTS
# =============================================================================


class Test_HoudiniLoggerAdapter:
    """Test houdini_toolbox.logging.adapters.HoudiniLoggerAdapter."""

    def test___init__(self, mocker):
        """Test object initialization."""
        mock_super_init = mocker.patch.object(
            houdini_toolbox.logging.adapters.logging.LoggerAdapter, "__init__"
        )

        mock_base_logger = mocker.MagicMock(spec=logging.Logger)
        mock_dialog = mocker.MagicMock(spec=bool)
        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_status_bar = mocker.MagicMock(spec=bool)

        log = houdini_toolbox.logging.adapters.HoudiniLoggerAdapter(
            mock_base_logger, mock_dialog, mock_node, mock_status_bar
        )

        mock_super_init.assert_called_with(mock_base_logger, {})

        assert log._dialog == mock_dialog
        assert log._node == mock_node
        assert log._status_bar == mock_status_bar

    # from_name

    def test_from_name(self, mocker):
        """Test 'from_name' with default args."""
        mock_get_logger = mocker.patch("houdini_toolbox.logging.adapters.logging.getLogger")
        mock_init = mocker.patch.object(
            houdini_toolbox.logging.adapters.HoudiniLoggerAdapter, "__init__", return_value=None
        )

        mock_name = mocker.MagicMock(spec=str)

        result = houdini_toolbox.logging.adapters.HoudiniLoggerAdapter.from_name(mock_name)

        assert isinstance(result, houdini_toolbox.logging.adapters.HoudiniLoggerAdapter)

        mock_get_logger.assert_called_with(mock_name)
        mock_init.assert_called_with(
            mock_get_logger.return_value, dialog=False, node=None, status_bar=False
        )

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

    def test_process__node_arg(self, init_adapter, mocker, mock_ui_unavailable):
        """Test when passing a node."""
        mocker.patch.object(
            houdini_toolbox.logging.adapters.HoudiniLoggerAdapter,
            "node",
            new_callable=mocker.PropertyMock,
        )
        mocker.patch.object(
            houdini_toolbox.logging.adapters.HoudiniLoggerAdapter,
            "dialog",
            new_callable=mocker.PropertyMock(return_value=False),
        )
        mocker.patch.object(
            houdini_toolbox.logging.adapters.HoudiniLoggerAdapter,
            "status_bar",
            new_callable=mocker.PropertyMock(return_value=False),
        )

        mock_message = mocker.MagicMock(spec=str)

        mock_node = mocker.MagicMock(spec=hou.Node)

        kwargs = {"extra": {"node": mock_node}}

        log = init_adapter()

        result = log.process(mock_message, kwargs)

        assert result == (
            f"{mock_node.path.return_value} - {mock_message}",
            kwargs,
        )

        mock_node.path.assert_called()

    def test_process__node_property(self, init_adapter, mocker, mock_ui_unavailable):
        """Test when using the 'node' property."""
        mock_node_prop = mocker.patch.object(
            houdini_toolbox.logging.adapters.HoudiniLoggerAdapter,
            "node",
            new_callable=mocker.PropertyMock,
        )
        mocker.patch.object(
            houdini_toolbox.logging.adapters.HoudiniLoggerAdapter,
            "dialog",
            new_callable=mocker.PropertyMock(return_value=False),
        )
        mocker.patch.object(
            houdini_toolbox.logging.adapters.HoudiniLoggerAdapter,
            "status_bar",
            new_callable=mocker.PropertyMock(return_value=False),
        )

        mock_message = mocker.MagicMock(spec=str)

        kwargs = {"extra": {}}

        log = init_adapter()

        result = log.process(mock_message, kwargs)

        assert result == (
            f"{ mock_node_prop.return_value.path.return_value} - {mock_message}",
            kwargs,
        )

        mock_node_prop.return_value.path.assert_called()

    def test_process__ui_passed_no_severity_no_title(
        self, init_adapter, mocker, mock_hou_ui
    ):
        """Test passing 'dialog' and 'status_bar' via extra dict with no severity or title."""
        mocker.patch.object(
            houdini_toolbox.logging.adapters.HoudiniLoggerAdapter,
            "node",
            new_callable=mocker.PropertyMock(return_value=None),
        )
        mocker.patch.object(
            houdini_toolbox.logging.adapters.HoudiniLoggerAdapter,
            "dialog",
            new_callable=mocker.PropertyMock(return_value=False),
        )
        mocker.patch.object(
            houdini_toolbox.logging.adapters.HoudiniLoggerAdapter,
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
        mocker.patch.object(
            houdini_toolbox.logging.adapters.HoudiniLoggerAdapter,
            "node",
            new_callable=mocker.PropertyMock(return_value=None),
        )
        mocker.patch.object(
            houdini_toolbox.logging.adapters.HoudiniLoggerAdapter,
            "dialog",
            new_callable=mocker.PropertyMock(return_value=True),
        )
        mocker.patch.object(
            houdini_toolbox.logging.adapters.HoudiniLoggerAdapter,
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
        mocker.patch.object(
            houdini_toolbox.logging.adapters.HoudiniLoggerAdapter,
            "node",
            new_callable=mocker.PropertyMock(return_value=None),
        )
        mocker.patch.object(
            houdini_toolbox.logging.adapters.HoudiniLoggerAdapter,
            "dialog",
            new_callable=mocker.PropertyMock(return_value=True),
        )
        mocker.patch.object(
            houdini_toolbox.logging.adapters.HoudiniLoggerAdapter,
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
        mocker.patch.object(
            houdini_toolbox.logging.adapters.HoudiniLoggerAdapter,
            "node",
            new_callable=mocker.PropertyMock(return_value=None),
        )
        mocker.patch.object(
            houdini_toolbox.logging.adapters.HoudiniLoggerAdapter,
            "dialog",
            new_callable=mocker.PropertyMock(return_value=False),
        )
        mocker.patch.object(
            houdini_toolbox.logging.adapters.HoudiniLoggerAdapter,
            "status_bar",
            new_callable=mocker.PropertyMock(return_value=False),
        )
        mocker.patch("houdini_toolbox.logging.adapters.hou.hipFile.basename")

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
        mock_node_prop = mocker.patch.object(
            houdini_toolbox.logging.adapters.HoudiniLoggerAdapter,
            "node",
            new_callable=mocker.PropertyMock,
        )
        mocker.patch.object(
            houdini_toolbox.logging.adapters.HoudiniLoggerAdapter,
            "dialog",
            new_callable=mocker.PropertyMock(return_value=False),
        )
        mocker.patch.object(
            houdini_toolbox.logging.adapters.HoudiniLoggerAdapter,
            "status_bar",
            new_callable=mocker.PropertyMock(return_value=False),
        )
        mocker.patch("houdini_toolbox.logging.adapters.hou.hipFile.basename")

        mock_message = mocker.MagicMock(spec=str)

        kwargs = {}

        log = init_adapter()

        result = log.process(mock_message, kwargs)

        assert result == (mock_message, kwargs)

        mock_node_prop.assert_not_called()

    @pytest.mark.parametrize(
        "level, severity, extra",
        [
            ("info", hou.severityType.ImportantMessage, {}),
            ("warning", hou.severityType.Warning, {}),
            ("error", hou.severityType.Error, {}),
            ("critical", hou.severityType.Error, {}),
            ("debug", hou.severityType.Message, {}),
            ("exception", hou.severityType.Error, {"exc_info": 1}),
        ],
    )
    def test_calls(self, init_adapter, mocker, level, severity, extra):
        """Test the various log calls."""
        mock_process = mocker.patch("houdini_toolbox.logging.adapters.HoudiniLoggerAdapter.process")
        mock_pre_process = mocker.patch("houdini_toolbox.logging.adapters._pre_process_args")

        mock_patch = mocker.patch("houdini_toolbox.logging.adapters._patch_logger")

        mock_process_msg = mocker.MagicMock(spec=str)

        mock_logger = mocker.MagicMock(spec=logging.Logger)

        log = init_adapter()
        log.logger = mock_logger

        mock_msg = mocker.MagicMock(spec=str)

        args = (mocker.MagicMock(),)

        kwargs = {"foo": mocker.MagicMock()}
        kwargs.update(extra)

        mock_process.return_value = (mock_process_msg, kwargs)

        getattr(log, level)(mock_msg, *args, **kwargs)

        mock_pre_process.assert_called_with(severity, args, kwargs)
        mock_process.assert_called_with(mock_msg, kwargs)

        mock_patch.assert_called_with(mock_logger)

        getattr(mock_logger, level).assert_called_with(
            mock_process_msg, *args, **kwargs
        )


def test__patch_logger(mocker):
    """Test houdini_toolbox.logging.adapters._patch_logger."""
    mock_patch = mocker.patch("houdini_toolbox.logging.adapters.patch_logger")

    mock_logger = mocker.MagicMock(spec=logging.Logger)

    original_class = mock_logger.__class__

    with houdini_toolbox.logging.adapters._patch_logger(mock_logger):
        assert mock_logger.__class__ == mock_patch.return_value

    assert mock_logger.__class__ == original_class


class Test__pre_process_args:
    """Test houdini_toolbox.logging.adapters._pre_process_args."""

    def test_all_kwargs(self, mocker):
        """Test with passing all optional kwarg args."""
        # Mock function args.
        mock_arg1 = mocker.MagicMock()
        mock_arg2 = mocker.MagicMock()

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_dialog = mocker.MagicMock(spec=bool)
        mock_status_bar = mocker.MagicMock(spec=bool)
        mock_notify = mocker.MagicMock(spec=bool)
        mock_title = mocker.MagicMock(spec=str)
        mock_stacklevel = mocker.MagicMock(spec=int)

        kwargs = {
            "node": mock_node,
            "dialog": mock_dialog,
            "status_bar": mock_status_bar,
            "notify_send": mock_notify,
            "title": mock_title,
            "stacklevel": mock_stacklevel,
        }

        houdini_toolbox.logging.adapters._pre_process_args(
            hou.severityType.Error, (mock_arg1, mock_arg2), kwargs
        )

        # The expected extra dict values.
        expected = {
            "node": mock_node,
            "dialog": mock_dialog,
            "status_bar": mock_status_bar,
            "notify_send": mock_notify,
            "severity": hou.severityType.Error,
            "title": mock_title,
            "message_args": (
                mock_arg1,
                mock_arg2,
            ),
        }

        assert kwargs["extra"] == expected

        assert kwargs["stacklevel"] == mock_stacklevel

    def test_no_kwargs(self):
        """Test with passing none of the optional kwarg args."""
        kwargs = {}

        houdini_toolbox.logging.adapters._pre_process_args(hou.severityType.Error, (), kwargs)

        # The expected extra dict values.
        expected = {"severity": hou.severityType.Error}

        assert kwargs["extra"] == expected

        assert kwargs["stacklevel"] == 2
