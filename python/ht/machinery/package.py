"""This module contains classes and functions related to Houdini builds."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import errno
import glob
import json
from operator import attrgetter
import os
import platform
import re
import shutil
import subprocess
import tarfile
import tempfile

# Houdini Toolbox Imports
from ht.machinery import sidefx_web_api


# =============================================================================
# GLOBALS
# =============================================================================

_BUILD_DATA_FILE = "build_data.json"
_PACKAGE_CONFIG_FILE = "houdini_package_config.json"


# =============================================================================
# CLASSES
# =============================================================================


class HoudiniBase:
    """This class represents a Houdini build on disk.

    :param path: The path to the build on disk.
    :type path: str
    :param version: The build version
    :type version: list or tuple
    :param product: Optional product name.
    :type product: str

    """

    def __init__(self, path, version, product=None):
        self._path = path

        self._major, self._minor, self._build, self._candidate = version

        self._product = product
        self._plugin_path = None

        if _SETTINGS_MANAGER.system.plugins is not None:
            plugin_folder = self.format_string(_SETTINGS_MANAGER.system.plugins.folder)

            # Generate the path to install the build to.
            self._plugin_path = os.path.join(
                _SETTINGS_MANAGER.system.plugins.target, plugin_folder
            )

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __eq__(self, other):
        if not isinstance(other, HoudiniBase):
            return NotImplemented

        # Check the Houdini version.
        if self.version != other.version:
            return False

        # Check the products.
        if self.product != other.product:
            return False

        return True

    def __ne__(self, other):
        if not isinstance(other, HoudiniBase):
            return NotImplemented

        return not self.__eq__(other)

    def __lt__(self, other):
        if not isinstance(other, HoudiniBase):
            return NotImplemented

        # Two objects are equal if their Houdini versions are equal.
        return self.version < other.version

    def __le__(self, other):
        if not isinstance(other, HoudiniBase):
            return NotImplemented

        # Two objects are equal if their Houdini versions are equal.
        return self.version <= other.version

    def __gt__(self, other):
        if not isinstance(other, HoudiniBase):
            return NotImplemented

        # Two objects are equal if their Houdini versions are equal.
        return self.version > other.version

    def __ge__(self, other):
        if not isinstance(other, HoudiniBase):
            return NotImplemented

        # Two objects are equal if their Houdini versions are equal.
        return self.version >= other.version

    def __hash__(self):
        return hash((self.major, self.minor, self.build, self.candidate, self.path))

    def __repr__(self):
        return "<{} {} @ {}>".format(
            self.__class__.__name__, self.display_name, self.path
        )

    def __str__(self):
        version = "{}.{}.{}".format(self.major, self.minor, self.build)

        if self.candidate is not None:
            version = "{}.{}".format(version, self.candidate)

        return version

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def build(self):
        """int: The build number for this build. """
        return self._build

    @property
    def candidate(self):
        """int: The release candidate number for this build. """
        return self._candidate

    @property
    def display_name(self):
        """str: The name to display ({version}{-product})."""
        value = str(self)

        if self.product is not None:
            value = "{}-{}".format(value, self.product)

        return value

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
    def product(self):
        """str: The optional extra product."""
        return self._product

    @property
    def version(self):
        """tuple(int): A tuple containing version information. """
        version = [self.major, self.minor, self.build]

        # Add the candidate number if necessary.
        if self.candidate is not None:
            version.append(self.candidate)

        return tuple(version)

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

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

        if self.product is not None:
            args["product"] = "-{}".format(self.product)

        else:
            args["product"] = ""

        return value.format(**args)


class HoudiniBuildData:
    """This class stores Houdini build data.

    :param data: A build data dictionary.
    :type data: dict

    """

    def __init__(self, data):
        self._file_template = data["file_template"]
        self._types = data["types"]
        self._versions = data["versions"]

    # -------------------------------------------------------------------------
    # NON-PUBLIC METHODS
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

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

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

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
        all_args.extend(_flatten_items(self._types[system].get("installer_args", ())))

        # Look for major.minor specific installer args.
        if major_minor is not None:
            if major_minor in self.versions:
                # Get the build information.
                version_data = self.versions[major_minor]

                # Try to find any specific installer args for the current version
                # and system.
                if "installer_args" in version_data:
                    all_args.extend(
                        _flatten_items(version_data["installer_args"].get(system, ()))
                    )

        return tuple(all_args)


class HoudiniBuildManager:
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

    # -------------------------------------------------------------------------
    # SPECIAL METHODS
    # -------------------------------------------------------------------------

    def __repr__(self):
        return "<HoudiniBuildManager>"

    # -------------------------------------------------------------------------
    # NON-PUBLIC METHODS
    # -------------------------------------------------------------------------

    def _populate_installable_packages(self):
        """Populate the installable build lists.

        :return:

        """
        files = []

        archive_ext = _SETTINGS_MANAGER.build_data.get_archive_extension()

        archive_template = _SETTINGS_MANAGER.build_data.file_template

        glob_string = archive_template.format(
            product="houdini*", version="*", arch="*", ext=archive_ext
        )

        # We need to glob in each directory for houdini installation packages.
        for directory in _SETTINGS_MANAGER.system.locations:
            search_path = os.path.join(directory, glob_string)

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

        format_args = {"version": "*", "product": "*"}

        # Generate the path to glob with.
        glob_string = os.path.join(
            self._install_target, self._install_folder.format(**format_args)
        )

        # Glob in the install location for installed Houdini builds.
        paths = glob.glob(glob_string)

        # Convert all the install directories to InstalledHoudiniBuild objects
        # if they are not symlinks.
        self._installed = [
            InstalledHoudiniBuild(path) for path in paths if not os.path.islink(path)
        ]

        self.installed.sort(key=attrgetter("version"))

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def installable(self):
        """tuple(HoudiniInstallFile): A tuple of installable Houdini builds."""
        return self._installable

    @property
    def installed(self):
        """tuple(InstalledHoudiniBuild): A tuple of installed Houdini builds."""
        return self._installed

    # -------------------------------------------------------------------------
    # STATIC METHODS
    # -------------------------------------------------------------------------

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
        # Download to the first available installation location.
        download_dir = os.path.expandvars(_SETTINGS_MANAGER.system.locations[0])

        for build_number in build_numbers:
            # Get the build file name for the current day
            version, build = _get_build_to_download(build_number)

            downloaded_path = sidefx_web_api.download_build(
                download_dir, version, build
            )

            if downloaded_path is not None:
                package = HoudiniInstallFile(downloaded_path)
                package.install(create_symlink)

    @staticmethod
    def download_builds(build_numbers, product="houdini"):
        """Download and a list of builds.

        Build numbers can be explicit numbers or major.minor versions.

        :param build_numbers: A list of build numbers to process.
        :type build_numbers: list(str)
        :param product: The specific product name.
        :type product: str
        :return:

        """
        # Download to the first available installation location.
        download_dir = os.path.expandvars(_SETTINGS_MANAGER.system.locations[0])

        archive_paths = []

        for build_number in build_numbers:
            # Get the build file name for the current day
            version, build = _get_build_to_download(build_number)

            downloaded_path = sidefx_web_api.download_build(
                download_dir, version, build, product=product
            )

            if downloaded_path is not None:
                archive_paths.append(downloaded_path)

        return archive_paths

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def get_default_build(self):
        """Attempt to find a default build.

        :return: The default build, if any.
        :rtype: InstalledHoudiniBuild or None

        """
        default = None

        # Get the builds that are installed.
        builds = self.installed

        # Ensure we have system settings available.
        if _SETTINGS_MANAGER.system is not None:
            # Get the defaults from the system settings.
            default_name = _SETTINGS_MANAGER.system.default_version
            default_product = _SETTINGS_MANAGER.system.default_product

            # Filter the list of builds by the default product.
            builds = [build for build in builds if build.product == default_product]

            # If a default name was given then filter the builds based on that.
            if default_name is not None:
                default = find_matching_builds(default_name, builds)

        # If the default could not be found (or none was specified) use the
        # latest build.
        if default is None and builds:
            default = builds[-1]

        return default


class HoudiniEnvironmentSettings:
    """This class stores environment settings.

    :param data: The source data dict.
    :type data: dict

    """

    def __init__(self, data):
        self._paths = data.get("paths", {})
        self._variables = data.get("variables", [])

        self._test_paths = data.get("test_paths", {})
        self._test_variables = data.get("test_variables", [])

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

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

    # -------------------------------------------------------------------------
    # STATIC METHODS
    # -------------------------------------------------------------------------

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

        # Only set LD_LIBRARY_PATH if it already exists.
        if "LD_LIBRARY_PATH" in os.environ:
            # We want to have HDSO at the end so that libs which may be
            # included in HDSO are found last.
            _set_variable(
                "LD_LIBRARY_PATH", (os.environ["LD_LIBRARY_PATH"], os.environ["HDSO"])
            )

        # Set variables with the version information.
        _set_variable("HOUDINI_MAJOR_RELEASE", installed_build.major)
        _set_variable("HOUDINI_MINOR_RELEASE", installed_build.minor)
        _set_variable("HOUDINI_BUILD_VERSION", installed_build.build)
        _set_variable("HOUDINI_VERSION", installed_build)

        # Insert the Houdini bin directories at the head of the PATH.
        _set_variable("PATH", (os.environ["HB"], os.environ["HSB"], os.environ["PATH"]))

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

    def set_custom_environment(self):
        """Apply custom env settings from package file.

        :return:

        """
        # Set variables first so they can possibly be used in custom paths.
        for variable, value in self.paths.items():
            _set_variable(variable, ":".join(value))

        for variable, value in self.variables.items():
            _set_variable(variable, value)

    def set_test_path_environment(self):
        """Apply test_path env settings from package file.

        :return:

        """
        # Set variables first so they can possibly be used in custom paths.
        for variable, value in self.test_paths.items():
            _set_variable(variable, ":".join(value))

        for variable, value in self.test_variables.items():
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
            product="houdini(-[a-z0-9]+)*",
            version="([0-9\\.]*)",
            arch=".+",
            ext=archive_ext,
        )

        result = re.match(pattern, os.path.basename(path))

        product = result.group(1)

        if product is not None:
            product = product.lstrip("-")

        version_string = result.group(2)

        # Get the build number components.
        components = [int(val) for val in version_string.split(".")]

        # If we have 3 then we don't have a release candidate value so we
        # append None.
        if len(components) == 3:
            components.append(None)

        super().__init__(path, components, product=product)

        self._install_target = _SETTINGS_MANAGER.system.installation.target
        self._install_folder = _SETTINGS_MANAGER.system.installation.folder
        self._link_name = _SETTINGS_MANAGER.system.installation.link_name

    # -------------------------------------------------------------------------
    # NON-PUBLIC METHODS
    # -------------------------------------------------------------------------

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

        print("Extracting {} to {}".format(self.path, temp_path))

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

        print("Running Houdini installer: {}".format(" ".join(cmd)))
        subprocess.call(cmd)

        # Remove the temporary extraction directory.
        print("Removing temporary install files.")
        shutil.rmtree(extract_path)

        if link_path is not None:
            print("Linking {} to {}".format(link_path, install_path))

            try:
                os.symlink(install_path, link_path)

            except OSError as inst:
                if inst.errno == errno.EEXIST:
                    os.remove(link_path)
                    os.symlink(install_path, link_path)

                else:
                    raise

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

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
            self._install_target, self.format_string(self._install_folder)
        )

        link_path = None

        if create_symlink:
            link_path = os.path.join(
                self._install_target, self.format_string(self._link_name)
            )

        # Check to see if the build is already installed.  If it is
        # we throw an exception.
        if os.path.exists(install_path):
            raise BuildAlreadyInstalledError(self.display_name)

        system = platform.system()

        if system == "Linux":
            self._install_linux(install_path, link_path)

        elif system == "Windows":
            raise UnsupportedOSError("Windows is not supported")

        elif system == "Darwin":
            raise UnsupportedOSError("OS X is not supported")

        # Notify that the build installation has completed.
        print("Installation of Houdini {} complete.".format(self.display_name))


class HoudiniInstallationSettings:
    """This class stores Houdini installation settings.

    :param data: The source data dict.
    :type data: dict

    """

    def __init__(self, data):
        self._target = data["target"]
        self._folder = data["folder"]
        self._link_name = data.get("symlink")

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

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


class HoudiniPluginSettings:
    """This class stores Houdini plugin settings.

    :param data: The source data dict.
    :type data: dict

    """

    def __init__(self, data):
        self._target = data["target"]
        self._folder = data["folder"]

        self._root = None
        self._command = None

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def folder(self):
        """str: The folder for Houdini plugins."""
        return self._folder

    @property
    def target(self):
        """str: The base path to the Houdini plugin directory."""
        return self._target


class HoudiniSettingsManager:
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
            config_path = os.path.join(os.path.dirname(__file__), _PACKAGE_CONFIG_FILE)

        # Couldn't find any valid files so we have nothing left to do.
        if not os.path.exists(config_path):
            raise IOError("Could not find houdini package configuration file")

        with open(config_path) as handle:
            # Get the json data.
            data = json.load(handle)

            # Construct settings objects for available data.
            self._environment = HoudiniEnvironmentSettings(data["environment"])

            self._system = HoudiniSystemSettings(data["system"])

        # Path to the build data config file.  This file should always be
        # alongside this module.
        build_config_path = os.path.join(os.path.dirname(__file__), _BUILD_DATA_FILE)

        # Couldn't find any valid files so we have nothing left to do.
        if not os.path.exists(build_config_path):
            raise IOError("Could not find houdini build configuration file")

        with open(build_config_path) as handle:
            data = json.load(handle)

            self._build_data = HoudiniBuildData(data)

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

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


class HoudiniSystemSettings:
    """This class stores Houdini system settings.

    :param data: The source data dict.
    :type data: dict

    """

    def __init__(self, data):
        self._locations = data["archive_locations"]
        self._plugins = None
        self._default_product = None
        self._default_version = None

        self._installation = HoudiniInstallationSettings(data["installation"])

        if "default_version" in data:
            self._default_version = data["default_version"]

        if "default_product" in data:
            self._default_product = data["default_product"]

        # Plugin data is optional.
        if "plugins" in data:
            self._plugins = HoudiniPluginSettings(data["plugins"])

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def default_product(self):
        """str or None: A default product string."""
        return self._default_product

    @property
    def default_version(self):
        """str or None: A default build version string."""
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
        """HoudiniPluginSettings or None: Houdini plugin settings."""
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
        pattern = folder_name.format(version="([0-9\\.]*)", product="(-[a-z0-9]*)*")

        result = re.match(pattern, os.path.basename(path))

        # Extract the build version numbers from the directory name.
        version_string = result.group(1)
        product = result.group(2)

        if product is not None:
            product = product.lstrip("-")

        # Get the build number components.
        components = [int(val) for val in version_string.split(".")]

        # If we have 3 then we don't have a release candidate value so we
        # append None.
        if len(components) == 3:
            components.append(None)

        super().__init__(path, components, product=product)

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------

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
            print("Initializing test_path environment\n")
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
            parent, self.format_string(_SETTINGS_MANAGER.system.installation.link_name)
        )

        # Check if the link exists and if it points to this build.  If so, try
        # to remove it.
        if os.path.islink(link_path):
            if os.path.realpath(link_path) == self.path:
                print("Removing symlink {} -> {}".format(link_path, self.path))

                try:
                    os.unlink(link_path)

                except OSError as inst:
                    print("Error: Could not remove symlink")
                    print(inst)

        print("Removing installation directory {}".format(self.path))

        shutil.rmtree(self.path)

        # If there are plugins, remove them.
        if self.plugin_path is not None:
            if os.path.isdir(self.plugin_path):
                print("Removing compiled operators in {}".format(self.plugin_path))

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
        super().__init__()

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


def _get_build_to_download(build):
    """Get the build version  to download.

    If the passed value is not an explict build number (eg. 15.0) then
    the build for the current day of that major/minor will be downloaded.

    :param build: The target build number.
    :type build: str
    :return: The target build information.
    :rtype: tuple(str)

    """
    components = build.split(".")

    num_components = len(components)

    if num_components == 1:
        components.append("0")

    if num_components == 2:
        return ".".join(components), None

    # Always treat the last component as the 'build'.  Unlike Houdini itself
    # which would treat a release candidate version as part of the build number
    # the web api will treat the candidate version as the build number and the
    # the 3 main components as the version.
    return ".".join(components[: num_components - 1]), components[-1]


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
    :rtype: InstalledHoudiniBuild or None

    """
    version = match_string
    product = None

    if "-" in match_string:
        version, product = match_string.split("-")

    # Filter all installed builds that match the build version
    # string.
    matching = [
        build
        for build in builds
        if str(build).startswith(version) and build.product == product
    ]

    # If there are any that match, use the latest/only one.
    if matching:
        return matching[-1]

    return None


# =============================================================================

# Build settings for common use by all Houdini objects.
_SETTINGS_MANAGER = HoudiniSettingsManager()
