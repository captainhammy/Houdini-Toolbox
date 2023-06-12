"""Test the houdini_toolbox.sohohooks.aovs.manager module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import os

# Third Party
import pytest

# Houdini Toolbox
from houdini_toolbox.sohohooks.aovs import aov
from houdini_toolbox.sohohooks.aovs import constants as consts
from houdini_toolbox.sohohooks.aovs import manager

# Houdini
import hou

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def init_file(mocker):
    """Fixture to initialize a file."""
    mocker.patch.object(manager.AOVFile, "__init__", lambda x, y: None)

    def _create():
        return manager.AOVFile(None)

    return _create


@pytest.fixture
def init_manager(mocker):
    """Fixture to initialize a manager."""
    mocker.patch.object(manager.AOVManager, "__init__", lambda x: None)

    def _create():
        return manager.AOVManager()

    return _create


# =============================================================================
# TESTS
# =============================================================================


class Test_AOVManager:
    """Test houdini_toolbox.sohohooks.aovs.manager.AOVManager object."""

    def test___init__(self, mocker):
        """Test object initialization."""
        mock_init = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.manager.AOVManager._init_from_files"
        )

        mgr = manager.AOVManager()

        assert mgr._aovs == {}
        assert mgr._groups == {}
        assert mgr._interface is None
        mock_init.assert_called()

    @pytest.mark.parametrize("existing", (False, True))
    def test__build_intrinsic_groups(self, init_manager, mocker, existing):
        """Test building intrinsic groups."""
        mock_aovs = mocker.patch.object(
            manager.AOVManager, "aovs", new_callable=mocker.PropertyMock
        )
        mock_groups = mocker.patch.object(
            manager.AOVManager, "groups", new_callable=mocker.PropertyMock
        )
        mock_add = mocker.patch.object(manager.AOVManager, "add_group")

        mock_aov = mocker.MagicMock(spec=manager.AOV)
        mock_aov.intrinsics = ["int1"]

        mock_aovs.return_value = {mocker.MagicMock(spec=str): mock_aov}

        mock_group = mocker.MagicMock(spec=aov.IntrinsicAOVGroup)

        # An intrinsic group already exists.
        if existing:
            mock_groups.return_value = {"i:int1": mock_group}

        else:
            mock_groups.return_value = {}

        mock_int_group = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.manager.IntrinsicAOVGroup", autospec=True
        )

        mgr = init_manager()
        mgr._build_intrinsic_groups()

        if existing:
            mock_group.aovs.append.assert_called_with(mock_aov)
            mock_add.assert_not_called()

        else:
            mock_int_group.assert_called_with("i:int1")
            mock_add.assert_called_with(mock_int_group.return_value)

            mock_int_group.return_value.aovs.append.assert_called_with(mock_aov)

    def test__init_from_files(self, init_manager, mocker):
        """Test initializing data from files."""
        mock_find = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.manager._find_aov_files"
        )
        mock_file = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.manager.AOVFile", autospec=True
        )
        mock_merge = mocker.patch.object(manager.AOVManager, "_merge_readers")
        mock_build = mocker.patch.object(manager.AOVManager, "_build_intrinsic_groups")

        mock_path = mocker.MagicMock(spec=str)
        mock_find.return_value = [mock_path]

        mgr = init_manager()
        mgr._init_from_files()

        mock_file.assert_called_with(mock_path)
        mock_merge.assert_called_with([mock_file.return_value])
        mock_build.assert_called()

    def test__init_group_members(self, init_manager, mocker):
        """Test initializing group members."""
        mock_aovs = mocker.patch.object(
            manager.AOVManager, "aovs", new_callable=mocker.PropertyMock
        )

        mock_varname1 = mocker.MagicMock(spec=str)
        mock_varname2 = mocker.MagicMock(spec=str)

        mock_group = mocker.MagicMock(spec=manager.AOVGroup)
        mock_group.includes = [mock_varname1, mock_varname2]

        mock_aov = mocker.MagicMock(spec=manager.AOV)

        mock_aovs.return_value = {mock_varname1: mock_aov}

        mgr = init_manager()
        mgr._init_group_members(mock_group)

        mock_group.aovs.append.assert_called_with(mock_aov)

    # _init_reader_aovs

    def test__init_reader_aovs__new_aov(self, init_manager, mocker):
        """Test initializing a new aov."""
        mock_aovs = mocker.patch.object(
            manager.AOVManager, "aovs", new_callable=mocker.PropertyMock
        )
        mock_add = mocker.patch.object(manager.AOVManager, "add_aov")

        mock_aov = mocker.MagicMock(spec=manager.AOV)

        mock_reader = mocker.MagicMock(spec=manager.AOVFile)
        mock_reader.aovs = [mock_aov]

        mock_aovs.return_value = {}

        mgr = init_manager()
        mgr._init_reader_aovs(mock_reader)

        mock_add.assert_called_with(mock_aov)

    def test__init_reader_aovs__matches_existing_priority_same(
        self, init_manager, mocker
    ):
        """Test initializing a new aov when the name matches an existing one of the same priority."""
        mock_aovs = mocker.patch.object(
            manager.AOVManager, "aovs", new_callable=mocker.PropertyMock
        )
        mock_add = mocker.patch.object(manager.AOVManager, "add_aov")

        mock_varname = mocker.MagicMock(spec=str)
        mock_priority = 3

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

    def test__init_reader_aovs__matches_existing_priority_lower(
        self, init_manager, mocker
    ):
        """Test initializing a new aov when the name matches an existing one a lower priority."""
        mock_aovs = mocker.patch.object(
            manager.AOVManager, "aovs", new_callable=mocker.PropertyMock
        )
        mock_add = mocker.patch.object(manager.AOVManager, "add_aov")

        mock_varname = mocker.MagicMock(spec=str)

        mock_new_aov = mocker.MagicMock(spec=manager.AOV)
        mock_new_aov.variable = mock_varname
        mock_new_aov.priority = 3

        mock_existing_aov = mocker.MagicMock(spec=manager.AOV)
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
        """Test initializing a new group."""
        mock_init = mocker.patch.object(manager.AOVManager, "_init_group_members")
        mock_groups = mocker.patch.object(
            manager.AOVManager, "groups", new_callable=mocker.PropertyMock
        )
        mock_add = mocker.patch.object(manager.AOVManager, "add_group")

        mock_group = mocker.MagicMock(spec=manager.AOVGroup)

        mock_reader = mocker.MagicMock(spec=manager.AOVFile)
        mock_reader.groups = [mock_group]

        mock_groups.return_value = {}

        mgr = init_manager()
        mgr._init_reader_groups(mock_reader)

        mock_init.assert_called_with(mock_group)

        mock_add.assert_called_with(mock_group)

    def test__init_reader_groups__matches_existing_priority_same(
        self, init_manager, mocker
    ):
        """Test initializing a new group when the name matches an existing one a lower priority."""
        mock_init = mocker.patch.object(manager.AOVManager, "_init_group_members")
        mock_groups = mocker.patch.object(
            manager.AOVManager, "groups", new_callable=mocker.PropertyMock
        )
        mock_add = mocker.patch.object(manager.AOVManager, "add_group")

        mock_group_name = mocker.MagicMock(spec=str)
        mock_priority = 3

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

    def test__init_reader_groups__matches_existing_priority_lower(
        self, init_manager, mocker
    ):
        """Test initializing a new group when the name matches an existing one a lower priority."""
        mock_init = mocker.patch.object(manager.AOVManager, "_init_group_members")
        mock_groups = mocker.patch.object(
            manager.AOVManager, "groups", new_callable=mocker.PropertyMock
        )
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
        """Test merging readers."""
        mock_init_aovs = mocker.patch.object(manager.AOVManager, "_init_reader_aovs")
        mock_init_groups = mocker.patch.object(
            manager.AOVManager, "_init_reader_groups"
        )

        mock_reader = mocker.MagicMock(spec=manager.AOVFile)

        readers = [mock_reader]

        mgr = init_manager()
        mgr._merge_readers(readers)

        mock_init_aovs.assert_called_with(mock_reader)
        mock_init_groups.assert_called_with(mock_reader)

    # Properties

    def test_aovs(self, init_manager, mocker):
        """Test the 'aovs' property."""
        mock_value = mocker.MagicMock(spec=list)

        mgr = init_manager()
        mgr._aovs = mock_value
        assert mgr.aovs == mock_value

    def test_groups(self, init_manager, mocker):
        """Test the 'groups' property."""
        mock_value = mocker.MagicMock(spec=list)

        mgr = init_manager()
        mgr._groups = mock_value
        assert mgr.groups == mock_value

    def test_interface(self, init_manager, mocker):
        """Test the 'interface' property."""
        mock_value = mocker.MagicMock()

        mgr = init_manager()
        mgr._interface = mock_value
        assert mgr.interface == mock_value

    @pytest.mark.parametrize("has_interface", (False, True))
    def test_add_aov__interface(self, init_manager, mocker, has_interface):
        """Test adding an aov."""
        mock_aovs = mocker.patch.object(
            manager.AOVManager, "aovs", new_callable=mocker.PropertyMock
        )

        mock_interface = mocker.patch.object(
            manager.AOVManager, "interface", new_callable=mocker.PropertyMock
        )

        if has_interface:
            interface = mocker.MagicMock()
            mock_interface.return_value = interface

        else:
            mock_interface.return_value = None
            interface = None

        aovs = {}
        mock_aovs.return_value = aovs

        mock_aov = mocker.MagicMock(spec=manager.AOV)

        mgr = init_manager()
        mgr.add_aov(mock_aov)

        assert aovs == {mock_aov.variable: mock_aov}

        if has_interface:
            interface.aov_added_signal.emit.assert_called_with(mock_aov)

    # add_aovs_to_ifd

    def test_add_aovs_to_ifd__no_parms(self, init_manager, mocker, patch_soho):
        """Test adding aovs to the ifd when the parameters don't exist."""
        mock_wrangler = mocker.MagicMock()

        mock_cam = mocker.MagicMock()
        mock_cam.wrangle.return_value = {}

        mock_now = mocker.MagicMock(spec=float)

        mgr = init_manager()

        calls = [
            mocker.call("enable_auto_aovs", "int", [1], skipdefault=False),
            mocker.call("auto_aovs", "str", [""], skipdefault=False),
        ]

        mgr.add_aovs_to_ifd(mock_wrangler, mock_cam, mock_now)

        patch_soho.soho.SohoParm.assert_has_calls(calls)

    def test_add_aovs_to_ifd__disabled(self, init_manager, mocker, patch_soho):
        """Test adding aovs to the ifd when disabled."""
        mocker.patch.object(manager.AOVManager, "get_aovs_from_string")

        mock_wrangler = mocker.MagicMock()

        mock_enable_result = mocker.MagicMock()
        mock_enable_result.Value = [0]

        mock_cam = mocker.MagicMock()
        mock_cam.wrangle.return_value = {"enable_auto_aovs": mock_enable_result}

        mock_now = mocker.MagicMock(spec=float)

        mgr = init_manager()

        calls = [
            mocker.call("enable_auto_aovs", "int", [1], skipdefault=False),
            mocker.call("auto_aovs", "str", [""], skipdefault=False),
        ]

        mgr.add_aovs_to_ifd(mock_wrangler, mock_cam, mock_now)

        patch_soho.soho.SohoParm.assert_has_calls(calls)

    def test_add_aovs_to_ifd__non_opid(self, init_manager, mocker, patch_soho):
        """Test adding aovs to the ifd when the variable isn't Op_Id."""
        mock_get = mocker.patch.object(manager.AOVManager, "get_aovs_from_string")
        mock_flattened = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.manager.flatten_aov_items"
        )

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

        mock_flattened.return_value = (mock_aov,)

        mgr = init_manager()

        calls = [
            mocker.call("enable_auto_aovs", "int", [1], skipdefault=False),
            mocker.call("auto_aovs", "str", [""], skipdefault=False),
        ]

        mgr.add_aovs_to_ifd(mock_wrangler, mock_cam, mock_now)

        patch_soho.soho.SohoParm.assert_has_calls(calls)

        mock_get.assert_called_with(mock_aovs_result.Value[0])

        mock_aov.write_to_ifd.assert_called_with(mock_wrangler, mock_cam, mock_now)

        patch_soho.IFDapi.ray_comment.assert_not_called()

    def test_add_aovs_to_ifd__opid(self, init_manager, mocker, patch_soho):
        """Test adding aovs to the ifd when the variable is Op_Id."""
        mock_get = mocker.patch.object(manager.AOVManager, "get_aovs_from_string")
        mock_flattened = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.manager.flatten_aov_items"
        )

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

        mock_flattened.return_value = (mock_aov,)

        mgr = init_manager()

        calls = [
            mocker.call("enable_auto_aovs", "int", [1], skipdefault=False),
            mocker.call("auto_aovs", "str", [""], skipdefault=False),
        ]

        mgr.add_aovs_to_ifd(mock_wrangler, mock_cam, mock_now)

        patch_soho.soho.SohoParm.assert_has_calls(calls)

        mock_get.assert_called_with(mock_aovs_result.Value[0])

        mock_aov.write_to_ifd.assert_called_with(mock_wrangler, mock_cam, mock_now)
        patch_soho.IFDapi.ray_comment.assert_called()
        assert patch_soho.IFDsettings._GenerateOpId

    @pytest.mark.parametrize("has_interface", (False, True))
    def test_add_group(self, init_manager, mocker, has_interface):
        """Test adding a group."""
        mock_groups = mocker.patch.object(
            manager.AOVManager, "groups", new_callable=mocker.PropertyMock
        )
        mock_interface = mocker.patch.object(
            manager.AOVManager, "interface", new_callable=mocker.PropertyMock
        )

        if has_interface:
            interface = mocker.MagicMock()
            mock_interface.return_value = interface

        else:
            interface = None
            mock_interface.return_value = None

        groups = {}
        mock_groups.return_value = groups

        mock_group = mocker.MagicMock(spec=manager.AOVGroup)

        mgr = init_manager()
        mgr.add_group(mock_group)

        assert groups == {mock_group.name: mock_group}

        if has_interface:
            interface.group_added_signal.emit.assert_called_with(mock_group)

    def test_attach_interface(self, init_manager, mocker):
        """Test attaching a viewer interface."""
        mock_interface = mocker.MagicMock()

        mgr = init_manager()
        mgr.attach_interface(mock_interface)

        assert mgr._interface == mock_interface

    def test_clear(self, init_manager, mocker):
        """Test clearing data."""
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
        """Test getting aovs with no matches."""
        mock_aovs = mocker.patch.object(
            manager.AOVManager, "aovs", new_callable=mocker.PropertyMock
        )
        mock_groups = mocker.patch.object(
            manager.AOVManager, "groups", new_callable=mocker.PropertyMock
        )

        mock_aovs.return_value = {}
        mock_groups.return_value = {}

        mgr = init_manager()

        pattern = ""

        result = mgr.get_aovs_from_string(pattern)

        assert result == ()

    def test_get_aovs_from_string__aovs_match_spaces(self, init_manager, mocker):
        """Test getting aovs separated by spaces."""
        mock_aovs = mocker.patch.object(
            manager.AOVManager, "aovs", new_callable=mocker.PropertyMock
        )
        mock_groups = mocker.patch.object(
            manager.AOVManager, "groups", new_callable=mocker.PropertyMock
        )

        mock_aov_n = mocker.MagicMock(spec=manager.AOV)
        mock_aov_p = mocker.MagicMock(spec=manager.AOV)

        mock_aovs.return_value = {"N": mock_aov_n, "P": mock_aov_p}
        mock_groups.return_value = {}

        mgr = init_manager()

        pattern = "N P R"

        result = mgr.get_aovs_from_string(pattern)

        assert result == (mock_aov_n, mock_aov_p)

    def test_get_aovs_from_string__aovs_match_commas(self, init_manager, mocker):
        """Test getting aovs separated by commas."""
        mock_aovs = mocker.patch.object(
            manager.AOVManager, "aovs", new_callable=mocker.PropertyMock
        )
        mock_groups = mocker.patch.object(
            manager.AOVManager, "groups", new_callable=mocker.PropertyMock
        )

        mock_aov_n = mocker.MagicMock(spec=manager.AOV)
        mock_aov_p = mocker.MagicMock(spec=manager.AOV)

        mock_aovs.return_value = {"N": mock_aov_n, "P": mock_aov_p}
        mock_groups.return_value = {}

        mgr = init_manager()

        pattern = "N,P,R"

        result = mgr.get_aovs_from_string(pattern)

        assert result == (mock_aov_n, mock_aov_p)

    def test_get_aovs_from_string__groups_match_spaces(self, init_manager, mocker):
        """Test getting groups separated by spaces."""
        mock_aovs = mocker.patch.object(
            manager.AOVManager, "aovs", new_callable=mocker.PropertyMock
        )
        mock_groups = mocker.patch.object(
            manager.AOVManager, "groups", new_callable=mocker.PropertyMock
        )

        mock_group1 = mocker.MagicMock(spec=manager.AOVGroup)
        mock_group2 = mocker.MagicMock(spec=manager.AOVGroup)

        mock_aovs.return_value = {}
        mock_groups.return_value = {"group1": mock_group1, "group2": mock_group2}

        mgr = init_manager()

        pattern = "@group1 @group3 @group2"

        result = mgr.get_aovs_from_string(pattern)

        assert result == (mock_group1, mock_group2)

    def test_get_aovs_from_string__groups_match_commas(self, init_manager, mocker):
        """Test getting groups separated by commas."""
        mock_aovs = mocker.patch.object(
            manager.AOVManager, "aovs", new_callable=mocker.PropertyMock
        )
        mock_groups = mocker.patch.object(
            manager.AOVManager, "groups", new_callable=mocker.PropertyMock
        )

        mock_group1 = mocker.MagicMock(spec=manager.AOVGroup)
        mock_group2 = mocker.MagicMock(spec=manager.AOVGroup)

        mock_aovs.return_value = {}
        mock_groups.return_value = {"group1": mock_group1, "group2": mock_group2}

        mgr = init_manager()

        pattern = "@group1,@group3, @group2"

        result = mgr.get_aovs_from_string(pattern)

        assert result == (mock_group1, mock_group2)

    def test_load(self, init_manager, mocker):
        """Test loading a file path."""
        mock_file = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.manager.AOVFile", autospec=True
        )
        mock_merge = mocker.patch.object(manager.AOVManager, "_merge_readers")

        mgr = init_manager()

        mock_path = mocker.MagicMock(spec=str)

        mgr.load(mock_path)

        mock_file.assert_called_with(mock_path)

        mock_merge.assert_called_with([mock_file.return_value])

    def test_reload(self, init_manager, mocker):
        """Test reloading all data."""
        mock_clear = mocker.patch.object(manager.AOVManager, "clear")
        mock_init = mocker.patch.object(manager.AOVManager, "_init_from_files")

        mgr = init_manager()

        mgr.reload()

        mock_clear.assert_called()
        mock_init.assert_called()

    @pytest.mark.parametrize(
        "has_match, has_interface",
        [
            (False, False),
            (True, False),
            (True, True),
        ],
    )
    def test_remove_aov(self, init_manager, mocker, has_match, has_interface):
        """Test removing an aov."""
        mock_aovs = mocker.patch.object(
            manager.AOVManager, "aovs", new_callable=mocker.PropertyMock
        )
        mock_interface = mocker.patch.object(
            manager.AOVManager, "interface", new_callable=mocker.PropertyMock
        )

        if has_interface:
            interface = mocker.MagicMock()
            mock_interface.return_value = interface

        else:
            mock_interface.return_value = None
            interface = None

        mock_aov1 = mocker.MagicMock(spec=manager.AOV)
        mock_aov2 = mocker.MagicMock(spec=manager.AOV)

        if has_match:
            aovs = {mock_aov1.variable: mock_aov1}

        else:
            aovs = {mock_aov2.variable: mock_aov2}

        mock_aovs.return_value = aovs

        mgr = init_manager()

        mgr.remove_aov(mock_aov1)

        if has_match:
            assert aovs == {}

            if has_interface:
                interface.aov_removed_signal.emit.assert_called_with(mock_aov1)

        else:
            assert aovs == {mock_aov2.variable: mock_aov2}

    @pytest.mark.parametrize(
        "has_match, has_interface",
        [
            (False, False),
            (True, False),
            (True, True),
        ],
    )
    def test_remove_group(self, init_manager, mocker, has_match, has_interface):
        """Test removing a group."""
        mock_groups = mocker.patch.object(
            manager.AOVManager, "groups", new_callable=mocker.PropertyMock
        )
        mock_interface = mocker.patch.object(
            manager.AOVManager, "interface", new_callable=mocker.PropertyMock
        )

        if has_interface:
            interface = mocker.MagicMock()
            mock_interface.return_value = interface

        else:
            mock_interface.return_value = None
            interface = None

        mock_group1 = mocker.MagicMock(spec=manager.AOVGroup)
        mock_group2 = mocker.MagicMock(spec=manager.AOVGroup)

        if has_match:
            groups = {mock_group1.name: mock_group1}

        else:
            groups = {mock_group2.name: mock_group2}

        mock_groups.return_value = groups

        mgr = init_manager()

        mgr.remove_group(mock_group1)

        if has_match:
            assert groups == {}

            if has_interface:
                interface.group_removed_signal.emit.assert_called_with(mock_group1)

        else:
            assert groups == {mock_group2.name: mock_group2}


class Test_AOVFile:
    """Test houdini_toolbox.sohohooks.aovs.manager.AOVFile object."""

    @pytest.mark.parametrize("exists", (True, False))
    def test___init__(self, mocker, exists):
        """Test object initialization."""
        mocker.patch.object(
            manager.AOVFile,
            "exists",
            new_callable=mocker.PropertyMock(return_value=exists),
        )
        mock_init = mocker.patch.object(manager.AOVFile, "_init_from_file")

        mock_path = mocker.MagicMock(spec=str)

        aov_file = manager.AOVFile(mock_path)

        assert aov_file._path == mock_path
        assert aov_file._aovs == []
        assert aov_file._data == {}
        assert aov_file._groups == []

        if exists:
            mock_init.assert_called()

        else:
            mock_init.assert_not_called()

    # Non-Public Methods

    def test__create_aovs(self, init_file, mocker):
        """Test creating aovs from definitions."""
        mock_path = mocker.patch.object(
            manager.AOVFile, "path", new_callable=mocker.PropertyMock
        )
        mock_aov = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.manager.AOV", autospec=True
        )
        mock_aovs = mocker.patch.object(
            manager.AOVFile, "aovs", new_callable=mocker.PropertyMock
        )

        mock_key = mocker.MagicMock(spec=str)
        mock_value = mocker.MagicMock(spec=str)

        definition = {mock_key: mock_value}
        definitions = [definition]

        aovs = []
        mock_aovs.return_value = aovs

        aov_file = init_file()

        aov_file._create_aovs(definitions)

        mock_aov.assert_called_with(
            {mock_key: mock_value, "path": mock_path.return_value}
        )

        # Test that the path got added to the definition.
        assert definition == {mock_key: mock_value, "path": mock_path.return_value}

        assert aovs == [mock_aov.return_value]

    @pytest.mark.parametrize("all_data", (False, True))
    def test__create_groups(self, init_file, mocker, all_data):
        """Test creating groups."""
        mock_group = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.manager.AOVGroup", autospec=True
        )
        mock_expand = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.manager.os.path.expandvars"
        )
        mock_path = mocker.patch.object(
            manager.AOVFile, "path", new_callable=mocker.PropertyMock
        )
        mock_groups = mocker.patch.object(
            manager.AOVFile, "groups", new_callable=mocker.PropertyMock
        )

        mock_group_name = mocker.MagicMock(spec=str)
        mock_includes = mocker.MagicMock(spec=list)
        mock_comment = mocker.MagicMock(spec=str)
        mock_priority = mocker.MagicMock(spec=int)
        mock_icon = mocker.MagicMock(spec=str)

        # Provide all the optional data.
        if all_data:
            group_data = {
                consts.GROUP_INCLUDE_KEY: mock_includes,
                consts.COMMENT_KEY: mock_comment,
                consts.PRIORITY_KEY: mock_priority,
                consts.GROUP_ICON_KEY: mock_icon,
            }

        else:
            group_data = {}

        definitions = {mock_group_name: group_data}

        groups = []
        mock_groups.return_value = groups

        aov_file = init_file()

        aov_file._create_groups(definitions)

        mock_group.assert_called_with(mock_group_name)

        assert groups == [mock_group.return_value]

        assert mock_group.return_value.path == mock_path.return_value

        if all_data:
            mock_expand.assert_called_with(mock_icon)

            assert mock_group.return_value.comment == mock_comment
            assert mock_group.return_value.priority == mock_priority
            assert mock_group.return_value.icon == mock_expand.return_value

            mock_group.return_value.includes.extend.assert_called_with(mock_includes)

    @pytest.mark.parametrize("has_data", (False, True))
    def test__init_from_file(self, init_file, mocker, has_data):
        """Test loading data from the file."""
        mock_path = mocker.patch.object(
            manager.AOVFile, "path", new_callable=mocker.PropertyMock
        )
        mock_load = mocker.patch("houdini_toolbox.sohohooks.aovs.manager.json.load")
        mock_create_aovs = mocker.patch.object(manager.AOVFile, "_create_aovs")
        mock_create_groups = mocker.patch.object(manager.AOVFile, "_create_groups")

        mock_definitions = mocker.MagicMock(spec=dict)
        mock_groups = mocker.MagicMock(spec=dict)

        if has_data:
            mock_load.return_value = {
                consts.FILE_DEFINITIONS_KEY: mock_definitions,
                consts.FILE_GROUPS_KEY: mock_groups,
            }

        else:
            mock_load.return_value = {}

        aov_file = init_file()

        mock_handle = mocker.mock_open()

        mocker.patch("builtins.open", mock_handle)

        aov_file._init_from_file()

        mock_handle.assert_called_with(mock_path.return_value, encoding="utf-8")

        mock_load.assert_called_with(mock_handle.return_value)

        if has_data:
            mock_create_aovs.assert_called_with(mock_definitions)
            mock_create_groups.assert_called_with(mock_groups)

        else:
            mock_create_aovs.assert_not_called()
            mock_create_groups.assert_not_called()

    # Properties

    def test_aovs(self, init_file, mocker):
        """Test the 'aovs' property."""
        mock_aov = mocker.MagicMock(spec=manager.AOV)

        aov_file = init_file()
        aov_file._aovs = [mock_aov]
        assert aov_file.aovs == [mock_aov]

    def test_groups(self, init_file, mocker):
        """Test the 'groups' property."""
        mock_group = mocker.MagicMock(spec=manager.AOVGroup)

        aov_file = init_file()
        aov_file._groups = [mock_group]
        assert aov_file.groups == [mock_group]

    def test_path(self, init_file, mocker):
        """Test the 'path' property."""
        mock_value = mocker.MagicMock(spec=str)

        aov_file = init_file()
        aov_file._path = mock_value
        assert aov_file.path == mock_value

    def test_exists(self, init_file, mocker):
        """Test the 'exists' property."""
        mock_isfile = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.manager.os.path.isfile"
        )
        mock_path = mocker.patch.object(
            manager.AOVFile, "path", new_callable=mocker.PropertyMock
        )

        aov_file = init_file()

        assert aov_file.exists == mock_isfile.return_value

        mock_isfile.assert_called_with(mock_path.return_value)

    # Methods

    def test_add_aov(self, init_file, mocker):
        """Test adding an aov."""
        mock_aovs = mocker.patch.object(
            manager.AOVFile, "aovs", new_callable=mocker.PropertyMock
        )

        mock_aov = mocker.MagicMock(spec=manager.AOV)

        aov_file = init_file()
        aov_file.add_aov(mock_aov)

        mock_aovs.return_value.append.assert_called_with(mock_aov)

    def test_add_group(self, init_file, mocker):
        """Test adding a group."""
        mock_groups = mocker.patch.object(
            manager.AOVFile, "groups", new_callable=mocker.PropertyMock
        )

        mock_group = mocker.MagicMock(spec=manager.AOVGroup)

        aov_file = init_file()
        aov_file.add_group(mock_group)

        mock_groups.return_value.append.assert_called_with(mock_group)

    def test_contains_aov(self, init_file, mocker):
        """Test if the manager contains an aov."""
        mock_aovs = mocker.patch.object(
            manager.AOVFile, "aovs", new_callable=mocker.PropertyMock
        )

        mock_aov = mocker.MagicMock(spec=manager.AOV)

        aov_file = init_file()
        result = aov_file.contains_aov(mock_aov)

        assert result == mock_aovs.return_value.__contains__.return_value

        mock_aovs.return_value.__contains__.assert_called_with(mock_aov)

    def test_contains_group(self, init_file, mocker):
        """Test if the manager contains a group."""
        mock_groups = mocker.patch.object(
            manager.AOVFile, "groups", new_callable=mocker.PropertyMock
        )

        mock_group = mocker.MagicMock(spec=manager.AOVGroup)

        aov_file = init_file()
        result = aov_file.contains_group(mock_group)

        assert result == mock_groups.return_value.__contains__.return_value

        mock_groups.return_value.__contains__.assert_called_with(mock_group)

    def test_remove_aov(self, init_file, mocker):
        """Test removing an aov."""
        mock_aovs = mocker.patch.object(
            manager.AOVFile, "aovs", new_callable=mocker.PropertyMock
        )

        mock_aov = mocker.MagicMock(spec=manager.AOV)

        aovs = [mock_aov]
        mock_aovs.return_value = aovs

        aov_file = init_file()
        aov_file.remove_aov(mock_aov)

        assert aovs == []

    def test_remove_group(self, init_file, mocker):
        """Test removing a group."""
        mock_groups = mocker.patch.object(
            manager.AOVFile, "groups", new_callable=mocker.PropertyMock
        )

        mock_group = mocker.MagicMock(spec=manager.AOVGroup)

        groups = [mock_group]
        mock_groups.return_value = groups

        aov_file = init_file()
        aov_file.remove_group(mock_group)

        assert groups == []

    def test_replace_aov(self, init_file, mocker):
        """Test replacing an aov."""
        mock_aovs = mocker.patch.object(
            manager.AOVFile, "aovs", new_callable=mocker.PropertyMock
        )

        mock_aov = mocker.MagicMock(spec=manager.AOV)

        mock_idx = mocker.MagicMock(spec=int)
        mock_aovs.return_value.index.return_value = mock_idx

        aov_file = init_file()
        aov_file.replace_aov(mock_aov)

        mock_aovs.return_value.index.assert_called_with(mock_aov)
        mock_aovs.return_value.__setitem__.assert_called_with(mock_idx, mock_aov)

    def test_replace_group(self, init_file, mocker):
        """Test replacing a group."""
        mock_groups = mocker.patch.object(
            manager.AOVFile, "groups", new_callable=mocker.PropertyMock
        )

        mock_group = mocker.MagicMock(spec=manager.AOVGroup)

        mock_idx = mocker.MagicMock(spec=int)
        mock_groups.return_value.index.return_value = mock_idx

        aov_file = init_file()
        aov_file.replace_group(mock_group)

        mock_groups.return_value.index.assert_called_with(mock_group)
        mock_groups.return_value.__setitem__.assert_called_with(mock_idx, mock_group)

    # write_to_file

    @pytest.mark.parametrize("external_path", (False, True))
    def test_write_to_file(self, init_file, mocker, external_path):
        """Test writing data to a file."""
        mock_groups = mocker.patch.object(
            manager.AOVFile, "groups", new_callable=mocker.PropertyMock
        )
        mock_aovs = mocker.patch.object(
            manager.AOVFile, "aovs", new_callable=mocker.PropertyMock
        )
        mock_path_prop = mocker.patch.object(
            manager.AOVFile, "path", new_callable=mocker.PropertyMock
        )

        path = None

        if external_path:
            path = mocker.MagicMock(spec=str)

        mock_dump = mocker.patch("houdini_toolbox.sohohooks.aovs.manager.json.dump")

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
            consts.FILE_DEFINITIONS_KEY: [{mock_aov_key: mock_aov_value}],
        }

        mock_handle = mocker.mock_open()

        mocker.patch("builtins.open", mock_handle)

        aov_file.write_to_file(path)

        if external_path:
            mock_handle.assert_called_with(path, "w", encoding="utf-8")

        else:
            mock_handle.assert_called_with(
                mock_path_prop.return_value, "w", encoding="utf-8"
            )

        mock_dump.assert_called_with(expected, mock_handle.return_value, indent=4)


class Test__find_aov_files:
    """Test houdini_toolbox.sohohooks.aovs.manager._find_aov_files."""

    def test_aov_path(self, mocker):
        """Test finding aov files with HT_AOV_PATH."""
        mock_glob = mocker.patch("glob.glob")
        mock_get_folders = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.manager._get_aov_path_folders"
        )

        folder_path = "/path/to/folder"
        mock_get_folders.return_value = (folder_path,)

        mock_path1 = mocker.MagicMock(spec=str)
        mock_path2 = mocker.MagicMock(spec=str)

        mock_glob.return_value = [mock_path1, mock_path2]

        mocker.patch.dict(os.environ, {"HT_AOV_PATH": "value"})

        result = manager._find_aov_files()

        assert result == (str(mock_path1), str(mock_path2))

        mock_get_folders.assert_called()

        mock_glob.assert_called_with(os.path.join(folder_path, "*.json"))

    def test_houdini_path(self, mocker):
        """Test finding aov files with HOUDINI_PATH."""
        mock_find = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.manager._find_houdinipath_aov_folders"
        )
        mock_glob = mocker.patch("glob.glob")

        folder_path = "/path/to/folder"
        mock_find.return_value = [folder_path]

        mock_path1 = mocker.MagicMock(spec=str)
        mock_path2 = mocker.MagicMock(spec=str)

        mock_glob.return_value = [mock_path1, mock_path2]

        mocker.patch.dict(os.environ, {}, clear=True)
        result = manager._find_aov_files()

        assert result == (str(mock_path1), str(mock_path2))

        mock_find.assert_called()

        mock_glob.assert_called_with(os.path.join(folder_path, "*.json"))


class Test__find_houdinipath_aov_folders:
    """Test houdini_toolbox.sohohooks.aovs.manager._find_houdinipath_aov_folders."""

    def test_no_dirs(self, mocker):
        """Test when no config/aov folders exist in HOUDINI_PATH."""
        mock_find = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.manager.hou.findDirectories"
        )
        mock_find.side_effect = hou.OperationFailed

        result = manager._find_houdinipath_aov_folders()

        assert result == ()

    def test_dirs(self, mocker):
        """Test when one or more config/aov folders exist in HOUDINI_PATH."""
        mock_find = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.manager.hou.findDirectories"
        )

        result = manager._find_houdinipath_aov_folders()

        assert result == mock_find.return_value


class Test__get_aov_path_folders:
    """Test houdini_toolbox.sohohooks.aovs.manager._get_aov_path_folders."""

    def test_no_hpath(self, mocker):
        """Test when the path does not contain the '&' character."""
        env_dict = {"HT_AOV_PATH": "path1:path2"}

        mocker.patch.dict(os.environ, env_dict)

        result = manager._get_aov_path_folders()

        assert result == ("path1", "path2")

    def test_hpath_no_folders(self, mocker):
        """Test when the path contains '&' but no folders are found in the HOUDINI_PATH."""
        mock_find = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.manager._find_houdinipath_aov_folders"
        )

        mock_find.return_value = ()

        env_dict = {"HT_AOV_PATH": "path1:path2:&"}

        mocker.patch.dict(os.environ, env_dict)

        result = manager._get_aov_path_folders()

        assert result == ("path1", "path2", "&")

    def test_hpath_folders(self, mocker):
        """Test when the path contains '&' and folders are found in the HOUDINI_PATH."""
        mock_find = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.manager._find_houdinipath_aov_folders"
        )

        mock_find.return_value = ("hpath1", "hpath2")

        env_dict = {"HT_AOV_PATH": "path1:path2:&"}

        mocker.patch.dict(os.environ, env_dict)

        result = manager._get_aov_path_folders()

        assert result == ("path1", "path2", "hpath1", "hpath2")


class Test_build_menu_script:
    """Test houdini_toolbox.sohohooks.aovs.manager.build_menu_script."""

    def test_no_groups(self, mocker):
        """Test when no groups exist."""
        mock_manager = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.manager.AOV_MANAGER", autospec=True
        )

        mock_manager.groups = None

        mock_aov1 = mocker.MagicMock(spec=manager.AOV)
        mock_aov2 = mocker.MagicMock(spec=manager.AOV)
        mock_aov3 = mocker.MagicMock(spec=manager.AOV)

        mock_manager.aovs = {"P": mock_aov1, "N": mock_aov2, "A": mock_aov3}

        result = manager.build_menu_script()

        assert result == ("A", "A", "N", "N", "P", "P")

    def test_with_groups(self, mocker):
        """Test when groups exist."""
        mock_manager = mocker.patch(
            "houdini_toolbox.sohohooks.aovs.manager.AOV_MANAGER", autospec=True
        )

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

        expected = (
            "@group1",
            "group1",
            "@group2",
            "group2",
            "@group3",
            "group3",
            "_separator_",
            "",
            "A",
            "A",
            "N",
            "N",
            "P",
            "P",
        )

        assert result == expected


def test_flatten_aov_items(mocker):
    """Test houdini_toolbox.sohohooks.aovs.manager.flatten_aov_items."""
    mock_aov = mocker.MagicMock(spec=manager.AOV)

    mock_group_aov = mocker.MagicMock(spec=manager.AOV)

    mock_group = mocker.MagicMock(spec=manager.AOVGroup)
    type(mock_group).aovs = mocker.PropertyMock(return_value=[mock_group_aov])

    result = manager.flatten_aov_items((mock_aov, mock_group))

    assert result == (mock_aov, mock_group_aov)


def test_load_json_files(mocker, mock_hou_ui):
    """Test houdini_toolbox.sohohooks.aovs.manager.load_json_files."""
    mock_expand = mocker.patch(
        "houdini_toolbox.sohohooks.aovs.manager.os.path.expandvars"
    )
    mock_exists = mocker.patch("houdini_toolbox.sohohooks.aovs.manager.os.path.exists")
    mock_manager = mocker.patch(
        "houdini_toolbox.sohohooks.aovs.manager.AOV_MANAGER", autospec=True
    )

    mock_expand.side_effect = ("expanded1", "expanded2")

    mock_exists.side_effect = (False, True)

    path_str = "path1 ; path2"

    mock_hou_ui.selectFile.return_value = path_str

    manager.load_json_files()

    mock_hou_ui.selectFile.assert_called_with(
        pattern="*.json", chooser_mode=hou.fileChooserMode.Read, multiple_select=True
    )

    mock_manager.load.assert_called_with("expanded2")
