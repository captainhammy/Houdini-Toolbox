"""Testing fixtures."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import os

# Third Party
import pytest

# Houdini
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
        names.append(f"{cls_name}_{test_name}")

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


@pytest.fixture(scope="module")
def load_module_test_file(request):
    """Load a test hip file with the same name as the running module.

    The file must be under a data/ directory which is a sibling of the test file.

    The fixture will clear the hip file after the tests are completed.

    """
    test_dir = request.fspath.dirpath()

    test_file_name = (
        os.path.splitext(os.path.basename(request.module.__file__))[0] + ".hip"
    )

    test_file_path = test_dir / "data" / test_file_name

    hou.hipFile.load(str(test_file_path), ignore_load_warnings=True)

    yield

    hou.hipFile.clear()


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
        raise RuntimeError(f"{test_node.path()} does not contain SOP nodes")

    return test_node.displayNode().geometry()


@pytest.fixture(scope="function")
def obj_test_geo_copy(obj_test_geo):
    """Fixture to get a writable copy of the display node geometry of a node in /obj matching the test."""
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
