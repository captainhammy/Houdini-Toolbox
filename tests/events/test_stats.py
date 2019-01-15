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
        mock_name = MagicMock(spec=str)
        inst = self._Tester(mock_name)

        self.assertEqual(
            ht.events.stats._StatsMeta._instances,
            {self._Tester: {mock_name: inst}}
        )

    def test_existing_default_args(self):
        mock_name = MagicMock(spec=str)

        inst1 = self._Tester(mock_name)
        inst2 = self._Tester(mock_name)

        self.assertTrue(inst1 is inst2)

    def test_existing_tags_positional(self):
        mock_name = MagicMock(spec=str)

        mock_tag1 = MagicMock(spec=str)
        mock_tag2 = MagicMock(spec=str)

        inst1 = self._Tester(mock_name, [mock_tag1])
        inst2 = self._Tester(mock_name, [mock_tag2])

        self.assertEqual(inst1._tags, [mock_tag1, mock_tag2])
        self.assertTrue(inst1 is inst2)

    def test_existing_tags_passed(self):
        mock_name = MagicMock(spec=str)

        mock_tag1 = MagicMock(spec=str)
        mock_tag2 = MagicMock(spec=str)

        inst1 = self._Tester(mock_name, tags=[mock_tag1])
        inst2 = self._Tester(mock_name, tags=[mock_tag2])

        self.assertEqual(inst1._tags, [mock_tag1, mock_tag2])
        self.assertTrue(inst1 is inst2)

    def test_existing_tags_avoid_duplicates(self):
        mock_name = MagicMock(spec=str)

        mock_tag = MagicMock(spec=str)

        inst1 = self._Tester(mock_name, tags=[mock_tag])
        inst2 = self._Tester(mock_name, tags=[mock_tag])

        self.assertEqual(inst1._tags, [mock_tag])
        self.assertTrue(inst1 is inst2)

    def test_existing_post_report_positional(self):
        mock_name = MagicMock(spec=str)

        inst1 = self._Tester(mock_name, None, False)
        inst2 = self._Tester(mock_name, None, True)

        self.assertTrue(inst1._post_report)
        self.assertTrue(inst1 is inst2)

    def test_existing_post_report_passed(self):
        mock_name = MagicMock(spec=str)

        inst1 = self._Tester(mock_name, post_report=False)
        inst2 = self._Tester(mock_name, post_report=True)

        self.assertTrue(inst1._post_report)
        self.assertTrue(inst1 is inst2)

    def test_existing_post_report_passed_keep_existing(self):
        mock_name = MagicMock(spec=str)

        inst1 = self._Tester(mock_name, post_report=True)
        inst2 = self._Tester(mock_name, post_report=False)

        self.assertTrue(inst1._post_report)
        self.assertTrue(inst1 is inst2)


class Test_HoudiniEventStats(unittest.TestCase):
    """Test ht.events.stats.HoudiniEventStats class."""

    def test___init___no_tags(self):
        mock_name = MagicMock(spec=str)

        stats = ht.events.stats.HoudiniEventStats(mock_name, post_report=True)

        self.assertEqual(stats._last_run_time, 0)
        self.assertEqual(stats._last_started, 0)
        self.assertEqual(stats._name, mock_name)
        self.assertTrue(stats._post_report)
        self.assertEqual(stats._run_count, 0)
        self.assertEqual(stats._total_time, 0)

        self.assertEqual(stats._tags, [])

    def test___init___tags(self):
        mock_name = MagicMock(spec=str)
        mock_tags = MagicMock(spec=list)
        stats = ht.events.stats.HoudiniEventStats(mock_name, tags=mock_tags, post_report=True)

        self.assertEqual(stats._last_run_time, 0)
        self.assertEqual(stats._last_started, 0)
        self.assertEqual(stats._name, mock_name)
        self.assertTrue(stats._post_report)
        self.assertEqual(stats._run_count, 0)
        self.assertEqual(stats._total_time, 0)
        self.assertEqual(stats._tags, mock_tags)

    @patch.object(ht.events.stats.HoudiniEventStats, "total_time", new_callable=PropertyMock(return_value=22.123456))
    @patch.object(ht.events.stats.HoudiniEventStats, "run_count", new_callable=PropertyMock(return_value=3))
    @patch.object(ht.events.stats.HoudiniEventStats, "name", new_callable=PropertyMock(return_value="name"))
    @patch.object(ht.events.stats.HoudiniEventStats, "__init__", lambda x, y: None)
    def test___repr__(self, mock_name, mock_count, mock_total):
        stats = ht.events.stats.HoudiniEventStats(None)

        result = stats.__repr__()

        self.assertEqual(result, "<HoudiniEventStats: name run_count=3 total_time=22.123>")

    # Properties

    @patch.object(ht.events.stats.HoudiniEventStats, "__init__", lambda x, y: None)
    def test_last_run_time(self):
        mock_value = MagicMock(spec=float)

        stats = ht.events.stats.HoudiniEventStats(None)

        stats._last_run_time = mock_value
        self.assertEqual(stats.last_run_time, mock_value)

        with self.assertRaises(AttributeError):
            stats.last_run_time = mock_value

    @patch.object(ht.events.stats.HoudiniEventStats, "__init__", lambda x, y: None)
    def test_name(self):
        mock_value = MagicMock(spec=str)

        stats = ht.events.stats.HoudiniEventStats(None)

        stats._name = mock_value
        self.assertEqual(stats.name, mock_value)

        with self.assertRaises(AttributeError):
            stats.name = mock_value

    @patch.object(ht.events.stats.HoudiniEventStats, "__init__", lambda x, y: None)
    def test_post_report(self):
        mock_value = MagicMock(spec=bool)

        stats = ht.events.stats.HoudiniEventStats(None)

        stats._post_report = mock_value
        self.assertEqual(stats.post_report, mock_value)

        with self.assertRaises(AttributeError):
            stats.post_report = mock_value

    @patch.object(ht.events.stats.HoudiniEventStats, "__init__", lambda x, y: None)
    def test_run_count(self):
        mock_value = MagicMock(spec=int)

        stats = ht.events.stats.HoudiniEventStats(None)

        stats._run_count = mock_value
        self.assertEqual(stats.run_count, mock_value)

        with self.assertRaises(AttributeError):
            stats.run_count = mock_value

    @patch.object(ht.events.stats.HoudiniEventStats, "__init__", lambda x, y: None)
    def test_tags(self):
        mock_value = MagicMock(spec=list)

        stats = ht.events.stats.HoudiniEventStats(None)

        stats._tags = mock_value
        self.assertEqual(stats.tags, mock_value)

        with self.assertRaises(AttributeError):
            stats.tags = mock_value

    @patch.object(ht.events.stats.HoudiniEventStats, "__init__", lambda x, y: None)
    def test_total_time(self):
        mock_value = MagicMock(spec=float)

        stats = ht.events.stats.HoudiniEventStats(None)

        stats._total_time = mock_value
        self.assertEqual(stats.total_time, mock_value)

        with self.assertRaises(AttributeError):
            stats.total_time = mock_value

    # Methods

    @patch("time.time")
    @patch.object(ht.events.stats.HoudiniEventStats, "__init__", lambda x, y: None)
    def test_enter(self, mock_time):
        stats = ht.events.stats.HoudiniEventStats(None)

        stats.__enter__()

        self.assertEqual(stats._last_started, mock_time.return_value)

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

    @patch("ht.events.stats.logger")
    @patch.object(ht.events.stats.HoudiniEventStats, "__init__", lambda x, y: None)
    def test_print_report(self, mock_logger):
        stats = ht.events.stats.HoudiniEventStats(None)

        stats._last_run_time = 3.123456
        stats._run_count = 2
        stats._name = "name"

        stats.print_report()

        self.assertEqual(mock_logger.info.call_count, 3)

    @patch.object(ht.events.stats.HoudiniEventStats, "__init__", lambda x, y: None)
    def test_reset(self):
        stats = ht.events.stats.HoudiniEventStats(None)

        stats._last_run_time = MagicMock(spec=float)
        stats._run_count = MagicMock(spec=int)
        stats._total_time = MagicMock(spec=float)

        stats.reset()

        self.assertEqual(stats._last_run_time, 0)
        self.assertEqual(stats._run_count, 0)
        self.assertEqual(stats._total_time, 0)

# =============================================================================

class Test_HoudiniEventItemStats(unittest.TestCase):
    """Test ht.events.stats.HoudiniEventItemStats class."""

    @patch.object(ht.events.stats.HoudiniEventStats, "__init__")
    def test___init__(self, mock_super_init):
        mock_name = MagicMock(spec=str)
        mock_tags = MagicMock(spec=list)

        stats = ht.events.stats.HoudiniEventItemStats(mock_name, mock_tags, True)

        mock_super_init.assert_called_with(mock_name, tags=mock_tags, post_report=True)
        self.assertTrue(isinstance(stats._item_stats, OrderedDict))

    # Properties

    @patch.object(ht.events.stats.HoudiniEventItemStats, "__init__", lambda x, y: None)
    def test_item_stats(self):
        mock_value = MagicMock(spec=OrderedDict)

        stats = ht.events.stats.HoudiniEventItemStats(None)

        stats._item_stats = mock_value
        self.assertEqual(stats.item_stats, mock_value)

    # Methods

    @patch("ht.events.stats.logger")
    @patch.object(ht.events.stats.HoudiniEventItemStats, "__init__", lambda x, y: None)
    def test_print_report(self, mock_logger):
        item_stats = OrderedDict()
        item_stats["stat name"] = 123.456789

        stats = ht.events.stats.HoudiniEventItemStats(None)

        stats._run_count = 2
        stats._name = "name"
        stats._item_stats = item_stats
        stats._last_run_time = 456.12345678

        stats.print_report()

        self.assertEqual(mock_logger.info.call_count, 5)

    @patch.object(ht.events.stats.HoudiniEventItemStats, "item_stats", new_callable=PropertyMock)
    @patch.object(ht.events.stats.HoudiniEventStats, "reset")
    @patch.object(ht.events.stats.HoudiniEventItemStats, "__init__", lambda x, y: None)
    def test_reset(self, mock_super_reset, mock_item_stats):
        stats = ht.events.stats.HoudiniEventItemStats(None)
        stats.reset()

        mock_super_reset.assert_called_once()
        mock_item_stats.return_value.clear.assert_called_once()

    @patch.object(ht.events.stats.HoudiniEventItemStats, "item_stats", new_callable=PropertyMock)
    @patch("time.time")
    @patch.object(ht.events.stats.HoudiniEventItemStats, "__init__", lambda x, y: None)
    def test_time_function(self, mock_time, mock_item_stats):
        mock_time.side_effect = (1, 2, 5, 8)

        mock_func1 = MagicMock()
        mock_func1.__name__ = MagicMock(spec=str)

        mock_func2 = MagicMock()
        mock_func2.__name__ = MagicMock(spec=str)

        odict = OrderedDict()
        mock_item_stats.return_value = odict
        stats = ht.events.stats.HoudiniEventItemStats(None)

        with stats.time_function(mock_func1):
            pass

        with stats.time_function(mock_func2):
            pass

        expected = OrderedDict()
        expected[mock_func1.__name__] = 1
        expected[mock_func2.__name__] = 3

        self.assertEqual(stats.item_stats, expected)

    @patch.object(ht.events.stats.HoudiniEventItemStats, "item_stats", new_callable=PropertyMock)
    @patch("time.time")
    @patch.object(ht.events.stats.HoudiniEventItemStats, "__init__", lambda x, y: None)
    def test_time_function_existing(self, mock_time, mock_item_stats):
        mock_time.side_effect = (1, 2, 5, 8)

        mock_func1 = MagicMock()
        mock_func1.__name__ = MagicMock(spec=str)

        mock_func2 = MagicMock()
        mock_func2.__name__ = MagicMock(spec=str)

        odict = OrderedDict()
        odict[mock_func1.__name__] = 1
        mock_item_stats.return_value = odict

        stats = ht.events.stats.HoudiniEventItemStats(None)

        with stats.time_function(mock_func1):
            pass

        with stats.time_function(mock_func2):
            pass

        expected = OrderedDict()
        expected[mock_func1.__name__] = 2
        expected[mock_func2.__name__] = 3

        self.assertEqual(stats.item_stats, expected)


class Test__get_matching_stats(unittest.TestCase):
    """Test ht.events.stats._get_matching_stats."""

    def test(self):
        mock_tag1 = MagicMock(spec=str)
        mock_tag2 = MagicMock(spec=str)

        mock_stats1 = MagicMock(spec=ht.events.stats.HoudiniEventStats)
        type(mock_stats1).tags = PropertyMock(return_value=[mock_tag1, mock_tag2])

        mock_stats2 = MagicMock(spec=ht.events.stats.HoudiniEventStats)
        type(mock_stats2).tags = PropertyMock(return_value=[mock_tag1])

        result = ht.events.stats._get_matching_stats([mock_stats1, mock_stats2], [mock_tag2])

        self.assertEqual(result, (mock_stats1,))


class Test_get_event_stats(unittest.TestCase):
    """Test ht.events.stats.get_event_stats."""

    @patch("ht.events.stats._get_matching_stats")
    @patch.object(ht.events.stats._StatsMeta, "_instances", new_callable=PropertyMock)
    def test_none(self, mock_instances, mock_matching):
        mock_instances.return_value = {}

        result = ht.events.stats.get_event_stats()

        self.assertEqual(result, ())

        mock_matching.assert_not_called()

    @patch("ht.events.stats._get_matching_stats")
    @patch.object(ht.events.stats._StatsMeta, "_instances", new_callable=PropertyMock)
    def test(self, mock_instances, mock_matching):
        mock_tag = MagicMock(spec=str)

        mock_stats = MagicMock(spec=ht.events.stats.HoudiniEventStats)

        mock_instances.return_value = {ht.events.stats.HoudiniEventStats: {mock_tag: mock_stats}}

        result = ht.events.stats.get_event_stats()

        self.assertEqual(result, (mock_stats, ))

        mock_matching.assert_not_called()

    @patch("ht.events.stats._get_matching_stats")
    @patch.object(ht.events.stats._StatsMeta, "_instances", new_callable=PropertyMock)
    def test_filtered(self, mock_instances, mock_matching):
        mock_tag = MagicMock(spec=str)

        mock_stats = MagicMock(spec=ht.events.stats.HoudiniEventStats)

        mock_instances.return_value = {ht.events.stats.HoudiniEventStats: {mock_tag: mock_stats}}

        result = ht.events.stats.get_event_stats([mock_tag])

        self.assertEqual(result, mock_matching.return_value)

        mock_matching.assert_called_with([mock_stats], [mock_tag])


class Test_get_item_stats(unittest.TestCase):
    """Test ht.events.stats.get_item_stats."""

    @patch("ht.events.stats._get_matching_stats")
    @patch.object(ht.events.stats._StatsMeta, "_instances", new_callable=PropertyMock)
    def test_none(self, mock_instances, mock_matching):
        mock_instances.return_value = {}

        result = ht.events.stats.get_item_stats()

        self.assertEqual(result, ())

        mock_matching.assert_not_called()

    @patch("ht.events.stats._get_matching_stats")
    @patch.object(ht.events.stats._StatsMeta, "_instances", new_callable=PropertyMock)
    def test(self, mock_instances, mock_matching):
        mock_tag = MagicMock(spec=str)

        mock_stats = MagicMock(spec=ht.events.stats.HoudiniEventItemStats)

        mock_instances.return_value = {ht.events.stats.HoudiniEventItemStats: {mock_tag: mock_stats}}

        result = ht.events.stats.get_item_stats()

        self.assertEqual(result, (mock_stats, ))

        mock_matching.assert_not_called()

    @patch("ht.events.stats._get_matching_stats")
    @patch.object(ht.events.stats._StatsMeta, "_instances", new_callable=PropertyMock)
    def test_filtered(self, mock_instances, mock_matching):
        mock_tag = MagicMock(spec=str)

        mock_stats = MagicMock(spec=ht.events.stats.HoudiniEventItemStats)
        mock_instances.return_value = {ht.events.stats.HoudiniEventItemStats: {mock_tag: mock_stats}}

        result = ht.events.stats.get_item_stats([mock_tag])

        self.assertEqual(result, mock_matching.return_value)

        mock_matching.assert_called_with([mock_stats], [mock_tag])

# =============================================================================

if __name__ == '__main__':
    unittest.main()
