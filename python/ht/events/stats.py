"""This module contains classes for event statistics."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
from __future__ import annotations
from collections import OrderedDict
from contextlib import contextmanager
import logging
import time
from typing import Callable, List, Optional, Tuple

_logger = logging.getLogger(__name__)


# =============================================================================
# CLASSES
# =============================================================================


class _StatsMeta(type):
    """Metaclass for HoudiniEventStats objects.

    This class lets us share instances according to the stats name.

    """

    # Dict of stats classes and their instances.
    INSTANCES = {}

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __call__(cls, *args, **kwargs):
        # pylint: disable=protected-access
        # Key off the name.
        key = args[0]

        # Get any instances of the target class.
        inst_dict = cls.INSTANCES.setdefault(cls, {})

        # Create a new class instance because the name has not been used yet.
        if key not in inst_dict:
            inst = super(_StatsMeta, cls).__call__(*args, **kwargs)
            inst_dict[key] = inst

        # If the instance already exists we want to check the args to make sure
        # that we support adding tags and print settings to the already existing
        # one.
        else:
            inst = inst_dict[key]

            # In the event that the calling code wanted to set tags we should
            # tag the specified tags and add them to the stats list.
            if len(args) > 1 or "tags" in kwargs:
                if len(args) > 1:
                    tags = args[1]

                else:
                    tags = kwargs["tags"]

                if tags is not None:
                    for tag in tags:
                        if tag not in inst._tags:
                            inst._tags.append(tag)

            # In the event the calling code passed post_report=True
            # we should enable the report.
            if len(args) == 3 or "post_report" in kwargs:
                if len(args) == 3:
                    post_report = args[2]

                else:
                    post_report = kwargs["post_report"]

                if post_report:
                    inst._post_report = True

        return inst


class HoudiniEventStats(metaclass=_StatsMeta):
    """The base statistics class.

    :param name: Name for the stats.
    :param tags: Optional stats tags.
    :param post_report: Print a report after running.
    :return:

    """

    def __init__(
        self, name: str, tags: Optional[List[str]] = None, post_report: bool = False
    ):
        self._last_run_time = 0
        self._last_started = 0
        self._name = name
        self._post_report = post_report
        self._run_count = 0
        self._total_time = 0

        if tags is None:
            tags = []

        self._tags = tags

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __repr__(self):
        return "<{}: {} run_count={} total_time={:0.3f}>".format(
            self.__class__.__name__, self.name, self.run_count, self.total_time
        )

    def __enter__(self):
        self._last_started = time.time()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end = time.time()

        self._last_run_time = end - self._last_started
        self._total_time += self._last_run_time

        self._run_count += 1

        if self.post_report:
            self.print_report()

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def last_run_time(self) -> float:
        """The run time of the most recent run."""
        return self._last_run_time

    @property
    def name(self) -> str:
        """The stats name."""
        return self._name

    @property
    def post_report(self) -> bool:
        """Whether or not to print the report at exit."""
        return self._post_report

    @property
    def run_count(self) -> int:
        """The number of times the stats have been run."""
        return self._run_count

    @property
    def tags(self) -> List[str]:
        """Tags associated with the stats."""
        return self._tags

    @property
    def total_time(self) -> float:
        """The total time for all stats runs."""
        return self._total_time

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def print_report(self):
        """Print (log) a stats report for the last run.

        :return:

        """
        _logger.info("Event name: %s", self.name)
        _logger.info("\tRun Count: %s", self.run_count)
        _logger.info("\tRun Time: %s", self.last_run_time)

    def reset(self):
        """Reset all counts.

        :return:

        """
        self._last_run_time = 0
        self._run_count = 0
        self._total_time = 0


class HoudiniEventItemStats(HoudiniEventStats):
    """Stats for Items.

    :param name: Name for the stats.
    :param tags: Optional stats tags.
    :param post_report: Print a report after running.
    :return:

    """

    def __init__(
        self, name: str, tags: Optional[List[str]] = None, post_report: bool = False
    ):
        super().__init__(name, tags=tags, post_report=post_report)

        self._item_stats = OrderedDict()

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def item_stats(self) -> OrderedDict:
        """Item statistics."""
        return self._item_stats

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def print_report(self):
        """Print (log) a stats report for the last run.

        :return:

        """
        _logger.info("Item: %s", self.name)
        _logger.info("\tRun Count: %s", self.run_count)
        _logger.info("\tCallables:")

        for item_name, item_time in list(self.item_stats.items()):
            _logger.info("\t\t%s: %0.4f", item_name, item_time)

        _logger.info("\tRun Time: %0.4f", self.last_run_time)

    def reset(self):
        """Reset all counts.

        :return:

        """
        super().reset()

        self.item_stats.clear()

    @contextmanager
    def time_function(self, func: Callable):
        """Time a function.

        :param func: Function.
        :return:

        """
        name = func.__name__
        start = time.time()

        yield

        end = time.time()

        if name not in self.item_stats:
            self.item_stats[name] = 0

        self.item_stats[name] += end - start


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _get_matching_stats(
    stats: List[HoudiniEventStats], tags: List[str]
) -> Tuple[HoudiniEventStats]:
    """Filter a list of stats for ones which match the tags.

    :param stats: An list of stats objects to search.
    :param tags: The list of tag values to filter by.
    :return: A tuple of stat objects.

    """
    matching_stats = []

    tag_set = set(tags)

    for stat in stats:
        stat_tags = set(stat.tags)

        if tag_set.intersection(stat_tags):
            matching_stats.append(stat)

    return tuple(matching_stats)


# =============================================================================
# FUNCTIONS
# =============================================================================


def get_event_stats(matching_tags: Optional[str] = None) -> Tuple[HoudiniEventStats]:
    """Get a list of event item related stats, optionally filtered by tag.

    :param matching_tags: An optional list of tag values to filter by.
    :return: A tuple of stat objects.

    """
    all_stats = list(
        _StatsMeta.INSTANCES.get(  # pylint: disable=protected-access
            HoudiniEventStats, {}
        ).values()
    )

    if matching_tags is None:
        return tuple(all_stats)

    return _get_matching_stats(all_stats, matching_tags)


def get_item_stats(matching_tags: Optional[str] = None) -> Tuple[HoudiniEventItemStats]:
    """Get a list of event related stats, optionally filtered by tag.

    :param matching_tags: An optional list of tag values to filter by.
    :return: A tuple of stat objects.

    """
    all_stats = list(
        _StatsMeta.INSTANCES.get(  # pylint: disable=protected-access
            HoudiniEventItemStats, {}
        ).values()
    )

    if matching_tags is None:
        return tuple(all_stats)

    return _get_matching_stats(all_stats, matching_tags)
