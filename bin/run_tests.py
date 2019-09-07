"""Discover and run unittests, with coverage."""


# =============================================================================
# IMPORTS
# =============================================================================

# Third Party Imports
import pytest

# Houdini Imports
import hou

# =============================================================================

result = pytest.main()

if not result:
    hou.exit(result)
