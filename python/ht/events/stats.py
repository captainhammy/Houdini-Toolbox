"""This module contains classes for event statistics."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
from collections import OrderedDict
from contextlib import contextmanager
import logging
import time

logger = logging.getLogger(__name__)


# =============================================================================
# CLASSES
# =============================================================================

class _StatsMeta(type):
    """Metaclass for HoudiniEventStats objects.

    This class lets us share instances according to the stats name.

    """

    # Dict of stats classes and their instances.
    _instances = {}

    def __call__(cls, *args, **kwargs):
        # Key off the name.
        key = args[0]

        # Get any instances of the target class.
        inst_dict = cls._instances.setdefault(cls, {})

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


class HoudiniEventStats(object):
    """The base statistics class.

    :param name: Name for the stats.
    :type name: str
    :param tags: Optional stats tags.
    :type tags: list(str)
    :param post_report: Print a report after running.
    :type post_report: bool
    :return:

    """

    __metaclass__ = _StatsMeta

    def __init__(self, name, tags=None, post_report=False):
        self._last_run_time = 0
        self._last_started = 0
        self._name = name
        self._post_report = post_report
        self._run_count = 0
        self._total_time = 0

        if tags is None:
            tags = []

        self._tags = tags

    def __repr__(self):
        return "<{}: {} run_count={} total_time={:0.3f}>".format(
            self.__class__.__name__,
            self.name,
            self.run_count,
            self.total_time,
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

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def last_run_time(self):
        """float: The run time of the most recent run."""
        return self._last_run_time

    @property
    def name(self):
        """str: The stats name."""
        return self._name

    @property
    def post_report(self):
        """bool: Whether or not to print the report at exit."""
        return self._post_report

    @property
    def run_count(self):
        """int: The number of times the stats have been run."""
        return self._run_count

    @property
    def tags(self):
        """list(str): Tags associated with the stats."""
        return self._tags

    @property
    def total_time(self):
        """float: The total time for all stats runs."""
        return self._total_time

    # =========================================================================
    # METHODS
    # =========================================================================

    def print_report(self):
        """Print (log) a stats report for the last run.

        :return:

        """
        logger.info("Event name: %s", self.name)
        logger.info("\tRun Count: %s", self.run_count)
        logger.info("\tRun Time: %s", self.last_run_time)

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
    :type name: str
    :param tags: Optional stats tags.
    :type tags: list(str)
    :param post_report: Print a report after running.
    :type post_report: bool
    :return:

    """

    def __init__(self, name, tags=None, post_report=False):
        super(HoudiniEventItemStats, self).__init__(name, tags=tags, post_report=post_report)

        self._item_stats = OrderedDict()

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def item_stats(self):
        """OrderedDict: Item statistics."""
        return self._item_stats

    # =========================================================================
    # METHODS
    # =========================================================================

    def print_report(self):
        """Print (log) a stats report for the last run.

        :return:

        """
        logger.info("Item: %s", self.name)
        logger.info("\tRun Count: %s", self.run_count)
        logger.info("\tCallables:")

        for item_name, item_time in self.item_stats.iteritems():
            logger.info("\t\t%s: %0.4f", item_name, item_time)

        logger.info("\tRun Time: %0.4f", self.last_run_time)

    def reset(self):
        """Reset all counts.

        :return:

        """
        super(HoudiniEventItemStats, self).reset()

        self.item_stats.clear()

    @contextmanager
    def time_function(self, func):
        """Time a function.

        :param func: Function.
        :type func: callable
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

def _get_matching_stats(stats, tags):
    """Filter a list of stats for ones which match the tags.

    :param stats: An list of stats objects to search.
    :type stats: [HoudiniEventStats]
    :param tags: The list of tag values to filter by.
    :type tags: [str]
    :return: A tuple of stat objects.
    :rtype: tuple(HoudiniEventStats)

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

def get_event_stats(matching_tags=None):
    """Get a list of event item related stats, optionally filtered by tag.

    :param matching_tags: An optional list of tag values to filter by.
    :type matching_tags: [str]
    :return: A tuple of stat objects.
    :rtype: tuple(HoudiniEventStats)

    """
    all_stats = _StatsMeta._instances.get(HoudiniEventStats, {}).values()

    if matching_tags is None:
        return tuple(all_stats)

    return _get_matching_stats(all_stats, matching_tags)


def get_item_stats(matching_tags=None):
    """Get a list of event related stats, optionally filtered by tag.

    :param matching_tags: An optional list of tag values to filter by.
    :type matching_tags: [str]
    :return: A tuple of stat objects.
    :rtype: tuple(HoudiniEventItemStats)

    """
    all_stats = _StatsMeta._instances.get(HoudiniEventItemStats, {}).values()

    if matching_tags is None:
        return tuple(all_stats)

    return _get_matching_stats(all_stats, matching_tags)
