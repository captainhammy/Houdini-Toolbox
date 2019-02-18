
project( SOP_DopImpactPoints )

set( op_context SOP )

set( library_name SOP_DopImpactPoints )

# Add a library and its source files.
add_library( ${library_name} SHARED
    SOP_DopImpactPoints.C
    SOP_DopImpactPoints.h
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

add_secondary_files( SHELF sop_dopimpactpoints.shelf HELP dopimpactpoints.txt )

