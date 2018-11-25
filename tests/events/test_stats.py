"""Tests for ht.events.stats module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
from collections import OrderedDict
from mock import MagicMock, PropertyMock, patch
import unittest

# Houdini Toolbox Imports
import ht.events.stats

reload(ht.events.stats)

# =============================================================================
# CLASSES
# =============================================================================

class Test__StatsMeta(unittest.TestCase):
    """Test ht.events.stats._StatsMeta metaclass."""

    def tearDown(self):
        super(Test__StatsMeta, self).tearDown()

        ht.events.stats._StatsMeta._instances.clear()

        del self._Tester

    def setUp(self):
        super(Test__StatsMeta, self).setUp()

        class _Tester(object):
            __metaclass__ = ht.events.stats._StatsMeta

            def __init__(self, name, tags=None, post_report=False):
                self._post_report = post_report

                if tags is None:
                    tags = []

                self._tags = tags

        self._Tester = _Tester

    def test_new(self):
        thinger = self._Tester("name")

        self.assertEqual(
            ht.events.stats._StatsMeta._instances,
            {self._Tester: {"name": thinger}}
        )

    def test_existing_default_args(self):
        thinger1 = self._Tester("name")
        thinger2 = self._Tester("name")

        self.assertTrue(thinger1 is thinger2)

    def test_existing_tags_positional(self):
        thinger1 = self._Tester("name", ["foo"])
        thinger2 = self._Tester("name", ["bar"])

        self.assertEqual(thinger1._tags, ["foo", "bar"])
        self.assertTrue(thinger1 is thinger2)

    def test_existing_tags_passed(self):
        thinger1 = self._Tester("name", tags=["foo"])
        thinger2 = self._Tester("name", tags=["bar"])

        self.assertEqual(thinger1._tags, ["foo", "bar"])
        self.assertTrue(thinger1 is thinger2)

    def test_existing_tags_avoid_duplicates(self):
        thinger1 = self._Tester("name", tags=["foo"])
        thinger2 = self._Tester("name", tags=["foo"])

        self.assertEqual(thinger1._tags, ["foo"])
        self.assertTrue(thinger1 is thinger2)

    def test_existing_post_report_positional(self):
        thinger1 = self._Tester("name", None, False)
        thinger2 = self._Tester("name", None, True)

        self.assertTrue(thinger1._post_report)
        self.assertTrue(thinger1 is thinger2)

    def test_existing_post_report_passed(self):
        thinger1 = self._Tester("name", post_report=False)
        thinger2 = self._Tester("name", post_report=True)

        self.assertTrue(thinger1._post_report)
        self.assertTrue(thinger1 is thinger2)

    def test_existing_post_report_passed_keep_existing(self):
        thinger1 = self._Tester("name", post_report=True)
        thinger2 = self._Tester("name", post_report=False)

        self.assertTrue(thinger1._post_report)
        self.assertTrue(thinger1 is thinger2)

class Test_HoudiniEventStats(unittest.TestCase):
    """Test ht.events.stats.HoudiniEventStats class."""

    def test___init___no_tags(self):
        name = "name"

        stats = ht.events.stats.HoudiniEventStats(name, post_report=True)

        self.assertEqual(stats._last_run_time, 0)
        self.assertEqual(stats._last_started, 0)
        self.assertEqual(stats._name, name)
        self.assertTrue(stats._post_report)
        self.assertEqual(stats._run_count, 0)
        self.assertEqual(stats._total_time, 0)

        self.assertEqual(stats._tags, [])

    def test___init___tags(self):
        name = "name"
        tags = ["tag"]
        stats = ht.events.stats.HoudiniEventStats(name, tags=tags, post_report=True)

        self.assertEqual(stats._last_run_time, 0)
        self.assertEqual(stats._last_started, 0)
        self.assertEqual(stats._name, name)
        self.assertTrue(stats._post_report)
        self.assertEqual(stats._run_count, 0)
        self.assertEqual(stats._total_time, 0)

        self.assertEqual(stats._tags, tags)


    @patch.object(ht.events.stats.HoudiniEventStats, "__init__", lambda x, y: None)
    def test___repr__(self):
        stats = ht.events.stats.HoudiniEventStats(None)

        stats._name = "name"
        stats._run_count = 3
        stats._total_time = 22.123456

        result = stats.__repr__()

        self.assertEqual(result, "<HoudiniEventStats: name run_count=3 total_time=22.123>")

    # Properties

    @patch.object(ht.events.stats.HoudiniEventStats, "__init__", lambda x, y: None)
    def test_last_run_time(self):
        stats = ht.events.stats.HoudiniEventStats(None)

        stats._last_run_time = 123
        self.assertEqual(stats._last_run_time, stats.last_run_time)

    @patch.object(ht.events.stats.HoudiniEventStats, "__init__", lambda x, y: None)
    def test_name(self):
        stats = ht.events.stats.HoudiniEventStats(None)

        stats._name = "test_name"
        self.assertEqual(stats._name, stats.name)

    @patch.object(ht.events.stats.HoudiniEventStats, "__init__", lambda x, y: None)
    def test_post_report(self):
        stats = ht.events.stats.HoudiniEventStats(None)

        stats._post_report = True
        self.assertEqual(stats._post_report, stats.post_report)

    @patch.object(ht.events.stats.HoudiniEventStats, "__init__", lambda x, y: None)
    def test_run_count(self):
        stats = ht.events.stats.HoudiniEventStats(None)

        stats._run_count = 3
        self.assertEqual(stats._run_count, stats.run_count)

    @patch.object(ht.events.stats.HoudiniEventStats, "__init__", lambda x, y: None)
    def test_tags(self):
        stats = ht.events.stats.HoudiniEventStats(None)

        stats._tags = ["tag1", "tag2"]
        self.assertEqual(stats._tags, stats.tags)

    @patch.object(ht.events.stats.HoudiniEventStats, "__init__", lambda x, y: None)
    def test_total_time(self):
        stats = ht.events.stats.HoudiniEventStats(None)

        stats._total_time = 30
        self.assertEqual(stats._total_time, stats.total_time)

    # Methods

    @patch("time.time")
    @patch.object(ht.events.stats.HoudiniEventStats, "__init__", lambda x, y: None)
    def test_enter(self, mock_time):
        stats = ht.events.stats.HoudiniEventStats(None)

        mock_time.return_value = 123

        stats.__enter__()

        self.assertEqual(stats._last_started, 123)

    @patch.object(ht.events.stats.HoudiniEventStats, "print_report")
    @patch("time.time")
    @patch.object(ht.events.stats.HoudiniEventStats, "__init__", lambda x, y: None)
    def test_exit(self, mock_time, mock_print):
        mock_time.return_value = 456

        stats = ht.events.stats.HoudiniEventStats(None)

        stats._post_report = True

        stats._last_run_time = 0
        stats._total_time = 0
        stats._last_started = 123
        stats._run_count = 0

        exc_type = MagicMock()
        exc_val = MagicMock()
        exc_tb = MagicMock()

        stats.__exit__(exc_type, exc_val, exc_tb)

        run_time = 456-123

        self.assertEqual(stats.last_run_time, run_time)
        self.assertEqual(stats.total_time, run_time)
        self.assertEqual(stats.run_count, 1)

        mock_print.assert_called_once()

    @patch.object(ht.events.stats.HoudiniEventStats, "print_report")
    @patch("time.time")
    @patch.object(ht.events.stats.HoudiniEventStats, "__init__", lambda x, y: None)
    def test_exit_no_post(self, mock_time, mock_print):
        mock_time.return_value = 456

        stats = ht.events.stats.HoudiniEventStats(None)

        stats._post_report = False

        stats._last_run_time = 0
        stats._total_time = 0
        stats._last_started = 123
        stats._run_count = 0

        exc_type = MagicMock()
        exc_val = MagicMock()
        exc_tb = MagicMock()

        stats.__exit__(exc_type, exc_val, exc_tb)

        run_time = 456-123

        self.assertEqual(stats.last_run_time, run_time)
        self.assertEqual(stats.total_time, run_time)
        self.assertEqual(stats.run_count, 1)

        mock_print.assert_not_called()

    @patch.object(ht.events.stats.HoudiniEventStats, "__init__", lambda x, y: None)
    def test_print_report(self):
        stats = ht.events.stats.HoudiniEventStats(None)

        stats._last_run_time = 3.123456
        stats._run_count = 2
        stats._name = "name"

        stats.print_report()

    @patch.object(ht.events.stats.HoudiniEventStats, "__init__", lambda x, y: None)
    def test_reset(self):
        stats = ht.events.stats.HoudiniEventStats(None)

        stats._last_run_time = 3
        stats._run_count = 2
        stats._total_time = 5

        stats.reset()

        self.assertEqual(stats._last_run_time, 0)
        self.assertEqual(stats._run_count, 0)
        self.assertEqual(stats._total_time, 0)

# =============================================================================

class Test_HoudiniEventItemStats(unittest.TestCase):
    """Test ht.events.stats.HoudiniEventItemStats class."""

    def test___init__(self):
        name = "name"
        tags = ["tag1", "tag2"]

        with patch.dict(ht.events.stats._StatsMeta._instances, {}, clear=True):
            stats = ht.events.stats.HoudiniEventItemStats(name, tags, True)

            self.assertTrue(isinstance(stats._item_stats, OrderedDict))

    # Properties

    @patch.object(ht.events.stats.HoudiniEventItemStats, "__init__", lambda x, y: None)
    def test_item_stats(self):
        stats = ht.events.stats.HoudiniEventItemStats(None)

        stats._item_stats = OrderedDict({"item": "stats"})
        self.assertEqual(stats._item_stats, stats.item_stats)

    # Methods

    def test_print_report(self):
        # TODO: figure out a test
        pass

    @patch.object(ht.events.stats.HoudiniEventItemStats, "__init__", lambda x, y: None)
    def test_print_report(self):
        item_stats= OrderedDict()
        item_stats["stat name"] = 123.456789

        stats = ht.events.stats.HoudiniEventItemStats(None)

        stats._run_count = 2
        stats._name = "name"
        stats._item_stats = item_stats
        stats._last_run_time = 456.12345678

        stats.print_report()

    @patch.object(ht.events.stats.HoudiniEventStats, "reset")
    @patch.object(ht.events.stats.HoudiniEventItemStats, "__init__", lambda x, y: None)
    def test_reset(self, mock_super_reset):
        mock_item_stats = MagicMock(spec=OrderedDict)

        stats = ht.events.stats.HoudiniEventItemStats(None)

        stats._item_stats = mock_item_stats

        stats.reset()

        mock_super_reset.assert_called_once()
        mock_item_stats.clear.assert_called_once()

    @patch("time.time")
    @patch.object(ht.events.stats.HoudiniEventItemStats, "__init__", lambda x, y: None)
    def test_time_function(self, mock_time):
        mock_time.side_effect = (1, 2, 5, 7)

        mock_func1 = MagicMock()
        mock_func1.__name__ = "foo"

        mock_func2 = MagicMock()
        mock_func2.__name__ = "bar"

        stats = ht.events.stats.HoudiniEventItemStats(None)
        stats._item_stats = OrderedDict()

        with stats.time_function(mock_func1):
            pass

        with stats.time_function(mock_func2):
            pass

        expected = OrderedDict()
        expected["foo"] = 1
        expected["bar"] = 2

        self.assertEqual(stats.item_stats, expected)

    @patch("time.time")
    @patch.object(ht.events.stats.HoudiniEventItemStats, "__init__", lambda x, y: None)
    def test_time_function_existing(self, mock_time):
        mock_time.side_effect = (1, 2, 5, 7)

        mock_func1 = MagicMock()
        mock_func1.__name__ = "foo"

        mock_func2 = MagicMock()
        mock_func2.__name__ = "bar"

        stats = ht.events.stats.HoudiniEventItemStats(None)
        stats._item_stats = OrderedDict()
        stats._item_stats["foo"] = 1

        with stats.time_function(mock_func1):
            pass

        with stats.time_function(mock_func2):
            pass

        expected = OrderedDict()
        expected["foo"] = 2
        expected["bar"] = 2

        self.assertEqual(stats.item_stats, expected)


class Test__get_matching_stats(unittest.TestCase):
    """Test ht.events.stats._get_matching_stats."""

    def test(self):
        mock_stats1 = MagicMock(spec=ht.events.stats.HoudiniEventStats)
        type(mock_stats1).tags = PropertyMock(return_value=["bar", "foo"])

        mock_stats2 = MagicMock(spec=ht.events.stats.HoudiniEventStats)
        type(mock_stats2).tags = PropertyMock(return_value=["bar"])

        result = ht.events.stats._get_matching_stats([mock_stats1, mock_stats2], ["foo"])

        self.assertEqual(result, (mock_stats1,))


class Test_get_event_stats(unittest.TestCase):
    """Test ht.events.stats.get_event_stats."""

    @patch("ht.events.stats._get_matching_stats")
    def test_none(self, mock_matching):
        mock_stats = {}

        with patch.dict(ht.events.stats._StatsMeta._instances, mock_stats, clear=True):
            result = ht.events.stats.get_event_stats()

            self.assertEqual(result, ())

    @patch("ht.events.stats._get_matching_stats")
    def test(self, mock_matching):
        mock_stat = MagicMock(spec=ht.events.stats.HoudiniEventStats)
        mock_stats = {ht.events.stats.HoudiniEventStats: {"foo": mock_stat}}

        with patch.dict(ht.events.stats._StatsMeta._instances, mock_stats, clear=True):
            result = ht.events.stats.get_event_stats()

            self.assertEqual(result, (mock_stat, ))

    @patch("ht.events.stats._get_matching_stats")
    def test_filtered(self, mock_matching):
        mock_stat = MagicMock(spec=ht.events.stats.HoudiniEventStats)
        mock_stats = {ht.events.stats.HoudiniEventStats: {"foo": mock_stat}}

        with patch.dict(ht.events.stats._StatsMeta._instances, mock_stats, clear=True):
            result = ht.events.stats.get_event_stats(["foo"])

            self.assertEqual(result, mock_matching.return_value)

            mock_matching.assert_called_with([mock_stat], ["foo"])


class Test_get_item_stats(unittest.TestCase):
    """Test ht.events.stats.get_item_stats."""

    @patch("ht.events.stats._get_matching_stats")
    def test_none(self, mock_matching):
        mock_stats = {}

        with patch.dict(ht.events.stats._StatsMeta._instances, mock_stats, clear=True):
            result = ht.events.stats.get_item_stats()

            self.assertEqual(result, ())

    @patch("ht.events.stats._get_matching_stats")
    def test(self, mock_matching):
        mock_stat = MagicMock(spec=ht.events.stats.HoudiniEventItemStats)
        mock_stats = {ht.events.stats.HoudiniEventItemStats: {"foo": mock_stat}}

        with patch.dict(ht.events.stats._StatsMeta._instances, mock_stats, clear=True):
            result = ht.events.stats.get_item_stats()

            self.assertEqual(result, (mock_stat, ))

    @patch("ht.events.stats._get_matching_stats")
    def test_filtered(self, mock_matching):
        mock_stat = MagicMock(spec=ht.events.stats.HoudiniEventItemStats)
        mock_stats = {ht.events.stats.HoudiniEventItemStats: {"foo": mock_stat}}

        with patch.dict(ht.events.stats._StatsMeta._instances, mock_stats, clear=True):
            result = ht.events.stats.get_item_stats(["foo"])

            self.assertEqual(result, mock_matching.return_value)

            mock_matching.assert_called_with([mock_stat], ["foo"])

# =============================================================================

if __name__ == '__main__':
    unittest.main()
