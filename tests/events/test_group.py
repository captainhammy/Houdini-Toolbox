"""Tests for houdini_toolbox.events.group module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox
import houdini_toolbox.events.group

# =============================================================================
# TESTS
# =============================================================================


class Test_HoudiniEventGroup:
    """Test houdini_toolbox.events.group.HoudiniEventGroup class."""

    def test___init__(self):
        """Test object initialization."""
        group = houdini_toolbox.events.group.HoudiniEventGroup()

        assert group._data == {}
        assert group._event_map == {}

    # Properties

    def test_data(self, mocker):
        """Test the 'data' property."""
        mocker.patch.object(
            houdini_toolbox.events.group.HoudiniEventGroup, "__init__", lambda x: None
        )
        group = houdini_toolbox.events.group.HoudiniEventGroup()

        mock_value = mocker.MagicMock(spec=dict)
        group._data = mock_value
        assert group.data == mock_value

    def test_event_map(self, mocker):
        """Test 'event_map' property."""
        mocker.patch.object(
            houdini_toolbox.events.group.HoudiniEventGroup, "__init__", lambda x: None
        )
        group = houdini_toolbox.events.group.HoudiniEventGroup()

        mock_value = mocker.MagicMock(spec=dict)
        group._event_map = mock_value
        assert group.event_map == mock_value
