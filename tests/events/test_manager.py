"""Tests for ht.events.manager module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import imp

# Third Party Imports
import pytest

# Houdini Toolbox Imports
from ht.events.item import HoudiniEventItem
from ht.events.event import HoudiniEvent
from ht.events.group import HoudiniEventGroup
import ht.events.manager

# Reload the module to test to capture load evaluation since it has already
# been loaded.
imp.reload(ht.events.manager)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def init_manager(mocker):
    """Fixture to initialize a manager."""
    mocker.patch.object(ht.events.manager.HoudiniEventManager, "__init__", lambda x: None)

    def _create():
        return ht.events.manager.HoudiniEventManager()

    return _create


# =============================================================================
# CLASSES
# =============================================================================

class Test_HoudiniEventManager(object):
    """Test ht.events.manager.HoudiniEventManager class."""

    def test___init__(self):
        """Test object initialization."""
        manager = ht.events.manager.HoudiniEventManager()

        assert manager._data == {}
        assert manager._events == {}
        assert manager._event_states == {}

    # Properties

    def test_data(self, init_manager, mocker):
        """Test the 'data' property"""
        mock_value = mocker.MagicMock(spec=dict)

        manager = init_manager()
        manager._data = mock_value
        assert manager.data == mock_value

    def test_events(self, init_manager, mocker):
        """Test the 'events' property"""
        mock_event = mocker.MagicMock(spec=HoudiniEvent)
        events = {mocker.MagicMock(spec=str): mock_event}

        manager = init_manager()
        manager._events = events
        assert manager.events == events

    # Methods

    # _disable_events

    def test__disable_events__all(self, init_manager, mocker):
        """Test disabling all events."""
        mock_events = mocker.patch.object(ht.events.manager.HoudiniEventManager, "events", new_callable=mocker.PropertyMock)

        mock_event1 = mocker.MagicMock(spec=HoudiniEvent)

        mock_enabled1 = mocker.PropertyMock(return_value=False)
        type(mock_event1).enabled = mock_enabled1

        mock_event2 = mocker.MagicMock(spec=HoudiniEvent)

        mock_enabled2 = mocker.PropertyMock(return_value=True)
        type(mock_event2).enabled = mock_enabled2

        mock_events.return_value = {
            mock_event1.name: mock_event1,
            mock_event2.name: mock_event2,
        }

        manager = init_manager()
        manager._event_states = {}

        manager._disable_events()

        # Each event should have it's enabled property accessed twice:
        # once to store the current value and then to set the value to False
        mock_enabled1.assert_has_calls([mocker.call(), mocker.call(False)])
        mock_enabled2.assert_has_calls([mocker.call(), mocker.call(False)])

        assert not manager._event_states[mock_event1.name]
        assert manager._event_states[mock_event2.name]

    def test__disable_events__specific_names(self, init_manager, mocker):
        """Test disabling specific events."""
        mock_events = mocker.patch.object(ht.events.manager.HoudiniEventManager, "events", new_callable=mocker.PropertyMock)

        mock_event1 = mocker.MagicMock(spec=HoudiniEvent)

        mock_enabled1 = mocker.PropertyMock(return_value=True)
        type(mock_event1).enabled = mock_enabled1

        mock_event2 = mocker.MagicMock(spec=HoudiniEvent)

        mock_enabled2 = mocker.PropertyMock(return_value=True)
        type(mock_event2).enabled = mock_enabled2

        mock_events.return_value = {
            mock_event1.name: mock_event1,
            mock_event2.name: mock_event2,
        }

        manager = init_manager()
        manager._event_states = {}

        manager._disable_events(names=[mock_event2.name])

        # Event 1's enabled property should not have been accessed.
        mock_enabled1.assert_not_called()

        # Event 2's should have been accessed to get the current value
        # and once to disable it.
        mock_enabled2.assert_has_calls([mocker.call(), mocker.call(False)])

        assert manager._event_states[mock_event2.name]
        assert len(manager._event_states) == 1

    def test__restore_events(self, init_manager, mocker):
        """Test restoring disabled events."""
        mock_events = mocker.patch.object(ht.events.manager.HoudiniEventManager, "events", new_callable=mocker.PropertyMock)

        mock_event1 = mocker.MagicMock(spec=HoudiniEvent)
        mock_enabled1 = mocker.PropertyMock(return_value=False)
        type(mock_event1).enabled = mock_enabled1

        mock_event2 = mocker.MagicMock(spec=HoudiniEvent)
        mock_enabled2 = mocker.PropertyMock(return_value=False)
        type(mock_event2).enabled = mock_enabled2

        mock_events.return_value = {
            mock_event1.name: mock_event1,
            mock_event2.name: mock_event2,
        }

        mock_states = mocker.MagicMock(spec=dict)

        states = {mock_event1.name: False, mock_event2.name: True}
        mock_states.items.return_value = states.items()

        manager = init_manager()
        manager._event_states = mock_states

        manager._restore_events()

        # Event 1's enable should have been set to False, 2's True
        mock_enabled1.assert_has_calls([mocker.call(False)])
        mock_enabled2.assert_has_calls([mocker.call(True)])

        mock_states.clear.assert_called_once()

    def test_create_event(self, init_manager, mocker):
        """Test creating an event."""
        mock_events = mocker.patch.object(ht.events.manager.HoudiniEventManager, "events", new_callable=mocker.PropertyMock)
        mock_factory = mocker.patch("ht.events.manager.HoudiniEventFactory")

        mock_event = mocker.MagicMock(spec=HoudiniEvent)
        mock_factory.get_event_type.return_value = mock_event

        events = {}
        mock_events.return_value = events

        manager = init_manager()

        mock_name = mocker.MagicMock(spec=str)

        result = manager.create_event(mock_name)

        assert result == mock_event
        assert mock_event in events.values()
        mock_factory.get_event_type.assert_called_with(mock_name)

    def test_event_disabler(self, init_manager, mocker):
        """Test the event_disabler context manager."""

        mock_disable = mocker.patch.object(ht.events.manager.HoudiniEventManager, "_disable_events")
        mock_restore = mocker.patch.object(ht.events.manager.HoudiniEventManager, "_restore_events")

        manager = init_manager()

        mock_names = mocker.MagicMock(spec=tuple)

        with manager.event_disabler(names=mock_names):
            pass

        mock_disable.assert_called_with(mock_names)
        mock_restore.assert_called_once()

    # register_event_group

    def test_register_event_group__invalid_type(self, init_manager, mocker):
        """Test registering an event group with an invalid object type."""
        # Don't spec so it will fail isinstance(EventGroup)
        mock_group = mocker.MagicMock()

        manager = init_manager()

        with pytest.raises(TypeError):
            manager.register_event_group(mock_group)

    def test_register_event_group__single_items(self, init_manager, mocker):
        """Test registering a group where no event of that name has been created."""
        mock_events = mocker.patch.object(ht.events.manager.HoudiniEventManager, "events", new_callable=mocker.PropertyMock)
        mock_create = mocker.patch.object(ht.events.manager.HoudiniEventManager, "create_event")

        mock_item1 = mocker.MagicMock(spec=HoudiniEventItem)
        mock_item2 = mocker.MagicMock(spec=HoudiniEventItem)

        mock_event_name1 = mocker.MagicMock(spec=str)
        mock_event_name2 = mocker.MagicMock(spec=str)

        event_map = {
            mock_event_name1: mock_item1,
            mock_event_name2: mock_item2
        }

        mock_group = mocker.MagicMock(spec=HoudiniEventGroup)
        type(mock_group).event_map = mocker.PropertyMock(return_value=event_map)

        mock_event1 = mocker.MagicMock(spec=HoudiniEvent)
        mock_event2 = mocker.MagicMock(spec=HoudiniEvent)

        events = {mock_event_name2: mock_event2}

        mock_events.return_value = events

        mock_create.side_effect = lambda name: events.setdefault(name, mock_event1)

        manager = init_manager()

        manager.register_event_group(mock_group)

        mock_create.assert_called_with(mock_event_name1)

        mock_event1.register_item.assert_called_with(mock_item1)
        mock_event2.register_item.assert_called_with(mock_item2)

    def test_register_event_group__item_lists(self, init_manager, mocker):
        """Test registering a group where no event of that name has been created."""
        mock_events = mocker.patch.object(ht.events.manager.HoudiniEventManager, "events", new_callable=mocker.PropertyMock)
        mock_create = mocker.patch.object(ht.events.manager.HoudiniEventManager, "create_event")

        mock_item1 = mocker.MagicMock(spec=HoudiniEventItem)
        mock_item2 = mocker.MagicMock(spec=HoudiniEventItem)

        mock_event_name1 = mocker.MagicMock(spec=str)
        mock_event_name2 = mocker.MagicMock(spec=str)

        event_map = {
            mock_event_name1: [mock_item1],
            mock_event_name2: [mock_item2]
        }

        mock_group = mocker.MagicMock(spec=HoudiniEventGroup)
        type(mock_group).event_map = mocker.PropertyMock(return_value=event_map)

        event_name1 = mock_event_name1

        mock_event1 = mocker.MagicMock(spec=HoudiniEvent)
        mock_event2 = mocker.MagicMock(spec=HoudiniEvent)

        events = {mock_event_name2: mock_event2}

        mock_events.return_value = events

        mock_create.side_effect = lambda name: events.setdefault(name, mock_event1)

        manager = init_manager()

        manager.register_event_group(mock_group)

        mock_create.assert_called_with(event_name1)

        mock_event1.register_item.assert_called_with(mock_item1)
        mock_event2.register_item.assert_called_with(mock_item2)

    # register_item

    def test_register_item__invalid_type(self, init_manager, mocker):
        # Don't spec so it will fail isinstance(HoudiniEventItem)
        manager = init_manager()

        with pytest.raises(TypeError):
            manager.register_item(None, mocker.MagicMock(spec=str))

    def test_register_item__new_event(self, init_manager, mocker):
        mock_events = mocker.patch.object(ht.events.manager.HoudiniEventManager, "events", new_callable=mocker.PropertyMock)
        mock_create = mocker.patch.object(ht.events.manager.HoudiniEventManager, "create_event")

        mock_event_name = mocker.MagicMock(spec=str)

        mock_event = mocker.MagicMock(spec=HoudiniEvent)

        events = {}

        mock_events.return_value = events

        mock_create.side_effect = lambda name: events.setdefault(name, mock_event)

        mock_item = mocker.MagicMock(spec=HoudiniEventItem)

        manager = init_manager()

        manager.register_item(mock_item, mock_event_name)

        mock_create.assert_called_with(mock_event_name)
        mock_event.register_item.assert_called_with(mock_item)

    def test_register_item__existing_event(self, init_manager, mocker):
        mock_events = mocker.patch.object(ht.events.manager.HoudiniEventManager, "events", new_callable=mocker.PropertyMock)
        mock_create = mocker.patch.object(ht.events.manager.HoudiniEventManager, "create_event")

        mock_event_name = mocker.MagicMock(spec=str)

        mock_event = mocker.MagicMock(spec=HoudiniEvent)

        mock_events.return_value = {mock_event_name: mock_event}

        mock_item = mocker.MagicMock(spec=HoudiniEventItem)

        manager = init_manager()

        manager.register_item(mock_item, mock_event_name)

        mock_create.assert_not_called()
        mock_event.register_item.assert_called_with(mock_item)

    # run_event

    def test_run_event__no_event(self, init_manager, mocker):
        """Test running an event where there are no matching events."""
        mock_events = mocker.patch.object(ht.events.manager.HoudiniEventManager, "events", new_callable=mocker.PropertyMock)

        mock_event_name = mocker.MagicMock(spec=str)

        mock_events.return_value = {}

        scriptargs = {}

        manager = init_manager()

        manager.run_event(mock_event_name, scriptargs)

        assert scriptargs == {}

    def test_run_event__no_scriptargs(self, init_manager, mocker):
        """Test running an event with no particular args."""
        mock_events = mocker.patch.object(ht.events.manager.HoudiniEventManager, "events", new_callable=mocker.PropertyMock)

        mock_event_name = mocker.MagicMock(spec=str)

        mock_event = mocker.MagicMock(spec=HoudiniEvent)

        mock_events.return_value = {mock_event_name: mock_event}

        manager = init_manager()

        manager.run_event(mock_event_name)

        scriptargs = {
            "_manager_": manager,
        }

        mock_event.run.assert_called_with(scriptargs)

    def test_run_event__scriptargs(self, init_manager, mocker):
        """Test running an event while passing in args."""
        mock_events = mocker.patch.object(ht.events.manager.HoudiniEventManager, "events", new_callable=mocker.PropertyMock)

        mock_event_name = mocker.MagicMock(spec=str)

        mock_event = mocker.MagicMock(spec=HoudiniEvent)

        mock_events.return_value = {mock_event_name: mock_event}

        manager = init_manager()

        scriptargs = {"key": "value"}

        manager.run_event(mock_event_name, scriptargs)

        expected_scriptargs = {
            "key": "value",
            "_manager_": manager,
        }

        mock_event.run.assert_called_with(expected_scriptargs)

        assert scriptargs == expected_scriptargs


def test_register_event_group(mocker):
    """Test ht.events.manager.register_event_group."""
    mock_manager = mocker.patch("ht.events.manager.MANAGER")

    mock_group = mocker.MagicMock(spec=HoudiniEventGroup)

    ht.events.manager.register_event_group(mock_group)

    mock_manager.register_event_group.assert_called_with(mock_group)


class Test_register_function(object):
    """Test ht.events.manager.register_function."""

    def test_not_callable(self, mocker):
        mock_event_name = mocker.MagicMock(spec=str)
        mock_item_name = mocker.MagicMock(spec=str)
        mock_priority = mocker.MagicMock(spec=int)
        mock_tags = mocker.MagicMock(spec=list)

        with pytest.raises(TypeError):
            ht.events.manager.register_function(None, mock_event_name, mock_item_name, mock_priority, mock_tags)

    def test(self, mocker):
        mock_cls = mocker.patch("ht.events.manager.HoudiniEventItem", autospec=True)
        mock_register_item = mocker.patch("ht.events.manager.register_item")

        mock_func = mocker.MagicMock()
        mock_event_name = mocker.MagicMock(spec=str)
        mock_item_name = mocker.MagicMock(spec=str)
        mock_priority = mocker.MagicMock(spec=int)
        mock_tags = mocker.MagicMock(spec=list)

        ht.events.manager.register_function(mock_func, mock_event_name, mock_item_name, mock_priority, mock_tags)

        mock_cls.assert_called_with((mock_func, ), mock_item_name, mock_priority, stat_tags=mock_tags)

        mock_register_item.assert_called_with(mock_cls.return_value, mock_event_name)


class Test_register_item(object):
    """Test ht.events.manager.register_item."""

    def test_not_item(self, mocker):
        mock_event_name = mocker.MagicMock(spec=str)

        with pytest.raises(TypeError):
            ht.events.manager.register_item(None, mock_event_name)

    def test(self, mocker):
        mock_manager = mocker.patch("ht.events.manager.MANAGER")

        mock_event_name = mocker.MagicMock(spec=str)

        mock_item = mocker.MagicMock(spec=HoudiniEventItem)

        ht.events.manager.register_item(mock_item, mock_event_name)

        mock_manager.register_item.assert_called_with(mock_item, mock_event_name)


def test_run_event(mocker):
    """Test ht.events.manager.run_event."""
    mock_manager = mocker.patch("ht.events.manager.MANAGER")

    mock_event_name = mocker.MagicMock(spec=str)
    mock_scriptargs = mocker.MagicMock(spec=dict)

    ht.events.manager.run_event(mock_event_name, mock_scriptargs)

    mock_manager.run_event.assert_called_with(mock_event_name, mock_scriptargs)
