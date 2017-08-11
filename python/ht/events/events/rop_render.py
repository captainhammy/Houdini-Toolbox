"""This module contains an event to perform actions related to ROP render
scripts.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import time

# Houdini Toolbox Imports
from ht.events.group import HoudiniEventGroup
from ht.events.types import RopEvents

# Houdini Imports
import hou

# =============================================================================
# CLASSES
# =============================================================================


class RopRenderEvent(HoudiniEventGroup):
    """Event to run on ROP render script events."""

    def __init__(self):
        super(RopRenderEvent, self).__init__()

        self._frame_start = None
        self._render_start = None

        self.event_map.update(
            {
                RopEvents.PreRender: (self.preRender,),
                RopEvents.PreFrame: (self.preFrame,),
                RopEvents.PostFrame: (self.postFrame,),
                RopEvents.PostRender: (self.postRender,),
                RopEvents.PostWrite: (self.postWrite,),
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

    def preRender(self, scriptargs):
        self._render_start = scriptargs["time"]

        frame_range = scriptargs["frame_range"]

        if frame_range is not None:
            start, end, inc = frame_range

            print "Starting render: {}-{}:{}".format(
                start,
                end,
                inc,
            )

        else:
            print "Starting render"

    def postFrame(self, scriptargs):
        """Action to run after the frame has rendered."""
        _printFrameWrite(scriptargs)

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

    def postRender(self, scriptargs):
        if self._render_start is not None:
            end_time = scriptargs["time"]

            print "Completed Render: {:0.5f}s".format(
                end_time-self._render_start
            )

        else:
            print "Completed Render"

    def postWrite(self, scriptargs):
        if "path" in scriptargs:
            print "Wrote frame {} to {}".format(
                scriptargs["frame"],
                scriptargs["path"]
            )

        else:
            print "Wrote frame {}".format(scriptargs["frame"])

# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _getTargetFile(node):
    node_type = node.type()
    node_type_name = node_type.name()

    if node_type_name in ("geometry", "rop_geometry"):
        return node.evalParm("sopoutput")

    elif node_type_name in ("alembic", "rop_alembic"):
        return node.evalParm("filename")

    elif node_type_name in ("ifd",):
        if node.evalParm("soho_outputmode"):
            return node.evalParm("soho_diskfile")

        else:
            return node.evalParm("vm_picture")


def _printFrameWrite(scriptargs):
    if "path" in scriptargs:
        node = scriptargs["node"]

        postwrite_parm = node.parm("tpostwrite")

        # If the node has a Post-Write script and it is enabled then we will
        # not handle printing out a write message.
        if postwrite_parm is not None and postwrite_parm.eval():
            pass

        else:
            print "Wrote frame {} to {}".format(
                scriptargs["frame"],
                scriptargs["path"]
            )


# =============================================================================
# FUNCTIONS
# =============================================================================


def buildScriptArgs(node=None):
    """Build relevant scriptargs for this action."""
    frame_range = None

    if node is not None:
        trange_parm = node.parm("trange")

        if trange_parm is not None:
            if trange_parm.evalAsString() != "off":
                frame_range = node.evalParmTuple("f")

    scriptargs = {
        "node": node,
        "frame": hou.frame(),
        "frame_range": frame_range,
        "time": time.time(),
    }

    if node is not None:
        scriptargs["path"] = _getTargetFile(node)

    return scriptargs
