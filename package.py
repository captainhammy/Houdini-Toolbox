"""Package definition file for houdini_toolbox."""

name = "houdini_toolbox"

@early()
def version() -> str:
    """Get the package version.

    Because this project is not versioned we'll just use the short git hash as the version.

    Returns:
        The package version.
    """
    import subprocess

    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()

authors = ["graham thompson"]

requires = [
    "houdini",
]

build_system = "cmake"

build_requires = [
    "PySide2",  # So we can compile resources at build time.
]

plugin_for = ["houdini"]

variants = [
     ["houdini-19.5"],
     ["houdini-20.0"],
 ]

tests = {
    "unit": {
        "command": "coverage erase && hython -m pytest tests",
        "requires": ["houdini", "pytest", "pytest_sugar", "coverage"],
    },
    "flake8": {
        "command": "houdini_package_flake8",
        "requires": ["houdini_package_runner", "houdini"],
        "run_on": "explicit",
    },
    "black-check": {
        "command": "houdini_package_black --check",
        "requires": ["houdini_package_runner", "houdini"],
        "run_on": "explicit",
    },
    "black": {
        "command": "houdini_package_black",
        "requires": ["houdini_package_runner", "houdini"],
        "run_on": "explicit",
    },
    "pylint": {
        "command": "houdini_package_pylint --skip-tests --rcfile pylintrc",
        "requires": ["houdini_package_runner", "houdini"],
        "run_on": "explicit",
    },
    "isort-check": {
        "command": "houdini_package_isort --check --package-names=houdini_toolbox,_ht_generic_text_badge,_ht_generic_image_badge",
        "requires": ["houdini_package_runner", "houdini"],
        "run_on": "explicit",
    },
    "isort": {
        "command": "houdini_package_isort --package-names=houdini_toolbox,_ht_generic_text_badge,_ht_generic_image_badge",
        "requires": ["houdini_package_runner", "houdini"],
        "run_on": "explicit",
    },
}


def commands():
    """Run commands on package setup."""
    env.PYTHONPATH.prepend("{root}/python")

    # We won't want to set HOUDINI_PATH when testing as this will cause Houdini to
    # load and run various things at startup and interfere with test coverage.
    if "HOUDINI_TOOLBOX_TESTING" not in env:
        env.HOUDINI_PATH.prepend("{root}/houdini")


def pre_test_commands():
    """Run commands before testing."""
    # Set an indicator that a test is running, so we can set paths differently.
    env.HOUDINI_TOOLBOX_TESTING = True

    if test.name == "unit":
        env.HOUDINI_DSO_PATH.prepend("{root}/houdini/dso")
        env.HOUDINI_OTLSCAN_PATH.prepend("{root}/houdini/otls")

        # When doing unit tests we need to set the TOOLBAR_PATH variable to point to the folder
        # containing shelf files so that we can access and run tests against them.
        env.TOOLBAR_PATH = f"{this.root}/houdini/toolbar"
