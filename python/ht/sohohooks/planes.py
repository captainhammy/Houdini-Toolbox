"""This module contains classes and functions used to build Mantra image planes
based on definitions in files.

Synopsis
--------

Classes:
    PlaneConditional
        An object representing conditional plane settings.

    RenderPlane
        An object representing an extra image plane for Mantra.

    RenderPlaneGroup
        An object representing a group of RenderPlane definitions.

Exceptions:
    InvalidPlaneValueError
        Exception for invalid plane setting values.

    MissingVexTypeError
        Exception for a 'vextype' information.

Functions:
    addRenderPlanes()
        Adds deep rasters as defined by a .json file.

    buildPlaneGroups()
        Build a list of all available RenderPlaneGroups found.

Description
-----------

By default, the automatic planes system uses planes defined in a string
parameter 'auto_planes'.  In this parameter you can specify groups of planes
that should be added.  Before attempting to add the planes it verifies that
they are not disabled by checking the 'disable_auto_planes' parameter.

"""
__author__ = "Graham Thompson"
__email__ = "captainhammy@gmail.com"

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import glob
import json
import os
import re

# Houdini Imports
import hou

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "InvalidPlaneValueError",
    "MissingVexTypeError",
    "PlaneConditional",
    "RenderPlane",
    "RenderPlaneGroup",
    "addRenderPlanes",
    "buildPlaneGroups"
]

# =============================================================================
# CONSTANTS
# =============================================================================

# Allowable values for various settings.
_ALLOWABLE_VALUES = {
    "lightexport": ("per-light", "single"),
    "quantization": ('8', '16', 'half', 'float'),
    "vextype": ("float", "vector", "vector4")
}

# =============================================================================
# CLASSES
# =============================================================================

class PlaneConditional(object):
    """An object representing conditional plane settings.

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, data):
        """Initialize a PlaneConditional object.

        Args:
            data : (dict)
                A dictionary of data.

        Raises:
            N/A

        Returns:
            N/A

        """
        # Store the pattern to match by.
        self._pattern = data["pattern"]

        # The parameter data to match against.
        self._parmData = data["parm"]

        # Data to return as a result of the match.
        self._match = {}
        self._nomatch = {}

        # If we have data to apply when the pattern mat
        if "match" in data:
            self._validateMatchData(data["match"])
            self.match.update(data["match"])

        if "nomatch" in data:
            self._validateMatchData(data["nomatch"])
            self.nomatch.update(data["nomatch"])

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __repr__(self):
        return "<PlaneConditional {0} ({1})>".format(
            self.parmData["name"],
            self.pattern
        )

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    # -------------------------------------------------------------------------
    #    Name: _validateMatchData
    #    Args: data : (dict)
    #              The plane data dictionary to validate.
    #  Raises: InvalidPlaneValueError
    #              This exception is raised when a render plane value is of a
    #              non-allowable value.
    # Returns: None
    #    Desc: Validate the match plane data to ensure all the values are
    #          legal.
    # -------------------------------------------------------------------------
    @staticmethod
    def _validateMatchData(data):
        for name, value in data.iteritems():
            # Check if there is a restriction on the data type.
            if name in _ALLOWABLE_VALUES:
                # Get the allowable types for this data.
                allowable = _ALLOWABLE_VALUES[name]

                # If the value isn't in the list, raise an exception.
                if value not in allowable:
                    raise InvalidPlaneValueError(name, value, allowable)

    # =========================================================================
    # INSTANCE PROPERTIES
    # =========================================================================

    @property
    def match(self):
        """(dict) Data to use when the pattern matches."""
        return self._match

    @property
    def nomatch(self):
        """(dict) Data to use when the pattern doesn match."""
        return self._nomatch

    @property
    def parmData(self):
        """(dict) Data about the parameter to match against."""
        return self._parmData

    @property
    def pattern(self):
        """(str) The regex pattern to match agains the parameter value."""
        return self._pattern

    # =========================================================================
    # METHODS
    # =========================================================================

    def getData(self, wrangler, cam, now):
        """Get the conditional data to apply.

        Args:
            wrangler : (Object)
                A wrangler object.

            cam : (soho.SohoObject)
                The camera being rendered.

            now : (float)
                The parameter evaluation time.

        Raises:
            N/A

        Returns:
            dict
                A dictionary of plane settings.

        This function matches the pattern against the specified parameter
        value and returns the corresponding match data.

        """
        import soho

        parmName = self.parmData["name"]

        # Build a dictionary containing the required SohoParm object.  We don't
        # want to skip defaults because if the parm is at its default we won't
        # be able to check against it.
        parms = {
            parmName: soho.SohoParm(
                parmName,
                self.parmData["type"],
                default=[self.parmData["default"]],
                skipdefault=False
            )
        }

        # Attempt to evaluate the parameter.
        plist = cam.wrangle(wrangler, parms, now)

        # Parameter exists and a value was found.
        if plist:
            # Get the parameter value.
            result = plist[parmName].Value[0]

            # Match the value against the pattern.  Return the corresponding
            # data.
            if re.match(self.pattern, result) is not None:
                return self.match

            else:
                return self.nomatch

        return {}


class RenderPlane(object):
    """An object representing an extra image plane for Mantra.

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, variable, filePath, data):
        """Initialize a RenderPlane object.

        Args:
            variable : (str)
                The name of the vex variable for the plane.

            filePath : (str)
                The path containing the plane definition.

            data : (dict)
                A dictionary containing render plane information.

        Raises:
            InvalidPlaneValueTypeError
                This exception is raised if a plane value error is not valid.

            MissingVexTypeError
                This exception is raised if there is no "vextype" entry in the
                data dictionary.

        Returns:
            N/A

        """
        self._variable = variable

        self._filePath = filePath

        self._conditionals = []

        # Plane information we care about.
        self._channel = None
        self._lightexport = None
        self._lightmask = None
        self._lightselection = None
        self._pfilter = None
        self._planefile = None
        self._quantize = "half"
        self._sfilter = "alpha"
        self._vextype = None

        # Process the dictionary.
        for name, value in data.iteritems():
            # If the value is None then the user specified a value of 'null'
            # and we should skip this option.
            if value is None:
                continue

            if name == "conditionals":
                continue

            # Check if there is a restriction on the data type.
            if name in _ALLOWABLE_VALUES:
                # Get the allowable types for this data.
                allowable = _ALLOWABLE_VALUES[name]

                # If the value isn't in the list, raise an exception.
                if value not in allowable:
                    raise InvalidPlaneValueError(name, value, allowable)

            # If the key corresponds to attributes on this object we store
            # the data.
            if hasattr(self, name):
                setattr(self, name, value)

        # If the vextype information wasn't specified, or was set to 'null',
        # raise an exception because it is mandatory.
        if self.vextype is None:
            raise MissingVexTypeError(variable)

        # Check for conditional settings.
        if "conditionals" in data:
            # Get the conditional data.
            conditionals = data["conditionals"]

            # Build PlaneConditionals and add them to our list.
            for conditionalData in conditionals:
                conditional = PlaneConditional(conditionalData)
                self.conditionals.append(conditional)

        # If no channel was specified, use the variable name.
        if self.channel is None:
            self.channel = self.variable

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def __repr__(self):
        return "<RenderPlane {0}>".format(self.variable)

    def __str__(self):
        return self.variable

    # =========================================================================
    # INSTANCE PROPERTIES
    # =========================================================================

    @property
    def channel(self):
        """(str) The name of the output plane's channel."""
        return self._channel

    @channel.setter
    def channel(self, channel):
        self._channel = channel

    @property
    def conditionals(self):
        """([RenderConditional]) RenderConditional objects for the plane."""
        return self._conditionals

    @property
    def filePath(self):
        """(str) The path containing the plane definition."""
        return self._filePath

    @filePath.setter
    def filePath(self, filePath):
        self._filePath = filePath

    @property
    def lightexport(self):
        """(str) The light output mode."""
        return self._lightexport

    @lightexport.setter
    def lightexport(self, lightexport):
        self._lightexport = lightexport

    @property
    def lightmask(self):
        """(str) The light mask."""
        return self._lightmask

    @lightmask.setter
    def lightmask(self, lightmask):
        self._lightmask = lightmask

    @property
    def lightselection(self):
        """(str) The light selection."""
        return self._lightselection

    @lightselection.setter
    def lightselection(self, lightselection):
        self._lightselection = lightselection

    @property
    def pfilter(self):
        """(str) The name of the output plane's pixel filter."""
        return self._pfilter

    @pfilter.setter
    def pfilter(self, pfilter):
        self._pfilter = pfilter

    @property
    def planefile(self):
        """(str) The name of the output plane's specific file, if any."""
        return self._planefile

    @planefile.setter
    def planefile(self, planefile):
        self._planefile = planefile

    @property
    def quantize(self):
        """(str) The type of quantization for the output plane."""
        return self._quantize

    @quantize.setter
    def quantize(self, quantize):
        self._quantize = quantize

    @property
    def sfilter(self):
        """(str) The name of the output plane's sample filter."""
        return self._sfilter

    @sfilter.setter
    def sfilter(self, sfilter):
        self._sfilter = sfilter

    @property
    def variable(self):
        """(str) The name of the output plane's vex variable."""
        return self._variable

    @property
    def vextype(self):
        """(str) The data type of the output plane."""
        return self._vextype

    @vextype.setter
    def vextype(self, vextype):
        self._vextype = vextype

    # =========================================================================
    # PUBLIC METHODS
    # =========================================================================

    def outputPlanes(self, wrangler, cam, now):
        """Output all necessary planes.

        Args:
            wrangler : (Object)
                A wrangler object.

            cam : (soho.SohoObject)
                The camera being rendered.

            now : (float)
                The parameter evaluation time.

        Raises:
            N/A

        Returns:
            None

        """
        import soho

        # The base data to pass along.
        data = {
            "variable": self.variable,
            "vextype": self.vextype,
            "channel": self.channel,
            "quantize": self.quantize,
            "planefile": self.planefile
        }

        if self.pfilter:
            data["pfilter"] = self.pfilter

        if self.sfilter:
            data["sfilter"] = self.sfilter

        # Apply any conditionals before the light export phase.
        if self.conditionals:
            for conditional in self.conditionals:
                data.update(conditional.getData(wrangler, cam, now))

        # Handle any light exporting.
        if self.lightexport is not None:
            # Get a list of lights matching out mask and selection.
            lights = cam.objectList(
                "objlist:light",
                now,
                self.lightmask,
                self.lightselection
            )

            if self.lightexport == "per-light":
                # Process each light.
                for light in lights:
                    # Try and find the suffix using the 'vm_export_suffix'
                    # parameter.  If it doesn't exist, use an emptry string.
                    suffix = light.getDefaultedString(
                        "vm_export_suffix", now, ['']
                    )[0]

                    prefix = []

                    # Look for the prefix parameter.  If it doesn't exist, use
                    # the light's name and replace the '/' with '_'.  The
                    # default value of 'vm_export_prefix' is usually $OS.
                    if not light.evalString("vm_export_prefix", now, prefix):
                        prefix = [light.getName()[1:].replace('/', '_')]

                    # If there is a prefix we construct the channel name using
                    # it and the suffix.
                    if prefix:
                        channel = "{0}_{1}{2}".format(
                            prefix[0],
                            self.channel,
                            suffix
                        )

                    # If not and there is a valid suffix, add it to the channel
                    # name.
                    elif suffix:
                        channel = "{0}{1}".format(self.channel, suffix)

                    # Throw an error because all the per-light channels will
                    # have the same name.
                    else:
                       soho.error("Empty suffix for per-light exports.")

                    data["channel"] = channel
                    data["lightexport"] = light.getName()

                    # Write this light export to the ifd.
                    self.writeToIfd(data, wrangler, cam, now)

            elif self.lightexport == "single":
                # Take all the light names and join them together.
                lightexport = ' '.join([light.getName() for light in lights])

                # If there are no lights, we can't pass in an empty string
                # since then mantra will think that light exports are
                # disabled.  So pass down an string that presumably doesn't
                # match any light name.
                if not lightexport:
                    lightexport = "__nolights__"

                data["lightexport"] = lightexport

                # Write the combined light export to the ifd.
                self.writeToIfd(data, wrangler, cam, now)

        else:
            # Write a normal plane definition.
            self.writeToIfd(data, wrangler, cam, now)


    @staticmethod
    def writeToIfd(data, wrangler, cam, now):
        """Write the plane to the ifd.

        Args:
            data : (dict)
                The data dictionary containing output information.

            wrangler : (Object)
                A wrangler object.

            cam : (soho.SohoObject)
                The camera being rendered.

            now : (float)
                The parameter evaluation time.

        Raises:
            N/A

        Returns:
            None

        """
        import IFDapi

        # Call the 'pre_defplane' hook.  If the function returns True,
        # return.
        if _callPreDefPlane(data, wrangler, cam, now):
            return

        # Start of plane block in IFD.
        IFDapi.ray_start("plane")

        # Primary block information.
        IFDapi.ray_property("plane", "variable", [data["variable"]])
        IFDapi.ray_property("plane", "vextype", [data["vextype"]])
        IFDapi.ray_property("plane", "channel", [data["channel"]])
        IFDapi.ray_property("plane", "quantize", [data["quantize"]])

        # Optional plane information.
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

        # Call the 'post_defplane' hook.
        if _callPostDefPlane(data, wrangler, cam, now):
            return

        # End the plane definition block.
        IFDapi.ray_end()


class RenderPlaneGroup(object):
    """An object representing a group of RenderPlane definitions.

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, name, filePath):
        """Initialize a RenderPlaneGroup.

        Args:
            name : (str)
                The name of the group.

            filePath : (str)
                The path containing the group definition.

        Raises:
            N/A

        Returns:
            N/A

        """
        self._name = name
        self._filePath = filePath
        self._planes = []

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __repr__(self):
        return "<RenderPlaneGroup {0} ({1} planes)>".format(
            self.name,
            len(self.planes)
        )

    def __str__(self):
        return self.name

    # =========================================================================
    # INSTANCE PROPERTIES
    # =========================================================================

    @property
    def filePath(self):
        """(str) The path containing the group definition."""
        return self._filePath

    @filePath.setter
    def filePath(self, filePath):
        self._filePath = filePath

    @property
    def name(self):
        """(str) The name of the group."""
        return self._name

    @property
    def planes(self):
        """([RenderPlane]) A list of RenderPlanes in the group."""
        return self._planes

    # =========================================================================
    # PUBLIC FUNCTIONS
    # =========================================================================

    def writePlanesToIfd(self, wrangler, cam, now):
        """Write all planes in the group to the ifd.

        Args:
            wrangler : (Object)
                A wrangler object.

            cam : (soho.SohoObject)
                The camera being rendered.

            now : (float)
                The parameter evaluation time.

        Raises:
            N/A

        Returns:
            None

        """
        for plane in self.planes:
            plane.outputPlanes(wrangler, cam, now)


# =============================================================================
# EXCEPTIONS
# =============================================================================

class InvalidPlaneValueError(Exception):
    """Exception for invalid plane setting values.

    """

    def __init__(self, name, value, allowable):
        super(InvalidPlaneValueError, self).__init__()
        self.allowable = allowable
        self.name = name
        self.value = value

    def __str__(self):
        return "Invalid value '{0}' in '{1}': Must be one of {2}".format(
            self.value,
            self.name,
            self.allowable
        )


class MissingVexTypeError(Exception):
    """Exception for missing 'vextype' information.

    """

    def __init__(self, variable):
        super(MissingVexTypeError, self).__init__()
        self.variable = variable

    def __str__(self):
        return "Cannot create plane {0}: missing 'vextype'.".format(
            self.variable
        )


# =============================================================================
# PRIVATE FUNCTIONS
# =============================================================================

# -----------------------------------------------------------------------------
#    Name: _callPostDefPlane
#    Args: data : (dict)
#              The plane data dictionary.
#          wrangler : (Object)
#              A wrangler object.
#          cam : (soho.SohoObject)
#              The camera being rendered.
#          now : (float)
#               The parameter evaluation time.
#  Raises: N/A
# Returns: bool
#              The result of the 'post_defplane' hook call.
#    Desc: Run the 'post_defplane' IFD hook.
# -----------------------------------------------------------------------------
def _callPostDefPlane(data, wrangler, cam, now):
    import IFDhooks

    return IFDhooks.call(
        "post_defplane",
        data["variable"],
        data["vextype"],
        -1,
        wrangler,
        cam,
        now,
        data["planefile"],
        data.get("lightexport")
    )


# -----------------------------------------------------------------------------
#    Name: _callPreDefPlane
#    Args: data : (dict)
#              The plane data dictionary.
#          wrangler : (Object)
#              A wrangler object.
#          cam : (soho.SohoObject)
#              The camera being rendered.
#          now : (float)
#               The parameter evaluation time.
#  Raises: N/A
# Returns: bool
#              The result of the 'pre_defplane' hook call.
#    Desc: Run the 'pre_defplane' IFD hook.
# -----------------------------------------------------------------------------
def _callPreDefPlane(data, wrangler, cam, now):
    import IFDhooks

    return IFDhooks.call(
        "pre_defplane",
        data["variable"],
        data["vextype"],
        -1,
        wrangler,
        cam,
        now,
        data["planefile"],
        data.get("lightexport")
    )


# -------------------------------------------------------------------------
#    Name: _convertFromUnicode
#    Args: data : (object)
#              An object to try to convert.
#  Raises: N/A
# Returns: object
#              The converted object.
#    Desc: Convert any unicode members to normal strings.
# -------------------------------------------------------------------------
def _convertFromUnicode(data):
    # If the data is a dictionary we need to convert the key/value pairs
    # and return a new dictionary.
    if isinstance(data, dict):
        return dict(
            [
                (_convertFromUnicode(key), _convertFromUnicode(value))
                 for key, value in data.iteritems()
            ]
        )

    # Convert any elements in a list.
    elif isinstance(data, list):
        return [_convertFromUnicode(element) for element in data]

    # The data is a unicode string, so encode it to a regular one.
    elif isinstance(data, unicode):
        return data.encode('utf-8')

    # Return the untouched data.
    else:
        return data


# -----------------------------------------------------------------------------
#    Name: _findPlaneDefinitions
#  Raises: N/A
# Returns: dict
#              A dictionary whose keys are render plane names and values are
#              are the corresponding RenderPlane objects.
#    Desc: Build a list of all available RenderPlane definitions.
# -----------------------------------------------------------------------------
def _findPlaneDefinitions():
    # Look for any plane definition files in the Houdini path.
    try:
        defFiles = hou.findFiles("soho/planes/definitions.json")

    # Couldn't find any so return an empty dictionary.
    except hou.OperationFailed:
        return {}

    # Mapping between plane names and the corresponding RenderPlane object.
    defMap = {}

    # Process each definition file.
    for filePath in defFiles:
        # Load the json file.
        f = open(filePath)
        data = json.load(f)
        f.close()

        # Convert from unicode to regular strings.
        data = _convertFromUnicode(data)

        # Process each plane definition.
        for planeName, planeData in data.iteritems():
            # If a plane of the same name has already been processed, skip it.
            if planeName in defMap:
                continue

            # Build the plane.
            plane = RenderPlane(planeName, filePath, planeData)

            # Store a reference to the plane based on the name in the map.
            defMap[planeName] = plane

    return defMap


# -----------------------------------------------------------------------------
#    Name: _findPlaneGroups
#  Raises: N/A
# Returns: dict
#              A dictionary whose keys are render plane group names and values
#              are the path to the defining file.
#    Desc: Build a list of all available RenderPlaneGroups found.
# -----------------------------------------------------------------------------
def _findPlaneGroups():
    # Mapping between plane group names and their source files.
    groupMap = {}

    # Look for planes throughout the Houdini path.
    for path in hou.houdiniPath():
        # Look for any json files in soho/planes/ dirs.
        files = glob.glob(os.path.join(path, "soho/planes/*.json"))

        for filePath in files:
            baseName = os.path.basename(filePath)

            # The file isn't a definitions file processed elsewhere.
            if baseName != "definitions.json":
                # The group name is the name of the file.
                groupName = os.path.splitext(baseName)[0]

                # If we haven't seen this group yet, add it to the map.
                if groupName not in groupMap:
                    groupMap[groupName] = filePath

    return groupMap


# -----------------------------------------------------------------------------
#    Name: _disablePlanes
#    Args: wrangler : (Object)
#              A wrangler object, if any.
#          cam : (soho.SohoObject)
#              The camera being rendered.
#          now : (float)
#               The parameter evaluation time.
#  Raises: N/A
# Returns: bool
#              Returns True if automatic planes should be disabled, otherwise
#              False.
#    Desc: Check if automatic planes should be disabled.  This function looks
#          for the value of the 'disable_auto_planes' parameter.
# -----------------------------------------------------------------------------
def _disablePlanes(wrangler, cam, now):
    import soho

    # The parameter that defines if planes should be disabled or not.
    parms = {"disable": soho.SohoParm("disable_auto_planes", "int", [False])}

    # Attempt to evaluate the parameter.
    plist = cam.wrangle(wrangler, parms, now)

    # Parameter exists.
    if plist:
        # If the parameter is set, return True to disable the planes.
        if plist["disable"].Value[0] == 1:
            return True

    return False


# =============================================================================
# FUNCTIONS
# =============================================================================

def addRenderPlanes(wrangler, cam, now):
    """Adds deep rasters as defined by a json file.

    Args:
        wrangler : (Object)
            A wrangler object, if any.

        cam : (soho.SohoObject)
            The camera being rendered.

        now : (float)
            The parameter evaluation time.

    Raises:
        N/A

    Returns:
        None

    """
    import soho

    # Check if automatic planes should be disabled.
    if _disablePlanes(wrangler, cam, now):
        return

    # The parameter that defines which automatic planes to add.
    parms = {"auto_planes": soho.SohoParm("auto_planes", "str", [""])}

    # Attempt to evaluate the parameter.
    plist = cam.wrangle(wrangler, parms, now)

    # Parameter exists.
    if plist:
        # Get the string value.
        planeStr = plist["auto_planes"].Value[0]

        if planeStr:
            # Split the string to get the group names.
            planeList = planeStr.split()

            # Build all existing groups.
            groups = buildPlaneGroups()

            # For each group available, if it matches the selection of groups
            # to add, write the planes to the ifd.
            for group in groups:
                if group.name in planeList:
                    group.writePlanesToIfd(wrangler, cam, now)


def buildPlaneGroups():
    """Build a list of all available RenderPlaneGroups found.

    Raises:
        N/A

    Returns:
        [RenderPlaneGroup]
            A list of found RenderPlaneGroups.

    """
    planeDefinitions = _findPlaneDefinitions()

    planeGroups = _findPlaneGroups()

    groups = []

    # Process each file name/path.
    for filePath in planeGroups.itervalues():
        # Load the json file.
        f = open(filePath)
        data = json.load(f)
        f.close()

        # Convert from unicode to regular strings.
        data = _convertFromUnicode(data)

        # Get the group name.
        groupName = data["name"]

        # Build a new group object.
        group = RenderPlaneGroup(groupName, filePath)

        definedDefinitions = {}

        if "define" in data:
            defines = data["define"]

            for planeName, planeData in defines.iteritems():
                # If a plane of the same name has already been processed, skip
                # it.
                if planeName in definedDefinitions:
                    continue

                # Build the plane.
                plane = RenderPlane(planeName, filePath, planeData)

                # Store a reference to the plane based on the name in the map.
                definedDefinitions[planeName] = plane

                group.planes.append(plane)

        if "include" in data:
            # Look for any planes to include.
            includes = data["include"]

            for planeName, enabled in includes.iteritems():
                # Skip disabled planes.
                if not enabled:
                    continue

                if planeName in definedDefinitions:
                    continue

                # If the plane is defined, add it to the group's list of
                # planes.
                if planeName in planeDefinitions:
                    plane = planeDefinitions[planeName]
                    group.planes.append(plane)

        # Add this group to the list.
        groups.append(group)

    return groups

