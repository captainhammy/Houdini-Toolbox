"""This module contains support functions for AOVs."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import os
import pickle

# Third Party Imports
from PySide2 import QtCore, QtGui

# Houdini Toolbox Imports
from ht.sohohooks.aovs.aov import ALLOWABLE_VALUES
from ht.sohohooks.aovs.aov import AOV, AOVGroup, IntrinsicAOVGroup
from ht.sohohooks.aovs import sources
from ht.ui.aovs import uidata

# Houdini Imports
import hou

# =============================================================================
# GLOBALS
# =============================================================================

# Mime data type name for AOV related data.
_AOV_MIME_TYPE = "application/houdini-ht.aov"


# =============================================================================
# CLASSES
# =============================================================================

class AOVViewerInterface(QtCore.QObject):
    """This class acts as an interface between viewer related UI elements
    and the AOVManager.

    """

    # Signals for when AOVs are created or changed.
    aov_added_signal = QtCore.Signal(AOV)
    aov_removed_signal = QtCore.Signal(AOV)
    aov_updated_signal = QtCore.Signal(AOV)

    # Signals for when AOVGroups are created or changed.
    group_added_signal = QtCore.Signal(AOVGroup)
    group_removed_signal = QtCore.Signal(AOVGroup)
    group_updated_signal = QtCore.Signal(AOVGroup)


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

def _get_item_menu_index(items, item):
    """Function to determine which index an item represents."""
    idx = 0

    for itm in items:
        if item == itm[0]:
            return idx

        idx += 1

    return 0


# =============================================================================
# FUNCTIONS
# =============================================================================

def apply_elements_as_parms(elements, nodes):
    """Apply a list of elements are multiparms."""
    aovs = flatten_element_list(elements)

    for node in nodes:
        apply_to_node_as_parms(node, aovs)


def apply_elements_as_string(elements, nodes):
    """Apply a list of elements at render time."""
    value = element_list_as_string(elements)

    for node in nodes:
        # Need to add the automatic aov parameters if they doesn't exist.
        if node.parm("auto_aovs") is None:
            # Add the parameters from the .ds file.
            hou.hscript(
                'opproperty -f -F "Extra Image Planes" {} ht_parms ht_automatic_aovs'.format(
                    node.path()
                )
            )

        parm = node.parm("auto_aovs")
        parm.set(value)

        if node.parm("enable_auto_aovs") is not None:
            node.parm("enable_auto_aovs").set(True)


def apply_to_node_as_parms(node, aovs):
    """Apply a list of AOVs to a Mantra node using multiparm entries."""
    num_aovs = len(aovs)

    node.parm("vm_numaux").set(num_aovs)

    for idx, aov in enumerate(aovs, 1):
        node.parm("vm_variable_plane{}".format(idx)).set(aov.variable)
        node.parm("vm_vextype_plane{}".format(idx)).set(aov.vextype)

        if aov.channel is not None and aov.channel != aov.variable:
            node.parm("vm_channel_plane{}".format(idx)).set(aov.channel)

        if aov.planefile is not None:
            node.parm("vm_usefile_plane{}".format(idx)).set(True)
            node.parm("vm_filename_plane{}".format(idx)).set(aov.planefile)

        if aov.quantize is not None:
            node.parm("vm_quantize_plane{}".format(idx)).set(aov.quantize)

        if aov.sfilter is not None:
            node.parm("vm_sfilter_plane{}".format(idx)).set(aov.sfilter)

        if aov.pfilter is not None:
            node.parm("vm_pfilter_plane{}".format(idx)).set(aov.pfilter)

        if aov.componentexport:
            node.parm("vm_componentexport{}".format(idx)).set(True)

        if aov.lightexport is not None:
            menu_idx = ALLOWABLE_VALUES["lightexport"].index(aov.lightexport)
            node.parm("vm_lightexport{}".format(idx)).set(menu_idx)
            node.parm("vm_lightexport_scope{}".format(idx)).set(aov.lightexport_scope)
            node.parm("vm_lightexport_select{}".format(idx)).set(aov.lightexport_select)


def build_aovs_from_multiparm(node):
    """Build a list of AOVs from a Mantra node's multiparm."""
    aovs = []

    num_aovs = node.evalParm("vm_numaux")

    for idx in range(1, num_aovs+1):
        aov_data = {
            "variable": node.evalParm("vm_variable_plane{}".format(idx)),
            "vextype": node.evalParm("vm_vextype_plane{}".format(idx))
        }

        channel = node.evalParm("vm_channel_plane{}".format(idx))
        if channel:
            aov_data["channel"] = channel

        aov_data["quantize"] = node.evalParm("vm_quantize_plane{}".format(idx))

        aov_data["sfilter"] = node.evalParm("vm_sfilter_plane{}".format(idx))

        pfilter = node.evalParm("vm_pfilter_plane{}".format(idx))

        if pfilter:
            aov_data["pfilter"] = node.evalParm("vm_pfilter_plane{}".format(idx))

        aov_data["componentexport"] = node.evalParm("vm_componentexport{}".format(idx))

        lightexport = node.evalParm("vm_lightexport{}".format(idx))
        lightexport = uidata.LIGHTEXPORT_MENU_ITEMS[lightexport][0]

        if lightexport:
            aov_data["lightexport"] = lightexport
            aov_data["lightexport_scope"] = node.evalParm("vm_lightexport_scope{}".format(idx))
            aov_data["lighexport_select"] = node.evalParm("vm_lightexport_select{}".format(idx))

        aovs.append(AOV(aov_data))

    return aovs


def decode_aov_mime_data(mime_data):
    """Decode AOV data from the mime data.

    :param mime_data: The mime data to decode from.
    :type mime_data: QtCore.QMimeData
    :return: A list of AOV related items.
    :rtype: list

    """
    return pickle.loads(mime_data.data(_AOV_MIME_TYPE).data())


def encode_aov_mime_data(mime_data, aov_data):
    """Encode AOV data into the mime data.

    :param mime_data: The mime data to decode from.
    :type mime_data: QtCore.QMimeData
    :param aov_data: A list of AOV related items.
    :type aov_data: list
    :return:

    """
    mime_data.setData(_AOV_MIME_TYPE, QtCore.QByteArray(pickle.dumps(aov_data)))


def get_selected_mantra_nodes():
    """Find any currently selected Mantra (ifd) nodes."""
    nodes = hou.selectedNodes()

    mantra_type = hou.nodeType("Driver/ifd")

    nodes = [node for node in nodes if node.type() == mantra_type]

    if not nodes:
        hou.ui.displayMessage(
            "No mantra nodes selected.",
            severity=hou.severityType.Error
        )

    return tuple(nodes)


def flatten_element_list(elements):
    """Flatten a list of elements into a list of AOVs."""
    aovs = set()

    for element in elements:
        if isinstance(element, AOV):
            aovs.add(element)

        else:
            for aov in element.aovs:
                aovs.add(aov)

    return aovs


def get_aov_names_from_multiparms(node):
    """Get a list of AOV names from a Mantra node's multiparm."""
    names = []

    num_aovs = node.evalParm("vm_numaux")

    for idx in range(1, num_aovs+1):
        names.append(node.evalParm("vm_variable_plane{}".format(idx)))

    return names


def get_icon_for_group(group):
    """Get the icon for an AOVGroup."""
    # Group has a custom icon path so use. it.
    if group.icon is not None:
        return QtGui.QIcon(group.icon)

    if isinstance(group, IntrinsicAOVGroup):
        return QtGui.QIcon(":ht/rsc/icons/aovs/intrinsic_group.png")

    source = group.source

    if isinstance(source, sources.AOVAssetSectionSource):
        return QtGui.QIcon(":ht/rsc/icons/aovs/otl_group.png")

    elif isinstance(source, sources.AOVHipSource):
        return QtGui.QIcon(":ht/rsc/icons/aovs/hip_group.png")

    return QtGui.QIcon(":ht/rsc/icons/aovs/group.png")


def get_icon_for_vex_type(vextype):
    """Get the icon corresponding to a VEX type."""
    if vextype == "unitvector":
        vextype = "vector"

    return hou.qt.createIcon("DATATYPES_{}".format(vextype))


def get_light_export_menu_index(lightexport):
    """Find the menu index of the lightexport value."""
    return _get_item_menu_index(
        uidata.LIGHTEXPORT_MENU_ITEMS,
        lightexport
    )


def get_quantize_menu_index(quantize):
    """Find the menu index of the quantize value."""
    return _get_item_menu_index(
        uidata.QUANTIZE_MENU_ITEMS,
        quantize
    )


def get_sfilter_menu_index(sfilter):
    """Find the menu index of the sfilter value."""
    return _get_item_menu_index(
        uidata.SFILTER_MENU_ITEMS,
        sfilter
    )


def get_vextype_menu_index(vextype):
    """Find the menu index of the vextype value."""
    return _get_item_menu_index(
        uidata.VEXTYPE_MENU_ITEMS,
        vextype
    )


def has_aov_mime_data(mime_data):
    """Check if the mime data contains AOV data.

    :param mime_data: The mime data to check.
    :type mime_data: QtCore.QMimeData
    :return: Whether or not the mime data contains AOV data.
    :rtype: bool

    """
    return mime_data.hasFormat(_AOV_MIME_TYPE)


def is_file_path_valid(path):
    """Check if a file path is valid."""
    if not path:
        return False

    dirname = os.path.dirname(path)

    file_name = os.path.basename(path)

    if not all([dirname, file_name]):
        return False

    elif not os.path.splitext(file_name)[1]:
        return False

    return True


def is_value_default(value, field):
    """Check if a value for a field is default."""
    return uidata.DEFAULT_VALUES[field] == value


def element_list_as_string(elements):
    """Flatten a list of elements into a space separated string."""
    names = []

    for element in elements:
        if isinstance(element, AOVGroup):
            names.append("@{}".format(element.name))

        else:
            names.append(element.variable)

    return " ".join(names)


def open_aov_editor(node):
    """Open the AOV Manager dialog based on a node."""
    interface = hou.pypanel.interfaceByName("aov_manager")

    desktop = hou.ui.curDesktop()

    tab = desktop.createFloatingPaneTab(
        hou.paneTabType.PythonPanel,
        size=(900, 800)
    )

    tab.showToolbar(False)
    tab.setActiveInterface(interface)

    widget = tab.activeInterfaceRootWidget()
    widget.set_node(node)
