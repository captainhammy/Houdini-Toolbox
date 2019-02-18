
# Quickly compile Qt icons using PySide2.
build-icons:
	pyside2-rcc -o python/ht/ui/icons.py icons/icons.qrc

# Envoke hcmake and make to build all plugins.
build-plugins:
	mkdir -p ${CURDIR}/plugins/build
	cd ${CURDIR}/plugins/build && hcmake .. && make

# Clean built plugins.
clean-plugins:
	cd ${CURDIR}/plugins/build && make clean

run-tests:
	hython bin/run_tests.py

