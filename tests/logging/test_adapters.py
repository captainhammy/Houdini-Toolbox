"""Tests for ht.logging.adapters module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
from __future__ import absolute_import
import logging
from mock import MagicMock, PropertyMock, patch
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
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "__init__", lambda x, y, z, w: None)
    def test___new__(self, mock_wrap):
        mock_base_logger = MagicMock(spec=logging.Logger)
        mock_dialog = MagicMock(spec=bool)
        mock_node = MagicMock(spec=hou.Node)
        mock_status_bar = MagicMock(spec=bool)

        wrap_dict = {
            "info": hou.severityType.ImportantMessage,
            "foobles": None
        }

        orig_info = ht.logging.adapters.HoudiniLoggerAdapter.info

        with patch.dict(ht.logging.adapters.HoudiniLoggerAdapter._TO_WRAP, wrap_dict, clear=True):
            with patch.object(ht.logging.adapters.logging.LoggerAdapter, "__new__") as mock_super_new:

                log = ht.logging.adapters.HoudiniLoggerAdapter(mock_base_logger, mock_dialog, mock_node, status_bar=mock_status_bar)

                self.assertEqual(log, mock_super_new.return_value)

                mock_super_new.assert_called_with(ht.logging.adapters.HoudiniLoggerAdapter, mock_base_logger, mock_dialog, mock_node, status_bar=mock_status_bar)

        mock_wrap.assert_called_with(orig_info, hou.severityType.ImportantMessage)

        self.assertEqual(ht.logging.adapters.HoudiniLoggerAdapter.info, mock_wrap.return_value)

    # Properties

    # dialog

    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "__init__", lambda x, y, z, w: None)
    def test_dialog(self):
        with patch.dict(ht.logging.adapters.HoudiniLoggerAdapter._TO_WRAP, {}, clear=True):
            log = ht.logging.adapters.HoudiniLoggerAdapter(None, None, None)

        mock_value1 = MagicMock(spec=bool)

        log._dialog = mock_value1

        self.assertEqual(log.dialog, mock_value1)

        mock_value2 = MagicMock(spec=bool)

        log.dialog = mock_value2
        self.assertEqual(log._dialog, mock_value2)

    # node

    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "__init__", lambda x, y, z, w: None)
    def test_node(self):
        with patch.dict(ht.logging.adapters.HoudiniLoggerAdapter._TO_WRAP, {}, clear=True):
            log = ht.logging.adapters.HoudiniLoggerAdapter(None, None, None)

        mock_value1 = MagicMock(spec=hou.Node)

        log._node = mock_value1

        self.assertEqual(log.node, mock_value1)

        mock_value2 = MagicMock(spec=hou.Node)

        log.node = mock_value2
        self.assertEqual(log._node, mock_value2)

    # status_bar

    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "__init__", lambda x, y, z, w: None)
    def test_status_bar(self):
        with patch.dict(ht.logging.adapters.HoudiniLoggerAdapter._TO_WRAP, {}, clear=True):
            log = ht.logging.adapters.HoudiniLoggerAdapter(None, None, None)

        mock_value1 = MagicMock(spec=bool)

        log._status_bar = mock_value1

        self.assertEqual(log.status_bar, mock_value1)

        mock_value2 = MagicMock(spec=bool)

        log.status_bar = mock_value2
        self.assertEqual(log._status_bar, mock_value2)

    # Methods

    # process

    @patch("ht.logging.adapters.hou.isUIAvailable", return_value=False)
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "status_bar", new_callable=PropertyMock(return_value=False))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "dialog", new_callable=PropertyMock(return_value=False))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "node", new_callable=PropertyMock)
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "__init__", lambda x, y, z, w: None)
    def test_process__node_arg(self, mock_node_prop, mock_dialog_prop, mock_status_prop, mock_available):
        mock_message = MagicMock(spec=str)

        mock_node = MagicMock(spec=hou.Node)

        kwargs = {
            "extra": {"node": mock_node}
        }

        with patch.dict(ht.logging.adapters.HoudiniLoggerAdapter._TO_WRAP, {}, clear=True):
            log = ht.logging.adapters.HoudiniLoggerAdapter(None, None, None)

        result = log.process(mock_message, kwargs)

        self.assertEqual(result, ("{} - {}".format(mock_node.path.return_value, mock_message), kwargs))

        mock_node.path.assert_called()

    @patch("ht.logging.adapters.hou.isUIAvailable", return_value=False)
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "status_bar", new_callable=PropertyMock(return_value=False))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "dialog", new_callable=PropertyMock(return_value=False))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "node", new_callable=PropertyMock)
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "__init__", lambda x, y, z, w: None)
    def test_process__node_property(self, mock_node_prop, mock_dialog_prop, mock_status_prop, mock_available):
        mock_message = MagicMock(spec=str)

        kwargs = {
            "extra": {}
        }

        with patch.dict(ht.logging.adapters.HoudiniLoggerAdapter._TO_WRAP, {}, clear=True):
            log = ht.logging.adapters.HoudiniLoggerAdapter(None, None, None)

        result = log.process(mock_message, kwargs)

        self.assertEqual(result, ("{} - {}".format(mock_node_prop.return_value.path.return_value, mock_message), kwargs))

        mock_node_prop.return_value.path.assert_called()

    @patch("ht.logging.adapters.hou.isUIAvailable", return_value=True)
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "status_bar", new_callable=PropertyMock(return_value=False))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "dialog", new_callable=PropertyMock(return_value=False))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "node", new_callable=PropertyMock(return_value=None))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "__init__", lambda x, y, z, w: None)
    def test_process__ui_passed_no_severity_no_title(self, mock_node_prop, mock_dialog_prop, mock_status_prop, mock_available):
        mock_message = MagicMock(spec=str)

        kwargs = {
            "extra": {"dialog": True, "status_bar": True}
        }

        mock_ui = MagicMock()
        hou.ui = mock_ui

        with patch.dict(ht.logging.adapters.HoudiniLoggerAdapter._TO_WRAP, {}, clear=True):
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
    def test_process__ui_properties_with_severity_and_title(self, mock_node_prop, mock_dialog_prop, mock_status_prop, mock_available):
        mock_message = MagicMock(spec=str)
        mock_title = MagicMock(spec=str)

        kwargs = {
            "extra": {"severity": hou.severityType.Error, "title": mock_title}
        }

        mock_ui = MagicMock()
        hou.ui = mock_ui

        with patch.dict(ht.logging.adapters.HoudiniLoggerAdapter._TO_WRAP, {}, clear=True):
            log = ht.logging.adapters.HoudiniLoggerAdapter(None, None, None)

        result = log.process(mock_message, kwargs)

        self.assertEqual(result, (mock_message, kwargs))

        mock_ui.displayMessage.assert_called_with(mock_message, severity=hou.severityType.Error, title=mock_title)
        mock_ui.setStatusMessage.assert_called_with(mock_message, severity=hou.severityType.Error)

        del hou.ui

    @patch("ht.logging.adapters.hou.hipFile.basename")
    @patch("ht.logging.adapters.hou.isUIAvailable", return_value=True)
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "status_bar", new_callable=PropertyMock(return_value=False))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "dialog", new_callable=PropertyMock(return_value=False))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "node", new_callable=PropertyMock(return_value=None))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "__init__", lambda x, y, z, w: None)
    def test_process__ui_no_properties_notify(self, mock_node_prop, mock_dialog_prop, mock_status_prop, mock_available,
                                              mock_basename):
        mock_message = MagicMock(spec=str)

        kwargs = {
            "extra": {"notify_send": True}
        }

        mock_ui = MagicMock()
        hou.ui = mock_ui

        with patch.dict(ht.logging.adapters.HoudiniLoggerAdapter._TO_WRAP, {}, clear=True):
            log = ht.logging.adapters.HoudiniLoggerAdapter(None, None, None)

        result = log.process(mock_message, kwargs)

        self.assertEqual(result, (mock_message, kwargs))

        mock_ui.displayMessage.assert_not_called()
        mock_ui.setStatusMessage.assert_not_called()

        del hou.ui

    @patch("ht.logging.adapters.hou.hipFile.basename")
    @patch("ht.logging.adapters.hou.isUIAvailable", return_value=False)
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "status_bar", new_callable=PropertyMock(return_value=False))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "dialog", new_callable=PropertyMock(return_value=False))
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "node", new_callable=PropertyMock)
    @patch.object(ht.logging.adapters.HoudiniLoggerAdapter, "__init__", lambda x, y, z, w: None)
    def test_process__no_extra(self, mock_node_prop, mock_dialog_prop, mock_status_prop, mock_available, mock_basename):
        mock_message = MagicMock(spec=str)

        kwargs = {}

        with patch.dict(ht.logging.adapters.HoudiniLoggerAdapter._TO_WRAP, {}, clear=True):
            log = ht.logging.adapters.HoudiniLoggerAdapter(None, None, None)

        result = log.process(mock_message, kwargs)

        self.assertEqual(result, (mock_message, kwargs))

        mock_node_prop.assert_not_called()


class Test__wrap_logger(unittest.TestCase):
    """Test ht.logging.adapters._wrap_logger."""

    def test_in_kwargs(self):
        """Test with passing all optional kwarg args."""
        mock_func = MagicMock(spec=str)
        mock_func.__name__ = "test"

        r = ht.logging.adapters._wrap_logger(mock_func, hou.severityType.Error)

        extra = {}

        mock_arg = MagicMock()

        mock_node = MagicMock(spec=hou.Node)
        mock_dialog = MagicMock(spec=bool)
        mock_status_bar = MagicMock(spec=bool)
        mock_title = MagicMock(spec=str)

        r(mock_arg, extra=extra, dialog=mock_dialog, node=mock_node, status_bar=mock_status_bar, title=mock_title)

        expected = {
            "node": mock_node,
            "dialog": mock_dialog,
            "status_bar": mock_status_bar,
            "severity": hou.severityType.Error,
            "title": mock_title,

        }

        self.assertEqual(extra, expected)

        mock_func.assert_called_with(mock_arg, extra=expected)

    def test_no_kwargs(self):
        """Test with passing none of the optional kwarg args."""

        mock_func = MagicMock(spec=str)
        mock_func.__name__ = "test"

        r = ht.logging.adapters._wrap_logger(mock_func, hou.severityType.Error)

        extra = {}

        mock_arg = MagicMock()

        r(mock_arg, extra=extra)

        expected = {
            "severity": hou.severityType.Error
        }

        self.assertEqual(extra, expected)

        mock_func.assert_called_with(mock_arg, extra=expected)


# =============================================================================

if __name__ == '__main__':
    unittest.main()
