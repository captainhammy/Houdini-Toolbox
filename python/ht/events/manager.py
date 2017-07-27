"""This module contains a class and functions for registering and managing
events in Houdini.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import collections
from contextlib import contextmanager

from ht.events.event import HoudiniEvent
from ht.events.block import HoudiniEventBlock
from ht.events.group import HoudiniEventGroup

# Houdini Imports
import hou

# =============================================================================
# CLASSES
# =============================================================================


class EventManager(object):
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

    def _restoreEvents(self):
        """Restore the enabled state of any events that were disabled.

        :return:
        """
        for name, state in self._event_states.iteritems():
            self.events[name].enabled = state

        self._event_states.clear()

    def _disableEvents(self, names=None):
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
    # STATIC METHODS
    # =========================================================================

    @staticmethod
    def getSessionManager():
        """Find or create an EventManager for the current session.

        :return: Returns the session's event manager
        :rtype: EventManager
        """
        if not hasattr(hou.session, "_event_manager"):
            hou.session._event_manager = EventManager()

        return hou.session._event_manager

    # =========================================================================
    # METHODS
    # =========================================================================

    def createEvent(self, name):
        """Create an event with a given name.

        :param name: The event name
        :type name: str
        :return: The newly created event
        :rtype: HoudiniEvent
        """
        event = HoudiniEvent(name)

        self.events[name] = event

    @contextmanager
    def eventDisabler(self, names=None):
        """Context manager to disable any events with matching names.

        :param: names: A list of names of events to disable.
        :type names: list(str) or None
        :return:
        """
        # Disable any matching events.
        self._disableEvents(names)

        # Wrap the yield in a try/finally block so even if an exception occurs
        # the restore function will always be run.
        try:
            yield

        finally:
            # Restore all event settings.
            self._restoreEvents()

    def registerEventBlock(self, event_block, priority=1):
        """Register an EventBlock with a given priority.

        :param event_block: The event block to register
        :type event_block: HoudiniEventBlock
        :param priority: The event priority
        :type priority: int
        :return:
        """
        if not isinstance(event_block, HoudiniEventBlock):
            raise TypeError("Expected HoudiniEventBlock, got {}".format(type(event_block)))

        name = event_block.event_name

        if name not in self.events:
            self.createEvent(name)

        event = self.events[name]
        event.registerBlock(event_block, priority)

    def registerEventGroup(self, event_group, priority=1):
        """Register a HoudiniEventGroup.

        This function will register all mapped functions in the event object's
        event_map with the given priority.

        :param: event_group: The event group to register
        :type event_group: HoudiniEventGroup
        :param priority: The event priority
        :type priority: int
        :return:
        """
        if not isinstance(event_group, HoudiniEventGroup):
            raise TypeError("Expected HoudiniEventGroup, got {}".format(type(event_group)))

        event_mappings = event_group.event_map

        for name, functions in event_mappings.iteritems():
            if name not in self.events:
                self.createEvent(name)

            event = self.events[name]
            event.registerFunctions(functions, priority)

    def registerFunction(self, func, event_name, priority=1):
        """Register a function for a given event name.

        :param: func: The function to register
        :type func: collections.Callable
        :param: event_name: The name of the event to register the function for
        :type event_name: str
        :param priority: The event priority
        :type priority: int
        :return:
        """
        if not isinstance(func, collections.Callable):
            raise TypeError("{} is not callable".format(func))

        if event_name not in self.events:
            self.createEvent(event_name)

        event = self.events[event_name]
        event.registerFunction(func, priority)

    def runEvent(self, event_name, scriptargs):
        """Run all registered events for the given name with the supplied
        args.

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
            scriptargs["_event_name_"] = event.name

            event.run(scriptargs)


# =============================================================================
# FUNCTIONS
# =============================================================================

def registerEventBlock(event_block, priority=1):
    """Register an event block.

    :param: event_block: The event block to register
    :type event_block: HoudiniEventBlock
    :param: priority: The event priority
    :type priority: int
    :return:
    """
    manager = EventManager.getSessionManager()

    manager.registerEventBlock(event_block, priority=priority)


def registerEventGroup(event_group, priority=1):
    """Register a HoudiniEvent.

    This function will register all mapped functions in the event object's
    event_map with the given priority.

    :param: event_group: The event group to register
    :type event_group: HoudiniEventGroup
    :param: priority: The event priority
    :type priority: int
    :return:
    """
    manager = EventManager.getSessionManager()

    manager.registerEventGroup(event_group, priority=priority)


def registerFunction(func, event_name, priority=1):
    """Register a function for a given event name.

    :param: func: The function to register
    :type func: collections.Callable
    :param: event_name: The event name
    :type event_name: str
    :param: priority: The event priority
    :type priority: int
    :return:
    """
    manager = EventManager.getSessionManager()

    manager.registerFunction(func, event_name, priority=priority)


def runEvent(event_name, scriptargs=None):
    """Run all registered events for the given name with the supplied args.

    :param: event_name: The name of the event to run
    :type event_name: str
    :param: scriptargs: Arguments passed to the event from the caller
    :type scriptargs: dict
    :return:
    """
    manager = EventManager.getSessionManager()

    manager.runEvent(event_name, scriptargs)
