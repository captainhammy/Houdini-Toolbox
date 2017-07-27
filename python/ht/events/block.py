"""This module contains the base Houdini event class."""

from ht.events.stats import EventBlockStats

# =============================================================================
# CLASSES
# =============================================================================


class HoudiniEventBlock(object):
    """A block of events to run at the same time."""

    _EVENT_NAME = None

    def __init__(self):
        self._data = {}
        self._order = []

        self._stats = EventBlockStats(self.__class__.__name__)

    def __repr__(self):
        return "<HoudiniEventBlock: {}>".format(self.__class__.__name__)

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def data(self):
        """Internal data for storing data that can be shared across event
        functions."""
        return self._data

    @property
    def event_name(self):
        """Internal event map used to register the functions of this event."""
        return self._EVENT_NAME

    @property
    def stats(self):
        return self._stats

    def run(self, scriptargs):
        with self.stats:
            for func in self._order:
                with self.stats.time_child(func.__name__):
                    func(scriptargs)
