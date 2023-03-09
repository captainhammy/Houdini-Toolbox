
execute_process(
    COMMAND pyside2-rcc -o $ENV{REZ_BUILD_PATH}/icons/icons.py ${CMAKE_CURRENT_SOURCE_DIR}/icons.qrc
    COMMAND_ECHO STDOUT
)

install(
    FILES
    "$ENV{REZ_BUILD_PATH}/icons/icons.py"
    DESTINATION
    "$ENV{REZ_BUILD_INSTALL_PATH}/python/houdini_toolbox/ui"
)
