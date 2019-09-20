"""Test setup."""

# =============================================================================
# IMPORTS
# =============================================================================

# Third Party Imports
import pytest


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def patch_operation_logger(mocker):
    """Mock the log_filter_call logger."""
    mock_logger = mocker.patch("ht.pyfilter.operations.operation._logger", autospec=True)

    yield mock_logger
