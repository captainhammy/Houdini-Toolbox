"""Tests for ht.events.event.rop_render module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
import ht.events.events.scene_load


# =============================================================================
# TESTS
# =============================================================================


def test_clear_session_settings(mocker):
    """Test clearing session settings."""
    mock_hscript = mocker.patch("hou.hscript")

    ht.events.events.scene_load.clear_session_settings({})

    mock_hscript.assert_called_with("set -u HOUDINI_ICON_CACHE_DIR")
