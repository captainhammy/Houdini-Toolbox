"""Test the ht.sohohooks.aovs.manager module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import imp
import os

# Third Party Imports
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
# FIXTURES
# =============================================================================

@pytest.fixture
def init_file(mocker):
    """Fixture to initialize a file."""
    mocker.patch.object(manager.AOVFile, "__init__", lambda x, y: None)

    def create():
        return manager.AOVFile(None)

    return create


@pytest.fixture
def init_manager(mocker):
    """Fixture to initialize a manager."""
    mocker.patch.object(manager.AOVManager, "__init__", lambda x: None)

    def create():
        return manager.AOVManager()

    return create


# =============================================================================
# CLASSES
# =============================================================================

class Test_AOVManager(object):
    """Test ht.sohohooks.aovs.manager.AOVManager object."""

    def test___init__(self, mocker):
        mock_init = mocker.patch("ht.sohohooks.aovs.manager.AOVManager._init_from_files")

        mgr = manager.AOVManager()

        assert mgr._aovs == {}
        assert mgr._groups == {}
        assert mgr._interface is None
        mock_init.assert_called()

    # _build_intrinsic_groups

    def test__build_intrinsic_groups__new_group(self, init_manager, mocker):
        mock_aovs = mocker.patch.object(manager.AOVManager, "aovs", new_callable=mocker.PropertyMock)
        mock_groups = mocker.patch.object(manager.AOVManager, "groups", new_callable=mocker.PropertyMock)
        mock_add = mocker.patch.object(manager.AOVManager, "add_group")
        mock_int_group = mocker.patch("ht.sohohooks.aovs.manager.IntrinsicAOVGroup", autospec=True)

        mock_aov = mocker.MagicMock(spec=manager.AOV)
        mock_aov.intrinsics = ["int1"]

        mock_groups.return_value = {}

        mock_aovs.return_value = {mocker.MagicMock(spec=str): mock_aov}

        mgr = init_manager()
        mgr._build_intrinsic_groups()

        mock_int_group.assert_called_with("i:int1")
        mock_add.assert_called_with(mock_int_group.return_value)

        mock_int_group.return_value.aovs.append.assert_called_with(mock_aov)

    def test__build_intrinsic_groups__existing_group(self, init_manager, mocker):
        mock_aovs = mocker.patch.object(manager.AOVManager, "aovs", new_callable=mocker.PropertyMock)
        mock_groups = mocker.patch.object(manager.AOVManager, "groups", new_callable=mocker.PropertyMock)
        mock_add = mocker.patch.object(manager.AOVManager, "add_group")

        mock_aov = mocker.MagicMock(spec=manager.AOV)
        mock_aov.intrinsics = ["int1"]

        mock_group = mocker.MagicMock(spec=aov.IntrinsicAOVGroup)

        mock_groups.return_value = {"i:int1": mock_group}

        mock_aovs.return_value = {mocker.MagicMock(spec=str): mock_aov}

        mgr = init_manager()
        mgr._build_intrinsic_groups()

        mock_group.aovs.append.assert_called_with(mock_aov)
        mock_add.assert_not_called()

    # _init_from_files

    def test__init_from_files(self, init_manager, mocker):
        mock_find = mocker.patch("ht.sohohooks.aovs.manager._find_aov_files")
        mock_file = mocker.patch("ht.sohohooks.aovs.manager.AOVFile", autospec=True)
        mock_merge = mocker.patch.object(manager.AOVManager, "_merge_readers")
        mock_build = mocker.patch.object(manager.AOVManager, "_build_intrinsic_groups")

        mock_path = mocker.MagicMock(spec=str)
        mock_find.return_value = [mock_path]

        mgr = init_manager()
        mgr._init_from_files()

        mock_file.assert_called_with(mock_path)
        mock_merge.assert_called_with([mock_file.return_value])
        mock_build.assert_called()

    # _init_group_members

    def test__init_group_members(self, init_manager, mocker):
        mock_aovs = mocker.patch.object(manager.AOVManager, "aovs", new_callable=mocker.PropertyMock)

        mock_varname1 = mocker.MagicMock(spec=str)
        mock_varname2 = mocker.MagicMock(spec=str)

        mock_group = mocker.MagicMock(spec=manager.AOVGroup)
        mock_group.includes = [mock_varname1, mock_varname2]

        mock_aov = mocker.MagicMock(spec=manager.AOV)

        mock_aovs.return_value = {
            mock_varname1: mock_aov,
        }

        mgr = init_manager()
        mgr._init_group_members(mock_group)

        mock_group.aovs.append.assert_called_with(mock_aov)

    # _init_reader_aovs

    def test__init_reader_aovs__new_aov(self, init_manager, mocker):
        mock_aovs = mocker.patch.object(manager.AOVManager, "aovs", new_callable=mocker.PropertyMock)
        mock_add = mocker.patch.object(manager.AOVManager, "add_aov")

        mock_aov = mocker.MagicMock(spec=manager.AOV)

        mock_reader = mocker.MagicMock(spec=manager.AOVFile)
        mock_reader.aovs = [mock_aov]

        mock_aovs.return_value = {}

        mgr = init_manager()
        mgr._init_reader_aovs(mock_reader)

        mock_add.assert_called_with(mock_aov)

    def test__init_reader_aovs__matches_existing_priority_same(self, init_manager, mocker):
        mock_aovs = mocker.patch.object(manager.AOVManager, "aovs", new_callable=mocker.PropertyMock)
        mock_add = mocker.patch.object(manager.AOVManager, "add_aov")

        mock_varname = mocker.MagicMock(spec=str)
        mock_priority = mocker.MagicMock(spec=int)

        mock_new_aov = mocker.MagicMock(spec=manager.AOV)
        mock_new_aov.variable = mock_varname
        mock_new_aov.priority = mock_priority

        mock_existing_aov = mocker.MagicMock(spec=manager.AOV)
        mock_existing_aov.variable = mock_varname
        mock_existing_aov.priority = mock_priority

        mock_reader = mocker.MagicMock(spec=manager.AOVFile)
        mock_reader.aovs = [mock_new_aov]

        mock_aovs.return_value = {mock_varname: mock_existing_aov}

        mgr = init_manager()
        mgr._init_reader_aovs(mock_reader)

        mock_add.assert_not_called()

    def test__init_reader_aovs__matches_existing_priority_lower(self, init_manager, mocker):
        mock_aovs = mocker.patch.object(manager.AOVManager, "aovs", new_callable=mocker.PropertyMock)
        mock_add = mocker.patch.object(manager.AOVManager, "add_aov")

        mock_varname = mocker.MagicMock(spec=str)

        mock_new_aov = mocker.MagicMock(spec=manager.AOV)
        mock_new_aov.variable = mock_varname
        mock_new_aov.priority = 3

        mock_existing_aov =mocker.MagicMock(spec=manager.AOV)
        mock_existing_aov.variable = mock_varname
        mock_existing_aov.priority = 2

        mock_reader = mocker.MagicMock(spec=manager.AOVFile)
        mock_reader.aovs = [mock_new_aov]

        mock_aovs.return_value = {mock_varname: mock_existing_aov}

        mgr = init_manager()
        mgr._init_reader_aovs(mock_reader)

        mock_add.assert_called_with(mock_new_aov)

    # _init_reader_groups

    def test__init_reader_groups__new_group(self, init_manager, mocker):
        mock_init = mocker.patch.object(manager.AOVManager, "_init_group_members")
        mock_groups = mocker.patch.object(manager.AOVManager, "groups", new_callable=mocker.PropertyMock)
        mock_add = mocker.patch.object(manager.AOVManager, "add_group")

        mock_group = mocker.MagicMock(spec=manager.AOVGroup)

        mock_reader = mocker.MagicMock(spec=manager.AOVFile)
        mock_reader.groups = [mock_group]

        mock_groups.return_value = {}

        mgr = init_manager()
        mgr._init_reader_groups(mock_reader)

        mock_init.assert_called_with(mock_group)

        mock_add.assert_called_with(mock_group)

    def test__init_reader_groups__matches_existing_priority_same(self, init_manager, mocker):
        mock_init = mocker.patch.object(manager.AOVManager, "_init_group_members")
        mock_groups = mocker.patch.object(manager.AOVManager, "groups", new_callable=mocker.PropertyMock)
        mock_add = mocker.patch.object(manager.AOVManager, "add_group")

        mock_group_name = mocker.MagicMock(spec=str)
        mock_priority = mocker.MagicMock(spec=int)

        mock_new_group = mocker.MagicMock(spec=manager.AOVGroup)
        mock_new_group.name = mock_group_name
        mock_new_group.priority = mock_priority

        mock_reader = mocker.MagicMock(spec=manager.AOVFile)
        mock_reader.groups = [mock_new_group]

        mock_existing_group = mocker.MagicMock(spec=manager.AOVGroup)
        mock_existing_group.name = mock_group_name
        mock_existing_group.priority = mock_priority

        mock_groups.return_value = {mock_group_name: mock_existing_group}

        mgr = init_manager()
        mgr._init_reader_groups(mock_reader)

        mock_init.assert_called_with(mock_new_group)

        mock_add.assert_not_called()

    def test__init_reader_groups__matches_existing_priority_lower(self, init_manager, mocker):
        mock_init = mocker.patch.object(manager.AOVManager, "_init_group_members")
        mock_groups = mocker.patch.object(manager.AOVManager, "groups", new_callable=mocker.PropertyMock)
        mock_add = mocker.patch.object(manager.AOVManager, "add_group")

        mock_group_name = mocker.MagicMock(spec=str)

        mock_new_group = mocker.MagicMock(spec=manager.AOV)
        mock_new_group.name = mock_group_name
        mock_new_group.priority = 3

        mock_reader = mocker.MagicMock(spec=manager.AOVFile)
        mock_reader.groups = [mock_new_group]

        mock_existing_group = mocker.MagicMock(spec=manager.AOV)
        mock_existing_group.name = mock_group_name
        mock_existing_group.priority = 2

        mock_groups.return_value = {mock_group_name: mock_existing_group}

        mgr = init_manager()
        mgr._init_reader_groups(mock_reader)

        mock_init.assert_called_with(mock_new_group)

        mock_add.assert_called_with(mock_new_group)

    # _merge_readers

    def test__merge_readers(self, init_manager, mocker):
        mock_init_aovs = mocker.patch.object(manager.AOVManager, "_init_reader_aovs")
        mock_init_groups = mocker.patch.object(manager.AOVManager, "_init_reader_groups")

        mock_reader = mocker.MagicMock(spec=manager.AOVFile)

        readers = [mock_reader]

        mgr = init_manager()
        mgr._merge_readers(readers)

        mock_init_aovs.assert_called_with(mock_reader)
        mock_init_groups.assert_called_with(mock_reader)

    # Properties

    def test_aovs(self, init_manager, mocker):
        mock_value = mocker.MagicMock(spec=list)

        mgr = init_manager()
        mgr._aovs = mock_value
        assert mgr.aovs == mock_value

    def test_groups(self, init_manager, mocker):
        mock_value = mocker.MagicMock(spec=list)

        mgr = init_manager()
        mgr._groups = mock_value
        assert mgr.groups == mock_value

    def test_interface(self, init_manager, mocker):
        mock_value = mocker.MagicMock()

        mgr = init_manager()
        mgr._interface = mock_value
        assert mgr.interface == mock_value

    # add_aov

    def test_add_aov__no_interface(self, init_manager, mocker):
        mock_aovs = mocker.patch.object(manager.AOVManager, "aovs", new_callable=mocker.PropertyMock)
        mocker.patch.object(manager.AOVManager, "interface", new_callable=mocker.PropertyMock(return_value=None))

        aovs = {}

        mock_aovs.return_value = aovs

        mock_aov = mocker.MagicMock(spec=manager.AOV)

        mgr = init_manager()
        mgr.add_aov(mock_aov)

        assert aovs == {mock_aov.variable: mock_aov}

    def test_add_aov__interface(self, init_manager, mocker):
        mock_aovs = mocker.patch.object(manager.AOVManager, "aovs", new_callable=mocker.PropertyMock)
        mock_interface = mocker.patch.object(manager.AOVManager, "interface", new_callable=mocker.PropertyMock)

        interface = mocker.MagicMock()
        mock_interface.return_value = interface

        aovs = {}
        mock_aovs.return_value = aovs

        mock_aov = mocker.MagicMock(spec=manager.AOV)

        mgr = init_manager()
        mgr.add_aov(mock_aov)

        assert aovs == {mock_aov.variable: mock_aov}
        interface.aov_added_signal.emit.assert_called_with(mock_aov)

    # add_aovs_to_ifd

    def test_add_aovs_to_ifd__no_parms(self, init_manager, mocker, patch_soho):
        mock_wrangler = mocker.MagicMock()

        mock_cam = mocker.MagicMock()
        mock_cam.wrangle.return_value = {}

        mock_now = mocker.MagicMock(spec=float)

        mgr = init_manager()

        calls = [
            mocker.call("enable_auto_aovs", "int", [1], skipdefault=False),
            mocker.call("auto_aovs", "str", [""], skipdefault=False)
        ]

        mgr.add_aovs_to_ifd(mock_wrangler, mock_cam, mock_now)

        patch_soho.soho.SohoParm.assert_has_calls(calls)

    def test_add_aovs_to_ifd__disabled(self, init_manager, mocker, patch_soho):
        mocker.patch.object(manager.AOVManager, "get_aovs_from_string")

        mock_wrangler = mocker.MagicMock()

        mock_enable_result = mocker.MagicMock()
        mock_enable_result.Value = [0]

        mock_cam = mocker.MagicMock()
        mock_cam.wrangle.return_value = {
            "enable_auto_aovs": mock_enable_result,
        }

        mock_now = mocker.MagicMock(spec=float)

        mgr = init_manager()

        calls = [
            mocker.call("enable_auto_aovs", "int", [1], skipdefault=False),
            mocker.call("auto_aovs", "str", [""], skipdefault=False)
        ]

        mgr.add_aovs_to_ifd(mock_wrangler, mock_cam, mock_now)

        patch_soho.soho.SohoParm.assert_has_calls(calls)

    def test_add_aovs_to_ifd__non_opid(self, init_manager, mocker, patch_soho):
        mock_get = mocker.patch.object(manager.AOVManager, "get_aovs_from_string")
        mock_flattened = mocker.patch("ht.sohohooks.aovs.manager.flatten_aov_items")

        mock_aov = mocker.MagicMock(spec=manager.AOV)

        mock_wrangler = mocker.MagicMock()

        mock_enable_result = mocker.MagicMock()
        mock_enable_result.Value = [1]

        mock_aovs_result = mocker.MagicMock()

        mock_cam = mocker.MagicMock()
        mock_cam.wrangle.return_value = {
            "enable_auto_aovs": mock_enable_result,
            "auto_aovs": mock_aovs_result,
        }

        mock_get.return_value = [mock_aov]

        mock_now = mocker.MagicMock(spec=float)

        mock_flattened.return_value = (mock_aov, )

        mgr = init_manager()

        calls = [
            mocker.call("enable_auto_aovs", "int", [1], skipdefault=False),
            mocker.call("auto_aovs", "str", [""], skipdefault=False)
        ]

        mgr.add_aovs_to_ifd(mock_wrangler, mock_cam, mock_now)

        patch_soho.soho.SohoParm.assert_has_calls(calls)

        mock_get.assert_called_with(mock_aovs_result.Value[0])

        mock_aov.write_to_ifd.assert_called_with(mock_wrangler, mock_cam, mock_now)

        patch_soho.IFDapi.ray_comment.assert_not_called()

    def test_add_aovs_to_ifd__opid(self, init_manager, mocker, patch_soho):
        mock_get = mocker.patch.object(manager.AOVManager, "get_aovs_from_string")
        mock_flattened = mocker.patch("ht.sohohooks.aovs.manager.flatten_aov_items")

        mock_aov = mocker.MagicMock(spec=manager.AOV)
        mock_aov.variable = "Op_Id"

        mock_wrangler = mocker.MagicMock()

        mock_enable_result = mocker.MagicMock()
        mock_enable_result.Value = [1]

        mock_aovs_result = mocker.MagicMock()

        mock_cam = mocker.MagicMock()
        mock_cam.wrangle.return_value = {
            "enable_auto_aovs": mock_enable_result,
            "auto_aovs": mock_aovs_result,
        }

        mock_get.return_value = [mock_aov]

        mock_now = mocker.MagicMock(spec=float)

        mock_flattened.return_value = (mock_aov, )

        mgr = init_manager()

        calls = [
            mocker.call("enable_auto_aovs", "int", [1], skipdefault=False),
            mocker.call("auto_aovs", "str", [""], skipdefault=False)
        ]

        mgr.add_aovs_to_ifd(mock_wrangler, mock_cam, mock_now)

        patch_soho.soho.SohoParm.assert_has_calls(calls)

        mock_get.assert_called_with(mock_aovs_result.Value[0])

        mock_aov.write_to_ifd.assert_called_with(mock_wrangler, mock_cam, mock_now)
        patch_soho.IFDapi.ray_comment.assert_called()
        assert patch_soho.IFDsettings._GenerateOpId

    # add_group

    def test_add_group__no_interface(self, init_manager, mocker):
        mock_groups = mocker.patch.object(manager.AOVManager, "groups", new_callable=mocker.PropertyMock)
        mocker.patch.object(manager.AOVManager, "interface", new_callable=mocker.PropertyMock(return_value=None))

        groups = {}

        mock_groups.return_value = groups

        mock_group = mocker.MagicMock(spec=manager.AOVGroup)

        mgr = init_manager()
        mgr.add_group(mock_group)

        assert groups == {mock_group.name: mock_group}

    def test_add_group__interface(self, init_manager, mocker):
        mock_groups = mocker.patch.object(manager.AOVManager, "groups", new_callable=mocker.PropertyMock)
        mock_interface = mocker.patch.object(manager.AOVManager, "interface", new_callable=mocker.PropertyMock)

        interface = mocker.MagicMock()
        mock_interface.return_value = interface

        groups = {}
        mock_groups.return_value = groups

        mock_group = mocker.MagicMock(spec=manager.AOVGroup)

        mgr = init_manager()
        mgr.add_group(mock_group)

        assert groups == {mock_group.name: mock_group}
        interface.group_added_signal.emit.assert_called_with(mock_group)

    # clear

    def test_clear(self, init_manager, mocker):
        mock_aovs = mocker.MagicMock(spec=dict)
        mock_groups = mocker.MagicMock(spec=dict)

        mgr = init_manager()
        mgr._aovs = mock_aovs
        mgr._groups = mock_groups

        mgr.clear()

        mock_aovs.clear.assert_called()
        mock_groups.clear.assert_called()

    # get_aovs_from_string

    def test_get_aovs_from_string__no_matches(self, init_manager, mocker):
        mock_aovs = mocker.patch.object(manager.AOVManager, "aovs", new_callable=mocker.PropertyMock)
        mock_groups = mocker.patch.object(manager.AOVManager, "groups", new_callable=mocker.PropertyMock)

        mock_aovs.return_value = {}
        mock_groups.return_value = {}

        mgr = init_manager()

        pattern = ""

        result = mgr.get_aovs_from_string(pattern)

        assert result == ()

    def test_get_aovs_from_string__aovs_match_spaces(self, init_manager, mocker):
        mock_aovs = mocker.patch.object(manager.AOVManager, "aovs", new_callable=mocker.PropertyMock)
        mock_groups = mocker.patch.object(manager.AOVManager, "groups", new_callable=mocker.PropertyMock)

        mock_aov_n = mocker.MagicMock(spec=manager.AOV)
        mock_aov_p = mocker.MagicMock(spec=manager.AOV)

        mock_aovs.return_value = {"N": mock_aov_n, "P": mock_aov_p}
        mock_groups.return_value = {}

        mgr = init_manager()

        pattern = "N P R"

        result = mgr.get_aovs_from_string(pattern)

        assert result == (mock_aov_n, mock_aov_p)

    def test_get_aovs_from_string__aovs_match_commas(self, init_manager, mocker):
        mock_aovs = mocker.patch.object(manager.AOVManager, "aovs", new_callable=mocker.PropertyMock)
        mock_groups = mocker.patch.object(manager.AOVManager, "groups", new_callable=mocker.PropertyMock)

        mock_aov_n = mocker.MagicMock(spec=manager.AOV)
        mock_aov_p = mocker.MagicMock(spec=manager.AOV)

        mock_aovs.return_value = {"N": mock_aov_n, "P": mock_aov_p}
        mock_groups.return_value = {}

        mgr = init_manager()

        pattern = "N,P,R"

        result = mgr.get_aovs_from_string(pattern)

        assert result == (mock_aov_n, mock_aov_p)

    def test_get_aovs_from_string__groups_match_spaces(self, init_manager, mocker):
        mock_aovs = mocker.patch.object(manager.AOVManager, "aovs", new_callable=mocker.PropertyMock)
        mock_groups = mocker.patch.object(manager.AOVManager, "groups", new_callable=mocker.PropertyMock)

        mock_group1 = mocker.MagicMock(spec=manager.AOVGroup)
        mock_group2 = mocker.MagicMock(spec=manager.AOVGroup)

        mock_aovs.return_value = {}
        mock_groups.return_value = {"group1": mock_group1, "group2": mock_group2}

        mgr = init_manager()

        pattern = "@group1 @group3 @group2"

        result = mgr.get_aovs_from_string(pattern)

        assert result == (mock_group1, mock_group2)

    def test_get_aovs_from_string__groups_match_commas(self, init_manager, mocker):
        mock_aovs = mocker.patch.object(manager.AOVManager, "aovs", new_callable=mocker.PropertyMock)
        mock_groups = mocker.patch.object(manager.AOVManager, "groups", new_callable=mocker.PropertyMock)

        mock_group1 = mocker.MagicMock(spec=manager.AOVGroup)
        mock_group2 = mocker.MagicMock(spec=manager.AOVGroup)

        mock_aovs.return_value = {}
        mock_groups.return_value = {"group1": mock_group1, "group2": mock_group2}

        mgr = init_manager()

        pattern = "@group1,@group3, @group2"

        result = mgr.get_aovs_from_string(pattern)

        assert result == (mock_group1, mock_group2)

    # init_interface

    def test_init_interface(self, init_manager, mocker):
        mock_utils = mocker.MagicMock()

        modules = {
            "ht.ui.aovs.utils": mock_utils
        }

        mgr = init_manager()

        mocker.patch.dict("sys.modules", modules)
        mgr.init_interface()

        assert mgr._interface == mock_utils.AOVViewerInterface.return_value

    # load

    def test_load(self, init_manager, mocker):
        mock_file = mocker.patch("ht.sohohooks.aovs.manager.AOVFile", autospec=True)
        mock_merge = mocker.patch.object(manager.AOVManager, "_merge_readers")

        mgr = init_manager()

        mock_path = mocker.MagicMock(spec=str)

        mgr.load(mock_path)

        mock_file.assert_called_with(mock_path)

        mock_merge.assert_called_with([mock_file.return_value])

    # reload

    def test_reload(self, init_manager, mocker):
        mock_clear = mocker.patch.object(manager.AOVManager, "clear")
        mock_init = mocker.patch.object(manager.AOVManager, "_init_from_files")

        mgr = init_manager()

        mgr.reload()

        mock_clear.assert_called()
        mock_init.assert_called()

    # remove_aov

    def test_remove_aov__no_match(self, init_manager, mocker):
        mock_aovs = mocker.patch.object(manager.AOVManager, "aovs", new_callable=mocker.PropertyMock)
        mocker.patch.object(manager.AOVManager, "interface", new_callable=mocker.PropertyMock)

        mock_aov1 = mocker.MagicMock(spec=manager.AOV)
        mock_aov2 = mocker.MagicMock(spec=manager.AOV)

        aovs = {mock_aov2.variable: mock_aov2}
        mock_aovs.return_value = aovs

        mgr = init_manager()

        mgr.remove_aov(mock_aov1)

        assert aovs == {mock_aov2.variable: mock_aov2}

    def test_remove_aov__match_no_interface(self, init_manager, mocker):
        mock_aovs = mocker.patch.object(manager.AOVManager, "aovs", new_callable=mocker.PropertyMock)
        mock_interface = mocker.patch.object(manager.AOVManager, "interface", new_callable=mocker.PropertyMock)

        mock_interface.return_value = None

        mock_aov = mocker.MagicMock(spec=manager.AOV)

        aovs = {mock_aov.variable: mock_aov}
        mock_aovs.return_value = aovs

        mgr = init_manager()

        mgr.remove_aov(mock_aov)

        assert aovs == {}

    def test_remove_aov__match_interface(self, init_manager, mocker):
        mock_aovs = mocker.patch.object(manager.AOVManager, "aovs", new_callable=mocker.PropertyMock)
        mock_interface = mocker.patch.object(manager.AOVManager, "interface", new_callable=mocker.PropertyMock)

        interface = mocker.MagicMock()
        mock_interface.return_value = interface

        mock_aov = mocker.MagicMock(spec=manager.AOV)

        aovs = {mock_aov.variable: mock_aov}
        mock_aovs.return_value = aovs

        mgr = init_manager()

        mgr.remove_aov(mock_aov)

        assert aovs == {}

        interface.aov_removed_signal.emit.assert_called_with(mock_aov)

    # remove_group

    def test_remove_group__no_match(self, init_manager, mocker):
        mock_groups = mocker.patch.object(manager.AOVManager, "groups", new_callable=mocker.PropertyMock)
        mock_interface = mocker.patch.object(manager.AOVManager, "interface", new_callable=mocker.PropertyMock)

        mock_group1 = mocker.MagicMock(spec=manager.AOVGroup)
        mock_group2 = mocker.MagicMock(spec=manager.AOVGroup)

        groups = {mock_group2.name: mock_group2}
        mock_groups.return_value = groups

        mgr = init_manager()

        mgr.remove_group(mock_group1)

        assert groups == {mock_group2.name: mock_group2}

    def test_remove_group__match_no_interface(self, init_manager, mocker):
        mock_groups = mocker.patch.object(manager.AOVManager, "groups", new_callable=mocker.PropertyMock)
        mock_interface = mocker.patch.object(manager.AOVManager, "interface", new_callable=mocker.PropertyMock)

        mock_interface.return_value = None

        mock_group = mocker.MagicMock(spec=manager.AOVGroup)

        groups = {mock_group.name: mock_group}
        mock_groups.return_value = groups

        mgr = init_manager()

        mgr.remove_group(mock_group)

        assert groups == {}

    def test_remove_group__match_interface(self, init_manager, mocker):
        mock_groups = mocker.patch.object(manager.AOVManager, "groups", new_callable=mocker.PropertyMock)
        mock_interface = mocker.patch.object(manager.AOVManager, "interface", new_callable=mocker.PropertyMock)

        interface = mocker.MagicMock()
        mock_interface.return_value = interface

        mock_group = mocker.MagicMock(spec=manager.AOVGroup)

        groups = {mock_group.name: mock_group}
        mock_groups.return_value = groups

        mgr = init_manager()

        mgr.remove_group(mock_group)

        assert groups == {}

        interface.group_removed_signal.emit.assert_called_with(mock_group)


class Test_AOVFile(object):
    """Test ht.sohohooks.aovs.manager.AOVFile object."""

    # __init__

    def test___init___exists(self, mocker):
        mocker.patch.object(manager.AOVFile, "exists", new_callable=mocker.PropertyMock(return_value=True))
        mock_init = mocker.patch.object(manager.AOVFile, "_init_from_file")

        mock_path = mocker.MagicMock(spec=str)

        aov_file = manager.AOVFile(mock_path)

        assert aov_file._path == mock_path
        assert aov_file._aovs == []
        assert aov_file._data == {}
        assert aov_file._groups == []

        mock_init.assert_called()

    def test___init___does_not_exist(self, mocker):
        mocker.patch.object(manager.AOVFile, "exists", new_callable=mocker.PropertyMock(return_value=False))
        mock_init = mocker.patch.object(manager.AOVFile, "_init_from_file")

        mock_path = mocker.MagicMock(spec=str)

        aov_file = manager.AOVFile(mock_path)

        assert aov_file._path == mock_path
        assert aov_file._aovs == []
        assert aov_file._data == {}
        assert aov_file._groups == []

        mock_init.assert_not_called()

    # Non-Public Methods

    # _create_aovs

    def test__create_aovs(self, init_file, mocker):
        mock_path = mocker.patch.object(manager.AOVFile, "path", new_callable=mocker.PropertyMock)
        mock_aov = mocker.patch("ht.sohohooks.aovs.manager.AOV", autospec=True)
        mock_aovs = mocker.patch.object(manager.AOVFile, "aovs", new_callable=mocker.PropertyMock)

        mock_key = mocker.MagicMock(spec=str)
        mock_value = mocker.MagicMock(spec=str)

        definition = {mock_key: mock_value}
        definitions = [definition]

        aovs = []
        mock_aovs.return_value = aovs

        aov_file = init_file()

        aov_file._create_aovs(definitions)

        mock_aov.assert_called_with({mock_key: mock_value, "path": mock_path.return_value})

        # Test that the path got added to the definition.
        assert definition == {mock_key: mock_value, "path": mock_path.return_value}

        assert aovs == [mock_aov.return_value]

    # _create_groups

    def test__create_groups_minimal(self, init_file, mocker):
        mock_group = mocker.patch("ht.sohohooks.aovs.manager.AOVGroup", autospec=True)
        mock_path = mocker.patch.object(manager.AOVFile, "path", new_callable=mocker.PropertyMock)
        mock_groups = mocker.patch.object(manager.AOVFile, "groups", new_callable=mocker.PropertyMock)

        mock_group_name = mocker.MagicMock(spec=str)

        group_data = {}

        definitions = {mock_group_name: group_data}

        groups = []
        mock_groups.return_value = groups

        aov_file = init_file()

        aov_file._create_groups(definitions)

        mock_group.assert_called_with(mock_group_name)

        assert groups == [mock_group.return_value]

        assert mock_group.return_value.path == mock_path.return_value

    def test__create_groups_all_data(self, init_file, mocker):
        mock_group = mocker.patch("ht.sohohooks.aovs.manager.AOVGroup", autospec=True)
        mock_expand = mocker.patch("ht.sohohooks.aovs.manager.os.path.expandvars")
        mock_path = mocker.patch.object(manager.AOVFile, "path", new_callable=mocker.PropertyMock)
        mock_groups = mocker.patch.object(manager.AOVFile, "groups", new_callable=mocker.PropertyMock)

        mock_group_name = mocker.MagicMock(spec=str)
        mock_includes = mocker.MagicMock(spec=list)
        mock_comment = mocker.MagicMock(spec=str)
        mock_priority = mocker.MagicMock(spec=int)
        mock_icon = mocker.MagicMock(spec=str)

        group_data = {
            consts.GROUP_INCLUDE_KEY: mock_includes,
            consts.COMMENT_KEY: mock_comment,
            consts.PRIORITY_KEY: mock_priority,
            consts.GROUP_ICON_KEY: mock_icon
        }

        definitions = {mock_group_name: group_data}

        groups = []
        mock_groups.return_value = groups

        aov_file = init_file()

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

    def test__init_from_file__no_items(self, init_file, mocker):
        mock_path = mocker.patch.object(manager.AOVFile, "path", new_callable=mocker.PropertyMock)
        mock_load = mocker.patch("ht.sohohooks.aovs.manager.json.load", return_value={})
        mock_create_aovs = mocker.patch.object(manager.AOVFile, "_create_aovs")
        mock_create_groups = mocker.patch.object(manager.AOVFile, "_create_groups")

        aov_file = init_file()

        mock_handle = mocker.mock_open()

        mocker.patch("__builtin__.open", mock_handle)

        aov_file._init_from_file()

        mock_handle.assert_called_with(mock_path.return_value)

        mock_load.assert_called_with(mock_handle.return_value)

        mock_create_aovs.assert_not_called()
        mock_create_groups.assert_not_called()

    def test__init_from_file__items(self, init_file, mocker):
        mock_path = mocker.patch.object(manager.AOVFile, "path", new_callable=mocker.PropertyMock)
        mock_load = mocker.patch("ht.sohohooks.aovs.manager.json.load")
        mock_create_aovs = mocker.patch.object(manager.AOVFile, "_create_aovs")
        mock_create_groups = mocker.patch.object(manager.AOVFile, "_create_groups")

        mock_definitions = mocker.MagicMock(spec=dict)
        mock_groups = mocker.MagicMock(spec=dict)

        mock_load.return_value = {
            consts.FILE_DEFINITIONS_KEY: mock_definitions,
            consts.FILE_GROUPS_KEY: mock_groups,
        }

        aov_file = init_file()

        mock_handle = mocker.mock_open()

        mocker.patch("__builtin__.open", mock_handle)

        aov_file._init_from_file()

        mock_handle.assert_called_with(mock_path.return_value)

        mock_load.assert_called_with(mock_handle.return_value)

        mock_create_aovs.assert_called_with(mock_definitions)
        mock_create_groups.assert_called_with(mock_groups)

    # Properties

    def test_aovs(self, init_file, mocker):
        mock_aov = mocker.MagicMock(spec=manager.AOV)

        aov_file = init_file()
        aov_file._aovs = [mock_aov]
        assert aov_file.aovs == [mock_aov]

    def test_groups(self, init_file, mocker):
        mock_group = mocker.MagicMock(spec=manager.AOVGroup)

        aov_file = init_file()
        aov_file._groups = [mock_group]
        assert aov_file.groups == [mock_group]

    def test_path(self, init_file, mocker):
        mock_value = mocker.MagicMock(spec=str)

        aov_file = init_file()
        aov_file._path = mock_value
        assert aov_file.path == mock_value

    def test_exists(self, init_file, mocker):
        mock_isfile = mocker.patch("ht.sohohooks.aovs.manager.os.path.isfile")
        mock_path = mocker.patch.object(manager.AOVFile, "path", new_callable=mocker.PropertyMock)

        aov_file = init_file()

        assert aov_file.exists == mock_isfile.return_value

        mock_isfile.assert_called_with(mock_path.return_value)

    # Methods

    def test_add_aov(self, init_file, mocker):
        mock_aovs = mocker.patch.object(manager.AOVFile, "aovs", new_callable=mocker.PropertyMock)

        mock_aov = mocker.MagicMock(spec=manager.AOV)

        aov_file = init_file()
        aov_file.add_aov(mock_aov)

        mock_aovs.return_value.append.assert_called_with(mock_aov)

    def test_add_group(self, init_file, mocker):
        mock_groups = mocker.patch.object(manager.AOVFile, "groups", new_callable=mocker.PropertyMock)

        mock_group = mocker.MagicMock(spec=manager.AOVGroup)

        aov_file = init_file()
        aov_file.add_group(mock_group)

        mock_groups.return_value.append.assert_called_with(mock_group)

    def test_contains_aov(self, init_file, mocker):
        mock_aovs = mocker.patch.object(manager.AOVFile, "aovs", new_callable=mocker.PropertyMock)

        mock_aov = mocker.MagicMock(spec=manager.AOV)

        aov_file = init_file()
        result = aov_file.contains_aov(mock_aov)

        assert result == mock_aovs.return_value.__contains__.return_value

        mock_aovs.return_value.__contains__.assert_called_with(mock_aov)

    def test_contains_group(self, init_file, mocker):
        mock_groups = mocker.patch.object(manager.AOVFile, "groups", new_callable=mocker.PropertyMock)

        mock_group = mocker.MagicMock(spec=manager.AOVGroup)

        aov_file = init_file()
        result = aov_file.contains_group(mock_group)

        assert result == mock_groups.return_value.__contains__.return_value

        mock_groups.return_value.__contains__.assert_called_with(mock_group)

    def test_remove_aov(self, init_file, mocker):
        mock_aovs = mocker.patch.object(manager.AOVFile, "aovs", new_callable=mocker.PropertyMock)

        mock_aov = mocker.MagicMock(spec=manager.AOV)

        aovs = [mock_aov]
        mock_aovs.return_value = aovs

        aov_file = init_file()
        aov_file.remove_aov(mock_aov)

        assert aovs == []

    def test_remove_group(self, init_file, mocker):
        mock_groups = mocker.patch.object(manager.AOVFile, "groups", new_callable=mocker.PropertyMock)

        mock_group = mocker.MagicMock(spec=manager.AOVGroup)

        groups = [mock_group]
        mock_groups.return_value = groups

        aov_file = init_file()
        aov_file.remove_group(mock_group)

        assert groups == []

    def test_replace_aov(self, init_file, mocker):
        mock_aovs = mocker.patch.object(manager.AOVFile, "aovs", new_callable=mocker.PropertyMock)

        mock_aov = mocker.MagicMock(spec=manager.AOV)

        mock_idx = mocker.MagicMock(spec=int)
        mock_aovs.return_value.index.return_value = mock_idx

        aov_file = init_file()
        aov_file.replace_aov(mock_aov)

        mock_aovs.return_value.index.assert_called_with(mock_aov)
        mock_aovs.return_value.__setitem__.assert_called_with(mock_idx, mock_aov)

    def test_replace_group(self, init_file, mocker):
        mock_groups = mocker.patch.object(manager.AOVFile, "groups", new_callable=mocker.PropertyMock)

        mock_group = mocker.MagicMock(spec=manager.AOVGroup)

        mock_idx = mocker.MagicMock(spec=int)
        mock_groups.return_value.index.return_value = mock_idx

        aov_file = init_file()
        aov_file.replace_group(mock_group)

        mock_groups.return_value.index.assert_called_with(mock_group)
        mock_groups.return_value.__setitem__.assert_called_with(mock_idx, mock_group)

    # write_to_file

    def test_write_to_file__nothing_explicit_path(self, init_file, mocker):
        mock_groups = mocker.patch.object(manager.AOVFile, "groups", new_callable=mocker.PropertyMock)
        mock_aovs = mocker.patch.object(manager.AOVFile, "aovs", new_callable=mocker.PropertyMock)
        mock_dump = mocker.patch("ht.sohohooks.aovs.manager.json.dump")

        mock_groups.return_value = []
        mock_aovs.return_value = []

        aov_file = init_file()

        mock_path = mocker.MagicMock(spec=str)

        mock_handle = mocker.mock_open()

        mocker.patch("__builtin__.open", mock_handle)

        aov_file.write_to_file(mock_path)

        mock_handle.assert_called_with(mock_path, 'w')

        mock_dump.assert_called_with({}, mock_handle.return_value, indent=4)

    def test_write_to_file(self, init_file, mocker):
        mock_groups = mocker.patch.object(manager.AOVFile, "groups", new_callable=mocker.PropertyMock)
        mock_aovs = mocker.patch.object(manager.AOVFile, "aovs", new_callable=mocker.PropertyMock)
        mock_path = mocker.patch.object(manager.AOVFile, "path", new_callable=mocker.PropertyMock)
        mock_dump = mocker.patch("ht.sohohooks.aovs.manager.json.dump")

        mock_group_key = mocker.MagicMock(spec=str)
        mock_group_value = mocker.MagicMock(spec=str)

        mock_group = mocker.MagicMock(spec=manager.AOVGroup)
        mock_group.as_data.return_value = {mock_group_key: mock_group_value}

        mock_groups.return_value = [mock_group]

        mock_aov_key = mocker.MagicMock(spec=str)
        mock_aov_value = mocker.MagicMock(spec=str)

        mock_aov = mocker.MagicMock(spec=manager.AOV)
        mock_aov.as_data.return_value = {mock_aov_key: mock_aov_value}

        mock_aovs.return_value = [mock_aov]

        aov_file = init_file()

        expected = {
            consts.FILE_GROUPS_KEY: {mock_group_key: mock_group_value},
            consts.FILE_DEFINITIONS_KEY: [{mock_aov_key: mock_aov_value}]
        }

        mock_handle = mocker.mock_open()

        mocker.patch("__builtin__.open", mock_handle)

        aov_file.write_to_file()

        mock_handle.assert_called_with(mock_path.return_value, 'w')

        mock_dump.assert_called_with(expected, mock_handle.return_value, indent=4)


class Test__find_aov_files(object):
    """Test ht.sohohooks.aovs.manager._find_aov_files."""

    def test_aov_path(self, mocker):
        mock_glob = mocker.patch("ht.sohohooks.aovs.manager.glob.glob")
        mock_get_folders = mocker.patch("ht.sohohooks.aovs.manager._get_aov_path_folders")

        mock_folder_path = mocker.MagicMock(spec=str)
        mock_get_folders.return_value = (mock_folder_path, )

        mock_path1 = mocker.MagicMock(spec=str)
        mock_path2 = mocker.MagicMock(spec=str)

        mock_glob.return_value = [mock_path1, mock_path2]

        mocker.patch.dict(os.environ, {"HT_AOV_PATH": "value"})

        result = manager._find_aov_files()

        assert result == (mock_path1, mock_path2)

        mock_get_folders.assert_called()

        mock_glob.assert_called_with(os.path.join(mock_folder_path, "*.json"))

    def test_houdini_path(self, mocker):
        mock_find = mocker.patch("ht.sohohooks.aovs.manager._find_houdinipath_aov_folders")
        mock_glob = mocker.patch("ht.sohohooks.aovs.manager.glob.glob")

        mock_folder_path = mocker.MagicMock(spec=str)
        mock_find.return_value = [mock_folder_path]

        mock_path1 = mocker.MagicMock(spec=str)
        mock_path2 = mocker.MagicMock(spec=str)

        mock_glob.return_value = [mock_path1, mock_path2]

        mocker.patch.dict(os.environ, {}, clear=True)
        result = manager._find_aov_files()

        assert result == (mock_path1, mock_path2)

        mock_find.assert_called()

        mock_glob.assert_called_with(os.path.join(mock_folder_path, "*.json"))


class Test__find_houdinipath_aov_folders(object):
    """Test ht.sohohooks.aovs.manager._find_houdinipath_aov_folders."""

    def test_no_dirs(self, mocker, mock_hou_exceptions):
        mock_find = mocker.patch("ht.sohohooks.aovs.manager.hou.findDirectories")
        mock_find.side_effect = mock_hou_exceptions.OperationFailed

        result = manager._find_houdinipath_aov_folders()

        assert result == ()

    def test_dirs(self, mocker):
        mock_find = mocker.patch("ht.sohohooks.aovs.manager.hou.findDirectories")

        result = manager._find_houdinipath_aov_folders()

        assert result == mock_find.return_value


class Test__get_aov_path_folders(object):
    """Test ht.sohohooks.aovs.manager._get_aov_path_folders."""

    def test_no_hpath(self, mocker):

        env_dict = {
            "HT_AOV_PATH": "path1:path2"
        }

        mocker.patch.dict(os.environ, env_dict)

        result = manager._get_aov_path_folders()

        assert result == ("path1", "path2")

    def test_hpath_no_folders(self, mocker):
        mock_find = mocker.patch("ht.sohohooks.aovs.manager._find_houdinipath_aov_folders")

        mock_find.return_value = ()

        env_dict = {
            "HT_AOV_PATH": "path1:path2:&"
        }

        mocker.patch.dict(os.environ, env_dict)

        result = manager._get_aov_path_folders()

        assert result == ("path1", "path2", "&")

    def test_hpath_folders(self, mocker):
        mock_find = mocker.patch("ht.sohohooks.aovs.manager._find_houdinipath_aov_folders")

        mock_find.return_value = ("hpath1", "hpath2")

        env_dict = {
            "HT_AOV_PATH": "path1:path2:&"
        }

        mocker.patch.dict(os.environ, env_dict)

        result = manager._get_aov_path_folders()

        assert result == ("path1", "path2", "hpath1", "hpath2")


class Test_build_menu_script(object):
    """Test ht.sohohooks.aovs.manager.build_menu_script."""

    def test_no_groups(self, mocker):
        mock_manager = mocker.patch("ht.sohohooks.aovs.manager.MANAGER", autospec=True)

        mock_manager.groups = None

        mock_aov1 = mocker.MagicMock(spec=manager.AOV)
        mock_aov2 = mocker.MagicMock(spec=manager.AOV)
        mock_aov3 = mocker.MagicMock(spec=manager.AOV)

        mock_manager.aovs = {"P": mock_aov1, "N": mock_aov2, "A": mock_aov3}

        result = manager.build_menu_script()

        assert result == ("A", "A", "N", "N", "P", "P")

    def test_with_groups(self, mocker):
        mock_manager = mocker.patch("ht.sohohooks.aovs.manager.MANAGER", autospec=True)

        mock_group1 = mocker.MagicMock(spec=manager.AOVGroup)
        mock_group2 = mocker.MagicMock(spec=manager.AOVGroup)
        mock_group3 = mocker.MagicMock(spec=manager.AOVGroup)

        mock_manager.groups = {
            "group1": mock_group1,
            "group2": mock_group2,
            "group3": mock_group3,
        }

        mock_aov1 = mocker.MagicMock(spec=manager.AOV)
        mock_aov2 = mocker.MagicMock(spec=manager.AOV)
        mock_aov3 = mocker.MagicMock(spec=manager.AOV)

        mock_manager.aovs = {"P": mock_aov1, "N": mock_aov2, "A": mock_aov3}

        result = manager.build_menu_script()

        expected = ("@group1", "group1", "@group2", "group2", "@group3", "group3", "_separator_", "", "A", "A", "N", "N", "P", "P")

        assert result == expected


def test_flatten_aov_items(mocker):
    """Test ht.sohohooks.aovs.manager.flatten_aov_items."""
    mock_aov = mocker.MagicMock(spec=manager.AOV)

    mock_group_aov = mocker.MagicMock(spec=manager.AOV)

    mock_group = mocker.MagicMock(spec=manager.AOVGroup)
    type(mock_group).aovs = mocker.PropertyMock(return_value=[mock_group_aov])

    result = manager.flatten_aov_items((mock_aov, mock_group))

    assert result == (mock_aov, mock_group_aov)


def test_load_json_files(mocker, mock_hou_ui):
    """Test ht.sohohooks.aovs.manager.load_json_files."""
    mock_expand = mocker.patch("ht.sohohooks.aovs.manager.os.path.expandvars")
    mock_exists = mocker.patch("ht.sohohooks.aovs.manager.os.path.exists")
    mock_manager = mocker.patch("ht.sohohooks.aovs.manager.MANAGER", autospec=True)

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
