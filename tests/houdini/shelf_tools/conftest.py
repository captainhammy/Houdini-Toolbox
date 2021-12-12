"""Testing fixtures."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import os
from xml.etree import ElementTree

# Third Party
import pytest


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def exec_tool_script():
    """Fixture to execute a tool inside an xml .shelf file."""

    def _exec(file_name: str, tool_name: str, kwargs: dict):
        """Execute tool code inside a file.

        :param file_name: The name of the .shelf file to execute.
        :param tool_name: The name of the tool to execute.
        :param kwargs: The global 'kwargs' dict for the tool execution.
        :return:

        """
        # Find the file to execute.
        path = os.path.join(os.environ["TOOLBAR_PATH"], file_name)

        # Fail if we can't find it.
        if not os.path.exists(path):
            raise OSError(f"Could not find file {path}")

        # Read the file and find all the tools.
        tree = ElementTree.parse(path)
        root = tree.getroot()
        tools = root.findall("tool")

        # Look for the specified tool.
        for tool in tools:
            if tool.get("name") == tool_name:
                script = tool.find("script")

                # Read the contents and break.
                contents = script.text
                break

        # We didn't find the target tool in the file so fail.
        else:
            raise RuntimeError(f"Could not find tool {tool_name}")

        temp_path = os.path.join("/var/tmp/", file_name)

        with open(temp_path, "w", encoding="utf-8") as handle:
            handle.writelines(contents)

        exec(contents, {"kwargs": kwargs})  # pylint: disable=exec-used

    return _exec
