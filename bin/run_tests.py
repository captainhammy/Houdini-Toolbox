"""Discover and run unittests, with coverage."""

import coverage
import unittest

# Start the coverage reporting.
cov = coverage.Coverage()
cov.start()

# Find and run tests
loader = unittest.TestLoader()
suite = loader.discover(".")
runner = unittest.TextTestRunner()
runner.run(suite)

# Stop the coverage operation, generate reports.
cov.stop()
cov.save()
cov.html_report()
cov.xml_report()

