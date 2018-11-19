"""Test the ht.pyfilter.operations.zdepth module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import argparse
import coverage
from mock import MagicMock, call, patch
import unittest

# Houdini Toolbox Imports
from ht.pyfilter.manager import PyFilterManager
from ht.pyfilter.operations import zdepth

cov = coverage.coverage(data_suffix=True, source=["ht.pyfilter.operations.zdepth"], branch=True)
cov.start()

reload(zdepth)

# =============================================================================
# CLASSES
# =============================================================================

class Test_ZDepthPass(unittest.TestCase):
    """Test the houdini_submission.pyfilter.operations.zdepth.ZDepthPass class.

    """

    def setUp(self):
        super(Test_ZDepthPass, self).setUp()

        modules = {"mantra": MagicMock()}
        self.patcher = patch.dict("sys.modules", modules)
        self.patcher.start()

    def tearDown(self):
        super(Test_ZDepthPass, self).tearDown()

        self.patcher.stop()

    def test___init__(self):
        mock_manager = MagicMock(spec=PyFilterManager)
        op = zdepth.ZDepthPass(mock_manager)

        self.assertEqual(op._data, {"set_pz": False})
        self.assertFalse(op._active)

    # Properties

    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_all_passes(self):
        op = zdepth.ZDepthPass(None)
        op._active = True
        self.assertTrue(op.active)

        op = zdepth.ZDepthPass(None)
        op._active = False
        op.active = True
        self.assertTrue(op._active)

    # Static Methods

    def test_build_arg_string(self):
        result = zdepth.ZDepthPass.build_arg_string()

        self.assertEquals(result, "")

        # Disable deep image path
        result = zdepth.ZDepthPass.build_arg_string(
            active=True
        )

        self.assertEquals(
            result,
            "--zdepth"
        )

    def test_register_parser_args(self):
        parser = argparse.ArgumentParser()

        zdepth.ZDepthPass.register_parser_args(parser)

        arg_names = {"--zdepth"}

        registered_args = []

        for action in parser._optionals._actions:
            registered_args.extend(action.option_strings)

        registered_args = set(registered_args)

        msg = "Expected args not registered: {}".format(
            ", ".join(arg_names - registered_args)
        )

        self.assertTrue(
            arg_names.issubset(registered_args),
            msg=msg
        )

    # Methods

    @patch("__main__.zdepth.set_property")
    @patch("__main__.zdepth.get_property")
    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_filterInstance__obj_matte(self, mock_get, mock_set):
        mock_get.side_effect = (True, False, "")

        op = zdepth.ZDepthPass(None)

        op.filterInstance()

        calls = [
            call("object:overridedetail", True),
            call("object:phantom", 1)
        ]

        mock_set.asset_has_calls(calls)

    @patch("__main__.zdepth.set_property")
    @patch("__main__.zdepth.get_property")
    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_filterInstance__obj_phantom(self, mock_get, mock_set):
        mock_get.side_effect = (False, True, "")

        op = zdepth.ZDepthPass(None)

        op.filterInstance()

        calls = [
            call("object:overridedetail", True),
            call("object:phantom", 1)
        ]

        mock_set.asset_has_calls(calls)

    @patch("__main__.zdepth.set_property")
    @patch("__main__.zdepth.get_property")
    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_filterInstance__surface_matte(self, mock_get, mock_set):
        mock_get.side_effect = (False, False, "matte")

        op = zdepth.ZDepthPass(None)

        op.filterInstance()

        calls = [
            call("object:overridedetail", True),
            call("object:phantom", 1)
        ]

        mock_set.asset_has_calls(calls)

    @patch("__main__.zdepth.set_property")
    @patch("__main__.zdepth.get_property")
    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_filterInstance__set_shader(self, mock_get, mock_set):
        mock_get.side_effect = (False, False, "")

        op = zdepth.ZDepthPass(None)

        op.filterInstance()

        calls = [
            call("object:overridedetail", True),
            call("object:surface", op.CONST_SHADER.split()),
            call("object:displace", None)
        ]

        mock_set.asset_has_calls(calls)

    @patch("__main__.zdepth.set_property")
    @patch("__main__.zdepth.get_property")
    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_filterPlane_Pz(self, mock_get, mock_set):
        mock_get.return_value = "Pz"

        op = zdepth.ZDepthPass(None)
        op._data = {"set_pz": False}

        op.filterPlane()

        self.assertTrue(op.data["set_pz"])

        mock_set.assert_not_called()

    @patch("__main__.zdepth.set_property")
    @patch("__main__.zdepth.get_property")
    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_filterPlane_Pz_already_set(self, mock_get, mock_set):
        mock_get.return_value = "Pz"

        op = zdepth.ZDepthPass(None)
        op._data = {"set_pz": True}

        op.filterPlane()

        mock_set.assert_called_with("plane:disable", True)

    @patch("__main__.zdepth.set_property")
    @patch("__main__.zdepth.get_property")
    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_filterPlane_no_pz_C(self, mock_get, mock_set):
        mock_get.return_value = "C"

        op = zdepth.ZDepthPass(None)
        op._data = {"set_pz": False}

        op.filterPlane()

        self.assertFalse(op.data["set_pz"])

        mock_set.assert_not_called()

    @patch("__main__.zdepth.set_property")
    @patch("__main__.zdepth.get_property")
    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_filterPlane_no_pz_Of(self, mock_get, mock_set):
        mock_get.return_value = "Of"

        op = zdepth.ZDepthPass(None)
        op._data = {"set_pz": False}

        op.filterPlane()

        self.assertFalse(op.data["set_pz"])

        mock_set.assert_called_with("plane:disable", True)

    @patch("__main__.zdepth.set_property")
    @patch("__main__.zdepth.get_property")
    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_filterPlane_not_set_misc_channel(self, mock_get, mock_set):
        mock_get.return_value = "channel1"

        op = zdepth.ZDepthPass(None)
        op._data = {"set_pz": False}

        op.filterPlane()

        self.assertTrue(op.data["set_pz"])

        calls = [
            call("plane:variable", "Pz"),
            call("plane:vextype", "float"),
            call("plane:channel", "Pz"),
            call("plane:pfilter", "minmax min"),
            call("plane:quantize", None),
        ]

        mock_set.assert_has_calls(calls)

    @patch("__main__.zdepth.set_property")
    @patch("__main__.zdepth.get_property")
    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_filterPlane_set_pz_misc(self, mock_get, mock_set):
        mock_get.return_value = "channel1"

        op = zdepth.ZDepthPass(None)
        op._data = {"set_pz": True}

        op.filterPlane()

        mock_set.assert_called_with("plane:disable", True)

    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_process_parsed_args(self):
        namespace = argparse.Namespace()
        namespace.zdepth = True

        op = zdepth.ZDepthPass(None)

        op._active = False

        op.process_parsed_args(namespace)

        self.assertTrue(op.active)

    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_process_parsed_args__none(self):
        namespace = argparse.Namespace()
        namespace.zdepth = None

        op = zdepth.ZDepthPass(None)

        op._active = False

        op.process_parsed_args(namespace)

        self.assertFalse(op.active)

    @patch.object(zdepth.ZDepthPass, "__init__", lambda x, y: None)
    def test_should_run(self):
        op = zdepth.ZDepthPass(None)

        op._active = False
        self.assertFalse(op.should_run())

        op._active = True
        self.assertTrue(op.should_run())

# =============================================================================

if __name__ == '__main__':
    # Run the tests.
    try:
        unittest.main()
    finally:
        cov.stop()
        cov.html_report()
        cov.save()
