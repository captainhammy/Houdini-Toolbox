"""Discover and run unittests, with coverage."""


# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import os
import unittest

# Third Party Imports
import coverage
import six

# Houdini Imports
import hou

# Start the coverage reporting.
cov = coverage.Coverage()
cov.start()

# Find and run tests
loader = unittest.TestLoader()
suite = loader.discover(".")
runner = unittest.TextTestRunner()
result = runner.run(suite)

# Stop the coverage operation, generate reports.
cov.stop()
cov.save()
cov.html_report()
cov.xml_report()

html_path = os.path.join(os.path.realpath(os.path.curdir), "coverage_html_report/index.html")
six.print_("View coverage report at file://{}".format(html_path))

if not result.wasSuccessful():
    hou.exit(1)
