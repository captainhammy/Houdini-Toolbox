"""This module contains a class for managing and running PyFilter filter
actions.

"""
# =============================================================================
# IMPORTS
# =============================================================================

from __future__ import annotations

# Standard Library
import argparse
import importlib
import json
import logging
from typing import TYPE_CHECKING, List, Optional, Tuple, Type

if TYPE_CHECKING:
    from houdini_toolbox.pyfilter.operations.operation import PyFilterOperation

_logger = logging.getLogger(__name__)


# =============================================================================
# CLASSES
# =============================================================================


class PyFilterManager:
    """Manager class for PyFilter operations."""

    def __init__(self):
        self._data = {}
        self._operations = []

        # Populate the list of operations.
        self._register_operations()

        # Build and parse any arguments.
        filter_args = self._get_parsed_args()

        self._process_parsed_args(filter_args)

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def data(self) -> dict:
        """Data dictionary that can be used to pass information."""
        return self._data

    @property
    def operations(self) -> List[PyFilterOperation]:
        """A list of registered operations."""
        return self._operations

    # -------------------------------------------------------------------------
    # NON-PUBLIC METHODS
    # -------------------------------------------------------------------------

    def _get_parsed_args(self) -> argparse.Namespace:
        """Parse any args passed to PyFilter.

        :return: Parsed filter args.

        """
        parser = _build_parser()

        self._register_parser_args(parser)

        filter_args = parser.parse_known_args()[0]

        return filter_args

    def _process_parsed_args(self, filter_args: argparse.Namespace):
        """Allow operations to process any args that were parsed.

        :param filter_args: The args passed to the filter command.
        :return:

        """
        for operation in self.operations:
            operation.process_parsed_args(filter_args)

    def _register_operations(self):
        """Register operations that should be run by the manager.

        :return:

        """
        files = _find_operation_files()

        for file_path in files:
            data = _get_operation_data(file_path)

            if "operations" not in data:
                continue

            for operation in data["operations"]:
                module_name, class_name = operation

                # Import the operation class.
                cls = _get_class(module_name, class_name)

                if cls is None:
                    _logger.warning(
                        "Could not load %s from %s", class_name, module_name
                    )

                    continue

                _logger.debug("Registering %s (%s)", class_name, module_name)

                # Add an instance of it to our operations list.
                self.operations.append(cls(self))

    def _register_parser_args(self, parser: argparse.ArgumentParser):
        """Register any necessary args with our parser.

        This allows filter operations to have their necessary args parsed and
        available.

        :param parser: The argument parser to register args to.
        :return:

        """
        for operation in self.operations:
            operation.register_parser_args(parser)

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def run_operations_for_stage(self, stage_name: str, *args, **kwargs) -> bool:
        """Run all filter operations for the specified stage.

        :param stage_name: The name of the stage to run.
        :param args: Positional arguments passed to the stage function.
        :param kwargs: Keyword args passed to the stage function.
        :return: Whether or any of the stage functions returned True.

        """
        results = []

        for operation in self.operations:
            # Skip operations that should not be run.
            if not operation.should_run():
                continue

            # Attempt to find the function for this stage.
            try:
                func = getattr(operation, stage_name)

            # Filter has no function for this stage so don't do anything.
            except AttributeError:
                continue

            # Run the filter.
            results.append(func(*args, **kwargs))

        return True in results


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _build_parser() -> argparse.ArgumentParser:
    """Build a default parser to be used.

    :return: The argument parser to use.

    """
    parser = argparse.ArgumentParser()

    return parser


def _find_operation_files() -> Tuple[str]:
    """Find any operation loading files.

    :return: Any found operations files.

    """
    import hou

    # Look for files containing a list of operations.
    try:
        files = hou.findFiles("pyfilter/operations.json")

    # If no files could be found then abort.
    except hou.OperationFailed:
        _logger.debug("Could not find any operations to load")
        files = ()

    return files


def _get_class(module_name: str, class_name: str) -> Optional[Type]:
    """Try to import class_name from module_name.

    :param module_name: The name of the module containing the class.
    :param class_name: The name of the class to get.
    :return: A found class, otherwise None.

    """

    try:
        module = importlib.import_module(module_name)

    except ImportError:
        cls = None

    else:
        cls = getattr(module, class_name, None)

    return cls


def _get_operation_data(file_path: str) -> dict:
    """Get operation data from a file path.

    :param file_path: The path to an operation file.
    :return: Operation data.

    """
    try:
        with open(file_path, encoding="utf-8") as handle:
            data = json.load(handle)

    except (IOError, ValueError) as inst:
        _logger.error("Error loading operation data from %s", file_path)
        _logger.exception(inst)

        data = {}

    return data
