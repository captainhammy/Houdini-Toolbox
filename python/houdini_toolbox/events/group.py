"""This module contains the Houdini event group class."""


# =============================================================================
# CLASSES
# =============================================================================


class HoudiniEventGroup:
    """The Houdini event group class.

    This class acts as a way to associate multiple event methods together.

    """

    def __init__(self) -> None:
        self._data: dict = {}
        self._event_map: dict = {}

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def data(self) -> dict:
        """Internal data for storing data that can be shared across event
        functions."""
        return self._data

    @property
    def event_map(self) -> dict:
        """Internal event map used to register the functions of this event."""
        return self._event_map
