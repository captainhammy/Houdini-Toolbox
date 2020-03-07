"""Tests for ht.logging.config module."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
from __future__ import absolute_import
import os

# Houdini Toolbox Imports
import ht.logging.config

# reload(ht.logging.config)

# =============================================================================
# TESTS
# =============================================================================


class Test_init_config(object):
    """Test ht.logging.config.init_config."""

    def test_config_exists(self, mocker):
        mock_path = mocker.MagicMock(spec=str)
        mocker.patch("ht.logging.config.__file__", mock_path)

        mock_exists = mocker.patch("os.path.exists", return_value=True)
        mock_load = mocker.patch("json.load")
        mock_config = mocker.patch("logging.config.dictConfig")

        mock_handle = mocker.mock_open()

        mocker.patch("__builtin__.open", mock_handle)

        ht.logging.config.init_config()

        mock_exists.assert_called_with(
            os.path.join(os.path.dirname(mock_path), "config.json")
        )
        mock_load.assert_called_with(mock_handle.return_value)
        mock_config.assert_called_with(mock_load.return_value)

    def test_no_config(self, mocker):
        mock_path = mocker.MagicMock(spec=str)
        mocker.patch("ht.logging.config.__file__", mock_path)

        mock_exists = mocker.patch("os.path.exists", return_value=False)

        mock_handle = mocker.mock_open()

        mocker.patch("__builtin__.open", mock_handle)

        ht.logging.config.init_config()

        mock_exists.assert_called_with(
            os.path.join(os.path.dirname(mock_path), "config.json")
        )
        mock_handle.assert_not_called()
