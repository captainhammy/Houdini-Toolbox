"""Tests for ht.events.item module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import copy
from mock import MagicMock, PropertyMock, patch
import unittest

# Houdini Toolbox Imports
import ht.events.item
import ht.events.stats

reload(ht.events.item)

# =============================================================================
# CLASSES
# =============================================================================

class Test_HoudiniEventItem(unittest.TestCase):
    """Test ht.events.item.HoudiniEventItem class."""

    @patch("ht.events.item.HoudiniEventItemStats", autospec=True)
    def test___init__(self, mock_stats):
        callables = (MagicMock(), MagicMock(), MagicMock())

        item = ht.events.item.HoudiniEventItem(callables, "CoolItem", 3, ["tag"])

        mock_stats.assert_called_with("CoolItem", tags=["tag"])

        self.assertEqual(item._callables, list(callables))
        self.assertEqual(item._name, "CoolItem")
        self.assertEqual(item._priority, 3)
        self.assertEqual(item._data, {})
        self.assertEqual(item._stats, mock_stats.return_value)

    @patch.object(ht.events.item.HoudiniEventItem, "priority", new_callable=PropertyMock)
    @patch.object(ht.events.item.HoudiniEventItem, "callables", new_callable=PropertyMock)
    @patch.object(ht.events.item.HoudiniEventItem, "name", new_callable=PropertyMock)
    @patch.object(ht.events.item.HoudiniEventItem, "__init__", lambda x, y, z, u, v: None)
    def test___eq__(self, mock_name, mock_callables, mock_priority):
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
        self.assertFalse(item1.__eq__(item2))

        mock_name.return_value = "name"
        item2.name = "name"

        # Names the same, callables differ
        self.assertFalse(item1.__eq__(item2))

        item2.callables = callables

        # Names and callables equal, priority differs
        self.assertFalse(item1.__eq__(item2))

        item2.priority = 3

        # Should be equal now
        self.assertEqual(item1, item2)

    @patch.object(ht.events.item.HoudiniEventItem, "__eq__")
    @patch.object(ht.events.item.HoudiniEventItem, "__init__", lambda x, y, z, u, v: None)
    def test___ne__(self, mock_eq):
        item = ht.events.item.HoudiniEventItem(None, None, None, None)
        mock_item = MagicMock(spec=ht.events.item.HoudiniEventItem)

        self.assertEqual(item.__ne__(mock_item), not mock_eq.return_value)
        mock_eq.assert_called_with(mock_item)

    # Properties

    @patch.object(ht.events.item.HoudiniEventItem, "__init__", lambda x, y, z, u, v: None)
    def test_callables(self):
        item = ht.events.item.HoudiniEventItem(None, None, None, None)

        callables = [MagicMock(), MagicMock(), MagicMock()]
        item._callables = callables
        self.assertEqual(item.callables, callables)

    @patch.object(ht.events.item.HoudiniEventItem, "__init__", lambda x, y, z, u, v: None)
    def test_data(self):

        item = ht.events.item.HoudiniEventItem(None, None, None, None)

        item._data = {"key": "value"}
        self.assertEqual(item.data, {"key": "value"})

    @patch.object(ht.events.item.HoudiniEventItem, "__init__", lambda x, y, z, u, v: None)
    def test_name(self):
        """Test 'name' access property."""
        item = ht.events.item.HoudiniEventItem(None, None, None, None)

        item._name = "name"
        self.assertEqual(item.name, "name")

    @patch.object(ht.events.item.HoudiniEventItem, "__init__", lambda x, y, z, u, v: None)
    def test_priority(self):
        item = ht.events.item.HoudiniEventItem(None, None, None, None)

        item._priority = 111
        self.assertEqual(item.priority, 111)

    @patch.object(ht.events.item.HoudiniEventItem, "__init__", lambda x, y, z, u, v: None)
    def test_stats(self):
        item = ht.events.item.HoudiniEventItem(None, None, None, None)

        mock_stats = MagicMock(spec=ht.events.stats.HoudiniEventItemStats)
        item._stats = mock_stats
        self.assertEqual(item.stats, mock_stats)

    # Methods

    @patch.object(ht.events.item.HoudiniEventItem, "callables", new_callable=PropertyMock)
    @patch.object(ht.events.item.HoudiniEventItem, "stats", new_callable=PropertyMock)
    @patch.object(ht.events.item.HoudiniEventItem, "__init__", lambda x, y, z, u, v: None)
    def test_run(self, mock_stats, mock_callables):
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

        callables = [
            mock_func1,
            mock_func2
        ]

        mock_callables.return_value = callables

        scriptargs = {"foo": "bar"}
        run_args = {"foo": "bar", "_item_": item}

        item.run(scriptargs)

        # Ensure the context manager was called.
        stats.__enter__.assert_called_once()
        stats.__exit__.assert_called_once()

        # Ensure time_child was called with the functions.  Do it this way since
        # the calls list is confusing due to the contextmanager decorator.
        stats.time_function.assert_any_call(mock_func1)
        stats.time_function.assert_any_call(mock_func2)

        # Ensure the functions were called with the real args.
        self.assertEqual(real_call_args[0], run_args)
        self.assertEqual(real_call_args[1], run_args)

        # Ensure we removed the item.
        self.assertEqual(scriptargs, {"foo": "bar"})


class Test_ExclusiveHoudiniEventItem(unittest.TestCase):
    """Test ht.events.item.ExclusiveHoudiniEventItem class."""

    @patch.object(ht.events.item.HoudiniEventItem, "__init__")
    @patch.object(ht.events.item.ExclusiveHoudiniEventItem, "priority", new_callable=PropertyMock)
    def test___init__(self, mock_priority, mock_super_init):
        mock_callable = MagicMock()
        name = "some_name"
        priority = 4
        stat_tags = ["foo"]

        mock_priority.return_value = priority

        map_dict = {}

        with patch.dict(ht.events.item.ExclusiveHoudiniEventItem._exclusive_map, map_dict, clear=True):
            item = ht.events.item.ExclusiveHoudiniEventItem([mock_callable], name, priority, stat_tags)

            mock_super_init.assert_called_with([mock_callable], name, priority, stat_tags)

            self.assertEqual(ht.events.item.ExclusiveHoudiniEventItem._exclusive_map, {name: item})

    @patch.object(ht.events.item.HoudiniEventItem, "__init__")
    @patch.object(ht.events.item.ExclusiveHoudiniEventItem, "priority", new_callable=PropertyMock)
    def test___init__replace(self, mock_priority, mock_super_init):
        mock_existing = MagicMock(spec=ht.events.item.ExclusiveHoudiniEventItem)
        mock_existing.priority = 1

        mock_callable = MagicMock()
        name = "some_name"
        priority = 4
        stat_tags = ["foo"]

        mock_priority.return_value = priority

        map_dict = {
            name: mock_existing
        }

        with patch.dict(ht.events.item.ExclusiveHoudiniEventItem._exclusive_map, map_dict, clear=True):
            item = ht.events.item.ExclusiveHoudiniEventItem([mock_callable], name, priority, stat_tags)

            mock_super_init.assert_called_with([mock_callable], name, priority, stat_tags)

            self.assertEqual(ht.events.item.ExclusiveHoudiniEventItem._exclusive_map, {name: item})

    @patch("ht.events.item.ExclusiveHoudiniEventItem.__eq__")
    @patch.object(ht.events.item.ExclusiveHoudiniEventItem, "__init__", lambda x, y, z, u, v: None)
    def test_run__no_run(self, mock_eq):
        mock_eq.return_value = False

        item = ht.events.item.ExclusiveHoudiniEventItem(None, None, None, None)
        item._name = "some_name"

        map_dict = {"some_name": item}

        scriptargs = {"foo": "bar"}

        with patch.object(ht.events.item.HoudiniEventItem, "run") as mock_super_run:
            with patch.dict(ht.events.item.ExclusiveHoudiniEventItem._exclusive_map, map_dict, clear=True):
                item.run(scriptargs)

            mock_super_run.assert_not_called()

    @patch("ht.events.item.ExclusiveHoudiniEventItem.__eq__")
    @patch.object(ht.events.item.ExclusiveHoudiniEventItem, "__init__", lambda x, y, z, u, v: None)
    def test__run(self, mock_eq):
        mock_eq.return_value = True

        item = ht.events.item.ExclusiveHoudiniEventItem(None, None, None, None)
        item._name = "some_name"

        map_dict = {"some_name": item}

        scriptargs = {"foo": "bar"}

        with patch.object(ht.events.item.HoudiniEventItem, "run") as mock_super_run:
            with patch.dict(ht.events.item.ExclusiveHoudiniEventItem._exclusive_map, map_dict, clear=True):
                item.run(scriptargs)

            mock_super_run.assert_called_with(scriptargs)

# =============================================================================

if __name__ == '__main__':
    unittest.main()


