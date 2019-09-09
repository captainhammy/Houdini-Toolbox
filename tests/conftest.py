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
    """Mock importing of the hou module.

    The mocked module is available via the 'hou' key.

    The original hou module is available via the 'original_hou' key.

    """
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
def mock_hou_ui():
    """Mock the hou.ui module which isn't available when running tests via Hython."""
    mock_ui = MagicMock()

    hou.ui = mock_ui

    yield mock_ui

    del hou.ui


@pytest.fixture
def patch_soho():
    """Mock importing of mantra/soho related modules.

    Available mocked modules are available via their original names as keys.

    """
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
    """Fixture to represent throwing a hou.OperationFailed exception.

    We have to use these because setting a mock object's side_effect to a
    hou.Error (or subclass) exception doesn't work properly compared to normal
    Exceptions.

    """
    def raise_error(*args, **kwargs):
        raise hou.OperationFailed()

    return raise_error
