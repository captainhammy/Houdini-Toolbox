"""This module contains a class for managing and running PyFilter filter
actions.

"""
# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import argparse
import json

# Houdini Toolbox Imports
from ht.pyfilter.logger import logger

# =============================================================================
# CLASSES
# =============================================================================

class PyFilterManager(object):
    """Manager class for PyFilter operations."""

    def __init__(self):
        self._data = {}
        self._operations = []

        # Populate the list of operations.
        self._register_operations()

        # Build and parse any arguments.
        filter_args = self._get_parsed_args()

        self._process_parsed_args(filter_args)

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def data(self):
        """dict: Data dictionary that can be used to pass information."""
        return self._data

    @property
    def operations(self):
        """list: A list of registered operations."""
        return self._operations

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _get_parsed_args(self):
        """Parse any args passed to PyFilter."""
        parser = _build_parser()

        self._register_parser_args(parser)

        filter_args = parser.parse_known_args()[0]

        return filter_args

    def _process_parsed_args(self, filter_args):
        """Allow operations to process any args that were parsed."""
        for operation in self.operations:
            operation.process_parsed_args(filter_args)

    def _register_operations(self):
        """Register operations that should be run by the manager."""
        files = _find_operation_files()

        for filepath in files:
            data = _get_operation_data(filepath)

            if "operations" not in data:
                continue

            for operation in data["operations"]:
                module_name, class_name = operation

                # Import the operation class.
                cls = _get_class(module_name, class_name)

                logger.debug(
                    "Registering {} ({})".format(
                        class_name,
                        module_name
                    )
                )

                # Add an instance of it to our operations list.
                self.operations.append(cls(self))

    def _register_parser_args(self, parser):
        """Register any necessary args with our parser.

        This allows filter operations to have their necessary args parsed and
        available.

        """
        for operation in self.operations:
            operation.register_parser_args(parser)

    # =========================================================================
    # METHODS
    # =========================================================================

    def run_operations_for_stage(self, stage, *args, **kwargs):
        """Run all filter operations for the specified stage."""
        results = []

        for operation in self.operations:
            # Skip operations that should not be run.
            if not operation.should_run():
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

# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

def _build_parser():
    """Build a default parser to be used."""
    parser = argparse.ArgumentParser()

    return parser


def _find_operation_files():
    """Find any operation loading files."""
    import hou

    # Look for files containing a list of operations.
    try:
        files = hou.findFiles("pyfilter/operations.json")

    # If no files could be found then abort.
    except hou.OperationFailed:
        logger.debug("Could not find any operations to load")
        files = ()

    return files


def _get_class(module_name, class_name):
    """Try to import class_name from module_name."""
    try:
        cls = getattr(
            __import__(module_name, {}, {}, [class_name]),
            class_name
        )

    except ImportError:
        cls = None

    return cls


def _get_operation_data(file_path):
    """Get operation data from a file path."""
    try:
        with open(file_path) as fp:
            data = json.load(fp)

    except (IOError, ValueError) as inst:
        logger.error("Error loading operation data from {}".format(file_path))
        logger.exception(inst)

        data = {}

    return data
