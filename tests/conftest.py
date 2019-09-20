"""Test setup."""

# =============================================================================
# IMPORTS
# =============================================================================

# Third Party Imports
import pytest

# Houdini Imports
import hou


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_hou_exceptions(mocker):
    """Fixture to support dealing with hou.Error exceptions.

    Since hou.Error and all derived exceptions are not actual Exception objects
    pytest will not list this.  If your code throws an uncaught exception it will
    confuse pytest and it will basically error, but not error.  The test execution
    will halt but your test will not fail.

    This fixture gets around this by patching all the hou.Error related exceptions
    with exceptions derived from Exception and the allowing you to catch those.
    When dealing testing code which involves hou exceptions you should include this
    fixture and then use the supplied fake exception when checking for raised exceptions.

    def foo():
        raise hou.OperationFailed()

    def test_foo(mock_hou_exception):
        with pytest.raises(mock_hou_exception.OperationFailed):
            foo()

    """

    class _HouError(Exception):
        """Exception to emulate a hou.Error"""

    class _HouGeometryPermissionError(_HouError):
        """Exception to emulate a hou.GeometryPermissionError"""

    class _HouInitScriptFailed(_HouError):
        """Exception to emulate a hou.InitScriptFailed"""

    class _HouInvalidInput(_HouError):
        """Exception to emulate a hou.InvalidInput"""

    class _HouInvalidNodeType(_HouError):
        """Exception to emulate a hou.InvalidNodeType"""

    class _HouInvalidSize(_HouError):
        """Exception to emulate a hou.InvalidSize"""

    class _HouKeyframeValueNotSet(_HouError):
        """Exception to emulate a hou.KeyframeValueNotSet"""

    class _HouLoadWarning(_HouError):
        """Exception to emulate a hou.LoadWarning"""

    class _HouMatchDefinitionError(_HouError):
        """Exception to emulate a hou.MatchDefinitionError"""

    class _HouNameConflict(_HouError):
        """Exception to emulate a hou.NameConflict"""

    class _HouNodeError(_HouError):
        """Exception to emulate a hou.NodeError"""

    class _HouNodeWarning(_HouError):
        """Exception to emulate a hou.NodeWarning"""

    class _HouNotAvailable(_HouError):
        """Exception to emulate a hou.NotAvailable"""

    class _HouObjectWasDeleted(_HouError):
        """Exception to emulate a hou.ObjectWasDeleted"""

    class _HouOperationFailed(_HouError):
        """Exception to emulate a hou.OperationFailed"""

    class _HouOperationInterrupted(_HouError):
        """Exception to emulate a hou.OperationInterrupted"""

    class _HouPermissionError(_HouError):
        """Exception to emulate a hou.PermissionError"""

    class _HouSystemExit(_HouError):
        """Exception to emulate a hou.SystemExit"""

    class _HouTypeError(_HouError):
        """Exception to emulate a hou.TypeError"""

    class _HouValueError(_HouError):
        """Exception to emulate a hou.ValueError"""

    mocker.patch("hou.Error", _HouError)
    mocker.patch("hou.GeometryPermissionError", _HouGeometryPermissionError)
    mocker.patch("hou.InitScriptFailed", _HouInitScriptFailed)
    mocker.patch("hou.InvalidInput", _HouInvalidInput)
    mocker.patch("hou.InvalidNodeType", _HouInvalidNodeType)
    mocker.patch("hou.InvalidSize", _HouInvalidSize)
    mocker.patch("hou.KeyframeValueNotSet", _HouKeyframeValueNotSet)
    mocker.patch("hou.LoadWarning", _HouLoadWarning)
    mocker.patch("hou.MatchDefinitionError", _HouMatchDefinitionError)
    mocker.patch("hou.NameConflict", _HouNameConflict)
    mocker.patch("hou.NodeError", _HouNodeError)
    mocker.patch("hou.NodeWarning", _HouNodeWarning)
    mocker.patch("hou.NotAvailable", _HouNotAvailable)
    mocker.patch("hou.ObjectWasDeleted", _HouObjectWasDeleted)
    mocker.patch("hou.OperationFailed", _HouOperationFailed)
    mocker.patch("hou.OperationInterrupted", _HouOperationInterrupted)
    mocker.patch("hou.PermissionError", _HouPermissionError)
    mocker.patch("hou.SystemExit", _HouSystemExit)
    mocker.patch("hou.TypeError", _HouTypeError)
    mocker.patch("hou.ValueError", _HouValueError)

    class HouExceptions(object):
        Error = _HouError
        GeometryPermissionError = _HouGeometryPermissionError
        InitScriptFailed = _HouInitScriptFailed
        InvalidInput = _HouInvalidInput
        InvalidNodeType = _HouInvalidNodeType
        InvalidSize = _HouInvalidSize
        KeyframeValueNotSet = _HouKeyframeValueNotSet
        LoadWarning = _HouLoadWarning
        MatchDefinitionError = _HouMatchDefinitionError
        NameConflict = _HouNameConflict
        NodeError = _HouNodeError
        NodeWarning = _HouNodeWarning
        NotAvailable = _HouNotAvailable
        ObjectWasDeleted = _HouObjectWasDeleted
        OperationFailed = _HouOperationFailed
        OperationInterrupted = _HouOperationInterrupted
        PermissionError = _HouPermissionError
        SystemExit = _HouSystemExit
        TypeError = _HouTypeError
        ValueError = _HouValueError

    yield HouExceptions


@pytest.fixture
def mock_hou_ui(mocker):
    """Mock the hou.ui module which isn't available when running tests via Hython."""
    mock_ui = mocker.MagicMock()

    hou.ui = mock_ui

    yield mock_ui

    del hou.ui


@pytest.fixture
def patch_hou(mocker):
    """Mock importing of the hou module.

    The mocked module is available via the 'hou' key.

    The original hou module is available via the 'original_hou' key.

    This is useful for dealing with tucked hou imports.

    """
    mock_hou = mocker.MagicMock()

    modules = {
        "hou": mock_hou,
        "original_hou": hou
    }

    mocker.patch.dict("sys.modules", modules)

    yield modules


@pytest.fixture
def patch_soho(mocker):
    """Mock importing of mantra/soho related modules.

    Available mocked modules are available via their original names from the fixture object.

    """
    mock_api = mocker.MagicMock()
    mock_hooks = mocker.MagicMock()
    mock_mantra = mocker.MagicMock()
    mock_settings = mocker.MagicMock()
    mock_soho = mocker.MagicMock()

    class MockSoho(object):
        IFDapi = mock_api
        IFDhooks = mock_hooks
        IFDsettings = mock_settings
        mantra = mock_mantra
        soho = mock_soho

    modules = {
        "IFDapi": mock_api,
        "IFDhooks": mock_hooks,
        "IFDsettings": mock_settings,
        "mantra": mock_mantra,
        "soho": mock_soho,
    }

    mocker.patch.dict("sys.modules", modules)

    yield MockSoho
