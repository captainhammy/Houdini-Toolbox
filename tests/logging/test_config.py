"""Tests for ht.logging.config module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import os

# Houdini Toolbox
import ht.logging.config

# =============================================================================
# TESTS
# =============================================================================


class Test_init_config:
    """Test ht.logging.config.init_config."""

    def test_config_exists(self, mocker):
        """Test when a config file exists."""
        fake_path = "/path/to/file.py"

        mocker.patch("ht.logging.config.__file__", fake_path)

        mock_exists = mocker.patch("os.path.exists", return_value=True)
        mock_load = mocker.patch("json.load")
        mock_config = mocker.patch("logging.config.dictConfig")

        mock_handle = mocker.mock_open()

        mocker.patch("builtins.open", mock_handle)

        ht.logging.config.init_config()

        mock_exists.assert_called_with(
            os.path.join(os.path.dirname(fake_path), "config.json")
        )
        mock_load.assert_called_with(mock_handle.return_value)
        mock_config.assert_called_with(mock_load.return_value)

    def test_no_config(self, mocker):
        """Test when a config file does not exist."""
        fake_path = "/path/to/file.py"

        mocker.patch("ht.logging.config.__file__", fake_path)

        mock_exists = mocker.patch("os.path.exists", return_value=False)

        mock_handle = mocker.mock_open()

        mocker.patch("builtins.open", mock_handle)

        ht.logging.config.init_config()

        mock_exists.assert_called_with(
            os.path.join(os.path.dirname(fake_path), "config.json")
        )
        mock_handle.assert_not_called()
