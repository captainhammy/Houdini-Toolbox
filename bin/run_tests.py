"""Discover and run unittests, with coverage."""

import coverage
import os
import six
import sys
import unittest

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
    sys.exit(1)

