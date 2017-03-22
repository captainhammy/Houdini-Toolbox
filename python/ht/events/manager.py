"""This module contains a class and functions for registering and managing
events in Houdini.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Houdini Imports
import hou

# =============================================================================
# CLASSES
# =============================================================================

class EventManager(object):
    """Manager and execute events in Houdini."""

    def __init__(self):
        self._event_map = {}

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def event_map(self):
        """The map of events to run."""
        return self._event_map

    # =========================================================================
    # STATIC METHODS
    # =========================================================================

    @staticmethod
    def getSessionManager():
        """Find or create an EventManager for the session."""
        if not hasattr(hou.session, "_event_manager"):
            hou.session._event_manager = EventManager()

        return hou.session._event_manager

    # =========================================================================
    # METHODS
    # =========================================================================

    def registerEvent(self, event, priority=1):
        """Register a HoudiniEvent.

        This function will register all mapped functions in the event object's
        event_map with the given priority.

        """
        event_mappings = event.event_map

        for name, functions in event_mappings.iteritems():
            events = self.event_map.setdefault(name, {})

            priority_map = events.setdefault(priority, [])

            priority_map.extend(functions)

    def registerFunction(self, event_name, func, priority=1):
        """Register a function for a given event name."""
        events = self.event_map.setdefault(event_name, {})

        priority_map = events.setdefault(priority, [])

        priority_map.append(func)

    def runEvents(self, event_name, scriptargs):
        """Run all registered events for the given name with the supplied
        args.

        Events are run in decreasing order of priority.
        """
        events = self.event_map.get(event_name, {})

        for priority in reversed(sorted(events.keys())):
            priority_events = events[priority]

            for event in priority_events:
                event(scriptargs)

# =============================================================================
# CLASSES
# =============================================================================

def runEvents(event_name, scriptargs):
    """Run all registered events for the given name with the supplied args."""
    manager = EventManager.getSessionManager()

    manager.runEvents(event_name, scriptargs)


def registerEvent(event, priority=1):
    """Register a HoudiniEvent.

    This function will register all mapped functions in the event object's
    event_map with the given priority.

    """
    manager = EventManager.getSessionManager()

    manager.registerEvent(event, priority=priority)


def registerFunction(event_name, func, priority=1):
    """Register a function for a given event name."""
    manager = EventManager.getSessionManager()

    manager.registerFunction(event_name, func, priority=priority)

