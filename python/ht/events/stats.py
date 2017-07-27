"""This module contains classes for event statistics."""

# Python Imports
from collections import OrderedDict
from contextlib import contextmanager
import time

# =============================================================================
# CLASSES
# =============================================================================


class EventStats(object):
    """The base statistics class."""

    def __init__(self, name, post_report=False):
        self._last_run_time = 0
        self._last_started = 0
        self._name = name
        self._post_report = post_report
        self._run_count = 0
        self._total_time = 0

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
            self.printReport()

    @property
    def last_run_time(self):
        return self._last_run_time

    @property
    def name(self):
        return self._name

    @property
    def post_report(self):
        return self._post_report

    @property
    def run_count(self):
        return self._run_count

    @property
    def total_time(self):
        return self._total_time

    def printReport(self):
        print "Event name: {}".format(self.name)
        print "\tRun Count: {}".format(self.run_count)
        print "\tRun Time: {}".format(self.last_run_time)

    def reset(self):
        self._last_run_time = 0
        self._run_count = 0
        self._total_time = 0


class EventBlockStats(EventStats):

    def __init__(self, name, post_report=False):
        super(EventBlockStats, self).__init__(name, post_report=post_report)

        self._child_stats = OrderedDict()

    @property
    def child_stats(self):
        return self._child_stats

    @property
    def child_stats(self):
        return self._child_stats

    def printReport(self):
        print "Event: {}".format(self.name)
        print "\tMethods:"
        for child_name, child_time in self.child_stats.iteritems():
            print "\t\t{}: {:0.4f}".format(child_name, child_time)

        print "\tRun Count: {}".format(self.run_count)
        print "\tRun Time: {:0.4f}".format(self.last_run_time)

    def reset(self):
        super(EventBlockStats, self).reset()

        self.child_stats.clear()

    @contextmanager
    def time_child(self, name):
        start = time.time()

        yield

        end = time.time()

        if name not in self.child_stats:
            self.child_stats[name] = 0

        self.child_stats[name] += end - start
