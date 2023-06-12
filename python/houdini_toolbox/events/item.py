"""This module contains event item runner class."""

# =============================================================================
# IMPORTS
# =============================================================================

# Future
from __future__ import annotations

# Standard Library
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# Houdini Toolbox
from houdini_toolbox.events.stats import HoudiniEventItemStats

# =============================================================================
# CLASSES
# =============================================================================


class HoudiniEventItem:
    """Class responsible for calling callable methods.

    :param callables: A list of callables to run.
    :param name: Optional item name.
    :param priority: The item priority.
    :param stat_tags: Optional stat tags.
    :return:

    """

    def __init__(
        self,
        callables: Union[List[Callable], Tuple[Callable]],
        name: str = None,
        priority: int = 1,
        stat_tags: List[str] = None,
    ):
        self._callables = list(callables)
        self._name = name
        self._priority = priority

        self._data: Dict[Any, Any] = {}

        self._stats = HoudiniEventItemStats(self.name, tags=stat_tags)

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __eq__(self, other: Any) -> bool:
        """Equality implementation that ignores the stats object.

        :param other: The item to compare to.
        :return: Whether the objects are equal.

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

    def __hash__(self) -> int:
        return hash((self.name, self.priority))

    def __ne__(self, other: Any) -> bool:
        """Inequality implementation that ignores the stats object.

        :param other: The other item to compare to.
        :return: Whether the objects are not equal.

        """
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} {self.name} ({len(self.callables)} callables)>"
        )

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def callables(self) -> List[Callable]:
        """list: A list of callable objects to call."""
        return self._callables

    @property
    def data(self) -> dict:
        """Internal data for storing data that can be shared across item
        functions."""
        return self._data

    @property
    def name(self) -> Optional[str]:
        """The item name."""
        return self._name

    @property
    def priority(self) -> int:
        """The item priority."""
        return self._priority

    @property
    def stats(self) -> HoudiniEventItemStats:
        """Stats for the item."""
        return self._stats

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def run(self, scriptargs: dict) -> None:
        """Run the callables with the given args.

        :param scriptargs: Arguments passed to the event from the caller
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

    :param callables: A list of callables to run.
    :param name: Optional item name.
    :param priority: The item priority.
    :param stat_tags: Optional stat tags.
    :return:

    """

    # Name to item mapping.
    _exclusive_map: Dict[Optional[str], ExclusiveHoudiniEventItem] = {}

    def __init__(
        self,
        callables: Union[List[Callable], Tuple[Callable]],
        name: str = None,
        priority: int = 1,
        stat_tags: List[str] = None,
    ) -> None:
        super().__init__(callables, name, priority, stat_tags)

        # Get the current entry (or add this item if one isn't set.)
        exclusive_item = self._exclusive_map.setdefault(name, self)

        # If this item has the higher priority then point to this item.
        if self.priority > exclusive_item.priority:
            self._exclusive_map[name] = self

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def run(self, scriptargs: dict) -> None:
        """Run the callables with the given args.

        The item is only run if it is the exclusive item.

        :param scriptargs: Arguments passed to the event from the caller
        :return:

        """
        # Only run this item if this item is the exclusive item for the name.
        if self._exclusive_map[self.name] == self:
            super().run(scriptargs)
