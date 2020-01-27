"""Tests for ht.events.event module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import imp

# Third Party Imports
import pytest

# Houdini Toolbox Imports
import ht.events.item
import ht.events.event
import ht.events.stats

# Reload the module to test to capture load evaluation since it has already
# been loaded.
imp.reload(ht.events.event)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def init_event(mocker):
    """Fixture to initialize an event."""
    mocker.patch.object(ht.events.event.HoudiniEvent, "__init__", lambda x, y: None)

    def _create():
        return ht.events.event.HoudiniEvent(None)

    return _create


# =============================================================================
# CLASSES
# =============================================================================


class Test_HoudiniEventFactory(object):
    """Test ht.events.event.HoudiniEventFactory class."""

    def test_get_event_type__mapped(self, mocker):
        """Test where an event mapping of the specified name exists."""
        mock_mappings = mocker.patch.object(
            ht.events.event.HoudiniEventFactory,
            "_mappings",
            new_callable=mocker.PropertyMock,
        )

        mock_name = mocker.MagicMock(spec=str)

        mock_return = mocker.MagicMock(spec=ht.events.event.HoudiniEvent)

        mock_mappings.return_value = {mock_name: mock_return}

        result = ht.events.event.HoudiniEventFactory.get_event_type(mock_name)

        assert result == mock_return.return_value
        mock_return.assert_called_once()

    def test_get_event_type__unmapped(self, mocker):
        """Test where no mapping exists, returns the default event."""
        mock_mappings = mocker.patch.object(
            ht.events.event.HoudiniEventFactory,
            "_mappings",
            new_callable=mocker.PropertyMock,
        )
        mock_event = mocker.patch("ht.events.event.HoudiniEvent", autospec=True)

        mock_name = mocker.MagicMock(spec=str)
        mock_event_name = mocker.MagicMock(spec=str)

        mock_cls = mocker.MagicMock()

        mock_mappings.return_value = {mock_name: mock_cls}

        result = ht.events.event.HoudiniEventFactory.get_event_type(mock_event_name)

        assert result == mock_event.return_value

        mock_event.assert_called_with(mock_event_name)

        mock_cls.assert_not_called()

    def test_register_event_class(self, mocker):
        """Test registering an event class by name."""
        mock_mappings = mocker.patch.object(
            ht.events.event.HoudiniEventFactory,
            "_mappings",
            new_callable=mocker.PropertyMock,
        )

        mock_event_name = mocker.MagicMock(spec=str)

        mappings = {}
        mock_mappings.return_value = mappings

        mock_event = mocker.MagicMock(spec=ht.events.event.HoudiniEvent)

        ht.events.event.HoudiniEventFactory.register_event_class(
            mock_event_name, mock_event
        )

        assert mappings == {mock_event_name: mock_event}


class Test_HoudiniEvent(object):
    """Test ht.events.event.HoudiniEvent class."""

    def test___init__(self, mocker):
        """Test the constructor."""
        mock_stats = mocker.patch("ht.events.event.HoudiniEventStats", autospec=True)

        mock_name = mocker.MagicMock(spec=str)

        event = ht.events.event.HoudiniEvent(mock_name)

        assert event._data == {}
        assert event._enabled
        assert event._item_map == {}
        assert event._name == mock_name
        assert event._stats == mock_stats.return_value

        mock_stats.assert_called_with(mock_name)

    # Properties

    def test_data(self, init_event, mocker):
        """Test 'data' property."""
        mock_value = mocker.MagicMock(spec=dict)

        event = init_event()
        event._data = mock_value

        assert event.data == mock_value

    def test_enabled(self, init_event, mocker):
        """Test 'enabled' property."""
        mock_value1 = mocker.MagicMock(spec=bool)

        event = init_event()
        event._enabled = mock_value1
        assert event.enabled == mock_value1

        mock_value2 = mocker.MagicMock(spec=bool)
        event.enabled = mock_value2
        assert event.enabled == mock_value2

    def test_item_map(self, init_event, mocker):
        """Test 'item_map' property."""
        mock_value = mocker.MagicMock(spec=dict)

        event = init_event()
        event._item_map = mock_value
        assert event.item_map == mock_value

    def test_name(self, init_event, mocker):
        """Test 'name' property."""
        mock_value = mocker.MagicMock(spec=str)

        event = init_event()
        event._name = mock_value
        assert event.name == mock_value

    def test_stats(self, init_event, mocker):
        """Test 'stats' property."""
        mock_stats = mocker.MagicMock(spec=ht.events.stats.HoudiniEventStats)

        event = init_event()
        event._stats = mock_stats

        assert event.stats == mock_stats

    # Functions

    # register_item

    def test_register_item__non_item(self, init_event):
        """Test registering an object which is not a HoudiniEventItem."""
        event = init_event()

        with pytest.raises(TypeError):
            event.register_item(None)

    def test_register_item(self, init_event, mocker):
        """Test registering a HoudiniEventItem."""
        mock_item_map = mocker.patch.object(
            ht.events.event.HoudiniEvent, "item_map", new_callable=mocker.PropertyMock
        )

        mock_map = {}
        mock_item_map.return_value = mock_map

        # Mock the item via the reference in the module so that the isinstance()
        # test is more reliable vs mocking ht.events.item.HoudiniEventItem
        mock_item = mocker.MagicMock(spec=ht.events.event.HoudiniEventItem)

        event = init_event()
        event.register_item(mock_item)

        assert mock_map == {mock_item.priority: [mock_item]}

    # run

    def test_run__not_enabled(self, init_event, mocker):
        """Test running an event that is disabled."""
        mocker.patch.object(
            ht.events.event.HoudiniEvent,
            "enabled",
            new_callable=mocker.PropertyMock(return_value=False),
        )

        event = init_event()

        scriptargs = {"key": "value"}
        event.run(scriptargs)

        # If the event is disabled nothing should happen and scriptargs should
        # be unchanged.
        expected_scriptargs = {"key": "value"}
        assert scriptargs == expected_scriptargs

    def test_run(self, init_event, mocker):
        """Test running all items in an event."""
        mocker.patch.object(
            ht.events.event.HoudiniEvent,
            "enabled",
            new_callable=mocker.PropertyMock(return_value=True),
        )
        mock_stats = mocker.patch.object(
            ht.events.event.HoudiniEvent, "stats", new_callable=mocker.PropertyMock
        )
        mock_item_map = mocker.patch.object(
            ht.events.event.HoudiniEvent, "item_map", new_callable=mocker.PropertyMock
        )

        mock_stats.return_value = mocker.MagicMock(
            spec=ht.events.stats.HoudiniEventStats
        )

        mock_map = {}
        mock_item_map.return_value = mock_map

        event = init_event()

        mock_item1 = mocker.MagicMock(spec=ht.events.item.HoudiniEventItem)
        mock_item1.run.side_effect = lambda sa: sa["order"].append(mock_item1)

        mock_item2 = mocker.MagicMock(spec=ht.events.item.HoudiniEventItem)
        mock_item2.run.side_effect = lambda sa: sa["order"].append(mock_item2)

        mock_item3 = mocker.MagicMock(spec=ht.events.item.HoudiniEventItem)
        mock_item3.run.side_effect = lambda sa: sa["order"].append(mock_item3)

        # Assign objects to event map with priorities.
        mock_map[0] = [mock_item2]
        mock_map[15] = [mock_item3]
        mock_map[5] = [mock_item1]

        scriptargs = {"key": "value", "order": []}

        expected_scriptargs = {
            "key": "value",
            # We expect events to be run in decreasing priority order
            "order": [mock_item3, mock_item1, mock_item2],
        }

        # Run the test event.
        event.run(scriptargs)

        # Make sure each thing was ran.
        mock_item1.run.assert_called_once()
        mock_item2.run.assert_called_once()
        mock_item3.run.assert_called_once()

        assert scriptargs == expected_scriptargs

        # Ensure the context manager was called.
        mock_stats.return_value.__enter__.assert_called_once()
        mock_stats.return_value.__exit__.assert_called_once()
