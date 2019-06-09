"""This module contains classes and functions related to Houdini builds."""

# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
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

from mechanize import Browser, LinkNotFoundError


# =============================================================================
# GLOBALS
# =============================================================================

_BUILD_DATA_FILE = "build_data.json"
_PACKAGE_CONFIG_FILE = "houdini_package_config.json"


# =============================================================================
# CLASSES
# =============================================================================

class HoudiniBase(object):
    """This class represents a Houdini build on disk.

    :param path: The path to the build on disk.
    :type path: str
    :param version: The build version
    :type version: tuple(int)

    """

    def __init__(self, path, version):
        self._path = path

        self._major, self._minor, self._build, self._candidate = version

        self._plugin_path = None

        if _SETTINGS_MANAGER.system.plugins is not None:
            plugin_folder = self.format_string(
                _SETTINGS_MANAGER.system.plugins.folder
            )

            # Generate the path to install the build to.
            self._plugin_path = os.path.join(
                _SETTINGS_MANAGER.system.plugins.target,
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
        """int: The build number for this build. """
        return self._build

    @property
    def candidate(self):
        """int: The release candidate number for this build. """
        return self._candidate

    @property
    def major(self):
        """int: The major number for this build. """
        return self._major

    @property
    def major_minor(self):
        """str: The major.minor number for this build. """
        return "{}.{}".format(self.major, self.minor)

    @property
    def minor(self):
        """int: The minor number for this build. """
        return self._minor

    @property
    def path(self):
        """str: The file path on disk of the build. """
        return self._path

    @property
    def plugin_path(self):
        """str: The location of any plugins for this build."""
        if self._plugin_path is None:
            return None

        return os.path.expandvars(self._plugin_path)

    @property
    def version(self):
        """tuple(int): A tuple containing version information. """
        version = [self.major, self.minor, self.build]

        # Add the candidate number if necessary.
        if self.candidate is not None:
            version.append(self.candidate)

        return tuple(version)

    # =========================================================================
    # METHODS
    # =========================================================================

    def format_string(self, value):
        """Format a string given information about this build.

        :param value: The string to format.
        :type value: str
        :return: The formatted string.
        :rtype: str

        """
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

    :param data: A build data dictionary.
    :type data: dict

    """

    def __init__(self, data):
        self._file_template = data["file_template"]
        self._types = data["types"]
        self._versions = data["versions"]

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _format_version_template(self, build_number, arch=None):
        """Format the file template for the build number and architecture.

        :param build_number: The build (version) string.
        :type build_number: str
        :param arch: Optional machine architecture string.
        :type arch: str
        :return: A formatted file template.
        :rtype: str

        """
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

    def _get_specified_arch_for_build(self, major_minor):
        """Check for a specific machine architecture for a build.

        :param major_minor: The major.minor version number.
        :type major_minor: str
        :return: A matching architecture string, if any.
        :rtype: str|None

        """
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

    def _get_specified_build(self, build_number):
        """Construct the build string for a specific build number.

        :param build_number: The build (version) string.
        :type build_number: str
        :return: A constructed file name.
        :rtype: str

        """
        components = build_number.split(".")

        # We need the major and minor versions to get key information.
        major, minor = components[:2]

        major_minor = "{}.{}".format(major, minor)

        if major_minor not in self.versions:
            raise ValueError("Invalid major/minor build number")

        arch = self._get_specified_arch_for_build(major_minor)

        return self._format_version_template(build_number, arch)

    def _get_daily_build(self, major_minor):
        """Construct the build string for today's major/minor build.

        :param major_minor: The base Houdini version to get.
        :type major_minor: str
        :return: The build string for the current day's build.
        :rtype: str

        """
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
        daily_build = reference_build + build_delta.days

        # It's release candidate time so that means there are now stub
        # versions.  If we have the stubdate set we can determine
        # which release candidate build we can download.
        if "stubdate" in version_data:
            stub_date = datetime.strptime(
                version_data["stubdate"],
                "%d/%m/%y"
            ).date()

            stub_delta = today - stub_date

            # Offset the normal build number by the stub's build number.
            release_num = daily_build - stub_delta.days

            build_number = "{}.{}.{}".format(
                major_minor,
                release_num,
                stub_delta.days
            )

        else:
            build_number = "{}.{}".format(major_minor, daily_build)

        arch = self._get_specified_arch_for_build(major_minor)

        return self._format_version_template(build_number, arch)

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def file_template(self):
        """str: Archive file template."""
        return self._file_template

    @property
    def types(self):
        """dict: Build types dictionary."""
        return self._types

    @property
    def versions(self):
        """dict: Build versions dictionary."""
        return self._versions

    # =========================================================================
    # METHODS
    # =========================================================================

    def get_build_to_download(self, build):
        """Get the build string to download.

        If the passed value is not an explict build number (eg. 15.0) then
        the build for the current day of that major/minor will be downloaded.

        :param build: The target build number.
        :type build: str
        :return: The build string to download.
        :rtype: str

        """
        components = build.split(".")

        if len(components) == 2:
            return self._get_daily_build(build)

        return self._get_specified_build(build)

    def get_archive_extension(self):
        """Get the installation archive file type based on the operating
        system.

        :return: The file extension.
        :rtype: str

        """
        system = platform.system()

        return self._types[system]["ext"]

    def get_install_args(self, major_minor=None):
        """Get installer args.

        :param major_minor: The base version to install.
        :type major_minor: str
        :return: A tuple of installer args.
        :rtype: tuple(str)

        """
        system = platform.system()

        all_args = []

        # Try to get any installer args for the current system.
        all_args.extend(
            _flatten_items(self._types[system].get("installer_args", ()))
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
                    _flatten_items(
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

        self._install_target = _SETTINGS_MANAGER.system.installation.target
        self._install_folder = _SETTINGS_MANAGER.system.installation.folder
        self._link_name = _SETTINGS_MANAGER.system.installation.folder

        self._populate_installed_builds()
        self._populate_installable_packages()

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __repr__(self):
        return "<HoudiniBuildManager>"

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _populate_installable_packages(self):
        """Populate the installable build lists.

        :return:

        """
        files = []

        archive_ext = _SETTINGS_MANAGER.build_data.get_archive_extension()

        archive_template = _SETTINGS_MANAGER.build_data.file_template

        glob_string = archive_template.format(
            version="*",
            arch="*",
            ext=archive_ext
        )

        # We need to glob in each directory for houdini installation packages.
        for directory in _SETTINGS_MANAGER.system.locations:
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

    def _populate_installed_builds(self):
        """Populate the installed build lists.

        :return:

        """

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
        """tuple(HoudiniInstallFile): A tuple of installable Houdini builds."""
        return self._installable

    @property
    def installed(self):
        """tuple(InstalledHoudiniBuild): A tuple of installed Houdini builds."""
        return self._installed

    # =========================================================================
    # STATIC METHODS
    # =========================================================================

    @staticmethod
    def download_and_install(build_numbers, create_symlink=False):
        """Download and install a list of build numbers.

        Build numbers can be explicit numbers or major.minor versions.

        :param build_numbers: A list of build numbers to process.
        :type build_numbers: list(str)
        :param create_symlink: Whether or not to create a major.minor symlink.
        :type create_symlink: bool
        :return:

        """
        # Get build information.
        build_data = _SETTINGS_MANAGER.build_data

        # Download to the first available installation location.
        download_dir = os.path.expandvars(_SETTINGS_MANAGER.system.locations[0])

        for build_number in build_numbers:
            # Get the build file name for the current day
            file_name = build_data.get_build_to_download(build_number)

            downloaded_path = _download_build(file_name, download_dir)

            if downloaded_path is not None:
                package = HoudiniInstallFile(downloaded_path)
                package.install(create_symlink)

    # =========================================================================
    # METHODS
    # =========================================================================

    def get_default_build(self):
        """Attempt to find a default build.

        :return: The default build, if any.
        :rtype: InstalledHoudiniBuild|None

        """
        default = None

        # Ensure we have system settings available.
        if _SETTINGS_MANAGER.system is not None:
            # Get the default from the system settings.
            default_name = _SETTINGS_MANAGER.system.default_version

            if default_name is not None:
                default = find_matching_builds(default_name, self.installed)

        # If the default could not be found (or none was specified) use the
        # latest build.
        if default is None and self.installed:
            default = self.installed[-1]

        return default


class HoudiniEnvironmentSettings(object):
    """This class stores environment settings.

    :param data: The source data dict.
    :type data: dict

    """

    def __init__(self, data):
        self._paths = data.get("paths", {})
        self._variables = data.get("variables", [])

        self._test_paths = data.get("test_paths", {})
        self._test_variables = data.get("test_variables", [])

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def paths(self):
        """dict: A dictionary of paths to set."""
        return self._paths

    @property
    def test_paths(self):
        """dict: A dictionary of paths to set."""
        return self._test_paths

    @property
    def test_variables(self):
        """dict: A dictionary of environment variables to set."""
        return self._test_variables

    @property
    def variables(self):
        """dict: A dictionary of environment variables to set."""
        return self._variables

    # =========================================================================
    # STATIC METHODS
    # =========================================================================

    # FIXME: Why is this static???
    @staticmethod
    def set_default_environment(installed_build):
        """Initialize the environment variables necessary to run applications.

        This is equivalent to sourcing the houdini_setup file located in $HFS.

        :param installed_build: An installed Houdini build.
        :type installed_build: InstalledHoudiniBuild
        :return:

        """
        # The base Houdini location.
        _set_variable("HFS", installed_build.path)

        # Handy shortcuts.
        _set_variable("H", "${HFS}")
        _set_variable("HB", "${H}/bin")
        _set_variable("HDSO", "${H}/dsolib")
        _set_variable("HD", "${H}/demo")
        _set_variable("HH", "${H}/houdini")
        _set_variable("HHC", "${HH}/config")
        _set_variable("HT", "${H}/toolkit")
        _set_variable("HSB", "${HH}/sbin")

        if "TEMP" not in os.environ:
            _set_variable("TEMP", tempfile.gettempdir())

        # Only set LD_LIBRARY_PATH if it already exists.  This makes sure
        # HDSO is always searched first.
        if "LD_LIBRARY_PATH" in os.environ:
            _set_variable(
                "LD_LIBRARY_PATH",
                (os.environ["HDSO"], os.environ["LD_LIBRARY_PATH"])
            )

        # Set variables with the version information.
        _set_variable("HOUDINI_MAJOR_RELEASE", installed_build.major)
        _set_variable("HOUDINI_MINOR_RELEASE", installed_build.minor)
        _set_variable("HOUDINI_BUILD_VERSION", installed_build.build)
        _set_variable("HOUDINI_VERSION", installed_build)

        # Insert the Houdini bin directories at the head of the PATH.
        _set_variable(
            "PATH",
            (os.environ["HB"], os.environ["HSB"], os.environ["PATH"])
        )

    # =========================================================================
    # METHODS
    # =========================================================================

    def set_custom_environment(self):
        """Apply custom env settings from package file.

        :return:

        """
        # Set variables first so they can possibly be used in custom paths.
        for variable, value in self.paths.iteritems():
            _set_variable(variable, ":".join(value))

        for variable, value in self.variables.iteritems():
            _set_variable(variable, value)

    def set_test_path_environment(self):
        """Apply test_path env settings from package file.

        :return:

        """
        # Set variables first so they can possibly be used in custom paths.
        for variable, value in self.test_paths.iteritems():
            _set_variable(variable, ":".join(value))

        for variable, value in self.test_variables.iteritems():
            _set_variable(variable, value)


class HoudiniInstallFile(HoudiniBase):
    """This class represents an installable Houdini package.

    :param path: The path to the installable archive on disk.
    :type path: str

    """

    def __init__(self, path):
        archive_template = _SETTINGS_MANAGER.build_data.file_template
        archive_ext = _SETTINGS_MANAGER.build_data.get_archive_extension()

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

        self._install_target = _SETTINGS_MANAGER.system.installation.target
        self._install_folder = _SETTINGS_MANAGER.system.installation.folder
        self._link_name = _SETTINGS_MANAGER.system.installation.link_name

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _install_linux(self, install_path, link_path):
        """Install the build on linux.

        :param install_path: The path to install to.
        :type install_path: str
        :param link_path: The symlink path.
        :type link_path: str
        :return:

        """
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
        cmd.extend(_SETTINGS_MANAGER.build_data.get_install_args(self.major_minor))

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

        :param create_symlink: Whether or not to create a major/minor symlink.
        :type create_symlink: bool
        :return:

        """
        # Generate the path to install the build to.
        install_path = os.path.join(
            self._install_target,
            self.format_string(self._install_folder)
        )

        link_path = None

        if create_symlink:
            link_path = os.path.join(
                self._install_target,
                self.format_string(self._link_name)
            )

        # Check to see if the build is already installed.  If it is
        # we throw an exception.
        if os.path.exists(install_path):
            raise BuildAlreadyInstalledError(str(self))

        system = platform.system()

        if system == "Linux":
            self._install_linux(install_path, link_path)

        elif system == "Windows":
            raise UnsupportedOSError("Windows is not supported")

        elif system == "Darwin":
            raise UnsupportedOSError("OS X is not supported")

        # Notify that the build installation has completed.
        print "Installation of Houdini {} complete.".format(self)


class HoudiniInstallationSettings(object):
    """This class stores Houdini installation settings.

    :param data: The source data dict.
    :type data: dict

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
        """str: The name of the symlink, if any."""
        return self._link_name

    @property
    def folder(self):
        """str: The folder to install Houdini to."""
        return self._folder

    @property
    def target(self):
        """str: The base path to install Houdini to."""
        return self._target


class HoudiniPluginSettings(object):
    """This class stores Houdini plugin settings.

    :param data: The source data dict.
    :type data: dict

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
        """str: The folder for Houdini plugins."""
        return self._folder

    @property
    def target(self):
        """str: The base path to the Houdini plugin directory."""
        return self._target


class HoudiniSettingsManager(object):
    """This class manages Houdini package settings.

    """

    def __init__(self):
        self._environment = None
        self._system = None

        # File to load configuration information from.
        config_path = None

        # Support directly specifying with an variable.
        if "HOUDINI_PACKAGE_JSON" in os.environ:
            # Assume that if it is specified it exists.
            config_path = os.environ["HOUDINI_PACKAGE_JSON"]

        # If no env is set look for a houdini_package_config.json file in
        # the home directory.
        else:
            home_path = os.path.expandvars(
                os.path.join("${HOME}", _PACKAGE_CONFIG_FILE)
            )

            # If that file exists then use it.
            if os.path.exists(home_path):
                config_path = home_path

        # If no user config was found look for the look for the package.json
        # file in the same directory as this module.
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__),
                _PACKAGE_CONFIG_FILE
            )

        # Couldn't find any valid files so we have nothing left to do.
        if not os.path.exists(config_path):
            raise IOError(
                "Could not find houdini package configuration file"
            )

        with open(config_path) as handle:
            # Get the json data.
            data = json.load(handle)

            # Construct settings objects for available data.
            self._environment = HoudiniEnvironmentSettings(
                data["environment"]
            )

            self._system = HoudiniSystemSettings(data["system"])

        # Path to the build data config file.  This file should always be
        # alongside this module.
        build_config_path = os.path.join(
            os.path.dirname(__file__),
            _BUILD_DATA_FILE
        )

        # Couldn't find any valid files so we have nothing left to do.
        if not os.path.exists(build_config_path):
            raise IOError(
                "Could not find houdini build configuration file"
            )

        with open(build_config_path) as handle:
            data = json.load(handle)

            self._build_data = HoudiniBuildData(data)

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def build_data(self):
        """HoudiniBuildData: Houdini build data."""
        return self._build_data

    @property
    def environment(self):
        """HoudiniEnvironmentSettings: Houdini environment settings."""
        return self._environment

    @property
    def system(self):
        """HoudiniSystemSettings: Houdini system settings."""
        return self._system


class HoudiniSystemSettings(object):
    """This class stores Houdini system settings.

    :param data: The source data dict.
    :type data: dict

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
        """str|None: A default build version string."""
        return self._default_version

    @property
    def installation(self):
        """HoudiniInstallationSettings: Houdini installation settings."""
        return self._installation

    @property
    def locations(self):
        """list(str): A list of locations to search for installable packages."""
        return self._locations

    @property
    def plugins(self):
        """HoudiniPluginSettings|None: Houdini plugin settings."""
        return self._plugins


class InstalledHoudiniBuild(HoudiniBase):
    """This class represents an installed Houdini build.

    :param path: The path to the build.
    :type path: str

    """

    def __init__(self, path):
        # Get the install folder name template.
        folder_name = _SETTINGS_MANAGER.system.installation.folder

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

    def setup_environment(self, test_path=False):
        """Setup the environment in order to run this build.

        :param test_path: Whether or not to run in test mode.
        :type test_path: bool
        :return:

        """
        # Run the default environment setup.
        HoudiniEnvironmentSettings.set_default_environment(self)

        # Run custom setup if allowed.
        if test_path:
            print "Initializing test_path environment\n"
            _SETTINGS_MANAGER.environment.set_test_path_environment()

        else:
            # Set a variable containing the plugin path, if it exists.
            if self.plugin_path is not None:
                os.environ["HOUDINI_PLUGIN_PATH"] = self.plugin_path

            _SETTINGS_MANAGER.environment.set_custom_environment()

    def uninstall(self):
        """Uninstall the Houdini build.

        This function will remove the install directory and optionally
        remove any compiled operators for the build.

        :return:

        """
        parent = os.path.dirname(self.path)

        # Construct the symlink path to check for.
        link_path = os.path.join(
            parent,
            self.format_string(_SETTINGS_MANAGER.system.installation.link_name)
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

class HoudiniPackageError(Exception):
    """Base class for Houdini package related errors."""


class BuildAlreadyInstalledError(HoudiniPackageError):
    """Exception raised when a build is already installed.

    :param build: A version string.
    :type build: str

    """

    def __init__(self, build):
        super(BuildAlreadyInstalledError, self).__init__()

        self.build = build

    def __str__(self):
        return "Houdini {} is already installed.".format(self.build)


class UnsupportedMachineArchitectureError(HoudiniPackageError):
    """Exception raised when there is no specified machine architecture for
    a certain build.

    """


class UnsupportedOSError(HoudiniPackageError):
    """Exception raised when there is no known way to install for an OS."""


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

def _download_build(build_file, target_directory):
    """Download a build file from the SESI website and place it in the target
    directory.

    :param build_file: The file name to download.
    :type build_file: str
    :param target_directory: The download target location.
    :type target_directory: str
    :return: The path to the downloaded file.
    :rtype: str|None

    """
    print "Attempting to download build: {}".format(build_file)

    user, password = _get_sesi_auth_info()

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

        return None

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


def _flatten_items(items):
    """Flatten a list of items.

    :param items: A list of items to flatted.
    :type items: list
    :return: The flattened items.
    :rtype: list

    """
    flattened = []

    for item in items:
        if isinstance(item, (list, tuple)):
            flattened.extend(item)

        else:
            flattened.append(item)

    return flattened


def _get_sesi_auth_info():
    """This function reads a custom .json file in the user's home directory to
    get their SESI website login credentials.

    This is necessary for automatic build downloading.

    Example file contents:

    {
        "username": "your_name,
        "password": "your_password"
    }

    :return: A user name and password.
    :rtype: tuple(str)

    """
    auth_path = os.path.expandvars("$HOME/.sesi_login_details")

    if not os.path.isfile(auth_path):
        raise IOError(
            "Could not find authentication information in {}".format(
                auth_path
            )
        )

    with open(auth_path) as handle:
        data = json.load(handle)

    return data["username"], data["password"]


def _set_variable(name, value):
    """Set an environment variable.

    This value can be a string, number or list of strings.  If the value is a
    list, they will be joined together with a ':'.

    This function will automatically expand any variables in the value before
    setting.

    :param name: The name of the variable to set.
    :type name: str
    :param value: The value to set.
    :type value: object
    :return:

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
# FUNCTIONS
# =============================================================================

def find_matching_builds(match_string, builds):
    """Find a matching build given a string and list of builds.

    :param match_string: The string to match against.
    :type match_string: str
    :param builds: Installed builds to match against.
    :type builds: tuple(InstalledHoudiniBuild)
    :return: A matching build.
    :rtype: InstalledHoudiniBuild|None

    """
    # Filter all installed builds that match the build version
    # string.
    matching = [build for build in builds
                if str(build).startswith(match_string)]

    # If there are any that match, use the latest/only one.
    if matching:
        return matching[-1]

    return None


# =============================================================================

# Build settings for common use by all Houdini objects.
_SETTINGS_MANAGER = HoudiniSettingsManager()
