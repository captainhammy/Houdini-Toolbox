"""Tests for ht.events.callbacks module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import imp

# Third Party Imports
from mock import MagicMock, patch

# Houdini Toolbox Imports
from ht.events import SceneEvents, callbacks

# Reload the module to test to capture load evaluation since it has already
# been loaded.
imp.reload(callbacks)


# =============================================================================
# CLASSES
# =============================================================================

class Test__atexit_callback(object):
    """Test ht.events.callbacks._atexit_callback."""

    @patch("ht.events.callbacks.run_event")
    def test(self, mock_run):
        """Run the Exit event."""
        callbacks._atexit_callback()

        mock_run.assert_called_with(SceneEvents.Exit)


class Test__emit_ui_available(object):
    """Test ht.events.callbacks._emit_ui_available."""

    @patch("ht.events.callbacks.run_event")
    def test(self, mock_run):
        """Run the WhenUIAvailable event."""
        callbacks._emit_ui_available()

        mock_run.assert_called_with(SceneEvents.WhenUIAvailable)


class Test__hip_event_callback(object):
    """Test ht.events.callbacks._hip_event_callback."""

    @patch("ht.events.callbacks.run_event")
    def test(self, mock_run):
        mock_event_type = MagicMock()
        mock_event_type.name.return_value = "event_name"

        mock_name_value = MagicMock(spec=str)

        mock_event = MagicMock()
        mock_event.event_name = mock_name_value

        with patch("ht.events.callbacks.HipFileEvents", mock_event):
            callbacks._hip_event_callback(mock_event_type)

            mock_run.assert_called_with(mock_name_value, {"hip_file_event_type": mock_event_type})

    @patch("ht.events.callbacks.run_event")
    def test_no_event_name(self, mock_run):
        mock_event_type = MagicMock()
        mock_event_type.name.return_value = "event_name"

        mock_event = MagicMock()
        del mock_event.event_name

        with patch("ht.events.callbacks.HipFileEvents", mock_event):
            callbacks._hip_event_callback(mock_event_type)

            mock_run.assert_not_called()


class Test__register_when_ui_available(object):
    """Test ht.events.callbacks._register_when_ui_available."""

    def test(self):
        """Register the _emit_ui_available function with hdefereval."""
        mock_hdefereval = MagicMock()

        # Need to mock importing hdefereval because the import will fail when
        # the UI is not available (like in testing).
        modules = {"hdefereval": mock_hdefereval}

        with patch.dict("sys.modules", modules):
            callbacks._register_when_ui_available()

            # Ensure we passed the _emit_ui_available method to the exec function.
            mock_hdefereval.executeDeferredAfterWaiting.assert_called_once_with(callbacks._emit_ui_available, 1)


class Test_register_callbacks(object):
    """Test ht.events.callbacks.register_callbacks."""

    @patch("ht.events.callbacks.hou.hipFile.addEventCallback")
    @patch("ht.events.callbacks._register_when_ui_available")
    @patch("ht.events.callbacks.atexit.register")
    @patch("hou.isUIAvailable")
    def test_no_ui(self, mock_available, mock_register, mock_emit, mock_add):
        """Register callbacks when the UI is not available."""
        mock_available.return_value = False

        callbacks.register_callbacks()

        mock_register.assert_called_with(callbacks._atexit_callback)

        # _register_when_ui_available() will NOT be called when the UI is not available.
        mock_emit.assert_not_called()

        mock_add.assert_called_with(callbacks._hip_event_callback)

    @patch("ht.events.callbacks.hou.hipFile.addEventCallback")
    @patch("ht.events.callbacks._register_when_ui_available")
    @patch("ht.events.callbacks.atexit.register")
    @patch("hou.isUIAvailable")
    def test_ui_available(self, mock_available, mock_register, mock_emit, mock_add):
        """Register callbacks when the UI is available."""
        mock_available.return_value = True

        callbacks.register_callbacks()

        mock_register.assert_called_with(callbacks._atexit_callback)

        mock_emit.assert_called_once()

        mock_add.assert_called_with(callbacks._hip_event_callback)
