"""Tests for ht.events.group module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
from mock import patch
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
        group = ht.events.group.HoudiniEventGroup()

        self.assertEqual(group._data, {})
        self.assertEqual(group._event_map, {})

    # Properties

    @patch.object(ht.events.group.HoudiniEventGroup, "__init__", lambda x: None)
    def test_data(self):
        group = ht.events.group.HoudiniEventGroup()
        group._data = {"key": "value"}
        self.assertEqual(group.data, {"key": "value"})

    @patch.object(ht.events.group.HoudiniEventGroup, "__init__", lambda x: None)
    def test_event_map(self):
        """Test 'event_map' access property."""
        group = ht.events.group.HoudiniEventGroup()
        group._event_map = {"key": "value"}

        self.assertEqual(group.event_map, {"key": "value"})

# =============================================================================

if __name__ == '__main__':
    unittest.main()
