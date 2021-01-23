"""Testing fixtures."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import os
import sys
from xml.etree import ElementTree

# Third Party Imports
import pytest

# Houdini Imports
import hou


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _find_matching_node(parent, request):
    """Try to find a matching child node based on a test request.

    Node search order is as follows:
    - Node matching the exact test name
    - Node matching the class name + test name (minus 'test_' prefix for function name)
    - Node matching the class name

    """
    test_name = request.node.name

    # First try to find a node with the exact test name.
    names = [test_name]

    if request.cls is not None:
        cls_name = request.cls.__name__.lower()

        test_name = test_name[5:]

        # Look for a node with the class name + test name (minus test_ from function name)
        names.append("{}_{}".format(cls_name, test_name))

        # Finally try to find a node with the class name.
        names.append(cls_name)

    node = None

    for name in names:
        node = parent.node(name)

        if node is not None:
            break

    return node


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def exec_tool_script():
    """Fixture to execute a tool inside an xml .shelf file."""

    def _exec(file_name, tool_name, kwargs):
        """Execute tool code inside a file.

        :param file_name: The name of the .shelf file to execute.
        :type file_name: str
        :param tool_name: The name of the tool to execute.
        :type tool_name: str
        :param kwargs: The global 'kwargs' dict for the tool execution.
        :type kwargs: dict
        :return:

        """
        # Find the file to execute.
        path = os.path.join(os.environ["TOOLBAR_PATH"], file_name)

        # Fail if we can't find it.
        if not os.path.exists(path):
            raise OSError("Could not find file {}".format(path))

        # Read the file and find all the tools.
        tree = ElementTree.parse(path)
        root = tree.getroot()
        tools = root.findall("tool")

        # Look for the specified tool.
        for tool in tools:
            if tool.get("name") == tool_name:
                script = tool.find("script")

                # Read the contents and break.
                contents = script.text
                break

        # We didn't find the target tool in the file so fail.
        else:
            raise RuntimeError("Could not find tool {}".format(tool_name))

        temp_path = os.path.join("/var/tmp/", file_name)

        with open(temp_path, "w") as handle:
            handle.writelines(contents)

        #execfile(temp_path,  {"kwargs": kwargs})

        exec(contents, {"kwargs": kwargs})

    return _exec


@pytest.fixture
def fix_hou_exceptions(monkeypatch):
    """Fixture to support dealing with hou.Error exceptions.

    Since hou.Error and all derived exceptions are not actual Exception objects
    pytest will not like this.  If your code throws an uncaught exception it will
    confuse pytest and it will basically error, but not error.  The test execution
    will halt but your test will not fail.

    This fixture gets around this by patching all the hou.Error related exceptions
    with exceptions derived from Exception and the allowing you to catch those.
    When dealing testing code which involves hou exceptions you should include this
    fixture.

    def foo():
        raise hou.OperationFailed()

    def test_foo(fix_hou_exceptions):
        with pytest.raises(hou.OperationFailed):
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

    if sys.version_info.major == 2:
        monkeypatch.setattr(hou, "Error", _HouError)
        monkeypatch.setattr(hou, "GeometryPermissionError", _HouGeometryPermissionError)
        monkeypatch.setattr(hou, "InitScriptFailed", _HouInitScriptFailed)
        monkeypatch.setattr(hou, "InvalidInput", _HouInvalidInput)
        monkeypatch.setattr(hou, "InvalidNodeType", _HouInvalidNodeType)
        monkeypatch.setattr(hou, "InvalidSize", _HouInvalidSize)
        monkeypatch.setattr(hou, "KeyframeValueNotSet", _HouKeyframeValueNotSet)
        monkeypatch.setattr(hou, "LoadWarning", _HouLoadWarning)
        monkeypatch.setattr(hou, "MatchDefinitionError", _HouMatchDefinitionError)
        monkeypatch.setattr(hou, "NodeError", _HouNodeError)
        monkeypatch.setattr(hou, "NodeWarning", _HouNodeWarning)
        monkeypatch.setattr(hou, "NotAvailable", _HouNotAvailable)
        monkeypatch.setattr(hou, "ObjectWasDeleted", _HouObjectWasDeleted)
        monkeypatch.setattr(hou, "OperationFailed", _HouOperationFailed)
        monkeypatch.setattr(hou, "OperationInterrupted", _HouOperationInterrupted)
        monkeypatch.setattr(hou, "PermissionError", _HouPermissionError)
        monkeypatch.setattr(hou, "SystemExit", _HouSystemExit)
        monkeypatch.setattr(hou, "TypeError", _HouTypeError)
        monkeypatch.setattr(hou, "ValueError", _HouValueError)

        # Support for any exceptions added in newer versions of Houdini.
        if hou.applicationVersion() > (17,):
            monkeypatch.setattr(hou, "NameConflict", _HouNameConflict)


@pytest.fixture
def mock_hdefereval(mocker):
    """Mock hdefereval which isn't available when running tests via Hython."""
    mocked_hdefereval = mocker.MagicMock()

    # Need to mock importing hdefereval because the import will fail when
    # the UI is not available (like in testing).
    modules = {"hdefereval": mocked_hdefereval}

    mocker.patch.dict("sys.modules", modules)

    yield mocked_hdefereval


@pytest.fixture
def mock_hou_qt(mocker):
    """Mock the hou.qt module which isn't available when running tests via Hython."""
    mock_qt = mocker.MagicMock()

    hou.qt = mock_qt

    yield mock_qt

    del hou.qt


@pytest.fixture
def mock_hou_ui(mocker, mock_ui_available):
    """Mock the hou.ui module which isn't available when running tests via Hython.

    This fixture will also mock hou.isUIAvailable() to return True.

    """
    mock_ui = mocker.MagicMock()

    hou.ui = mock_ui

    yield mock_ui

    del hou.ui


@pytest.fixture
def mock_ui_available(mocker):
    """Fixture to mock hou.isUIAvailable() to return True."""
    yield mocker.patch("hou.isUIAvailable", return_value=True)


@pytest.fixture
def mock_ui_unavailable(mocker):
    """Fixture to mock hou.isUIAvailable() to return False."""
    yield mocker.patch("hou.isUIAvailable", return_value=False)


@pytest.fixture(scope="function")
def obj_test_node(request):
    """Fixture to provide a node in /obj matching the test."""
    parent = hou.node("/obj")

    return _find_matching_node(parent, request)


@pytest.fixture(scope="function")
def obj_test_geo(request):
    """Fixture to provide the display node geometry of a node in /obj matching the test."""
    parent = hou.node("/obj")

    test_node = _find_matching_node(parent, request)

    if test_node is None:
        return None

    if test_node.childTypeCategory() != hou.sopNodeTypeCategory():
        raise RuntimeError("{} does not contain SOP nodes".format(test_node.path()))

    return test_node.displayNode().geometry()


@pytest.fixture(scope="function")
def obj_test_geo_copy(obj_test_geo):
    """Fixture to get a writable copy of the display node geometry of a ndoe in /obj matching the test."""
    geo = hou.Geometry()

    geo.merge(obj_test_geo)

    return geo


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

    class MockSoho:
        """Mock object for accessing patched mantra/SOHO modules."""
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
