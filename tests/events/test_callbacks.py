"""Tests for ht.events.callbacks module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Third Party
import pytest

# Houdini Toolbox
from ht.events import SceneEvents, callbacks

# =============================================================================
# TESTS
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


@pytest.mark.parametrize("exists", (True, False))
def test__hip_event_callback(mocker, exists):
    """Test ht.events.callbacks._hip_event_callback."""
    mock_run = mocker.patch("ht.events.callbacks.run_event")

    mock_event_type = mocker.MagicMock()
    mock_event_type.name.return_value = "event_name"

    mock_name_value = mocker.MagicMock(spec=str)

    mock_event = mocker.MagicMock()

    if exists:
        mock_event.event_name = mock_name_value

    else:
        del mock_event.event_name

    mocker.patch("ht.events.callbacks.HipFileEvents", mock_event)
    callbacks._hip_event_callback(mock_event_type)

    if exists:
        mock_run.assert_called_with(
            mock_name_value, {"hip_file_event_type": mock_event_type}
        )

    else:
        mock_run.assert_not_called()


def test_register_when_ui_available(mock_hdefereval):
    """Register the _emit_ui_available function with hdefereval."""
    callbacks._register_when_ui_available()

    # Ensure we passed the _emit_ui_available method to the exec function.
    mock_hdefereval.executeDeferredAfterWaiting.assert_called_once_with(
        callbacks._emit_ui_available, 1
    )


@pytest.mark.parametrize("ui_available", (False, True))
def test_register_callbacks(mocker, ui_available):
    """Test ht.events.callbacks.register_callbacks."""
    mocker.patch("hou.isUIAvailable", return_value=ui_available)
    mock_register = mocker.patch("ht.events.callbacks.atexit.register")
    mock_emit = mocker.patch("ht.events.callbacks._register_when_ui_available")
    mock_add = mocker.patch("ht.events.callbacks.hou.hipFile.addEventCallback")

    callbacks.register_callbacks()

    mock_register.assert_called_with(callbacks._atexit_callback)

    if not ui_available:
        # _register_when_ui_available() will NOT be called when the UI is not available.
        mock_emit.assert_not_called()

    else:
        mock_emit.assert_called_once()

    mock_add.assert_called_with(callbacks._hip_event_callback)
