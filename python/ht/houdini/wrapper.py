"""This module contains a class to set up an environment and launch Houdini
related applications based on arguments.

Synopsis
--------

Classes:
    HoudiniWrapper
        Initialize the environment and run Houdini related applications.

"""
__author__ = "Graham Thompson"
__email__ = "captainhammy@gmail.com"

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
import json
import os
import signal
import subprocess
import sys

# Houdini Toolbox Imports
import ht.argument
import ht.houdini.package
import ht.output
import ht.utils

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "HoudiniWrapper"
]

# =============================================================================
# CLASSES
# =============================================================================

class HoudiniWrapper(object):
    """Initialize the environment and run Houdini related application.

    """

    # =========================================================================
    # CONSTRUCTORS
    # =========================================================================

    def __init__(self):
        """Initialize a HoudiniWrapper object.

        Raises:
            N/A

        Returns:
            N/A

        Initializing the object will also run the command.

        """
        self._arguments = None
        self._build = None
        self._programName = None
        self._programArgs = None

        # Build a parser.
        self._parser = _buildParser()

        # Parse the arguments.
        self._arguments, self.programArgs = self.parser.parse_known_args()

        # Get the name of the executable we are trying to run.
        self.programName = os.path.basename(sys.argv[0])

        self._nojemalloc = self.arguments.nojemalloc
        self._silent = self.arguments.silent
        self._testpath = self.arguments.testpath

        self._print("Houdini Wrapper:\n", colored="darkyellow")

        # If version is False (no argument), display any availble versions and
        # exit.
        if not self.arguments.version:
            self._dislayVersions()
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
        self.build.setupEnvironment(allowCustom=not self.testpath)

        if self.testpath:
            # Use Houdini's internal Python.
            os.environ["HOUDINI_USE_HFS_PYTHON"] = "1"

        # Handle setting options when the 'hmake' compile command is used.
        if self.programName == "hmake":
            self.programName = "make"

            # Set the plugin installation directory to the plugin path if
            # the build has one.
            if self.build.pluginPath is not None:
                os.environ["INSTDIR"] = self.build.pluginPath

        # Process any specified argument variables.
        if self.arguments.var is not None:
            for var in self.arguments.var:
                name, value = var.split('=')
                os.environ[name] = value

        # Dumping all the environment and Houdini settings.
        if self.arguments.dumpenv:
            # To display the Houdini configuration, change the program to run
            # hconfig -a.
            self.programName = "hconfig"
            self.programArgs = ["-a"]

            self._print("Dumping env settings\n", colored="darkyellow")

            # Dump the environment with 'printenv'.
            proc = subprocess.Popen(
                "printenv",
                stdout=subprocess.PIPE
            )

            self._print(proc.communicate()[0])
            self._print()

        # Start with the name of the program to run.
        runArgs = [self.programName]

        # If we don't want to have Houdini use jemalloc we need to replace the
        # run args. For more information, see
        # http://www.sidefx.com/docs/houdini12.5/ref/panes/perfmon
        if self.nojemalloc:
            runArgs = self._setNoJemalloc()

        # Print the Houdini version information.
        self._print(
            "\tHoudini {build}: {path}\n".format(
                build=self.build,
                path=self.build.path
            )
        )

        # Print the command being run.
        self._print(
            "Launching {app} {args} ... ".format(
                app=" ".join(runArgs),
                args=" ".join(self.programArgs)
            ),
            colored="darkyellow"
        )

        # Run the application.
        proc = subprocess.Popen(runArgs + self.programArgs)

        # Display the process id.
        self._print(
            "{app} process id: {id}".format(
                app=self.programName,
                id=proc.pid+2
            ),
            colored="blue"
        )

        # Wait for the program to complete.
        proc.wait()

        # Get the return code.
        returnCode = proc.returncode

        # If the program didn't end clean, print a message.
        if returnCode != 0:
            self._print(
                "{app} died with signal {sig}.".format(
                    app=self.programName,
                    sig=abs(returnCode)
                ),
                colored="darkred"
            )

        # Exit with the program's return code.
        sys.exit(returnCode)

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def __repr__(self):
        return "<HoudiniWrapper '{app}' ({build})>".format(
            app=self.programName,
            build=self.build
        )

    # =========================================================================
    # NON-PUBLIC METHODS
    # =========================================================================

    # -------------------------------------------------------------------------
    #    Name: _dislayVersions
    #  Raises: N/A
    # Returns: None
    #    Desc: Display a list of Houdini versions that are available to
    #          install, run or uninstall.
    # -------------------------------------------------------------------------
    def _dislayVersions(self):
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

    # -------------------------------------------------------------------------
    #    Name: _findBuild
    #  Raises: N/A
    # Returns: None
    #    Desc: Search for the selected build.  If no valid build was selected
    #          print a message.
    # -------------------------------------------------------------------------
    def _findBuild(self):
        # Construct a HoudiniBuildManager to handle all our available Houdini
        # options.
        manager = ht.houdini.package.HoudiniBuildManager()

        # If trying to install, get any builds that are installable.
        if self.arguments.install:
            searchBuilds = manager.installable

        # Get the installed builds.
        else:
            searchBuilds = manager.installed

        # Couldn't find any builds, so print the appropriate message.
        if not searchBuilds:
            if self.arguments.install:
                self._print("No builds found to install.")

            elif self.arguments.uninstall:
                self._print("No builds found to uninstall.")

            else:
                self._print("No builds found.")

            return

        # Use the last build in the list since it is sorted by version.
        if self.arguments.version == "latest":
            self.build = searchBuilds[-1]

        # Look for a build matching the string.
        else:
            for installed in searchBuilds:
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

    # -------------------------------------------------------------------------
    #    Name: _print
    #    Args: msg="" : (str)
    #              The message to print.
    #          colored=None : (str)
    #              An optional color to print the message in.
    #  Raises: N/A
    # Returns: None
    #    Desc: Print a message, optionally with color, respecting the -silent
    #          flag.
    # -------------------------------------------------------------------------
    def _print(self, msg="", colored=None):
        # Doing colored output.
        if colored is not None:
            shell = ht.output.ShellOutput()

            # Run the message through the styler.
            msg = getattr(shell, colored)(msg)

        # Print the message.
        if not self.silent:
            print msg
    # -------------------------------------------------------------------------
    #    Name: _setNoJemalloc
    #  Raises: N/A
    # Returns: [str]
    #              The application run args to launch without jemalloc.
    #    Desc: Set the environment in order to run without jemalloc.
    # -------------------------------------------------------------------------
    def _setNoJemalloc(self):
        ldPath = "{hdso}/empty_jemalloc".format(
            hdso=os.environ["HDSO"]
        )

        # See if the LD_LIBRARY_PATH is already set since we need to modify it.
        existingLdPath = os.getenv("LD_LIBRARY_PATH")

        # If the path exists we insert our custom part before the existing
        # values.
        if existingLdPath is not None:
            ldPath = "{new}:{existing}".format(
                new=ldPath,
                existing=existingLdPath
            )

        # Set the variable to contain our path.
        os.environ["LD_LIBRARY_PATH"] = ldPath

        # Build the new list of main run arguments and return them.
        runArgs = [
            "/lib64/ld-linux-x86-64.so.2",
            "--inhibit-rpath",
            "''",
            "{path}/bin/{name}-bin".format(
                path=self.build.path,
                name=self.programName
            )
        ]

        return runArgs

    # =========================================================================
    # INSTANCE PROPERTIES
    # =========================================================================

    @property
    def arguments(self):
        """(argparse.Namespace) The parsed, known wrapper args."""
        return self._arguments

    @property
    def build(self):
        """(ht.houdini.package.HoudiniInstall) The Houdini build to run."""
        return self._build

    @build.setter
    def build(self, build):
        self._build = build

    @property
    def nojemalloc(self):
        """(bool) Launch with out jemalloc."""
        return self._nojemalloc

    @property
    def parser(self):
        """(ht.argument.ArgumentParser) The wrapper argument parser."""
        return self._parser

    @parser.setter
    def parser(self, parser):
        self._parser = parser

    @property
    def programArgs(self):
        """([str]) A list of arguments to pass to the application."""
        return self._programArgs

    @programArgs.setter
    def programArgs(self, programArgs):
        self._programArgs = programArgs

    @property
    def programName(self):
        """(str) The name of the program to run."""
        return self._programName

    @programName.setter
    def programName(self, programName):
        self._programName = programName

    @property
    def silent(self):
        """(bool) Don't output verbose messages."""
        return self._silent

    @property
    def testpath(self):
        """(bool) Run the application outside of the custom environment."""
        return self._testpath


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================

# -----------------------------------------------------------------------------
#    Name: _buildParser
#  Raises: N/A
# Returns: ht.argument.ArgumentParser
#              The wrapper argument parser.
#    Desc: Build an ArgumentParser for the wrapper.
# -----------------------------------------------------------------------------
def _buildParser():
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
    installGroup = parser.add_mutually_exclusive_group()

    installGroup.add_argument(
        "-install",
        action="store_true",
        default=False,
        help="Install a Houdini build."
    )

    installGroup.add_argument(
        "-uninstall",
        action="store_true",
        default=False,
        help="Uninstall a Houdini build."
    )

    return parser

