"""Tests for ht.events.event.rop_render module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import imp

# Third Party Imports
import pytest

# Houdini Toolbox Imports
import ht.events.events.rop_render

from ht.events.item import HoudiniEventItem
from ht.events.types import RopEvents

# Houdini Imports
import hou

# Reload the module to test to capture load evaluation since it has already
# been loaded.
imp.reload(ht.events.events.rop_render)


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


# =============================================================================
# TESTS
# =============================================================================


class Test_RopRenderEvent(object):
    """Test ht.events.events.rop_render.RopRenderEvent class."""

    def test___init__(self):
        """Test object initialization."""
        event = ht.events.events.rop_render.RopRenderEvent()

        assert event._frame_start is None
        assert event._render_start is None

        expected_map = {
            RopEvents.PreRender: HoudiniEventItem((event.pre_render,)),
            RopEvents.PreFrame: HoudiniEventItem((event.pre_frame,)),
            RopEvents.PostFrame: HoudiniEventItem((event.post_frame,)),
            RopEvents.PostRender: HoudiniEventItem((event.post_render,)),
            RopEvents.PostWrite: HoudiniEventItem((event.post_write,)),
        }

        assert event.event_map == expected_map

    # Methods

    # pre_frame

    def test_pre_frame(self, init_event, mocker):
        mock_logger = mocker.patch("ht.events.events.rop_render._logger")

        event = init_event()
        event._frame_start = None

        mock_time = mocker.MagicMock(spec=float)

        scriptargs = {"time": mock_time, "frame": mocker.MagicMock(spec=int)}

        event.pre_frame(scriptargs)

        assert event._frame_start == mock_time

        mock_logger.info.assert_called()

    # pre_render

    def test_pre_render__with_frame_range(self, init_event, mocker):
        mock_logger = mocker.patch("ht.events.events.rop_render._logger")

        event = init_event()
        event._render_start = None

        mock_time = mocker.MagicMock(spec=float)

        frange = (
            mocker.MagicMock(spec=int),
            mocker.MagicMock(spec=int),
            mocker.MagicMock(spec=int),
        )

        scriptargs = {"time": mock_time, "frame_range": frange}

        event.pre_render(scriptargs)

        assert event._render_start == mock_time

        mock_logger.info.assert_called()

    def test_pre_render__no_frame_range(self, init_event, mocker):
        mock_logger = mocker.patch("ht.events.events.rop_render._logger")

        event = init_event()
        event._render_start = None

        mock_time = mocker.MagicMock(spec=float)

        scriptargs = {"time": mock_time, "frame_range": None}

        event.pre_render(scriptargs)

        assert event._render_start == mock_time

        mock_logger.info.assert_called()

    # post_frame

    def test_post_frame__valid_start_frame(self, init_event, mocker):
        mock_logger = mocker.patch("ht.events.events.rop_render._logger")
        mock_print = mocker.patch("ht.events.events.rop_render._print_frame_write")

        event = init_event()
        event._frame_start = mocker.MagicMock(spec=float)

        scriptargs = {
            "time": mocker.MagicMock(spec=float),
            "frame": mocker.MagicMock(spec=int),
        }

        event.post_frame(scriptargs)

        mock_print.assert_called_with(scriptargs)

        mock_logger.info.assert_called()

    def test_post_frame__no_start_frame(self, init_event, mocker):
        mock_logger = mocker.patch("ht.events.events.rop_render._logger")
        mock_print = mocker.patch("ht.events.events.rop_render._print_frame_write")

        event = init_event()
        event._frame_start = None

        scriptargs = {"frame": mocker.MagicMock(spec=int)}

        event.post_frame(scriptargs)

        mock_print.assert_called_with(scriptargs)

        mock_logger.info.assert_called()

    # post_render

    def test_post_render__valid_start_frame(self, init_event, mocker):
        mock_logger = mocker.patch("ht.events.events.rop_render._logger")

        event = init_event()
        event._render_start = mocker.MagicMock(spec=float)

        scriptargs = {"time": mocker.MagicMock(spec=float)}

        event.post_render(scriptargs)

        mock_logger.info.assert_called()

    def test_post_render__no_start_frame(self, init_event, mocker):
        mock_logger = mocker.patch("ht.events.events.rop_render._logger")

        event = init_event()
        event._render_start = None

        event.post_render({})

        mock_logger.info.assert_called()

    # post_write

    def test_post_write__valid_path(self, init_event, mocker):
        mock_logger = mocker.patch("ht.events.events.rop_render._logger")

        event = init_event()

        scriptargs = {
            "frame": mocker.MagicMock(spec=int),
            "path": mocker.MagicMock(spec=str),
        }

        event.post_write(scriptargs)

        mock_logger.info.assert_called()

    def test_post_write__no_path(self, init_event, mocker):
        mock_logger = mocker.patch("ht.events.events.rop_render._logger")

        event = init_event()

        scriptargs = {"frame": mocker.MagicMock(spec=int)}

        event.post_write(scriptargs)

        mock_logger.info.assert_called()


class Test__get_target_file(object):
    """Test ht.events.events.rop_render._get_target_file."""

    def test_geometry(self, mocker):
        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.name.return_value = "geometry"

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.type.return_value = mock_type

        mock_path = mocker.MagicMock(spec=str)

        mock_node.evalParm.return_value = mock_path

        result = ht.events.events.rop_render._get_target_file(mock_node)

        assert result == mock_path
        mock_node.evalParm.assert_called_with("sopoutput")

        # Try again but with rop_geometry.
        mock_type.name.return_value = "rop_geometry"

        result = ht.events.events.rop_render._get_target_file(mock_node)

        assert result == mock_path
        mock_node.evalParm.assert_called_with("sopoutput")

    def test_alembic(self, mocker):
        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.name.return_value = "alembic"

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.type.return_value = mock_type

        mock_path = mocker.MagicMock(spec=str)

        mock_node.evalParm.return_value = mock_path

        result = ht.events.events.rop_render._get_target_file(mock_node)

        assert result == mock_path
        mock_node.evalParm.assert_called_with("filename")

        # Try again but with rop_alembic.
        mock_type.name.return_value = "rop_alembic"

        result = ht.events.events.rop_render._get_target_file(mock_node)

        assert result == mock_path
        mock_node.evalParm.assert_called_with("filename")

    def test_ifd(self, mocker):
        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.name.return_value = "ifd"

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.type.return_value = mock_type

        mock_path = mocker.MagicMock(spec=str)

        # Return True for soho_outputmode (writing ifd) and the path.
        mock_node.evalParm.side_effect = (True, mock_path)

        result = ht.events.events.rop_render._get_target_file(mock_node)

        assert result == mock_path
        mock_node.evalParm.assert_any_call("soho_outputmode")
        mock_node.evalParm.assert_any_call("soho_diskfile")

        mock_node.reset_mock()

        # Try again but with writing an image.
        mock_node.evalParm.side_effect = (False, "/var/tmp/test.exr")

        result = ht.events.events.rop_render._get_target_file(mock_node)

        assert result == "/var/tmp/test.exr"
        mock_node.evalParm.assert_any_call("soho_outputmode")
        mock_node.evalParm.assert_any_call("vm_picture")

    def test_unknown(self, mocker):
        mock_type = mocker.MagicMock(spec=hou.NodeType)
        mock_type.name.return_value = mocker.MagicMock(spec=str)

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.type.return_value = mock_type

        result = ht.events.events.rop_render._get_target_file(mock_node)

        assert result is None


class Test__print_frame_write(object):
    """Test ht.events.events.rop_render._print_frame_write."""

    def test_no_path(self, mocker):
        mock_node = mocker.MagicMock(spec=hou.Node)
        scriptargs = {"node": mock_node}

        ht.events.events.rop_render._print_frame_write(scriptargs)

        mock_node.parm.assert_not_called()

    def test_post_script(self, mocker):
        mock_logger = mocker.patch("ht.events.events.rop_render._logger")

        mock_script = mocker.MagicMock(spec=str)
        mock_script.__len__.return_value = 1

        mock_parm = mocker.MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = mock_script

        mock_node = mocker.MagicMock(spec=hou.Node)
        mock_node.parm.return_value = mock_parm

        scriptargs = {"node": mock_node, "path": mocker.MagicMock(spec=str)}

        ht.events.events.rop_render._print_frame_write(scriptargs)

        mock_logger.info.assert_not_called()

    def test_path_no_post_script(self, mocker):
        mock_logger = mocker.patch("ht.events.events.rop_render._logger")

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
