"""This module contains event item runner class."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.events.stats import HoudiniEventItemStats

# =============================================================================
# IMPORTS
# =============================================================================

class HoudiniEventItem(object):
    """Class responsible for calling callable methods."""

    def __init__(self, callables, name=None, priority=1, stat_tags=None):
        self._callables = list(callables)
        self._name = name
        self._priority = priority

        self._data = {}

        self._stats = HoudiniEventItemStats(self.name, tags=stat_tags)

    def __eq__(self, item):
        """Equality implementation that ignores the stats object."""
        if self.name != item.name:
            return False

        if self.callables != item.callables:
            return False

        if self.priority != item.priority:
            return False

        return True

    def __ne__(self, item):
        """Inequality implementation that ignores the stats object."""
        return not self.__eq__(item)

    def __repr__(self):
        return "<{} {} ({} callables)>".format(
            self.__class__.__name__,
            self.name,
            len(self.callables)
        )

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def callables(self):
        """list: A list of callable objects to call."""
        return self._callables

    @property
    def data(self):
        """dict: Internal data for storing data that can be shared across item
        functions."""
        return self._data

    @property
    def name(self):
        """str: The item name."""
        return self._name

    @property
    def priority(self):
        """int: The item priority."""
        return self._priority

    @property
    def stats(self):
        """HoudiniEventItemStats: Stats for the item."""
        return self._stats

    # =========================================================================
    # METHODS
    # =========================================================================

    def run(self, scriptargs):
        """Run the callables with the given args.

        :param: scriptargs: Arguments passed to the event from the caller
        :type scriptargs: dict
        :return:

        """
        scriptargs["_item_"] = self

        with self.stats:
            for func in self.callables:
                with self.stats.time_function(func):
                    func(scriptargs)

        del scriptargs["_item_"]


class ExclusiveHoudiniEventItem(HoudiniEventItem):
    """HoudiniEventItem subclass which uses the name and priority to determine
    which item of the same name should be run.

    """

    # Name to item mapping.
    _exclusive_map = {}

    def __init__(self, callables, name, priority=1, stat_tags=None):
        super(ExclusiveHoudiniEventItem, self).__init__(callables, name, priority, stat_tags)

        # Get the current entry (or add ourself if one isn't set.)
        exclusive_item = self._exclusive_map.setdefault(name, self)

        # If this item has the higher priority then point to this item.
        if self.priority > exclusive_item.priority:
            self._exclusive_map[name] = self

    def run(self, scriptargs):
        """Run the callables with the given args.

        The item is only run if it is the exclusive item.

        :param: scriptargs: Arguments passed to the event from the caller
        :type scriptargs: dict
        :return:

        """
        # Only run this item if this item is the exclusive item for the name.
        if self._exclusive_map[self.name] == self:
            super(ExclusiveHoudiniEventItem, self).run(scriptargs)

