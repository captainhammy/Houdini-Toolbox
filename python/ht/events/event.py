"""This module contains the base Houdini event class."""

import collections

from ht.events.block import HoudiniEventBlock
from ht.events.stats import EventStats

# =============================================================================
# CLASSES
# =============================================================================


class HoudiniEvent(object):
    """The base Houdini event class."""

    def __init__(self, name):
        self._data = {}
        self._enabled = True
        self._event_map = {}
        self._name = name
        self._run_count = 0

        self._stats = EventStats(name)

    def __repr__(self):
        return "<HoudiniEvent: {}>".format(self.name)

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def data(self):
        """dict: Internal data for storing data that can be shared across event
        functions."""
        return self._data

    @property
    def enabled(self):
        """bool: Returns whether or not the action is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled

    @property
    def event_map(self):
        """dict: Internal event map used to register the functions of this event."""
        return self._event_map

    @property
    def name(self):
        """str: The event name."""
        return self._name

    @property
    def stats(self):
        """EventStats: Statistics related to this event."""
        return self._stats

    # =========================================================================
    # METHODS
    # =========================================================================

    def registerBlock(self, event_block, priority=1):
        """Register a function with a priority.

        :param event_block: The event block to register
        :type event_block: HoudiniEventBlock
        :param priority: The event priority
        :type priority: int
        :return:
        """
        if not isinstance(event_block, HoudiniEventBlock):
            raise TypeError(
                "Excepted HoudiniEventBlock, got {}".format(type(event_block))
            )

        priority_map = self.event_map.setdefault(priority, [])

        priority_map.append(event_block)

    def registerFunction(self, func, priority=1):
        """Register a function with a priority.

        :param: func: The function to register
        :type func: collections.Callable
        :param priority: The function priority
        :type priority: int
        :return:
        """
        if not isinstance(func, collections.Callable):
            raise TypeError("{} is not callable".format(func))

        priority_map = self.event_map.setdefault(priority, [])

        priority_map.append(func)

    def registerFunctions(self, functions, priority=1):
        """Register a list of functions with a priority.


        :param: functions: The functions to register
        :type functions: list(collections.Callable)
        :param priority: The function priority
        :type priority: int
        :return:
        """
        non_callable = [func for func in function
                        if not isinstance(func, collections.Callable)]

        if non_callable:
            raise TypeError("Cannot register non-callable objects")

        priority_map = self.event_map.setdefault(priority, [])

        priority_map.extend(functions)

    def run(self, scriptargs):
        """Run the functions with the given args.

        Functions are run in decreasing order of priority.

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
            for priority in reversed(sorted(self.event_map.keys())):
                priority_events = self.event_map[priority]

                for event in priority_events:
                    if isinstance(event, HoudiniEventBlock):
                        event.run(scriptargs)

                    else:
                        event(scriptargs)
