"""This module contains classes and functions used to build Mantra image planes
based on definitions in files.

Synopsis
========

Classes:
    RenderPlane
        An object representing an extra image plane for Mantra.

    RenderPlaneGroup
        An object representing a group of RenderPlane definitions.

Exceptions:
    MissingVexTypeError
        Exception for a 'vextype' information.

Functions:
    addRenderPlanes()
        Adds deep rasters as defined by a .json file.

Description
===========

By default, the automatic planes system uses planes defined in a string
parameter 'auto_planes'.  In this parameter you can specify groups of planes
that should be added.  Before attempting to add the planes it verifies that
they are not disabled by checking the 'disable_auto_planes' parameter.

"""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import glob
import json
import os

# Houdini Imports
import IFDapi
import IFDhooks
import hou
import soho

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MissingVexTypeError",
    "RenderPlane",
    "RenderPlaneGroup",
    "addRenderPlanes",
]

# =============================================================================
# CLASSES
# =============================================================================

class RenderPlane(object):
    """An object representing an extra image plane for Mantra."""

    def __init__(self, variable, data):
        """Create a new RenderPlane object.

        Args:
            variable : (str)
                The name of the vex variable for the plane.

            data : (dict)
                A dictionary containing render plane information.

        Raises:
            MissingVexTypeError
                This exception is raised if there is no "vextype" entry
                in the data dictionary.

        Returns:
            N/A

        """
	self._variable = str(variable)

        # If there is no 'vextype' data in the dictionary we need to raise
        # an exception.
        if "vextype" not in data:
            raise MissingVexTypeError(str(variable))

        # Remove the data from the dictionary and store it.
	self._vextype = str(data.pop("vextype"))

        # Plane information we care about.
	self._channel = None
	self._lightexport = None
	self._pfilter = None
	self._planefile = None
	self._quantize = "half"
	self._sfilter = "alpha"

        # TODO: Verify values?

        # Process the dictionary.  If any of the keys correspond to attributes
        # on this object we store their data.
	for name, value in data.iteritems():
	    if hasattr(self, name):
		setattr(self, name, str(value))

        # If no channel was specified, use the variable name.
        if self.channel is None:
            self.channel = self.variable

        # TODO: Light export stuff?

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __repr__(self):
        return "<RenderPlane {0}>".format(self.variable)

    def __str__(self):
        return self.variable

    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================

    # -------------------------------------------------------------------------
    #    Name: _callPostDefPlane
    #    Args: wrangler : (Object)
    #              A wrangler object.
    #          cam : (soho.SohoObject)
    #              The camera being rendered.
    #          now : (float)
    #               The parameter evaluation time.
    #  Raises: N/A
    # Returns: None
    #    Desc: Run the 'post_defplane' IFD hook.
    # -------------------------------------------------------------------------
    def _callPostDefPlane(self, wrangler, cam, now):
	IFDhooks.call(
	    "post_defplane",
	    self.variable,
	    self.vextype,
	    -1,
	    wrangler,
	    cam,
	    now,
	    self.planefile,
	    self.lightexport
	)

    # -------------------------------------------------------------------------
    #    Name: _callPreDefPlane
    #    Args: wrangler : (Object)
    #              A wrangler object.
    #          cam : (soho.SohoObject)
    #              The camera being rendered.
    #          now : (float)
    #               The parameter evaluation time.
    #  Raises: N/A
    # Returns: bool
    #              The result of the 'pre_defplane' hook call.
    #    Desc: Run the 'pre_defplane' IFD hook.
    # -------------------------------------------------------------------------
    def _callPreDefPlane(self, wrangler, cam, now):
	return IFDhooks.call(
	    "pre_defplane",
	    self.variable,
	    self.vextype,
	    -1,
	    wrangler,
	    cam,
	    now,
	    self.planefile,
	    self.lightexport
	)

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
    def lightexport(self):
	return self._lightexport

    @lightexport.setter
    def lightexport(self, lightexport):
	self._lightexport = lightexport

    @property
    def pfilter(self):
        """(str) The name of the output plane's pixel filter."""
	return self._pfilter

    @pfilter.setter
    def pfilter(self, pfilter):
	self._pfilter = pfilter

    @property
    def planefile(self):
        """(str|None) The name of the output plane's specific file, if any."""
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

    # =========================================================================
    # PUBLIC METHODS
    # =========================================================================

    def writeToIfd(self, wrangler, cam, now):
        """Write the plane to the ifd.

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
        # Call the 'pre_defplane' hook.  If the function returns True,
        # return.
	if self._callPreDefPlane(wrangler, cam, now):
	    return

        # Start of plane block in IFD.
	IFDapi.ray_start("plane")

        # Primary block information.
        IFDapi.ray_property("plane", "variable", [self.variable])
        IFDapi.ray_property("plane", "vextype", [self.vextype])
        IFDapi.ray_property("plane", "channel", [self.channel])
        IFDapi.ray_property("plane", "quantize", [self.quantize])

        # Optional plane information.
	if self.planefile is not None:
	    IFDapi.ray_property("plane", "planefile", [self.planefile])

	if self.lightexport is not None:
	    IFDapi.ray_property("plane", "lightexport", [self.lightexport])

	if self.pfilter:
	    IFDapi.ray_property("plane", "pfilter", [self.pfilter])
	
	if self.sfilter:
	    IFDapi.ray_property("plane", "sfilter", [self.sfilter])
	
        # Call the 'post_defplane' hook.
	self._callPostDefPlane(wrangler, cam, now)

        # End the plane definition block.
	IFDapi.ray_end()


class RenderPlaneGroup(object):
    """An object representing a group of RenderPlane definitions."""

    def __init__(self, name):
        """Create a new RenderPlaneGroup.

        Args:
            name : (str)
                The name of the group.

        Raises:
            N/A

        Returns:
            N/A

        """
	self._name = name
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
	    plane.writeToIfd(wrangler, cam, now)


# =============================================================================
# EXCEPTIONS
# =============================================================================

def MissingVexTypeError(Exception):
    """Exception for a 'vextype' information."""

    def __init__(self, variable):
        self.variable = variable

    def __str__(self):
        return "Cannot create plane {0}: missing 'vextype'.".format(
            self.variable
        )


# =============================================================================
# PRIVATE FUNCTIONS
# =============================================================================

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

        # Process each plane definition.
        for planeName, planeData in data.iteritems():
            # If a plane of the same name has already been processed, skip it.
            if planeName in defMap:
                continue

            # Build the plane.
            plane = RenderPlane(planeName, planeData)

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
#    Name: _buildPlaneGroups
#  Raises: N/A
# Returns: [RenderPlaneGroup]
#              A list of found RenderPlaneGroups.
#    Desc: Build a list of all available RenderPlaneGroups found.
# -----------------------------------------------------------------------------
def _buildPlaneGroups():
    planeDefinitions = _findPlaneDefinitions()

    planeGroups = _findPlaneGroups()

    groups = []

    # Process each file name/path.
    for fileName, filePath in planeGroups.iteritems():
        # Load the json file.
        f = open(filePath)
        data = json.load(f)
        f.close()

        # Get the group name.
        groupName = data["name"]

        # Build a new group object.
        group = RenderPlaneGroup(groupName)

        definedDefinitions = {}

        if "define" in data:
            defines = data["define"]

            for planeName, planeData in defines.iteritems():
                # If a plane of the same name has already been processed, skip
                # it.
                if planeName in definedDefinitions:
                    continue

                # Build the plane.
                plane = RenderPlane(planeName, planeData)

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


# -----------------------------------------------------------------------------
#    Name: _disablePlanes
#    Args: wrangler : (Object|None)
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
        wrangler : (Object|None)
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
	    groups = _buildPlaneGroups()

            # For each group available, if it matches the selection of groups
            # to add, write the planes to the ifd.
	    for group in groups:
		if group.name in planeList:
		    group.writePlanesToIfd(wrangler, cam, now)

