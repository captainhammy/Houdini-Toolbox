
# Default Houdini version to use for commands.
HOUDINI_VERSION := $(shell houdini --default-version)

# Quickly compile Qt icons using PySide2.
build-icons:
	pyside2-rcc -o python/ht/ui/icons.py icons/icons.qrc

# Invoke hcmake and make to build all plugins.
build-plugins:
	mkdir -p ${CURDIR}/plugins/build
	cd ${CURDIR}/plugins/build && hcmake --version $(HOUDINI_VERSION) .. && make

# Build a single plugin: build-plugin PLUGIN={PLUGIN_NAME}
build-plugin:
	mkdir -p ${CURDIR}/plugins/build
	cd ${CURDIR}/plugins/build && hcmake --version $(HOUDINI_VERSION) .. && make ${PLUGIN}

# Clean built plugins.
clean-plugins:
	cd ${CURDIR}/plugins/build && make clean
	rm -rf ${CURDIR}/plugins/build

# List all available plugins
list-targets:
	cd ${CURDIR}/plugins/build && make help

# Initialize the build location and run cmake
init-build:
	mkdir -p ${CURDIR}/plugins/build
	cd ${CURDIR}/plugins/build && hcmake --version $(HOUDINI_VERSION) ..

.PHONY: run-flake run-lint

# Run all linting targets
run-all-linting: run-flake run-lint

# Run flake8 linting
run-flake:
	flake8

# Run python linting
run-lint:
	bin/run_lint --rcfile=.pylint.rc --package-name=ht --add-file houdini/pyfilter/ht-pyfilter.py --add-dir bin

# Run Python unit tests
run-tests:
	@coverage erase
	env --unset=HOUDINI_PATH TOOLBAR_PATH=`pwd`/houdini/toolbar hython --version $(HOUDINI_VERSION) -m pytest tests/
