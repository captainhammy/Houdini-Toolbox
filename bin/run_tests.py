"""Discover and run unittests, with coverage."""

import coverage
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

if not result.wasSuccessful():
    sys.exit(1)

