"""Tests for ht.events.callbacks module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import imp

# Houdini Toolbox Imports
from ht.events import SceneEvents, callbacks

# Reload the module to test to capture load evaluation since it has already
# been loaded.
imp.reload(callbacks)


# =============================================================================
# CLASSES
# =============================================================================


def test_atexit_callback(mocker):
    """Test ht.events.callbacks._atexit_callback."""
    mock_run = mocker.patch("ht.events.callbacks.run_event")

    callbacks._atexit_callback()

    mock_run.assert_called_with(SceneEvents.Exit)


def test_emit_ui_available(mocker):
    """Test ht.events.callbacks._emit_ui_available."""
    mock_run = mocker.patch("ht.events.callbacks.run_event")

    callbacks._emit_ui_available()

    mock_run.assert_called_with(SceneEvents.WhenUIAvailable)


class Test__hip_event_callback(object):
    """Test ht.events.callbacks._hip_event_callback."""

    def test(self, mocker):
        mock_run = mocker.patch("ht.events.callbacks.run_event")

        mock_event_type = mocker.MagicMock()
        mock_event_type.name.return_value = "event_name"

        mock_name_value = mocker.MagicMock(spec=str)

        mock_event = mocker.MagicMock()
        mock_event.event_name = mock_name_value

        mocker.patch("ht.events.callbacks.HipFileEvents", mock_event)
        callbacks._hip_event_callback(mock_event_type)

        mock_run.assert_called_with(
            mock_name_value, {"hip_file_event_type": mock_event_type}
        )

    def test_no_event_name(self, mocker):
        mock_run = mocker.patch("ht.events.callbacks.run_event")

        mock_event_type = mocker.MagicMock()
        mock_event_type.name.return_value = "event_name"

        mock_event = mocker.MagicMock()
        del mock_event.event_name

        mocker.patch("ht.events.callbacks.HipFileEvents", mock_event)
        callbacks._hip_event_callback(mock_event_type)

        mock_run.assert_not_called()


def test_register_when_ui_available(mocker):
    """Register the _emit_ui_available function with hdefereval."""
    mock_hdefereval = mocker.MagicMock()

    # Need to mock importing hdefereval because the import will fail when
    # the UI is not available (like in testing).
    modules = {"hdefereval": mock_hdefereval}

    mocker.patch.dict("sys.modules", modules)
    callbacks._register_when_ui_available()

    # Ensure we passed the _emit_ui_available method to the exec function.
    mock_hdefereval.executeDeferredAfterWaiting.assert_called_once_with(
        callbacks._emit_ui_available, 1
    )


class Test_register_callbacks(object):
    """Test ht.events.callbacks.register_callbacks."""

    def test_no_ui(self, mocker):
        """Register callbacks when the UI is not available."""
        mocker.patch("hou.isUIAvailable", return_value=False)
        mock_register = mocker.patch("ht.events.callbacks.atexit.register")
        mock_emit = mocker.patch("ht.events.callbacks._register_when_ui_available")
        mock_add = mocker.patch("ht.events.callbacks.hou.hipFile.addEventCallback")

        callbacks.register_callbacks()

        mock_register.assert_called_with(callbacks._atexit_callback)

        # _register_when_ui_available() will NOT be called when the UI is not available.
        mock_emit.assert_not_called()

        mock_add.assert_called_with(callbacks._hip_event_callback)

    def test_ui_available(self, mocker):
        """Register callbacks when the UI is available."""
        mocker.patch("hou.isUIAvailable", return_value=True)
        mock_register = mocker.patch("ht.events.callbacks.atexit.register")
        mock_emit = mocker.patch("ht.events.callbacks._register_when_ui_available")
        mock_add = mocker.patch("ht.events.callbacks.hou.hipFile.addEventCallback")

        callbacks.register_callbacks()

        mock_register.assert_called_with(callbacks._atexit_callback)

        mock_emit.assert_called_once()

        mock_add.assert_called_with(callbacks._hip_event_callback)
