"""This module contains classes and functions related to Houdini builds."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
from datetime import datetime
import glob
import json
from operator import attrgetter
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

# Third Party Imports
from mechanize import Browser, LinkNotFoundError

# Houdini Toolbox Imports
import ht.utils

# =============================================================================
# GLOBALS
# =============================================================================

BUILD_DATA_FILE = "build_data.json"
PACKAGE_CONFIG_FILE = "houdini_package_config.json"

# =============================================================================
# CLASSES
# =============================================================================


class HoudiniBase(object):
    """This class represents a Houdini build on disk.

    """

    def __init__(self, path, version):
        self._path = path

        self._major, self._minor, self._build, self._candidate = version

        self._plugin_path = None

        if SETTINGS.system.plugins is not None:
            plugin_folder = self.formatString(
                SETTINGS.system.plugins.folder
            )

            # Generate the path to install the build to.
            self._plugin_path = os.path.join(
                SETTINGS.system.plugins.target,
                plugin_folder
            )

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __eq__(self, other):
        # Two objects are equal if their Houdini versions are equal.
        return str(self) == str(other)

    def __repr__(self):
        return "<{} {} @ {}>".format(
            self.__class__.__name__,
            str(self),
            self.path
        )

    def __str__(self):
        version = "{}.{}.{}".format(
            self.major,
            self.minor,
            self.build
        )

        if self.candidate is not None:
            version = "{}.{}".format(
                version,
                self.candidate
            )

        return version

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def build(self):
        """The build number for this build. """
        return self._build

    @property
    def candidate(self):
        """The release candidate number for this build. """
        return self._candidate

    @property
    def major(self):
        """The major number for this build. """
        return self._major

    @property
    def major_minor(self):
        """The major number for this build. """
        return "{}.{}".format(self.major, self.minor)

    @property
    def minor(self):
        """The minor number for this build. """
        return self._minor

    @property
    def path(self):
        """The file path on disk of the build. """
        return self._path

    @property
    def plugin_path(self):
        """The location of any plugins for this build."""
        return os.path.expandvars(self._plugin_path)

    @property
    def version(self):
        """A tuple containing version information. """
        version = [self.major, self.minor, self.build]

        # Add the candidate number if necessary.
        if self.candidate is not None:
            version.append(self.candidate)

        return tuple(version)

    # =========================================================================
    # METHODS
    # =========================================================================

    def formatString(self, value):
        """Format a string given information about this build."""
        args = {
            "version": str(self),
            "major": self.major,
            "minor": self.minor,
            "major_minor": self.major_minor,
            "build": self.build,
            "candidate": self.candidate,
        }

        return value.format(**args)


class HoudiniBuildData(object):
    """This class stores Houdini build data.

    """

    def __init__(self, data):
        self._file_template = data["file_template"]
        self._types = data["types"]
        self._versions = data["versions"]

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _formatVersionTemplate(self, build_number, arch=None):
        """Format the file template for the build number and architecture."""
        system = platform.system()

        type_info = self.types[system]

        # Use the "default" architecture for this system.
        if arch is None:
            arch = type_info["arch"]

        return self.file_template.format(
            version=build_number,
            arch=arch,
            ext=type_info["ext"]
        )

    def _getSpecificArchForBuild(self, major_minor):
        """Check for a specific machine architecture for a build."""
        version_data = self.versions[major_minor]

        system = platform.system()

        if "types" in version_data:
            type_data = version_data["types"]

            if system in type_data:
                return type_data[system].get("arch")

            raise UnsupportedMachineArchitectureError(
                "Machine architecture not supported for {}".format(major_minor)
            )

        return None

    def _getSpecificBuild(self, build_number):
        """Construct the build string for a specific build number."""
        components = build_number.split(".")

        # We need the major and minor versions to get key information.
        major, minor = components[:2]

        major_minor = "{}.{}".format(major, minor)

        if major_minor not in self.versions:
            raise ValueError("Invalid major/minor build number")

        arch = self._getSpecificArchForBuild(major_minor)

        return self._formatVersionTemplate(build_number, arch)

    def _getTodaysBuild(self, major_minor):
        """Construct the build string for today's major/minor build."""
        if major_minor not in self.versions:
            raise ValueError("Invalid build number")

        # Get the build information.
        version_data = self.versions[major_minor]

        # Today's date.
        today = datetime.now().date()

        # The date and build number to use as a reference in downloading
        # today's build.
        reference_date, reference_build = version_data["reference_date"]

        # Build a date object for the reference date.
        start_date = datetime.strptime(reference_date, "%d/%m/%y").date()

        build_delta = today - start_date

        # The build number is the reference build + time delta in days.
        todays_build = reference_build + build_delta.days

        # It's release candidate time so that means there are now stub
        # versions.  If we have the stubdata set we can determine
        # which release candidate build we can download.
        if "stubdate" in version_data:
            stub_date = datetime.strptime(
                version_data["stubdate"],
                "%d/%m/%y"
            ).date()

            stub_delta = today - stub_date

            # Offset the normal build number by the stub's build number.
            release_num = todays_build - stub_delta.days

            build_number = "{}.{}.{}".format(
                major_minor,
                release_num,
                stub_delta.days
            )

        else:
            build_number = "{}.{}".format(major_minor, todays_build)

        arch = self._getSpecificArchForBuild(major_minor)

        return self._formatVersionTemplate(build_number, arch)

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def file_template(self):
        """Archive file template."""
        return self._file_template

    @property
    def types(self):
        """Build types dictionary."""
        return self._types

    @property
    def versions(self):
        """Build versions dictionary."""
        return self._versions

    # =========================================================================
    # METHODS
    # =========================================================================

    def getBuildToDownload(self, build):
        """Get the build string to download.

        If the passed value is not an explict build number (eg. 15.0) then
        the build for the current day of that major/minor will be downloaded.

        """
        components = build.split(".")

        if len(components) == 2:
            return self._getTodaysBuild(build)

        else:
            return self._getSpecificBuild(build)

    def getArchiveExt(self):
        """Get the installation archive file type based on the operating
        system.

        """
        system = platform.system()

        return self._types[system]["ext"]

    def getInstallerArgs(self, major_minor=None):
        """Get installer args."""
        system = platform.system()

        all_args = []

        # Try to get any installer args for the current system.
        all_args.extend(
            _flattenItems(self._types[system].get("installer_args", ()))
        )

        # Look for major.minor specific installer args.
        if major_minor is not None:
            if major_minor not in self.versions:
                raise ValueError("Invalid build number")

            # Get the build information.
            version_data = self.versions[major_minor]

            # Try to find any specific installer args for the current version
            # and system.
            if "installer_args" in version_data:
                all_args.extend(
                    _flattenItems(
                        version_data["installer_args"].get(system, ())
                    )
                )

        return tuple(all_args)


class HoudiniBuildManager(object):
    """This class provides an interface for accessing installable and installed
    Houdini builds.

    """

    def __init__(self):
        self._installable = []
        self._installed = []

        self._install_target = SETTINGS.system.installation.target
        self._install_folder = SETTINGS.system.installation.folder
        self._link_name = SETTINGS.system.installation.folder

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

    def _getInstallablePackages(self):
        """Populate the installable build lists."""
        files = []

        archive_ext = SETTINGS.build_data.getArchiveExt()

        archive_template = SETTINGS.build_data.file_template

        glob_string = archive_template.format(
            version="*",
            arch="*",
            ext=archive_ext
        )

        # We need to glob in each directory for houdini installation packages.
        for directory in SETTINGS.system.locations:
            search_path = os.path.join(
                directory,
                glob_string
            )

            # Add any found files to the list.
            files += glob.glob(os.path.expandvars(search_path))

        # Convert all the files into HoudiniInstallFile objects.
        self._installable = [HoudiniInstallFile(path) for path in files]

        # Sort the builds by their version number.
        self.installable.sort(key=attrgetter("version"))

    def _getInstalledBuilds(self):
        """Populate the installed build lists."""

        format_args = {
            "version": "*",
        }

        # Generate the path to glob with.
        glob_string = os.path.join(
            self._install_target,
            self._install_folder.format(**format_args)
        )

        # Glob in the install location for installed Houdini builds.
        paths = glob.glob(glob_string)

        # Convert all the install directories to InstalledHoudiniBuild objects
        # if they are not symlinks.
        self._installed = [InstalledHoudiniBuild(path) for path in paths
                           if not os.path.islink(path)]

        self.installed.sort(key=attrgetter("version"))

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def installable(self):
        """A tuple of installable Houdini builds."""
        return self._installable

    @property
    def installed(self):
        """A tuple of installed Houdini builds."""
        return self._installed

    # =========================================================================
    # METHODS
    # =========================================================================

    @staticmethod
    def downloadAndInstall(build_numbers, create_symlink=False):
        """Download and install a list of build numbers.

        Build numbers can be explicit numbers or major.minor versions.
        """
        # Get build information.
        build_data = SETTINGS.build_data

        # Download to the first available installation location.
        download_dir = os.path.expandvars(SETTINGS.system.locations[0])

        for build_number in build_numbers:
            # Get the build file name for the current day
            file_name = build_data.getBuildToDownload(build_number)

            downloaded_path = downloadBuild(file_name, download_dir)

            if downloaded_path is not None:
                package = HoudiniInstallFile(downloaded_path)
                package.install(create_symlink)

    def findMatchingBuilds(self, match_string, builds):
        """Find a matching build given a string and list of builds"""
        # Filter all installed builds that match the build version
        # string.
        matching = [build for build in builds
                    if str(build).startswith(match_string)]

        # If there are any that match, use the latest/only one.
        if matching:
            return matching[-1]

    def getDefaultBuild(self):
        """Attempt to find a default build."""
        default = None

        # Ensure we have system settings available.
        if SETTINGS.system is not None:
            # Get the default from the system settings.
            default_name = SETTINGS.system.default_version

            if default_name is not None:
                default = self.findMatchingBuilds(default_name, self.installed)

        # If the default could not be found (or none was specified) use the
        # latest build.
        if default is None:
            default = self.installed[-1]

        return default


class HoudiniEnvironmentSettings(object):
    """This class stores environment settings.

    """

    def __init__(self, data):
        """Initialize a HoudiniEnvironmentSettings object."""
        self._paths = data.get("paths", {})
        self._variables = data.get("variables", [])

        self._test_paths = data.get("test_paths", {})
        self._test_variables = data.get("test_variables", [])

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def paths(self):
        """A dictionary of paths to set."""
        return self._paths

    @property
    def test_paths(self):
        """A dictionary of paths to set."""
        return self._test_paths

    @property
    def test_variables(self):
        """A dictionary of environment variables to set."""
        return self._test_variables

    @property
    def variables(self):
        """A dictionary of environment variables to set."""
        return self._variables

    # =========================================================================
    # METHODS
    # =========================================================================

    def setCustomEnv(self):
        """Apply custom env settings from package file."""
        # Set variables first so they can possibly be used in custom paths.
        for variable, value in self.paths.iteritems():
            setVar(variable, ":".join(value))

        for variable, value in self.variables.iteritems():
            setVar(variable, value)

    @staticmethod
    def setDefaultEnvironment(installed_build):
        """This function will initialize the environment variables necessary
        to run applications.  This is equivalent to sourcing the houdini_setup
        file located in $HFS.

        """
        # The base Houdini location.
        setVar("HFS", installed_build.path)

        # Handy shortcuts.
        setVar("H", "${HFS}")
        setVar("HB", "${H}/bin")
        setVar("HDSO", "${H}/dsolib")
        setVar("HD", "${H}/demo")
        setVar("HH", "${H}/houdini")
        setVar("HHC", "${HH}/config")
        setVar("HT", "${H}/toolkit")
        setVar("HSB", "${HH}/sbin")

        if "TEMP" not in os.environ:
            setVar("TEMP", tempfile.gettempdir())

        # Only set LD_LIBRARY_PATH if it already exists.  This makes sure
        # HDSO is always searched first.
        if "LD_LIBRARY_PATH" in os.environ:
            setVar(
                "LD_LIBRARY_PATH",
                (os.environ["HDSO"], os.environ["LD_LIBRARY_PATH"])
            )

        # Set variables with the version information.
        setVar("HOUDINI_MAJOR_RELEASE", installed_build.major)
        setVar("HOUDINI_MINOR_RELEASE", installed_build.minor)
        setVar("HOUDINI_BUILD_VERSION", installed_build.build)
        setVar("HOUDINI_VERSION", installed_build)

        # Insert the Houdini bin directories at the head of the PATH.
        setVar(
            "PATH",
            (os.environ["HB"], os.environ["HSB"], os.environ["PATH"])
        )

    def setTestpathEnv(self):
        """Apply testpath env settings from package file."""
        # Set variables first so they can possibly be used in custom paths.
        for variable, value in self.test_paths.iteritems():
            setVar(variable, ":".join(value))

        for variable, value in self.test_variables.iteritems():
            setVar(variable, value)


class HoudiniInstallFile(HoudiniBase):
    """This class represents an installable Houdini package.

    The path is a path to the installable archive on disk.

    """

    def __init__(self, path):
        archive_template = SETTINGS.build_data.file_template
        archive_ext = SETTINGS.build_data.getArchiveExt()

        pattern = archive_template.format(
            version="([0-9\\.]*)",
            arch=".+",
            ext=archive_ext
        )

        result = re.match(pattern, os.path.basename(path))

        version_string = result.group(1)

        # Get the build number components.
        components = [int(val) for val in version_string.split(".")]

        # If we have 3 then we don't have a release candidate value so we
        # append None.
        if len(components) == 3:
            components.append(None)

        super(HoudiniInstallFile, self).__init__(path, components)

        self._install_target = SETTINGS.system.installation.target
        self._install_folder = SETTINGS.system.installation.folder
        self._link_name = SETTINGS.system.installation.link_name

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _installLinux(self, install_path, link_path):
        """Install the build on linux."""
        # Let our system tell us where we can store the temp files.
        temp_path = tempfile.gettempdir()

        print "Extracting {} to {}".format(
            self.path,
            temp_path
        )

        # Open the tar file that this object represents and extract
        # everything to our temp directory, closing the file afterwards.
        with tarfile.open(self.path, "r:gz") as handle:
            handle.extractall(temp_path)

        # Store the archive file name, minus the file extensions.
        archive_name = os.path.basename(self.path).replace(".tar.gz", "")

        # Build the path to the newly extracted tarball.
        extract_path = os.path.join(temp_path, archive_name)

        # Path to the installer script.
        cmd = [os.path.join(extract_path, "houdini.install")]

        # Get any installer arguments.
        cmd.extend(SETTINGS.build_data.getInstallerArgs(self.major_minor))

        # Last arg is the target path.
        cmd.append(install_path)

        print "Running Houdini installer: {}".format(" ".join(cmd))
        subprocess.call(cmd)

        # Remove the temporary extraction directory.
        print "Removing temporary install files."
        shutil.rmtree(extract_path)

        if link_path is not None:
            print "Linking {} to {}".format(link_path, install_path)

            try:
                os.symlink(install_path, link_path)

            except OSError as inst:
                if inst.errno == os.errno.EEXIST:
                    os.remove(link_path)
                    os.symlink(install_path, link_path)

                else:
                    raise

    # =========================================================================
    # METHODS
    # =========================================================================

    def install(self, create_symlink=False):
        """Install this package to the install directory.

        To install we need to extract the contents to a temp directory.  We
        can then run the shipped installer script to properly install Houdini.
        Afterwards we remove the temp directory.

        """
        # Generate the path to install the build to.
        install_path = os.path.join(
            self._install_target,
            self.formatString(self._install_folder)
        )

        link_path = None

        if create_symlink:
            link_path = os.path.join(
                self._install_target,
                self.formatString(self._link_name)
            )

        # Check to see if the build is already installed.  If it is
        # we throw an exception.
        if os.path.exists(install_path):
            raise BuildAlreadyInstalledError(str(self))

        system = platform.system()

        if system == "Linux":
            self._installLinux(install_path, link_path)

        elif system == "Windows":
            raise UnsupportedOSError("Windows is not supported")

        elif system == "Darwin":
            raise UnsupportedOSError("OS X is not supported")

        # Notify that the build installation has completed.
        print "Installation of Houdini {} complete.".format(self)


class HoudiniInstallationSettings(object):
    """This class stores Houdini installation settings.

    """

    def __init__(self, data):
        self._target = data["target"]
        self._folder = data["folder"]
        self._link_name = data.get("symlink")

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def link_name(self):
        """The name of the symlink, if any."""
        return self._link_name

    @property
    def folder(self):
        """The folder to install Houdini to."""
        return self._folder

    @property
    def target(self):
        """The base path to install Houdini to."""
        return self._target


class HoudiniPluginSettings(object):
    """This class stores Houdini plugin settings.

    """

    def __init__(self, data):
        self._target = data["target"]
        self._folder = data["folder"]

        self._root = None
        self._command = None

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def folder(self):
        """The folder for Houdini plugins."""
        return self._folder

    @property
    def target(self):
        """The base path to the Houdini plugin directory."""
        return self._target


class HoudiniSettingsManager(object):
    """This class manages Houdini package settings.

    """

    def __init__(self):
        self._environment = None
        self._system = None

        # File to load configuation information from.
        config_path = None

        # Support directly specifying with an variable.
        if "HOUDINI_PACKAGE_JSON" in os.environ:
            # Assume that if it is specified it exists.
            config_path = os.environ["HOUDINI_PACKAGE_JSON"]

        # If no env is set look for a houdini_package_config.json file in
        # the home directory.
        else:
            home_path = os.path.expandvars(
                os.path.join("${HOME}", PACKAGE_CONFIG_FILE)
            )

            # If that file exists then use it.
            if os.path.exists(home_path):
                config_path = home_path

        # If no user config was found look for the look for the package.json
        # file in the same directory as this module.
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__),
                PACKAGE_CONFIG_FILE
            )

        # Couldn't find any valid files so we have nothing left to do.
        if not os.path.exists(config_path):
            raise IOError(
                "Could not find houdini package configuration file"
            )

        with open(config_path) as handle:
            # Get the json data.
            data = json.load(handle, object_hook=ht.utils.convertFromUnicode)

            # Construct settings objects for available data.
            self._environment = HoudiniEnvironmentSettings(
                data["environment"]
            )

            self._system = HoudiniSystemSettings(data["system"])

        # Path to the build data config file.  This file should always be
        # alongside this module.
        build_config_path = os.path.join(
            os.path.dirname(__file__),
            BUILD_DATA_FILE
        )

        # Couldn't find any valid files so we have nothing left to do.
        if not os.path.exists(build_config_path):
            raise IOError(
                "Could not find houdini build configuration file"
            )

        with open(build_config_path) as handle:
            data = json.load(handle, object_hook=ht.utils.convertFromUnicode)

            self._build_data = HoudiniBuildData(data)

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def build_data(self):
        """Houdini build data."""
        return self._build_data

    @property
    def environment(self):
        """Houdini environment settings."""
        return self._environment

    @property
    def system(self):
        """Houdini environment settings."""
        return self._system


class HoudiniSystemSettings(object):
    """This class stores Houdini system settings.

    """

    def __init__(self, data):
        self._locations = data["archive_locations"]
        self._plugins = None
        self._default_version = None

        self._installation = HoudiniInstallationSettings(data["installation"])

        if "default_version" in data:
            self._default_version = data["default_version"]

        # Plugin data is optional.
        if "plugins" in data:
            self._plugins = HoudiniPluginSettings(data["plugins"])

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def default_version(self):
        """A default build version string."""
        return self._default_version

    @property
    def installation(self):
        """Houdini installation settings."""
        return self._installation

    @property
    def locations(self):
        """A list of locations to search for installable packages."""
        return self._locations

    @property
    def plugins(self):
        """Houdini plugin settings."""
        return self._plugins


class InstalledHoudiniBuild(HoudiniBase):
    """This class represents an installed Houdini build.

    """

    def __init__(self, path):
        # Get the install folder name template.
        folder_name = SETTINGS.system.installation.folder

        # Replace
        pattern = folder_name.format(version="([0-9\\.]*)")

        result = re.match(pattern, os.path.basename(path))

        # Extract the build version numbers from the directory name.
        version_string = result.group(1)

        # Get the build number components.
        components = [int(val) for val in version_string.split(".")]

        # If we have 3 then we don't have a release candidate value so we
        # append None.
        if len(components) == 3:
            components.append(None)

        super(InstalledHoudiniBuild, self).__init__(path, components)

    # =========================================================================
    # METHODS
    # =========================================================================

    def setupEnvironment(self, testpath=False):
        """Setup the environment in order to run this build."""
        # Run the default environment setup.
        HoudiniEnvironmentSettings.setDefaultEnvironment(self)

        # Run custom setup if allowed.
        if testpath:
            print "Initializing testpath environment\n"
            SETTINGS.environment.setTestpathEnv()

        else:
            # Set a variable containing the plugin path, if it exists.
            if self.plugin_path is not None:
                os.environ["HOUDINI_PLUGIN_PATH"] = self.plugin_path

            SETTINGS.environment.setCustomEnv()

    def uninstall(self):
        """Uninstall the Houdini build.

        This function will remove the install directory and optionally
        remove any compiled operators for the build.

        """
        parent = os.path.dirname(self.path)

        # Construct the symlink path to check for.
        link_path = os.path.join(
            parent,
            self.formatString(SETTINGS.system.installation.link_name)
        )

        # Check if the link exists and if it points to this build.  If so, try
        # to remove it.
        if os.path.islink(link_path):
            if os.path.realpath(link_path) == self.path:
                print "Removing symlink {} -> {}".format(link_path, self.path)

                try:
                    os.unlink(link_path)

                except OSError as inst:
                    print "Error: Could not remove symlink"
                    print inst

        print "Removing installation directory {}".format(self.path)

        shutil.rmtree(self.path)

        # If there are plugins, remove them.
        if self.plugin_path is not None:
            if os.path.isdir(self.plugin_path):
                print "Removing compiled operators in {}".format(
                    self.plugin_path
                )

                shutil.rmtree(self.plugin_path)

# =============================================================================
# EXCEPTIONS
# =============================================================================

class BuildAlreadyInstalledError(Exception):
    """Exception raised when a build is already installed."""

    def __init__(self, build):
        super(BuildAlreadyInstalledError, self).__init__()

        self.build = build

    def __str__(self):
        return "Houdini {} is already installed.".format(self.build)


class UnsupportedMachineArchitectureError(Exception):
    """Exception raised when there is no specified machine architecture for
    a certain build.

    """
    pass


class UnsupportedOSError(Exception):
    """Exception raised when there is no known way to install for an OS."""
    pass


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

def _flattenItems(items):
    """Flatten a list of items."""
    flattened = []

    for item in items:
        if isinstance(item, (list, tuple)):
            flattened.extend(item)

        else:
            flattened.append(item)

    return flattened


def _getSESIAuthInfo():
    """This function reads a custom .json file in the user's home directory to
    get their SESI website login credentials.

    This is necessary for automatic build downloading.

    Example file contents:

{
    "username": "your_name,
    "password": "your_password"
}

    """
    auth_path = os.path.expandvars("$HOME/.sesi_login_details")

    if not os.path.isfile(auth_path):
        raise IOError(
            "Could not find authentication information in {}".format(
                auth_path
            )
        )

    with open(auth_path) as handle:
        data = json.load(handle, object_hook=ht.utils.convertFromUnicode)

    return data["username"], data["password"]

# =============================================================================
# FUNCTIONS
# =============================================================================


def downloadBuild(build_file, target_directory):
    """Download a build file from the SESI website and place it in the target
    directory.

    """
    print "Attempting to download build: {}".format(build_file)

    user, password = _getSESIAuthInfo()

    browser = Browser()
    browser.set_handle_robots(False)
    browser.open("https://www.sidefx.com/login/?next=/download/daily-builds/")

    browser.select_form(nr=0)
    browser.form['username'] = user
    browser.form['password'] = password
    browser.submit()

    browser.open('http://www.sidefx.com/download/daily-builds/')

    try:
        resp = browser.follow_link(text=build_file, nr=0)

    except LinkNotFoundError:
        print "Error: {} does not exist".format(build_file)
        return

    url = resp.geturl()
    url += 'get/'
    resp = browser.open(url)

    file_size = int(resp.info()["Content-Length"])
    block_size = file_size / 10

    target_path = os.path.join(target_directory, build_file)

    print "Downloading to {}".format(target_path)
    print "\tFile size: {:0.2f}MB".format(file_size / (1024.0**2))
    print "\tDownload block size of {:0.2f}MB\n".format(block_size / (1024.0**2))

    total = 0

    with open(target_path, 'wb') as handle:
        sys.stdout.write("0% complete")
        sys.stdout.flush()

        while True:
            buf = resp.read(block_size)

            if not buf:
                break

            total += block_size

            sys.stdout.write(
                "\r{}% complete".format(min(int((total / float(file_size)) * 100), 100))
            )
            sys.stdout.flush()

            handle.write(buf)

    print "\n\nDownload complete"

    return target_path


def setVar(name, value):
    """Set an environment variable.

    This value can be a string, number or list of strings.  If the value is a
    list, they will be joined together with a ':'.

    This function will automatically expand any variables in the value before
    setting.

    """
    # If the value is a list, join the entries together ensuring they are
    # strings.
    if isinstance(value, (list, tuple)):
        value = ":".join([str(val) for val in value])

    # Convert the value to a string since that is the data type that must be
    # used when setting environment variables.
    else:
        value = str(value)

    # Expand any variables in the value.
    value = os.path.expandvars(value)

    os.environ[name] = value

# =============================================================================

# Build settings for common use by all Houdini objects.
SETTINGS = HoudiniSettingsManager()

