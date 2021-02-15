"""This module contains the base Houdini event class."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
from __future__ import annotations
import enum
from typing import Any, Dict, List, Type

# Houdini Toolbox Imports
from ht.events.item import HoudiniEventItem
from ht.events.stats import HoudiniEventStats


# =============================================================================
# CLASSES
# =============================================================================


class HoudiniEventFactory:
    """Class responsible for determining event classes."""

    _mappings: Dict[enum.Enum, Type[HoudiniEvent]] = {}

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)

    # -------------------------------------------------------------------------
    # STATIC METHODS
    # -------------------------------------------------------------------------

    @staticmethod
    def get_event_type(event: enum.Enum) -> HoudiniEvent:
        """Get an event for a given name.

        If there is no explicit mapping a base HoudiniEvent will be returned.

        :param event: An event enum.
        :return: A found event class instance.

        """
        cls = HoudiniEventFactory._mappings.get(event)

        if cls is not None:
            return cls(event.value)

        return HoudiniEvent(event.value)


class HoudiniEvent:
    """The base Houdini event class.

    :param name: THe event name.
    :return:

    """

    def __init__(self, name: str):
        self._data: Dict[Any, Any] = dict()
        self._enabled = True
        self._name = name
        self._item_map: Dict[int, List[HoudiniEventItem]] = dict()

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
    def data(self) -> dict:
        """Internal data for storing data that can be shared across event functions."""
        return self._data

    @property
    def enabled(self) -> bool:
        """Whether or not the action is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled

    @property
    def item_map(self) -> dict:
        """Internal event map used to register the functions of this event."""
        return self._item_map

    @property
    def name(self) -> str:
        """str: The event name."""
        return self._name

    @property
    def stats(self) -> HoudiniEventStats:
        """Statistics related to this event."""
        return self._stats

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def register_item(self, item: HoudiniEventItem):
        """Register an item to run.

        :param item: An item to run.
        :return:

        """
        if not isinstance(item, HoudiniEventItem):
            raise TypeError("Expected HoudiniEventItem, got {}".format(type(item)))

        priority_items = self.item_map.setdefault(item.priority, [])
        priority_items.append(item)

    def run(self, scriptargs: dict):
        """Run the items with the given args.

        Items are run in decreasing order of priority.

        :param scriptargs: Arguments passed to the event from the caller
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
