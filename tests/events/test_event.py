"""Tests for ht.events.event module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
from mock import MagicMock, PropertyMock, patch
import unittest

# Houdini Toolbox Imports
import ht.events.item
import ht.events.event
import ht.events.stats

reload(ht.events.event)

# =============================================================================
# CLASSES
# =============================================================================

class Test_HoudiniEventFactory(unittest.TestCase):
    """Test ht.events.event.HoudiniEventFactory class."""

    @patch.object(ht.events.event.HoudiniEventFactory, "_mappings", new_callable=PropertyMock)
    def test_get_event_type__mapped(self, mock_mappings):
        """Test where an event mapping of the specified name exists."""
        mock_name = MagicMock(spec=str)

        mock_return = MagicMock(spec=ht.events.event.HoudiniEvent)

        mock_mappings.return_value = {mock_name: mock_return}

        result = ht.events.event.HoudiniEventFactory.get_event_type(mock_name)

        self.assertEqual(result, mock_return.return_value)
        mock_return.assert_called_once()

    @patch("ht.events.event.HoudiniEvent", autospec=True)
    @patch.object(ht.events.event.HoudiniEventFactory, "_mappings", new_callable=PropertyMock)
    def test_get_event_type__unmapped(self, mock_mappings, mock_event):
        """Test where no mapping exists, returns the default event."""
        mock_name = MagicMock(spec=str)

        mock_event_name = MagicMock(spec=str)

        mock_cls = MagicMock()

        mock_mappings.return_value = {mock_name: mock_cls}

        result = ht.events.event.HoudiniEventFactory.get_event_type(mock_event_name)

        self.assertEqual(result, mock_event.return_value)

        mock_event.assert_called_with(mock_event_name)

        mock_cls.assert_not_called()

    @patch.object(ht.events.event.HoudiniEventFactory, "_mappings", new_callable=PropertyMock)
    def test_register_event_class(self, _mappings):
        """Test registering an event class by name."""
        mock_event_name = MagicMock(spec=str)

        mappings = {}
        _mappings.return_value = mappings

        mock_event = MagicMock(spec=ht.events.event.HoudiniEvent)

        ht.events.event.HoudiniEventFactory.register_event_class(mock_event_name, mock_event)

        self.assertEqual(mappings, {mock_event_name: mock_event})


class Test_HoudiniEvent(unittest.TestCase):
    """Test ht.events.event.HoudiniEvent class."""

    @patch("ht.events.event.HoudiniEventStats", spec=ht.events.stats.HoudiniEventStats)
    def test___init__(self, mock_stats):
        """Test the constructor."""
        mock_name = MagicMock(spec=str)

        event = ht.events.event.HoudiniEvent(mock_name)

        self.assertEqual(event._data, {})
        self.assertTrue(event._enabled)
        self.assertEqual(event._item_map, {})
        self.assertEqual(event._name, mock_name)

        self.assertTrue(isinstance(event._stats, ht.events.stats.HoudiniEventStats))
        mock_stats.assert_called_with(mock_name)

    # Properties

    @patch.object(ht.events.event.HoudiniEvent, "__init__", lambda x, y: None)
    def test_data(self):
        """Test 'data' property."""
        mock_value = MagicMock(spec=dict)
        event = ht.events.event.HoudiniEvent(None)
        event._data = mock_value

        self.assertEqual(event.data, mock_value)

    @patch.object(ht.events.event.HoudiniEvent, "__init__", lambda x, y: None)
    def test_enabled(self):
        """Test 'enabled' property."""
        mock_value1 = MagicMock(spec=bool)
        event = ht.events.event.HoudiniEvent(None)

        event._enabled = mock_value1
        self.assertEqual(event.enabled, mock_value1)

        mock_value2 = MagicMock(spec=bool)
        event.enabled = mock_value2
        self.assertEqual(event.enabled, mock_value2)

    @patch.object(ht.events.event.HoudiniEvent, "__init__", lambda x, y: None)
    def test_item_map(self):
        """Test 'item_map' property."""
        mock_value = MagicMock(spec=dict)

        event = ht.events.event.HoudiniEvent(None)

        event._item_map = mock_value
        self.assertEqual(event.item_map, mock_value)

    @patch.object(ht.events.event.HoudiniEvent, "__init__", lambda x, y: None)
    def test_name(self):
        """Test 'name' property."""
        mock_value = MagicMock(spec=str)
        event = ht.events.event.HoudiniEvent(None)

        event._name = mock_value
        self.assertEqual(event.name, mock_value)

    @patch.object(ht.events.event.HoudiniEvent, "__init__", lambda x, y: None)
    def test_stats(self):
        """Test 'stats' property."""
        event = ht.events.event.HoudiniEvent(None)

        mock_stats = MagicMock(spec=ht.events.stats.HoudiniEventStats)
        event._stats = mock_stats

        self.assertEqual(event.stats, mock_stats)

    # Functions

    # register_item

    @patch.object(ht.events.event.HoudiniEvent, "__init__", lambda x, y: None)
    def test_register_item__non_item(self):
        """Test registering an object which is not a HoudiniEventItem."""
        event = ht.events.event.HoudiniEvent(None)

        with self.assertRaises(TypeError):
            event.register_item(None)

    @patch.object(ht.events.event.HoudiniEvent, "item_map", new_callable=PropertyMock)
    @patch.object(ht.events.event.HoudiniEvent, "__init__", lambda x, y: None)
    def test_register_item(self, mock_item_map):
        """Test registering a HoudiniEventItem."""
        mock_map = {}
        mock_item_map.return_value = mock_map

        mock_item = MagicMock(spec=ht.events.item.HoudiniEventItem)

        event = ht.events.event.HoudiniEvent(None)
        event.register_item(mock_item)

        self.assertEqual(mock_map, {mock_item.priority: [mock_item]})

    # run

    @patch.object(ht.events.event.HoudiniEvent, "enabled", new_callable=PropertyMock)
    @patch.object(ht.events.event.HoudiniEvent, "__init__", lambda x, y: None)
    def test_run__not_enabled(self, mock_enabled):
        """Test running an event that is disabled."""
        mock_enabled.return_value = False

        event = ht.events.event.HoudiniEvent(None)

        scriptargs = {"key": "value"}
        event.run(scriptargs)

        # If the event is disabled nothing should happen and scriptargs should
        # be unchanged.
        expected_scriptargs = {"key": "value"}
        self.assertEqual(scriptargs, expected_scriptargs)

    @patch.object(ht.events.event.HoudiniEvent, "item_map", new_callable=PropertyMock)
    @patch.object(ht.events.event.HoudiniEvent, "stats", new_callable=PropertyMock)
    @patch.object(ht.events.event.HoudiniEvent, "enabled", new_callable=PropertyMock)
    @patch.object(ht.events.event.HoudiniEvent, "__init__", lambda x, y: None)
    def test_run(self, mock_enabled, mock_stats,  mock_item_map):
        """Test running all items in an event."""
        mock_enabled.return_value = True

        mock_stats.return_value = MagicMock(spec=ht.events.stats.HoudiniEventStats)

        mock_map = {}
        mock_item_map.return_value = mock_map

        event = ht.events.event.HoudiniEvent(None)

        mock_item1 = MagicMock(spec=ht.events.item.HoudiniEventItem)
        mock_item1.run.side_effect = lambda sa: sa["order"].append(mock_item1)

        mock_item2 = MagicMock(spec=ht.events.item.HoudiniEventItem)
        mock_item2.run.side_effect = lambda sa: sa["order"].append(mock_item2)

        mock_item3 = MagicMock(spec=ht.events.item.HoudiniEventItem)
        mock_item3.run.side_effect = lambda sa: sa["order"].append(mock_item3)

        # Assign objects to event map with priorities.
        mock_map[0] = [mock_item2]
        mock_map[15] = [mock_item3]
        mock_map[5] = [mock_item1]

        scriptargs = {"key": "value", "order": []}

        expected_scriptargs = {
            "key": "value",
            # We expect events to be run in decreasing priority order
            "order": [mock_item3, mock_item1, mock_item2]
        }

        # Run the test event.
        event.run(scriptargs)

        # Make sure each thing was ran.
        mock_item1.run.assert_called_once()
        mock_item2.run.assert_called_once()
        mock_item3.run.assert_called_once()

        self.assertEqual(scriptargs, expected_scriptargs)

        # Ensure the context manager was called.
        mock_stats.return_value.__enter__.assert_called_once()
        mock_stats.return_value.__exit__.assert_called_once()

# =============================================================================

if __name__ == '__main__':
    unittest.main()
