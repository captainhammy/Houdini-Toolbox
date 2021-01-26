"""Test the ht.pyfilter.manager module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import argparse

# Third Party Imports
import pytest

# Houdini Toolbox Imports
from ht.pyfilter import manager
from ht.pyfilter.operations.operation import PyFilterOperation

# Houdini Imports
import hou

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def init_manager(mocker):
    """Fixture to initialize a manager."""
    mocker.patch.object(manager.PyFilterManager, "__init__", lambda x: None)

    def _create():
        return manager.PyFilterManager()

    return _create


# =============================================================================
# TESTS
# =============================================================================


class TestManager:
    """Test ht.pyfilter.manager.PyFilterManager object."""

    def test___init__(self, mocker):
        """Test object initialization."""
        mock_register = mocker.patch(
            "ht.pyfilter.manager.PyFilterManager._register_operations"
        )
        mock_parse = mocker.patch(
            "ht.pyfilter.manager.PyFilterManager._get_parsed_args"
        )
        mock_process = mocker.patch(
            "ht.pyfilter.manager.PyFilterManager._process_parsed_args"
        )

        mgr = manager.PyFilterManager()

        assert mgr._data == {}
        assert mgr._operations == []

        mock_register.assert_called()
        mock_parse.assert_called()
        mock_process.assert_called_with(mock_parse.return_value)

    # Properties

    def test_data(self, init_manager, mocker):
        """Test the "data" property."""
        mock_value = mocker.MagicMock(spec=dict)

        mgr = init_manager()
        mgr._data = mock_value

        assert mgr.data == mock_value

    def test_operations(self, init_manager, mocker):
        """Test the "operations" property."""
        mock_value = mocker.MagicMock(spec=list)

        mgr = init_manager()
        mgr._operations = mock_value

        assert mgr.operations == mock_value

    # Methods

    def test__get_parsed_args(self, init_manager, mocker):
        """Test getting pyfilter args."""
        mock_build_parser = mocker.patch("ht.pyfilter.manager._build_parser")
        mock_register_args = mocker.patch.object(
            manager.PyFilterManager, "_register_parser_args"
        )

        mock_parser = mocker.MagicMock(argparse.ArgumentParser)

        mock_build_parser.return_value = mock_parser

        mgr = init_manager()

        result = mgr._get_parsed_args()

        assert result == mock_parser.parse_known_args.return_value[0]

        mock_register_args.assert_called_with(mock_parser)

    def test__process_parsed_args(self, init_manager, mocker):
        """Test having registered operations process their known args."""
        mock_operations = mocker.patch.object(
            manager.PyFilterManager, "operations", new_callable=mocker.PropertyMock
        )

        mock_args = mocker.MagicMock(spec=argparse.Namespace)

        mock_operation = mocker.MagicMock(spec=PyFilterOperation)

        mock_operations.return_value = [mock_operation]

        mgr = init_manager()

        mgr._process_parsed_args(mock_args)

        mock_operation.process_parsed_args.assert_called_with(mock_args)

    # _register_operations

    def test__register_operations__no_data(self, init_manager, mocker):
        """Test registering a file with no operation definitions."""
        mock_find_files = mocker.patch("ht.pyfilter.manager._find_operation_files")
        mock_get_data = mocker.patch("ht.pyfilter.manager._get_operation_data")
        mock_get_class = mocker.patch("ht.pyfilter.manager._get_class")

        mock_path = mocker.MagicMock(spec=str)
        mock_find_files.return_value = (mock_path,)

        data = {}
        mock_get_data.return_value = data

        mgr = init_manager()

        mgr._register_operations()

        mock_get_data.assert_called_with(mock_path)
        mock_get_class.assert_not_called()

    def test__register_operations__no_class(self, init_manager, mocker):
        """Test registering a file with no an unknown operation class."""
        mock_operations = mocker.patch.object(
            manager.PyFilterManager, "operations", new_callable=mocker.PropertyMock
        )
        mock_find_files = mocker.patch("ht.pyfilter.manager._find_operation_files")
        mock_get_data = mocker.patch("ht.pyfilter.manager._get_operation_data")
        mock_get_class = mocker.patch(
            "ht.pyfilter.manager._get_class", return_value=None
        )
        mock_logger = mocker.patch("ht.pyfilter.manager._logger")

        mock_path = mocker.MagicMock(spec=str)
        mock_find_files.return_value = (mock_path,)

        mock_module_name = mocker.MagicMock(spec=str)
        mock_class_name = mocker.MagicMock(spec=str)

        data = {"operations": [(mock_module_name, mock_class_name)]}
        mock_get_data.return_value = data

        mgr = init_manager()

        operations = []
        mock_operations.return_value = operations

        mgr._register_operations()

        mock_get_data.assert_called_with(mock_path)
        mock_get_class.assert_called_with(mock_module_name, mock_class_name)

        assert operations == []
        mock_logger.warning.assert_called()

    def test__register_operations(self, init_manager, mocker):
        """Test registering operations."""
        mock_operations = mocker.patch.object(
            manager.PyFilterManager, "operations", new_callable=mocker.PropertyMock
        )
        mock_find_files = mocker.patch("ht.pyfilter.manager._find_operation_files")
        mock_get_data = mocker.patch("ht.pyfilter.manager._get_operation_data")
        mock_get_class = mocker.patch("ht.pyfilter.manager._get_class")

        mock_path = mocker.MagicMock(spec=str)
        mock_find_files.return_value = (mock_path,)

        mock_module_name = mocker.MagicMock(spec=str)
        mock_class_name = mocker.MagicMock(spec=str)

        data = {"operations": [(mock_module_name, mock_class_name)]}
        mock_get_data.return_value = data

        mgr = init_manager()

        operations = []
        mock_operations.return_value = operations

        mgr._register_operations()

        mock_get_data.assert_called_with(mock_path)
        mock_get_class.assert_called_with(mock_module_name, mock_class_name)

        assert mock_get_class.return_value.return_value in operations
        mock_get_class.return_value.assert_called_with(mgr)

    def test__register_parser_args(self, init_manager, mocker):
        """Test registering known args for the operations."""
        mock_operations = mocker.patch.object(
            manager.PyFilterManager, "operations", new_callable=mocker.PropertyMock
        )

        mock_parser = mocker.MagicMock(spec=argparse.ArgumentParser)

        mock_operation = mocker.MagicMock(spec=PyFilterOperation)

        mgr = init_manager()

        mock_operations.return_value = [mock_operation]

        mgr._register_parser_args(mock_parser)

        mock_operation.register_parser_args.assert_called_with(mock_parser)

    # run_operations_for_stage

    def test_run_operations_for_stage__no_operations(self, init_manager, mocker):
        """Test running for a stage with no operations."""
        mocker.patch.object(
            manager.PyFilterManager, "operations", new_callable=mocker.PropertyMock
        )

        mock_stage_name = mocker.MagicMock(spec=str)

        mgr = init_manager()

        result = mgr.run_operations_for_stage(mock_stage_name)

        assert not result

    def test_run_operations_for_stage__no_runnable(self, init_manager, mocker):
        """Test running for a stage with no operations which should run."""
        mock_operations = mocker.patch.object(
            manager.PyFilterManager, "operations", new_callable=mocker.PropertyMock
        )

        mock_stage_name = mocker.MagicMock(spec=str)

        mock_operation = mocker.MagicMock(spec=PyFilterOperation)
        mock_operation.should_run.return_value = False

        mgr = init_manager()

        mock_operations.return_value = [mock_operation]

        result = mgr.run_operations_for_stage(mock_stage_name)

        assert not result

    def test_run_operations_for_stage__no_matching_stage(self, init_manager, mocker):
        """Test running for a stage where registered operations don't match the stage."""
        mock_operations = mocker.patch.object(
            manager.PyFilterManager, "operations", new_callable=mocker.PropertyMock
        )

        stage_name = "stage_name"

        mock_operation = mocker.MagicMock(spec=PyFilterOperation)
        mock_operation.should_run.return_value = True

        mgr = init_manager()

        mock_operations.return_value = [mock_operation]

        result = mgr.run_operations_for_stage(stage_name)

        assert not result

    def test_run_operations_for_stage(self, init_manager, mocker):
        """Test running operations for a stage."""
        mock_operations = mocker.patch.object(
            manager.PyFilterManager, "operations", new_callable=mocker.PropertyMock
        )

        stage_name = "stage_name"

        mock_func = mocker.MagicMock()
        mock_func.return_value = True

        mock_operation = mocker.MagicMock(spec=PyFilterOperation)
        mock_operation.should_run.return_value = True
        mock_operation.stage_name = mock_func

        mgr = init_manager()

        mock_operations.return_value = [mock_operation]

        result = mgr.run_operations_for_stage(stage_name, "value", bar="value")

        assert result

        mock_func.assert_called_with("value", bar="value")


def test_build_parser():
    """Test ht.pyfilter.manager._build_parser."""
    result = manager._build_parser()

    assert isinstance(result, argparse.ArgumentParser)


class Test__find_operation_files:
    """Test ht.pyfilter.manager._find_operation_files."""

    def test_no_files(self, mocker):
        """Test when no files could be found."""
        mocker.patch("hou.findFiles", side_effect=hou.OperationFailed)

        result = manager._find_operation_files()

        assert result == ()

    def test(self, mocker):
        """Test when operation files are found."""
        mock_find = mocker.patch("hou.findFiles")

        result = manager._find_operation_files()

        assert result == mock_find.return_value


class Test__get_class:
    """Test ht.pyfilter.manager._get_class."""

    def test_importerror(self, mocker):
        """Test importing a module when an ImportError occurs."""
        mock_import = mocker.patch("ht.pyfilter.manager.importlib.import_module")

        mock_module_name = mocker.MagicMock(spec=str)
        mock_class_name = mocker.MagicMock(spec=str)

        mock_import.side_effect = ImportError

        result = manager._get_class(mock_module_name, mock_class_name)

        assert result is None

        mock_import.assert_called_with(mock_module_name)

    def test(self, mocker):
        """Test importing a module and class."""
        mock_import = mocker.patch("ht.pyfilter.manager.importlib.import_module")

        mock_module_name = mocker.MagicMock(spec=str)
        class_name = "class_name"

        mock_cls = mocker.MagicMock()

        mock_module = mocker.MagicMock()
        setattr(mock_module, class_name, mock_cls)

        mock_import.return_value = mock_module

        result = manager._get_class(mock_module_name, class_name)

        assert result == mock_cls

        mock_import.assert_called_with(mock_module_name)


class Test__get_operation_data:
    """Test ht.pyfilter.manager._get_operation_data."""

    def test_ioerror(self, mocker):
        """Test getting operation data when the file cannot be opened."""
        mock_handle = mocker.mock_open()
        mock_handle.side_effect = IOError
        mocker.patch("builtins.open", mock_handle)

        mock_path = mocker.MagicMock(spec=str)

        result = manager._get_operation_data(mock_path)
        assert result == {}

    def test_valueerror(self, mocker):
        """Test getting operation data when the file cannot be converted to json."""
        mock_load = mocker.patch("json.load")
        mock_load.side_effect = ValueError

        mock_path = mocker.MagicMock(spec=str)

        mock_handle = mocker.mock_open()
        mocker.patch("builtins.open", mock_handle)

        result = manager._get_operation_data(mock_path)

        assert result == {}

        mock_load.assert_called_with(mock_handle.return_value)

    def test(self, mocker):
        """Test getting operation data from a file."""
        mock_load = mocker.patch("json.load")

        mock_path = mocker.MagicMock(spec=str)

        mock_handle = mocker.mock_open()
        mocker.patch("builtins.open", mock_handle)

        result = manager._get_operation_data(mock_path)

        assert result == mock_load.return_value

        mock_handle.assert_called_with(mock_path)

        mock_load.assert_called_with(mock_handle.return_value)
