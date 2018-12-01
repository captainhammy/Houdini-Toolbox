"""Tests for ht.events.group module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
from mock import MagicMock, patch
import unittest

# Houdini Toolbox Imports
import ht.events.group

reload(ht.events.group)

# =============================================================================
# CLASSES
# =============================================================================

class Test_HoudiniEventGroup(unittest.TestCase):
    """Test ht.events.group.HoudiniEventGroup class."""

    def test___init__(self):
        """Test the constructor."""
        group = ht.events.group.HoudiniEventGroup()

        self.assertEqual(group._data, {})
        self.assertEqual(group._event_map, {})

    # Properties

    @patch.object(ht.events.group.HoudiniEventGroup, "__init__", lambda x: None)
    def test_data(self):
        """Test the 'data' property."""
        mock_value = MagicMock(spec=dict)

        group = ht.events.group.HoudiniEventGroup()
        group._data = mock_value
        self.assertEqual(group.data, mock_value)

    @patch.object(ht.events.group.HoudiniEventGroup, "__init__", lambda x: None)
    def test_event_map(self):
        """Test 'event_map' property."""
        mock_value = MagicMock(spec=dict)

        group = ht.events.group.HoudiniEventGroup()
        group._event_map = mock_value

        self.assertEqual(group.event_map, mock_value)

# =============================================================================

if __name__ == '__main__':
    unittest.main()
