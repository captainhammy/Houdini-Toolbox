
import coverage
import os
import unittest

from mock import MagicMock, PropertyMock, call, mock_open, patch

from ht.sohohooks.aovs import aov, manager

import hou

cov = coverage.Coverage(data_suffix=True, source=["ht.sohohooks.aovs.manager"], branch=True)

cov.start()

reload(manager)

# =============================================================================
# CLASSES
# =============================================================================

class Test_AOVManager(unittest.TestCase):
    """Test ht.sohohooks.manager.AOVManager object."""

    def setUp(self):
        super(Test_AOVManager, self).setUp()

        self.mock_api = MagicMock()
        self.mock_settings = MagicMock()
        self.mock_soho = MagicMock()

        modules = {
            "IFDapi": self.mock_api,
            "IFDsettings": self.mock_settings,
            "soho": self.mock_soho
        }

        self.patcher = patch.dict("sys.modules", modules)
        self.patcher.start()

    def tearDown(self):
        super(Test_AOVManager, self).tearDown()

        self.patcher.stop()

    @patch("__main__.manager.AOVManager._init_from_files")
    def test___init__(self, mock_init):
        mgr = manager.AOVManager()

        self.assertEqual(mgr._aovs, {})
        self.assertEqual(mgr._groups, {})
        self.assertIsNone(mgr._interface)
        mock_init.assert_called()

    # _build_intrinsic_groups

    @patch("__main__.manager.IntrinsicAOVGroup", autospec=True)
    @patch.object(manager.AOVManager, "add_group")
    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test__build_intrinsic_groups__new_group(self, mock_aovs, mock_groups, mock_add, mock_int_group):

        mock_aov = MagicMock(spec=aov.AOV)
        mock_aov.intrinsics = ["int1"]

        mock_groups.return_value = {}

        mock_aovs.return_value = {"name": mock_aov}

        mgr = manager.AOVManager()
        mgr._build_intrinsic_groups()

        mock_int_group.assert_called_with("i:int1")
        mock_add.assert_called_with(mock_int_group.return_value)

        mock_int_group.return_value.aovs.append.assert_called_with(mock_aov)

    @patch.object(manager.AOVManager, "add_group")
    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test__build_intrinsic_groups__existing_group(self, mock_aovs, mock_groups, mock_add):
        mock_aov = MagicMock(spec=aov.AOV)
        mock_aov.intrinsics = ["int1"]

        mock_group = MagicMock(spec=aov.IntrinsicAOVGroup)

        mock_groups.return_value = {"i:int1": mock_group}

        mock_aovs.return_value = {"name": mock_aov}

        mgr = manager.AOVManager()
        mgr._build_intrinsic_groups()

        mock_group.aovs.append.assert_called_with(mock_aov)

    # _init_from_files

    @patch.object(manager.AOVManager, "_build_intrinsic_groups")
    @patch.object(manager.AOVManager, "_merge_readers")
    @patch("__main__.manager.AOVFile", autospec=True)
    @patch("__main__.manager._find_aov_files")
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test__init_from_files(self, mock_find, mock_file, mock_merge, mock_build):
        mock_find.return_value = ["/path/to/file1.json"]

        mgr = manager.AOVManager()
        mgr._init_from_files()

        mock_file.assert_called_with("/path/to/file1.json")
        mock_merge.assert_called_with([mock_file.return_value])
        mock_build.assert_called()

    # _init_group_members

    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test__init_group_members(self, mock_aovs):
        mock_group = MagicMock(spec=aov.AOVGroup)
        mock_group.includes = ["N", "P"]

        mock_aov = MagicMock(spec=aov.AOV)

        mock_aovs.return_value = {
            "N": mock_aov,
        }

        mgr = manager.AOVManager()
        mgr._init_group_members(mock_group)

        mock_group.aovs.append.assert_called_with(mock_aov)

    # _init_reader_aovs

    @patch.object(manager.AOVManager, "add_aov")
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test__init_reader_aovs__new_aov(self, mock_aovs, mock_add):
        mock_aov = MagicMock(spec=aov.AOV)
        mock_aov.variable = "N"

        mock_reader = MagicMock(spec=manager.AOVFile)
        mock_reader.aovs = [mock_aov]

        mock_aovs.return_value = {}

        mgr = manager.AOVManager()
        mgr._init_reader_aovs(mock_reader)

        mock_add.assert_called_with(mock_aov)

    @patch.object(manager.AOVManager, "add_aov")
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test__init_reader_aovs__matches_existing_priority_same(self, mock_aovs, mock_add):
        mock_new_aov = MagicMock(spec=aov.AOV)
        mock_new_aov.variable = "N"
        mock_new_aov.priority = 3

        mock_existing_aov = MagicMock(spec=aov.AOV)
        mock_existing_aov.variable = "N"
        mock_existing_aov.priority = 3

        mock_reader = MagicMock(spec=manager.AOVFile)
        mock_reader.aovs = [mock_new_aov]

        mock_aovs.return_value = {"N": mock_existing_aov}

        mgr = manager.AOVManager()
        mgr._init_reader_aovs(mock_reader)

        mock_add.assert_not_called()

    @patch.object(manager.AOVManager, "add_aov")
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test__init_reader_aovs__matches_existing_priority_lower(self, mock_aovs, mock_add):
        mock_new_aov = MagicMock(spec=aov.AOV)
        mock_new_aov.variable = "N"
        mock_new_aov.priority = 3

        mock_existing_aov = MagicMock(spec=aov.AOV)
        mock_existing_aov.variable = "N"
        mock_existing_aov.priority = 2

        mock_reader = MagicMock(spec=manager.AOVFile)
        mock_reader.aovs = [mock_new_aov]

        mock_aovs.return_value = {"N": mock_existing_aov}

        mgr = manager.AOVManager()
        mgr._init_reader_aovs(mock_reader)

        mock_add.assert_called_with(mock_new_aov)

    # _init_reader_groups

    @patch.object(manager.AOVManager, "add_group")
    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "_init_group_members")
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test__init_reader_groups__new_group(self, mock_init, mock_groups, mock_add):
        mock_group = MagicMock(spec=aov.AOV)
        mock_group.name = "name"

        mock_reader = MagicMock(spec=manager.AOVFile)
        mock_reader.groups = [mock_group]

        mock_groups.return_value = {}

        mgr = manager.AOVManager()
        mgr._init_reader_groups(mock_reader)

        mock_init.assert_called_with(mock_group)

        mock_add.assert_called_with(mock_group)

    @patch.object(manager.AOVManager, "add_group")
    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "_init_group_members")
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test__init_reader_groups__matches_existing_priority_same(self, mock_init, mock_groups, mock_add):
        mock_new_group = MagicMock(spec=aov.AOV)
        mock_new_group.name = "name"
        mock_new_group.priority = 3

        mock_reader = MagicMock(spec=manager.AOVFile)
        mock_reader.groups = [mock_new_group]

        mock_existing_group = MagicMock(spec=aov.AOV)
        mock_existing_group.name = "name"
        mock_existing_group.priority = 3

        mock_groups.return_value = {"name": mock_existing_group}

        mgr = manager.AOVManager()
        mgr._init_reader_groups(mock_reader)

        mock_init.assert_called_with(mock_new_group)

        mock_add.assert_not_called()

    @patch.object(manager.AOVManager, "add_group")
    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "_init_group_members")
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test__init_reader_groups__matches_existing_priority_lower(self, mock_init, mock_groups, mock_add):
        mock_new_group = MagicMock(spec=aov.AOV)
        mock_new_group.name = "name"
        mock_new_group.priority = 3

        mock_reader = MagicMock(spec=manager.AOVFile)
        mock_reader.groups = [mock_new_group]

        mock_existing_group = MagicMock(spec=aov.AOV)
        mock_existing_group.name = "name"
        mock_existing_group.priority = 2

        mock_groups.return_value = {"name": mock_existing_group}

        mgr = manager.AOVManager()
        mgr._init_reader_groups(mock_reader)

        mock_init.assert_called_with(mock_new_group)

        mock_add.assert_called_with(mock_new_group)

    # _merge_readers

    @patch.object(manager.AOVManager, "_init_reader_groups")
    @patch.object(manager.AOVManager, "_init_reader_aovs")
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test__merge_readers(self, mock_init_aovs, mock_init_groups):
        mock_reader = MagicMock(spec=manager.AOVFile)

        readers = [mock_reader]

        mgr = manager.AOVManager()
        mgr._merge_readers(readers)

        mock_init_aovs.assert_called_with(mock_reader)
        mock_init_groups.assert_called_with(mock_reader)

    # properties

    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_aovs(self):
        mgr = manager.AOVManager()
        mgr._aovs = ["aovs"]

        self.assertEqual(mgr.aovs, ["aovs"])

    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_groups(self):
        mgr = manager.AOVManager()
        mgr._groups = ["groups"]

        self.assertEqual(mgr.groups, ["groups"])

    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_interface(self):
        mgr = manager.AOVManager()
        mgr._interface = None

        self.assertIsNone(mgr.interface)

    # add_aov

    @patch.object(manager.AOVManager, "interface", new_callable=PropertyMock(return_value=None))
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_add_aov__no_interface(self, mock_aovs, mock_interface):
        aovs = {}

        mock_aovs.return_value = aovs

        mock_aov = MagicMock(spec=aov.AOV)
        mock_aov.variable = "P"

        mgr = manager.AOVManager()
        mgr.add_aov(mock_aov)

        self.assertEqual(aovs, {"P": mock_aov})

    @patch.object(manager.AOVManager, "interface", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_add_aov__interface(self, mock_aovs, mock_interface):
        interface = MagicMock()
        mock_interface.return_value = interface

        aovs = {}
        mock_aovs.return_value = aovs

        mock_aov = MagicMock(spec=aov.AOV)
        mock_aov.variable = "P"

        mgr = manager.AOVManager()
        mgr.add_aov(mock_aov)

        self.assertEqual(aovs, {"P": mock_aov})
        interface.aovAddedSignal.emit.assert_called_with(mock_aov)

    # add_aovs_to_ifd

    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_add_aovs_to_ifd__no_parms(self):
        mock_wrangler = MagicMock()

        mock_cam = MagicMock()
        mock_cam.wrangle.return_value = {}

        now = 123

        mgr = manager.AOVManager()

        calls = [
            call("enable_auto_aovs", "int", [1], skipdefault=False),
            call("auto_aovs", "str", [""], skipdefault=False)
        ]

        mgr.add_aovs_to_ifd(mock_wrangler, mock_cam, now)

        self.mock_soho.SohoParm.assert_has_calls(calls)

    @patch.object(manager.AOVManager, "get_aovs_from_string")
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_add_aovs_to_ifd__disabled(self, mock_get):
        mock_wrangler = MagicMock()

        mock_enable_result = MagicMock()
        mock_enable_result.Value = [0]

        mock_cam = MagicMock()
        mock_cam.wrangle.return_value = {
            "enable_auto_aovs": mock_enable_result,
        }

        now = 123

        mgr = manager.AOVManager()

        calls = [
            call("enable_auto_aovs", "int", [1], skipdefault=False),
            call("auto_aovs", "str", [""], skipdefault=False)
        ]

        mgr.add_aovs_to_ifd(mock_wrangler, mock_cam, now)

        self.mock_soho.SohoParm.assert_has_calls(calls)

    @patch("__main__.manager.flatten_aov_items")
    @patch.object(manager.AOVManager, "get_aovs_from_string")
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_add_aovs_to_ifd__non_opid(self, mock_get, mock_flattened):
        mock_aov = MagicMock(spec=aov.AOV)
        mock_aov.variable = "P"

        mock_wrangler = MagicMock()

        mock_enable_result = MagicMock()
        mock_enable_result.Value = [1]

        mock_aovs_result = MagicMock()

        mock_cam = MagicMock()
        mock_cam.wrangle.return_value = {
            "enable_auto_aovs": mock_enable_result,
            "auto_aovs": mock_aovs_result,
        }

        mock_get.return_value = [mock_aov]

        now = 123

        mock_flattened.return_value = (mock_aov, )

        mgr = manager.AOVManager()

        calls = [
            call("enable_auto_aovs", "int", [1], skipdefault=False),
            call("auto_aovs", "str", [""], skipdefault=False)
        ]

        mgr.add_aovs_to_ifd(mock_wrangler, mock_cam, now)

        self.mock_soho.SohoParm.assert_has_calls(calls)

        mock_get.assert_called_with(mock_aovs_result.Value[0])

        mock_aov.write_to_ifd.assert_called_with(mock_wrangler, mock_cam, now)

        self.mock_api.ray_comment.assert_not_called()

    @patch("__main__.manager.flatten_aov_items")
    @patch.object(manager.AOVManager, "get_aovs_from_string")
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_add_aovs_to_ifd__opid(self, mock_get, mock_flattened):
        mock_aov = MagicMock(spec=aov.AOV)
        mock_aov.variable = "Op_Id"

        mock_wrangler = MagicMock()

        mock_enable_result = MagicMock()
        mock_enable_result.Value = [1]

        mock_aovs_result = MagicMock()

        mock_cam = MagicMock()
        mock_cam.wrangle.return_value = {
            "enable_auto_aovs": mock_enable_result,
            "auto_aovs": mock_aovs_result,
        }

        mock_get.return_value = [mock_aov]

        now = 123

        mock_flattened.return_value = (mock_aov, )

        mgr = manager.AOVManager()

        calls = [
            call("enable_auto_aovs", "int", [1], skipdefault=False),
            call("auto_aovs", "str", [""], skipdefault=False)
        ]

        mgr.add_aovs_to_ifd(mock_wrangler, mock_cam, now)

        self.mock_soho.SohoParm.assert_has_calls(calls)

        mock_get.assert_called_with(mock_aovs_result.Value[0])

        mock_aov.write_to_ifd.assert_called_with(mock_wrangler, mock_cam, now)
        self.mock_api.ray_comment.assert_called()
        self.assertTrue(self.mock_settings._GenerateOpId)

    # add_group

    @patch.object(manager.AOVManager, "interface", new_callable=PropertyMock(return_value=None))
    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_add_group__no_interface(self, mock_groups, mock_interface):
        groups = {}

        mock_groups.return_value = groups

        mock_group = MagicMock(spec=aov.AOVGroup)
        mock_group.name = "name"

        mgr = manager.AOVManager()
        mgr.add_group(mock_group)

        self.assertEqual(groups, {"name": mock_group})

    @patch.object(manager.AOVManager, "interface", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_add_group__interface(self, mock_groups, mock_interface):
        interface = MagicMock()
        mock_interface.return_value = interface

        groups = {}
        mock_groups.return_value = groups

        mock_group = MagicMock(spec=aov.AOVGroup)
        mock_group.name = "name"

        mgr = manager.AOVManager()
        mgr.add_group(mock_group)

        self.assertEqual(groups, {"name": mock_group})
        interface.groupAddedSignal.emit.assert_called_with(mock_group)

    # clear

    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_clear(self):
        mgr = manager.AOVManager()
        mgr._aovs = {"key": "value"}
        mgr._groups = {"key": "value"}

        mgr.clear()

        self.assertEqual(mgr._aovs, {})
        self.assertEqual(mgr._groups, {})

    # get_aovs_from_string

    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_get_aovs_from_string__no_matches(self, mock_aovs, mock_groups):
        mock_aovs.return_value = {}
        mock_groups.return_value = {}

        mgr = manager.AOVManager()

        pattern = ""

        result = mgr.get_aovs_from_string(pattern)

        self.assertEqual(result, [])

    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_get_aovs_from_string__aovs_match_spaces(self, mock_aovs, mock_groups):
        mock_aov_n = MagicMock(spec=aov.AOV)
        mock_aov_p = MagicMock(spec=aov.AOV)

        mock_aovs.return_value = {"N": mock_aov_n, "P": mock_aov_p}
        mock_groups.return_value = {}

        mgr = manager.AOVManager()

        pattern = "N P R"

        result = mgr.get_aovs_from_string(pattern)

        self.assertEqual(result, [mock_aov_n, mock_aov_p])

    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_get_aovs_from_string__aovs_match_commas(self, mock_aovs, mock_groups):
        mock_aov_n = MagicMock(spec=aov.AOV)
        mock_aov_p = MagicMock(spec=aov.AOV)

        mock_aovs.return_value = {"N": mock_aov_n, "P": mock_aov_p}
        mock_groups.return_value = {}

        mgr = manager.AOVManager()

        pattern = "N,P,R"

        result = mgr.get_aovs_from_string(pattern)

        self.assertEqual(result, [mock_aov_n, mock_aov_p])

    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_get_aovs_from_string__groups_match_spaces(self, mock_aovs, mock_groups):
        mock_group1 = MagicMock(spec=aov.AOVGroup)
        mock_group2 = MagicMock(spec=aov.AOVGroup)

        mock_aovs.return_value = {}
        mock_groups.return_value = {"group1": mock_group1, "group2": mock_group2}

        mgr = manager.AOVManager()

        pattern = "@group1 @group3 @group2"

        result = mgr.get_aovs_from_string(pattern)

        self.assertEqual(result, [mock_group1, mock_group2])

    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_get_aovs_from_string__groups_match_commas(self, mock_aovs, mock_groups):
        mock_group1 = MagicMock(spec=aov.AOVGroup)
        mock_group2 = MagicMock(spec=aov.AOVGroup)

        mock_aovs.return_value = {}
        mock_groups.return_value = {"group1": mock_group1, "group2": mock_group2}

        mgr = manager.AOVManager()

        pattern = "@group1,@group3, @group2"

        result = mgr.get_aovs_from_string(pattern)

        self.assertEqual(result, [mock_group1, mock_group2])

    # init_interface

    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_init_interface(self):
        mock_utils = MagicMock()

        modules = {
            "ht.ui.aovs.utils": mock_utils
        }

        mgr = manager.AOVManager()

        with patch.dict("sys.modules", modules):
            mgr.init_interface()

        self.assertEqual(mgr._interface, mock_utils.AOVViewerInterface.return_value)

    # load

    @patch.object(manager.AOVManager, "_merge_readers")
    @patch("__main__.manager.AOVFile", autospec=True)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_load(self, mock_file, mock_merge):
        mgr = manager.AOVManager()

        path = "/path/to/file.json"

        mgr.load(path)

        mock_file.assert_called_with(path)

        mock_merge.assert_called_with([mock_file.return_value])

    # reload

    @patch.object(manager.AOVManager, "_init_from_files")
    @patch.object(manager.AOVManager, "clear")
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_reload(self, mock_clear, mock_init):
        mgr = manager.AOVManager()

        mgr.reload()

        mock_clear.assert_called()
        mock_init.assert_called()

    # remove_aov

    @patch.object(manager.AOVManager, "interface", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_remove_aov__no_match(self, mock_aovs, mock_interface):
        mock_aov1 = MagicMock(spec=aov.AOV)
        mock_aov1.variable = "P"

        mock_aov2 = MagicMock(spec=aov.AOV)
        mock_aov2.variable = "N"

        aovs = {"N": mock_aov2}
        mock_aovs.return_value = aovs

        mgr = manager.AOVManager()

        mgr.remove_aov(mock_aov1)

        self.assertEqual(aovs, {"N": mock_aov2})

    @patch.object(manager.AOVManager, "interface", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_remove_aov__match_no_interface(self, mock_aovs, mock_interface):
        mock_interface.return_value = None

        mock_aov = MagicMock(spec=aov.AOV)
        mock_aov.variable = "P"

        aovs = {"P": mock_aov}
        mock_aovs.return_value = aovs

        mgr = manager.AOVManager()

        mgr.remove_aov(mock_aov)

        self.assertEqual(aovs, {})

    @patch.object(manager.AOVManager, "interface", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_remove_aov__match_interface(self, mock_aovs, mock_interface):
        interface = MagicMock()
        mock_interface.return_value = interface

        mock_aov = MagicMock(spec=aov.AOV)
        mock_aov.variable = "P"

        aovs = {"P": mock_aov}
        mock_aovs.return_value = aovs

        mgr = manager.AOVManager()

        mgr.remove_aov(mock_aov)

        self.assertEqual(aovs, {})

        interface.aovRemovedSignal.emit.assert_called_with(mock_aov)

    # remove_group

    @patch.object(manager.AOVManager, "interface", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_remove_group__no_match(self, mock_groups, mock_interface):
        mock_group1 = MagicMock(spec=aov.AOVGroup)
        mock_group1.name = "group1"

        mock_group2 = MagicMock(spec=aov.AOVGroup)
        mock_group2.name = "group2"

        groups = {"group2": mock_group2}
        mock_groups.return_value = groups

        mgr = manager.AOVManager()

        mgr.remove_group(mock_group1)

        self.assertEqual(groups, {"group2": mock_group2})

    @patch.object(manager.AOVManager, "interface", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_remove_group__match_no_interface(self, mock_groups, mock_interface):
        mock_interface.return_value = None

        mock_group = MagicMock(spec=aov.AOVGroup)
        mock_group.name = "group"

        groups = {"group": mock_group}
        mock_groups.return_value = groups

        mgr = manager.AOVManager()

        mgr.remove_group(mock_group)

        self.assertEqual(groups, {})

    @patch.object(manager.AOVManager, "interface", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_remove_group__match_interface(self, mock_groups, mock_interface):
        interface = MagicMock()
        mock_interface.return_value = interface

        mock_group = MagicMock(spec=aov.AOVGroup)
        mock_group.name = "group"

        groups = {"group": mock_group}
        mock_groups.return_value = groups

        mgr = manager.AOVManager()

        mgr.remove_group(mock_group)

        self.assertEqual(groups, {})

        interface.groupRemovedSignal.emit.assert_called_with(mock_group)


class Test_AOVFile(unittest.TestCase):
    """Test ht.sohohooks.manager.AOVFile object."""

    @patch.object(manager.AOVFile, "_init_from_file")
    @patch.object(manager.AOVFile, "exists", new_callable=PropertyMock(return_value=True))
    def test___init___exists(self, mock_exists, mock_init):
        path = "/path/to/file.json"

        aov_file = manager.AOVFile(path)

        self.assertEqual(aov_file._path, path)
        self.assertEqual(aov_file._aovs, [])
        self.assertEqual(aov_file._data, {})
        self.assertEqual(aov_file._groups, [])

        mock_init.assert_called()

    @patch.object(manager.AOVFile, "_init_from_file")
    @patch.object(manager.AOVFile, "exists", new_callable=PropertyMock(return_value=False))
    def test___init___does_not_exist(self, mock_exists, mock_init):
        path = "/path/to/file.json"

        aov_file = manager.AOVFile(path)

        self.assertEqual(aov_file._path, path)
        self.assertEqual(aov_file._aovs, [])
        self.assertEqual(aov_file._data, {})
        self.assertEqual(aov_file._groups, [])

        mock_init.assert_not_called()

    # _create_aovs

    @patch.object(manager.AOVFile, "aovs", new_callable=PropertyMock)
    @patch("__main__.manager.AOV", autospec=True)
    @patch.object(manager.AOVFile, "path", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test__create_aovs(self, mock_path, mock_aov, mock_aovs):
        definition = {
            "key": "value"
        }

        definitions = [
            definition
        ]

        aovs = []
        mock_aovs.return_value = aovs

        aov_file = manager.AOVFile(None)

        aov_file._create_aovs(definitions)

        mock_aov.assert_called_with({"key": "value", "path": mock_path.return_value})

        self.assertEqual(definition, {"key": "value", "path": mock_path.return_value})

        self.assertEqual(aovs, [mock_aov.return_value])

    # _create_groups

    @patch.object(manager.AOVFile, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "path", new_callable=PropertyMock)
    @patch("__main__.manager.AOVGroup", autospec=True)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test__create_groups_minimal(self, mock_group, mock_path, mock_groups):
        group_data = {}

        definitions = {"group_name": group_data}

        groups = []
        mock_groups.return_value = groups

        aov_file = manager.AOVFile(None)

        aov_file._create_groups(definitions)

        mock_group.assert_called_with("group_name")

        self.assertEqual(groups, [mock_group.return_value])

        self.assertEqual(mock_group.return_value.path, mock_path.return_value)

    @patch.object(manager.AOVFile, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "path", new_callable=PropertyMock)
    @patch("__main__.manager.os.path.expandvars")
    @patch("__main__.manager.AOVGroup", autospec=True)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test__create_groups_all_data(self, mock_group, mock_expand, mock_path, mock_groups):
        group_data = {
            "include": ["a", "b"],
            "comment": "This is a comment",
            "priority": 3,
            "icon": "icon.png"
        }

        definitions = {"group_name": group_data}

        groups = []
        mock_groups.return_value = groups

        aov_file = manager.AOVFile(None)

        aov_file._create_groups(definitions)

        mock_group.assert_called_with("group_name")

        self.assertEqual(groups, [mock_group.return_value])

        mock_expand.assert_called_with("icon.png")

        self.assertEqual(mock_group.return_value.path, mock_path.return_value)
        self.assertEqual(mock_group.return_value.comment, "This is a comment")
        self.assertEqual(mock_group.return_value.priority, 3)
        self.assertEqual(mock_group.return_value.icon, mock_expand.return_value)

        mock_group.return_value.includes.extend.assert_called_with(["a", "b"])

    # _init_from_file

    @patch.object(manager.AOVFile, "_create_groups")
    @patch.object(manager.AOVFile, "_create_aovs")
    @patch("__main__.manager.json.load")
    @patch.object(manager.AOVFile, "path", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test__init_from_file__no_items(self, mock_path, mock_load, mock_create_aovs, mock_create_groups):
        mock_load.return_value = {}
        aov_file = manager.AOVFile(None)

        with patch("__builtin__.open", mock_open()) as mock_handle:
            aov_file._init_from_file()

            mock_handle.assert_called_with(mock_path.return_value)

            mock_load.assert_called_with(mock_handle.return_value)

        mock_create_aovs.assert_not_called()
        mock_create_groups.assert_not_called()

    @patch.object(manager.AOVFile, "_create_groups")
    @patch.object(manager.AOVFile, "_create_aovs")
    @patch("__main__.manager.json.load")
    @patch.object(manager.AOVFile, "path", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test__init_from_file__items(self, mock_path, mock_load, mock_create_aovs, mock_create_groups):
        mock_definitions = MagicMock(spec=dict)
        mock_groups = MagicMock(spec=dict)

        mock_load.return_value = {
            "definitions": mock_definitions,
            "groups": mock_groups,
        }

        aov_file = manager.AOVFile(None)

        with patch("__builtin__.open", mock_open()) as mock_handle:
            aov_file._init_from_file()

            mock_handle.assert_called_with(mock_path.return_value)

            mock_load.assert_called_with(mock_handle.return_value)

        mock_create_aovs.assert_called_with(mock_definitions)
        mock_create_groups.assert_called_with(mock_groups)

    # properties

    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_aovs(self):
        mock_aov = MagicMock(spec=aov.AOV)

        aov_file = manager.AOVFile(None)

        aov_file._aovs = [mock_aov]

        self.assertEqual(aov_file.aovs, [mock_aov])

        with self.assertRaises(AttributeError):
            aov_file.aovs = []

    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_groups(self):
        mock_group = MagicMock(spec=aov.AOVGroup)

        aov_file = manager.AOVFile(None)

        aov_file._groups = [mock_group]

        self.assertEqual(aov_file.groups, [mock_group])

        with self.assertRaises(AttributeError):
            aov_file.groups = []

    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_path(self):
        aov_file = manager.AOVFile(None)

        aov_file._path = "/path/to/file.json"

        self.assertEqual(aov_file.path, "/path/to/file.json")

        with self.assertRaises(AttributeError):
            aov_file.path = "/some/path"

    @patch.object(manager.AOVFile, "path", new_callable=PropertyMock)
    @patch("__main__.manager.os.path.isfile")
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_exists(self, mock_isfile, mock_path):
        aov_file = manager.AOVFile(None)

        self.assertEqual(aov_file.exists, mock_isfile.return_value)

        mock_isfile.assert_called_with(mock_path.return_value)

        with self.assertRaises(AttributeError):
            aov_file.exists = False

    # add_aov

    @patch.object(manager.AOVFile, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_add_aov(self, mock_aovs):
        mock_aov = MagicMock(spec=aov.AOV)

        aov_file = manager.AOVFile(None)
        aov_file.add_aov(mock_aov)

        mock_aovs.return_value.append.assert_called_with(mock_aov)

    # add_group

    @patch.object(manager.AOVFile, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_add_group(self, mock_groups):
        mock_group = MagicMock(spec=aov.AOVGroup)

        aov_file = manager.AOVFile(None)
        aov_file.add_group(mock_group)

        mock_groups.return_value.append.assert_called_with(mock_group)

    # contains_aov

    @patch.object(manager.AOVFile, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_contains_aov(self, mock_aovs):
        mock_aov = MagicMock(spec=aov.AOV)

        aov_file = manager.AOVFile(None)
        result = aov_file.contains_aov(mock_aov)

        self.assertEqual(result, mock_aovs.return_value.__contains__.return_value)

        mock_aovs.return_value.__contains__.assert_called_with(mock_aov)

    # contains_group

    @patch.object(manager.AOVFile, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_contains_group(self, mock_groups):
        mock_group = MagicMock(spec=aov.AOVGroup)

        aov_file = manager.AOVFile(None)
        result = aov_file.contains_group(mock_group)

        self.assertEqual(result, mock_groups.return_value.__contains__.return_value)

        mock_groups.return_value.__contains__.assert_called_with(mock_group)

    # remove_aov

    @patch.object(manager.AOVFile, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_remove_aov(self, mock_aovs):
        mock_aov = MagicMock(spec=aov.AOV)

        aovs = [mock_aov]
        mock_aovs.return_value = aovs

        aov_file = manager.AOVFile(None)
        aov_file.remove_aov(mock_aov)

        self.assertEqual(aovs, [])

    # remove_group

    @patch.object(manager.AOVFile, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_remove_group(self, mock_groups):
        mock_group = MagicMock(spec=aov.AOVGroup)

        groups = [mock_group]
        mock_groups.return_value = groups

        aov_file = manager.AOVFile(None)
        aov_file.remove_group(mock_group)

        self.assertEqual(groups, [])

    # replace_aov

    @patch.object(manager.AOVFile, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_replace_aov(self, mock_aovs):
        mock_aov = MagicMock(spec=aov.AOV)

        mock_aovs.return_value.index.return_value = 3

        aov_file = manager.AOVFile(None)
        aov_file.replace_aov(mock_aov)

        mock_aovs.return_value.index.assert_called_with(mock_aov)
        mock_aovs.return_value.__setitem__.assert_called_with(3, mock_aov)

    # replace_group

    @patch.object(manager.AOVFile, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_replace_group(self, mock_groups):
        mock_group = MagicMock(spec=aov.AOVGroup)

        mock_groups.return_value.index.return_value = 2

        aov_file = manager.AOVFile(None)
        aov_file.replace_group(mock_group)

        mock_groups.return_value.index.assert_called_with(mock_group)
        mock_groups.return_value.__setitem__.assert_called_with(2, mock_group)

    # write_to_file

    @patch("__main__.manager.json.dump")
    @patch.object(manager.AOVFile, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_write_to_file__nothing_explicit_path(self, mock_groups, mock_aovs, mock_dump):
        mock_groups.return_value = []
        mock_aovs.return_value = []

        aov_file = manager.AOVFile(None)

        path = "/path/to/file.json"

        with patch("__builtin__.open", mock_open()) as mock_handle:
            aov_file.write_to_file(path)

            mock_handle.assert_called_with(path, 'w')

            mock_dump.assert_called_with({}, mock_handle.return_value, indent=4)

    @patch("__main__.manager.json.dump")
    @patch.object(manager.AOVFile, "path", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_write_to_file(self, mock_groups, mock_aovs, mock_path, mock_dump):
        mock_group = MagicMock(spec=aov.AOVGroup)
        mock_group.as_data.return_value = {"group_key": "group_value"}

        mock_groups.return_value = [mock_group]

        mock_aov = MagicMock(spec=aov.AOV)
        mock_aov.as_data.return_value = {"aov_key": "aov_value"}

        mock_aovs.return_value = [mock_aov]

        aov_file = manager.AOVFile(None)

        expected = {
            "groups": {"group_key": "group_value"},
            "definitions": [{"aov_key": "aov_value"}]
        }

        with patch("__builtin__.open", mock_open()) as mock_handle:
            aov_file.write_to_file()

            mock_handle.assert_called_with(mock_path.return_value, 'w')

            mock_dump.assert_called_with(expected, mock_handle.return_value, indent=4)


class Test__find_aov_files(unittest.TestCase):
    """Test ht.sohohooks.manager._find_aov_files."""

    @patch("__main__.manager.glob.glob")
    @patch("__main__.manager._get_aov_path_folders")
    def test_aov_path(self, mock_get_folders, mock_glob):
        mock_get_folders.return_value = ("/path/to/folder", )
        mock_glob.return_value = ["path1", "path2"]

        with patch.dict(os.environ, {"HT_AOV_PATH": "value"}):
            result = manager._find_aov_files()

        self.assertEqual(result, ("path1", "path2"))

        mock_get_folders.assert_called()

        mock_glob.assert_called_with(os.path.join("/path/to/folder", "*.json"))


    @patch("__main__.manager.glob.glob")
    @patch("__main__.manager._find_houdinipath_aov_folders")
    def test_houdini_path(self, mock_find, mock_glob):
        mock_find.return_value = ["/path/to/folder"]
        mock_glob.return_value = ["path1", "path2"]

        with patch.dict(os.environ, {}, clear=True):
            result = manager._find_aov_files()

        self.assertEqual(result,("path1", "path2"))

        mock_find.assert_called()

        mock_glob.assert_called_with(os.path.join("/path/to/folder", "*.json"))


class Test__find_houdinipath_aov_folders(unittest.TestCase):
    """Test ht.sohohooks.manager._find_houdinipath_aov_folders."""

    @patch("__main__.manager.hou.findDirectories")
    def test_no_dirs(self, mock_find):
        def raise_error(*args, **kwargs):
            raise hou.OperationFailed()

        mock_find.side_effect = raise_error

        result = manager._find_houdinipath_aov_folders()

        self.assertEqual(result, ())

    @patch("__main__.manager.hou.findDirectories")
    def test_dirs(self, mock_find):
        result = manager._find_houdinipath_aov_folders()

        self.assertEqual(result, mock_find.return_value)


class Test__get_aov_path_folders(unittest.TestCase):
    """Test ht.sohohooks.manager._get_aov_path_folders."""

    def test_no_hpath(self):

        env_dict = {
            "HT_AOV_PATH": "path1:path2"
        }

        with patch.dict(os.environ, env_dict):
            result = manager._get_aov_path_folders()

        self.assertEqual(result, ("path1", "path2"))

    @patch("__main__.manager._find_houdinipath_aov_folders")
    def test_hpath_no_folders(self, mock_find):
        mock_find.return_value = ()

        env_dict = {
            "HT_AOV_PATH": "path1:path2:&"
        }

        with patch.dict(os.environ, env_dict):
            result = manager._get_aov_path_folders()

        self.assertEqual(result, ("path1", "path2", "&"))

    @patch("__main__.manager._find_houdinipath_aov_folders")
    def test_hpath_folders(self, mock_find):
        mock_find.return_value = ("hpath1", "hpath2")

        env_dict = {
            "HT_AOV_PATH": "path1:path2:&"
        }

        with patch.dict(os.environ, env_dict):
            result = manager._get_aov_path_folders()

        self.assertEqual(result, ("path1", "path2", "hpath1", "hpath2"))


class Test_build_menu_script(unittest.TestCase):
    """Test ht.sohohooks.manager.build_menu_script."""

    @patch("__main__.manager.MANAGER", autospec=True)
    def test_no_groups(self, mock_manager):
        mock_manager.groups = None

        mock_aov1 = MagicMock(spec=aov.AOV)
        mock_aov2 = MagicMock(spec=aov.AOV)
        mock_aov3 = MagicMock(spec=aov.AOV)

        mock_manager.aovs = {"P": mock_aov1, "N": mock_aov2, "A": mock_aov3}

        result = manager.build_menu_script()

        self.assertEqual(result, ("A", "A", "N", "N", "P", "P"))

    @patch("__main__.manager.MANAGER", autospec=True)
    def test_with_groups(self, mock_manager):
        mock_group1 = MagicMock(spec=aov.AOVGroup)
        mock_group2 = MagicMock(spec=aov.AOVGroup)
        mock_group3 = MagicMock(spec=aov.AOVGroup)

        mock_manager.groups = {
            "foo": mock_group1,
            "bar": mock_group2,
            "test": mock_group3,
        }

        mock_aov1 = MagicMock(spec=aov.AOV)
        mock_aov2 = MagicMock(spec=aov.AOV)
        mock_aov3 = MagicMock(spec=aov.AOV)

        mock_manager.aovs = {"P": mock_aov1, "N": mock_aov2, "A": mock_aov3}

        result = manager.build_menu_script()

        expected = ("@bar", "bar", "@foo", "foo", "@test", "test", "_separator_", "", "A", "A", "N", "N", "P", "P")

        self.assertEqual(result, expected)


class Test_flatten_aov_items(unittest.TestCase):
    """Test ht.sohohooks.manager.flatten_aov_items."""

    def test(self):
        mock_aov = MagicMock(spec=aov.AOV)

        mock_group_aov = MagicMock(spec=aov.AOV)

        mock_group = MagicMock(spec=aov.AOVGroup)
        type(mock_group).aovs = PropertyMock(return_value = [mock_group_aov])

        result = manager.flatten_aov_items([mock_aov, mock_group])

        self.assertEqual(result, (mock_aov, mock_group_aov))


class Test_load_json_files(unittest.TestCase):
    """Test ht.sohohooks.manager.load_json_files."""

    @patch("__main__.manager.MANAGER", autospec=True)
    @patch("__main__.manager.os.path.exists")
    @patch("__main__.manager.os.path.expandvars")
    def test(self, mock_expand, mock_exists, mock_manager):
        mock_expand.side_effect = ("expanded1", "expanded2")

        mock_exists.side_effect = (False, True)

        path_str = "path1 ; path2"

        mock_ui = MagicMock()
        mock_ui.selectFile.return_value = path_str

        hou.ui = mock_ui

        manager.load_json_files()

        mock_ui.selectFile.assert_called_with(
            pattern="*.json",
            chooser_mode=hou.fileChooserMode.Read,
            multiple_select=True
        )

        mock_manager.load.assert_called_with("expanded2")

        del hou.ui

# =============================================================================

if __name__ == '__main__':
    # Run the tests.
    try:
        unittest.main()

    finally:
        cov.stop()
        cov.html_report()
        cov.save()
