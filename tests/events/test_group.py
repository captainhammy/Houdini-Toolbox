"""Tests for ht.events.group module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import imp

# Third Party Imports
from mock import MagicMock, patch

# Houdini Toolbox Imports
import ht.events.group

# Reload the module to test to capture load evaluation since it has already
# been loaded.
imp.reload(ht.events.group)


# =============================================================================
# CLASSES
# =============================================================================

class Test_HoudiniEventGroup(object):
    """Test ht.events.group.HoudiniEventGroup class."""

    def test___init__(self):
        """Test the constructor."""
        group = ht.events.group.HoudiniEventGroup()

        assert group._data == {}
        assert group._event_map == {}

    # Properties

    @patch.object(ht.events.group.HoudiniEventGroup, "__init__", lambda x: None)
    def test_data(self):
        """Test the 'data' property."""
        mock_value = MagicMock(spec=dict)

        group = ht.events.group.HoudiniEventGroup()
        group._data = mock_value
        assert group.data == mock_value

    @patch.object(ht.events.group.HoudiniEventGroup, "__init__", lambda x: None)
    def test_event_map(self):
        """Test 'event_map' property."""
        mock_value = MagicMock(spec=dict)

        group = ht.events.group.HoudiniEventGroup()
        group._event_map = mock_value

        assert group.event_map == mock_value
