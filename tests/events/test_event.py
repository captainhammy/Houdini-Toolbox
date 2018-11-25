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
    def test_register_event_class(self, _mappings):
        mappings = {}
        _mappings.return_value = mappings

        mock_event = MagicMock(spec=ht.events.event.HoudiniEvent)

        ht.events.event.HoudiniEventFactory.register_event_class("test", mock_event)

        self.assertEqual(mappings, {"test": mock_event})

    @patch.object(ht.events.event.HoudiniEventFactory, "_mappings", new_callable=PropertyMock)
    def test_event_get_type_mapped(self, mock_mappings):
        mock_return = MagicMock(spec=ht.events.event.HoudiniEvent)

        mappings = {"name": mock_return}
        mock_mappings.return_value = mappings

        result = ht.events.event.HoudiniEventFactory.get_event_type("name")

        self.assertEqual(result, mock_return.return_value)
        mock_return.assert_called_once()

    @patch("ht.events.event.HoudiniEvent", autospec=True)
    @patch.object(ht.events.event.HoudiniEventFactory, "_mappings", new_callable=PropertyMock)
    def test_event_get_type_unmapped(self, mock_mappings, mock_event):
        mock_cls = MagicMock()

        mappings = {"name": mock_cls}
        mock_mappings.return_value = mappings

        result = ht.events.event.HoudiniEventFactory.get_event_type("missing")

        self.assertEqual(result, mock_event.return_value)

        mock_event.assert_called_with("missing")

        mock_cls.assert_not_called()


class Test_HoudiniEvent(unittest.TestCase):
    """Test ht.events.event.HoudiniEvent class."""

    @patch("ht.events.event.HoudiniEventStats", spec=ht.events.stats.HoudiniEventStats)
    def test_init(self, mock_stats):
        name = "event_name"

        event = ht.events.event.HoudiniEvent(name)

        self.assertEqual(event._data, {})
        self.assertTrue(event._enabled)
        self.assertEqual(event._item_map, {})
        self.assertEqual(event._name, name)

        self.assertTrue(isinstance(event._stats, ht.events.stats.HoudiniEventStats))
        mock_stats.assert_called_with(name)

    # Properties

    @patch.object(ht.events.event.HoudiniEvent, "__init__", lambda x, y: None)
    def test_data(self):
        """Test 'data' access property."""
        event = ht.events.event.HoudiniEvent(None)
        event._data = {"foo": "bar"}

        self.assertEqual(event.data, {"foo": "bar"})

    @patch.object(ht.events.event.HoudiniEvent, "__init__", lambda x, y: None)
    def test_enabled(self):
        """Test 'enabled' access property."""
        event = ht.events.event.HoudiniEvent(None)

        event._enabled = False
        self.assertFalse(event.enabled)

        event.enabled = False
        self.assertFalse(event._enabled)

    @patch.object(ht.events.event.HoudiniEvent, "__init__", lambda x, y: None)
    def test_item_map(self):
        """Test 'item_map' access property."""
        event = ht.events.event.HoudiniEvent(None)

        event._item_map = {"foo": "bar"}
        self.assertEqual(event.item_map, {"foo": "bar"})

    @patch.object(ht.events.event.HoudiniEvent, "__init__", lambda x, y: None)
    def test_name(self):
        """Test 'name' access property."""
        event = ht.events.event.HoudiniEvent(None)

        event._name = "foo"
        self.assertEqual(event.name, "foo")

    @patch.object(ht.events.event.HoudiniEvent, "__init__", lambda x, y: None)
    def test_stats(self):
        """Test 'stats' access property."""
        event = ht.events.event.HoudiniEvent(None)

        mock_stats = MagicMock(spec=ht.events.stats.HoudiniEventStats)
        event._stats = mock_stats

        self.assertEqual(event.stats, mock_stats)

    # Functions

    # register_item

    @patch.object(ht.events.event.HoudiniEvent, "__init__", lambda x, y: None)
    def test_register_item__non_item(self):
        """Test registering an object which is not an HoudiniEventItem."""
        event = ht.events.event.HoudiniEvent(None)

        with self.assertRaises(TypeError):
            event.register_item(None)

    @patch.object(ht.events.event.HoudiniEvent, "item_map", new_callable=PropertyMock)
    @patch.object(ht.events.event.HoudiniEvent, "__init__", lambda x, y: None)
    def test_register_item(self, mock_item_map):
        """Test registering a function."""
        mock_map = {}
        mock_item_map.return_value = mock_map

        priority = 3

        mock_item = MagicMock(spec=ht.events.item.HoudiniEventItem)
        type(mock_item).priority = PropertyMock(return_value=priority)

        event = ht.events.event.HoudiniEvent(None)
        event.register_item(mock_item)

        self.assertEqual(mock_map.get(priority), [mock_item])

    # run

    @patch.object(ht.events.event.HoudiniEvent, "enabled", new_callable=PropertyMock)
    @patch.object(ht.events.event.HoudiniEvent, "__init__", lambda x, y: None)
    def test_run__not_enabled(self, mock_enabled):
        """Test running an event that is disabled."""
        mock_enabled.return_value = False

        event = ht.events.event.HoudiniEvent(None)

        scriptargs = {"foo": "bar"}
        event.run(scriptargs)

        # If the event is disabled nothing should happen and scriptargs should
        # be unchanged.
        expected_scriptargs = {"foo": "bar"}
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

        scriptargs = {"foo": "bar", "order": []}

        expected_scriptargs = {
            "foo": "bar",
            "_event_": event,
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
