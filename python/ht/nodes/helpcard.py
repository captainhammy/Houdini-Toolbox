"""Utilities for constructing a help card from a node."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import collections.abc
import io
import os
import re
from typing import List, OrderedDict, Tuple, Union
import yaml

# Third Party Imports
import jinja2

# Houdini Imports
import hou


# =============================================================================
# GLOBALS
# =============================================================================

_PATH = os.path.join(
    os.path.expandvars("$HOUDINI_TOOLBOX_DIR"), "resources", "help_template.yaml"
)

with open(_PATH) as handle:
    _TEMPLATES = yaml.safe_load(handle)

# Parameter templates which are multiparms.
_MULTIPARM_TYPES = (
    hou.folderType.MultiparmBlock,
    hou.folderType.ScrollingMultiparmBlock,
    hou.folderType.TabbedMultiparmBlock,
)

# Parameter types to ignore.
_TEMPLATES_TO_IGNORE = (hou.SeparatorParmTemplate, hou.LabelParmTemplate)


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _add_inputs(string_buf: io.StringIO, node: hou.Node):
    """Create the INPUTS section.

    :param string_buf: The output buffer.
    :param node: The source node.
    :return:

    """
    # For some reason you have to get the input labels from the node itself
    # instead of the type or definition.
    labels = node.inputLabels()

    if labels:
        string_buf.write("@inputs\n")

        input_template = _get_template("input_template")

        for label in labels:
            string_buf.write(input_template.render({"label": label}))

            string_buf.write("\n\n")


def _add_using_section(string_buf: io.StringIO, node_type: hou.NodeType):
    """Create the 'Using' section.

    :param string_buf: The output buffer.
    :param node_type: The source node type.
    :return:

    """
    template = _get_template("using_template")

    icon = None

    tool_tab = None

    tool_name = hou.shelves.defaultToolName(
        node_type.category().name(), node_type.name()
    )
    tool = hou.shelves.tool(tool_name)

    if tool is not None:
        icon = _resolve_icon(tool.icon(), node_type)

        for shelf in list(hou.shelves.shelves().values()):
            if tool in shelf.tools():
                tool_tab = shelf.label()

                break

    string_buf.write(
        template.render(
            {"label": node_type.description(), "icon": icon, "tool_tab": tool_tab}
        )
    )

    string_buf.write("\n\n")


def _add_folder_help(
    parm_template: hou.FolderParmTemplate,
    items: Union[List, OrderedDict],
    in_multiparm: bool = False,
):
    """Build a help item for a folder parameter.

    :param parm_template: The source parameter template.
    :param items: A list of help items.
    :param in_multiparm: Whether or not the template is inside a multiparm
    :return:

    """
    template = _get_template("folder_template", in_multiparm)

    result = template.render({"label": parm_template.label()})

    folder_items = []

    if parm_template.folderType() in _MULTIPARM_TYPES:
        in_multiparm = True

    _process_parm_templates(
        folder_items, parm_template.parmTemplates(), in_multiparm=in_multiparm
    )

    if isinstance(items, collections.OrderedDict):
        items[result] = folder_items

    else:
        dict_items = collections.OrderedDict({result: folder_items})

        items.append(dict_items)


def _add_help_for_parameter(
    parm_template: hou.ParmTemplate,
    items: Union[List, OrderedDict],
    in_multiparm: bool = False,
):
    """Build a help item for a parameter.

    :param parm_template: The source parameter template.
    :param items: A list of help items.
    :param in_multiparm: Whether or not the template is inside a multiparm
    :return:

    """
    args = {"label": parm_template.label(), "id": parm_template.name()}

    template = _get_template("parameter_template", in_multiparm)

    if parm_template.help():
        args["help"] = parm_template.help()

    parm_help = template.render(**args)

    if isinstance(parm_template, hou.MenuParmTemplate):
        menu_item_template = _get_template("menu_item_template", in_multiparm)

        menu_help = []

        for label in parm_template.menuLabels():
            menu_help.append(menu_item_template.render(item=label))

        menu_dict = collections.OrderedDict({parm_help: menu_help})

        items.append(menu_dict)

    else:
        items.append(parm_help)


def _add_parameters_section(string_buf: io.StringIO, node_type: hou.NodeType):
    """Add a parameters section to the buffer.

    :param string_buf: The output buffer.
    :param node_type: The source node type.
    :return:

    """
    string_buf.write("@parameters\n")

    parameter_items = []

    _process_parm_templates(
        parameter_items, node_type.parmTemplateGroup().parmTemplates()
    )

    # Convert the items to strings and add them to the buffer.
    _get_help_text(string_buf, parameter_items, 0)


def _create_header(string_buf: io.StringIO, node_type: hou.NodeType):
    """Create the header sections.

    :param string_buf: The output buffer.
    :param node_type: The source node type.
    :return:

    """
    internal = _get_template("internal_header_template")

    string_buf.write(
        internal.render(
            {
                "context": node_type.category().name(),
                "internal": node_type.name(),
                "icon": _resolve_icon(node_type.icon(), node_type),
            }
        )
    )

    string_buf.write("\n\n")

    header = _get_template("header_template")

    string_buf.write(header.render({"label": node_type.description()}))

    string_buf.write("\n\n")


def _get_template(key: str, in_multiparm: bool = False) -> jinja2.Template:
    """Get the template for a particular key.

    If a template will be for a parameter inside a multiparm, any '#id:' entries will
    be removed since they will cause problems.

    :param key: The output key.
    :param in_multiparm: Whether or not the template is inside a multiparm
    :return: The help template.

    """
    raw_data = _TEMPLATES[key]

    if in_multiparm:
        raw_data = re.sub("([ ]+#id:.+\\n)", "", raw_data)

    template = jinja2.Template(raw_data)

    return template


def _get_help_text(
    string_buf: io.StringIO, items: Union[List, OrderedDict, str], indent: int
):
    """Add items to the output.

    :param string_buf: The output buffer.
    :param items: Help items or strings.
    :param indent: The indentation level.
    :return:

    """
    if isinstance(items, collections.OrderedDict):
        for key, value in list(items.items()):
            for line in key.split("\n"):
                string_buf.write("{}{}\n".format("    " * indent, line))

            string_buf.write("\n")

            _get_help_text(string_buf, value, indent + 1)

    elif isinstance(items, list):
        for value in items:
            _get_help_text(string_buf, value, indent)

    else:
        for line in items.split("\n"):
            string_buf.write("{}{}\n".format("    " * indent, line))

        string_buf.write("\n")


def _process_parm_templates(
    items: Union[List, OrderedDict],
    templates: Tuple[hou.ParmTemplate],
    in_multiparm: bool = False,
):
    """Process parameter templates.

    :param items: A list of help items.
    :param templates: The parameter templates to process.
    :param in_multiparm: Whether or not the templates are inside a multiparm.
    :return:

    """
    for parm_template in templates:
        if parm_template.isHidden():
            continue

        if isinstance(parm_template, _TEMPLATES_TO_IGNORE):
            continue

        if not isinstance(
            parm_template, (hou.FolderParmTemplate, hou.FolderSetParmTemplate)
        ):
            _add_help_for_parameter(parm_template, items, in_multiparm)

        else:
            _add_folder_help(parm_template, items, in_multiparm)


def _resolve_icon(icon: str, node_type: hou.NodeType) -> str:
    """Try to resolve a node type's icon to a help server friendly format.

    This function will attempt to handle the following cases:

    - If the icon() value is an opdef value, replace the fully qualified name with '.'
    - If the icon() value is a Houdini style icon ({CONTEXT}_{name}), convert to {CONTEXT}/{name}

    :param icon: The icon name.
    :param node_type: A node type to help resolve the icon.
    :return: An icon value.

    """
    if icon.startswith("opdef:/{}".format(node_type.nameWithCategory())):
        icon = icon.replace("/{}".format(node_type.nameWithCategory()), ".")

    result = re.match("([A-Z]+)_([a-z_]+)", icon)

    if result is not None:
        icon = "{}/{}".format(result.group(1), result.group(2))

    return icon


# =============================================================================
# FUNCTIONS
# =============================================================================


def generate_help_card(
    node: hou.Node, inputs: bool = False, related: bool = False, using: bool = False
) -> str:
    """Generate help card text for a node.

    :param node: The source node.
    :param inputs: Whether or not to include an 'Inputs' section.
    :param related: Whether or not to include a 'See also' section.
    :param using: Whether or not to create a 'Using ...' section.
    :return: The generated help card text.

    """
    node_type = node.type()

    # Use a StringIO object for generating all the text.
    string_buf = io.StringIO()

    # Construct the internal and main header.
    _create_header(string_buf, node_type)

    # Add the Using section if necessary.
    if using:
        _add_using_section(string_buf, node_type)

    _add_parameters_section(string_buf, node_type)

    # Add inputs section if necessary.
    if inputs:
        _add_inputs(string_buf, node)

    # Add related section if necessary.
    if related:
        related_template = _get_template("related_template")

        string_buf.write(related_template.render({}))

    # Get the resulting help text before closing the buffer.
    help_text = string_buf.getvalue()

    string_buf.close()

    return help_text
