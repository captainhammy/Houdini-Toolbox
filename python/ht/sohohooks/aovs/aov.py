"""This module contains classes to define AOVs and groups of AOVs."""

import copy

# =============================================================================
# GLOBALS
# =============================================================================

# Allowable values for various settings.
ALLOWABLE_VALUES = {
    "lightexport": ("per-category", "per-light", "single"),
    "quantization": ("8", "16", "half", "float"),
    "vextype": ("float", "unitvector", "vector", "vector4")
}

_DEFAULT_AOV_DATA = {
    "variable": None,
    "vextype": None,
    "channel": None,
    "componentexport": None,
    "components": [],
    "comment": "",
    "exclude_from_dcm": None,
    "intrinsics": [],
    "lightexport": None,
    "lightexport_scope": "*",
    "lightexport_select": "*",
    "path": None,
    "pfilter": None,
    "planefile": None,
    "priority": -1,
    "quantize": None,
    "sfilter": None,
}

# =============================================================================
# CLASSES
# =============================================================================

class AOV(object):
    """This class represents an AOV to be exported."""

    def __init__(self, data):
        self._data = copy.copy(_DEFAULT_AOV_DATA)

        self._update_data(data)

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __cmp__(self, other):
        if isinstance(other, self.__class__):
            return cmp(self.variable, other.variable)

        return -1

    def __hash__(self):
        return hash(self.variable)

    def __repr__(self): # pragma: no cover
        return "<AOV {} ({})>".format(self.variable, self.vextype)

    def __str__(self):
        return self.variable

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _light_export_planes(self, data, wrangler, cam, now):
        """Handle exporting the image planes based on their export settings."""
        # Handle any light exporting.
        if self.lightexport is not None:
            # Get a list of lights matching our mask and selection.
            lights = cam.objectList(
                "objlist:light",
                now,
                self.lightexport_scope,
                self.lightexport_select
            )

            base_channel = data["channel"]

            if self.lightexport == "per-light":
                # Process each light.
                for light in lights:
                    _write_light(light, base_channel, data, wrangler, cam, now)

            elif self.lightexport == "single":
                _write_single_channel(lights, data, wrangler, cam, now)

            elif self.lightexport == "per-category":
                _write_per_category(lights, base_channel, data, wrangler, cam, now)

            else:
                raise InvalidAOVValueError("lightexport", self.lightexport)

        else:
            # Write a normal AOV definition.
            _write_data_to_ifd(data, wrangler, cam, now)

    def _update_data(self, data):
        """Update internal data with new data."""
        for name, value in data.iteritems():
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

    def _verify_internal_data(self):
        """Verify data to make sure it is valid."""
        if self.variable is None:
            raise MissingVariableError()

        if self.vextype is None:
            raise MissingVexTypeError(self.variable)

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def channel(self):
        """The name of the output AOV's channel."""
        return self._data["channel"]

    @channel.setter
    def channel(self, channel):
        self._data["channel"] = channel

    # =========================================================================

    @property
    def comment(self):
        """Optional comment about this AOV."""
        return self._data["comment"]

    @comment.setter
    def comment(self, comment):
        self._data["comment"] = comment

    # =========================================================================

    @property
    def componentexport(self):
        """Whether or not components are being exported."""
        return self._data["componentexport"]

    @componentexport.setter
    def componentexport(self, componentexport):
        self._data["componentexport"] = componentexport

    # =========================================================================

    @property
    def components(self):
        """List of components to export."""
        return self._data["components"]

    @components.setter
    def components(self, components):
        self._data["components"] = components

    # =========================================================================

    @property
    def exclude_from_dcm(self):
        """Exclude this aov from dcms."""
        return self._data["exclude_from_dcm"]

    @exclude_from_dcm.setter
    def exclude_from_dcm(self, exclude):
        self._data["exclude_from_dcm"] = exclude

    # =========================================================================

    @property
    def intrinsics(self):
        return self._data["intrinsics"]

    @intrinsics.setter
    def intrinsics(self, intrinsics):
        self._data["intrinsics"] = intrinsics

    # =========================================================================

    @property
    def lightexport(self):
        """The light output mode."""
        return self._data["lightexport"]

    @lightexport.setter
    def lightexport(self, lightexport):
        self._data["lightexport"] = lightexport

    # =========================================================================

    @property
    def lightexport_scope(self):
        """The light mask."""
        return self._data["lightexport_scope"]

    @lightexport_scope.setter
    def lightexport_scope(self, lightexport_scope):
        self._data["lightexport_scope"] = lightexport_scope

    # =========================================================================

    @property
    def lightexport_select(self):
        """The light selection (categories)."""
        return self._data["lightexport_select"]

    @lightexport_select.setter
    def lightexport_select(self, lightexport_select):
        self._data["lightexport_select"] = lightexport_select

    # =========================================================================

    @property
    def path(self):
        """The path containing the AOV definition."""
        return self._data["path"]

    @path.setter
    def path(self, path):
        self._data["path"] = path

    # =========================================================================

    @property
    def pfilter(self):
        """The name of the output AOV's pixel filter."""
        return self._data["pfilter"]

    @pfilter.setter
    def pfilter(self, pfilter):
        self._data["pfilter"] = pfilter

    # =========================================================================

    @property
    def planefile(self):
        """The name of the output AOV's specific file, if any."""
        return self._data["planefile"]

    @planefile.setter
    def planefile(self, planefile):
        self._data["planefile"] = planefile

    # =========================================================================

    @property
    def priority(self):
        """Group priority."""
        return self._data["priority"]

    @priority.setter
    def priority(self, priority):
        self._data["priority"] = priority

    # =========================================================================

    @property
    def quantize(self):
        """The type of quantization for the output AOV."""
        return self._data["quantize"]

    @quantize.setter
    def quantize(self, quantize):
        self._data["quantize"] = quantize

    # =========================================================================

    @property
    def sfilter(self):
        """The name of the output AOV's sample filter."""
        return self._data["sfilter"]

    @sfilter.setter
    def sfilter(self, sfilter):
        self._data["sfilter"] = sfilter

    # =========================================================================

    @property
    def variable(self):
        """The name of the output AOV's vex variable."""
        return self._data["variable"]

    @variable.setter
    def variable(self, variable):
        self._data["variable"] = variable

    # =========================================================================

    @property
    def vextype(self):
        """The data type of the output AOV."""
        return self._data["vextype"]

    @vextype.setter
    def vextype(self, vextype):
        self._data["vextype"] = vextype

    # =========================================================================
    # METHODS
    # =========================================================================

    def as_data(self):
        """Get a dictionary representing the AOV."""
        d = {
            "variable": self.variable,
            "vextype": self.vextype,
        }

        if self.channel:
            d["channel"] = self.channel

        if self.quantize is not None:
            d["quantize"] = self.quantize

        if self.sfilter is not None:
            d["sfilter"] = self.sfilter

        if self.pfilter is not None:
            d["pfilter"] = self.pfilter

        if self.exclude_from_dcm is not None:
            d["exclude_from_dcm"] = self.exclude_from_dcm

        if self.componentexport is not None:
            d["componentexport"] = self.componentexport

            if self.components:
                d["components"] = self.components

        if self.lightexport is not None:
            d["lightexport"] = self.lightexport

            if self.lightexport != "per-category":
                d["lightexport_scope"] = self.lightexport_scope
                d["lightexport_select"] = self.lightexport_select

        if self.intrinsics:
            d["intrinsics"] = self.intrinsics

        if self.comment:
            d["comment"] = self.comment

        if self.priority != -1:
            d["priority"] = self.priority

        return d

    # =========================================================================

    def write_to_ifd(self, wrangler, cam, now):
        """Output the AOV."""
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
                        "vm_exportcomponents",
                        "str",
                        [""],
                        skipdefault=False
                    ),
                }

                plist = cam.wrangle(wrangler, parms, now)

                if plist:
                    components = plist["vm_exportcomponents"].Value[0]
                    components = components.split()

            # Create a unique channel for each component and output the block.
            for component in components:
                comp_data = copy.copy(data)
                comp_data["channel"] = "{}_{}".format(channel, component)
                comp_data["component"] = component

                self._light_export_planes(comp_data, wrangler, cam, now)

        else:
            # Update the data with the channel.
            data["channel"] = channel

            self._light_export_planes(data, wrangler, cam, now)

# =============================================================================


class AOVGroup(object):
    """This class represents a group of AOV definitions.

    """

    def __init__(self, name):
        self._aovs = []
        self._comment = ""
        self._icon = None
        self._includes = []
        self._name = name
        self._path = None
        self._priority = -1

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __cmp__(self, other):
        if isinstance(other, self.__class__):
            return cmp(self.name, other.name)

        return -1

    def __repr__(self): # pragma: no cover
        return "<{} {} ({} AOVs)>".format(
            self.__class__.__name__,
            self.name,
            len(self.aovs)
        )

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def aovs(self):
        """A list of AOVs in the group."""
        return self._aovs

    # =========================================================================

    @property
    def comment(self):
        """Optional comment about this AOV."""
        return self._comment

    @comment.setter
    def comment(self, comment):
        self._comment = comment

    # =========================================================================

    @property
    def icon(self):
        """Optional path to an icon for this group."""
        return self._icon

    @icon.setter
    def icon(self, icon):
        self._icon = icon

    # =========================================================================

    @property
    def includes(self):
        """List of AOV names belonging to the group."""
        return self._includes

    # =========================================================================

    @property
    def name(self):
        """The name of the group."""
        return self._name

    # =========================================================================

    @property
    def path(self):
        """The path containing the group definition."""
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    # =========================================================================

    @property
    def priority(self):
        """Group priority."""
        return self._priority

    @priority.setter
    def priority(self, priority):
        self._priority = priority

    # =========================================================================
    # METHODS
    # =========================================================================

    def clear(self):
        """Clear the list of AOVs belonging to this group."""
        self._aovs = []

    def as_data(self):
        """Get a dictionary representing the group."""
        includes = []

        includes.extend(self.includes)

        includes.extend([aov.variable for aov in self.aovs])

        d = {
            self.name: {
                "include": includes,
            }
        }

        if self.comment:
            d[self.name]["comment"] = self.comment

        if self.priority != -1:
            d[self.name]["priority"] = self.priority

        return d

    def write_to_ifd(self, wrangler, cam, now):
        """Write all AOVs in the group to the ifd."""
        for aov in self.aovs:
            aov.write_to_ifd(wrangler, cam, now)


class IntrinsicAOVGroup(AOVGroup):
    """An intrinsic grouping of AOVs."""

    def __init__(self, name):
        super(IntrinsicAOVGroup, self).__init__(name)

        self._comment = "Automatically generated"

# =============================================================================
# EXCEPTIONS
# =============================================================================


class AOVError(Exception): # pragma: no cover
    """AOV exception base class."""
    pass


class InvalidAOVValueError(AOVError): # pragma: no cover
    """Exception for invalid AOV setting values."""

    def __init__(self, name, value):
        super(InvalidAOVValueError, self).__init__()
        self.name = name
        self.value = value

    def __str__(self):
        return "Invalid value '{}' in '{}': Must be one of {}".format(
            self.value,
            self.name,
            ALLOWABLE_VALUES[self.name],
        )


class MissingVariableError(AOVError): # pragma: no cover
    """Exception for missing 'variable' information."""

    def __str__(self):
        return "Cannot create AOV: missing 'variable' value."


class MissingVexTypeError(AOVError): # pragma: no cover
    """Exception for missing 'vextype' information."""

    def __init__(self, vextype):
        super(MissingVexTypeError, self).__init__()
        self.vextype = vextype

    def __str__(self):
        return "Cannot create AOV {}: missing 'vextype'.".format(
            self.vextype
        )

# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

def _build_category_map(lights, now):
    category_map = {}

    # Process each selected light.
    for light in lights:
        # Get the category for the light.
        value = []
        light.evalString("categories", now, value)

        # Light doesn't have a 'categories' parameter.
        if not value:
            continue

        # Get the raw string.
        categories = value[0]

        # Since the categories value can be space or comma
        # separated we replace the commas with spaces then split.
        categories = categories.replace(',', ' ')
        categories = categories.split()

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


def _call_post_defplane(data, wrangler, cam, now):
    """Call the post_defplane hook."""
    import IFDhooks

    return IFDhooks.call(
        "post_defplane",
        data["variable"],
        data["vextype"],
        -1,
        wrangler,
        cam,
        now,
        data.get("planefile"),
        data.get("lightexport")
    )


def _call_pre_defplane(data, wrangler, cam, now):
    """Call the pre_defplane hook."""
    import IFDhooks

    return IFDhooks.call(
        "pre_defplane",
        data["variable"],
        data["vextype"],
        -1,
        wrangler,
        cam,
        now,
        data.get("planefile"),
        data.get("lightexport")
    )


def _write_data_to_ifd(data, wrangler, cam, now):
    """Write AOV data to the ifd."""
    import IFDapi

    # Call the 'pre_defplane' hook.  If the function returns True,
    # return.
    if _call_pre_defplane(data, wrangler, cam, now):
        return

    # Start of plane block in IFD.
    IFDapi.ray_start("plane")

    # Primary block information.
    IFDapi.ray_property("plane", "variable", [data["variable"]])
    IFDapi.ray_property("plane", "vextype", [data["vextype"]])
    IFDapi.ray_property("plane", "channel", [data["channel"]])

    if "quantize" in data:
        IFDapi.ray_property("plane", "quantize", [data["quantize"]])

    # Optional AOV information.
    if "planefile" in data:
        planefile = data["planefile"]

        if planefile is not None:
            IFDapi.ray_property("plane", "planefile", [planefile])

    if "lightexport" in data:
        IFDapi.ray_property("plane", "lightexport", [data["lightexport"]])

    if "pfilter" in data:
        IFDapi.ray_property("plane", "pfilter", [data["pfilter"]])

    if "sfilter" in data:
        IFDapi.ray_property("plane", "sfilter", [data["sfilter"]])

    if "component" in data:
        IFDapi.ray_property("plane", "component", [data["component"]])

    if "exclude_from_dcm" in data:
        IFDapi.ray_property("plane", "excludedcm", [True])

    # Call the 'post_defplane' hook.
    if _call_post_defplane(data, wrangler, cam, now):
        return

    # End the plane definition block.
    IFDapi.ray_end()


def _write_light(light, base_channel, data, wrangler, cam, now):
    import soho

    # Try and find the suffix using the 'vm_export_suffix'
    # parameter.  If it doesn't exist, use an empty string.
    suffix = light.getDefaultedString("vm_export_suffix", now, [''])[0]

    prefix = []

    # Look for the prefix parameter.  If it doesn't exist, use
    # the light's name and replace the '/' with '_'.  The
    # default value of 'vm_export_prefix' is usually $OS.
    if not light.evalString("vm_export_prefix", now, prefix):
        prefix = [light.getName()[1:].replace('/', '_')]

    # If there is a prefix we construct the channel name using
    # it and the suffix.
    if prefix:
        channel = "{}_{}{}".format(prefix[0], base_channel, suffix)

    # If not and there is a valid suffix, add it to the channel
    # name.
    elif suffix:
        channel = "{}{}".format(base_channel, suffix)

    # Throw an error because all the per-light channels will
    # have the same name.
    else:
        soho.error("Empty suffix for per-light exports.")
        channel = base_channel

    data["channel"] = channel
    data["lightexport"] = light.getName()

    # Write this light export to the ifd.
    _write_data_to_ifd(data, wrangler, cam, now)


def _write_per_category(lights, base_channel, data, wrangler, cam, now):
    # A mapping between category names and their member lights.
    category_map = _build_category_map(lights, now)

    # Process all the found categories and their member lights.
    for category, category_lights in category_map.iteritems():
        # Construct the export string to contain all the member
        # lights.
        data["lightexport"] = ' '.join([light.getName() for light in category_lights])

        if category is not None:
            # The channel is the regular channel named prefixed with
            # the category name.
            data["channel"] = "{}_{}".format(category, base_channel)

        else:
            data["channel"] = base_channel

        # Write the per-category light export to the ifd.
        _write_data_to_ifd(data, wrangler, cam, now)


def _write_single_channel(lights, data, wrangler, cam, now):
    # Take all the light names and join them together.
    if lights:
        lightexport = ' '.join([light.getName() for light in lights])

    # If there are no lights, we can't pass in an empty string
    # since then mantra will think that light exports are
    # disabled.  So pass down an string that presumably doesn't
    # match any light name.
    else:
        lightexport = "__nolights__"

    data["lightexport"] = lightexport

    # Write the combined light export to the ifd.
    _write_data_to_ifd(data, wrangler, cam, now)
