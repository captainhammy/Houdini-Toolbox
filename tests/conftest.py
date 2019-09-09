"""Test setup."""

# =============================================================================
# IMPORTS
# =============================================================================

# Third Party Imports
from mock import MagicMock, patch
import pytest

# Houdini Imports
import hou

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def patch_hou():
    """Mock importing of the hou module."""
    mock_hou = MagicMock()

    modules = {
        "hou": mock_hou,
        "original_hou": hou
    }

    patcher = patch.dict("sys.modules", modules)
    patcher.start()

    yield modules

    patcher.stop()


@pytest.fixture
def patch_soho():
    """Mock importing of soho modules."""
    mock_api = MagicMock()
    mock_hooks = MagicMock()
    mock_mantra = MagicMock()
    mock_settings = MagicMock()
    mock_soho = MagicMock()

    modules = {
        "IFDapi": mock_api,
        "IFDhooks": mock_hooks,
        "IFDsettings": mock_settings,
        "mantra": mock_mantra,
        "soho": mock_soho,
    }

    patcher = patch.dict("sys.modules", modules)
    patcher.start()

    yield modules

    patcher.stop()


@pytest.fixture
def raise_hou_operationfailed():

    def raise_error(*args, **kwargs):
        raise hou.OperationFailed()

    return raise_error
