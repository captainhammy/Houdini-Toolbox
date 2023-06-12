"""This module contains an event to perform actions related to ROP render
scripts.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import logging
import time
from typing import Optional

# Houdini Toolbox
from houdini_toolbox.events.group import HoudiniEventGroup
from houdini_toolbox.events.item import HoudiniEventItem
from houdini_toolbox.events.types import RopEvents

# Houdini
import hou

_logger = logging.getLogger(__name__)


# =============================================================================
# CLASSES
# =============================================================================


class RopRenderEvent(HoudiniEventGroup):
    """Event to run on ROP render script events."""

    def __init__(self) -> None:
        super().__init__()

        self._frame_start = None
        self._render_start = None

        self.event_map.update(
            {
                RopEvents.PreRender: HoudiniEventItem((self.pre_render,)),
                RopEvents.PreFrame: HoudiniEventItem((self.pre_frame,)),
                RopEvents.PostFrame: HoudiniEventItem((self.post_frame,)),
                RopEvents.PostRender: HoudiniEventItem((self.post_render,)),
                RopEvents.PostWrite: HoudiniEventItem((self.post_write,)),
            }
        )

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def pre_frame(self, scriptargs: dict) -> None:
        """Action run before the frame starts rendering.

        :param scriptargs: Event data.
        :return:

        """
        # Store the time as the "start time" so it can be referenced after the
        # frame is completed to get the duration.
        self._frame_start = scriptargs["time"]

        _logger.info("Starting Frame: %s", scriptargs["frame"])

    def pre_render(self, scriptargs: dict) -> None:
        """Action run before the render starts.

        :param scriptargs: Event data.
        :return:

        """
        self._render_start = scriptargs["time"]

        frame_range = scriptargs["frame_range"]

        if frame_range is not None:
            start, end, inc = frame_range

            _logger.info("Starting render: %s-%s:%s", start, end, inc)

        else:
            _logger.info("Starting render")

    def post_frame(self, scriptargs: dict) -> None:
        """Action run after the frame has rendered.

        :param scriptargs: Event data.
        :return:

        """
        _print_frame_write(scriptargs)

        # Ensure we had a start time.
        if self._frame_start is not None:
            end_time = scriptargs["time"]
            duration = end_time - self._frame_start

            # Print a complete message that includes our calculated duration.
            _logger.info("Completed Frame: %s (%0.5fs)", scriptargs["frame"], duration)

        # If we somehow didn't, just print the complete message.
        else:
            _logger.info("Completed Frame: %s", scriptargs["frame"])

    def post_render(self, scriptargs: dict) -> None:
        """Action run after the render is complete.

        :param scriptargs: Event data.
        :return:

        """
        if self._render_start is not None:
            end_time = scriptargs["time"]

            _logger.info("Completed Render: %0.5fs", end_time - self._render_start)

        else:
            _logger.info("Completed Render")

    @staticmethod
    def post_write(scriptargs: dict) -> None:
        """Action run after the frame is written to disk.

        :param scriptargs: Event data.
        :return:

        """
        if "path" in scriptargs:
            _logger.info(
                "Wrote frame %s to %s", scriptargs["frame"], scriptargs["path"]
            )

        else:
            _logger.info("Wrote frame %s", scriptargs["frame"])


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _get_target_file(node: hou.RopNode) -> Optional[str]:
    """Attempt to determine the target output file:

    :param node: The running node.
    :return: The output file path, if any.

    """
    node_type = node.type()
    node_type_name = node_type.name()

    if node_type_name in ("geometry", "rop_geometry"):
        return node.evalParm("sopoutput")

    if node_type_name in ("alembic", "rop_alembic"):
        return node.evalParm("filename")

    if node_type_name in ("ifd",):
        if node.evalParm("soho_outputmode"):
            return node.evalParm("soho_diskfile")

        return node.evalParm("vm_picture")

    return None


def _print_frame_write(scriptargs: dict) -> None:
    """Print that a file was written.

    :param scriptargs: Event data.
    :return:

    """
    if "path" in scriptargs:
        node = scriptargs["node"]

        postwrite_parm = node.parm("tpostwrite")

        # If the node has a Post-Write script and it is enabled then we will
        # not handle printing out a write message.
        if postwrite_parm is not None and postwrite_parm.eval():
            pass

        else:
            _logger.info(
                "Wrote frame %s to %s", scriptargs["frame"], scriptargs["path"]
            )


# =============================================================================
# FUNCTIONS
# =============================================================================


def build_scriptargs(node: Optional[hou.Node] = None) -> dict:
    """Build relevant scriptargs for this action.

    :param node: Optionally rendering node.
    :return: Data related to the running script parm.

    """
    frame_range = None

    if node is not None:
        trange_parm = node.parm("trange")

        if trange_parm is not None and trange_parm.evalAsString() != "off":
            frame_range = node.evalParmTuple("f")

    scriptargs = {
        "node": node,
        "frame": hou.frame(),
        "frame_range": frame_range,
        "time": time.time(),
    }

    if node is not None:
        scriptargs["path"] = _get_target_file(node)

    return scriptargs
