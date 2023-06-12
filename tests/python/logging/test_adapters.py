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
def test_adapter():
    """Fixture to provide a minimally set up HoudiniLoggerAdapter."""
    logger = logging.getLogger("test_logger")

    adapter = houdini_toolbox.logging.adapters.HoudiniLoggerAdapter(logger)

    yield adapter


# =============================================================================
# TESTS
# =============================================================================


class Test_HoudiniLoggerAdapter:
    """Test houdini_toolbox.logging.adapters.HoudiniLoggerAdapter."""

    def test___init__(self, mocker):
        """Test object initialization."""
        test_logger = logging.getLogger("test_logger")
        extra = {"extra": "value"}

        mock_dialog = mocker.MagicMock(spec=bool)
        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_status_bar = mocker.MagicMock(spec=bool)

        log = houdini_toolbox.logging.adapters.HoudiniLoggerAdapter(
            test_logger, mock_node, mock_dialog, mock_status_bar, extra=extra
        )

        assert log.logger == test_logger
        assert log.extra == extra

        assert log._dialog == mock_dialog
        assert log._node == mock_node
        assert log._status_bar == mock_status_bar

    def test_from_name(self):
        """Test HoudiniLoggerAdapter.from_name()."""
        result = houdini_toolbox.logging.adapters.HoudiniLoggerAdapter.from_name(
            "test_name"
        )

        assert result.logger.name == "test_name"

        result = houdini_toolbox.logging.adapters.HoudiniLoggerAdapter.from_name(
            "test_name",
            node=hou.node("/obj"),
            dialog=True,
            status_bar=True,
            extra={"foo": "bar"},
        )

        assert result.logger.name == "test_name"
        assert result.node == hou.node("/obj")
        assert result.dialog
        assert result.status_bar
        assert result.extra == {"foo": "bar"}

    # Properties

    def test_dialog(self, test_adapter):
        """Test HoudiniLoggerAdapter.dialog."""
        assert not test_adapter.dialog

        test_adapter.dialog = True
        assert test_adapter._dialog

    def test_node(self, test_adapter):
        """Test HoudiniLoggerAdapter.node."""
        assert test_adapter.node is None

        test_node = hou.node("/obj")
        test_adapter.node = test_node
        assert test_adapter._node == test_node

    def test_status_bar(self, test_adapter):
        """Test HoudiniLoggerAdapter.status_bar."""
        assert not test_adapter.status_bar

        test_adapter.status_bar = True
        assert test_adapter._status_bar

    # Methods

    def test_process__node_arg(self, test_adapter, mock_ui_unavailable):
        """Test HoudiniLoggerAdapter.process() when passing a node."""
        kwargs = {"extra": {"node": hou.node("/out")}}

        test_adapter.node = hou.node("/obj")

        result = test_adapter.process("test logger message", kwargs)

        assert result == ("/out - test logger message", kwargs)

    def test_process__node_property(self, test_adapter, mock_ui_unavailable):
        """Test HoudiniLoggerAdapter.process() when using the node property."""
        kwargs = {"extra": {}}

        test_adapter.node = hou.node("/obj")

        result = test_adapter.process("test logger message", kwargs)

        assert result == ("/obj - test logger message", kwargs)

    def test_process__ui_passed_no_severity_no_title(
        self, mocker, test_adapter, mock_hou_ui
    ):
        """Test HoudiniLoggerAdapter.process() when passing 'dialog' and 'status_bar' via the extra dict."""
        mock_message = mocker.MagicMock(spec=str)

        kwargs = {"extra": {"dialog": True, "status_bar": True}}

        result = test_adapter.process(mock_message, kwargs)

        assert result == (mock_message, kwargs)

        mock_hou_ui.displayMessage.assert_called_with(
            mock_message, severity=hou.severityType.Message, title=None
        )
        mock_hou_ui.setStatusMessage.assert_called_with(
            mock_message, severity=hou.severityType.Message
        )

    def test_process__ui_properties_with_severity_and_title(
        self, mocker, test_adapter, mock_hou_ui
    ):
        """Test HoudiniLoggerAdapter.process() passing 'dialog' and 'status_bar' via properties with a severity
        and title."""
        test_adapter.dialog = True
        test_adapter.status_bar = True

        mock_message = mocker.MagicMock(spec=str)
        mock_title = mocker.MagicMock(spec=str)

        kwargs = {"extra": {"severity": hou.severityType.Error, "title": mock_title}}

        result = test_adapter.process(mock_message, kwargs)

        assert result == (mock_message, kwargs)

        mock_hou_ui.displayMessage.assert_called_with(
            mock_message, severity=hou.severityType.Error, title=mock_title
        )
        mock_hou_ui.setStatusMessage.assert_called_with(
            mock_message, severity=hou.severityType.Error
        )

    def test_process__message_args(self, test_adapter, mock_hou_ui):
        """Test HoudiniLoggerAdapter.process() passing 'message_args'."""
        test_adapter.dialog = True

        kwargs = {"extra": {"message_args": ("extra", 3)}}

        result = test_adapter.process("test logger message %s %d", kwargs)

        assert result == ("test logger message %s %d", kwargs)

        mock_hou_ui.displayMessage.assert_called_with(
            "test logger message extra 3",
            severity=hou.severityType.Message,
            title=None,
        )

    def test_process__message_args_no_display(self, test_adapter, mock_hou_ui):
        """Test HoudiniLoggerAdapter.process() passing 'message_args' but not displaying them."""
        kwargs = {"extra": {"message_args": ("extra", 3)}}

        result = test_adapter.process("test logger message %s %d", kwargs)

        assert result == ("test logger message %s %d", kwargs)

        mock_hou_ui.displayMessage.assert_not_called()

    def test_process__no_extra(self, mocker, test_adapter):
        """Test HoudiniLoggerAdapter.process() when passing an empty kwargs dict."""
        mock_message = mocker.MagicMock(spec=str)

        kwargs = {}

        result = test_adapter.process(mock_message, kwargs)

        assert result == (mock_message, kwargs)

    @pytest.mark.parametrize(
        "level, severity, num_message_args, passed_kwargs",
        [
            ("info", hou.severityType.ImportantMessage, 0, {"status_bar": True}),
            ("warning", hou.severityType.Warning, 1, {"node": hou.node("/obj")}),
            ("error", hou.severityType.Error, 2, {"dialog": True}),
            ("critical", hou.severityType.Error, 1, {"title": "A Title"}),
            ("debug", hou.severityType.Message, 1, {"stacklevel": 3}),
            ("exception", hou.severityType.Error, 1, {}),
        ],
    )
    def test_calls(
        self, mocker, test_adapter, level, severity, num_message_args, passed_kwargs
    ):
        """Test the various log calls.

        This helps to test the _wrap_logger functionality and that the wrapping occurred as expected.
        """
        mock_logger = mocker.MagicMock(spec=logging.Logger)
        mocker.patch.object(test_adapter, "logger", mock_logger)

        mock_msg = mocker.MagicMock(spec=str)

        message_args = tuple(
            [mocker.MagicMock(spec=str) for i in range(num_message_args)]
        )

        kwargs = {
            "foo": 3,  # A dummy extra kwarg our calling code does not care about
        }
        kwargs.update(passed_kwargs)

        # We're going to mock process() call to determine whether all our wrapper logic
        # runs and passes the expected data for the actual log call.
        mock_process = mocker.patch(
            "houdini_toolbox.logging.adapters.HoudiniLoggerAdapter.process",
            return_value=(mocker.MagicMock(spec=str), kwargs),
        )

        expected_kwargs = {
            "foo": 3,
            "extra": {
                "severity": severity,
            },
            "stacklevel": passed_kwargs.get("stacklevel", 4),
        }

        # If there were any extra message args we expect them to have been added
        # to the extra dict.
        if num_message_args:
            expected_kwargs["extra"]["message_args"] = message_args

        for arg, value in passed_kwargs.items():
            if arg in ("node", "dialog", "status_bar", "title"):
                expected_kwargs["extra"][arg] = value

        # If logging an exception, ensure that exc_info=True is passed.
        if level == "exception":
            expected_kwargs["exc_info"] = True

        getattr(test_adapter, level)(mock_msg, *message_args, **kwargs)

        mock_process.assert_called_with(mock_msg, expected_kwargs)
