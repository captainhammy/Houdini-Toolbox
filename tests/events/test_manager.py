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
import ht.events.manager

reload(ht.events.manager)

# =============================================================================
# CLASSES
# =============================================================================

class Test_HoudiniEventManager(unittest.TestCase):
    """Test ht.events.manager.HoudiniEventManager class."""

    def test___init__(self):
        manager = ht.events.manager.HoudiniEventManager()

        self.assertEqual(manager._data, {})
        self.assertEqual(manager._events, {})
        self.assertEqual(manager._event_states, {})

    # Properties

    @patch.object(ht.events.manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_data(self):
        mock_value = MagicMock(spec=dict)

        manager = ht.events.manager.HoudiniEventManager()

        manager._data = mock_value
        self.assertEqual(manager.data, mock_value)

    @patch.object(ht.events.manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_events(self):
        manager = ht.events.manager.HoudiniEventManager()

        mock_event = MagicMock(spec=HoudiniEvent)
        events = {MagicMock(spec=str): mock_event}

        manager._events = events
        self.assertEqual(manager.events, events)

    # Methods

    # _disable_events

    @patch.object(ht.events.manager.HoudiniEventManager, "events", new_callable=PropertyMock)
    @patch.object(ht.events.manager.HoudiniEventManager, "__init__", lambda x: None)
    def test__disable_events__all(self, mock_events):
        """Test disabling all events."""
        mock_event1 = MagicMock(spec=HoudiniEvent)

        mock_enabled1 = PropertyMock(return_value=False)
        type(mock_event1).enabled = mock_enabled1

        mock_event2 = MagicMock(spec=HoudiniEvent)

        mock_enabled2 = PropertyMock(return_value=True)
        type(mock_event2).enabled = mock_enabled2

        mock_events.return_value = {
            mock_event1.name: mock_event1,
            mock_event2.name: mock_event2,
        }

        manager = ht.events.manager.HoudiniEventManager()
        manager._event_states = {}

        manager._disable_events()

        # Each event should have it's enabled property accessed twice:
        # once to store the current value and then to set the value to False
        mock_enabled1.assert_has_calls([call(), call(False)])
        mock_enabled2.assert_has_calls([call(), call(False)])

        self.assertFalse(manager._event_states[mock_event1.name])
        self.assertTrue(manager._event_states[mock_event2.name])

    @patch.object(ht.events.manager.HoudiniEventManager, "events", new_callable=PropertyMock)
    @patch.object(ht.events.manager.HoudiniEventManager, "__init__", lambda x: None)
    def test__disable_events__specific_names(self, mock_events):
        """Test disabling specific events."""
        mock_event1 = MagicMock(spec=HoudiniEvent)

        mock_enabled1 = PropertyMock(return_value=True)
        type(mock_event1).enabled = mock_enabled1

        mock_event2 = MagicMock(spec=HoudiniEvent)

        mock_enabled2 = PropertyMock(return_value=True)
        type(mock_event2).enabled = mock_enabled2

        mock_events.return_value = {
            mock_event1.name: mock_event1,
            mock_event2.name: mock_event2,
        }

        manager = ht.events.manager.HoudiniEventManager()
        manager._event_states = {}

        manager._disable_events(names=[mock_event2.name])

        # Event 1's enabled property should not have been accessed.
        mock_enabled1.assert_not_called()

        # Event 2's should have been accessed to get the current value
        # and once to disable it.
        mock_enabled2.assert_has_calls([call(), call(False)])

        self.assertTrue(manager._event_states[mock_event2.name])
        self.assertEqual(len(manager._event_states), 1)

    # _restore_events

    @patch.object(ht.events.manager.HoudiniEventManager, "events", new_callable=PropertyMock)
    @patch.object(ht.events.manager.HoudiniEventManager, "__init__", lambda x: None)
    def test__restore_events(self, mock_events):
        """Test restoring disabled events."""

        mock_event1 = MagicMock(spec=HoudiniEvent)
        mock_enabled1 = PropertyMock(return_value=False)
        type(mock_event1).enabled = mock_enabled1

        mock_event2 = MagicMock(spec=HoudiniEvent)
        mock_enabled2 = PropertyMock(return_value=False)
        type(mock_event2).enabled = mock_enabled2

        mock_events.return_value = {
            mock_event1.name: mock_event1,
            mock_event2.name: mock_event2,
        }

        mock_states = MagicMock(spec=dict)

        states = {mock_event1.name: False, mock_event2.name: True}
        mock_states.iteritems.return_value = states.iteritems()

        manager = ht.events.manager.HoudiniEventManager()
        manager._event_states = mock_states

        manager._restore_events()

        # Event 1's enable should have been set to False, 2's True
        mock_enabled1.assert_has_calls([call(False)])
        mock_enabled2.assert_has_calls([call(True)])

        mock_states.clear.assert_called_once()

    # create_event

    @patch("ht.events.manager.HoudiniEventFactory")
    @patch.object(ht.events.manager.HoudiniEventManager, "events", new_callable=PropertyMock)
    @patch.object(ht.events.manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_create_event(self, mock_events, mock_factory):
        """Test creating an event."""
        mock_event = MagicMock(spec=HoudiniEvent)
        mock_factory.get_event_type.return_value = mock_event

        events = {}
        mock_events.return_value = events

        manager = ht.events.manager.HoudiniEventManager()

        mock_name = MagicMock(spec=str)

        result = manager.create_event(mock_name)

        self.assertEqual(result, mock_event)
        self.assertTrue(mock_event in events.values())
        mock_factory.get_event_type.assert_called_with(mock_name)

    # event_disabler

    @patch.object(ht.events.manager.HoudiniEventManager, "_restore_events")
    @patch.object(ht.events.manager.HoudiniEventManager, "_disable_events")
    @patch.object(ht.events.manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_event_disabler(self, mock_disable, mock_restore):
        """Test the event_disabler context manager."""
        manager = ht.events.manager.HoudiniEventManager()

        mock_names = MagicMock(spec=tuple)

        with manager.event_disabler(names=mock_names):
            pass

        mock_disable.assert_called_with(mock_names)
        mock_restore.assert_called_once()

    # register_event_group

    @patch.object(ht.events.manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_register_event_group__invalid_type(self):
        """Test registering an event group with an invalid object type."""
        # Don't spec so it will fail isinstance(EventGroup)
        mock_group = MagicMock()

        manager = ht.events.manager.HoudiniEventManager()

        with self.assertRaises(TypeError):
            manager.register_event_group(mock_group)

    @patch.object(ht.events.manager.HoudiniEventManager, "create_event")
    @patch.object(ht.events.manager.HoudiniEventManager, "events", new_callable=PropertyMock)
    @patch.object(ht.events.manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_register_event_group__single_items(self, mock_events, mock_create):
        """Test registering a group where no event of that name has been created."""
        mock_item1 = MagicMock(spec=HoudiniEventItem)
        mock_item2 = MagicMock(spec=HoudiniEventItem)

        mock_event_name1 = MagicMock(spec=str)
        mock_event_name2 = MagicMock(spec=str)

        event_map = {
            mock_event_name1: mock_item1,
            mock_event_name2: mock_item2
        }

        mock_group = MagicMock(spec=HoudiniEventGroup)
        type(mock_group).event_map = PropertyMock(return_value=event_map)

        mock_event1 = MagicMock(spec=HoudiniEvent)
        mock_event2 = MagicMock(spec=HoudiniEvent)

        events = {mock_event_name2: mock_event2}

        mock_events.return_value = events

        mock_create.side_effect = lambda name: events.setdefault(name, mock_event1)

        manager = ht.events.manager.HoudiniEventManager()

        manager.register_event_group(mock_group)

        mock_create.assert_called_with(mock_event_name1)

        mock_event1.register_item.assert_called_with(mock_item1)
        mock_event2.register_item.assert_called_with(mock_item2)

    @patch.object(ht.events.manager.HoudiniEventManager, "create_event")
    @patch.object(ht.events.manager.HoudiniEventManager, "events", new_callable=PropertyMock)
    @patch.object(ht.events.manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_register_event_group__item_lists(self, mock_events, mock_create):
        """Test registering a group where no event of that name has been created."""
        mock_item1 = MagicMock(spec=HoudiniEventItem)
        mock_item2 = MagicMock(spec=HoudiniEventItem)

        mock_event_name1 = MagicMock(spec=str)
        mock_event_name2 = MagicMock(spec=str)

        event_map = {
            mock_event_name1: [mock_item1],
            mock_event_name2: [mock_item2]
        }

        mock_group = MagicMock(spec=HoudiniEventGroup)
        type(mock_group).event_map = PropertyMock(return_value=event_map)

        event_name1 = mock_event_name1

        mock_event1 = MagicMock(spec=HoudiniEvent)
        mock_event2 = MagicMock(spec=HoudiniEvent)

        events = {mock_event_name2: mock_event2}

        mock_events.return_value = events

        mock_create.side_effect = lambda name: events.setdefault(name, mock_event1)

        manager = ht.events.manager.HoudiniEventManager()

        manager.register_event_group(mock_group)

        mock_create.assert_called_with(event_name1)

        mock_event1.register_item.assert_called_with(mock_item1)
        mock_event2.register_item.assert_called_with(mock_item2)

    # register_item

    @patch.object(ht.events.manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_register_item__invalid_type(self):
        # Don't spec so it will fail isinstance(HoudiniEventItem)
        manager = ht.events.manager.HoudiniEventManager()

        with self.assertRaises(TypeError):
            manager.register_item(None, MagicMock(spec=str))

    @patch.object(ht.events.manager.HoudiniEventManager, "create_event")
    @patch.object(ht.events.manager.HoudiniEventManager, "events", new_callable=PropertyMock)
    @patch.object(ht.events.manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_register_item__new_event(self, mock_events, mock_create):
        mock_event_name = MagicMock(spec=str)

        mock_event = MagicMock(spec=HoudiniEvent)

        events = {}

        mock_events.return_value = events

        mock_create.side_effect = lambda name: events.setdefault(name, mock_event)

        mock_item = MagicMock(spec=HoudiniEventItem)

        manager = ht.events.manager.HoudiniEventManager()

        manager.register_item(mock_item, mock_event_name)

        mock_create.assert_called_with(mock_event_name)
        mock_event.register_item.assert_called_with(mock_item)

    @patch.object(ht.events.manager.HoudiniEventManager, "create_event")
    @patch.object(ht.events.manager.HoudiniEventManager, "events", new_callable=PropertyMock)
    @patch.object(ht.events.manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_register_item__existing_event(self, mock_events, mock_create):
        mock_event_name = MagicMock(spec=str)

        mock_event = MagicMock(spec=HoudiniEvent)

        mock_events.return_value = {mock_event_name: mock_event}

        mock_item = MagicMock(spec=HoudiniEventItem)

        manager = ht.events.manager.HoudiniEventManager()

        manager.register_item(mock_item, mock_event_name)

        mock_create.assert_not_called()
        mock_event.register_item.assert_called_with(mock_item)

    # run_event

    @patch.object(ht.events.manager.HoudiniEventManager, "events", new_callable=PropertyMock)
    @patch.object(ht.events.manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_run_event__no_event(self, mock_events):
        """Test running an event where there are no matching events."""
        mock_event_name = MagicMock(spec=str)

        mock_events.return_value = {}

        scriptargs = {}

        manager = ht.events.manager.HoudiniEventManager()

        manager.run_event(mock_event_name, scriptargs)

        self.assertEqual(scriptargs, {})

    @patch.object(ht.events.manager.HoudiniEventManager, "events", new_callable=PropertyMock)
    @patch.object(ht.events.manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_run_event__no_scriptargs(self, mock_events):
        """Test running an event with no particular args."""
        mock_event_name = MagicMock(spec=str)

        mock_event = MagicMock(spec=HoudiniEvent)

        mock_events.return_value = {mock_event_name: mock_event}

        manager = ht.events.manager.HoudiniEventManager()

        manager.run_event(mock_event_name)

        scriptargs = {
            "_manager_": manager,
        }

        mock_event.run.assert_called_with(scriptargs)

    @patch.object(ht.events.manager.HoudiniEventManager, "events", new_callable=PropertyMock)
    @patch.object(ht.events.manager.HoudiniEventManager, "__init__", lambda x: None)
    def test_run_event__scriptargs(self, mock_events):
        """Test running an event while passing in args."""
        mock_event_name = MagicMock(spec=str)

        mock_event = MagicMock(spec=HoudiniEvent)

        mock_events.return_value = {mock_event_name: mock_event}

        manager = ht.events.manager.HoudiniEventManager()

        scriptargs = {"key": "value"}

        manager.run_event(mock_event_name, scriptargs)

        expected_scriptargs = {
            "key": "value",
            "_manager_": manager,
        }

        mock_event.run.assert_called_with(expected_scriptargs)

        self.assertEqual(scriptargs, expected_scriptargs)


class Test_register_event_group(unittest.TestCase):
    """Test ht.events.manager.register_event_group."""

    @patch("ht.events.manager.MANAGER")
    def test(self, mock_manager):
        mock_group = MagicMock(spec=HoudiniEventGroup)

        ht.events.manager.register_event_group(mock_group)

        mock_manager.register_event_group.assert_called_with(mock_group)


class Test_register_function(unittest.TestCase):
    """Test ht.events.manager.register_function."""

    def test_not_callable(self):
        mock_event_name = MagicMock(spec=str)
        mock_item_name = MagicMock(spec=str)
        mock_priority = MagicMock(spec=int)
        mock_tags = MagicMock(spec=list)

        with self.assertRaises(TypeError):
            ht.events.manager.register_function(None, mock_event_name, mock_item_name, mock_priority, mock_tags)

    @patch("ht.events.manager.register_item")
    @patch("ht.events.manager.HoudiniEventItem", autospec=True)
    def test(self, mock_cls, mock_register_item):
        mock_func = MagicMock()
        mock_event_name = MagicMock(spec=str)
        mock_item_name = MagicMock(spec=str)
        mock_priority = MagicMock(spec=int)
        mock_tags = MagicMock(spec=list)

        ht.events.manager.register_function(mock_func, mock_event_name, mock_item_name, mock_priority, mock_tags)

        mock_cls.assert_called_with([mock_func], mock_item_name, mock_priority, stat_tags=mock_tags)

        mock_register_item.assert_called_with(mock_cls.return_value, mock_event_name)


class Test_register_item(unittest.TestCase):
    """Test ht.events.manager.register_item."""

    def test_not_item(self):
        mock_event_name = MagicMock(spec=str)

        with self.assertRaises(TypeError):
            ht.events.manager.register_item(None, mock_event_name)

    @patch("ht.events.manager.MANAGER")
    def test(self, mock_manager):
        mock_event_name = MagicMock(spec=str)

        mock_item = MagicMock(spec=HoudiniEventItem)

        ht.events.manager.register_item(mock_item, mock_event_name)

        mock_manager.register_item.assert_called_with(mock_item, mock_event_name)


class Test_run_event(unittest.TestCase):
    """Test ht.events.manager.run_event."""

    @patch("ht.events.manager.MANAGER")
    def test(self, mock_manager):
        """Test running an event."""
        mock_event_name = MagicMock(spec=str)
        mock_scriptargs = MagicMock(spec=dict)

        ht.events.manager.run_event(mock_event_name, mock_scriptargs)

        mock_manager.run_event.assert_called_with(mock_event_name, mock_scriptargs)

# =============================================================================

if __name__ == '__main__':
    unittest.main()
