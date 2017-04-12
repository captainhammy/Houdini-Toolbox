"""This module contains an event to perform actions related to ROP render
scripts.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import time

# Houdini Toolbox Imports
from ht.events.event import HoudiniEvent

# Houdini Imports
import hou

# =============================================================================
# CLASSES
# =============================================================================

class RopRenderEvent(HoudiniEvent):
    """Event to run on ROP render script events."""

    def __init__(self):
        super(RopRenderEvent, self).__init__()

        self._frame_start = None

        self.event_map.update(
            {
                "Pre-Frame": (self.preFrame,),
                "Post-Frame": (self.postFrame,),
            }
        )

    # =========================================================================
    # METHODS
    # =========================================================================

    def preFrame(self, scriptargs):
        """Action to run before the frame starts rendering."""
        # Store the time as the "start time" so it can be referenced after the
        # frame is completed to get the duration.
        self._frame_start = scriptargs["time"]

        print "Starting Frame: {}".format(
            scriptargs["frame"],
        )

    def postFrame(self, scriptargs):
        """Action to run after the frame has rendered."""
        # Ensure we had a start time.
        if self._frame_start is not None:
            end_time = scriptargs["time"]

            # Print a complete message that includes our calculated duration.
            print "Completed Frame: {} ({:0.5f}s)".format(
                scriptargs["frame"],
                end_time-self._frame_start
            )

        # If we somehow didn't, just print the complete message.
        else:
            print "Completed Frame: {}".format(
                scriptargs["frame"],
            )

# =============================================================================

def buildScriptArgs(node=None):
    """Build relevant scriptargs for this action."""
    scriptargs = {
        "node": node,
        "frame": hou.frame(),
        "time": time.time(),
    }

    return scriptargs

