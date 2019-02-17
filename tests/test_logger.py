"""Tests for ht.logger module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import logging
from mock import MagicMock, PropertyMock, mock_open, patch
import unittest

# Houdini Toolbox Imports
import ht.logger

reload(ht.logger)

# =============================================================================
# CLASSES
# =============================================================================

class Test__get_default_log_level(unittest.TestCase):
    """Test ht.logger._get_default_log_level."""

    @patch("ht.logger._log_level_from_string")
    @patch("ht.logger.os.getenv")
    def test_from_env(self, mock_getenv, mock_from_string):
        """Test getting the default from HT_LOG_LEVEL."""
        mock_level = MagicMock(spec=str)

        env_dict = {"HT_LOG_LEVEL": mock_level}

        mock_getenv.side_effect = env_dict.get

        result = ht.logger._get_default_log_level()

        self.assertEqual(result, mock_from_string.return_value)

        mock_from_string.assert_called_with(mock_level)

    @patch("ht.logger._log_level_from_string")
    @patch("ht.logger.os.getenv")
    def test_default(self, mock_getenv, mock_from_string):
        """Test using the hardcoded default value."""
        env_dict = {}

        mock_getenv.side_effect = env_dict.get

        result = ht.logger._get_default_log_level()

        self.assertEqual(result, mock_from_string.return_value)

        mock_from_string.assert_called_with("INFO")


class Test__init_logger_config(unittest.TestCase):
    """Test ht.logger._init_logger_config."""

    @patch("ht.logger.logging.config.dictConfig")
    @patch("ht.logger.json.load")
    @patch("ht.logger.os.path")
    def test_exists(self, mock_os_path, mock_load, mock_config):
        """Test when the target config file exists."""
        m = mock_open()

        mock_os_path.exists.return_value = True

        with patch("ht.logger.__file__", new_callable=PropertyMock) as mock_file:
            with patch("__builtin__.open", m):
                ht.logger._init_logger_config()

        mock_os_path.exists.assert_called_with(mock_os_path.join.return_value)
        m.assert_called_with(mock_os_path.join.return_value, 'r')

        mock_load.assert_called_with(m.return_value)
        mock_config.assert_called_with(mock_load.return_value)

    @patch("ht.logger.json.load")
    @patch("ht.logger.os.path")
    def test_path_does_not_exist(self, mock_os_path, mock_load):
        """Test when the target config file does not exist."""
        m = mock_open()

        mock_os_path.exists.return_value = False

        with patch("ht.logger.__file__", new_callable=PropertyMock) as mock_file:
            with patch("__builtin__.open", m):
                ht.logger._init_logger_config()

        mock_os_path.exists.assert_called_with(mock_os_path.join.return_value)
        m.assert_not_called()


class Test__log_level_from_string(unittest.TestCase):
    """Test ht.logger._log_level_from_string."""

    def test_lower_case(self):
        """Test a lower case string which would be converted to upper case."""
        result = ht.logger._log_level_from_string("info")

        self.assertEqual(result, logging.INFO)

    def test_upper_case(self):
        """Test an upper case string."""
        result = ht.logger._log_level_from_string("INFO")

        self.assertEqual(result, logging.INFO)

    def test_no_match(self):
        """Test an invalid value."""
        with self.assertRaises(AttributeError):
            ht.logger._log_level_from_string("foo")


class Test_get_logger(unittest.TestCase):
    """Test ht.logger.get_logger."""

    @patch("ht.logger._get_default_log_level")
    @patch("ht.logger.logging.getLogger")
    def test_none_level(self, mock_get, mock_get_default):
        """Test when there is no passed logger level and it uses the default."""
        mock_name = MagicMock(spec=str)

        mock_logger = MagicMock(spec=logging.Logger)
        mock_get.return_value = mock_logger

        result = ht.logger.get_logger(mock_name)

        self.assertEqual(result, mock_logger)

        mock_get.assert_called_with(mock_name)
        mock_logger.setLevel.assert_called_with(mock_get_default.return_value)

    @patch("ht.logger._log_level_from_string")
    @patch("ht.logger.logging.getLogger")
    def test_str_level(self, mock_get, mock_from_string):
        """Test when an optional logger level string is passed."""
        mock_name = MagicMock(spec=str)
        mock_level = MagicMock(spec=str)

        mock_logger = MagicMock(spec=logging.Logger)
        mock_get.return_value = mock_logger

        result = ht.logger.get_logger(mock_name, mock_level)

        self.assertEqual(result, mock_logger)

        mock_get.assert_called_with(mock_name)
        mock_from_string.assert_called_with(mock_level)
        mock_logger.setLevel.assert_called_with(mock_from_string.return_value)

# =============================================================================

if __name__ == '__main__':
    unittest.main()
