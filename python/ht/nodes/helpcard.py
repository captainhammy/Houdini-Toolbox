"""Utilities for constructing a help card from a node."""

# =============================================================================
# IMPORTS
# =============================================================================

from future import standard_library
standard_library.install_aliases()

# Standard Library Imports
from collections import OrderedDict
import io
import os
import re
import yaml

# Third Party Imports
import jinja2

# Houdini Imports
import hou


# =============================================================================
# GLOBALS
# =============================================================================

_PATH = os.path.join(
    os.path.expandvars("$TOOLBOXDIR"), "resources", "help_template.yaml"
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


def _add_inputs(string_buf, node):
    """Create the INPUTS section.

    :param string_buf: The output buffer.
    :type string_buf: io.StringIO
    :param node: The source node.
    :type node: hou.Node
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


def _add_using_section(string_buf, node_type):
    """Create the 'Using' section.

    :param string_buf: The output buffer.
    :type string_buf: io.StringIO
    :param node_type: The source node type.
    :type node_type: hou.NodeType
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


def _add_folder_help(parm_template, items, in_multiparm=False):
    """Build a help item for a folder parameter.

    :param parm_template: The source parameter template.
    :type parm_template: hou.FolderParmTemplate
    :param items: A list of help items.
    :type items: OrderedDict or list
    :param in_multiparm: Whether or not the template is inside a multiparm
    :type in_multiparm: bool
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

    if isinstance(items, OrderedDict):
        items[result] = folder_items

    else:
        dict_items = OrderedDict({result: folder_items})

        items.append(dict_items)


def _add_help_for_parameter(parm_template, items, in_multiparm=False):
    """Build a help item for a parameter.

    :param parm_template: The source parameter template.
    :type parm_template: hou.ParmTemplate
    :param items: A list of help items.
    :type items: list
    :param in_multiparm: Whether or not the template is inside a multiparm
    :type in_multiparm: bool
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

        menu_dict = OrderedDict({parm_help: menu_help})

        items.append(menu_dict)

    else:
        items.append(parm_help)


def _add_parameters_section(string_buf, node_type):
    """Add a parameters section to the buffer.

    :param string_buf: The output buffer.
    :type string_buf: io.StringIO
    :param node_type: The source node type.
    :type node_type: hou.NodeType
    :return:

    """
    string_buf.write("@parameters\n")

    parameter_items = []

    _process_parm_templates(
        parameter_items, node_type.parmTemplateGroup().parmTemplates()
    )

    # Convert the items to strings and add them to the buffer.
    _get_help_text(string_buf, parameter_items, 0)


def _create_header(string_buf, node_type):
    """Create the header sections.

    :param string_buf: The output buffer.
    :type string_buf: io.StringIO
    :param node_type: The source node type.
    :type node_type: hou.NodeType
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


def _get_template(key, in_multiparm=False):
    """Get the template for a particular key.

    If a template will be for a parameter inside a multiparm, any '#id:' entries will
    be removed since they will cause problems.

    :param key: The output key.
    :type key: str
    :param in_multiparm: Whether or not the template is inside a multiparm
    :type in_multiparm: bool
    :return: The help template.
    :rtype: jinja2.Template

    """
    raw_data = _TEMPLATES[key]

    if in_multiparm:
        raw_data = re.sub("([ ]+#id:.+\\n)", "", raw_data)

    template = jinja2.Template(raw_data)

    return template


def _get_help_text(string_buf, items, indent):
    """Add items to the output.

    :param string_buf: The output buffer.
    :type string_buf: io.StringIO
    :param items: Help items or strings.
    :type items: list or OrderedDict or str
    :param indent: The indentation level.
    :type indent: int
    :return:

    """
    if isinstance(items, OrderedDict):
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


def _process_parm_templates(items, templates, in_multiparm=False):
    """Process parameter templates.

    :param items: A list of help items.
    :type items: list
    :param templates: The parameter templates to process.
    :type templates: tuple(hou.ParmTemplate)
    :param in_multiparm: Whether or not the templates are inside a multiparm.
    :type in_multiparm: bool
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


def _resolve_icon(icon, node_type):
    """Try to resolve a node type's icon to a help server friendly format.

    This function will attempt to handle the following cases:

    - If the icon() value is an opdef value, replace the fully qualified name with '.'
    - If the icon() value is a Houdini style icon ({CONTEXT}_{name}), convert to {CONTEXT}/{name}

    :param icon: The icon name.
    :type icon: str
    :param node_type: A node type to help resolve the icon.
    :type node_type: hou.NodeType
    :return: An icon value.
    :rtype: str

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


def generate_help_card(node, inputs=False, related=False, using=False):
    """Generate help card text for a node.

    :param node: The source node.
    :type node: hou.Node
    :param inputs: Whether or not to include an 'Inputs' section.
    :type inputs: bool
    :param related: Whether or not to include a 'See also' section.
    :type related: bool
    :param using: Whether or not to create a 'Using ...' section.
    :type using: bool
    :return: The generated help card text.
    :rtype: str

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
