cmake_minimum_required(VERSION 3.6)

include(RezBuild)

file(GLOB_RECURSE py_files "python/*.py" "python/*.yaml" "python/*.json")

rez_install_files(
    FILES ${py_files}
    DESTINATION .
)

# Handle installing houdini/ files.
file(GLOB_RECURSE houdini_files RELATIVE "${CMAKE_SOURCE_DIR}" "houdini/*")

# Filter files to remove things we don't actually want to install. In particular we want
# to avoid any digital assets and Python bytecode files.
list(FILTER houdini_files EXCLUDE REGEX "houdini/otls/.*|.\.pyc")

rez_install_files(
    ${houdini_files}
    DESTINATION .
)

# As we store one or more digital assets in expanded mode in the VCS we want to explicitly
# process them and collapse them on build.
add_subdirectory(houdini/otls)

# Compile Qt related icons
add_subdirectory(icons)

# Add the plugins/ subdirectory to trigger building of HDK plugins.
add_subdirectory(plugins)
