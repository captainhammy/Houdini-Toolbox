"""This module contains classes to define AOVs and groups of AOVs."""

# =============================================================================
# IMPORTS
# =============================================================================

# Future
from __future__ import annotations

# Standard Library
import copy
from typing import TYPE_CHECKING, Any, Dict, List, Optional

# Houdini Toolbox
from houdini_toolbox.sohohooks.aovs import constants as consts

if TYPE_CHECKING:
    import soho  # type: ignore


# =============================================================================
# GLOBALS
# =============================================================================

# Allowable values for various settings.
ALLOWABLE_VALUES = {
    consts.LIGHTEXPORT_KEY: (
        consts.LIGHTEXPORT_PER_CATEGORY_KEY,
        consts.LIGHTEXPORT_PER_LIGHT_KEY,
        consts.LIGHTEXPORT_SINGLE_KEY,
    ),
    consts.QUANTIZE_KEY: ("8", "16", "half", "float"),
    consts.VEXTYPE_KEY: ("float", "unitvector", "vector", "vector4"),
}

_DEFAULT_AOV_DATA: Dict[str, Any] = {
    consts.VARIABLE_KEY: None,
    consts.VEXTYPE_KEY: None,
    consts.CHANNEL_KEY: None,
    consts.COMPONENTEXPORT_KEY: None,
    consts.COMPONENTS_KEY: [],
    consts.COMMENT_KEY: "",
    consts.EXCLUDE_DCM_KEY: None,
    consts.INTRINSICS_KEY: [],
    consts.LIGHTEXPORT_KEY: None,
    consts.LIGHTEXPORT_SCOPE_KEY: "*",
    consts.LIGHTEXPORT_SELECT_KEY: "*",
    consts.PATH_KEY: None,
    consts.PFILTER_KEY: None,
    consts.PLANEFILE_KEY: None,
    consts.PRIORITY_KEY: -1,
    consts.QUANTIZE_KEY: None,
    consts.SFILTER_KEY: None,
}


# =============================================================================
# CLASSES
# =============================================================================


class AOV:
    """This class represents an AOV to be exported.

    :param data: AOV data.

    """

    def __init__(self, data: dict) -> None:
        self._data = copy.copy(_DEFAULT_AOV_DATA)

        self.update_data(data)

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, AOV):
            return NotImplemented

        return self.variable == other.variable

    def __ge__(self, other: Any) -> bool:
        if not isinstance(other, AOV):
            return NotImplemented

        return self.variable >= other.variable

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, AOV):
            return NotImplemented

        return self.variable > other.variable

    def __hash__(self) -> int:
        return hash(self.variable)

    def __le__(self, other: Any) -> bool:
        if not isinstance(other, AOV):
            return NotImplemented

        return self.variable <= other.variable

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, AOV):
            return NotImplemented

        return self.variable < other.variable

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return f"<AOV {self.variable} ({self.vextype})>"

    def __str__(self) -> str:
        return self.variable

    # -------------------------------------------------------------------------
    # NON-PUBLIC METHODS
    # -------------------------------------------------------------------------

    def _light_export_planes(
        self, data: dict, wrangler: Any, cam: soho.SohoObject, now: float
    ) -> None:
        """Handle exporting the image planes based on their export settings.

        :param data: The data to write.
        :param wrangler: A SOHO wrangler.
        :param cam: A SOHO camera.
        :param now: The evaluation time.
        :return:

        """
        # Handle any light exporting.
        if self.lightexport is not None:
            if self.lightexport not in ALLOWABLE_VALUES[consts.LIGHTEXPORT_KEY]:
                raise InvalidAOVValueError(consts.LIGHTEXPORT_KEY, self.lightexport)

            # Get a list of lights matching our mask and selection.
            lights = cam.objectList(
                "objlist:light", now, self.lightexport_scope, self.lightexport_select
            )

            base_channel = data[consts.CHANNEL_KEY]

            if self.lightexport == consts.LIGHTEXPORT_PER_LIGHT_KEY:
                # Process each light.
                for light in lights:
                    _write_light(light, base_channel, data, wrangler, cam, now)

            elif self.lightexport == consts.LIGHTEXPORT_SINGLE_KEY:
                _write_single_channel(lights, data, wrangler, cam, now)

            # consts.LIGHTEXPORT_PER_CATEGORY_KEY
            else:
                _write_per_category(lights, base_channel, data, wrangler, cam, now)

        else:
            # Write a normal AOV definition.
            _write_data_to_ifd(data, wrangler, cam, now)

    def _verify_internal_data(self) -> None:
        """Verify data to make sure it is valid.

        :return:

        """
        if self.variable is None:
            raise MissingVariableError()

        if self.vextype is None:
            raise MissingVexTypeError(self.variable)

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def channel(self) -> str:
        """The name of the output channel."""
        return self._data[consts.CHANNEL_KEY]

    @channel.setter
    def channel(self, channel: str) -> None:
        self._data[consts.CHANNEL_KEY] = channel

    # -------------------------------------------------------------------------

    @property
    def comment(self) -> str:
        """Optional comment about this AOV."""
        return self._data[consts.COMMENT_KEY]

    @comment.setter
    def comment(self, comment: str) -> None:
        self._data[consts.COMMENT_KEY] = comment

    # -------------------------------------------------------------------------

    @property
    def componentexport(self) -> bool:
        """Whether components are being exported."""
        return self._data[consts.COMPONENTEXPORT_KEY]

    @componentexport.setter
    def componentexport(self, componentexport: bool) -> None:
        self._data[consts.COMPONENTEXPORT_KEY] = componentexport

    # -------------------------------------------------------------------------

    @property
    def components(self) -> List[str]:
        """list(str): List of components to export."""
        return self._data[consts.COMPONENTS_KEY]

    @components.setter
    def components(self, components: List[str]) -> None:
        self._data[consts.COMPONENTS_KEY] = components

    # -------------------------------------------------------------------------

    @property
    def exclude_from_dcm(self) -> bool:
        """Exclude this aov from dcm renders."""
        return self._data[consts.EXCLUDE_DCM_KEY]

    @exclude_from_dcm.setter
    def exclude_from_dcm(self, exclude: bool) -> None:
        self._data[consts.EXCLUDE_DCM_KEY] = exclude

    # -------------------------------------------------------------------------

    @property
    def intrinsics(self) -> List[str]:
        """list(str): Any associated intrinsic names."""
        return self._data[consts.INTRINSICS_KEY]

    @intrinsics.setter
    def intrinsics(self, intrinsics: List[str]) -> None:
        self._data[consts.INTRINSICS_KEY] = intrinsics

    # -------------------------------------------------------------------------

    @property
    def lightexport(self) -> str:
        """The light output mode."""
        return self._data[consts.LIGHTEXPORT_KEY]

    @lightexport.setter
    def lightexport(self, lightexport: str) -> None:
        self._data[consts.LIGHTEXPORT_KEY] = lightexport

    # -------------------------------------------------------------------------

    @property
    def lightexport_scope(self) -> str:
        """The light mask."""
        return self._data[consts.LIGHTEXPORT_SCOPE_KEY]

    @lightexport_scope.setter
    def lightexport_scope(self, lightexport_scope: str) -> None:
        self._data[consts.LIGHTEXPORT_SCOPE_KEY] = lightexport_scope

    # -------------------------------------------------------------------------

    @property
    def lightexport_select(self) -> str:
        """The light selection (categories)."""
        return self._data[consts.LIGHTEXPORT_SELECT_KEY]

    @lightexport_select.setter
    def lightexport_select(self, lightexport_select: str) -> None:
        self._data[consts.LIGHTEXPORT_SELECT_KEY] = lightexport_select

    # -------------------------------------------------------------------------

    @property
    def path(self) -> str:
        """The path containing the AOV definition."""
        return self._data[consts.PATH_KEY]

    @path.setter
    def path(self, path: str) -> None:
        self._data[consts.PATH_KEY] = path

    # -------------------------------------------------------------------------

    @property
    def pfilter(self) -> str:
        """The name of the pixel filter."""
        return self._data[consts.PFILTER_KEY]

    @pfilter.setter
    def pfilter(self, pfilter: str) -> None:
        self._data[consts.PFILTER_KEY] = pfilter

    # -------------------------------------------------------------------------

    @property
    def planefile(self) -> str:
        """The path to the specific file, if any."""
        return self._data[consts.PLANEFILE_KEY]

    @planefile.setter
    def planefile(self, planefile: str) -> None:
        self._data[consts.PLANEFILE_KEY] = planefile

    # -------------------------------------------------------------------------

    @property
    def priority(self) -> int:
        """The AOV priority."""
        return self._data[consts.PRIORITY_KEY]

    @priority.setter
    def priority(self, priority: int) -> None:
        self._data[consts.PRIORITY_KEY] = priority

    # -------------------------------------------------------------------------

    @property
    def quantize(self) -> str:
        """The type of quantization for the output AOV."""
        return self._data[consts.QUANTIZE_KEY]

    @quantize.setter
    def quantize(self, quantize: str) -> None:
        self._data[consts.QUANTIZE_KEY] = quantize

    # -------------------------------------------------------------------------

    @property
    def sfilter(self) -> str:
        """The name of the sample filter."""
        return self._data[consts.SFILTER_KEY]

    @sfilter.setter
    def sfilter(self, sfilter: str) -> None:
        self._data[consts.SFILTER_KEY] = sfilter

    # -------------------------------------------------------------------------

    @property
    def variable(self) -> str:
        """The name of the vex variable."""
        return self._data[consts.VARIABLE_KEY]

    @variable.setter
    def variable(self, variable: str) -> None:
        self._data[consts.VARIABLE_KEY] = variable

    # -------------------------------------------------------------------------

    @property
    def vextype(self) -> str:
        """The data type of the output AOV."""
        return self._data[consts.VEXTYPE_KEY]

    @vextype.setter
    def vextype(self, vextype: str) -> None:
        self._data[consts.VEXTYPE_KEY] = vextype

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def as_data(self) -> dict:
        """Get a dictionary representing the AOV.

        :return: Data representing this object.

        """
        data: Dict[str, Any] = {
            consts.VARIABLE_KEY: self.variable,
            consts.VEXTYPE_KEY: self.vextype,
        }

        if self.channel:
            data[consts.CHANNEL_KEY] = self.channel

        if self.quantize is not None:
            data[consts.QUANTIZE_KEY] = self.quantize

        if self.sfilter is not None:
            data[consts.SFILTER_KEY] = self.sfilter

        if self.pfilter is not None:
            data[consts.PFILTER_KEY] = self.pfilter

        if self.exclude_from_dcm is not None:
            data[consts.EXCLUDE_DCM_KEY] = self.exclude_from_dcm

        if self.componentexport is not None:
            data[consts.COMPONENTEXPORT_KEY] = self.componentexport

            if self.components:
                data[consts.COMPONENTS_KEY] = self.components

        if self.lightexport is not None:
            data[consts.LIGHTEXPORT_KEY] = self.lightexport

            if self.lightexport != consts.LIGHTEXPORT_PER_CATEGORY_KEY:
                data[consts.LIGHTEXPORT_SCOPE_KEY] = self.lightexport_scope
                data[consts.LIGHTEXPORT_SELECT_KEY] = self.lightexport_select

        if self.intrinsics:
            data[consts.INTRINSICS_KEY] = self.intrinsics

        if self.comment:
            data[consts.COMMENT_KEY] = self.comment

        if self.priority != -1:
            data[consts.PRIORITY_KEY] = self.priority

        return data

    def update_data(self, data: dict) -> None:
        """Update internal data with new data.

        :param data: AOV data.
        :return:

        """
        for name, value in list(data.items()):
            # Check if there is a restriction on the data type.
            if name in ALLOWABLE_VALUES:
                # Get the allowable types for this data.
                allowable = ALLOWABLE_VALUES[name]

                # If the value isn't in the list, raise an exception.
                if value not in allowable:
                    raise InvalidAOVValueError(name, value)

            # If the key corresponds to the data in this object we store the
            # data.
            if name in self._data:
                self._data[name] = value

        # Verify the new data is valid.
        self._verify_internal_data()

    def write_to_ifd(self, wrangler: Any, cam: soho.SohoObject, now: float) -> None:
        """Output the AOV.

        :param wrangler: A SOHO wrangler.
        :param cam: A SOHO camera.
        :param now: The evaluation time.
        :return:

        """
        import soho

        # The base data to pass along.
        data = self.as_data()

        channel = self.channel

        # If there is no explicit channel set, use the variable name.
        if channel is None:
            channel = self.variable

        # Handle exporting of multiple components
        if self.componentexport:
            components = self.components

            # If no components are explicitly set on the AOV, use the
            # vm_exportcomponents parameter from the Mantra ROP.
            if not components:
                parms = {
                    "vm_exportcomponents": soho.SohoParm(
                        "vm_exportcomponents", "str", [""], skipdefault=False
                    )
                }

                plist = cam.wrangle(wrangler, parms, now)

                if plist:
                    export_components = plist["vm_exportcomponents"].Value[0]
                    components = export_components.split()

            # Create a unique channel for each component and output the block.
            for component in components:
                comp_data = copy.copy(data)
                comp_data[consts.CHANNEL_KEY] = f"{channel}_{component}"
                comp_data[consts.COMPONENT_KEY] = component

                self._light_export_planes(comp_data, wrangler, cam, now)

        else:
            # Update the data with the channel.
            data[consts.CHANNEL_KEY] = channel

            self._light_export_planes(data, wrangler, cam, now)


# =============================================================================


class AOVGroup:
    """This class represents a group of AOV definitions.

    :param name: The group name.

    """

    def __init__(self, name: str) -> None:
        self._aovs: List[AOV] = []
        self._comment = ""
        self._icon: Optional[str] = None
        self._includes: List[str] = []
        self._name = name
        self._path: Optional[str] = None
        self._priority = -1

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, AOVGroup):
            return NotImplemented

        return self.name == other.name

    def __ge__(self, other: Any) -> bool:
        if not isinstance(other, AOVGroup):
            return NotImplemented

        return self.name >= other.name

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, AOVGroup):
            return NotImplemented

        return self.name > other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __le__(self, other: Any) -> bool:
        if not isinstance(other, AOVGroup):
            return NotImplemented

        return self.name <= other.name

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, AOVGroup):
            return NotImplemented

        return self.name < other.name

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name} ({len(self.aovs)} AOVs)>"

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def aovs(self) -> List[AOV]:
        """A list of AOVs in the group."""
        return self._aovs

    # -------------------------------------------------------------------------

    @property
    def comment(self) -> str:
        """Optional comment about this AOV."""
        return self._comment

    @comment.setter
    def comment(self, comment: str) -> None:
        self._comment = comment

    # -------------------------------------------------------------------------

    @property
    def icon(self) -> Optional[str]:
        """Optional path to an icon for this group."""
        return self._icon

    @icon.setter
    def icon(self, icon: Optional[str]) -> None:
        self._icon = icon

    # -------------------------------------------------------------------------

    @property
    def includes(self) -> List[str]:
        """List of AOV names belonging to the group."""
        return self._includes

    # -------------------------------------------------------------------------

    @property
    def name(self) -> str:
        """The name of the group."""
        return self._name

    # -------------------------------------------------------------------------

    @property
    def path(self) -> Optional[str]:
        """The path containing the group definition."""
        return self._path

    @path.setter
    def path(self, path: str) -> None:
        self._path = path

    # -------------------------------------------------------------------------

    @property
    def priority(self) -> int:
        """Group priority."""
        return self._priority

    @priority.setter
    def priority(self, priority: int) -> None:
        self._priority = priority

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def clear(self) -> None:
        """Clear the list of AOVs belonging to this group.

        :return:

        """
        self._aovs = []
        self._includes = []

    def as_data(self) -> dict:
        """Get a dictionary representing the group.

        :return: Data representing this object.

        """
        includes = []

        includes.extend(self.includes)

        includes.extend([aov.variable for aov in self.aovs])

        data: Dict[str, Any] = {consts.GROUP_INCLUDE_KEY: includes}

        if self.comment:
            data[consts.COMMENT_KEY] = self.comment

        if self.priority != -1:
            data[consts.PRIORITY_KEY] = self.priority

        return {self.name: data}

    def write_to_ifd(self, wrangler: Any, cam: soho.SohoObject, now: float) -> None:
        """Write all AOVs in the group to the ifd.

        :param wrangler: A SOHO wrangler.
        :param cam: A SOHO camera.
        :param now: The evaluation time.
        :return:

        """
        for aov in self.aovs:
            aov.write_to_ifd(wrangler, cam, now)


class IntrinsicAOVGroup(AOVGroup):
    """An intrinsic grouping of AOVs.

    :param name: The group name.

    """

    def __init__(self, name: str) -> None:
        super().__init__(name)

        self._comment = "Automatically generated"


# =============================================================================
# EXCEPTIONS
# =============================================================================


class AOVError(Exception):  # pragma: no cover
    """AOV exception base class."""


class InvalidAOVValueError(AOVError):  # pragma: no cover
    """Exception for invalid AOV setting values.

    :param name: The invalid setting name.
    :param value: The invalid setting value.

    """

    def __init__(self, name: str, value: str) -> None:
        super().__init__()
        self.name = name
        self.value = value

    def __str__(self) -> str:
        return f"Invalid value '{self.value}' in '{self.name}': Must be one of {ALLOWABLE_VALUES[self.name]}"


class MissingVariableError(AOVError):  # pragma: no cover
    """Exception for missing 'variable' information."""

    def __str__(self) -> str:
        return "Cannot create AOV: missing 'variable' value."


class MissingVexTypeError(AOVError):  # pragma: no cover
    """Exception for missing 'vextype' information.

    :param variable: The variable naming missing vextype information.

    """

    def __init__(self, variable: str) -> None:
        super().__init__()
        self.variable = variable

    def __str__(self) -> str:
        return f"Cannot create AOV {self.variable}: missing 'vextype'."


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _build_category_map(lights: List[soho.SohoObject], now: float) -> dict:
    """Build a mapping of category names to lights.

    :param lights: A list of lights.
    :param now: The evaluation time.
    :return: The category map.

    """
    category_map: Dict[Optional[str], List[soho.SohoObject]] = {}

    # Process each selected light.
    for light in lights:
        # Get the category for the light.
        value: List[str] = []
        light.evalString("categories", now, value)

        # Light doesn't have a 'categories' parameter.
        if not value:
            continue

        # Get the raw string.
        categories_value = value[0]

        # Since the categories value can be space or comma
        # separated we replace the commas with spaces then split.
        categories_value = categories_value.replace(",", " ")
        categories = categories_value.split()

        # If the categories list was empty, put the light in a fake
        # category.
        if not categories:
            no_category_lights = category_map.setdefault(None, [])
            no_category_lights.append(light)

        else:
            # For each category the light belongs to, add it to
            # the list.
            for category in categories:
                category_lights = category_map.setdefault(category, [])
                category_lights.append(light)

    return category_map


def _call_post_defplane(
    data: dict, wrangler: Any, cam: soho.SohoObject, now: float
) -> bool:
    """Call the post_defplane hook.

    :param data: AOV data.
    :param wrangler: A SOHO wrangler.
    :param cam: A SOHO camera.
    :param now: The evaluation time.
    :return: Whether the hook was successful.

    """
    import IFDhooks  # type: ignore

    return IFDhooks.call(
        "post_defplane",
        data[consts.VARIABLE_KEY],
        data[consts.VEXTYPE_KEY],
        -1,
        wrangler,
        cam,
        now,
        data.get(consts.PLANEFILE_KEY),
        data.get(consts.LIGHTEXPORT_KEY),
    )


def _call_pre_defplane(
    data: dict, wrangler: Any, cam: soho.SohoObject, now: float
) -> bool:
    """Call the pre_defplane hook.

    :param data: AOV data.
    :param wrangler: A SOHO wrangler.
    :param cam: A SOHO camera.
    :param now: The evaluation time.
    :return: Whether the hook was successful.

    """
    import IFDhooks

    return IFDhooks.call(
        "pre_defplane",
        data[consts.VARIABLE_KEY],
        data[consts.VEXTYPE_KEY],
        -1,
        wrangler,
        cam,
        now,
        data.get(consts.PLANEFILE_KEY),
        data.get(consts.LIGHTEXPORT_KEY),
    )


def _write_data_to_ifd(
    data: dict, wrangler: Any, cam: soho.SohoObject, now: float
) -> None:
    """Write AOV data to the ifd.

    :param data: AOV data.
    :param wrangler: A SOHO wrangler.
    :param cam: A SOHO camera.
    :param now: The evaluation time.
    :return:

    """
    import IFDapi

    # Call the 'pre_defplane' hook.  If the function returns True,
    # return.
    if _call_pre_defplane(data, wrangler, cam, now):
        return

    # Start of plane block in IFD.
    IFDapi.ray_start("plane")

    # Primary block information.
    IFDapi.ray_property("plane", "variable", [data[consts.VARIABLE_KEY]])
    IFDapi.ray_property("plane", "vextype", [data[consts.VEXTYPE_KEY]])
    IFDapi.ray_property("plane", "channel", [data[consts.CHANNEL_KEY]])

    if consts.QUANTIZE_KEY in data:
        IFDapi.ray_property("plane", "quantize", [data[consts.QUANTIZE_KEY]])

    # Optional AOV information.
    if consts.PLANEFILE_KEY in data:
        planefile = data["planefile"]

        if planefile is not None:
            IFDapi.ray_property("plane", "planefile", [planefile])

    if consts.LIGHTEXPORT_KEY in data:
        IFDapi.ray_property("plane", "lightexport", [data[consts.LIGHTEXPORT_KEY]])

    if consts.PFILTER_KEY in data:
        IFDapi.ray_property("plane", "pfilter", [data[consts.PFILTER_KEY]])

    if consts.SFILTER_KEY in data:
        IFDapi.ray_property("plane", "sfilter", [data[consts.SFILTER_KEY]])

    if consts.COMPONENT_KEY in data:
        IFDapi.ray_property("plane", "component", [data[consts.COMPONENT_KEY]])

    if consts.EXCLUDE_DCM_KEY in data:
        IFDapi.ray_property("plane", "excludedcm", [True])

    # Call the 'post_defplane' hook.
    if _call_post_defplane(data, wrangler, cam, now):
        return

    # End the plane definition block.
    IFDapi.ray_end()


def _write_light(
    light: soho.SohoObject,
    base_channel: str,
    data: dict,
    wrangler: Any,
    cam: soho.SohoObject,
    now: float,
) -> None:
    """Write a light to the ifd.

    :param light: The light to write.
    :param base_channel: The channel name.
    :param data: AOV data.
    :param wrangler: A SOHO wrangler.
    :param cam: A SOHO camera.
    :param now: The evaluation time.
    :return:

    """
    import soho

    # Try and find the suffix using the 'vm_export_suffix'
    # parameter.  If it doesn't exist, use an empty string.
    suffix = light.getDefaultedString("vm_export_suffix", now, [""])[0]

    prefix: List[str] = []

    # Look for the prefix parameter.  If it doesn't exist, use
    # the light's name and replace the '/' with '_'.  The
    # default value of 'vm_export_prefix' is usually $OS.
    if not light.evalString("vm_export_prefix", now, prefix):
        prefix = [light.getName()[1:].replace("/", "_")]

    # If there is a prefix we construct the channel name using
    # it and the suffix.
    if prefix:
        channel = f"{prefix[0]}_{base_channel}{suffix}"

    # If not and there is a valid suffix, add it to the channel
    # name.
    elif suffix:
        channel = f"{base_channel}{suffix}"

    # Throw an error because all the per-light channels will
    # have the same name.
    else:
        soho.error("Empty suffix for per-light exports.")
        channel = base_channel

    data[consts.CHANNEL_KEY] = channel
    data[consts.LIGHTEXPORT_KEY] = light.getName()

    # Write this light export to the ifd.
    _write_data_to_ifd(data, wrangler, cam, now)


def _write_per_category(
    lights: List[soho.SohoObject],
    base_channel: str,
    data: dict,
    wrangler: Any,
    cam: soho.SohoObject,
    now: float,
) -> None:
    """Write lights to the ifd based on their category.

    :param lights: The light to write.
    :param base_channel: The channel name.
    :param data: AOV data.
    :param wrangler: A SOHO wrangler.
    :param cam: A SOHO camera.
    :param now: The evaluation time.
    :return:

    """
    # A mapping between category names and their member lights.
    category_map = _build_category_map(lights, now)

    # Process all the found categories and their member lights.
    for category, category_lights in list(category_map.items()):
        # Construct the export string to contain all the member
        # lights.
        data[consts.LIGHTEXPORT_KEY] = " ".join(
            [light.getName() for light in category_lights]
        )

        if category is not None:
            # The channel is the regular channel named prefixed with
            # the category name.
            data[consts.CHANNEL_KEY] = f"{category}_{base_channel}"

        else:
            data[consts.CHANNEL_KEY] = base_channel

        # Write the per-category light export to the ifd.
        _write_data_to_ifd(data, wrangler, cam, now)


def _write_single_channel(
    lights: List[soho.SohoObject],
    data: dict,
    wrangler: Any,
    cam: soho.SohoObject,
    now: float,
) -> None:
    """Write lights to the ifd as a single channel.

    :param lights: The lights to write.
    :param data: AOV data.
    :param wrangler: A SOHO wrangler.
    :param cam: A SOHO camera.
    :param now: The evaluation time.
    :return:

    """
    # Take all the light names and join them together.
    if lights:
        lightexport = " ".join([light.getName() for light in lights])

    # If there are no lights, we can't pass in an empty string
    # since then mantra will think that light exports are
    # disabled.  So pass down an string that presumably doesn't
    # match any light name.
    else:
        lightexport = "__nolights__"

    data[consts.LIGHTEXPORT_KEY] = lightexport

    # Write the combined light export to the ifd.
    _write_data_to_ifd(data, wrangler, cam, now)
