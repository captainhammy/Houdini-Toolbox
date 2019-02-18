#cmake_minimum_required( VERSION 3.6 )

project( ROP_Script )

# CMAKE_PREFIX_PATH must contain the path to the toolkit/cmake subdirectory of
# the Houdini installation. See the "Compiling with CMake" section of the HDK
# documentation for more details, which describes several options for
# specifying this path.
#list( APPEND CMAKE_PREFIX_PATH "$ENV{HFS}/toolkit/cmake" )

# Locate Houdini's libraries and header files.
# Registers an imported library target named 'Houdini'.
#find_package( Houdini REQUIRED )

set (op_context ROP )

set( library_name ROP_script )

# Code generation for the embedded DS file in SOP_Star.C.
#houdini_generate_proto_headers( FILES SOP_Star.C )

# Add a library and its source files.
add_library( ${library_name} SHARED
    ROP_Script.C
    ROP_Script.h
)

# Link against the Houdini libraries, and add required include directories and
# compile definitions.
target_link_libraries( ${library_name} Houdini )

# Include ${CMAKE_CURRENT_BINARY_DIR} for the generated header.
target_include_directories( ${library_name} PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}
)

# Sets several common target properties, such as the library's output directory.
houdini_configure_target( ${library_name} INSTDIR "$ENV{PLUGIN_BUILD_DIR}/dso" )

add_secondary_files( SHELF rop_script.shelf ICON ROP_script.svg HELP script.txt )


