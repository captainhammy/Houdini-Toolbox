"""This module contains a class to set up an environment and launch Houdini
related applications based on arguments.

"""
# =============================================================================
# IMPORTS
# =============================================================================

# Python Imports
import os
import subprocess
import sys

# Houdini Toolbox Imports
import ht.argument
import ht.houdini.package
import ht.output
import ht.utils

# =============================================================================
# CLASSES
# =============================================================================

class HoudiniWrapper(object):
    """Initialize the environment and run Houdini related application.

    """

    def __init__(self):
        self._arguments = None
        self._build = None
        self._program_name = None
        self._program_args = None

        # Build a parser.
        self._parser = _build_parser()

        # Parse the arguments.
        self._arguments, self.program_args = self.parser.parse_known_args()

        # Get the name of the executable we are trying to run.
        self.program_name = os.path.basename(sys.argv[0])

        self._no_jemalloc = self.arguments.no_jemalloc
        self._test_path = self.arguments.test_path
        self._log_level = self.arguments.log_level

        os.environ["HT_LOG_LEVEL"] = self._log_level

        _print("Houdini Wrapper:\n", colored="darkyellow")

        # If version is False (no argument), display any available versions and
        # exit.
        if not self.arguments.version:
            self._display_versions()

            return

        # We are going to download and install a build so do this before
        # anything else.
        if self.arguments.dl_install:
            self._download_and_install(self.arguments.create_symlink)

            return

        # Try to find a build.
        self._find_build()

        # No build found, so abort.
        if self.build is None:
            return

        # Install the selected build.
        if self.arguments.install:
            self.build.install(self.arguments.create_symlink)

            return

        # Uninstall the selected build.
        elif self.arguments.uninstall:
            self.build.uninstall()

            return

        # Set the base environment for the build.
        self.build.setup_environment(test_path=self.test_path)

        # Handle setting options when the 'hcmake' compile command is used.
        if self.program_name == "hcmake":
            self.program_name = "cmake"

            # Set the plugin installation directory to the plugin path if
            # the build has one.
            if self.build.plugin_path is not None:
                os.environ["PLUGIN_BUILD_DIR"] = self.build.plugin_path

        # Dumping all the environment and Houdini settings.
        if self.arguments.dump_env:
            # To display the Houdini configuration, change the program to run
            # hconfig -a.
            self.program_name = "hconfig"
            self.program_args = ["-a"]

            _print("Dumping env settings\n", colored="darkyellow")

            # Dump the environment with 'printenv'.
            proc = subprocess.Popen(
                "printenv",
                stdout=subprocess.PIPE
            )

            _print(proc.communicate()[0])
            _print()

        # Start with the name of the program to run.
        run_args = [self.program_name]

        # If we don't want to have Houdini use jemalloc we need to replace the
        # run args. For more information, see
        # http://www.sidefx.com/docs/houdini/ref/panes/perfmon
        if self.no_jemalloc:
            run_args = self._set_no_jemalloc()

        # Print the Houdini version information.
        _print("\tHoudini {}: {}\n".format(self.build, self.build.path))

        # Print the command being run.
        _print(
            "Launching {} {} ... ".format(
                " ".join(run_args),
                " ".join(self.program_args)
            ),
            colored="darkyellow"
        )

        # Run the application.
        proc = subprocess.Popen(run_args + self.program_args)

        # Display the process id.
        _print(
            "{} process id: {}".format(self.program_name, proc.pid+2),
            colored="blue"
        )

        # Wait for the program to complete.
        proc.wait()

        # Get the return code.
        return_code = proc.returncode

        # If the program didn't end clean, print a message.
        if return_code != 0:
            _print(
                "{} exited with signal {}.".format(
                    self.program_name,
                    abs(return_code)
                ),
                colored="darkred"
            )

        # Exit with the program's return code.
        sys.exit(return_code)

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __repr__(self):
        return "<HoudiniWrapper '{}' ({})>".format(
            self.program_name,
            self.build
        )

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    def _display_versions(self):
        """Display a list of Houdini versions that are available to install,
        run or uninstall.

        """
        # Construct a HoudiniBuildManager to handle all our available Houdini
        # options.
        manager = ht.houdini.package.HoudiniBuildManager()

        # List builds that can be installed.
        if self.arguments.install:
            _print("Houdini builds to install:")

            _print(
                '\t' + " ".join(
                    [str(build) for build in manager.installable]
                )
            )

            _print()

        # Builds that can be ran can also be uninstalled.
        else:
            if self.arguments.uninstall:
                _print("Houdini builds to uninstall:")

            else:
                _print("Installed Houdini builds:")

            default_build = manager.get_default_build()

            output = []

            for build in manager.installed:
                if build == default_build:
                    # Run the message through the styler.
                    msg = ht.output.ShellOutput.blue(str(build))

                    output.append(msg)

                else:
                    output.append(str(build))

            _print('\t' + ' '.join(output))

            _print()

    def _download_and_install(self, create_symlink=False):
        """Download and automatically install a build."""
        ht.houdini.package.HoudiniBuildManager.download_and_install(
            self.arguments.dl_install,
            create_symlink
        )

    def _find_build(self):
        """Search for the selected build.  If no valid build was selected
        print a message.

        """
        # Construct a HoudiniBuildManager to handle all our available Houdini
        # options.
        manager = ht.houdini.package.HoudiniBuildManager()

        version = self.arguments.version

        # If trying to install, get any builds that are installable.
        if self.arguments.install:
            search_builds = manager.installable

            # If we are installing builds there is no default so remap to 'latest'.
            if version == "default":
                version = "latest"

        # Get the installed builds.
        else:
            search_builds = manager.installed

        # Couldn't find any builds, so print the appropriate message.
        if not search_builds:
            if self.arguments.install:
                _print("No builds found to install.")

            elif self.arguments.uninstall:
                _print("No builds found to uninstall.")

            else:
                _print("No builds found.")

            return

        # Use the last build in the list since it is sorted by version.
        if version == "latest":
            self.build = search_builds[-1]

        # Support a 'default' build as defined in the config file.
        elif version == "default":
            self.build = manager.get_default_build()

        # Look for a build matching the string.
        else:
            result = manager.find_matching_builds(version, search_builds)

            if result is None:
                _print("Could not find version: {ver}".format(ver=version))

            else:
                self.build = result

    def _set_no_jemalloc(self):
        """Set the environment in order to run without jemalloc."""
        ld_path = os.path.join(os.environ["HDSO"], "empty_jemalloc")

        # See if the LD_LIBRARY_PATH is already set since we need to modify it.
        current_ld_path = os.getenv("LD_LIBRARY_PATH")

        # If the path exists we insert our custom part before the existing
        # values.
        if current_ld_path is not None:
            ld_path = ":".join([ld_path, current_ld_path])

        # Set the variable to contain our path.
        os.environ["LD_LIBRARY_PATH"] = ld_path

        # Build the new list of main run arguments and return them.
        run_args = [
            "/lib64/ld-linux-x86-64.so.2",
            "--inhibit-rpath",
            "''",
            "{}/bin/{}-bin".format(self.build.path, self.program_name)
        ]

        return run_args

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def arguments(self):
        """The parsed, known wrapper args."""
        return self._arguments

    # =========================================================================

    @property
    def build(self):
        """The Houdini build to run."""
        return self._build

    @build.setter
    def build(self, build):
        self._build = build

    # =========================================================================

    @property
    def no_jemalloc(self):
        """Launch with out jemalloc."""
        return self._no_jemalloc

    # =========================================================================

    @property
    def parser(self):
        """The wrapper argument parser."""
        return self._parser

    @parser.setter
    def parser(self, parser):
        self._parser = parser

    # =========================================================================

    @property
    def program_args(self):
        """A list of arguments to pass to the application."""
        return self._program_args

    @program_args.setter
    def program_args(self, program_args):
        self._program_args = program_args

    # =========================================================================

    @property
    def program_name(self):
        """The name of the program to run."""
        return self._program_name

    @program_name.setter
    def program_name(self, program_name):
        self._program_name = program_name

    # =========================================================================

    @property
    def test_path(self):
        """Run the application outside of the custom environment."""
        return self._test_path

# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

def _build_parser():
    """Build an ArgumentParser for the wrapper."""
    # Don't allow abbreviations since we don't want them to interfere with any
    # flags that might need to be passed through.
    parser = ht.argument.ArgumentParser(
        description="Run Houdini related applications.",
        allow_abbrev=False
    )

    parser.add_argument(
        "--dump-env",
        action="store_true",
        help="Display environment variables and values.",
        dest="dump_env"
    )

    parser.add_argument(
        "--log-level",
        help="The Python logging level.",
        default="INFO",
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        dest="log_level"
    )

    parser.add_argument(
        "--no-jemalloc",
        action="store_true",
        help="Launch Houdini in debugging mode without jemalloc.",
        dest="no_jemalloc"
    )

    parser.add_argument(
        "--test-path",
        action="store_true",
        default=False,
        help="Don't include any non-standard environment settings.",
        dest="test_path"
    )

    parser.add_argument(
        "--version",
        nargs="?",
        default="default",
        help="Set the package version."
    )

    # Exclusive group to handle installs and uninstalls.
    install_group = parser.add_mutually_exclusive_group()

    install_group.add_argument(
        "--install",
        action="store_true",
        default=False,
        help="Install a Houdini build."
    )

    install_group.add_argument(
        "--uninstall",
        action="store_true",
        default=False,
        help="Uninstall a Houdini build."
    )

    install_group.add_argument(
        "--dl-install",
        nargs=1,
        help="Download and install today's Houdini build.",
        dest="dl_install"
    )

    parser.add_argument(
        "--create-symlink",
        action="store_true",
        default=True,
        help="Create a major.minor symlink",
        dest="create_symlink"
    )

    return parser


def _print(msg="", colored=None):
    """Print a message, optionally with color.

    """
    # Doing colored output.
    if colored is not None:
        # Run the message through the styler.
        msg = getattr(ht.output.ShellOutput, colored)(msg)

    # Print the message.
    print msg
