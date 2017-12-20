"""This module contains the Houdini event group class."""

# =============================================================================
# CLASSES
# =============================================================================


class HoudiniEventGroup(object):
    """The Houdini event group class.

    This class acts as a way to associate multiple event methods together.

    """

    def __init__(self):
        self._data = {}
        self._event_map = {}

    def __repr__(self):
        return "<HoudiniEventGroup: {}>".format(self.__class__.__name__)

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

