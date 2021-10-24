
project( SOP_PointsFromVoxels )

set( op_context sop )
set( op_name pointsfromvoxels )
set( op_namespace com.houdinitoolbox )
set( op_version 1 )

set( library_name SOP_PointsFromVoxels )

# Add a library and its source files.
add_library( ${library_name} SHARED
    SOP_PointsFromVoxels.C
    SOP_PointsFromVoxels.h
)

# Link against the Houdini libraries, and add required include directories and
# compile definitions.
target_link_libraries( ${library_name} Houdini )

# Include ${CMAKE_CURRENT_BINARY_DIR} for the generated header.
target_include_directories( ${library_name} PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}
)

# Sets several common target properties, such as the library's output directory.
houdini_configure_target( ${library_name} INSTDIR "${HOUDINI_TOOLBOX_PLUGIN_BUILD_DIR}/dso" )

add_secondary_files( SHELF 1 ICON svg HELP 1 )

