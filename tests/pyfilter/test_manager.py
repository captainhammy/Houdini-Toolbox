"""Test the ht.pyfilter.manager module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import argparse

# Third Party Imports
from mock import MagicMock, PropertyMock, mock_open, patch

# Houdini Toolbox Imports
from ht.pyfilter import manager
from ht.pyfilter.operations.operation import PyFilterOperation

# Houdini Imports
import hou


# =============================================================================
# CLASSES
# =============================================================================

class TestManager(object):
    """Test ht.pyfilter.manager.PyFilterManager object."""

    @patch("ht.pyfilter.manager.PyFilterManager._process_parsed_args")
    @patch("ht.pyfilter.manager.PyFilterManager._get_parsed_args")
    @patch("ht.pyfilter.manager.PyFilterManager._register_operations")
    def test___init__(self, mock_register, mock_parse, mock_process):
        mgr = manager.PyFilterManager()

        assert mgr._data == {}
        assert mgr._operations == []

        mock_register.assert_called()
        mock_parse.assert_called()
        mock_process.assert_called_with(mock_parse.return_value)

    # Properties

    @patch.object(manager.PyFilterManager, "__init__", lambda x: None)
    def test_data(self):
        value = MagicMock(spec=dict)

        mgr = manager.PyFilterManager()

        mgr._data = value

        assert mgr.data == value

    @patch.object(manager.PyFilterManager, "__init__", lambda x: None)
    def test_operations(self):
        value = MagicMock(spec=list)

        mgr = manager.PyFilterManager()

        mgr._operations = value

        assert mgr.operations == value

    # Methods

    # _get_parsed_args

    @patch.object(manager.PyFilterManager, "_register_parser_args")
    @patch("ht.pyfilter.manager._build_parser")
    @patch.object(manager.PyFilterManager, "__init__", lambda x: None)
    def test__get_parsed_args(self, mock_build_parser, mock_register_args):
        mock_parser = MagicMock(argparse.ArgumentParser)

        mock_build_parser.return_value = mock_parser

        mgr = manager.PyFilterManager()

        result = mgr._get_parsed_args()

        assert result == mock_parser.parse_known_args.return_value[0]

        mock_register_args.assert_called_with(mock_parser)

    # _process_parsed_args

    @patch.object(manager.PyFilterManager, "operations", new_callable=PropertyMock)
    @patch.object(manager.PyFilterManager, "__init__", lambda x: None)
    def test__process_parsed_args(self, mock_operations):
        mock_args = MagicMock(spec=argparse.Namespace)

        mock_operation = MagicMock(spec=PyFilterOperation)

        mock_operations.return_value = [mock_operation]

        mgr = manager.PyFilterManager()

        mgr._process_parsed_args(mock_args)

        mock_operation.process_parsed_args.assert_called_with(mock_args)

    # _register_operations

    @patch("ht.pyfilter.manager._logger")
    @patch("ht.pyfilter.manager._get_class")
    @patch("ht.pyfilter.manager._get_operation_data")
    @patch("ht.pyfilter.manager._find_operation_files")
    @patch.object(manager.PyFilterManager, "__init__", lambda x: None)
    def test__register_operations__no_data(self, mock_find_files, mock_get_data, mock_get_class, mock_logger):
        mock_file_path = MagicMock(spec=str)
        mock_find_files.return_value = (mock_file_path, )

        data = {}
        mock_get_data.return_value = data

        mgr = manager.PyFilterManager()

        mgr._register_operations()

        mock_get_data.assert_called_with(mock_file_path)
        mock_get_class.assert_not_called()

    @patch("ht.pyfilter.manager._logger")
    @patch("ht.pyfilter.manager._get_class", return_value=None)
    @patch("ht.pyfilter.manager._get_operation_data")
    @patch("ht.pyfilter.manager._find_operation_files")
    @patch.object(manager.PyFilterManager, "operations", new_callable=PropertyMock)
    @patch.object(manager.PyFilterManager, "__init__", lambda x: None)
    def test__register_operations__no_class(self, mock_operations, mock_find_files, mock_get_data, mock_get_class, mock_logger):
        mock_file_path = MagicMock(spec=str)
        mock_find_files.return_value = (mock_file_path, )

        mock_module_name = MagicMock(spec=str)
        mock_class_name = MagicMock(spec=str)

        data = {
            "operations": [
                (mock_module_name, mock_class_name),
            ]
        }
        mock_get_data.return_value = data

        mgr = manager.PyFilterManager()

        operations = []
        mock_operations.return_value = operations

        mgr._register_operations()

        mock_get_data.assert_called_with(mock_file_path)
        mock_get_class.assert_called_with(mock_module_name, mock_class_name)

        assert operations == []
        mock_logger.warning.assert_called()

    @patch("ht.pyfilter.manager._logger")
    @patch("ht.pyfilter.manager._get_class")
    @patch("ht.pyfilter.manager._get_operation_data")
    @patch("ht.pyfilter.manager._find_operation_files")
    @patch.object(manager.PyFilterManager, "operations", new_callable=PropertyMock)
    @patch.object(manager.PyFilterManager, "__init__", lambda x: None)
    def test__register_operations(self, mock_operations, mock_find_files, mock_get_data, mock_get_class, mock_logger):
        mock_file_path = MagicMock(spec=str)
        mock_find_files.return_value = (mock_file_path, )

        mock_module_name = MagicMock(spec=str)
        mock_class_name = MagicMock(spec=str)

        data = {
            "operations": [
                (mock_module_name, mock_class_name),
            ]
        }
        mock_get_data.return_value = data

        mgr = manager.PyFilterManager()

        operations = []
        mock_operations.return_value = operations

        mgr._register_operations()

        mock_get_data.assert_called_with(mock_file_path)
        mock_get_class.assert_called_with(mock_module_name, mock_class_name)

        assert mock_get_class.return_value.return_value in operations
        mock_get_class.return_value.assert_called_with(mgr)

    # _register_parser_args

    @patch.object(manager.PyFilterManager, "operations", new_callable=PropertyMock)
    @patch.object(manager.PyFilterManager, "__init__", lambda x: None)
    def test__register_parser_args(self, mock_operations):
        mock_parser = MagicMock(spec=argparse.ArgumentParser)

        mock_operation = MagicMock(spec=PyFilterOperation)

        mgr = manager.PyFilterManager()

        mock_operations.return_value = [mock_operation]

        mgr._register_parser_args(mock_parser)

        mock_operation.register_parser_args.assert_called_with(mock_parser)

    # run_operations_for_stage

    @patch.object(manager.PyFilterManager, "operations", new_callable=PropertyMock(return_value=[]))
    @patch.object(manager.PyFilterManager, "__init__", lambda x: None)
    def test_run_operations_for_stage__no_operations(self, mock_operations):
        mock_stage_name = MagicMock(spec=str)

        mgr = manager.PyFilterManager()

        result = mgr.run_operations_for_stage(mock_stage_name)

        assert not result

    @patch.object(manager.PyFilterManager, "operations", new_callable=PropertyMock)
    @patch.object(manager.PyFilterManager, "__init__", lambda x: None)
    def test_run_operations_for_stage__no_runnable(self, mock_operations):
        mock_stage_name = MagicMock(spec=str)

        mock_operation = MagicMock(spec=PyFilterOperation)
        mock_operation.should_run.return_value = False

        mgr = manager.PyFilterManager()

        mock_operations.return_value = [mock_operation]

        result = mgr.run_operations_for_stage(mock_stage_name)

        assert not result

    @patch.object(manager.PyFilterManager, "operations", new_callable=PropertyMock)
    @patch.object(manager.PyFilterManager, "__init__", lambda x: None)
    def test_run_operations_for_stage__no_matching_stage(self, mock_operations):
        stage_name = "stage_name"

        mock_operation = MagicMock(spec=PyFilterOperation)
        mock_operation.should_run.return_value = True

        mgr = manager.PyFilterManager()

        mock_operations.return_value = [mock_operation]

        result = mgr.run_operations_for_stage(stage_name)

        assert not result

    @patch.object(manager.PyFilterManager, "operations", new_callable=PropertyMock)
    @patch.object(manager.PyFilterManager, "__init__", lambda x: None)
    def test_run_operations_for_stage(self, mock_operations):
        stage_name = "stage_name"

        mock_func = MagicMock()
        mock_func.return_value = True

        mock_operation = MagicMock(spec=PyFilterOperation)
        mock_operation.should_run.return_value = True
        mock_operation.stage_name = mock_func

        mgr = manager.PyFilterManager()

        mock_operations.return_value = [mock_operation]

        result = mgr.run_operations_for_stage(stage_name, "value", bar="value")

        assert result

        mock_func.assert_called_with("value", bar="value")


class Test__build_parser(object):
    """Test ht.pyfilter.manager._build_parser."""

    def test_build_parser(self):
        result = manager._build_parser()

        assert (isinstance(result, argparse.ArgumentParser))


class Test__find_operation_files(object):
    """Test ht.pyfilter.manager._find_operation_files."""

    @patch("ht.pyfilter.manager._logger")
    @patch("hou.findFiles")
    def test_no_files(self, mock_find_files, mock_logger):
        def raise_exc(*args, **kwargs):
            raise hou.OperationFailed

        mock_find_files.side_effect = raise_exc

        result = manager._find_operation_files()

        assert result == ()

    @patch("hou.findFiles")
    def test(self, mock_find_files):
        result = manager._find_operation_files()

        assert result == mock_find_files.return_value


class Test__get_class(object):
    """Test ht.pyfilter.manager._get_class."""

    @patch("ht.pyfilter.manager.importlib.import_module")
    def test_ImportError(self, mock_import):
        mock_module_name = MagicMock(spec=str)
        mock_class_name = MagicMock(spec=str)

        mock_import.side_effect = ImportError

        result = manager._get_class(mock_module_name, mock_class_name)

        assert result is None

        mock_import.assert_called_with(mock_module_name)

    @patch("ht.pyfilter.manager.importlib.import_module")
    def test(self, mock_import):
        mock_module_name = MagicMock(spec=str)
        class_name = "class_name"

        mock_cls = MagicMock()

        mock_module = MagicMock()
        setattr(mock_module, class_name, mock_cls)

        mock_import.return_value = mock_module

        result = manager._get_class(mock_module_name, class_name)

        assert result == mock_cls

        mock_import.assert_called_with(mock_module_name)


class Test__get_operation_data(object):
    """Test ht.pyfilter.manager._get_operation_data."""

    @patch("ht.pyfilter.manager._logger")
    @patch("__builtin__.open")
    def test_IOError(self, mock_open, mock_logger):
        mock_file_path = MagicMock(spec=str)

        mock_open.side_effect = IOError

        result = manager._get_operation_data(mock_file_path)
        assert result == {}

    @patch("ht.pyfilter.manager._logger")
    @patch("json.load")
    @patch("__builtin__.open", new_callable=mock_open)
    def test_ValueError(self, mock_open_file, mock_load, mock_logger):
        mock_file_path = MagicMock(spec=str)

        mock_load.side_effect = ValueError

        result = manager._get_operation_data(mock_file_path)
        assert result == {}

    @patch("json.load")
    @patch("__builtin__.open", new_callable=mock_open)
    def test(self, mock_open_file, mock_load):
        mock_file_path = MagicMock(spec=str)

        result = manager._get_operation_data(mock_file_path)

        assert result == mock_load.return_value

        mock_open_file.assert_called_with(mock_file_path)
