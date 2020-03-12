"""Tests for ht.events.item module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import copy

# Third Party Imports
import pytest

# Houdini Toolbox Imports
import ht.events.item
import ht.events.stats


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def init_exclusive_item(mocker):
    """Fixture to initialize an exclusive item."""
    mocker.patch.object(
        ht.events.item.ExclusiveHoudiniEventItem, "__init__", lambda x, y, z: None
    )

    def _create():
        return ht.events.item.ExclusiveHoudiniEventItem(None, None)

    return _create


@pytest.fixture
def init_item(mocker):
    """Fixture to initialize an item."""
    mocker.patch.object(ht.events.item.HoudiniEventItem, "__init__", lambda x, y: None)

    def _create():
        return ht.events.item.HoudiniEventItem(None)

    return _create


# =============================================================================
# TESTS
# =============================================================================


class Test_HoudiniEventItem(object):
    """Test ht.events.item.HoudiniEventItem class."""

    def test___init__(self, mocker):
        """Test object initialization."""
        mock_stats = mocker.patch("ht.events.item.HoudiniEventItemStats", autospec=True)

        callables = (mocker.MagicMock(), mocker.MagicMock(), mocker.MagicMock())
        mock_name = mocker.MagicMock(spec=str)
        mock_priority = mocker.MagicMock(spec=int)
        mock_tags = mocker.MagicMock(spec=list)

        item = ht.events.item.HoudiniEventItem(
            callables, mock_name, mock_priority, mock_tags
        )

        mock_stats.assert_called_with(mock_name, tags=mock_tags)

        assert item._callables == list(callables)
        assert item._name == mock_name
        assert item._priority == mock_priority
        assert item._data == {}
        assert item._stats == mock_stats.return_value

    def test___eq__(self, init_item, mocker):
        """Test the equality operator."""
        mock_name = mocker.patch.object(
            ht.events.item.HoudiniEventItem, "name", new_callable=mocker.PropertyMock
        )
        mock_callables = mocker.patch.object(
            ht.events.item.HoudiniEventItem,
            "callables",
            new_callable=mocker.PropertyMock,
        )
        mock_priority = mocker.patch.object(
            ht.events.item.HoudiniEventItem,
            "priority",
            new_callable=mocker.PropertyMock,
        )

        callables = [mocker.MagicMock(), mocker.MagicMock(), mocker.MagicMock()]

        mock_callables.return_value = callables
        mock_name.return_value = "name1"
        mock_priority.return_value = 3

        item1 = init_item()

        item2 = mocker.MagicMock(spec=ht.events.item.HoudiniEventItem)
        item2.callables = []
        item2.name = "name2"
        item2.priority = 4

        # Names differ
        assert not item1.__eq__(item2)

        mock_name.return_value = "name"
        item2.name = "name"

        # Names the same, callables differ
        assert not item1.__eq__(item2)

        item2.callables = callables

        # Names and callables equal, priority differs
        assert not item1.__eq__(item2)

        item2.priority = 3

        # Should be equal now
        assert item1 == item2

        assert item1.__eq__(mocker.MagicMock()) == NotImplemented

    def test___ne__(self, init_item, mocker):
        """Test the not-equals operator."""
        mock_eq = mocker.patch.object(ht.events.item.HoudiniEventItem, "__eq__")

        item = init_item()
        mock_item = mocker.MagicMock(spec=ht.events.item.HoudiniEventItem)

        assert item.__ne__(mock_item) != mock_eq.return_value
        mock_eq.assert_called_with(mock_item)

    def test___hash__(self, init_item, mocker):
        """Test the not-equals operator."""
        item = init_item()

        mock_name = mocker.MagicMock(spec=str)
        mock_priority = mocker.MagicMock(spec=int)

        item._name = mock_name
        item._priority = mock_priority

        assert item.__hash__() == hash((mock_name, mock_priority))

    # Properties

    def test_callables(self, init_item, mocker):
        """Test the 'callables' property."""
        mock_value = mocker.MagicMock(spec=list)

        item = init_item()

        item._callables = mock_value
        assert item.callables == mock_value

    def test_data(self, init_item, mocker):
        """Test the 'data' property."""
        mock_value = mocker.MagicMock(spec=dict)

        item = init_item()

        item._data = mock_value
        assert item.data == mock_value

    def test_name(self, init_item, mocker):
        """Test 'name' property."""
        mock_value = mocker.MagicMock(spec=str)

        item = init_item()

        item._name = mock_value
        assert item.name == mock_value

    def test_priority(self, init_item, mocker):
        """Test the 'priority' property."""
        mock_value = mocker.MagicMock(spec=int)

        item = init_item()

        item._priority = mock_value
        assert item.priority == mock_value

    def test_stats(self, init_item, mocker):
        """Test the 'stats' property."""
        item = init_item()

        mock_stats = mocker.MagicMock(spec=ht.events.stats.HoudiniEventItemStats)
        item._stats = mock_stats
        assert item.stats == mock_stats

    # Methods

    def test_run(self, init_item, mocker):
        """Test running an item."""
        mock_stats = mocker.patch.object(
            ht.events.item.HoudiniEventItem, "stats", new_callable=mocker.PropertyMock
        )
        mock_callables = mocker.patch.object(
            ht.events.item.HoudiniEventItem,
            "callables",
            new_callable=mocker.PropertyMock,
        )

        item = init_item()

        stats = mocker.MagicMock(spec=ht.events.stats.HoudiniEventItemStats)

        mock_stats.return_value = stats

        # To ensure that the callables are called with the HoudiniEventItem in the scriptargs
        # as _item_ we need to record the call data ourselves because Mock just
        # stores a reference and since we add/del the item into the dict it won't
        # be there inside the data that it thinks the functions were called with.
        real_call_args = []

        mock_func1 = mocker.MagicMock()
        mock_func1.side_effect = lambda sa: real_call_args.append(copy.copy(sa))

        mock_func2 = mocker.MagicMock()
        mock_func2.side_effect = lambda sa: real_call_args.append(copy.copy(sa))

        mock_callables.return_value = [mock_func1, mock_func2]

        scriptargs = {"key": "value"}
        run_args = {"key": "value", "_item_": item}

        item.run(scriptargs)

        # Ensure the context manager was called.
        stats.__enter__.assert_called_once()
        stats.__exit__.assert_called_once()

        # Ensure time_child was called with the functions.  Do it this way since
        # the calls list is confusing due to the contextmanager decorator.
        stats.time_function.assert_any_call(mock_func1)
        stats.time_function.assert_any_call(mock_func2)

        # Ensure the functions were called with the real args.
        assert real_call_args[0] == run_args
        assert real_call_args[1] == run_args

        # Ensure we removed the item.
        assert scriptargs == {"key": "value"}


class Test_ExclusiveHoudiniEventItem(object):
    """Test ht.events.item.ExclusiveHoudiniEventItem class."""

    # __init__

    def test___init__(self, mocker):
        """Test object initialization."""
        mock_priority = mocker.patch.object(
            ht.events.item.ExclusiveHoudiniEventItem,
            "priority",
            new_callable=mocker.PropertyMock,
        )
        mock_super_init = mocker.patch.object(
            ht.events.item.HoudiniEventItem, "__init__"
        )
        mock_map = mocker.patch.object(
            ht.events.item.ExclusiveHoudiniEventItem,
            "_exclusive_map",
            new_callable=mocker.PropertyMock,
        )

        mock_callables = (mocker.MagicMock(),)
        mock_name = mocker.MagicMock(spec=str)
        priority = mocker.MagicMock(spec=int)
        mock_stat_tags = mocker.MagicMock(spec=list)

        mock_priority.return_value = priority

        mock_map.return_value = {}

        item = ht.events.item.ExclusiveHoudiniEventItem(
            mock_callables, mock_name, priority, mock_stat_tags
        )

        mock_super_init.assert_called_with(
            mock_callables, mock_name, priority, mock_stat_tags
        )

        assert ht.events.item.ExclusiveHoudiniEventItem._exclusive_map == {
            mock_name: item
        }

    def test___init__replace(self, mocker):
        """Test initialization when replacing an existing item."""
        mock_priority = mocker.patch.object(
            ht.events.item.ExclusiveHoudiniEventItem,
            "priority",
            new_callable=mocker.PropertyMock,
        )
        mock_super_init = mocker.patch.object(
            ht.events.item.HoudiniEventItem, "__init__"
        )
        mock_map = mocker.patch.object(
            ht.events.item.ExclusiveHoudiniEventItem,
            "_exclusive_map",
            new_callable=mocker.PropertyMock,
        )

        mock_existing = mocker.MagicMock(spec=ht.events.item.ExclusiveHoudiniEventItem)
        mock_existing.priority = 1

        mock_callables = (mocker.MagicMock(),)
        mock_name = mocker.MagicMock(spec=str)
        priority = mocker.MagicMock(spec=int)
        mock_stat_tags = mocker.MagicMock(spec=list)

        mock_priority.return_value = 3

        mapping = {mock_name: mock_existing}
        mock_map.return_value = mapping

        item = ht.events.item.ExclusiveHoudiniEventItem(
            mock_callables, mock_name, priority, mock_stat_tags
        )

        mock_super_init.assert_called_with(
            mock_callables, mock_name, priority, mock_stat_tags
        )

        assert mapping == {mock_name: item}

    # Methods

    # run

    def test_run__no_run(self, init_exclusive_item, mocker):
        """Test when the event item is not the exclusive item."""
        mocker.patch(
            "ht.events.item.ExclusiveHoudiniEventItem.__eq__", return_value=False
        )
        mock_super_run = mocker.patch.object(ht.events.item.HoudiniEventItem, "run")
        mock_map = mocker.patch.object(
            ht.events.item.ExclusiveHoudiniEventItem,
            "_exclusive_map",
            new_callable=mocker.PropertyMock,
        )
        mock_name = mocker.patch.object(
            ht.events.item.ExclusiveHoudiniEventItem,
            "name",
            new_callable=mocker.PropertyMock,
        )

        item = init_exclusive_item()

        mock_map.return_value = {mock_name.return_value: item}

        scriptargs = {"key": "value"}

        item.run(scriptargs)
        mock_super_run.assert_not_called()

    def test__run(self, init_exclusive_item, mocker):
        """Test when the event item is the exclusive item."""
        mocker.patch(
            "ht.events.item.ExclusiveHoudiniEventItem.__eq__", return_value=True
        )
        mock_super_run = mocker.patch.object(ht.events.item.HoudiniEventItem, "run")
        mock_map = mocker.patch.object(
            ht.events.item.ExclusiveHoudiniEventItem,
            "_exclusive_map",
            new_callable=mocker.PropertyMock,
        )
        mock_name = mocker.patch.object(
            ht.events.item.ExclusiveHoudiniEventItem,
            "name",
            new_callable=mocker.PropertyMock,
        )

        item = init_exclusive_item()

        mock_map.return_value = {mock_name.return_value: item}

        mock_scriptargs = mocker.MagicMock(spec=dict)

        item.run(mock_scriptargs)

        mock_super_run.assert_called_with(mock_scriptargs)
