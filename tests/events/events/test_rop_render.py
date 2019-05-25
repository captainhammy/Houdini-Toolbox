"""Tests for ht.events.event.rop_render module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
from mock import MagicMock, patch
import unittest

# Houdini Toolbox Imports
import ht.events.events.rop_render

from ht.events.item import HoudiniEventItem
from ht.events.types import RopEvents

# Houdini Imports
import hou

reload(ht.events.events.rop_render)

# =============================================================================
# CLASSES
# =============================================================================

class Test_RopRenderEvent(unittest.TestCase):
    """Test ht.events.events.rop_render.RopRendeEvent class."""

    def test___init__(self):
        event = ht.events.events.rop_render.RopRenderEvent()

        self.assertIsNone(event._frame_start)
        self.assertIsNone(event._render_start)

        expected_map = {
            RopEvents.PreRender: HoudiniEventItem((event.pre_render,)),
            RopEvents.PreFrame: HoudiniEventItem((event.pre_frame,)),
            RopEvents.PostFrame: HoudiniEventItem((event.post_frame,)),
            RopEvents.PostRender: HoudiniEventItem((event.post_render,)),
            RopEvents.PostWrite: HoudiniEventItem((event.post_write,)),
        }

        self.assertEqual(event.event_map, expected_map)

    # Methods

    # pre_frame

    @patch("ht.events.events.rop_render.LOGGER")
    @patch.object(ht.events.events.rop_render.RopRenderEvent, "__init__", lambda x: None)
    def test_pre_frame(self, mock_logger):
        event = ht.events.events.rop_render.RopRenderEvent()
        event._frame_start = None

        scriptargs = {"time": 123, "frame": 1001}

        event.pre_frame(scriptargs)

        self.assertEqual(event._frame_start, 123)

        mock_logger.info.assert_called()

    # pre_render

    @patch("ht.events.events.rop_render.LOGGER")
    @patch.object(ht.events.events.rop_render.RopRenderEvent, "__init__", lambda x: None)
    def test_pre_render__with_frame_range(self, mock_logger):
        event = ht.events.events.rop_render.RopRenderEvent()
        event._render_start = None

        scriptargs = {"time": 123, "frame_range": (1001, 1015, 1)}

        event.pre_render(scriptargs)

        self.assertEqual(event._render_start, 123)

        mock_logger.info.assert_called()

    @patch("ht.events.events.rop_render.LOGGER")
    @patch.object(ht.events.events.rop_render.RopRenderEvent, "__init__", lambda x: None)
    def test_pre_render__no_frame_range(self, mock_logger):
        event = ht.events.events.rop_render.RopRenderEvent()
        event._render_start = None

        scriptargs = {"time": 123, "frame_range": None}

        event.pre_render(scriptargs)

        self.assertEqual(event._render_start, 123)

        mock_logger.info.assert_called()

    # post_frame

    @patch("ht.events.events.rop_render.LOGGER")
    @patch("ht.events.events.rop_render._print_frame_write")
    @patch.object(ht.events.events.rop_render.RopRenderEvent, "__init__", lambda x: None)
    def test_post_frame__valid_start_frame(self, mock_print, mock_logger):
        event = ht.events.events.rop_render.RopRenderEvent()
        event._frame_start = 123

        scriptargs = {"time": 456, "frame": 1001}

        event.post_frame(scriptargs)

        mock_print.assert_called_with(scriptargs)

        mock_logger.info.assert_called()

    @patch("ht.events.events.rop_render.LOGGER")
    @patch("ht.events.events.rop_render._print_frame_write")
    @patch.object(ht.events.events.rop_render.RopRenderEvent, "__init__", lambda x: None)
    def test_post_frame__no_start_frame(self, mock_print, mock_logger):
        event = ht.events.events.rop_render.RopRenderEvent()
        event._frame_start = None

        scriptargs = {"frame": 1001}

        event.post_frame(scriptargs)

        mock_print.assert_called_with(scriptargs)

        mock_logger.info.assert_called()

    # post_render

    @patch("ht.events.events.rop_render.LOGGER")
    @patch.object(ht.events.events.rop_render.RopRenderEvent, "__init__", lambda x: None)
    def test_post_render__valid_start_frame(self, mock_logger):
        event = ht.events.events.rop_render.RopRenderEvent()
        event._render_start = 123

        scriptargs = {"time": 456,}

        event.post_render(scriptargs)

        mock_logger.info.assert_called()

    @patch("ht.events.events.rop_render.LOGGER")
    @patch.object(ht.events.events.rop_render.RopRenderEvent, "__init__", lambda x: None)
    def test_post_render__no_start_frame(self, mock_logger):
        event = ht.events.events.rop_render.RopRenderEvent()
        event._render_start = None

        event.post_render({})

        mock_logger.info.assert_called()

    # post_write

    @patch("ht.events.events.rop_render.LOGGER")
    @patch.object(ht.events.events.rop_render.RopRenderEvent, "__init__", lambda x: None)
    def test_post_write__valid_path(self, mock_logger):
        event = ht.events.events.rop_render.RopRenderEvent()

        scriptargs = {"frame": 1001, "path": MagicMock(spec=str)}

        event.post_write(scriptargs)

        mock_logger.info.assert_called()

    @patch("ht.events.events.rop_render.LOGGER")
    @patch.object(ht.events.events.rop_render.RopRenderEvent, "__init__", lambda x: None)
    def test_post_write__no_path(self, mock_logger):
        event = ht.events.events.rop_render.RopRenderEvent()

        scriptargs = {"frame": 1001}

        event.post_write(scriptargs)

        mock_logger.info.assert_called()


class Test__get_target_file(unittest.TestCase):
    """Test ht.events.events.rop_render._get_target_file."""

    def test_geometry(self):
        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.name.return_value = "geometry"

        mock_node = MagicMock(spec=hou.Node)
        mock_node.type.return_value = mock_type

        mock_node.evalParm.return_value = "/var/tmp/test.bgeo"

        result = ht.events.events.rop_render._get_target_file(mock_node)

        self.assertEqual(result, "/var/tmp/test.bgeo")
        mock_node.evalParm.assert_called_with("sopoutput")

        # Try again but with rop_geometry.
        mock_type.name.return_value = "rop_geometry"

        result = ht.events.events.rop_render._get_target_file(mock_node)

        self.assertEqual(result, "/var/tmp/test.bgeo")
        mock_node.evalParm.assert_called_with("sopoutput")

    def test_alembic(self):
        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.name.return_value = "alembic"

        mock_node = MagicMock(spec=hou.Node)
        mock_node.type.return_value = mock_type

        mock_node.evalParm.return_value = "/var/tmp/test.abc"

        result = ht.events.events.rop_render._get_target_file(mock_node)

        self.assertEqual(result, "/var/tmp/test.abc")
        mock_node.evalParm.assert_called_with("filename")

        # Try again but with rop_alembic.
        mock_type.name.return_value = "rop_alembic"

        result = ht.events.events.rop_render._get_target_file(mock_node)

        self.assertEqual(result, "/var/tmp/test.abc")
        mock_node.evalParm.assert_called_with("filename")

    def test_ifd(self):
        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.name.return_value = "ifd"

        mock_node = MagicMock(spec=hou.Node)
        mock_node.type.return_value = mock_type

        # Return True for soho_outputmode (writing ifd) and the path.
        mock_node.evalParm.side_effect = (True, "/var/tmp/test.ifd")

        result = ht.events.events.rop_render._get_target_file(mock_node)

        self.assertEqual(result, "/var/tmp/test.ifd")
        mock_node.evalParm.assert_any_call("soho_outputmode")
        mock_node.evalParm.assert_any_call("soho_diskfile")

        mock_node.reset_mock()

        # Try again but with writing an image.
        mock_node.evalParm.side_effect = (False, "/var/tmp/test.exr")

        result = ht.events.events.rop_render._get_target_file(mock_node)

        self.assertEqual(result, "/var/tmp/test.exr")
        mock_node.evalParm.assert_any_call("soho_outputmode")
        mock_node.evalParm.assert_any_call("vm_picture")

    def test_unknown(self):
        mock_type = MagicMock(spec=hou.NodeType)
        mock_type.name.return_value = "unknown"

        mock_node = MagicMock(spec=hou.Node)
        mock_node.type.return_value = mock_type

        result = ht.events.events.rop_render._get_target_file(mock_node)

        self.assertIsNone(result)


class Test__print_frame_write(unittest.TestCase):
    """Test ht.events.events.rop_render._print_frame_write."""

    def test_no_path(self):
        mock_node = MagicMock(spec=hou.Node)
        scriptargs = {"node": mock_node}

        ht.events.events.rop_render._print_frame_write(scriptargs)

        mock_node.parm.assert_not_called()

    @patch("ht.events.events.rop_render.LOGGER")
    def test_post_script(self, mock_logger):
        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = "a dummy script"

        mock_node = MagicMock(spec=hou.Node)
        mock_node.parm.return_value = mock_parm

        scriptargs = {"node": mock_node, "path": "/var/tmp/test.bgeo"}

        ht.events.events.rop_render._print_frame_write(scriptargs)

        mock_logger.info.assert_not_called()

    @patch("ht.events.events.rop_render.LOGGER")
    def test_path_no_post_script(self, mock_logger):
        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.eval.return_value = ""

        mock_node = MagicMock(spec=hou.Node)
        mock_node.parm.return_value = mock_parm

        scriptargs = {"node": mock_node, "frame": 1001, "path": "/var/tmp/test.bgeo"}

        ht.events.events.rop_render._print_frame_write(scriptargs)

        mock_logger.info.assert_called()


class Test_build_scriptargs(unittest.TestCase):
    """Test ht.events.events.rop_render.build_scriptargs."""

    @patch("ht.events.events.rop_render._get_target_file")
    @patch("ht.events.events.rop_render.hou")
    @patch("ht.events.events.rop_render.time")
    def test_no_args(self, mock_time, mock_hou, mock_get):
        """Test where there all args are default."""
        mock_hou.frame.return_value = 1001.0
        mock_time.time.return_value = 123

        result = ht.events.events.rop_render.build_scriptargs()

        expected = {
            "node": None,
            "frame": 1001.0,
            "frame_range": None,
            "time": 123,
        }

        self.assertEqual(result, expected)

        mock_get.assert_not_called()

    @patch("ht.events.events.rop_render._get_target_file")
    @patch("ht.events.events.rop_render.hou")
    @patch("ht.events.events.rop_render.time")
    def test_no_trange(self, mock_time, mock_hou, mock_get):
        """Test where there is no 'trange' parm."""
        mock_hou.frame.return_value = 1001.0
        mock_time.time.return_value = 123

        mock_node = MagicMock(spec=hou.Node)
        mock_node.parm.return_value = None

        mock_get.return_value = "/var/tmp/test.bgeo"

        result = ht.events.events.rop_render.build_scriptargs(mock_node)

        expected = {
            "node": mock_node,
            "frame": 1001.0,
            "frame_range": None,
            "time": 123,
            "path": "/var/tmp/test.bgeo",
        }

        self.assertEqual(result, expected)

        mock_get.assert_called_with(mock_node)

    @patch("ht.events.events.rop_render._get_target_file")
    @patch("ht.events.events.rop_render.hou")
    @patch("ht.events.events.rop_render.time")
    def test_trange_off(self, mock_time, mock_hou, mock_get):
        """Test where we can't get a frame range because it is off."""
        mock_hou.frame.return_value = 1001.0
        mock_time.time.return_value = 123

        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.evalAsString.return_value = "off"

        mock_node = MagicMock(spec=hou.Node)
        mock_node.parm.return_value = mock_parm

        mock_get.return_value = "/var/tmp/test.bgeo"

        result = ht.events.events.rop_render.build_scriptargs(mock_node)

        expected = {
            "node": mock_node,
            "frame": 1001.0,
            "frame_range": None,
            "time": 123,
            "path": "/var/tmp/test.bgeo"
        }

        self.assertEqual(result, expected)

        mock_get.assert_called_with(mock_node)

    @patch("ht.events.events.rop_render._get_target_file")
    @patch("ht.events.events.rop_render.hou")
    @patch("ht.events.events.rop_render.time")
    def test_found_frame_range(self, mock_time, mock_hou, mock_get):
        """Test where we actually get a frame range."""
        mock_hou.frame.return_value = 1001.0
        mock_time.time.return_value = 123

        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.evalAsString.return_value = "normal"

        mock_node = MagicMock(spec=hou.Node)
        mock_node.parm.return_value = mock_parm
        mock_node.evalParmTuple.return_value = (1001, 1015, 1)

        mock_get.return_value = "/var/tmp/test.bgeo"

        result = ht.events.events.rop_render.build_scriptargs(mock_node)

        expected = {
            "node": mock_node,
            "frame": 1001.0,
            "frame_range": (1001, 1015, 1),
            "time": 123,
            "path": "/var/tmp/test.bgeo"
        }

        self.assertEqual(result, expected)

        mock_get.assert_called_with(mock_node)

    @patch("ht.events.events.rop_render._get_target_file")
    @patch("ht.events.events.rop_render.hou")
    @patch("ht.events.events.rop_render.time")
    def test_no_path(self, mock_time, mock_hou, mock_get):
        """Test where we actually get a frame range."""
        mock_hou.frame.return_value = 1001.0
        mock_time.time.return_value = 123

        mock_parm = MagicMock(spec=hou.Parm)
        mock_parm.evalAsString.return_value = "normal"

        mock_node = MagicMock(spec=hou.Node)
        mock_node.parm.return_value = mock_parm
        mock_node.evalParmTuple.return_value = (1001, 1015, 1)

        mock_get.return_value = None

        result = ht.events.events.rop_render.build_scriptargs(mock_node)

        expected = {
            "node": mock_node,
            "frame": 1001.0,
            "frame_range": (1001, 1015, 1),
            "path": None,
            "time": 123
        }

        self.assertEqual(result, expected)

        mock_get.assert_called_with(mock_node)

# =============================================================================

if __name__ == '__main__':
    unittest.main()
