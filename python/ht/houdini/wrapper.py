"""This module contains a class to set up an environment and launch Houdini
related applications based on arguments.

"""
# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
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
        self._parser = _buildParser()

        # Parse the arguments.
        self._arguments, self.program_args = self.parser.parse_known_args()

        # Get the name of the executable we are trying to run.
        self.program_name = os.path.basename(sys.argv[0])

        self._nojemalloc = self.arguments.nojemalloc
        self._silent = self.arguments.silent
        self._testpath = self.arguments.testpath

        self._print("Houdini Wrapper:\n", colored="darkyellow")

        # If version is False (no argument), display any availble versions and
        # exit.
        if not self.arguments.version:
            self._dislayVersions()
            return

        # We are going to download and install a build so do this before
        # anything else.
        if self.arguments.dlinstall:
            self._downloadAndInstall()
            return

        # Try to find a build.
        self._findBuild()

        # No build found, so abort.
        if self.build is None:
            return

        # Install the selected build.
        if self.arguments.install:
            self.build.install()
            return

        # Uninstall the selected build.
        elif self.arguments.uninstall:
            self.build.uninstall()
            return

        # Set the base environment for the build.
        self.build.setupEnvironment(testpath=self.testpath)

        # Handle setting options when the 'hmake' compile command is used.
        if self.program_name == "hmake":
            self.program_name = "make"

            # Set the plugin installation directory to the plugin path if
            # the build has one.
            if self.build.plugin_path is not None:
                os.environ["INSTDIR"] = self.build.plugin_path

        # Process any specified argument variables.
        if self.arguments.var is not None:
            for var in self.arguments.var:
                name, value = var.split('=')
                os.environ[name] = value

        # Dumping all the environment and Houdini settings.
        if self.arguments.dumpenv:
            # To display the Houdini configuration, change the program to run
            # hconfig -a.
            self.program_name = "hconfig"
            self.program_args = ["-a"]

            self._print("Dumping env settings\n", colored="darkyellow")

            # Dump the environment with 'printenv'.
            proc = subprocess.Popen(
                "printenv",
                stdout=subprocess.PIPE
            )

            self._print(proc.communicate()[0])
            self._print()

        # Start with the name of the program to run.
        run_args = [self.program_name]

        # If we don't want to have Houdini use jemalloc we need to replace the
        # run args. For more information, see
        # http://www.sidefx.com/docs/houdini15.0/ref/panes/perfmon
        if self.nojemalloc:
            run_args = self._setNoJemalloc()

        # Print the Houdini version information.
        self._print("\tHoudini {}: {}\n".format(self.build, self.build.path))

        # Print the command being run.
        self._print(
            "Launching {} {} ... ".format(
                " ".join(run_args),
                " ".join(self.program_args)
            ),
            colored="darkyellow"
        )

        # Run the application.
        proc = subprocess.Popen(run_args + self.program_args)

        # Display the process id.
        self._print(
            "{} process id: {}".format(self.program_name, proc.pid+2),
            colored="blue"
        )

        # Wait for the program to complete.
        proc.wait()

        # Get the return code.
        returncode = proc.returncode

        # If the program didn't end clean, print a message.
        if returncode != 0:
            self._print(
                "{} exited with signal {}.".format(
                    self.program_name,
                    abs(returncode)
                ),
                colored="darkred"
            )

        # Exit with the program's return code.
        sys.exit(returncode)

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

    def _dislayVersions(self):
        """Display a list of Houdini versions that are available to install,
        run or uninstall.

        """
        # Construct a HoudiniBuildManager to handle all our available Houdini
        # options.
        manager = ht.houdini.package.HoudiniBuildManager()

        # List builds that can be installed.
        if self.arguments.install:
            self._print("Houdini builds to install:")

            self._print(
                '\t' + " ".join(
                    [str(build) for build in manager.installable]
                )
            )

            self._print()

        # Builds that can be ran can also be uninstalled.
        else:
            if self.arguments.uninstall:
                self._print("Houdini builds to uninstall:")

            else:
                self._print("Installed Houdini builds:")

            self._print(
                '\t' + " ".join(
                    [str(build) for build in manager.installed]
                )
            )

            self._print()

    def _downloadAndInstall(self):
        """Download and automatically install a build."""
        ht.houdini.package.HoudiniBuildManager.downloadAndInstall(
            self.arguments.dlinstall
        )

    def _findBuild(self):
        """Search for the selected build.  If no valid build was selected
        print a message.

        """
        # Construct a HoudiniBuildManager to handle all our available Houdini
        # options.
        manager = ht.houdini.package.HoudiniBuildManager()

        # If trying to install, get any builds that are installable.
        if self.arguments.install:
            search_builds = manager.installable

        # Get the installed builds.
        else:
            search_builds = manager.installed

        # Couldn't find any builds, so print the appropriate message.
        if not search_builds:
            if self.arguments.install:
                self._print("No builds found to install.")

            elif self.arguments.uninstall:
                self._print("No builds found to uninstall.")

            else:
                self._print("No builds found.")

            return

        # Use the last build in the list since it is sorted by version.
        if self.arguments.version == "latest":
            self.build = search_builds[-1]

        # Look for a build matching the string.
        else:
            for installed in search_builds:
                if str(installed) == self.arguments.version:
                    self.build = installed
                    break

            # If we didn't find any matching build, display a message.
            else:
                self._print(
                    "Could not find version: {ver}".format(
                        ver=self.arguments.version
                    )
                )

    def _print(self, msg="", colored=None):
        """Print a message, optionally with color, respecting the -silent flag.

        """
        # Doing colored output.
        if colored is not None:
            shell = ht.output.ShellOutput()

            # Run the message through the styler.
            msg = getattr(shell, colored)(msg)

        # Print the message.
        if not self.silent:
            print msg

    def _setNoJemalloc(self):
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
    def nojemalloc(self):
        """Launch with out jemalloc."""
        return self._nojemalloc

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
    def silent(self):
        """Don't output verbose messages."""
        return self._silent

    # =========================================================================

    @property
    def testpath(self):
        """Run the application outside of the custom environment."""
        return self._testpath

# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _buildParser():
    """Build an ArgumentParser for the wrapper."""
    # Don't allow abbreviations since we don't want them to interfere with any
    # flags that might need to be passed through.
    parser = ht.argument.ArgumentParser(
        description="Run Houdini related applications.",
        allow_abbrev=False
    )

    parser.add_argument(
        "-dumpenv",
        action="store_true",
        help="Display environment variables and values."
    )

    parser.add_argument(
        "-nojemalloc",
        action="store_true",
        help="Launch Houdini in debugging mode without jemalloc."
    )

    parser.add_argument(
        "-silent",
        action="store_true",
        default=False,
        help="Don't output verbose information."
    )

    parser.add_argument(
        "-testpath",
        action="store_true",
        default=False,
        help="Don't include any non-standard environment settings."
    )

    parser.add_argument(
        "-version",
        nargs="?",
        default="latest",
        help="Set the package version."
    )

    parser.add_argument(
        "-var",
        action="append",
        nargs="?",
        help="Specify env vars to be set. e.g. -var FOO=5"
    )

    # Exclusive group to handle installs and uninstalls.
    install_group = parser.add_mutually_exclusive_group()

    install_group.add_argument(
        "-install",
        action="store_true",
        default=False,
        help="Install a Houdini build."
    )

    install_group.add_argument(
        "-uninstall",
        action="store_true",
        default=False,
        help="Uninstall a Houdini build."
    )

    install_group.add_argument(
        "-dlinstall",
        nargs=1,
        help="Download and install today's Houdini build."
    )

    return parser

