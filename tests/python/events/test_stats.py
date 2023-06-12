"""Tests for houdini_toolbox.events.stats module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
from collections import OrderedDict

# Third Party
import pytest

# Houdini Toolbox
import houdini_toolbox.events.stats

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def init_item_stats(mocker):
    """Fixture to initialize a stats object."""
    mocker.patch.object(
        houdini_toolbox.events.stats.HoudiniEventItemStats,
        "__init__",
        lambda x, y: None,
    )

    def _create():
        return houdini_toolbox.events.stats.HoudiniEventItemStats(None)

    return _create


@pytest.fixture
def init_stats(mocker):
    """Fixture to initialize a stats object."""
    mocker.patch.object(
        houdini_toolbox.events.stats.HoudiniEventStats, "__init__", lambda x, y: None
    )

    def _create():
        return houdini_toolbox.events.stats.HoudiniEventStats(None)

    return _create


@pytest.fixture
def reset_meta_instances():
    """Dummy fixture to clear the StatsMeta instance dict after test completion."""
    yield

    # Reset the instances.
    houdini_toolbox.events.stats._StatsMeta.INSTANCES.clear()


# =============================================================================
# TESTS
# =============================================================================


class Test__StatsMeta:
    """Test houdini_toolbox.events.stats._StatsMeta metaclass."""

    def test_new(self, reset_meta_instances, mocker):
        """Test when instantiating a new instance."""
        # Clear instances since there might be some already from other tests.
        houdini_toolbox.events.stats._StatsMeta.INSTANCES.clear()

        mock_name = mocker.MagicMock(spec=str)
        inst = houdini_toolbox.events.stats.HoudiniEventStats(mock_name)

        assert houdini_toolbox.events.stats._StatsMeta.INSTANCES == {
            houdini_toolbox.events.stats.HoudiniEventStats: {mock_name: inst}
        }

    def test_existing_default_args(self, reset_meta_instances, mocker):
        """Test reusing an existing instance of default args."""
        mock_name = mocker.MagicMock(spec=str)

        inst1 = houdini_toolbox.events.stats.HoudiniEventStats(mock_name)
        inst2 = houdini_toolbox.events.stats.HoudiniEventStats(mock_name)

        assert inst1 is inst2

    def test_existing_tags_positional(self, reset_meta_instances, mocker):
        """Test reusing an existing instance via positional args."""
        mock_name = mocker.MagicMock(spec=str)

        mock_tag1 = mocker.MagicMock(spec=str)
        mock_tag2 = mocker.MagicMock(spec=str)

        inst1 = houdini_toolbox.events.stats.HoudiniEventStats(mock_name, [mock_tag1])
        inst2 = houdini_toolbox.events.stats.HoudiniEventStats(mock_name, [mock_tag2])

        assert inst1._tags == [mock_tag1, mock_tag2]
        assert inst1 is inst2

    def test_existing_tags_passed(self, reset_meta_instances, mocker):
        """Test reusing an existing instance passing tags."""
        mock_name = mocker.MagicMock(spec=str)

        mock_tag1 = mocker.MagicMock(spec=str)
        mock_tag2 = mocker.MagicMock(spec=str)

        inst1 = houdini_toolbox.events.stats.HoudiniEventStats(
            mock_name, tags=[mock_tag1]
        )
        inst2 = houdini_toolbox.events.stats.HoudiniEventStats(
            mock_name, tags=[mock_tag2]
        )

        assert inst1._tags == [mock_tag1, mock_tag2]
        assert inst1 is inst2

    def test_existing_tags_avoid_duplicates(self, reset_meta_instances, mocker):
        """Test reusing an existing instance based on tags."""
        mock_name = mocker.MagicMock(spec=str)

        mock_tag = mocker.MagicMock(spec=str)

        inst1 = houdini_toolbox.events.stats.HoudiniEventStats(
            mock_name, tags=[mock_tag]
        )
        inst2 = houdini_toolbox.events.stats.HoudiniEventStats(
            mock_name, tags=[mock_tag]
        )

        assert inst1._tags == [mock_tag]
        assert inst1 is inst2

    def test_existing_post_report_positional(self, reset_meta_instances, mocker):
        """Test reusing an existing instance based on a post-report positionally passed."""
        mock_name = mocker.MagicMock(spec=str)

        inst1 = houdini_toolbox.events.stats.HoudiniEventStats(mock_name, None, False)
        inst2 = houdini_toolbox.events.stats.HoudiniEventStats(mock_name, None, True)

        assert inst1._post_report
        assert inst1 is inst2

    def test_existing_post_report_passed(self, reset_meta_instances, mocker):
        """Test reusing an existing instance based on a post-report explicitly passed."""
        mock_name = mocker.MagicMock(spec=str)

        inst1 = houdini_toolbox.events.stats.HoudiniEventStats(
            mock_name, post_report=False
        )
        inst2 = houdini_toolbox.events.stats.HoudiniEventStats(
            mock_name, post_report=True
        )

        assert inst1._post_report
        assert inst1 is inst2

    def test_existing_post_report_passed_keep_existing(
        self, reset_meta_instances, mocker
    ):
        """Test reusing an existing instance based on a post-report explicitly passed."""
        mock_name = mocker.MagicMock(spec=str)

        inst1 = houdini_toolbox.events.stats.HoudiniEventStats(
            mock_name, post_report=True
        )
        inst2 = houdini_toolbox.events.stats.HoudiniEventStats(
            mock_name, post_report=False
        )

        assert inst1._post_report
        assert inst1 is inst2


class Test_HoudiniEventStats:
    """Test houdini_toolbox.events.stats.HoudiniEventStats class."""

    def test___init___no_tags(self, mocker):
        """Test object initialization with no tags."""
        mock_name = mocker.MagicMock(spec=str)

        stats = houdini_toolbox.events.stats.HoudiniEventStats(
            mock_name, post_report=True
        )

        assert stats._last_run_time == 0
        assert stats._last_started == 0
        assert stats._name == mock_name
        assert stats._post_report
        assert stats._run_count == 0
        assert stats._total_time == 0

        assert stats._tags == []

    def test___init___tags(self, mocker):
        """Test object initialization with tags."""
        mock_name = mocker.MagicMock(spec=str)
        mock_tags = mocker.MagicMock(spec=list)
        stats = houdini_toolbox.events.stats.HoudiniEventStats(
            mock_name, tags=mock_tags, post_report=True
        )

        assert stats._last_run_time == 0
        assert stats._last_started == 0
        assert stats._name == mock_name
        assert stats._post_report
        assert stats._run_count == 0
        assert stats._total_time == 0
        assert stats._tags == mock_tags

    # Properties

    def test_last_run_time(self, init_stats, mocker):
        """Test the 'last_run_time' property."""
        mock_value = mocker.MagicMock(spec=float)

        stats = init_stats()
        stats._last_run_time = mock_value
        assert stats.last_run_time == mock_value

    def test_name(self, init_stats, mocker):
        """Test the 'name' property."""
        mock_value = mocker.MagicMock(spec=str)

        stats = init_stats()
        stats._name = mock_value
        assert stats.name == mock_value

    def test_post_report(self, init_stats, mocker):
        """Test the 'post_report' property."""
        mock_value = mocker.MagicMock(spec=bool)

        stats = init_stats()
        stats._post_report = mock_value
        assert stats.post_report == mock_value

    def test_run_count(self, init_stats, mocker):
        """Test the 'last_run_time' property."""
        mock_value = mocker.MagicMock(spec=int)

        stats = init_stats()
        stats._run_count = mock_value
        assert stats.run_count == mock_value

    def test_tags(self, init_stats, mocker):
        """Test the 'tags' property."""
        mock_value = mocker.MagicMock(spec=list)

        stats = init_stats()
        stats._tags = mock_value
        assert stats.tags == mock_value

    def test_total_time(self, init_stats, mocker):
        """Test the 'total_time' property."""
        mock_value = mocker.MagicMock(spec=float)

        stats = init_stats()
        stats._total_time = mock_value
        assert stats.total_time == mock_value

    # Methods

    def test___enter__(self, init_stats, mocker):
        """Test the __enter__ method."""
        mock_time = mocker.patch("time.time")

        stats = init_stats()

        stats.__enter__()

        assert stats._last_started == mock_time.return_value

    @pytest.mark.parametrize("print_report", [True, False])
    def test___exit___with_report(self, init_stats, mocker, print_report):
        """Test __exit__."""
        mock_time = mocker.patch("time.time")
        mock_print = mocker.patch.object(
            houdini_toolbox.events.stats.HoudiniEventStats, "print_report"
        )

        stats = init_stats()

        stats._post_report = print_report

        mock_run_time = mocker.MagicMock(spec=int)
        mock_time.return_value = mock_run_time

        mock_total_time = mocker.MagicMock(spec=int)
        mock_last_run_time = mocker.MagicMock(spec=int)
        mock_last_started = mocker.MagicMock(spec=int)
        mock_run_count = mocker.MagicMock(spec=int)

        stats._last_run_time = mock_last_run_time
        stats._total_time = mock_total_time
        stats._last_started = mock_last_started
        stats._run_count = mock_run_count

        exc_type = mocker.MagicMock()
        exc_val = mocker.MagicMock()
        exc_tb = mocker.MagicMock()

        stats.__exit__(exc_type, exc_val, exc_tb)

        run_time = mock_run_time - mock_last_started

        assert stats._last_run_time == run_time
        assert stats._total_time == mock_total_time + run_time
        assert stats._run_count == mock_run_count + 1

        if print_report:
            mock_print.assert_called_once()

        else:
            mock_print.assert_not_called()

    def test_print_report(self, init_stats, mocker):
        """Test printing a report."""
        mock_logger = mocker.patch("houdini_toolbox.events.stats._logger")

        stats = init_stats()

        stats._last_run_time = 3.123456
        stats._run_count = 2
        stats._name = "name"

        stats.print_report()

        assert mock_logger.info.call_count == 3

    def test_reset(self, init_stats, mocker):
        """Test resetting internal data."""
        stats = init_stats()

        stats._last_run_time = mocker.MagicMock(spec=float)
        stats._run_count = mocker.MagicMock(spec=int)
        stats._total_time = mocker.MagicMock(spec=float)

        stats.reset()

        assert stats._last_run_time == 0
        assert stats._run_count == 0
        assert stats._total_time == 0


class Test_HoudiniEventItemStats:
    """Test houdini_toolbox.events.stats.HoudiniEventItemStats class."""

    def test___init__(self, mocker):
        """Test object initialization."""
        mock_super_init = mocker.patch.object(
            houdini_toolbox.events.stats.HoudiniEventStats, "__init__"
        )

        mock_name = mocker.MagicMock(spec=str)
        mock_tags = mocker.MagicMock(spec=list)

        stats = houdini_toolbox.events.stats.HoudiniEventItemStats(
            mock_name, mock_tags, True
        )

        mock_super_init.assert_called_with(mock_name, tags=mock_tags, post_report=True)
        assert isinstance(stats._item_stats, OrderedDict)

    # Properties

    def test_item_stats(self, init_item_stats, mocker):
        """Test the 'total_time' property."""
        mock_value = mocker.MagicMock(spec=OrderedDict)

        stats = init_item_stats()

        stats._item_stats = mock_value
        assert stats.item_stats == mock_value

    # Methods

    def test_print_report(self, init_item_stats, mocker):
        """Test printing a report."""
        mock_logger = mocker.patch("houdini_toolbox.events.stats._logger")

        item_stats = OrderedDict()
        item_stats["stat name"] = 123.456789

        stats = init_item_stats()

        stats._run_count = 2
        stats._name = "name"
        stats._item_stats = item_stats
        stats._last_run_time = 456.12345678

        stats.print_report()

        assert mock_logger.info.call_count == 5

    def test_reset(self, init_item_stats, mocker):
        """Test resetting internal data."""
        mock_super_reset = mocker.patch.object(
            houdini_toolbox.events.stats.HoudiniEventStats, "reset"
        )

        mock_item_stats = mocker.patch.object(
            houdini_toolbox.events.stats.HoudiniEventItemStats,
            "item_stats",
            new_callable=mocker.PropertyMock,
        )

        stats = init_item_stats()
        stats.reset()

        mock_super_reset.assert_called_once()
        mock_item_stats.return_value.clear.assert_called_once()

    @pytest.mark.parametrize("has_existing", (False, True))
    def test_time_function(self, init_item_stats, mocker, has_existing):
        """Test timing a function."""
        mock_item_stats = mocker.patch.object(
            houdini_toolbox.events.stats.HoudiniEventItemStats,
            "item_stats",
            new_callable=mocker.PropertyMock,
        )
        mock_time = mocker.patch("time.time")

        mock_start1 = mocker.MagicMock(spec=int)
        mock_start2 = mocker.MagicMock(spec=int)
        mock_end1 = mocker.MagicMock(spec=int)
        mock_end2 = mocker.MagicMock(spec=int)

        mock_time.side_effect = (mock_start1, mock_end1, mock_start2, mock_end2)

        mock_func1 = mocker.MagicMock()
        mock_func1.__name__ = mocker.MagicMock(spec=str)

        mock_func2 = mocker.MagicMock()
        mock_func2.__name__ = mocker.MagicMock(spec=str)

        odict = OrderedDict()

        if has_existing:
            odict[mock_func1.__name__] = 1

        mock_item_stats.return_value = odict

        stats = init_item_stats()

        with stats.time_function(mock_func1):
            pass

        with stats.time_function(mock_func2):
            pass

        expected = OrderedDict()
        expected[mock_func1.__name__] = 0 + (mock_end1 - mock_start1)
        expected[mock_func2.__name__] = 0 + (mock_end2 - mock_start2)

        assert stats.item_stats == expected


def test__get_matching_stats(mocker):
    """Test houdini_toolbox.events.stats._get_matching_stats."""
    mock_tag1 = mocker.MagicMock(spec=str)
    mock_tag2 = mocker.MagicMock(spec=str)

    mock_stats1 = mocker.MagicMock(spec=houdini_toolbox.events.stats.HoudiniEventStats)
    type(mock_stats1).tags = mocker.PropertyMock(return_value=[mock_tag1, mock_tag2])

    mock_stats2 = mocker.MagicMock(spec=houdini_toolbox.events.stats.HoudiniEventStats)
    type(mock_stats2).tags = mocker.PropertyMock(return_value=[mock_tag1])

    result = houdini_toolbox.events.stats._get_matching_stats(
        [mock_stats1, mock_stats2], [mock_tag2]
    )

    assert result == (mock_stats1,)


class Test_get_event_stats:
    """Test houdini_toolbox.events.stats.get_event_stats."""

    def test_none(self, mocker):
        """Test when there are no stat instances."""
        mocker.patch.object(
            houdini_toolbox.events.stats._StatsMeta,
            "INSTANCES",
            new_callable=mocker.PropertyMock(return_value={}),
        )

        mock_matching = mocker.patch("houdini_toolbox.events.stats._get_matching_stats")

        result = houdini_toolbox.events.stats.get_event_stats()

        assert result == ()

        mock_matching.assert_not_called()

    def test_all(self, mocker):
        """Test returning all found stats."""
        mockINSTANCES = mocker.patch.object(
            houdini_toolbox.events.stats._StatsMeta,
            "INSTANCES",
            new_callable=mocker.PropertyMock,
        )
        mock_matching = mocker.patch("houdini_toolbox.events.stats._get_matching_stats")

        mock_tag = mocker.MagicMock(spec=str)

        mock_stats = mocker.MagicMock(
            spec=houdini_toolbox.events.stats.HoudiniEventStats
        )

        mockINSTANCES.return_value = {
            houdini_toolbox.events.stats.HoudiniEventStats: {mock_tag: mock_stats}
        }

        result = houdini_toolbox.events.stats.get_event_stats()

        assert result == (mock_stats,)

        mock_matching.assert_not_called()

    def test_filtered(self, mocker):
        """Test returning a filtered list of stats."""
        mockINSTANCES = mocker.patch.object(
            houdini_toolbox.events.stats._StatsMeta,
            "INSTANCES",
            new_callable=mocker.PropertyMock,
        )
        mock_matching = mocker.patch("houdini_toolbox.events.stats._get_matching_stats")

        mock_tag = mocker.MagicMock(spec=str)

        mock_stats = mocker.MagicMock(
            spec=houdini_toolbox.events.stats.HoudiniEventStats
        )

        mockINSTANCES.return_value = {
            houdini_toolbox.events.stats.HoudiniEventStats: {mock_tag: mock_stats}
        }

        result = houdini_toolbox.events.stats.get_event_stats([mock_tag])

        assert result == mock_matching.return_value

        mock_matching.assert_called_with([mock_stats], [mock_tag])


class Test_get_item_stats:
    """Test houdini_toolbox.events.stats.get_item_stats."""

    def test_none(self, mocker):
        """Test when there are no stat instances."""
        mocker.patch.object(
            houdini_toolbox.events.stats._StatsMeta,
            "INSTANCES",
            new_callable=mocker.PropertyMock(return_value={}),
        )
        mock_matching = mocker.patch("houdini_toolbox.events.stats._get_matching_stats")

        result = houdini_toolbox.events.stats.get_item_stats()

        assert result == ()

        mock_matching.assert_not_called()

    def test_all(self, mocker):
        """Test returning all found stats."""
        mockINSTANCES = mocker.patch.object(
            houdini_toolbox.events.stats._StatsMeta,
            "INSTANCES",
            new_callable=mocker.PropertyMock,
        )
        mock_matching = mocker.patch("houdini_toolbox.events.stats._get_matching_stats")

        mock_tag = mocker.MagicMock(spec=str)

        mock_stats = mocker.MagicMock(
            spec=houdini_toolbox.events.stats.HoudiniEventItemStats
        )

        mockINSTANCES.return_value = {
            houdini_toolbox.events.stats.HoudiniEventItemStats: {mock_tag: mock_stats}
        }

        result = houdini_toolbox.events.stats.get_item_stats()

        assert result == (mock_stats,)

        mock_matching.assert_not_called()

    def test_filtered(self, mocker):
        """Test returning a filtered list of stats."""
        mockINSTANCES = mocker.patch.object(
            houdini_toolbox.events.stats._StatsMeta,
            "INSTANCES",
            new_callable=mocker.PropertyMock,
        )
        mock_matching = mocker.patch("houdini_toolbox.events.stats._get_matching_stats")

        mock_tag = mocker.MagicMock(spec=str)

        mock_stats = mocker.MagicMock(
            spec=houdini_toolbox.events.stats.HoudiniEventItemStats
        )
        mockINSTANCES.return_value = {
            houdini_toolbox.events.stats.HoudiniEventItemStats: {mock_tag: mock_stats}
        }

        result = houdini_toolbox.events.stats.get_item_stats([mock_tag])

        assert result == mock_matching.return_value

        mock_matching.assert_called_with([mock_stats], [mock_tag])
