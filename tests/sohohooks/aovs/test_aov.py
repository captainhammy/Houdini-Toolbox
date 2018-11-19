
import coverage

import unittest

from mock import MagicMock, PropertyMock, call, patch

from ht.sohohooks.aovs import aov

cov = coverage.Coverage(data_suffix=True, source=["ht.sohohooks.aovs.aov"], branch=True)

cov.start()

reload(aov)

# =============================================================================
# CLASSES
# =============================================================================

class Test_AOV(unittest.TestCase):
    """Test ht.sohohooks.aovs.AOV object."""

    def setUp(self):
        super(Test_AOV, self).setUp()

        self.mock_soho = MagicMock()

        modules = {
            "soho": self.mock_soho
        }

        self.patcher = patch.dict("sys.modules", modules)
        self.patcher.start()

    def tearDown(self):
        super(Test_AOV, self).tearDown()

        self.patcher.stop()

    # __init__

    @patch.object(aov.AOV, "_update_data")
    @patch("__main__.aov.copy.copy")
    def test___init__(self, mock_copy, mock_update):
        data = {"key1", "value1"}

        inst = aov.AOV(data)

        mock_copy.assert_called_with(aov._DEFAULT_AOV_DATA)
        mock_update.assert_called_with(data)

    # __cmp__

    @patch("__main__.aov.AOV.variable", new_callable=PropertyMock(return_value="P"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___cmp___equal(self, mock_variable):
        inst1 = aov.AOV(None)

        inst2 = MagicMock(spec=aov.AOV)
        type(inst2).variable = PropertyMock(return_value="P")

        result = inst1.__cmp__(inst2)

        self.assertEqual(result, 0)

    @patch("__main__.aov.AOV.variable", new_callable=PropertyMock(return_value="N"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___cmp___not_equal(self, mock_variable):
        inst1 = aov.AOV(None)

        inst2 = MagicMock(spec=aov.AOV)
        type(inst2).variable = PropertyMock(return_value="P")

        result = inst1.__cmp__(inst2)

        self.assertNotEqual(result, 0)

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___cmp___non_aov(self):
        inst1 = aov.AOV(None)
        inst2 = MagicMock()

        result = inst1.__cmp__(inst2)

        self.assertNotEqual(result, 0)

    # __hash__

    @patch("__main__.aov.AOV.variable", new_callable=PropertyMock(return_value="N"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___hash__(self, mock_variable):
        inst1 = aov.AOV(None)

        result = inst1.__hash__()

        self.assertEqual(result, hash("N"))

        self.assertEqual(hash(inst1), hash("N"))

    # __str__

    @patch("__main__.aov.AOV.variable", new_callable=PropertyMock(return_value="N"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test___str__(self, mock_variable):
        inst1 = aov.AOV(None)

        result = inst1.__str__()

        self.assertEqual(str(inst1), "N")

        self.assertEqual(result, "N")

    # _light_export_planes

    @patch("__main__.aov._write_data_to_ifd")
    @patch("__main__.aov.AOV.lightexport", new_callable=PropertyMock(return_value=None))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__light_export_planes__no_lightexport(self, mock_lightexport, mock_write):
        inst = aov.AOV(None)

        data = {"key": "value"}
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        now = 123

        inst._light_export_planes(data, mock_wrangler, mock_cam, now)

        mock_write.assert_called_with(data, mock_wrangler, mock_cam, now)

    @patch("__main__.aov._write_light")
    @patch("__main__.aov.AOV.lightexport_select", new_callable=PropertyMock)
    @patch("__main__.aov.AOV.lightexport_scope", new_callable=PropertyMock)
    @patch("__main__.aov.AOV.lightexport", new_callable=PropertyMock)
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__light_export_planes__per_light(self, mock_lightexport, mock_scope, mock_select, mock_write):
        mock_lightexport.return_value = "per-light"
        mock_scope.return_value = "scope"
        mock_select.return_value = "select"

        inst = aov.AOV(None)

        mock_light1 = MagicMock()
        mock_light2 = MagicMock()

        lights = [mock_light1, mock_light2]

        data = {"channel": "channel"}
        mock_wrangler = MagicMock()

        mock_cam = MagicMock()
        mock_cam.objectList.return_value = lights
        now = 123

        inst._light_export_planes(data, mock_wrangler, mock_cam, now)

        mock_cam.objectList.assert_called_with("objlist:light", now, "scope", "select")

        calls = [
            call(mock_light1, "channel", data, mock_wrangler, mock_cam, now),
            call(mock_light2, "channel", data, mock_wrangler, mock_cam, now)
        ]

        mock_write.assert_has_calls(calls)

    @patch("__main__.aov._write_single_channel")
    @patch("__main__.aov.AOV.lightexport_select", new_callable=PropertyMock)
    @patch("__main__.aov.AOV.lightexport_scope", new_callable=PropertyMock)
    @patch("__main__.aov.AOV.lightexport", new_callable=PropertyMock)
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__light_export_planes__single(self, mock_lightexport, mock_scope, mock_select, mock_write):
        mock_lightexport.return_value = "single"
        mock_scope.return_value = "scope"
        mock_select.return_value = "select"

        inst = aov.AOV(None)

        mock_light1 = MagicMock()
        mock_light2 = MagicMock()

        lights = [mock_light1, mock_light2]

        data = {"channel": "channel"}
        mock_wrangler = MagicMock()

        mock_cam = MagicMock()
        mock_cam.objectList.return_value = lights
        now = 123

        inst._light_export_planes(data, mock_wrangler, mock_cam, now)

        mock_cam.objectList.assert_called_with("objlist:light", now, "scope", "select")

        mock_write.assert_called_with(lights, data, mock_wrangler, mock_cam, now)

    @patch("__main__.aov._write_per_category")
    @patch("__main__.aov.AOV.lightexport_select", new_callable=PropertyMock)
    @patch("__main__.aov.AOV.lightexport_scope", new_callable=PropertyMock)
    @patch("__main__.aov.AOV.lightexport", new_callable=PropertyMock)
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__light_export_planes__per_category(self, mock_lightexport, mock_scope, mock_select, mock_write):
        mock_lightexport.return_value = "per-category"
        mock_scope.return_value = "scope"
        mock_select.return_value = "select"

        inst = aov.AOV(None)

        mock_light1 = MagicMock()
        mock_light2 = MagicMock()

        lights = [mock_light1, mock_light2]

        data = {"channel": "channel"}
        mock_wrangler = MagicMock()

        mock_cam = MagicMock()
        mock_cam.objectList.return_value = lights
        now = 123

        inst._light_export_planes(data, mock_wrangler, mock_cam, now)

        mock_cam.objectList.assert_called_with("objlist:light", now, "scope", "select")

        mock_write.assert_called_with(lights, "channel", data, mock_wrangler, mock_cam, now)

    @patch("__main__.aov.AOV.lightexport_select", new_callable=PropertyMock)
    @patch("__main__.aov.AOV.lightexport_scope", new_callable=PropertyMock)
    @patch("__main__.aov.AOV.lightexport", new_callable=PropertyMock)
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__light_export_planes__bad_value(self, mock_lightexport, mock_scope, mock_select):
        mock_lightexport.return_value = "bad_value"
        mock_scope.return_value = "scope"
        mock_select.return_value = "select"

        inst = aov.AOV(None)

        mock_light1 = MagicMock()
        mock_light2 = MagicMock()

        lights = [mock_light1, mock_light2]

        data = {"channel": "channel"}
        mock_wrangler = MagicMock()

        mock_cam = MagicMock()
        mock_cam.objectList.return_value = lights
        now = 123

        with self.assertRaises(aov.InvalidAOVValueError):
            inst._light_export_planes(data, mock_wrangler, mock_cam, now)

        mock_cam.objectList.assert_called_with("objlist:light", now, "scope", "select")

    # _update_data

    @patch("__main__.aov.AOV._verify_internal_data")
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__update_data__unknown(self, mock_verify):
        inst = aov.AOV(None)
        inst._data = {}

        data = {"key": None}

        with patch.dict(aov.ALLOWABLE_VALUES, {}, clear=True):
            inst._update_data(data)

        self.assertEqual(inst._data, {})

        mock_verify.assert_called()

    @patch("__main__.aov.AOV._verify_internal_data")
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__update_data__settable(self, mock_verify):
        inst = aov.AOV(None)
        inst._data = {"key": None}

        data = {"key": "value"}

        with patch.dict(aov.ALLOWABLE_VALUES, {}, clear=True):
            inst._update_data(data)

        self.assertEqual(inst._data, {"key": "value"})

        mock_verify.assert_called()

    @patch("__main__.aov.AOV._verify_internal_data")
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__update_data__allowable_valid(self, mock_verify):
        inst = aov.AOV(None)
        inst._data = {"key": None}

        data = {"key": "value1"}

        allowable = {
            "key": ("value1", "value2")
        }

        with patch.dict(aov.ALLOWABLE_VALUES, allowable, clear=True):
            inst._update_data(data)

        self.assertEqual(inst._data, {"key": "value1"})

        mock_verify.assert_called()

    @patch("__main__.aov.AOV._verify_internal_data")
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__update_data__allowable_invalid(self, mock_verify):
        inst = aov.AOV(None)
        inst._data = {"key": None}

        data = {"key": "value3"}

        allowable = {
            "key": ("value1", "value2")
        }

        with patch.dict(aov.ALLOWABLE_VALUES, allowable, clear=True):
            with self.assertRaises(aov.InvalidAOVValueError):
                inst._update_data(data)

    # _verify_internal_data

    @patch("__main__.aov.AOV.variable", new_callable=PropertyMock)
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__verify_internal_data__no_variable(self, mock_variable):
        mock_variable.return_value = None

        inst = aov.AOV(None)

        with self.assertRaises(aov.MissingVariableError):
            inst._verify_internal_data()

    @patch("__main__.aov.AOV.vextype", new_callable=PropertyMock)
    @patch("__main__.aov.AOV.variable", new_callable=PropertyMock)
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__verify_internal_data__no_vextype(self, mock_variable, mock_vextype):
        mock_variable.return_value = "variable"
        mock_vextype.return_value = None

        inst = aov.AOV(None)

        with self.assertRaises(aov.MissingVexTypeError):
            inst._verify_internal_data()

    @patch("__main__.aov.AOV.vextype", new_callable=PropertyMock)
    @patch("__main__.aov.AOV.variable", new_callable=PropertyMock)
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test__verify_internal_data__valid(self, mock_variable, mock_vextype):
        mock_variable.return_value = "variable"
        mock_vextype.return_value = "vextype"

        inst = aov.AOV(None)

        inst._verify_internal_data()

    # properties

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_channel(self):
        inst = aov.AOV(None)
        inst._data = {"channel": "channel"}

        self.assertEqual(inst.channel, "channel")

        inst.channel = None

        self.assertIsNone(inst._data["channel"])

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_comment(self):
        inst = aov.AOV(None)
        inst._data = {"comment": "comment"}

        self.assertEqual(inst.comment, "comment")

        inst.comment = None

        self.assertIsNone(inst._data["comment"])

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_componentexport(self):
        inst = aov.AOV(None)
        inst._data = {"componentexport": True}

        self.assertTrue(inst.componentexport)

        inst.componentexport = False

        self.assertFalse(inst._data["componentexport"])

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_components(self):
        inst = aov.AOV(None)
        inst._data = {"components": ["component1", "component2"]}

        self.assertEqual(inst.components, ["component1", "component2"])

        inst.components = ["component3"]

        self.assertEqual(inst._data["components"], ["component3"])

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_exclude_from_dcm(self):
        inst = aov.AOV(None)
        inst._data = {"exclude_from_dcm": True}

        self.assertTrue(inst.exclude_from_dcm)

        inst.exclude_from_dcm = False

        self.assertFalse(inst._data["exclude_from_dcm"])

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_intrinsics(self):
        inst = aov.AOV(None)
        inst._data = {"intrinsics": ["intrinsic1", "intrinsic2"]}

        self.assertEqual(inst.intrinsics, ["intrinsic1", "intrinsic2"])

        inst.intrinsics = ["intrinsic3"]

        self.assertEqual(inst._data["intrinsics"], ["intrinsic3"])

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_lightexport(self):
        inst = aov.AOV(None)
        inst._data = {"lightexport": "lightexport"}

        self.assertEqual(inst.lightexport, "lightexport")

        inst.lightexport = None

        self.assertIsNone(inst._data["lightexport"])

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_lightexport_select(self):
        inst = aov.AOV(None)
        inst._data = {"lightexport_select": "lightexport_select"}

        self.assertEqual(inst.lightexport_select, "lightexport_select")

        inst.lightexport_select = None

        self.assertIsNone(inst._data["lightexport_select"])

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_lightexport_scope(self):
        inst = aov.AOV(None)
        inst._data = {"lightexport_scope": "lightexport_scope"}

        self.assertEqual(inst.lightexport_scope, "lightexport_scope")

        inst.lightexport_scope = None

        self.assertIsNone(inst._data["lightexport_scope"])

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_path(self):
        inst = aov.AOV(None)
        inst._data = {"path": "/path/to/file.json"}

        self.assertEqual(inst.path, "/path/to/file.json")

        inst.path = None

        self.assertIsNone(inst._data["path"])

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_pfilter(self):
        inst = aov.AOV(None)
        inst._data = {"pfilter": "pfilter"}

        self.assertEqual(inst.pfilter, "pfilter")

        inst.pfilter = None

        self.assertIsNone(inst._data["pfilter"])

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_planefile(self):
        inst = aov.AOV(None)
        inst._data = {"planefile": "/path/to/plane.exr"}

        self.assertEqual(inst.planefile, "/path/to/plane.exr")

        inst.planefile = None

        self.assertIsNone(inst._data["planefile"])

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_priority(self):
        inst = aov.AOV(None)
        inst._data = {"priority": 1}

        self.assertEqual(inst.priority, 1)

        inst.priority = None

        self.assertIsNone(inst._data["priority"])

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_quantize(self):
        inst = aov.AOV(None)
        inst._data = {"quantize": "float"}

        self.assertEqual(inst.quantize, "float")

        inst.quantize = None

        self.assertIsNone(inst._data["quantize"])

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_sfilter(self):
        inst = aov.AOV(None)
        inst._data = {"sfilter": "sfilter"}

        self.assertEqual(inst.sfilter, "sfilter")

        inst.sfilter = None

        self.assertIsNone(inst._data["sfilter"])

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_variable(self):
        inst = aov.AOV(None)
        inst._data = {"variable": "P"}

        self.assertEqual(inst.variable, "P")

        inst.variable = "N"

        self.assertEqual(inst._data["variable"], "N")

    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_vextype(self):
        inst = aov.AOV(None)
        inst._data = {"vextype": "vector"}

        self.assertEqual(inst.vextype, "vector")

        inst.vextype = "half"

        self.assertEqual(inst._data["vextype"], "half")

    # _as_data

    @patch.object(aov.AOV, "priority", new_callable=PropertyMock(return_value=-1))
    @patch.object(aov.AOV, "comment", new_callable=PropertyMock(return_value=""))
    @patch.object(aov.AOV, "intrinsics", new_callable=PropertyMock(return_value=[]))
    @patch.object(aov.AOV, "lightexport", new_callable=PropertyMock(return_value=None))
    @patch.object(aov.AOV, "componentexport", new_callable=PropertyMock(return_value=None))
    @patch.object(aov.AOV, "exclude_from_dcm", new_callable=PropertyMock(return_value=None))
    @patch.object(aov.AOV, "pfilter", new_callable=PropertyMock(return_value=None))
    @patch.object(aov.AOV, "sfilter", new_callable=PropertyMock(return_value=None))
    @patch.object(aov.AOV, "quantize", new_callable=PropertyMock(return_value=None))
    @patch.object(aov.AOV, "channel", new_callable=PropertyMock(return_value=None))
    @patch.object(aov.AOV, "vextype", new_callable=PropertyMock(return_value="vector"))
    @patch.object(aov.AOV, "variable", new_callable=PropertyMock(return_value="P"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_as_data__defaults(self, *args, **kwargs):
        inst = aov.AOV(None)

        result = inst.as_data()

        self.assertEqual(result, {"variable": "P", "vextype": "vector"})

    @patch.object(aov.AOV, "priority", new_callable=PropertyMock(return_value=22))
    @patch.object(aov.AOV, "comment", new_callable=PropertyMock(return_value="This is a comment"))
    @patch.object(aov.AOV, "intrinsics", new_callable=PropertyMock(return_value=["intrinsic1"]))
    @patch.object(aov.AOV, "lightexport", new_callable=PropertyMock(return_value="per-category"))
    @patch.object(aov.AOV, "components", new_callable=PropertyMock(return_value=[]))
    @patch.object(aov.AOV, "componentexport", new_callable=PropertyMock(return_value=True))
    @patch.object(aov.AOV, "exclude_from_dcm", new_callable=PropertyMock(return_value=True))
    @patch.object(aov.AOV, "pfilter", new_callable=PropertyMock(return_value="minmax omedian"))
    @patch.object(aov.AOV, "sfilter", new_callable=PropertyMock(return_value="alpha"))
    @patch.object(aov.AOV, "quantize", new_callable=PropertyMock(return_value="float"))
    @patch.object(aov.AOV, "channel", new_callable=PropertyMock(return_value="Pworld"))
    @patch.object(aov.AOV, "vextype", new_callable=PropertyMock(return_value="vector"))
    @patch.object(aov.AOV, "variable", new_callable=PropertyMock(return_value="P"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_as_data__values_per_category_no_components(self, *args, **kwargs):
        inst = aov.AOV(None)

        result = inst.as_data()

        expected = {
            "variable": "P",
            "vextype": "vector",
            "channel": "Pworld",
            "quantize": "float",
            "sfilter": "alpha",
            "pfilter": "minmax omedian",
            "exclude_from_dcm": True,
            "componentexport": True,
            "lightexport": "per-category",
            "intrinsics": ["intrinsic1"],
            "comment": "This is a comment",
            "priority": 22
        }

        self.assertEqual(result, expected)

    @patch.object(aov.AOV, "priority", new_callable=PropertyMock(return_value=22))
    @patch.object(aov.AOV, "comment", new_callable=PropertyMock(return_value="This is a comment"))
    @patch.object(aov.AOV, "intrinsics", new_callable=PropertyMock(return_value=["intrinsic1"]))
    @patch.object(aov.AOV, "lightexport_select", new_callable=PropertyMock(return_value="* ^foo"))
    @patch.object(aov.AOV, "lightexport_scope", new_callable=PropertyMock(return_value="*"))
    @patch.object(aov.AOV, "lightexport", new_callable=PropertyMock(return_value="single"))
    @patch.object(aov.AOV, "components", new_callable=PropertyMock(return_value=["comp1"]))
    @patch.object(aov.AOV, "componentexport", new_callable=PropertyMock(return_value=True))
    @patch.object(aov.AOV, "exclude_from_dcm", new_callable=PropertyMock(return_value=True))
    @patch.object(aov.AOV, "pfilter", new_callable=PropertyMock(return_value="minmax omedian"))
    @patch.object(aov.AOV, "sfilter", new_callable=PropertyMock(return_value="alpha"))
    @patch.object(aov.AOV, "quantize", new_callable=PropertyMock(return_value="float"))
    @patch.object(aov.AOV, "channel", new_callable=PropertyMock(return_value="Pworld"))
    @patch.object(aov.AOV, "vextype", new_callable=PropertyMock(return_value="vector"))
    @patch.object(aov.AOV, "variable", new_callable=PropertyMock(return_value="P"))
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_as_data__values_exports_components(self, *args, **kwargs):
        inst = aov.AOV(None)

        result = inst.as_data()

        expected = {
            "variable": "P",
            "vextype": "vector",
            "channel": "Pworld",
            "quantize": "float",
            "sfilter": "alpha",
            "pfilter": "minmax omedian",
            "exclude_from_dcm": True,
            "componentexport": True,
            "components": ["comp1"],
            "lightexport": "single",
            "lightexport_scope": "*",
            "lightexport_select": "* ^foo",
            "intrinsics": ["intrinsic1"],
            "comment": "This is a comment",
            "priority": 22
        }

        self.assertEqual(result, expected)

    # write_to_ifd

    @patch.object(aov.AOV, "_light_export_planes")
    @patch.object(aov.AOV, "componentexport", new_callable=PropertyMock(return_value=False))
    @patch.object(aov.AOV, "variable", new_callable=PropertyMock(return_value="P"))
    @patch.object(aov.AOV, "channel", new_callable=PropertyMock(return_value=None))
    @patch.object(aov.AOV, "as_data")
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_write_to_ifd__no_channel_no_comp(self, mock_as_data, mock_channel, mock_variable, mock_component, mock_export):
        mock_as_data.return_value = {"key": "value"}

        inst = aov.AOV(None)

        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        now = 123

        inst.write_to_ifd(mock_wrangler, mock_cam, now)

        mock_export.assert_called_with(
            {"key": "value", "channel": "P"},
            mock_wrangler,
            mock_cam,
            now
        )

    @patch.object(aov.AOV, "_light_export_planes")
    @patch.object(aov.AOV, "componentexport", new_callable=PropertyMock(return_value=False))
    @patch.object(aov.AOV, "channel", new_callable=PropertyMock(return_value="Pworld"))
    @patch.object(aov.AOV, "as_data")
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_write_to_ifd__channel_no_comp(self, mock_as_data, mock_channel, mock_component, mock_export):
        mock_as_data.return_value = {"key": "value"}

        inst = aov.AOV(None)

        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        now = 123

        inst.write_to_ifd(mock_wrangler, mock_cam, now)

        mock_export.assert_called_with(
            {"key": "value", "channel": "Pworld"},
            mock_wrangler,
            mock_cam,
            now
        )

    @patch.object(aov.AOV, "_light_export_planes")
    @patch.object(aov.AOV, "components", new_callable=PropertyMock(return_value=[]))
    @patch.object(aov.AOV, "componentexport", new_callable=PropertyMock(return_value=True))
    @patch.object(aov.AOV, "channel", new_callable=PropertyMock(return_value="Pworld"))
    @patch.object(aov.AOV, "as_data")
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_write_to_ifd__export_no_comp(self, mock_as_data, mock_channel, mock_compexport, mock_components, mock_export):
        mock_as_data.return_value = {"key": "value"}

        inst = aov.AOV(None)

        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        now = 123

        mock_parm = MagicMock()
        self.mock_soho.SohoParm.return_value = mock_parm

        mock_cam.wrangle.return_value = {}

        inst.write_to_ifd(mock_wrangler, mock_cam, now)

        self.mock_soho.SohoParm.assert_called_with("vm_exportcomponents", "str", [''], skipdefault=False)

        mock_export.assert_not_called()

    @patch.object(aov.AOV, "_light_export_planes")
    @patch.object(aov.AOV, "components", new_callable=PropertyMock(return_value=[]))
    @patch.object(aov.AOV, "componentexport", new_callable=PropertyMock(return_value=True))
    @patch.object(aov.AOV, "channel", new_callable=PropertyMock(return_value="Pworld"))
    @patch.object(aov.AOV, "as_data")
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_write_to_ifd__export_components_from_node(self, mock_as_data, mock_channel, mock_compexport, mock_components, mock_export):
        mock_as_data.return_value = {"key": "value"}

        inst = aov.AOV(None)

        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        now = 123

        mock_parm = MagicMock()
        self.mock_soho.SohoParm.return_value = mock_parm

        mock_result = MagicMock()
        mock_result.Value = ["comp1 comp2"]

        mock_cam.wrangle.return_value = {
            "vm_exportcomponents": mock_result
        }

        inst.write_to_ifd(mock_wrangler, mock_cam, now)

        self.mock_soho.SohoParm.assert_called_with("vm_exportcomponents", "str", [''], skipdefault=False)

        calls = [
            call({"key": "value", "channel": "Pworld_comp1", "component": "comp1"}, mock_wrangler, mock_cam, now),
            call({"key": "value", "channel": "Pworld_comp2", "component": "comp2"}, mock_wrangler, mock_cam, now)
        ]

        mock_export.assert_has_calls(calls)

    @patch.object(aov.AOV, "_light_export_planes")
    @patch.object(aov.AOV, "components", new_callable=PropertyMock(return_value=["comp3", "comp4"]))
    @patch.object(aov.AOV, "componentexport", new_callable=PropertyMock(return_value=True))
    @patch.object(aov.AOV, "channel", new_callable=PropertyMock(return_value="Pworld"))
    @patch.object(aov.AOV, "as_data")
    @patch.object(aov.AOV, "__init__", lambda x, y: None)
    def test_write_to_ifd__export_components(self, mock_as_data, mock_channel, mock_compexport, mock_components, mock_export):
        mock_as_data.return_value = {"key": "value"}

        inst = aov.AOV(None)

        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        now = 123

        inst.write_to_ifd(mock_wrangler, mock_cam, now)

        calls = [
            call({"key": "value", "channel": "Pworld_comp3", "component": "comp3"}, mock_wrangler, mock_cam, now),
            call({"key": "value", "channel": "Pworld_comp4", "component": "comp4"}, mock_wrangler, mock_cam, now)
        ]

        mock_export.assert_has_calls(calls)


class Test_AOVGroup(unittest.TestCase):
    """Test ht.sohohooks.aovs.AOVGroup object."""

    # __init__

    def test___init__(self):
        group = aov.AOVGroup("name")

        self.assertEqual(group._aovs, [])
        self.assertEqual(group._comment, "")
        self.assertEqual(group._icon, None)
        self.assertEqual(group._includes, [])
        self.assertEqual(group._name, "name")
        self.assertEqual(group._path, None)
        self.assertEqual(group._priority, -1)

    # __cmp__

    @patch("__main__.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___cmp___equal(self, mock_name):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock(spec=aov.AOVGroup)
        type(group2).name = PropertyMock(return_value="name")

        result = group1.__cmp__(group2)

        self.assertEqual(result, 0)

    @patch("__main__.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name1"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___cmp___not_equal(self, mock_name):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock(spec=aov.AOVGroup)
        type(group2).name = PropertyMock(return_value="name2")

        result = group1.__cmp__(group2)

        self.assertNotEqual(result, 0)

    @patch("__main__.aov.AOVGroup.name", new_callable=PropertyMock(return_value="name1"))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test___cmp___non_group(self, mock_name):
        group1 = aov.AOVGroup(None)

        group2 = MagicMock()

        result = group1.__cmp__(group2)

        self.assertNotEqual(result, 0)

    # properties

    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test_aovs(self):
        mock_aov = MagicMock(spec=aov.AOV)

        group = aov.AOVGroup(None)
        group._aovs = [mock_aov]

        self.assertEqual(group.aovs, [mock_aov])

        with self.assertRaises(AttributeError):
            group.aovs = []

    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test_comment(self):
        group = aov.AOVGroup(None)

        group._comment = "comment"
        self.assertEqual(group.comment, "comment")

        group.comment = "new comment"
        self.assertEqual(group._comment, "new comment")

    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test_icon(self):
        group = aov.AOVGroup(None)

        group._icon = "icon"
        self.assertEqual(group.icon, "icon")

        group.icon = "new icon"
        self.assertEqual(group._icon, "new icon")

    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test_includes(self):
        group = aov.AOVGroup(None)
        group._includes = ["A", "B"]

        self.assertEqual(group.includes, ["A", "B"])

        with self.assertRaises(AttributeError):
            group.includes = ["C"]

    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test_name(self):
        group = aov.AOVGroup(None)

        group._name = "name"
        self.assertEqual(group.name, "name")

        with self.assertRaises(AttributeError):
            group.name = "test"

    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test_path(self):
        group = aov.AOVGroup(None)

        group._path = "path"
        self.assertEqual(group.path, "path")

        group.path = "new path"
        self.assertEqual(group._path, "new path")

    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test_priority(self):
        group = aov.AOVGroup(None)

        group._priority = 1
        self.assertEqual(group.priority, 1)

        group.priority = 2
        self.assertEqual(group._priority, 2)

    # clear

    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test_clear(self):
        mock_aov = MagicMock(spec=aov.AOV)

        group = aov.AOVGroup(None)
        group._aovs = [mock_aov]

        group.clear()

        self.assertEqual(group._aovs, [])

    @patch.object(aov.AOVGroup, "priority", new_callable=PropertyMock(return_value=-1))
    @patch.object(aov.AOVGroup, "comment", new_callable=PropertyMock(return_value=""))
    @patch.object(aov.AOVGroup, "aovs", new_callable=PropertyMock)
    @patch.object(aov.AOVGroup, "name", new_callable=PropertyMock(return_value="name"))
    @patch.object(aov.AOVGroup, "includes", new_callable=PropertyMock(return_value=["N", "P"]))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test_as_data__no_comment_or_priority(self, mock_includes, mock_name, mock_aovs, mock_comment, mock_priority):
        mock_aov1 = MagicMock(spec=aov.AOV)
        mock_aov1.variable = "Pz"

        mock_aov2 = MagicMock(spec=aov.AOV)
        mock_aov2.variable = "direct"

        mock_aovs.return_value = [mock_aov1, mock_aov2]

        expected = {
            "name": {
                "include": ["N", "P", "Pz", "direct"],

            }
        }

        group = aov.AOVGroup(None)

        result = group.as_data()

        self.assertEqual(result, expected)

    @patch.object(aov.AOVGroup, "priority", new_callable=PropertyMock(return_value=10))
    @patch.object(aov.AOVGroup, "comment", new_callable=PropertyMock(return_value="comment"))
    @patch.object(aov.AOVGroup, "aovs", new_callable=PropertyMock)
    @patch.object(aov.AOVGroup, "name", new_callable=PropertyMock(return_value="name"))
    @patch.object(aov.AOVGroup, "includes", new_callable=PropertyMock(return_value=["N", "P"]))
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test_as_data(self, mock_includes, mock_name, mock_aovs, mock_comment, mock_priority):
        mock_aov1 = MagicMock(spec=aov.AOV)
        mock_aov1.variable = "Pz"

        mock_aov2 = MagicMock(spec=aov.AOV)
        mock_aov2.variable = "direct"

        mock_aovs.return_value = [mock_aov1, mock_aov2]

        expected = {
            "name": {
                "include": ["N", "P", "Pz", "direct"],
                "priority": 10,
                "comment": "comment"

            }
        }

        group = aov.AOVGroup(None)

        result = group.as_data()

        self.assertEqual(result, expected)

    @patch.object(aov.AOVGroup, "aovs", new_callable=PropertyMock)
    @patch.object(aov.AOVGroup, "__init__", lambda x, y: None)
    def test_write_to_ifd(self, mock_aovs):
        mock_aov1 = MagicMock(spec=aov.AOV)
        mock_aov2 = MagicMock(spec=aov.AOV)

        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        now = 123

        mock_aovs.return_value = [mock_aov1, mock_aov2]

        group = aov.AOVGroup(None)

        group.write_to_ifd(mock_wrangler, mock_cam, now)

        mock_aov1.write_to_ifd.assert_called_with(mock_wrangler, mock_cam, now)
        mock_aov2.write_to_ifd.assert_called_with(mock_wrangler, mock_cam, now)






class Test__call_post_defplane(unittest.TestCase):

    def test(self):
        mock_IFDhooks = MagicMock()

        modules = {"IFDhooks": mock_IFDhooks}

        data = {
            "variable": "Pz",
            "vextype": "float",
            "planefile": "/var/tmp/foo.exr",
            "lightexport": "lightexport"
        }

        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        now = 123

        with patch.dict("sys.modules", modules):
            aov._call_post_defplane(
                data,
                mock_wrangler,
                mock_cam,
                now
            )

            mock_IFDhooks.call.assert_called_with(
                "post_defplane",
                data["variable"],
                data["vextype"],
                -1,
                mock_wrangler,
                mock_cam,
                now,
                data.get("planefile"),
                data.get("lightexport")
            )

class Test__call_pre_defplane(unittest.TestCase):

    def test(self):
        mock_IFDhooks = MagicMock()

        modules = {"IFDhooks": mock_IFDhooks}

        data = {
            "variable": "Pz",
            "vextype": "float",
            "planefile": "/var/tmp/foo.exr",
            "lightexport": "lightexport"
        }

        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        now = 123

        with patch.dict("sys.modules", modules):
            aov._call_pre_defplane(
                data,
                mock_wrangler,
                mock_cam,
                now
            )

            mock_IFDhooks.call.assert_called_with(
                "pre_defplane",
                data["variable"],
                data["vextype"],
                -1,
                mock_wrangler,
                mock_cam,
                now,
                data.get("planefile"),
                data.get("lightexport")
            )


class Test_IntrinsicAOVGroup(unittest.TestCase):

    @patch("__main__.aov.AOVGroup.__init__")
    def test___init__(self, mock_super_init):
        name = "group_name"

        result = aov.IntrinsicAOVGroup(name)

        mock_super_init.assert_called_with(name)
        self.assertEqual(result._comment, "Automatically generated")


class Test__build_category_map(unittest.TestCase):

    def test_no_parm(self):
        mock_light1 = MagicMock()

        lights = (mock_light1, )

        now = 123

        result = aov._build_category_map(lights, now)

        self.assertEqual(result, {})

        mock_light1.evalString.assert_called_with("categories", now, [])

    def test_no_categories(self):
        mock_light1 = MagicMock()

        mock_light1.evalString.side_effect = lambda name, t, value: value.append("")

        lights = (mock_light1, )

        now = 123

        result = aov._build_category_map(lights, now)

        self.assertEqual(result, {None: [mock_light1]})

    def test_categories(self):
        mock_light1 = MagicMock()
        mock_light1.evalString.side_effect = lambda name, t, value: value.append("cat1 cat2")

        mock_light2 = MagicMock()
        mock_light2.evalString.side_effect = lambda name, t, value: value.append("cat2,cat3")

        lights = (mock_light1, mock_light2)

        now = 123

        result = aov._build_category_map(lights, now)

        self.assertEqual(result, {"cat1": [mock_light1], "cat2": [mock_light1, mock_light2], "cat3": [mock_light2]})


class Test__write_data_to_ifd(unittest.TestCase):

    def setUp(self):
        super(Test__write_data_to_ifd, self).setUp()

        self.mock_ifd = MagicMock()
        modules = {"IFDapi": self.mock_ifd}

        self.patcher = patch.dict("sys.modules", modules)

        self.patcher.start()

    def tearDown(self):
        super(Test__write_data_to_ifd, self).tearDown()

        self.patcher.stop()

    @patch("__main__.aov._call_pre_defplane")
    def test_pre_defplane(self, mock_pre):
        mock_pre.return_value = True

        data = {}
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        now = 123

        aov._write_data_to_ifd(data, mock_wrangler, mock_cam, now)

        mock_pre.assert_called_with(data, mock_wrangler, mock_cam, now)

        self.mock_ifd.ray_start.assert_not_called()

    @patch("__main__.aov._call_post_defplane")
    @patch("__main__.aov._call_pre_defplane")
    def test_base_data(self, mock_pre, mock_post):
        mock_pre.return_value = False
        mock_post.return_value = False

        data = {
            "variable": "variable",
            "vextype": "vextype",
            "channel": "channel"
        }
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        now = 123

        aov._write_data_to_ifd(data, mock_wrangler, mock_cam, now)

        calls = [
            call("plane", "variable", [data["variable"]]),
            call("plane", "vextype", [data["vextype"]]),
            call("plane", "channel", [data["channel"]]),

        ]

        self.mock_ifd.ray_property.assert_has_calls(calls)

        mock_pre.assert_called_with(data, mock_wrangler, mock_cam, now)
        mock_post.assert_called_with(data, mock_wrangler, mock_cam, now)

    @patch("__main__.aov._call_post_defplane")
    @patch("__main__.aov._call_pre_defplane")
    def test_full_data(self, mock_pre, mock_post):
        mock_pre.return_value = False
        mock_post.return_value = False

        data = {
            "variable": "variable",
            "vextype": "vextype",
            "channel": "channel",
            "quantize": "quantize",
            "planefile": "planefile",
            "lightexport": "lightexport",
            "pfilter": "pfilter",
            "sfilter": "sfilter",
            "component": "component",
            "exclude_from_dcm": "exclude_from_dcm"
        }
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        now = 123

        aov._write_data_to_ifd(data, mock_wrangler, mock_cam, now)

        calls = [
            call("plane", "variable", [data["variable"]]),
            call("plane", "vextype", [data["vextype"]]),
            call("plane", "channel", [data["channel"]]),
            call("plane", "quantize", [data["quantize"]]),
            call("plane", "planefile", [data["planefile"]]),
            call("plane", "lightexport", [data["lightexport"]]),
            call("plane", "pfilter", [data["pfilter"]]),
            call("plane", "sfilter", [data["sfilter"]]),
            call("plane", "component", [data["component"]]),
            call("plane", "excludedcm", [True]),


        ]

        self.mock_ifd.ray_property.assert_has_calls(calls)

        mock_pre.assert_called_with(data, mock_wrangler, mock_cam, now)
        mock_post.assert_called_with(data, mock_wrangler, mock_cam, now)

    @patch("__main__.aov._call_post_defplane")
    @patch("__main__.aov._call_pre_defplane")
    def test_None_planefile(self, mock_pre, mock_post):
        mock_pre.return_value = False
        mock_post.return_value = False

        data = {
            "variable": "variable",
            "vextype": "vextype",
            "channel": "channel",
            "planefile": None,
        }
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        now = 123

        aov._write_data_to_ifd(data, mock_wrangler, mock_cam, now)

        calls = [
            call("plane", "variable", [data["variable"]]),
            call("plane", "vextype", [data["vextype"]]),
            call("plane", "channel", [data["channel"]]),

        ]

        self.mock_ifd.ray_property.assert_has_calls(calls)

        mock_pre.assert_called_with(data, mock_wrangler, mock_cam, now)
        mock_post.assert_called_with(data, mock_wrangler, mock_cam, now)

    @patch("__main__.aov._call_post_defplane")
    @patch("__main__.aov._call_pre_defplane")
    def test_post_defplane(self, mock_pre, mock_post):
        mock_pre.return_value = False
        mock_post.return_value = True

        data = {
            "variable": "variable",
            "vextype": "vextype",
            "channel": "channel",
        }
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        now = 123

        aov._write_data_to_ifd(data, mock_wrangler, mock_cam, now)

        calls = [
            call("plane", "variable", [data["variable"]]),
            call("plane", "vextype", [data["vextype"]]),
            call("plane", "channel", [data["channel"]]),

        ]

        self.mock_ifd.ray_property.assert_has_calls(calls)

        mock_pre.assert_called_with(data, mock_wrangler, mock_cam, now)
        mock_post.assert_called_with(data, mock_wrangler, mock_cam, now)

        self.mock_ifd.ray_end.assert_not_called()


class Test__write_light(unittest.TestCase):

    def setUp(self):
        super(Test__write_light, self).setUp()

        self.mock_soho = MagicMock()
        modules = {"soho": self.mock_soho}

        self.patcher = patch.dict("sys.modules", modules)

        self.patcher.start()

    def tearDown(self):
        super(Test__write_light, self).tearDown()

        self.patcher.stop()

    @patch("__main__.aov._write_data_to_ifd")
    def test_suffix_prefix(self, mock_write):
        mock_light = MagicMock()
        mock_light.getName.return_value = "light1"

        mock_light.getDefaultedString.return_value = ["suffix"]

        def evalString(name, now, prefix):
            prefix.append("prefix")
            return True

        mock_light.evalString.side_effect = evalString

        data = {}
        base_channel = "base"
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        now = 123

        aov._write_light(mock_light, base_channel, data, mock_wrangler, mock_cam, now)

        mock_write.assert_called_with(
            {
                "lightexport": "light1",
                "channel": "prefix_basesuffix"
            },
            mock_wrangler,
            mock_cam,
            now
        )

    @patch("__main__.aov._write_data_to_ifd")
    def test_no_suffix_path_prefix(self, mock_write):
        mock_light = MagicMock()
        mock_light.getName.return_value = "/obj/light1"

        def getDefaulted(name, now, default):
            return default

        mock_light.getDefaultedString.side_effect = getDefaulted

        mock_light.evalString.return_value = False

        data = {}
        base_channel = "base"
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        now = 123

        aov._write_light(mock_light, base_channel, data, mock_wrangler, mock_cam, now)

        mock_write.assert_called_with(
            {
                "lightexport": "/obj/light1",
                "channel": "obj_light1_base"
            },
            mock_wrangler,
            mock_cam,
            now
        )

    @patch("__main__.aov._write_data_to_ifd")
    def test_suffix_no_prefix(self, mock_write):
        mock_light = MagicMock()
        mock_light.getName.return_value = "/obj/light1"

        mock_light.getDefaultedString.return_value = ["suffix"]

        def evalString(name, now, prefix):
            return True

        mock_light.evalString.side_effect = evalString

        data = {}
        base_channel = "base"
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        now = 123

        aov._write_light(mock_light, base_channel, data, mock_wrangler, mock_cam, now)

        mock_write.assert_called_with(
            {
                "lightexport": "/obj/light1",
                "channel": "basesuffix"
            },
            mock_wrangler,
            mock_cam,
            now
        )

    @patch("__main__.aov._write_data_to_ifd")
    def test_empty_suffix(self, mock_write):
        mock_light = MagicMock()
        mock_light.getName.return_value = "/obj/light1"

        mock_light.getDefaultedString.return_value = ['']

        def evalString(name, now, prefix):
            return True

        mock_light.evalString.side_effect = evalString

        data = {}
        base_channel = "base"
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        now = 123

        aov._write_light(mock_light, base_channel, data, mock_wrangler, mock_cam, now)

        self.mock_soho.error.assert_called()

        mock_write.assert_called_with(
            {
                "lightexport": "/obj/light1",
                "channel": "base"
            },
            mock_wrangler,
            mock_cam,
            now
        )


class Test__write_per_category(unittest.TestCase):

    @patch("__main__.aov._write_data_to_ifd")
    @patch("__main__.aov._build_category_map")
    def test_no_category(self, mock_build, mock_write):
        mock_light1 = MagicMock()
        mock_light1.getName.return_value = "light1"

        mock_light2 = MagicMock()
        mock_light2.getName.return_value = "light2"

        lights = (mock_light1, mock_light2)

        category_lights = lights

        mock_build.return_value = {None: category_lights}


        data = {}
        base_channel = "base"
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        now = 123

        aov._write_per_category(lights, base_channel, data, mock_wrangler, mock_cam, now)

        mock_write.assert_called_with(
            {
                "lightexport": "light1 light2",
                "channel": base_channel
            },
            mock_wrangler,
            mock_cam,
            now
        )

    @patch("__main__.aov._write_data_to_ifd")
    @patch("__main__.aov._build_category_map")
    def test_category(self, mock_build, mock_write):
        mock_light1 = MagicMock()
        mock_light1.getName.return_value = "light1"

        mock_light2 = MagicMock()
        mock_light2.getName.return_value = "light2"

        lights = (mock_light1, mock_light2)

        category_lights = lights

        category = "test"

        mock_build.return_value = {category: category_lights}


        data = {}
        base_channel = "base"
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        now = 123

        aov._write_per_category(lights, base_channel, data, mock_wrangler, mock_cam, now)

        mock_write.assert_called_with(
            {
                "lightexport": "light1 light2",
                "channel": "{}_{}".format(category, base_channel)
            },
            mock_wrangler,
            mock_cam,
            now
        )


class Test__write_single_channel(unittest.TestCase):

    @patch("__main__.aov._write_data_to_ifd")
    def test_lights(self, mock_write):
        mock_light1 = MagicMock()
        mock_light1.getName.return_value = "light1"

        mock_light2 = MagicMock()
        mock_light2.getName.return_value = "light2"

        lights = (mock_light1, mock_light2)

        data = {}
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        now = 123

        aov._write_single_channel(lights, data, mock_wrangler, mock_cam, now)

        mock_write.assert_called_with(
            {"lightexport": "light1 light2"},
            mock_wrangler,
            mock_cam,
            now
        )

    @patch("__main__.aov._write_data_to_ifd")
    def test_no_lights(self, mock_write):
        lights = ()

        data = {}
        mock_wrangler = MagicMock()
        mock_cam = MagicMock()
        now = 123

        aov._write_single_channel(lights, data, mock_wrangler, mock_cam, now)

        mock_write.assert_called_with(
            {"lightexport": "__nolights__"},
            mock_wrangler,
            mock_cam,
            now
        )

# =============================================================================

if __name__ == '__main__':
    # Run the tests.
    try:
        unittest.main()

    finally:
        cov.stop()
        cov.html_report()
        cov.save()

