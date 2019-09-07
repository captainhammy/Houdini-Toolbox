"""Tests for ht.events.item module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import copy
import imp

# Python Imports
from mock import MagicMock, PropertyMock, patch

# Houdini Toolbox Imports
import ht.events.item
import ht.events.stats

# Reload the module to test to capture load evaluation since it has already
# been loaded.
imp.reload(ht.events.item)


# =============================================================================
# CLASSES
# =============================================================================

class Test_HoudiniEventItem(object):
    """Test ht.events.item.HoudiniEventItem class."""

    @patch("ht.events.item.HoudiniEventItemStats", autospec=True)
    def test___init__(self, mock_stats):
        """Test the constructor."""
        callables = (MagicMock(), MagicMock(), MagicMock())
        mock_name = MagicMock(spec=str)
        mock_priority = MagicMock(spec=int)
        mock_tags = MagicMock(spec=list)

        item = ht.events.item.HoudiniEventItem(callables, mock_name, mock_priority, mock_tags)

        mock_stats.assert_called_with(mock_name, tags=mock_tags)

        assert item._callables == list(callables)
        assert item._name == mock_name
        assert item._priority == mock_priority
        assert item._data == {}
        assert item._stats == mock_stats.return_value

    @patch.object(ht.events.item.HoudiniEventItem, "priority", new_callable=PropertyMock)
    @patch.object(ht.events.item.HoudiniEventItem, "callables", new_callable=PropertyMock)
    @patch.object(ht.events.item.HoudiniEventItem, "name", new_callable=PropertyMock)
    @patch.object(ht.events.item.HoudiniEventItem, "__init__", lambda x, y, z, u, v: None)
    def test___eq__(self, mock_name, mock_callables, mock_priority):
        """Test the equality operator."""
        callables = [MagicMock(), MagicMock(), MagicMock()]

        mock_callables.return_value = callables
        mock_name.return_value = "name1"
        mock_priority.return_value = 3

        item1 = ht.events.item.HoudiniEventItem(None, None, None, None)

        item2 = MagicMock(spec=ht.events.item.HoudiniEventItem)
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

        assert item1.__eq__(MagicMock()) == NotImplemented

    @patch.object(ht.events.item.HoudiniEventItem, "__eq__")
    @patch.object(ht.events.item.HoudiniEventItem, "__init__", lambda x, y, z, u, v: None)
    def test___ne__(self, mock_eq):
        """Test the not-equals operator."""
        item = ht.events.item.HoudiniEventItem(None, None, None, None)
        mock_item = MagicMock(spec=ht.events.item.HoudiniEventItem)

        assert item.__ne__(mock_item) != mock_eq.return_value
        mock_eq.assert_called_with(mock_item)

    @patch.object(ht.events.item.HoudiniEventItem, "__init__", lambda x, y, z, u, v: None)
    def test___hash__(self):
        """Test the not-equals operator."""
        item = ht.events.item.HoudiniEventItem(None, None, None, None)

        mock_name = MagicMock(spec=str)
        mock_priority = MagicMock(spec=int)

        item._name = mock_name
        item._priority = mock_priority

        assert item.__hash__() == hash((mock_name, mock_priority))

    # Properties

    @patch.object(ht.events.item.HoudiniEventItem, "__init__", lambda x, y, z, u, v: None)
    def test_callables(self):
        """Test the 'callables' property."""
        mock_value = MagicMock(spec=list)

        item = ht.events.item.HoudiniEventItem(None, None, None, None)

        item._callables = mock_value
        assert item.callables == mock_value

    @patch.object(ht.events.item.HoudiniEventItem, "__init__", lambda x, y, z, u, v: None)
    def test_data(self):
        """Test the 'data' property."""
        mock_value = MagicMock(spec=dict)

        item = ht.events.item.HoudiniEventItem(None, None, None, None)

        item._data = mock_value
        assert item.data == mock_value

    @patch.object(ht.events.item.HoudiniEventItem, "__init__", lambda x, y, z, u, v: None)
    def test_name(self):
        """Test 'name' property."""
        mock_value = MagicMock(spec=str)

        item = ht.events.item.HoudiniEventItem(None, None, None, None)

        item._name = mock_value
        assert item.name == mock_value

    @patch.object(ht.events.item.HoudiniEventItem, "__init__", lambda x, y, z, u, v: None)
    def test_priority(self):
        """Test the 'priority' property."""
        mock_value = MagicMock(spec=int)

        item = ht.events.item.HoudiniEventItem(None, None, None, None)

        item._priority = mock_value
        assert item.priority == mock_value

    @patch.object(ht.events.item.HoudiniEventItem, "__init__", lambda x, y, z, u, v: None)
    def test_stats(self):
        """Test the 'stats' property."""
        item = ht.events.item.HoudiniEventItem(None, None, None, None)

        mock_stats = MagicMock(spec=ht.events.stats.HoudiniEventItemStats)
        item._stats = mock_stats
        assert item.stats == mock_stats

    # Methods

    @patch.object(ht.events.item.HoudiniEventItem, "callables", new_callable=PropertyMock)
    @patch.object(ht.events.item.HoudiniEventItem, "stats", new_callable=PropertyMock)
    @patch.object(ht.events.item.HoudiniEventItem, "__init__", lambda x, y, z, u, v: None)
    def test_run(self, mock_stats, mock_callables):
        """Test running an item."""
        item = ht.events.item.HoudiniEventItem(None, None, None, None)

        stats = MagicMock(spec=ht.events.stats.HoudiniEventItemStats)

        mock_stats.return_value = stats

        # To ensure that the callables are called with the HoudiniEventItem in the scriptargs
        # as _item_ we need to record the call data ourselves because Mock just
        # stores a reference and since we add/del the item into the dict it won't
        # be there inside the data that it thinks the functions were called with.
        real_call_args = []

        mock_func1 = MagicMock()
        mock_func1.side_effect = lambda sa: real_call_args.append(copy.copy(sa))

        mock_func2 = MagicMock()
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
        assert real_call_args[1] ==run_args

        # Ensure we removed the item.
        assert scriptargs == {"key": "value"}


class Test_ExclusiveHoudiniEventItem(object):
    """Test ht.events.item.ExclusiveHoudiniEventItem class."""

    @patch.object(ht.events.item.ExclusiveHoudiniEventItem, "_exclusive_map", new_callable=PropertyMock)
    @patch.object(ht.events.item.HoudiniEventItem, "__init__")
    @patch.object(ht.events.item.ExclusiveHoudiniEventItem, "priority", new_callable=PropertyMock)
    def test___init__(self, mock_priority, mock_super_init, mock_map):
        """Test the constructor."""
        mock_callables = (MagicMock(), )
        mock_name = MagicMock(spec=str)
        priority = MagicMock(spec=int)
        mock_stat_tags = MagicMock(spec=list)

        mock_priority.return_value = priority

        mock_map.return_value = {}

        item = ht.events.item.ExclusiveHoudiniEventItem(mock_callables, mock_name, priority, mock_stat_tags)

        mock_super_init.assert_called_with(mock_callables, mock_name, priority, mock_stat_tags)

        assert ht.events.item.ExclusiveHoudiniEventItem._exclusive_map == {mock_name: item}

    @patch.object(ht.events.item.ExclusiveHoudiniEventItem, "_exclusive_map", new_callable=PropertyMock)
    @patch.object(ht.events.item.HoudiniEventItem, "__init__")
    @patch.object(ht.events.item.ExclusiveHoudiniEventItem, "priority", new_callable=PropertyMock)
    def test___init__replace(self, mock_priority, mock_super_init, mock_map):
        """Test the constructor when replacing an existing item."""
        mock_existing = MagicMock(spec=ht.events.item.ExclusiveHoudiniEventItem)
        mock_existing.priority = 1

        mock_callables = (MagicMock(), )
        mock_name = MagicMock(spec=str)
        priority = MagicMock(spec=int)
        mock_stat_tags = MagicMock(spec=list)

        mock_priority.return_value = 3

        mapping = {mock_name: mock_existing}
        mock_map.return_value = mapping

        item = ht.events.item.ExclusiveHoudiniEventItem(mock_callables, mock_name, priority, mock_stat_tags)

        mock_super_init.assert_called_with(mock_callables, mock_name, priority, mock_stat_tags)

        assert mapping == {mock_name: item}

    @patch.object(ht.events.item.ExclusiveHoudiniEventItem, "name", new_callable=PropertyMock)
    @patch.object(ht.events.item.ExclusiveHoudiniEventItem, "_exclusive_map", new_callable=PropertyMock)
    @patch.object(ht.events.item.HoudiniEventItem, "run")
    @patch("ht.events.item.ExclusiveHoudiniEventItem.__eq__")
    @patch.object(ht.events.item.ExclusiveHoudiniEventItem, "__init__", lambda x, y, z, u, v: None)
    def test_run__no_run(self, mock_eq, mock_super_run, mock_map, mock_name):
        mock_eq.return_value = False

        item = ht.events.item.ExclusiveHoudiniEventItem(None, None, None, None)

        mock_map.return_value = {mock_name.return_value: item}

        scriptargs = {"key": "value"}

        item.run(scriptargs)
        mock_super_run.assert_not_called()

    @patch.object(ht.events.item.ExclusiveHoudiniEventItem, "name", new_callable=PropertyMock)
    @patch.object(ht.events.item.ExclusiveHoudiniEventItem, "_exclusive_map", new_callable=PropertyMock)
    @patch.object(ht.events.item.HoudiniEventItem, "run")
    @patch("ht.events.item.ExclusiveHoudiniEventItem.__eq__")
    @patch.object(ht.events.item.ExclusiveHoudiniEventItem, "__init__", lambda x, y, z, u, v: None)
    def test__run(self, mock_eq, mock_super_run, mock_map, mock_name):
        mock_eq.return_value = True

        item = ht.events.item.ExclusiveHoudiniEventItem(None, None, None, None)

        mock_map.return_value = {mock_name.return_value: item}

        mock_scriptargs = MagicMock(spec=dict)

        item.run(mock_scriptargs)

        mock_super_run.assert_called_with(mock_scriptargs)
