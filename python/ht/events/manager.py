"""This module contains a class and functions for registering and managing
events in Houdini.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import collections
from contextlib import contextmanager

# Houdini Toolbox Imports
from ht.events.event import HoudiniEventFactory
from ht.events.group import HoudiniEventGroup
from ht.events.item import HoudiniEventItem


# =============================================================================
# CLASSES
# =============================================================================

class HoudiniEventManager(object):
    """Manager and execute events in Houdini."""

    def __init__(self):
        self._data = {}
        self._events = {}

        # Special dict used to maintain event enabled states when using
        # disabling context manager.
        self._event_states = {}

    def __repr__(self):
        return "<EventManager>"

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _disable_events(self, names=None):
        """Disable any events with matching names.

        :param: names: A list of names of events to disable.
        :type names: list(str) or None
        :return:

        """
        if names is not None:
            for event in self.events.values():
                if event.name in names:
                    self._event_states[event.name] = event.enabled

                    event.enabled = False
        else:
            for event in self.events.values():
                self._event_states[event.name] = event.enabled
                event.enabled = False

    def _restore_events(self):
        """Restore the enabled state of any events that were disabled.

        :return:

        """
        for name, state in self._event_states.iteritems():
            self.events[name].enabled = state

        self._event_states.clear()

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def data(self):
        """dict: Data stored on the manager."""
        return self._data

    @property
    def events(self):
        """dict: The map of events to run."""
        return self._events

    # =========================================================================
    # METHODS
    # =========================================================================

    def create_event(self, name):
        """Create an event with a given name.

        :param name: The event name
        :type name: str
        :return: The newly created event
        :rtype: HoudiniEvent

        """
        event = HoudiniEventFactory.get_event_type(name)

        self.events[name] = event

        return event

    @contextmanager
    def event_disabler(self, names=None):
        """Context manager to disable any events with matching names.

        :param: names: A list of names of events to disable.
        :type names: list(str) or None
        :return:

        """
        # Disable any matching events.
        self._disable_events(names)

        # Wrap the yield in a try/finally block so even if an exception occurs
        # the restore function will always be run.
        try:
            yield

        finally:
            # Restore all event settings.
            self._restore_events()

    def register_event_group(self, event_group):
        """Register a HoudiniEventGroup.

        This function will register all mapped functions in the event object's
        event_map with the given priority.

        :param: event_group: The event group to register
        :type event_group: HoudiniEventGroup
        :return:

        """
        if not isinstance(event_group, HoudiniEventGroup):
            raise TypeError("Expected HoudiniEventGroup, got {}".format(type(event_group)))

        event_mappings = event_group.event_map

        for name, items in event_mappings.iteritems():
            if name not in self.events:
                self.create_event(name)

            event = self.events[name]

            if not isinstance(items, (list, tuple)):
                items = [items]

            for item in items:
                event.register_item(item)

    def register_item(self, item, event_name):
        """Register a function for a given event name.

        :param item: The item to register
        :type item: HoudiniEventItem
        :param event_name: The name of the event to register the item to.
        :type event_name: str
        :return:

        """
        if not isinstance(item, HoudiniEventItem):
            raise TypeError("Expected HoudiniEventItem, got {}".format(type(item)))

        if event_name not in self.events:
            self.create_event(event_name)

        event = self.events[event_name]
        event.register_item(item)

    def run_event(self, event_name, scriptargs=None):
        """Run all registered events for the given name with the supplied args.

        Events are run in decreasing order of priority.

        :param: event_name: The name of the event to run
        :type event_name: str
        :param: scriptargs: Arguments passed to the event from the caller
        :type scriptargs: dict
        :return:

        """
        event = self.events.get(event_name)

        if event is not None:
            if scriptargs is None:
                scriptargs = {}

            # Add data about the manager and event to the scriptargs
            scriptargs["_manager_"] = self

            event.run(scriptargs)


# =============================================================================
# FUNCTIONS
# =============================================================================

def register_event_group(event_group):
    """Register a HoudiniEvent.

    This function will register all mapped functions in the event object's
    event_map with the given priority.

    :param: event_group: The event group to register.
    :type event_group: HoudiniEventGroup
    :return:

    """
    MANAGER.register_event_group(event_group)


def register_function(func, event_name, item_name=None, priority=1, stat_tags=None):
    """Register a function for a given event name.

    :param: func: The function to register.
    :type func: collections.Callable
    :param: event_name: The event name.
    :type event_name: str
    :param item_name: Optional item name.
    :type item_name: str
    :param: priority: The event priority.
    :type priority: int
    :param: stat_tags: Optional tags to group stats together.
    :type stat_tags: [str]
    :return:

    """
    if not isinstance(func, collections.Callable):
        raise TypeError("{} is not callable".format(func))

    item = HoudiniEventItem([func], item_name, priority, stat_tags=stat_tags)

    register_item(item, event_name)


def register_item(item, event_name):
    """Register an item for a given event name.

    :param: item: The item to register.
    :type item: ht.events.item.HoudiniEventItem
    :param: event_name: The event name.
    :type event_name: str
    :return:

    """
    if not isinstance(item, HoudiniEventItem):
        raise TypeError("{} is not a valid item".format(item))

    MANAGER.register_item(item, event_name)


def run_event(event_name, scriptargs=None):
    """Run all registered events for the given name with the supplied args.

    :param: event_name: The name of the event to run.
    :type event_name: str
    :param: scriptargs: Arguments passed to the event from the caller.
    :type scriptargs: dict
    :return:

    """
    MANAGER.run_event(event_name, scriptargs)


# =============================================================================

MANAGER = HoudiniEventManager()
