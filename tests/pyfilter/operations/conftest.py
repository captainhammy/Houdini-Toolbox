"""Test setup."""

# =============================================================================
# IMPORTS
# =============================================================================

# Third Party Imports
from mock import patch
import pytest


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def patch_operation_logger():
    """Mock the log_filter_call logger."""
    with patch("ht.pyfilter.operations.operation._logger", autospec=True) as mock_logger:
        yield mock_logger
