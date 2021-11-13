"""Test setup."""

# =============================================================================
# IMPORTS
# =============================================================================

# Third Party
import pytest

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def patch_operation_logger(mocker):
    """Mock the log_filter_call logger."""
    mock_logger = mocker.patch(
        "houdini_toolbox.pyfilter.operations.operation._logger", autospec=True
    )

    yield mock_logger
