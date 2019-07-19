"""Tests for ht.logging.adapters module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
from __future__ import absolute_import
import logging
from mock import MagicMock, PropertyMock, call, patch
import unittest

# Houdini Toolbox Imports
import ht.logging.adapters

# Houdini Imports
import hou

reload(ht.logging.adapters)


# =============================================================================
# CLASSES
# =============================================================================

class Test_HoudiniLoggerAdapter(unittest.TestCase):
    """Test ht.logging.adapters.HoudiniLoggerAdapter."""

    def test___init__(self):
        """Test object initialization."""
        mock_base_logger = MagicMock(spec=logging.Logger)
        mock_dialog = MagicMock(spec=bool)
        mock_node = MagicMock(spec=hou.Node)
        mock_status_bar = MagicMock(spec=bool)

        with patch.object(ht.logging.adapters.logging.LoggerAdapter, "__init__") as mock_super_init:
            log = ht.logging.adapters.HoudiniLoggerAdapter(mock_base_logger, mock_dialog, mock_node, mock_status_bar)

            mock_super_init.assert_called_with(mock_base_logger, {})

        self.assertEqual(log._dialog, mock_dialog)
        self.assertEqual(log._node, mock_node)
        self.assertEqual(log._status_bar, mock_status_bar)

    @patch("ht.logging.adapters._wrap_logger")
    @patch("ht.logging.adapters.callable", side_effect=(True, False))
    @patch.object(ht.logging.adapters.logging.LoggerAdapter, "__new__")
    def test___new__(self, mock_super_new, mock_callable, mock_wrap):
        """Test object creation."""
        mock_base_logger = MagicMock(spec=logging.Logger)
        mock_dialog = MagicMock(spec=bool)

        mock_inst = MagicMock(spec=ht.logging.adapters.HoudiniLoggerAdapter)

        orig_info = mock_inst.info

        mock_super_new.return_value = mock_inst

        cls = ht.logging.adapters.HoudiniLoggerAdapter

        wrap_dict = {
            "info": hou.severityType.ImportantMessage,
            "warning": None,
            "foobles": None
        }

        with patch.dict(ht.logging.adapters._TO_WRAP, wrap_dict, clear=True):
            result = cls.__new__(cls, mock_base_logger, dialog=mock_dialog)

        self.assertEqual(result, mock_inst)
        mock_super_new.assert_called_with(cls)

        mock_callable.assert_has_calls(
            [
                call(orig_info),
                call(mock_inst.warning)
            ]
        )

        mock_wrap.assert_called_with(orig_info, hou.severityType.ImportantMessage)

        self.assertEqual(mock_inst.info, mock_wrap.return_value)

    # Properties

    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "__init__", lambda x, y, z, w: None)
    def test_dialog(self):
        """Test the 'dialog' property."""
        adapter = ht.logging.adapters.HoudiniLoggerAdapter(None, None, None)

        mock_value1 = MagicMock(spec=bool)

        adapter._dialog = mock_value1

        self.assertEqual(adapter.dialog, mock_value1)

        mock_value2 = MagicMock(spec=bool)

        adapter.dialog = mock_value2
        self.assertEqual(adapter._dialog, mock_value2)

    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "__init__", lambda x, y, z, w: None)
    def test_node(self):
        """Test the 'node' property."""
        adapter = ht.logging.adapters.HoudiniLoggerAdapter(None, None, None)

        mock_value1 = MagicMock(spec=hou.Node)

        adapter._node = mock_value1

        self.assertEqual(adapter.node, mock_value1)

        mock_value2 = MagicMock(spec=hou.Node)

        adapter.node = mock_value2
        self.assertEqual(adapter._node, mock_value2)

    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "__init__", lambda x, y, z, w: None)
    def test_status_bar(self):
        """Test the 'status_bar' property."""
        adapter = ht.logging.adapters.HoudiniLoggerAdapter(None, None, None)

        mock_value1 = MagicMock(spec=bool)

        adapter._status_bar = mock_value1

        self.assertEqual(adapter.status_bar, mock_value1)

        mock_value2 = MagicMock(spec=bool)

        adapter.status_bar = mock_value2
        self.assertEqual(adapter._status_bar, mock_value2)

    # Methods

    # process

    @patch("ht.logging.adapters.hou.isUIAvailable", return_value=False)
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "status_bar", new_callable=PropertyMock(return_value=False))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "dialog", new_callable=PropertyMock(return_value=False))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "node", new_callable=PropertyMock)
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "__init__", lambda x, y, z, w: None)
    @patch.dict(ht.logging.adapters._TO_WRAP, {}, clear=True)
    def test_process__node_arg(self, mock_node_prop, mock_dialog_prop, mock_status_prop, mock_available):
        """Test when passing a node."""
        mock_message = MagicMock(spec=str)

        mock_node = MagicMock(spec=hou.Node)

        kwargs = {
            "extra": {"node": mock_node}
        }

        log = ht.logging.adapters.HoudiniLoggerAdapter(None, None, None)

        result = log.process(mock_message, kwargs)

        self.assertEqual(result, ("{} - {}".format(mock_node.path.return_value, mock_message), kwargs))

        mock_node.path.assert_called()

    @patch("ht.logging.adapters.hou.isUIAvailable", return_value=False)
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "status_bar", new_callable=PropertyMock(return_value=False))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "dialog", new_callable=PropertyMock(return_value=False))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "node", new_callable=PropertyMock)
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "__init__", lambda x, y, z, w: None)
    @patch.dict(ht.logging.adapters._TO_WRAP, {}, clear=True)
    def test_process__node_property(self, mock_node_prop, mock_dialog_prop, mock_status_prop, mock_available):
        """Test when using the 'node' property."""
        mock_message = MagicMock(spec=str)

        kwargs = {
            "extra": {}
        }

        log = ht.logging.adapters.HoudiniLoggerAdapter(None, None, None)

        result = log.process(mock_message, kwargs)

        self.assertEqual(
            result,
            ("{} - {}".format(mock_node_prop.return_value.path.return_value, mock_message), kwargs)
        )

        mock_node_prop.return_value.path.assert_called()

    @patch("ht.logging.adapters.hou.isUIAvailable", return_value=True)
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "status_bar", new_callable=PropertyMock(return_value=False))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "dialog", new_callable=PropertyMock(return_value=False))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "node", new_callable=PropertyMock(return_value=None))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "__init__", lambda x, y, z, w: None)
    @patch.dict(ht.logging.adapters._TO_WRAP, {}, clear=True)
    def test_process__ui_passed_no_severity_no_title(self, mock_node_prop, mock_dialog_prop, mock_status_prop, mock_available):
        """Test passing 'dialog' and 'status_bar' via extra dict with no severity or title."""
        mock_message = MagicMock(spec=str)

        kwargs = {
            "extra": {"dialog": True, "status_bar": True}
        }

        mock_ui = MagicMock()
        hou.ui = mock_ui

        log = ht.logging.adapters.HoudiniLoggerAdapter(None, None, None)

        result = log.process(mock_message, kwargs)

        self.assertEqual(result, (mock_message, kwargs))

        mock_ui.displayMessage.assert_called_with(mock_message, severity=hou.severityType.Message, title=None)
        mock_ui.setStatusMessage.assert_called_with(mock_message, severity=hou.severityType.Message)

        del hou.ui

    @patch("ht.logging.adapters.hou.isUIAvailable", return_value=True)
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "status_bar", new_callable=PropertyMock(return_value=True))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "dialog", new_callable=PropertyMock(return_value=True))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "node", new_callable=PropertyMock(return_value=None))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "__init__", lambda x, y, z, w: None)
    @patch.dict(ht.logging.adapters._TO_WRAP, {}, clear=True)
    def test_process__ui_properties_with_severity_and_title(self, mock_node_prop, mock_dialog_prop, mock_status_prop, mock_available):
        """Test passing 'dialog' and 'status_bar' via properties with a severity and title."""
        mock_message = MagicMock(spec=str)
        mock_title = MagicMock(spec=str)

        kwargs = {
            "extra": {"severity": hou.severityType.Error, "title": mock_title}
        }

        mock_ui = MagicMock()
        hou.ui = mock_ui

        log = ht.logging.adapters.HoudiniLoggerAdapter(None, None, None)

        result = log.process(mock_message, kwargs)

        self.assertEqual(result, (mock_message, kwargs))

        mock_ui.displayMessage.assert_called_with(mock_message, severity=hou.severityType.Error, title=mock_title)
        mock_ui.setStatusMessage.assert_called_with(mock_message, severity=hou.severityType.Error)

        del hou.ui

    @patch("ht.logging.adapters.hou.hipFile.basename")
    @patch("ht.logging.adapters.hou.isUIAvailable", return_value=True)
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "status_bar", new_callable=PropertyMock(return_value=False))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "dialog", new_callable=PropertyMock(return_value=True))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "node", new_callable=PropertyMock(return_value=None))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "__init__", lambda x, y, z, w: None)
    @patch.dict(ht.logging.adapters._TO_WRAP, {}, clear=True)
    def test_process__message_args(self, mock_node_prop, mock_dialog_prop, mock_status_prop, mock_available, mock_basename):
        """Test passing along 'message_args'."""
        mock_message = MagicMock(spec=str)
        mock_arg = MagicMock(spec=str)

        kwargs = {"extra": {"message_args": (mock_arg, )}}

        mock_ui = MagicMock()
        hou.ui = mock_ui

        log = ht.logging.adapters.HoudiniLoggerAdapter(None, None, None)

        result = log.process(mock_message, kwargs)

        self.assertEqual(result, (mock_message, kwargs))

        mock_ui.displayMessage.assert_called_with(mock_message.__mod__.return_value, severity=hou.severityType.Message, title=None)

        mock_message.__mod__.assert_called_with((mock_arg, ))

        del hou.ui

    @patch("ht.logging.adapters.hou.hipFile.basename")
    @patch("ht.logging.adapters.hou.isUIAvailable", return_value=True)
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "status_bar", new_callable=PropertyMock(return_value=False))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "dialog", new_callable=PropertyMock(return_value=False))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "node", new_callable=PropertyMock(return_value=None))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "__init__", lambda x, y, z, w: None)
    @patch.dict(ht.logging.adapters._TO_WRAP, {}, clear=True)
    def test_process__message_args_no_display(self, mock_node_prop, mock_dialog_prop, mock_status_prop, mock_available, mock_basename):
        """Test passing along 'message_args' but not displaying them."""
        mock_message = MagicMock(spec=str)
        mock_arg = MagicMock(spec=str)

        kwargs = {"extra": {"message_args": (mock_arg, )}}

        mock_ui = MagicMock()
        hou.ui = mock_ui

        log = ht.logging.adapters.HoudiniLoggerAdapter(None, None, None)

        result = log.process(mock_message, kwargs)

        self.assertEqual(result, (mock_message, kwargs))

        mock_ui.displayMessage.assert_not_called()

        mock_message.__mod__.assert_called_with((mock_arg, ))

        del hou.ui

    @patch("ht.logging.adapters.hou.hipFile.basename")
    @patch("ht.logging.adapters.hou.isUIAvailable", return_value=False)
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "status_bar", new_callable=PropertyMock(return_value=False))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "dialog", new_callable=PropertyMock(return_value=False))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "node", new_callable=PropertyMock)
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "__init__", lambda x, y, z, w: None)
    @patch.dict(ht.logging.adapters._TO_WRAP, {}, clear=True)
    def test_process__no_extra(self, mock_node_prop, mock_dialog_prop, mock_status_prop, mock_available, mock_basename):
        """Test passing along an empty kwargs dict."""
        mock_message = MagicMock(spec=str)

        kwargs = {}

        log = ht.logging.adapters.HoudiniLoggerAdapter(None, None, None)

        result = log.process(mock_message, kwargs)

        self.assertEqual(result, (mock_message, kwargs))

        mock_node_prop.assert_not_called()


class Test__wrap_logger(unittest.TestCase):
    """Test ht.logging.adapters._wrap_logger."""

    def test_all_kwargs(self):
        """Test with passing all optional kwarg args."""
        # A fake function to wrap.
        mock_func = MagicMock(spec=str)
        mock_func.__name__ = "test"

        # Wrap the test function up.
        func = ht.logging.adapters._wrap_logger(mock_func, hou.severityType.Error)

        # Extra dictionary that will get the logger data added to it.
        extra = {}

        # Mock function args.
        mock_arg1 = MagicMock()
        mock_arg2 = MagicMock()

        mock_node = MagicMock(spec=hou.Node)
        mock_dialog = MagicMock(spec=bool)
        mock_status_bar = MagicMock(spec=bool)
        mock_title = MagicMock(spec=str)

        # Call the function.
        func(mock_arg1, mock_arg2, extra=extra, dialog=mock_dialog, node=mock_node, status_bar=mock_status_bar, title=mock_title)

        # The expected extra dict values.
        expected = {
            "node": mock_node,
            "dialog": mock_dialog,
            "status_bar": mock_status_bar,
            "severity": hou.severityType.Error,
            "title": mock_title,
            "message_args": (mock_arg2,)

        }

        self.assertEqual(extra, expected)

        # Verify that the wrapped function was called with the expected data.
        mock_func.assert_called_with(mock_arg1, mock_arg2, extra=expected)

    def test_no_kwargs(self):
        """Test with passing none of the optional kwarg args."""
        # A fake function to wrap.
        mock_func = MagicMock(spec=str)
        mock_func.__name__ = "test"

        # Wrap the test function up.
        func = ht.logging.adapters._wrap_logger(mock_func, hou.severityType.Error)

        # Extra dictionary that will get the logger data added to it.
        extra = {}

        # Mock function arg.
        mock_arg = MagicMock()

        # Call the function.
        func(mock_arg, extra=extra)

        # The expected extra dict values.
        expected = {
            "severity": hou.severityType.Error
        }

        self.assertEqual(extra, expected)

        # Verify that the wrapped function was called with the expected data.
        mock_func.assert_called_with(mock_arg, extra=expected)


# =============================================================================

if __name__ == '__main__':
    unittest.main()
