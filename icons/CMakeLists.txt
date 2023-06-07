# Generate a compiled resource file for any icons we are using and install it into the appropriate
# location.

# Convert our icons resource file into a Python file via pyside2-rcc.
execute_process(
    COMMAND pyside2-rcc -o $ENV{REZ_BUILD_PATH}/icons/icons.py ${CMAKE_CURRENT_SOURCE_DIR}/icons.qrc
    COMMAND_ECHO STDOUT
)

# Install the icons.py file into the main Python area.
install(
    FILES
    "$ENV{REZ_BUILD_PATH}/icons/icons.py"
    DESTINATION
    "$ENV{REZ_BUILD_INSTALL_PATH}/python/houdini_toolbox/ui"
)
