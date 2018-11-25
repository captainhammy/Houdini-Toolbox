"""Tests for ht.events.manager module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
from mock import MagicMock, PropertyMock, call, patch
import unittest

# Houdini Toolbox Imports
from ht.events.item import HoudiniEventItem
from ht.events.event import HoudiniEvent
from ht.events.group import HoudiniEventGroup
from ht.events import manager

reload(manager)

# =============================================================================
# CLASSES
# =============================================================================

class Test_HoudiniEventManager(unittest.TestCase):
    """Test ht.events.manager.HoudiniEventManager class."""

    def test___init__(self):
        mgr = manager.HoudiniEventManager()

        self.assertEqual(mgr._data, {})
        self.assertEqual(mgr._events, {})
        self.assertEqual(mgr._event_states, {})

    # Properties

    @patch.object(manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_data(self):
        mgr = manager.HoudiniEventManager()

        data = {"key": "value"}

        mgr._data = data
        self.assertEqual(mgr.data, data)

    @patch.object(manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_events(self):
        mgr = manager.HoudiniEventManager()

        mock_event = MagicMock(spec=HoudiniEvent)
        events = {"name": mock_event}

        mgr._events = events
        self.assertEqual(mgr.events, events)

    # Methods

    # _disable_events

    @patch.object(manager.HoudiniEventManager, "events", new_callable=PropertyMock)
    @patch.object(manager.HoudiniEventManager, "__init__", lambda x: None)
    def test__disable_events__all(self, mock_events):
        """Test disabling all events."""
        mock_event1 = MagicMock(spec=HoudiniEvent)
        mock_enabled1 = PropertyMock(return_value=False)

        type(mock_event1).name = PropertyMock(return_value="name1")
        type(mock_event1).enabled = mock_enabled1

        mock_event2 = MagicMock(spec=HoudiniEvent)
        mock_enabled2 = PropertyMock(return_value=True)

        type(mock_event2).name = PropertyMock(return_value="name2")
        type(mock_event2).enabled = mock_enabled2

        mock_events.return_value = {
            "name1": mock_event1,
            "name2": mock_event2,
        }

        mgr = manager.HoudiniEventManager()
        mgr._event_states = {}

        mgr._disable_events()

        # Each event should have it's enabled property accessed twice:
        # once to store the current value and then to set the value to False
        mock_enabled1.assert_has_calls([call(), call(False)])
        mock_enabled2.assert_has_calls([call(), call(False)])

        self.assertFalse(mgr._event_states["name1"])
        self.assertTrue(mgr._event_states["name2"])

    @patch.object(manager.HoudiniEventManager, "events", new_callable=PropertyMock)
    @patch.object(manager.HoudiniEventManager, "__init__", lambda x: None)
    def test__disable_events__specific_names(self, mock_events):
        """Test disabling specific events."""
        mock_event1 = MagicMock(spec=HoudiniEvent)
        mock_enabled1 = PropertyMock(return_value=True)
        type(mock_event1).name = PropertyMock(return_value="name1")
        type(mock_event1).enabled = mock_enabled1

        mock_event2 = MagicMock(spec=HoudiniEvent)
        mock_enabled2 = PropertyMock(return_value=True)
        type(mock_event2).name = PropertyMock(return_value="name2")
        type(mock_event2).enabled = mock_enabled2

        mock_events.return_value = {
            "name1": mock_event1,
            "name2": mock_event2,
        }

        mgr = manager.HoudiniEventManager()
        mgr._event_states = {}

        mgr._disable_events(names=["name2"])

        # Event 1's enabled property should not have been accessed.
        mock_enabled1.assert_not_called()

        # Event 2's should have been accessed to get the current value
        # and once to disable it.
        mock_enabled2.assert_has_calls([call(), call(False)])

        self.assertTrue(mgr._event_states["name2"])
        self.assertEqual(len(mgr._event_states), 1)

    # _restore_events

    @patch.object(manager.HoudiniEventManager, "events", new_callable=PropertyMock)
    @patch.object(manager.HoudiniEventManager, "__init__", lambda x: None)
    def test__restore_events(self, mock_events):
        """Test restoring disabled events."""
        mock_states = MagicMock(spec=dict)

        states = {"name1": False, "name2": True}
        mock_states.iteritems.return_value = states.iteritems()

        mock_event1 = MagicMock(spec=HoudiniEvent)
        mock_enabled1 = PropertyMock(return_value=False)
        type(mock_event1).enabled = mock_enabled1

        mock_event2 = MagicMock(spec=HoudiniEvent)
        mock_enabled2 = PropertyMock(return_value=False)
        type(mock_event2).enabled = mock_enabled2

        mock_events.return_value = {
            "name1": mock_event1,
            "name2": mock_event2,
        }

        mgr = manager.HoudiniEventManager()
        mgr._event_states = mock_states

        mgr._restore_events()

        # Event 1's enable should have been set to False, 2's True
        mock_enabled1.assert_has_calls([call(False)])
        mock_enabled2.assert_has_calls([call(True)])

        mock_states.clear.assert_called_once()

    # create_event

    @patch("ht.events.manager.HoudiniEventFactory")
    @patch.object(manager.HoudiniEventManager, "events", new_callable=PropertyMock)
    @patch.object(manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_create_event(self, mock_events, mock_factory):
        """Test creating an event."""
        mock_event = MagicMock(spec=HoudiniEvent)
        mock_factory.get_event_type.return_value = mock_event

        events = {}
        mock_events.return_value = events

        mgr = manager.HoudiniEventManager()

        result = mgr.create_event("test_event")

        self.assertEqual(result, mock_event)
        self.assertTrue(mock_event in events.values())
        mock_factory.get_event_type.assert_called_with("test_event")

    # event_disabler

    @patch.object(manager.HoudiniEventManager, "_restore_events")
    @patch.object(manager.HoudiniEventManager, "_disable_events")
    @patch.object(manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_event_disabler(self, mock_disable, mock_restore):
        """Test the event_disabler context manager."""
        mgr = manager.HoudiniEventManager()

        names = ("name1", "name2")

        with mgr.event_disabler(names=names):
            pass

        mock_disable.assert_called_with(names)
        mock_restore.assert_called_once()

    # register_event_group

    @patch.object(manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_register_event_group__invalid_type(self):
        """Test registering an event group with an invalid object type."""
        # Don't spec so it will fail isinstance(EventGroup)
        mock_group = MagicMock()

        mgr = manager.HoudiniEventManager()

        with self.assertRaises(TypeError):
            mgr.register_event_group(mock_group)

    @patch.object(manager.HoudiniEventManager, "create_event")
    @patch.object(manager.HoudiniEventManager, "events", new_callable=PropertyMock)
    @patch.object(manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_register_event_group__single_items(self, mock_events, mock_create):
        """Test registering a group where no event of that name has been created."""
        mock_item1 = MagicMock(spec=HoudiniEventItem)
        mock_item2 = MagicMock(spec=HoudiniEventItem)

        event_map = {
            "event_name1": mock_item1,
            "event_name2": mock_item2
        }

        mock_group = MagicMock(spec=HoudiniEventGroup)
        type(mock_group).event_map = PropertyMock(return_value=event_map)

        event_name1 = "event_name1"

        mock_event1 = MagicMock(spec=HoudiniEvent)
        mock_event2 = MagicMock(spec=HoudiniEvent)

        events = {"event_name2": mock_event2}

        mock_events.return_value = events

        mock_create.side_effect = lambda name: events.setdefault(name, mock_event1)

        mgr = manager.HoudiniEventManager()

        mgr.register_event_group(mock_group)

        mock_create.assert_called_with(event_name1)

        mock_event1.register_item.assert_called_with(mock_item1)
        mock_event2.register_item.assert_called_with(mock_item2)

    @patch.object(manager.HoudiniEventManager, "create_event")
    @patch.object(manager.HoudiniEventManager, "events", new_callable=PropertyMock)
    @patch.object(manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_register_event_group__item_lists(self, mock_events, mock_create):
        """Test registering a group where no event of that name has been created."""
        mock_item1 = MagicMock(spec=HoudiniEventItem)
        mock_item2 = MagicMock(spec=HoudiniEventItem)

        event_map = {
            "event_name1": [mock_item1],
            "event_name2": [mock_item2]
        }

        mock_group = MagicMock(spec=HoudiniEventGroup)
        type(mock_group).event_map = PropertyMock(return_value=event_map)

        event_name1 = "event_name1"

        mock_event1 = MagicMock(spec=HoudiniEvent)
        mock_event2 = MagicMock(spec=HoudiniEvent)

        events = {"event_name2": mock_event2}

        mock_events.return_value = events

        mock_create.side_effect = lambda name: events.setdefault(name, mock_event1)

        mgr = manager.HoudiniEventManager()

        mgr.register_event_group(mock_group)

        mock_create.assert_called_with(event_name1)

        mock_event1.register_item.assert_called_with(mock_item1)
        mock_event2.register_item.assert_called_with(mock_item2)

    # register_item

    @patch.object(manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_register_item__invalid_type(self):
        # Don't spec so it will fail isinstance(HoudiniEventItem)
        mgr = manager.HoudiniEventManager()

        with self.assertRaises(TypeError):
            mgr.register_item(None, "event_name")

    @patch.object(manager.HoudiniEventManager, "create_event")
    @patch.object(manager.HoudiniEventManager, "events", new_callable=PropertyMock)
    @patch.object(manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_register_item__new_event(self, mock_events, mock_create):
        event_name = "event_name"
        mock_event = MagicMock(spec=HoudiniEvent)

        events = {}

        mock_events.return_value = events

        mock_create.side_effect = lambda name: events.setdefault(name, mock_event)

        mock_item = MagicMock(spec=HoudiniEventItem)

        mgr = manager.HoudiniEventManager()

        mgr.register_item(mock_item, event_name)

        mock_create.assert_called_with(event_name)
        mock_event.register_item.assert_called_with(mock_item)

    @patch.object(manager.HoudiniEventManager, "create_event")
    @patch.object(manager.HoudiniEventManager, "events", new_callable=PropertyMock)
    @patch.object(manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_register_item__existing_event(self, mock_events, mock_create):
        event_name = "event_name"
        mock_event = MagicMock(spec=HoudiniEvent)

        mock_events.return_value = {event_name: mock_event}

        mock_item = MagicMock(spec=HoudiniEventItem)

        mgr = manager.HoudiniEventManager()

        mgr.register_item(mock_item, event_name)

        mock_create.assert_not_called()
        mock_event.register_item.assert_called_with(mock_item)

    # run_event

    @patch.object(manager.HoudiniEventManager, "events", new_callable=PropertyMock)
    @patch.object(manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_run_event__no_event(self, mock_events):
        """Test running an event where there are no matching events."""
        event_name = "TestRunEvent"

        mock_events.return_value = {}

        scriptargs = {}

        mgr = manager.HoudiniEventManager()

        mgr.run_event(event_name, scriptargs)

        self.assertEqual(scriptargs, {})

    @patch.object(manager.HoudiniEventManager, "events", new_callable=PropertyMock)
    @patch.object(manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_run_event__no_scriptargs(self, mock_events):
        """Test running an event with no particular args."""
        event_name = "TestRunEvent"

        mock_event = MagicMock(spec=HoudiniEvent)
        type(mock_event).name = PropertyMock(return_value=event_name)

        mock_events.return_value = {event_name: mock_event}

        mgr = manager.HoudiniEventManager()

        mgr.run_event(event_name)

        scriptargs = {
            "_manager_": mgr,
        }

        mock_event.run.assert_called_with(scriptargs)

    @patch.object(manager.HoudiniEventManager, "events", new_callable=PropertyMock)
    @patch.object(manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_run_event__scriptargs(self, mock_events):
        """Test running an event while passing in args."""
        event_name = "TestRunEvent"
        mock_event = MagicMock(spec=HoudiniEvent)
        type(mock_event).name = PropertyMock(return_value=event_name)

        mock_events.return_value = {event_name: mock_event}

        mgr = manager.HoudiniEventManager()

        scriptargs = {"key": "value"}

        mgr.run_event(event_name, scriptargs)

        expected_scriptargs = {
            "key": "value",
            "_manager_": mgr,
        }

        mock_event.run.assert_called_with(expected_scriptargs)

        self.assertEqual(scriptargs, expected_scriptargs)


class Test_register_event_group(unittest.TestCase):
    """Test ht.events.manager.register_event_group."""

    @patch("ht.events.manager.MANAGER")
    def test(self, mock_manager):
        mock_group = MagicMock(spec=HoudiniEventGroup)

        manager.register_event_group(mock_group)

        mock_manager.register_event_group.assert_called_with(mock_group)


class Test_register_function(unittest.TestCase):
    """Test ht.events.manager.register_function."""

    def test_not_callable(self):
        event_name = "TestEvent"
        item_name = "CoolItem"
        priority = 10
        tags = ["tag"]

        with self.assertRaises(TypeError):
            manager.register_function(None, event_name, item_name, priority, tags)

    @patch("ht.events.manager.register_item")
    @patch("ht.events.manager.HoudiniEventItem", autospec=True)
    def test(self, mock_cls, mock_register_item):
        mock_func = MagicMock()
        event_name = "TestEvent"
        item_name = "CoolItem"
        priority = 10
        tags = ["tag"]

        manager.register_function(mock_func, event_name, item_name, priority, tags)

        mock_cls.assert_called_with([mock_func], item_name, priority, stat_tags=tags)

        mock_register_item.assert_called_with(mock_cls.return_value, event_name)


class Test_register_item(unittest.TestCase):
    """Test ht.events.manager.register_item."""

    def test_not_item(self):
        event_name = "TestEvent"

        with self.assertRaises(TypeError):
            manager.register_item(None, event_name)

    @patch("ht.events.manager.MANAGER")
    def test(self, mock_manager):
        event_name = "TestEvent"

        mock_item = MagicMock(spec=HoudiniEventItem)

        manager.register_item(mock_item, event_name)

        mock_manager.register_item.assert_called_with(mock_item, event_name)


class Test_run_event(unittest.TestCase):
    """Test ht.events.manager.run_event."""

    @patch("ht.events.manager.MANAGER")
    def test(self, mock_manager):
        """Test running an event."""
        event_name = "TestEvent"
        scriptargs = {"test": "value"}

        manager.run_event(event_name, scriptargs)

        mock_manager.run_event.assert_called_with(event_name, scriptargs)

# =============================================================================

if __name__ == '__main__':
    unittest.main()

