
# Quickly compile Qt icons using PySide2.
build-icons:
	pyside2-rcc -o python/ht/ui/icons.py icons/icons.qrc

# Invoke hcmake and make to build all plugins.
build-plugins:
	mkdir -p ${CURDIR}/plugins/build
	cd ${CURDIR}/plugins/build && hcmake .. && make

# Build a single plugin: build-plugin PLUGIN={PLUGIN_NAME}
build-plugin:
	mkdir -p ${CURDIR}/plugins/build
	cd ${CURDIR}/plugins/build && hcmake .. && make ${PLUGIN}

# Clean built plugins.
clean-plugins:
	cd ${CURDIR}/plugins/build && make clean

# List all available plugins
list-targets:
	cd ${CURDIR}/plugins/build && make help

# Initialize the build location and run cmake
init-build:
	mkdir -p ${CURDIR}/plugins/build
	cd ${CURDIR}/plugins/build && hcmake ..

# Run Python unit tests
run-tests:
	hython bin/run_tests.py
