"""Tests for ht.events.callbacks module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
from mock import MagicMock, patch
import unittest

# Houdini Toolbox Imports
from ht.events import SceneEvents, callbacks

reload(callbacks)

# =============================================================================
# CLASSES
# =============================================================================

class Test__atexit_callback(unittest.TestCase):
    """Test houdini_event.callbacks._atexit_callback."""

    @patch("ht.events.callbacks.run_event")
    def test(self, mock_run):
        callbacks._atexit_callback()

        mock_run.assert_called_with(SceneEvents.Exit)


class Test__emit_ui_available(unittest.TestCase):
    """Test houdini_event.callbacks._emit_ui_available."""

    @patch("ht.events.callbacks.run_event")
    def test(self, mock_run):
        callbacks._emit_ui_available()

        mock_run.assert_called_with(SceneEvents.WhenUIAvailable)


class Test__register_atexit(unittest.TestCase):
    """Test houdini_event.callbacks._register_atexit."""

    @patch("atexit.register")
    def test(self, mock_register):
        callbacks._register_atexit()

        # Ensure we passed the _atexit_callback method to the register function.
        mock_register.assert_called_with(callbacks._atexit_callback)


class Test__register_when_ui_available(unittest.TestCase):
    """Test houdini_event.callbacks._register_when_ui_available."""

    def test(self):
        mock_hdefereval = MagicMock()

        # Need to mock importing hdefereval because the import will fail when
        # the UI is not available (like in testing).
        modules = {"hdefereval": mock_hdefereval}

        with patch.dict("sys.modules", modules):
            callbacks._register_when_ui_available()

            # Ensure we passed the _emit_ui_available method to the exec function.
            mock_hdefereval.executeDeferredAfterWaiting.assert_called_once_with(callbacks._emit_ui_available, 1)


class Test_register_callbacks(unittest.TestCase):
    """Test houdini_event.callbacks.register_callbacks."""

    @patch("ht.events.callbacks._register_when_ui_available")
    @patch("ht.events.callbacks._register_atexit")
    @patch("hou.isUIAvailable")
    def test_no_ui(self, mock_available, mock_atexit, mock_emit):
        mock_available.return_value = False

        callbacks.register_callbacks()

        mock_atexit.assert_called_once()

        # _register_when_ui_available() will NOT be called when the UI is not available.
        mock_emit.assert_not_called()

    @patch("ht.events.callbacks._register_when_ui_available")
    @patch("ht.events.callbacks._register_atexit")
    @patch("hou.isUIAvailable")
    def test_ui_available(self, mock_available, mock_atexit, mock_emit):
        mock_available.return_value = True

        callbacks.register_callbacks()

        mock_atexit.assert_called_once()
        mock_emit.assert_called_once()

# =============================================================================

if __name__ == '__main__':
    unittest.main()
