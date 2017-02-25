"""This module contains a class for managing and running PyFilter filter
actions.

"""
# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import argparse
import logging
import json

# Houdini Toolbox Imports
from ht.pyfilter.logger import logger

import ht.utils

# =============================================================================
# CLASSES
# =============================================================================

class PyFilterManager(object):
    """Manager class for PyFilter operations."""

    def __init__(self):
        self._data = {}
        self._operations = []

        # Populate the list of operations.
        self._registerOperations()

        # Build and parse any arguments.
        self._parsePyFilterArgs()

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def data(self):
        """Data dictionary that can be used to pass information."""
        return self._data

    @property
    def operations(self):
        """A list of registered operations."""
        return self._operations

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _parsePyFilterArgs(self):
        """Parse any args passed to PyFilter."""
        parser = argparse.ArgumentParser()

        self._registerParserArgs(parser)

        filter_args = parser.parse_known_args()[0]

        self._processParsedArgs(filter_args)

    def _processParsedArgs(self, filter_args):
        """Allow operations to process any args that were parsed."""
        for operation in self.operations:
            operation.processParsedArgs(filter_args)

    def _registerOperations(self):
        """Register operations that should be run by the manager."""
        import hou

        # Look for files containing a list of operations.
        try:
            files = hou.findFiles("pyfilter/operations.json")

        # If no files could be found then abort.
        except hou.OperationFailed:
            return

        for filepath in files:
            with open(filepath) as fp:
                data = json.load(fp, object_hook=ht.utils.convertFromUnicode)

            if "operations" not in data:
                continue

            for operation in data["operations"]:
                module_name, class_name = operation

                # Import the operation class.
                cls = getattr(
                    __import__(module_name, {}, {}, [class_name]),
                    class_name
                )

                logger.debug("Registering {}".format(class_name))

                # Add an instance of it to our operations list.
                self.operations.append(cls(self))

    def _registerParserArgs(self, parser):
        """Register any necessary args with our parser.

        This allows filter operations to have their necessary args parsed and
        available.

        """
        for operation in self.operations:
            operation.registerParserArgs(parser)

    # =========================================================================
    # METHODS
    # =========================================================================

    def runFilters(self, stage, *args, **kwargs):
        """Run all filter operations for the specified stage."""
        results = []

        for operation in self.operations:
            # Skip operations that should not be run.
            if not operation.shouldRun():
                continue

            # Attempt to find the function for this stage.
            try:
                func = getattr(operation, stage)

            # Filter has no function for this stage so don't do anything.
            except AttributeError:
                continue

            # Run the filter.
            results.append(func(*args, **kwargs))

        return True in results

