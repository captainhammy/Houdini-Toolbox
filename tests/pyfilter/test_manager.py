"""Test the ht.pyfilter.manager module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import argparse
from mock import MagicMock, mock_open, patch
import unittest

# Houdini Toolbox Imports
from ht.pyfilter import manager
from ht.pyfilter.operations.operation import PyFilterOperation

# Houdini Imports
import hou

reload(manager)

# =============================================================================
# CLASSES
# =============================================================================

class TestManager(unittest.TestCase):
    """Test ht.pyfilter.manager.PyFilterManager object."""

    @patch("ht.pyfilter.manager.PyFilterManager._process_parsed_args")
    @patch("ht.pyfilter.manager.PyFilterManager._get_parsed_args")
    @patch("ht.pyfilter.manager.PyFilterManager._register_operations")
    def test___init__(self, mock_register, mock_parse, mock_process):
        mgr = manager.PyFilterManager()

        self.assertEqual(mgr._data, {})
        self.assertEqual(mgr._operations, [])

        mock_register.assert_called()
        mock_parse.assert_called()
        mock_process.assert_called_with(mock_parse.return_value)

    # Properties

    @patch.object(manager.PyFilterManager, "__init__", lambda x: None)
    def test_data(self):
        value = {"key": "value"}

        mgr = manager.PyFilterManager()

        mgr._data = value

        self.assertEqual(mgr.data, value)

    @patch.object(manager.PyFilterManager, "__init__", lambda x: None)
    def test_operations(self):
        value = ["operation1"]

        mgr = manager.PyFilterManager()

        mgr._operations = value

        self.assertEqual(mgr.operations, value)

    # Methods

    @patch.object(manager.PyFilterManager, "_register_parser_args")
    @patch("ht.pyfilter.manager._build_parser")
    @patch.object(manager.PyFilterManager, "__init__", lambda x: None)
    def test__get_parsed_args(self, mock_build_parser, mock_register_args):
        mock_parser = MagicMock(argparse.ArgumentParser)

        mock_build_parser.return_value = mock_parser

        mgr = manager.PyFilterManager()

        result = mgr._get_parsed_args()

        self.assertEqual(result, mock_parser.parse_known_args.return_value[0])

        mock_register_args.assert_called_with(mock_parser)

    @patch.object(manager.PyFilterManager, "__init__", lambda x: None)
    def test__process_parsed_args(self):
        mock_args = MagicMock(spec=argparse.Namespace)

        mock_operation = MagicMock(spec=PyFilterOperation)

        mgr = manager.PyFilterManager()
        mgr._operations = [mock_operation]

        mgr._process_parsed_args(mock_args)

        mock_operation.process_parsed_args.assert_called_with(mock_args)

    @patch("ht.pyfilter.manager.logger")
    @patch("ht.pyfilter.manager._get_class")
    @patch("ht.pyfilter.manager._get_operation_data")
    @patch("ht.pyfilter.manager._find_operation_files")
    @patch.object(manager.PyFilterManager, "__init__", lambda x: None)
    def test__register_operations__no_data(self, mock_find_files, mock_get_data, mock_get_class, mock_logger):
        filepath = "/path/to/file.json"
        mock_find_files.return_value = (filepath, )

        data = {}
        mock_get_data.return_value = data

        mgr = manager.PyFilterManager()

        mgr._register_operations()

        mock_get_data.assert_called_with(filepath)
        mock_get_class.assert_not_called()

    @patch("ht.pyfilter.manager.logger")
    @patch("ht.pyfilter.manager._get_class")
    @patch("ht.pyfilter.manager._get_operation_data")
    @patch("ht.pyfilter.manager._find_operation_files")
    @patch.object(manager.PyFilterManager, "__init__", lambda x: None)
    def test__register_operations(self, mock_find_files, mock_get_data, mock_get_class, mock_logger):
        filepath = "/path/to/file.json"
        mock_find_files.return_value = (filepath, )

        module_name = "module_name"
        class_name = "class_name"

        data = {
            "operations": [
                (module_name, class_name),
            ]
        }
        mock_get_data.return_value = data

        mgr = manager.PyFilterManager()
        mgr._operations = []

        mgr._register_operations()

        mock_get_data.assert_called_with(filepath)
        mock_get_class.assert_called_with(module_name, class_name)

        self.assertTrue(mock_get_class.return_value.return_value in mgr._operations)
        mock_get_class.return_value.assert_called_with(mgr)

    @patch.object(manager.PyFilterManager, "__init__", lambda x: None)
    def test__register_parser_args(self):
        mock_parser = MagicMock(spec=argparse.ArgumentParser)

        mock_operation = MagicMock(spec=PyFilterOperation)

        mgr = manager.PyFilterManager()
        mgr._operations = [mock_operation]

        mgr._register_parser_args(mock_parser)

        mock_operation.register_parser_args.assert_called_with(mock_parser)

    @patch.object(manager.PyFilterManager, "__init__", lambda x: None)
    def test_run_operations_for_stage__no_operations(self):

        mgr = manager.PyFilterManager()
        mgr._operations = []

        result = mgr.run_operations_for_stage("stage_name")

        self.assertFalse(result)

    @patch.object(manager.PyFilterManager, "__init__", lambda x: None)
    def test_run_operations_for_stage__no_runnable(self):
        mock_operation = MagicMock(spec=PyFilterOperation)
        mock_operation.should_run.return_value = False

        mgr = manager.PyFilterManager()
        mgr._operations = [mock_operation]

        result = mgr.run_operations_for_stage("stage_name")

        self.assertFalse(result)

    @patch.object(manager.PyFilterManager, "__init__", lambda x: None)
    def test_run_operations_for_stage__no_matching_stage(self):
        mock_operation = MagicMock(spec=PyFilterOperation)
        mock_operation.should_run.return_value = True
        #del mock_operation.f

        mgr = manager.PyFilterManager()
        mgr._operations = [mock_operation]

        result = mgr.run_operations_for_stage("stage_name")

        self.assertFalse(result)

    @patch.object(manager.PyFilterManager, "__init__", lambda x: None)
    def test_run_operations_for_stage(self):
        mock_func = MagicMock()
        mock_func.return_value = True

        mock_operation = MagicMock(spec=PyFilterOperation)
        mock_operation.should_run.return_value = True
        mock_operation.stage_name = mock_func

        mgr = manager.PyFilterManager()
        mgr._operations = [mock_operation]

        result = mgr.run_operations_for_stage("stage_name", "value", bar="value")

        self.assertTrue(result)

        mock_func.assert_called_with("value", bar="value")


class Test__build_parser(unittest.TestCase):
    """Test ht.pyfilter.manager._build_parser."""

    def test_build_parser(self):
        result = manager._build_parser()

        self.assertTrue(isinstance(result, argparse.ArgumentParser))


class Test__find_operation_files(unittest.TestCase):
    """Test ht.pyfilter.manager._find_operation_files."""

    @patch("ht.pyfilter.manager.logger")
    @patch("hou.findFiles")
    def test_no_files(self, mock_find_files, mock_logger):
        def raise_exc(*args, **kwargs):
            raise hou.OperationFailed

        mock_find_files.side_effect = raise_exc

        result = manager._find_operation_files()

        self.assertEqual(result, ())

    @patch("hou.findFiles")
    def test(self, mock_find_files):
        result = manager._find_operation_files()

        self.assertEqual(result, mock_find_files.return_value)


class Test__get_class(unittest.TestCase):
    """Test ht.pyfilter.manager._get_operation_data."""

    def test_ImportError(self):
        with patch("__builtin__.__import__") as mock_import:
            mock_import.side_effect = ImportError

            result = manager._get_class("foo", "bar")

            self.assertIsNone(result)

    def test(self):
        module_name = "module_name"
        class_name = "class_name"

        mock_cls = MagicMock()

        mock_module = MagicMock()
        mock_module.class_name = mock_cls

        with patch("__builtin__.__import__") as mock_import:
            mock_import.return_value = mock_module

            result = manager._get_class(module_name, class_name)

            self.assertEqual(result, mock_cls)

            mock_import.assert_called_with(module_name, {}, {}, [class_name])


class Test__get_operation_data(unittest.TestCase):
    """Test ht.pyfilter.manager._get_operation_data."""

    @patch("ht.pyfilter.manager.logger")
    @patch("__builtin__.open")
    def test_IOError(self, mock_open, mock_logger):
        file_path = "/path/to/data.json"
        mock_open.side_effect = IOError

        result = manager._get_operation_data(file_path)
        self.assertEqual(result, {})

    @patch("ht.pyfilter.manager.logger")
    @patch("json.load")
    @patch("__builtin__.open", new_callable=mock_open)
    def test_ValueError(self, mock_open_file, mock_load, mock_logger):
        file_path = "/path/to/data.json"

        mock_load.side_effect = ValueError

        result = manager._get_operation_data(file_path)
        self.assertEqual(result, {})

    @patch("json.load")
    @patch("__builtin__.open", new_callable=mock_open)
    def test(self, mock_open_file, mock_load):
        file_path = "/path/to/data.json"

        result = manager._get_operation_data(file_path)

        self.assertEqual(result, mock_load.return_value)

        mock_open_file.assert_called_with(file_path)

# =============================================================================

if __name__ == '__main__':
    unittest.main()

