"""This module contains the base Houdini event class."""

# =============================================================================
# CLASSES
# =============================================================================

class HoudiniEvent(object):
    """The base Houdini event class."""

    def __init__(self):
        self._data = {}
        self._event_map = {}

        def __repr__(self):
            return "<HoudiniEvent: {}>".format(self.__class__.__name__)

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def data(self):
        """Internal data for storing data that can be shared across event
        functions."""
        return self._data

    @property
    def event_map(self):
        """Internal event map used to register the functions of this event."""
        return self._event_map

