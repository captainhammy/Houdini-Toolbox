"""This module contains classes and functions related to Houdini builds.

Synopsis
--------

Classes:
    HoudiniBase
        This class represents a Houdini build on disk.

    HoudiniBuildManager
        This class provides an interface for accessing installable and
        installed Houdini builds.

    HoudiniInstall
        This class represents an installed Houdini build.

    HoudiniPackage
        This class represents a Houdini install package.

Exceptions:
    BuildAlreadyInstalledError
        Exception raised when a build is already installed.

Functions:
    setVar(name, value):
        Set an environment variable.

"""
__author__ = "Graham Thompson"
__email__ = "captainhammy@gmail.com"


# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import glob
import json
from operator import attrgetter
import os
import re
import shutil
import subprocess
import tarfile
import tempfile

# Houdini Toolbox Imports
import ht.utils

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "BuildAlreadyInstalledError",
    "HoudiniBase",
    "HoudiniBuildManager",
    "HoudiniInstall",
    "HoudiniPackage",
]

# =============================================================================
# NON-PUBLIC CLASSES
# =============================================================================

class _HoudiniEnvironmentSettings(object):
    """This class stores environment settings.

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, data):
        """Initialize a _HoudiniEnvironmentSettings object.

        Args:
            data : (dict)
                A dictionary of environment data.

        Raises:
            N/A

        Returns:
            N/A

        """
        self._variables = data.get("variables", [])
        self._paths = data.get("paths", {})

    # =========================================================================
    # INSTANCE PROPERTIES
    # =========================================================================

    @property
    def variables(self):
        """(dict) A dictionary of environment variables to set."""
        return self._variables

    @property
    def paths(self):
        """(dict) A dictionary of paths to set."""
        return self._paths


class _HoudiniInstallationSettings(object):
    """This class stores Houdini installation settings.

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, data):
        """Initialize a _HoudiniInstallationSettings object.

        Args:
            data : (dict)
                A dictionary of installation data.

        Raises:
            N/A

        Returns:
            N/A

        """
        self._directory = data["directory"]
        self._prefix = data["prefix"]

    # =========================================================================
    # INSTANCE PROPERTIES
    # =========================================================================

    @property
    def directory(self):
        """(str) The base path to install Houdini to."""
        return self._directory

    @property
    def prefix(self):
        """(str) The folder prefix to install Houdini to."""
        return self._prefix


class _HoudiniPluginSettings(object):
    """This class stores Houdini plugin settings.

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, data):
        """Initialize a _HoudiniPluginSettings object.

        Args:
            data : (dict)
                A dictionary of plugin data.

        Raises:
            N/A

        Returns:
            N/A

        """
        self._directory = data["directory"]
        self._prefix = data["prefix"]

        self._root = None
        self._command = None

    # =========================================================================
    # INSTANCE PROPERTIES
    # =========================================================================

    @property
    def directory(self):
        """(str) The base path to the Houdini plugin directory."""
        return self._directory

    @property
    def prefix(self):
        """(str) The folder prefix for Houdini plugins."""
        return self._prefix


class _HoudiniSettingsManager(object):
    """This class manages Houdini package settings.

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self):
        """Initialize a _HoudiniSettingsManager object.

        Raises:
            N/A

        Returns:
            N/A

        """
        self._environment = None
        self._system = None

        # Look for the package.json file in the same directory as this module.
        path = os.path.join(os.path.dirname(__file__), "package.json")

        # Couldn't find it so we have nothing left to do.
        if not os.path.exists(path):
            return

        with open(path) as f:
            # Get the json data.
            data = json.load(f, object_hook=ht.utils.convertFromUnicode)

            # Consturct settings objects for available data.
            if "environment" in data:
                self._environment = _HoudiniEnvironmentSettings(
                    data["environment"]
                )

            if "system" in data:
                self._system = _HoudiniSystemSettings(data["system"])

    # =========================================================================
    # INSTANCE PROPERTIES
    # =========================================================================

    @property
    def environment(self):
        """(_HoudiniEnvironmentSettings) Houdini environment settings."""
        return self._environment

    @property
    def system(self):
        """(_HoudiniSystemSettings) Houdini environment settings."""
        return self._system


class _HoudiniSystemSettings(object):
    """This class stores Houdini system settings.

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, data):
        """Initialize a _HoudiniSystemSettings object.

        Args:
            data : (dict)
                A dictionary of system data.

        Raises:
            N/A

        Returns:
            N/A

        """
        self._locations = None
        self._plugins = None

        self._locations = data["locations"]

        self._installation = _HoudiniInstallationSettings(data["installation"])

        # Plugin data is optional.
        if "plugins" in data:
            self._plugins = _HoudiniPluginSettings(data["plugins"])

    # =========================================================================
    # INSTANCE PROPERTIES
    # =========================================================================

    @property
    def installation(self):
        """(_HoudiniInstallationSettings) Houdini installation settings."""
        return self._installation

    @property
    def locations(self):
        """([str]) A list of locations to search for installable packages."""
        return self._locations

    @property
    def plugins(self):
        """(_HoudiniPluginSettings) Houdini plugin settings."""
        return self._plugins


# =============================================================================
# CLASSES
# =============================================================================

class HoudiniBase(object):
    """This class represents a Houdini build on disk.

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, path, major, minor, build, candidate=None):
        """Initialize a HoudiniBase object.

        Args:
            path : (str)
                The path to the package on disk.

            major : (int)
                The Houdini major version number.

            minor : (int)
                The Houdini minor version number.

            build : (int)
                The Houdini build number.

            candidate=None : (int)
                The Houdini release candidate number.

        Raises:
            N/A

        Returns:
            N/A

        """
        self._path = path

        self._major = major
        self._minor = minor
        self._build = build
        self._candidate = candidate

        self._pluginPath = None

        if _SETTINGS.system.plugins is not None:
            # Generate the path to install the build to.
            self._pluginPath = os.path.join(
                    _SETTINGS.system.plugins.directory,
                    "{prefix}{version}".format(
                        prefix=_SETTINGS.system.plugins.prefix,
                        version=self
                    )
                )

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __eq__(self, other):
        # Two objects are equal if their Houdini versions are equal.
        return str(self) == str(other)

    def __repr__(self):
        return "<{name} {version} @ {path}>".format(
            name=self.__class__.__name__,
            version=str(self),
            path=self.path
        )

    def __str__(self):
        version = "{major}.{minor}.{build}".format(
            major=self.major,
            minor=self.minor,
            build = self.build
        )

        if self.candidate is not None:
            version = "{version}.{candidate}".format(
                version=version,
                candidate=self.candidate
            )

        return version

    # =========================================================================
    # INSTANCE PROPERTIES
    # =========================================================================

    @property
    def build(self):
        """(int) The build number for this build. """
        return self._build

    @property
    def candidate(self):
        """(int) The release candidate number for this build. """
        return self._candidate

    @property
    def major(self):
        """(int) The major number for this build. """
        return self._major

    @property
    def minor(self):
        """(int) The minor number for this build. """
        return self._minor

    @property
    def path(self):
        """(str) The file path on disk of the build. """
        return self._path

    @property
    def pluginPath(self):
        """(str) The location of any plugins for this build."""
        return os.path.expandvars(self._pluginPath)

    @property
    def version(self):
        """((int)) A tuple containing version information. """
        version = [self.major, self.minor, self.build]

        # Add the candidate number if necessary.
        if self.candidate is not None:
            version.append(self.candidate)

        return tuple(version)


class HoudiniBuildManager(object):
    """This class provides an interface for accessing installable and installed
    Houdini builds.

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self):
        self._installable = []
        self._installed = []

        self._installDirectory = _SETTINGS.system.installation.directory
        self._installPrefix = _SETTINGS.system.installation.prefix

        self._getInstalledBuilds()
        self._getInstallablePackages()

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __repr__(self):
        return "<HoudiniBuildManager>"

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    # -------------------------------------------------------------------------
    #    Name: _getInstallablePackages
    #  Raises: N/A
    # Returns: None
    #    Desc: Populate the installable build lists.
    # -------------------------------------------------------------------------
    def _getInstallablePackages(self):
        files = []

        # We need to glob in each directory for houdini installation packages.
        for directory in _SETTINGS.system.locations:
            filePath = os.path.join(directory, "houdini*-*.*.*.tar.gz")

            # Add any found files to the list.
            files += glob.glob(os.path.expandvars(filePath))

        # Convert all the files into HoudiniPackage objects.
        self._installable = [HoudiniPackage(path) for path in files]

        # Sort the builds by their version number.
        self.installable.sort(key=attrgetter("version"))

    # -------------------------------------------------------------------------
    #    Name: _getInstalledPackages
    #  Raises: N/A
    # Returns: None
    #    Desc: Populate the installed build lists.
    # -------------------------------------------------------------------------
    def _getInstalledBuilds(self):
        # Glob in the base install location for installed Houdini builds.
        paths = glob.glob(
            os.path.join(
                self._installDirectory,
                "{prefix}*.*.*".format(prefix=self._installPrefix)
            )
        )

        # Convert all the install directories to HoudiniInstall objects.
        self._installed = [HoudiniInstall(path) for path in paths]

        self.installed.sort(key=attrgetter("version"))

    # =========================================================================
    # INSTANCE PROPERTIES
    # =========================================================================

    @property
    def installable(self):
        """((HoudiniPackage)) A tuple of installable Houdini builds."""
        return self._installable

    @property
    def installed(self):
        """((HoudiniInstall)) A tuple of installed Houdini builds."""
        return self._installed


class HoudiniInstall(HoudiniBase):
    """This class represents an installed Houdini build.

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, path):
        """Initialize a HoudiniInstall object.

        Args:
            path : (str)
                The path to the installation on disk.

        Raises:
            N/A

        Returns:
            N/A

        """
        # Extract the build version numbers from the directory name.
        result = re.search("([0-9\.]+)", os.path.basename(path))

        versionString = result.group(0)

        # Get the build number components.
        components = [int(val) for val in versionString.split(".")]

        # If we have 4 then we have a release candidate.
        if len(components) == 4:
            major, minor, build, candidate = components

        # Otherwise a normal build.
        else:
            major, minor, build = components
            candidate = None

        # Create our parent HoudiniBase object.
        super(HoudiniInstall, self).__init__(
            path,
            major,
            minor,
            build,
            candidate
        )

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    # -------------------------------------------------------------------------
    #    Name: _setCustomPaths
    #  Raises: N/A
    # Returns: None
    #    Desc: Set any custom paths specified in ht config settings.
    # -------------------------------------------------------------------------
    def _setCustomPaths(self):
        for variable, value in _SETTINGS.environment.paths.iteritems():
            setVar(variable, ":".join(value))

    # -------------------------------------------------------------------------
    #    Name: _setCustomVariables
    #  Raises: N/A
    # Returns: None
    #    Desc: Set any additional environment variables specified in ht config
    #          settings.
    # -------------------------------------------------------------------------
    def _setCustomVariables(self):
        for variable, value in _SETTINGS.environment.variables.iteritems():
            setVar(variable, value)

    # -------------------------------------------------------------------------
    #    Name: _setupDefaultEnvironment
    #  Raises: N/A
    # Returns: None
    #    Desc: This function will initialize the environment variables
    #          necessary to run applications.  This is equivalent to sourcing
    #          the houdini_setup file located in $HFS.
    # -------------------------------------------------------------------------
    def _setupDefaultEnvironment(self):
        # The base Houdini location.
        hfs = self.path

        setVar("HFS", hfs)
        setVar("H", hfs)

        # Build and set bin vars.
        HB = "${HFS}/bin"
        setVar("HB", HB)

        HSB = "${HFS}/houdini/sbin"
        setVar("HSB", HSB)

        # Set additional location variables.
        setVar("HDSO", "${HFS}/dsolib")
        setVar("HD", "${HFS}/demo")
        setVar("HH", "${HFS}/houdini")
        setVar("HHC", "${HFS}/houdini/config")
        setVar("HT", "${HFS}/toolkit")

        if not "TEMP" in os.environ:
            setVar("TEMP", tempfile.gettempdir())

        # Set variables with the version information.
        setVar("HOUDINI_MAJOR_RELEASE", self.major)
        setVar("HOUDINI_MINOR_RELEASE", self.minor)
        setVar("HOUDINI_BUILD_VERSION", self.build)
        setVar("HOUDINI_VERSION", self)

        # Get the current PATH.
        PATH = os.environ["PATH"]

        # Insert the Houdini bin directories at the head of the PATH.
        setVar("PATH", [HB, HSB, PATH])

    # =========================================================================
    # METHODS
    # =========================================================================

    def setupEnvironment(self, allowCustom=True):
        """Setup the environment in order to run this build.

        Args:
            allowCustom=True : (bool)
                Set custom environment settings.

        Raises:
            N/A

        Returns:
            None

        """
        # Run the default environment setup.
        self._setupDefaultEnvironment()

        # Run custom setup if allowed.
        if allowCustom:
            # Set a variable containing the plugin path, if it exists.
            if self.pluginPath is not None:
                os.environ["HOUDINI_PLUGIN_PATH"] = self.pluginPath

            # Set any variables.
            self._setCustomVariables()

            # Set paths after variables in case any paths use the variables.
            self._setCustomPaths()

    def uninstall(self):
        """Uninstall the Houdini build.

        Raises:
            N/A

        Returns:
            None

        This function will remove the install directory and optionally
        remove any compiled operators for the build.

        """
        print "Removing installation directory {path}".format(
            path=self.path
        )

        shutil.rmtree(self.path)

        # If there are plugins, remove them.
        if self.pluginPath is not None:
            if os.path.isdir(self.pluginPath):
                print "Removing compiled operators in {path}".format(
                    path=self.pluginPath
                )

                shutil.rmtree(self.pluginPath)


class HoudiniPackage(HoudiniBase):
    """This class represents an installable Houdini package.

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self, path):
        """Initialize a HoudiniInstall object.

        Args:
            path : (str)
                The path to the installable archive on disk.

        Raises:
            N/A

        Returns:
            N/A

        """
        result = re.match("houdini.*-([0-9\.]*)-", os.path.basename(path))

        versionString = result.group(1)

        # Get the build number components.
        components = [int(val) for val in versionString.split(".")]

        # If we have 4 then we have a release candidate.
        if len(components) == 4:
            major, minor, build, candidate = components

        # Otherwise a normal build.
        else:
            major, minor, build = components
            candidate = None

        # Create our parent HoudiniBase object.
        super(HoudiniPackage, self).__init__(
            path,
            major,
            minor,
            build,
            candidate
        )

        self._installDirectory = _SETTINGS.system.installation.directory
        self._installPrefix = _SETTINGS.system.installation.prefix

    # =========================================================================
    # METHODS
    # =========================================================================

    def install(self):
        """Install this package to the install directory.

        Raises:
            BuildAlreadyInstalledError
                This exception is raised when the target directory already
                exists.

        Returns:
            None

        To install we need to extract the contents to a temp directory.  We
        can then run the shipped installer script to properly install Houdini.
        Afterwards we remove the temp directory.

        """
        # Let our system tell us where we can store the temp files.
        tempPath = tempfile.gettempdir()

        # Generate the path to install the build to.
        installPath = os.path.join(
                self._installDirectory,
                "{prefix}{version}".format(
                    prefix=self._installPrefix,
                    version=self
                )
            )

        # Check to see if the build is already installed.  If it is
        # we throw an exception.
        if os.path.exists(installPath):
            raise BuildAlreadyInstalledError(str(self))

        print "Extracting {archive} to {path}".format(
            archive=self.path,
            path=tempPath
        )

        # Open the tar file that this object represents and extract
        # everything to our temp directory, closing the file afterwards.
        # TODO: Use with statement when moving fully to Python 2.7.
        tar = tarfile.open(self.path, "r:gz")
        tar.extractall(tempPath)
        tar.close()

        # Store the archive file name, minus the file extensions.
        archiveName = os.path.basename(self.path).replace(".tar.gz", "")

        # Build the path to the newly extracted tarball.
        extractPath = os.path.join(tempPath, archiveName)

        # Execute the Houdini install script.
        print "Running Houdini installer."

        cmdArgs = (
            "{path}/houdini.install".format(path=extractPath),
            "--no-license",
            "--no-menus",
            "--accept-EULA",
            "--make-dir",
            installPath
        )

        subprocess.call(cmdArgs)

        # Remove the temporary extraction directory.
        print "Removing temporary install files."
        shutil.rmtree(extractPath)

        # Notify that the build installation has completed.
        print "Installation of Houdini {version} complete.".format(
            version=self
        )


# =============================================================================
# EXCEPTIONS
# =============================================================================

class BuildAlreadyInstalledError(Exception):
    """Exception raised when a build is already installed.

    """

    def __init__(self, build):
        self.build = build

    def __str__(self):
        return "Houdini {build} is already installed.".format(
            build=self.build
        )

# =============================================================================
# FUNCTIONS
# =============================================================================

def setVar(name, value):
    """Set an environment variable.

    Args:
        name : (str)
            The name of the environment variable.

        value : (object)
            The value of the variable.  This can be a string, number or list
            of strings.  If the value is a list, they will be joined together
            with a ':'.

    Raises:
        N/A

    Returns:
        None

    This function will automatically expand any variables in the value before
    setting.

    """
    # If the value is a list, join the entries together.
    if isinstance(value, (list, tuple)):
        value = ":".join(value)

    # Convert the value to a string since that is the data type that must be
    # used when setting environment variables.
    else:
        value = str(value)

    # Expand any variables in the value.
    value = os.path.expandvars(value)

    os.environ[name] = value

# =============================================================================
# CONSTANTS
# =============================================================================

# Build settings for common use by all Houdini objects.
_SETTINGS = _HoudiniSettingsManager()

