"""Test the ht.sohohooks.aovs.manager module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import imp
import os

# Third Party Imports
from mock import MagicMock, PropertyMock, call, mock_open, patch
import pytest

# Houdini Toolbox Imports
from ht.sohohooks.aovs import aov, manager
from ht.sohohooks.aovs import constants as consts

# Houdini Imports
import hou

# Reload the module to test to capture load evaluation since it has already
# been loaded.
imp.reload(manager)


# =============================================================================
# CLASSES
# =============================================================================

class Test_AOVManager(object):
    """Test ht.sohohooks.aovs.manager.AOVManager object."""

    @patch("ht.sohohooks.aovs.manager.AOVManager._init_from_files")
    def test___init__(self, mock_init):
        mgr = manager.AOVManager()

        assert mgr._aovs == {}
        assert mgr._groups == {}
        assert mgr._interface is None
        mock_init.assert_called()

    # _build_intrinsic_groups

    @patch("ht.sohohooks.aovs.manager.IntrinsicAOVGroup", autospec=True)
    @patch.object(manager.AOVManager, "add_group")
    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test__build_intrinsic_groups__new_group(self, mock_aovs, mock_groups, mock_add, mock_int_group):
        mock_aov = MagicMock(spec=manager.AOV)
        mock_aov.intrinsics = ["int1"]

        mock_groups.return_value = {}

        mock_aovs.return_value = {MagicMock(spec=str): mock_aov}

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
        mock_aov = MagicMock(spec=manager.AOV)
        mock_aov.intrinsics = ["int1"]

        mock_group = MagicMock(spec=aov.IntrinsicAOVGroup)

        mock_groups.return_value = {"i:int1": mock_group}

        mock_aovs.return_value = {MagicMock(spec=str): mock_aov}

        mgr = manager.AOVManager()
        mgr._build_intrinsic_groups()

        mock_group.aovs.append.assert_called_with(mock_aov)

    # _init_from_files

    @patch.object(manager.AOVManager, "_build_intrinsic_groups")
    @patch.object(manager.AOVManager, "_merge_readers")
    @patch("ht.sohohooks.aovs.manager.AOVFile", autospec=True)
    @patch("ht.sohohooks.aovs.manager._find_aov_files")
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test__init_from_files(self, mock_find, mock_file, mock_merge, mock_build):
        mock_path = MagicMock(spec=str)
        mock_find.return_value = [mock_path]

        mgr = manager.AOVManager()
        mgr._init_from_files()

        mock_file.assert_called_with(mock_path)
        mock_merge.assert_called_with([mock_file.return_value])
        mock_build.assert_called()

    # _init_group_members

    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test__init_group_members(self, mock_aovs):
        mock_varname1 = MagicMock(spec=str)
        mock_varname2 = MagicMock(spec=str)

        mock_group = MagicMock(spec=manager.AOVGroup)
        mock_group.includes = [mock_varname1, mock_varname2]

        mock_aov = MagicMock(spec=manager.AOV)

        mock_aovs.return_value = {
            mock_varname1: mock_aov,
        }

        mgr = manager.AOVManager()
        mgr._init_group_members(mock_group)

        mock_group.aovs.append.assert_called_with(mock_aov)

    # _init_reader_aovs

    @patch.object(manager.AOVManager, "add_aov")
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test__init_reader_aovs__new_aov(self, mock_aovs, mock_add):
        mock_aov = MagicMock(spec=manager.AOV)

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
        mock_varname = MagicMock(spec=str)
        mock_priority = MagicMock(spec=int)

        mock_new_aov = MagicMock(spec=manager.AOV)
        mock_new_aov.variable = mock_varname
        mock_new_aov.priority = mock_priority

        mock_existing_aov = MagicMock(spec=manager.AOV)
        mock_existing_aov.variable = mock_varname
        mock_existing_aov.priority = mock_priority

        mock_reader = MagicMock(spec=manager.AOVFile)
        mock_reader.aovs = [mock_new_aov]

        mock_aovs.return_value = {mock_varname: mock_existing_aov}

        mgr = manager.AOVManager()
        mgr._init_reader_aovs(mock_reader)

        mock_add.assert_not_called()

    @patch.object(manager.AOVManager, "add_aov")
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test__init_reader_aovs__matches_existing_priority_lower(self, mock_aovs, mock_add):
        mock_varname = MagicMock(spec=str)

        mock_new_aov = MagicMock(spec=manager.AOV)
        mock_new_aov.variable = mock_varname
        mock_new_aov.priority = 3

        mock_existing_aov = MagicMock(spec=manager.AOV)
        mock_existing_aov.variable = mock_varname
        mock_existing_aov.priority = 2

        mock_reader = MagicMock(spec=manager.AOVFile)
        mock_reader.aovs = [mock_new_aov]

        mock_aovs.return_value = {mock_varname: mock_existing_aov}

        mgr = manager.AOVManager()
        mgr._init_reader_aovs(mock_reader)

        mock_add.assert_called_with(mock_new_aov)

    # _init_reader_groups

    @patch.object(manager.AOVManager, "add_group")
    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "_init_group_members")
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test__init_reader_groups__new_group(self, mock_init, mock_groups, mock_add):
        mock_group = MagicMock(spec=manager.AOVGroup)

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
        mock_group_name = MagicMock(spec=str)
        mock_priority = MagicMock(spec=int)

        mock_new_group = MagicMock(spec=manager.AOVGroup)
        mock_new_group.name = mock_group_name
        mock_new_group.priority = mock_priority

        mock_reader = MagicMock(spec=manager.AOVFile)
        mock_reader.groups = [mock_new_group]

        mock_existing_group = MagicMock(spec=manager.AOVGroup)
        mock_existing_group.name = mock_group_name
        mock_existing_group.priority = mock_priority

        mock_groups.return_value = {mock_group_name: mock_existing_group}

        mgr = manager.AOVManager()
        mgr._init_reader_groups(mock_reader)

        mock_init.assert_called_with(mock_new_group)

        mock_add.assert_not_called()

    @patch.object(manager.AOVManager, "add_group")
    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "_init_group_members")
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test__init_reader_groups__matches_existing_priority_lower(self, mock_init, mock_groups, mock_add):
        mock_group_name = MagicMock(spec=str)

        mock_new_group = MagicMock(spec=manager.AOV)
        mock_new_group.name = mock_group_name
        mock_new_group.priority = 3

        mock_reader = MagicMock(spec=manager.AOVFile)
        mock_reader.groups = [mock_new_group]

        mock_existing_group = MagicMock(spec=manager.AOV)
        mock_existing_group.name = mock_group_name
        mock_existing_group.priority = 2

        mock_groups.return_value = {mock_group_name: mock_existing_group}

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
        mock_value = MagicMock(spec=list)

        mgr = manager.AOVManager()
        mgr._aovs = mock_value

        assert mgr.aovs == mock_value

    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_groups(self):
        mock_value = MagicMock(spec=list)

        mgr = manager.AOVManager()
        mgr._groups = mock_value

        assert mgr.groups == mock_value

    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_interface(self):
        mgr = manager.AOVManager()
        mgr._interface = None

        assert mgr.interface is None

    # add_aov

    @patch.object(manager.AOVManager, "interface", new_callable=PropertyMock(return_value=None))
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_add_aov__no_interface(self, mock_aovs, mock_interface):
        aovs = {}

        mock_aovs.return_value = aovs

        mock_aov = MagicMock(spec=manager.AOV)

        mgr = manager.AOVManager()
        mgr.add_aov(mock_aov)

        assert aovs == {mock_aov.variable: mock_aov}

    @patch.object(manager.AOVManager, "interface", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_add_aov__interface(self, mock_aovs, mock_interface):
        interface = MagicMock()
        mock_interface.return_value = interface

        aovs = {}
        mock_aovs.return_value = aovs

        mock_aov = MagicMock(spec=manager.AOV)

        mgr = manager.AOVManager()
        mgr.add_aov(mock_aov)

        assert aovs == {mock_aov.variable: mock_aov}
        interface.aov_added_signal.emit.assert_called_with(mock_aov)

    # add_aovs_to_ifd

    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_add_aovs_to_ifd__no_parms(self, patch_soho):
        mock_wrangler = MagicMock()

        mock_cam = MagicMock()
        mock_cam.wrangle.return_value = {}

        mock_now = MagicMock(spec=float)

        mgr = manager.AOVManager()

        calls = [
            call("enable_auto_aovs", "int", [1], skipdefault=False),
            call("auto_aovs", "str", [""], skipdefault=False)
        ]

        mgr.add_aovs_to_ifd(mock_wrangler, mock_cam, mock_now)

        patch_soho["soho"].SohoParm.assert_has_calls(calls)

    @patch.object(manager.AOVManager, "get_aovs_from_string")
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_add_aovs_to_ifd__disabled(self, mock_get, patch_soho):
        mock_wrangler = MagicMock()

        mock_enable_result = MagicMock()
        mock_enable_result.Value = [0]

        mock_cam = MagicMock()
        mock_cam.wrangle.return_value = {
            "enable_auto_aovs": mock_enable_result,
        }

        mock_now = MagicMock(spec=float)

        mgr = manager.AOVManager()

        calls = [
            call("enable_auto_aovs", "int", [1], skipdefault=False),
            call("auto_aovs", "str", [""], skipdefault=False)
        ]

        mgr.add_aovs_to_ifd(mock_wrangler, mock_cam, mock_now)

        patch_soho["soho"].SohoParm.assert_has_calls(calls)

    @patch("ht.sohohooks.aovs.manager.flatten_aov_items")
    @patch.object(manager.AOVManager, "get_aovs_from_string")
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_add_aovs_to_ifd__non_opid(self, mock_get, mock_flattened, patch_soho):
        mock_aov = MagicMock(spec=manager.AOV)

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

        mock_now = MagicMock(spec=float)

        mock_flattened.return_value = (mock_aov, )

        mgr = manager.AOVManager()

        calls = [
            call("enable_auto_aovs", "int", [1], skipdefault=False),
            call("auto_aovs", "str", [""], skipdefault=False)
        ]

        mgr.add_aovs_to_ifd(mock_wrangler, mock_cam, mock_now)

        patch_soho["soho"].SohoParm.assert_has_calls(calls)

        mock_get.assert_called_with(mock_aovs_result.Value[0])

        mock_aov.write_to_ifd.assert_called_with(mock_wrangler, mock_cam, mock_now)

        patch_soho["IFDapi"].ray_comment.assert_not_called()

    @patch("ht.sohohooks.aovs.manager.flatten_aov_items")
    @patch.object(manager.AOVManager, "get_aovs_from_string")
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_add_aovs_to_ifd__opid(self, mock_get, mock_flattened, patch_soho):
        mock_aov = MagicMock(spec=manager.AOV)
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

        mock_now = MagicMock(spec=float)

        mock_flattened.return_value = (mock_aov, )

        mgr = manager.AOVManager()

        calls = [
            call("enable_auto_aovs", "int", [1], skipdefault=False),
            call("auto_aovs", "str", [""], skipdefault=False)
        ]

        mgr.add_aovs_to_ifd(mock_wrangler, mock_cam, mock_now)

        patch_soho["soho"].SohoParm.assert_has_calls(calls)

        mock_get.assert_called_with(mock_aovs_result.Value[0])

        mock_aov.write_to_ifd.assert_called_with(mock_wrangler, mock_cam, mock_now)
        patch_soho["IFDapi"].ray_comment.assert_called()
        assert patch_soho["IFDsettings"]._GenerateOpId

    # add_group

    @patch.object(manager.AOVManager, "interface", new_callable=PropertyMock(return_value=None))
    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_add_group__no_interface(self, mock_groups, mock_interface):
        groups = {}

        mock_groups.return_value = groups

        mock_group = MagicMock(spec=manager.AOVGroup)

        mgr = manager.AOVManager()
        mgr.add_group(mock_group)

        assert groups == {mock_group.name: mock_group}

    @patch.object(manager.AOVManager, "interface", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_add_group__interface(self, mock_groups, mock_interface):
        interface = MagicMock()
        mock_interface.return_value = interface

        groups = {}
        mock_groups.return_value = groups

        mock_group = MagicMock(spec=manager.AOVGroup)

        mgr = manager.AOVManager()
        mgr.add_group(mock_group)

        assert groups == {mock_group.name: mock_group}
        interface.group_added_signal.emit.assert_called_with(mock_group)

    # clear

    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_clear(self):
        mock_aovs = MagicMock(spec=dict)
        mock_groups = MagicMock(spec=dict)

        mgr = manager.AOVManager()
        mgr._aovs = mock_aovs
        mgr._groups = mock_groups

        mgr.clear()

        mock_aovs.clear.assert_called()
        mock_groups.clear.assert_called()

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

        assert result == ()

    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_get_aovs_from_string__aovs_match_spaces(self, mock_aovs, mock_groups):
        mock_aov_n = MagicMock(spec=manager.AOV)
        mock_aov_p = MagicMock(spec=manager.AOV)

        mock_aovs.return_value = {"N": mock_aov_n, "P": mock_aov_p}
        mock_groups.return_value = {}

        mgr = manager.AOVManager()

        pattern = "N P R"

        result = mgr.get_aovs_from_string(pattern)

        assert result == (mock_aov_n, mock_aov_p)

    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_get_aovs_from_string__aovs_match_commas(self, mock_aovs, mock_groups):
        mock_aov_n = MagicMock(spec=manager.AOV)
        mock_aov_p = MagicMock(spec=manager.AOV)

        mock_aovs.return_value = {"N": mock_aov_n, "P": mock_aov_p}
        mock_groups.return_value = {}

        mgr = manager.AOVManager()

        pattern = "N,P,R"

        result = mgr.get_aovs_from_string(pattern)

        assert result == (mock_aov_n, mock_aov_p)

    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_get_aovs_from_string__groups_match_spaces(self, mock_aovs, mock_groups):
        mock_group1 = MagicMock(spec=manager.AOVGroup)
        mock_group2 = MagicMock(spec=manager.AOVGroup)

        mock_aovs.return_value = {}
        mock_groups.return_value = {"group1": mock_group1, "group2": mock_group2}

        mgr = manager.AOVManager()

        pattern = "@group1 @group3 @group2"

        result = mgr.get_aovs_from_string(pattern)

        assert result == (mock_group1, mock_group2)

    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_get_aovs_from_string__groups_match_commas(self, mock_aovs, mock_groups):
        mock_group1 = MagicMock(spec=manager.AOVGroup)
        mock_group2 = MagicMock(spec=manager.AOVGroup)

        mock_aovs.return_value = {}
        mock_groups.return_value = {"group1": mock_group1, "group2": mock_group2}

        mgr = manager.AOVManager()

        pattern = "@group1,@group3, @group2"

        result = mgr.get_aovs_from_string(pattern)

        assert result == (mock_group1, mock_group2)

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

        assert mgr._interface == mock_utils.AOVViewerInterface.return_value

    # load

    @patch.object(manager.AOVManager, "_merge_readers")
    @patch("ht.sohohooks.aovs.manager.AOVFile", autospec=True)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_load(self, mock_file, mock_merge):
        mgr = manager.AOVManager()

        mock_path = MagicMock(spec=str)

        mgr.load(mock_path)

        mock_file.assert_called_with(mock_path)

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
        mock_aov1 = MagicMock(spec=manager.AOV)
        mock_aov2 = MagicMock(spec=manager.AOV)

        aovs = {mock_aov2.variable: mock_aov2}
        mock_aovs.return_value = aovs

        mgr = manager.AOVManager()

        mgr.remove_aov(mock_aov1)

        assert aovs == {mock_aov2.variable: mock_aov2}

    @patch.object(manager.AOVManager, "interface", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_remove_aov__match_no_interface(self, mock_aovs, mock_interface):
        mock_interface.return_value = None

        mock_aov = MagicMock(spec=manager.AOV)

        aovs = {mock_aov.variable: mock_aov}
        mock_aovs.return_value = aovs

        mgr = manager.AOVManager()

        mgr.remove_aov(mock_aov)

        assert aovs == {}

    @patch.object(manager.AOVManager, "interface", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_remove_aov__match_interface(self, mock_aovs, mock_interface):
        interface = MagicMock()
        mock_interface.return_value = interface

        mock_aov = MagicMock(spec=manager.AOV)

        aovs = {mock_aov.variable: mock_aov}
        mock_aovs.return_value = aovs

        mgr = manager.AOVManager()

        mgr.remove_aov(mock_aov)

        assert aovs == {}

        interface.aov_removed_signal.emit.assert_called_with(mock_aov)

    # remove_group

    @patch.object(manager.AOVManager, "interface", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_remove_group__no_match(self, mock_groups, mock_interface):
        mock_group1 = MagicMock(spec=manager.AOVGroup)
        mock_group2 = MagicMock(spec=manager.AOVGroup)

        groups = {mock_group2.name: mock_group2}
        mock_groups.return_value = groups

        mgr = manager.AOVManager()

        mgr.remove_group(mock_group1)

        assert groups == {mock_group2.name: mock_group2}

    @patch.object(manager.AOVManager, "interface", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_remove_group__match_no_interface(self, mock_groups, mock_interface):
        mock_interface.return_value = None

        mock_group = MagicMock(spec=manager.AOVGroup)

        groups = {mock_group.name: mock_group}
        mock_groups.return_value = groups

        mgr = manager.AOVManager()

        mgr.remove_group(mock_group)

        assert groups == {}

    @patch.object(manager.AOVManager, "interface", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVManager, "__init__", lambda x: None)
    def test_remove_group__match_interface(self, mock_groups, mock_interface):
        interface = MagicMock()
        mock_interface.return_value = interface

        mock_group = MagicMock(spec=manager.AOVGroup)

        groups = {mock_group.name: mock_group}
        mock_groups.return_value = groups

        mgr = manager.AOVManager()

        mgr.remove_group(mock_group)

        assert groups == {}

        interface.group_removed_signal.emit.assert_called_with(mock_group)


class Test_AOVFile(object):
    """Test ht.sohohooks.aovs.manager.AOVFile object."""

    @patch.object(manager.AOVFile, "_init_from_file")
    @patch.object(manager.AOVFile, "exists", new_callable=PropertyMock(return_value=True))
    def test___init___exists(self, mock_exists, mock_init):
        mock_path = MagicMock(spec=str)

        aov_file = manager.AOVFile(mock_path)

        assert aov_file._path == mock_path
        assert aov_file._aovs == []
        assert aov_file._data == {}
        assert aov_file._groups == []

        mock_init.assert_called()

    @patch.object(manager.AOVFile, "_init_from_file")
    @patch.object(manager.AOVFile, "exists", new_callable=PropertyMock(return_value=False))
    def test___init___does_not_exist(self, mock_exists, mock_init):
        mock_path = MagicMock(spec=str)

        aov_file = manager.AOVFile(mock_path)

        assert aov_file._path == mock_path
        assert aov_file._aovs == []
        assert aov_file._data == {}
        assert aov_file._groups == []

        mock_init.assert_not_called()

    # _create_aovs

    @patch.object(manager.AOVFile, "aovs", new_callable=PropertyMock)
    @patch("ht.sohohooks.aovs.manager.AOV", autospec=True)
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

        assert definition == {"key": "value", "path": mock_path.return_value}

        assert aovs == [mock_aov.return_value]

    # _create_groups

    @patch.object(manager.AOVFile, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "path", new_callable=PropertyMock)
    @patch("ht.sohohooks.aovs.manager.AOVGroup", autospec=True)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test__create_groups_minimal(self, mock_group, mock_path, mock_groups):
        mock_group_name = MagicMock(spec=str)

        group_data = {}

        definitions = {mock_group_name: group_data}

        groups = []
        mock_groups.return_value = groups

        aov_file = manager.AOVFile(None)

        aov_file._create_groups(definitions)

        mock_group.assert_called_with(mock_group_name)

        assert groups == [mock_group.return_value]

        assert mock_group.return_value.path == mock_path.return_value

    @patch.object(manager.AOVFile, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "path", new_callable=PropertyMock)
    @patch("ht.sohohooks.aovs.manager.os.path.expandvars")
    @patch("ht.sohohooks.aovs.manager.AOVGroup", autospec=True)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test__create_groups_all_data(self, mock_group, mock_expand, mock_path, mock_groups):
        mock_group_name = MagicMock(spec=str)
        mock_includes = MagicMock(spec=list)
        mock_comment = MagicMock(spec=str)
        mock_priority = MagicMock(spec=int)
        mock_icon = MagicMock(spec=str)

        group_data = {
            consts.GROUP_INCLUDE_KEY: mock_includes,
            consts.COMMENT_KEY: mock_comment,
            consts.PRIORITY_KEY: mock_priority,
            consts.GROUP_ICON_KEY: mock_icon
        }

        definitions = {mock_group_name: group_data}

        groups = []
        mock_groups.return_value = groups

        aov_file = manager.AOVFile(None)

        aov_file._create_groups(definitions)

        mock_group.assert_called_with(mock_group_name)

        assert groups == [mock_group.return_value]

        mock_expand.assert_called_with(mock_icon)

        assert mock_group.return_value.path == mock_path.return_value
        assert mock_group.return_value.comment == mock_comment
        assert mock_group.return_value.priority == mock_priority
        assert mock_group.return_value.icon == mock_expand.return_value

        mock_group.return_value.includes.extend.assert_called_with(mock_includes)

    # _init_from_file

    @patch.object(manager.AOVFile, "_create_groups")
    @patch.object(manager.AOVFile, "_create_aovs")
    @patch("ht.sohohooks.aovs.manager.json.load", return_value={})
    @patch.object(manager.AOVFile, "path", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test__init_from_file__no_items(self, mock_path, mock_load, mock_create_aovs, mock_create_groups):
        aov_file = manager.AOVFile(None)

        with patch("__builtin__.open", mock_open()) as mock_handle:
            aov_file._init_from_file()

            mock_handle.assert_called_with(mock_path.return_value)

            mock_load.assert_called_with(mock_handle.return_value)

        mock_create_aovs.assert_not_called()
        mock_create_groups.assert_not_called()

    @patch.object(manager.AOVFile, "_create_groups")
    @patch.object(manager.AOVFile, "_create_aovs")
    @patch("ht.sohohooks.aovs.manager.json.load")
    @patch.object(manager.AOVFile, "path", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test__init_from_file__items(self, mock_path, mock_load, mock_create_aovs, mock_create_groups):
        mock_definitions = MagicMock(spec=dict)
        mock_groups = MagicMock(spec=dict)

        mock_load.return_value = {
            consts.FILE_DEFINITIONS_KEY: mock_definitions,
            consts.FILE_GROUPS_KEY: mock_groups,
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
        mock_aov = MagicMock(spec=manager.AOV)

        aov_file = manager.AOVFile(None)

        aov_file._aovs = [mock_aov]

        assert aov_file.aovs == [mock_aov]

        with pytest.raises(AttributeError):
            aov_file.aovs = []

    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_groups(self):
        mock_group = MagicMock(spec=manager.AOVGroup)

        aov_file = manager.AOVFile(None)

        aov_file._groups = [mock_group]

        assert aov_file.groups ==[mock_group]

        with pytest.raises(AttributeError):
            aov_file.groups = []

    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_path(self):
        mock_value = MagicMock(spec=str)

        aov_file = manager.AOVFile(None)

        aov_file._path = mock_value

        assert aov_file.path == mock_value

        with pytest.raises(AttributeError):
            aov_file.path = mock_value

    @patch.object(manager.AOVFile, "path", new_callable=PropertyMock)
    @patch("ht.sohohooks.aovs.manager.os.path.isfile")
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_exists(self, mock_isfile, mock_path):
        aov_file = manager.AOVFile(None)

        assert aov_file.exists == mock_isfile.return_value

        mock_isfile.assert_called_with(mock_path.return_value)

        with pytest.raises(AttributeError):
            aov_file.exists = False

    # add_aov

    @patch.object(manager.AOVFile, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_add_aov(self, mock_aovs):
        mock_aov = MagicMock(spec=manager.AOV)

        aov_file = manager.AOVFile(None)
        aov_file.add_aov(mock_aov)

        mock_aovs.return_value.append.assert_called_with(mock_aov)

    # add_group

    @patch.object(manager.AOVFile, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_add_group(self, mock_groups):
        mock_group = MagicMock(spec=manager.AOVGroup)

        aov_file = manager.AOVFile(None)
        aov_file.add_group(mock_group)

        mock_groups.return_value.append.assert_called_with(mock_group)

    # contains_aov

    @patch.object(manager.AOVFile, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_contains_aov(self, mock_aovs):
        mock_aov = MagicMock(spec=manager.AOV)

        aov_file = manager.AOVFile(None)
        result = aov_file.contains_aov(mock_aov)

        assert result == mock_aovs.return_value.__contains__.return_value

        mock_aovs.return_value.__contains__.assert_called_with(mock_aov)

    # contains_group

    @patch.object(manager.AOVFile, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_contains_group(self, mock_groups):
        mock_group = MagicMock(spec=manager.AOVGroup)

        aov_file = manager.AOVFile(None)
        result = aov_file.contains_group(mock_group)

        assert result == mock_groups.return_value.__contains__.return_value

        mock_groups.return_value.__contains__.assert_called_with(mock_group)

    # remove_aov

    @patch.object(manager.AOVFile, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_remove_aov(self, mock_aovs):
        mock_aov = MagicMock(spec=manager.AOV)

        aovs = [mock_aov]
        mock_aovs.return_value = aovs

        aov_file = manager.AOVFile(None)
        aov_file.remove_aov(mock_aov)

        assert aovs == []

    # remove_group

    @patch.object(manager.AOVFile, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_remove_group(self, mock_groups):
        mock_group = MagicMock(spec=manager.AOVGroup)

        groups = [mock_group]
        mock_groups.return_value = groups

        aov_file = manager.AOVFile(None)
        aov_file.remove_group(mock_group)

        assert groups == []

    # replace_aov

    @patch.object(manager.AOVFile, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_replace_aov(self, mock_aovs):
        mock_aov = MagicMock(spec=manager.AOV)

        mock_aovs.return_value.index.return_value = 3

        aov_file = manager.AOVFile(None)
        aov_file.replace_aov(mock_aov)

        mock_aovs.return_value.index.assert_called_with(mock_aov)
        mock_aovs.return_value.__setitem__.assert_called_with(3, mock_aov)

    # replace_group

    @patch.object(manager.AOVFile, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_replace_group(self, mock_groups):
        mock_group = MagicMock(spec=manager.AOVGroup)

        mock_groups.return_value.index.return_value = 2

        aov_file = manager.AOVFile(None)
        aov_file.replace_group(mock_group)

        mock_groups.return_value.index.assert_called_with(mock_group)
        mock_groups.return_value.__setitem__.assert_called_with(2, mock_group)

    # write_to_file

    @patch("ht.sohohooks.aovs.manager.json.dump")
    @patch.object(manager.AOVFile, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_write_to_file__nothing_explicit_path(self, mock_groups, mock_aovs, mock_dump):
        mock_groups.return_value = []
        mock_aovs.return_value = []

        aov_file = manager.AOVFile(None)

        mock_path = MagicMock(spec=str)

        with patch("__builtin__.open", mock_open()) as mock_handle:
            aov_file.write_to_file(mock_path)

            mock_handle.assert_called_with(mock_path, 'w')

            mock_dump.assert_called_with({}, mock_handle.return_value, indent=4)

    @patch("ht.sohohooks.aovs.manager.json.dump")
    @patch.object(manager.AOVFile, "path", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "aovs", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "groups", new_callable=PropertyMock)
    @patch.object(manager.AOVFile, "__init__", lambda x, y: None)
    def test_write_to_file(self, mock_groups, mock_aovs, mock_path, mock_dump):
        mock_group_key = MagicMock(spec=str)
        mock_group_value = MagicMock(spec=str)

        mock_group = MagicMock(spec=manager.AOVGroup)
        mock_group.as_data.return_value = {mock_group_key: mock_group_value}

        mock_groups.return_value = [mock_group]

        mock_aov_key = MagicMock(spec=str)
        mock_aov_value = MagicMock(spec=str)

        mock_aov = MagicMock(spec=manager.AOV)
        mock_aov.as_data.return_value = {mock_aov_key: mock_aov_value}

        mock_aovs.return_value = [mock_aov]

        aov_file = manager.AOVFile(None)

        expected = {
            consts.FILE_GROUPS_KEY: {mock_group_key: mock_group_value},
            consts.FILE_DEFINITIONS_KEY: [{mock_aov_key: mock_aov_value}]
        }

        with patch("__builtin__.open", mock_open()) as mock_handle:
            aov_file.write_to_file()

            mock_handle.assert_called_with(mock_path.return_value, 'w')

            mock_dump.assert_called_with(expected, mock_handle.return_value, indent=4)


class Test__find_aov_files(object):
    """Test ht.sohohooks.aovs.manager._find_aov_files."""

    @patch("ht.sohohooks.aovs.manager.glob.glob")
    @patch("ht.sohohooks.aovs.manager._get_aov_path_folders")
    def test_aov_path(self, mock_get_folders, mock_glob):
        mock_folder_path = MagicMock(spec=str)
        mock_get_folders.return_value = (mock_folder_path, )

        mock_path1 = MagicMock(spec=str)
        mock_path2 = MagicMock(spec=str)

        mock_glob.return_value = [mock_path1, mock_path2]

        with patch.dict(os.environ, {"HT_AOV_PATH": "value"}):
            result = manager._find_aov_files()

        assert result == (mock_path1, mock_path2)

        mock_get_folders.assert_called()

        mock_glob.assert_called_with(os.path.join(mock_folder_path, "*.json"))

    @patch("ht.sohohooks.aovs.manager.glob.glob")
    @patch("ht.sohohooks.aovs.manager._find_houdinipath_aov_folders")
    def test_houdini_path(self, mock_find, mock_glob):
        mock_folder_path = MagicMock(spec=str)
        mock_find.return_value = [mock_folder_path]

        mock_path1 = MagicMock(spec=str)
        mock_path2 = MagicMock(spec=str)

        mock_glob.return_value = [mock_path1, mock_path2]

        with patch.dict(os.environ, {}, clear=True):
            result = manager._find_aov_files()

        assert result == (mock_path1, mock_path2)

        mock_find.assert_called()

        mock_glob.assert_called_with(os.path.join(mock_folder_path, "*.json"))


class Test__find_houdinipath_aov_folders(object):
    """Test ht.sohohooks.aovs.manager._find_houdinipath_aov_folders."""

    @patch("ht.sohohooks.aovs.manager.hou.findDirectories")
    def test_no_dirs(self, mock_find, raise_hou_operationfailed):
        mock_find.side_effect = raise_hou_operationfailed

        result = manager._find_houdinipath_aov_folders()

        assert result == ()

    @patch("ht.sohohooks.aovs.manager.hou.findDirectories")
    def test_dirs(self, mock_find):
        result = manager._find_houdinipath_aov_folders()

        assert result == mock_find.return_value


class Test__get_aov_path_folders(object):
    """Test ht.sohohooks.aovs.manager._get_aov_path_folders."""

    def test_no_hpath(self):

        env_dict = {
            "HT_AOV_PATH": "path1:path2"
        }

        with patch.dict(os.environ, env_dict):
            result = manager._get_aov_path_folders()

        assert result == ("path1", "path2")

    @patch("ht.sohohooks.aovs.manager._find_houdinipath_aov_folders")
    def test_hpath_no_folders(self, mock_find):
        mock_find.return_value = ()

        env_dict = {
            "HT_AOV_PATH": "path1:path2:&"
        }

        with patch.dict(os.environ, env_dict):
            result = manager._get_aov_path_folders()

        assert result == ("path1", "path2", "&")

    @patch("ht.sohohooks.aovs.manager._find_houdinipath_aov_folders")
    def test_hpath_folders(self, mock_find):
        mock_find.return_value = ("hpath1", "hpath2")

        env_dict = {
            "HT_AOV_PATH": "path1:path2:&"
        }

        with patch.dict(os.environ, env_dict):
            result = manager._get_aov_path_folders()

        assert result == ("path1", "path2", "hpath1", "hpath2")


class Test_build_menu_script(object):
    """Test ht.sohohooks.aovs.manager.build_menu_script."""

    @patch("ht.sohohooks.aovs.manager.MANAGER", autospec=True)
    def test_no_groups(self, mock_manager):
        mock_manager.groups = None

        mock_aov1 = MagicMock(spec=manager.AOV)
        mock_aov2 = MagicMock(spec=manager.AOV)
        mock_aov3 = MagicMock(spec=manager.AOV)

        mock_manager.aovs = {"P": mock_aov1, "N": mock_aov2, "A": mock_aov3}

        result = manager.build_menu_script()

        assert result == ("A", "A", "N", "N", "P", "P")

    @patch("ht.sohohooks.aovs.manager.MANAGER", autospec=True)
    def test_with_groups(self, mock_manager):
        mock_group1 = MagicMock(spec=manager.AOVGroup)
        mock_group2 = MagicMock(spec=manager.AOVGroup)
        mock_group3 = MagicMock(spec=manager.AOVGroup)

        mock_manager.groups = {
            "group1": mock_group1,
            "group2": mock_group2,
            "group3": mock_group3,
        }

        mock_aov1 = MagicMock(spec=manager.AOV)
        mock_aov2 = MagicMock(spec=manager.AOV)
        mock_aov3 = MagicMock(spec=manager.AOV)

        mock_manager.aovs = {"P": mock_aov1, "N": mock_aov2, "A": mock_aov3}

        result = manager.build_menu_script()

        expected = ("@group1", "group1", "@group2", "group2", "@group3", "group3", "_separator_", "", "A", "A", "N", "N", "P", "P")

        assert result == expected


def test_flatten_aov_items():
    """Test ht.sohohooks.aovs.manager.flatten_aov_items."""
    mock_aov = MagicMock(spec=manager.AOV)

    mock_group_aov = MagicMock(spec=manager.AOV)

    mock_group = MagicMock(spec=manager.AOVGroup)
    type(mock_group).aovs = PropertyMock(return_value = [mock_group_aov])

    result = manager.flatten_aov_items((mock_aov, mock_group))

    assert result == (mock_aov, mock_group_aov)


@patch("ht.sohohooks.aovs.manager.MANAGER", autospec=True)
@patch("ht.sohohooks.aovs.manager.os.path.exists")
@patch("ht.sohohooks.aovs.manager.os.path.expandvars")
def test_load_json_files(mock_expand, mock_exists, mock_manager, mock_hou_ui):
    """Test ht.sohohooks.aovs.manager.load_json_files."""
    mock_expand.side_effect = ("expanded1", "expanded2")

    mock_exists.side_effect = (False, True)

    path_str = "path1 ; path2"

    mock_hou_ui.selectFile.return_value = path_str

    manager.load_json_files()

    mock_hou_ui.selectFile.assert_called_with(
        pattern="*.json",
        chooser_mode=hou.fileChooserMode.Read,
        multiple_select=True
    )

    mock_manager.load.assert_called_with("expanded2")
