"""UI testing fixtures"""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import sys

# Third Party Imports
import mock


# =============================================================================


# Mock nodegraph related imports for testing.
mock_nodegraphdisplay = mock.MagicMock()
mock_nodegraphutils = mock.MagicMock()

sys.modules["nodegraphdisplay"] = mock_nodegraphdisplay
sys.modules["nodegraphutils"] = mock_nodegraphutils
