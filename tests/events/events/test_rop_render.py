"""Tests for ht.events.event.rop_render module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Third Party Imports
from builtins import object
import pytest

# Houdini Toolbox Imports
import ht.events.events.rop_render
from ht.events.item import HoudiniEventItem
from ht.events.types import RopEvents

# Houdini Imports
import hou


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def init_event(mocker):
    """Fixture to initialize an event."""
    mocker.patch.object(
        ht.events.events.rop_render.RopRenderEvent, "__init__", lambda x: None
    )

    def _create():
        return ht.events.events.rop_render.RopRenderEvent()

    return _create


@pytest.fixture
def mock_logger(mocker):
    """Mock the module logger."""
    yield mocker.patch("ht.events.events.rop_render._logger")


# =============================================================================
# TESTS
# =============================================================================


class Test_RopRenderEvent(object):
    """Test ht.events.events.rop_render.RopRenderEvent class."""

    def test___init__(self, mocker):
        """Test object initialization."""
        mock_super_init = mocker.patch.object(ht.events.rop_render.HoudiniEventGroup, "__init__")

        event_map = {}
        mocker.patch.object(ht.events.events.rop_render.RopRenderEvent, "event_map", event_map)

        event = ht.events.events.rop_render.RopRenderEvent()

        mock_super_init.assert_called()

        assert event._frame_start is None
        assert event._render_start is None

        expected_map = {
            RopEvents.PreRender: HoudiniEventItem((event.pre_render,)),
            RopEvents.PreFrame: HoudiniEventItem((event.pre_frame,)),
            RopEvents.PostFrame: HoudiniEventItem((event.post_frame,)),
            RopEvents.PostRender: HoudiniEventItem((event.post_render,)),
            RopEvents.PostWrite: HoudiniEventItem((event.post_write,)),
        }

        assert event_map == expected_map

    # pre_frame

    def test_pre_frame(self, init_event, mocker, mock_logger):
        """Test pre-frame action."""
        event = init_event()
        event._frame_start = None

        mock_frame = mocker.MagicMock(spec=int)
        mock_time = mocker.MagicMock(spec=float)

        scriptargs = {"time": mock_time, "frame": mock_frame}

        event.pre_frame(scriptargs)

        assert event._frame_start == mock_time

        mock_logger.info.assert_called_with("Starting Frame: %s", mock_frame)

    # pre_render

    def test_pre_render__with_frame_range(self, init_event, mocker, mock_logger):
        """Test when a frame range is passed."""
        event = init_event()
        event._render_start = None

        mock_time = mocker.MagicMock(spec=float)

        mock_start = mocker.MagicMock(spec=int)
        mock_end = mocker.MagicMock(spec=int)
        mock_inc = mocker.MagicMock(spec=int)

        scriptargs = {"time": mock_time, "frame_range": (mock_start, mock_end, mock_inc)}

        event.pre_render(scriptargs)

        assert event._render_start == mock_time

        mock_logger.info.assert_called_with("Starting render: %s-%s:%s", mock_start, mock_end, mock_inc)

    def test_pre_render__no_frame_range(self, init_event, mocker, mock_logger):
        """Test with no frame range."""
        event = init_event()
        event._render_start = None

        mock_time = mocker.MagicMock(spec=float)

        scriptargs = {"time": mock_time, "frame_range": None}

        event.pre_render(scriptargs)

        assert event._render_start == mock_time

        mock_logger.info.assert_called_with("Starting render")

    # post_frame

    def test_post_frame__valid_start_frame(self, init_event, mocker, mock_logger):
        """Test when a start time exists."""
        mock_print = mocker.patch("ht.events.events.rop_render._print_frame_write")

        event = init_event()
        event._frame_start = mocker.MagicMock(spec=float)

        mock_time = mocker.MagicMock(spec=float)
        mock_frame = mocker.MagicMock(spec=int)

        scriptargs = {
            "time": mock_time,
            "frame": mock_frame,
        }

        event.post_frame(scriptargs)

        mock_print.assert_called_with(scriptargs)

        mock_logger.info.assert_called_with("Completed Frame: %s (%0.5fs)", mock_frame, mock_time-event._frame_start)

    def test_post_frame__no_start_frame(self, init_event, mocker, mock_logger):
        """Test when no start time is known."""
        mock_print = mocker.patch("ht.events.events.rop_render._print_frame_write")

        event = init_event()
        event._frame_start = None

        mock_frame = mocker.MagicMock(spec=int)

        scriptargs = {"frame": mock_frame}

        event.post_frame(scriptargs)

        mock_print.assert_called_with(scriptargs)

        mock_logger.info.assert_called_with("Completed Frame: %s", mock_frame)

    # post_render

    def test_post_render__valid_start_time(self, init_event, mocker, mock_logger):
        """Test when a start time exists."""
        event = init_event()
        event._render_start = mocker.MagicMock(spec=float)

        mock_time = mocker.MagicMock(spec=float)

        scriptargs = {"time": mock_time}

        event.post_render(scriptargs)

        mock_logger.info.assert_called_with("Completed Render: %0.5fs", mock_time-event._render_start)

    def test_post_render__no_start_time(self, init_event, mock_logger):
        """Test when no start time is known."""
        event = init_event()
        event._render_start = None

        event.post_render({})

        mock_logger.info.assert_called_with("Completed Render")

    # post_write

    def test_post_write__valid_path(self, init_event, mocker, mock_logger):
        """Test when the output path is known."""
        event = init_event()

        mock_frame = mocker.MagicMock(spec=int)
        mock_path = mocker.MagicMock(spec=str)

        scriptargs = {
            "frame": mock_frame,
            "path": mock_path
        }

        event.post_write(scriptargs)

        mock_logger.info.assert_called_with("Wrote frame %s to %s", mock_frame, mock_path)

    def test_post_write__no_path(self, init_event, mocker, mock_logger):
        """Test when the output path is unknown."""
        event = init_event()

        mock_frame = mocker.MagicMock(spec=int)

        scriptargs = {
            "frame": mock_frame,
        }

        event.post_write(scriptargs)

        mock_logger.info.assert_called()


@pytest.mark.parametrize("type_name, return_value, expected", [
    ("geometry", None, ("sopoutput", )),
    ("rop_geometry", None, ("sopoutput", )),
    ("alembic", None, ("filename", )),
    ("rop_alembic", None, ("filename", )),
    ("ifd", True, ("soho_outputmode", "soho_diskfile")),
    ("ifd", False, ("vm_picture", )),
    (None, None, None),
])
def test__get_target_file(mocker, type_name, return_value, expected):
    """Test ht.events.events.rop_render._get_target_file."""
    mock_type = mocker.MagicMock(spec=hou.NodeType)
    mock_type.name.return_value = type_name

    mock_type = mocker.MagicMock(spec=hou.NodeType)
    mock_type.name.return_value = type_name

    mock_node = mocker.MagicMock(spec=hou.Node)
    mock_node.evalParm.return_value = return_value
    mock_node.type.return_value = mock_type

    result = ht.events.events.rop_render._get_target_file(mock_node)

    if expected:
        assert result == mock_node.evalParm.return_value

        calls = [mocker.call(value) for value in expected]
        mock_node.evalParm.assert_has_calls(calls)

    else:
        assert result is None


class Test__print_frame_write(object):
    """Test ht.events.events.rop_render._print_frame_write."""

    def test_no_path(self, mocker):
        """Test when no path is found."""
        mock_node = mocker.MagicMock(spec=hou.Node)
        scriptargs = {"node": mock_node}

        ht.events.events.rop_render._print_frame_write(scriptargs)

        mock_node.parm.assert_not_called()

    def test_post_script(self, mocker, mock_logger):
        """Test when there is a post-write script enabled and the path won't be printed."""
        mock_script = mocker.MagicMock(spec=str)
        mock_script.__len__.return_value = 1

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = mock_script

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.parm.return_value = mock_parm

        scriptargs = {"node": mock_node, "path": mocker.MagicMock(spec=str)}

        ht.events.events.rop_render._print_frame_write(scriptargs)

        mock_logger.info.assert_not_called()

    def test_path_no_post_script(self, mocker, mock_logger):
        """Test when the path will be printed."""
        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = ""

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.parm.return_value = mock_parm

        scriptargs = {
            "node": mock_node,
            "frame": mocker.MagicMock(spec=int),
            "path": mocker.MagicMock(spec=str),
        }

        ht.events.events.rop_render._print_frame_write(scriptargs)

        mock_logger.info.assert_called()


class Test_build_scriptargs(object):
    """Test ht.events.events.rop_render.build_scriptargs."""

    def test_no_args(self, mocker):
        """Test where there all args are default."""
        mock_time = mocker.patch("ht.events.events.rop_render.time.time")
        mock_frame = mocker.patch("ht.events.events.rop_render.hou.frame")
        mock_get = mocker.patch("ht.events.events.rop_render._get_target_file")

        result = ht.events.events.rop_render.build_scriptargs()

        expected = {
            "node": None,
            "frame": mock_frame.return_value,
            "frame_range": None,
            "time": mock_time.return_value,
        }

        assert result == expected

        mock_get.assert_not_called()

    def test_no_trange(self, mocker):
        """Test where there is no 'trange' parm."""
        mock_time = mocker.patch("ht.events.events.rop_render.time.time")
        mock_frame = mocker.patch("ht.events.events.rop_render.hou.frame")
        mock_get = mocker.patch("ht.events.events.rop_render._get_target_file")

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.parm.return_value = None

        result = ht.events.events.rop_render.build_scriptargs(mock_node)

        expected = {
            "node": mock_node,
            "frame": mock_frame.return_value,
            "frame_range": None,
            "time": mock_time.return_value,
            "path": mock_get.return_value,
        }

        assert result == expected

        mock_get.assert_called_with(mock_node)

    def test_trange_off(self, mocker):
        """Test where we can't get a frame range because it is off."""
        mock_time = mocker.patch("ht.events.events.rop_render.time.time")
        mock_frame = mocker.patch("ht.events.events.rop_render.hou.frame")
        mock_get = mocker.patch("ht.events.events.rop_render._get_target_file")

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.evalAsString.return_value = "off"

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.parm.return_value = mock_parm

        result = ht.events.events.rop_render.build_scriptargs(mock_node)

        expected = {
            "node": mock_node,
            "frame": mock_frame.return_value,
            "frame_range": None,
            "time": mock_time.return_value,
            "path": mock_get.return_value,
        }

        assert result == expected

        mock_get.assert_called_with(mock_node)

    def test_found_frame_range(self, mocker):
        """Test where we actually get a frame range."""
        mock_time = mocker.patch("ht.events.events.rop_render.time.time")
        mock_frame = mocker.patch("ht.events.events.rop_render.hou.frame")
        mock_get = mocker.patch("ht.events.events.rop_render._get_target_file")

        mock_node = mocker.MagicMock(spec=hou.Node)

        result = ht.events.events.rop_render.build_scriptargs(mock_node)

        expected = {
            "node": mock_node,
            "frame": mock_frame.return_value,
            "frame_range": mock_node.evalParmTuple.return_value,
            "time": mock_time.return_value,
            "path": mock_get.return_value,
        }

        assert result == expected

        mock_node.evalParmTuple.assert_called_with("f")
        mock_get.assert_called_with(mock_node)

    def test_no_path(self, mocker):
        """Test where we actually get a frame range."""
        mock_time = mocker.patch("ht.events.events.rop_render.time.time")
        mock_frame = mocker.patch("ht.events.events.rop_render.hou.frame")
        mock_get = mocker.patch(
            "ht.events.events.rop_render._get_target_file", return_value=None
        )

        mock_node = mocker.MagicMock(spec=hou.Node)

        mock_get.return_value = None

        result = ht.events.events.rop_render.build_scriptargs(mock_node)

        expected = {
            "node": mock_node,
            "frame": mock_frame.return_value,
            "frame_range": mock_node.evalParmTuple.return_value,
            "time": mock_time.return_value,
            "path": mock_get.return_value,
        }

        assert result == expected

        mock_node.evalParmTuple.assert_called_with("f")
        mock_get.assert_called_with(mock_node)
