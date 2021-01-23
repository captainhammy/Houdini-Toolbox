"""This module contains the base Houdini event class."""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Toolbox Imports
from ht.events.item import HoudiniEventItem
from ht.events.stats import HoudiniEventStats


# =============================================================================
# CLASSES
# =============================================================================


class HoudiniEventFactory:
    """Class responsible for determining event classes."""

    _mappings = {}

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __repr__(self):
        return "<HoudiniEventFactory>"

    # -------------------------------------------------------------------------
    # STATIC METHODS
    # -------------------------------------------------------------------------

    @staticmethod
    def get_event_type(name):
        """Get an event for a given name.

        If there is no explicit mapping a base HoudiniEvent will be returned.

        :param name: An event name.
        :type name: str
        :return: A found event class instance.
        :rtype: HoudiniEvent

        """
        cls = HoudiniEventFactory._mappings.get(name)

        if cls is not None:
            return cls()

        return HoudiniEvent(name)

    @staticmethod
    def register_event_class(name, event_class):
        """Register an event type class to a name.

        :param name: The event name
        :type name: str
        :param event_class: A customize subclass of HoudiniEvent.
        :type event_class: HoudiniEvent
        :return:

        """
        HoudiniEventFactory._mappings[name] = event_class


class HoudiniEvent:
    """The base Houdini event class.

    :param name: THe event name.
    :type name: str
    :return:

    """

    def __init__(self, name):
        self._data = {}
        self._enabled = True
        self._name = name
        self._item_map = {}

        self._stats = HoudiniEventStats(name)

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.name)

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def data(self):
        """dict: Internal data for storing data that can be shared across event functions."""
        return self._data

    # -------------------------------------------------------------------------

    @property
    def enabled(self):
        """bool: Returns whether or not the action is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled

    # -------------------------------------------------------------------------

    @property
    def item_map(self):
        """dict: Internal event map used to register the functions of this event."""
        return self._item_map

    @property
    def name(self):
        """str: The event name."""
        return self._name

    @property
    def stats(self):
        """EventStats: Statistics related to this event."""
        return self._stats

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def register_item(self, item):
        """Register an item to run.

        :param: item: An item to run.
        :type item: HoudiniEventItem
        :return:

        """
        if not isinstance(item, HoudiniEventItem):
            raise TypeError("Expected HoudiniEventItem, got {}".format(type(item)))

        priority_items = self.item_map.setdefault(item.priority, [])
        priority_items.append(item)

    def run(self, scriptargs):
        """Run the items with the given args.

        Items are run in decreasing order of priority.

        :param: scriptargs: Arguments passed to the event from the caller
        :type scriptargs: dict
        :return:

        """
        # Abort if this action should not run.
        if not self.enabled:
            return

        # Add the Event to the scriptargs in case it needs to be accessed
        scriptargs["_event_"] = self

        with self.stats:
            # Run in order of decreasing priority
            for priority in reversed(sorted(self.item_map.keys())):
                priority_items = self.item_map[priority]

                for item in priority_items:
                    item.run(scriptargs)

        del scriptargs["_event_"]
