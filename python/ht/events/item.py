"""This module contains event item runner class."""

# =============================================================================
# IMPORTS
# =============================================================================

# Third Party Imports
from builtins import object

# Houdini Toolbox Imports
from builtins import object
from ht.events.stats import HoudiniEventItemStats


# =============================================================================
# CLASSES
# =============================================================================


class HoudiniEventItem(object):
    """Class responsible for calling callable methods.

    :param callables: A list of callables to run.
    :type callables: tuple
    :param name: Optional item name.
    :type name: str
    :param priority: The item priority.
    :type priority: int
    :param stat_tags: Optional stat tags.
    :type stat_tags: list(str)
    :return:

    """

    def __init__(self, callables, name=None, priority=1, stat_tags=None):
        self._callables = list(callables)
        self._name = name
        self._priority = priority

        self._data = {}

        self._stats = HoudiniEventItemStats(self.name, tags=stat_tags)

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __eq__(self, other):
        """Equality implementation that ignores the stats object.

        :param other: The item to compare to.
        :type other: HoudiniEventItem
        :return: Whether the objects are equal.
        :rtype: bool

        """
        if not isinstance(other, self.__class__):
            return NotImplemented

        if self.name != other.name:
            return False

        if self.callables != other.callables:
            return False

        if self.priority != other.priority:
            return False

        return True

    def __ne__(self, other):
        """Inequality implementation that ignores the stats object.

        :param other: The other item to compare to.
        :type other: HoudiniEventItem
        :return: Whether the objects are not equal.
        :rtype: bool

        """
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.name, self.priority))

    def __repr__(self):
        return "<{} {} ({} callables)>".format(
            self.__class__.__name__, self.name, len(self.callables)
        )

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

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

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

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
        super(ExclusiveHoudiniEventItem, self).__init__(
            callables, name, priority, stat_tags
        )

        # Get the current entry (or add this item if one isn't set.)
        exclusive_item = self._exclusive_map.setdefault(name, self)

        # If this item has the higher priority then point to this item.
        if self.priority > exclusive_item.priority:
            self._exclusive_map[name] = self

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

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
