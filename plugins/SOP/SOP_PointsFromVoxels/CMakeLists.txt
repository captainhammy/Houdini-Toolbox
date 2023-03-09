
project( SOP_PointsFromVoxels )

set( OP_CONTEXT sop )
set( OP_NAME pointsfromvoxels )
set( OP_VERSION 1 )
set( OP_LABEL "${HT_LABEL_PREFIX} Points From Voxels" )

set( library_name SOP_PointsFromVoxels )

conifgure_operator_files( SHELF 1 ICON svg HELP 1 )

# Copy files so we can use cmake to replace naming bits.
configure_file( SOP_PointsFromVoxels.C.in SOP_PointsFromVoxels.C )
configure_file( SOP_PointsFromVoxels.h SOP_PointsFromVoxels.h COPYONLY )

# Add a library and its source files.
add_library( ${library_name} SHARED
    "${PROJECT_BINARY_DIR}/SOP_PointsFromVoxels.C"
    "${PROJECT_BINARY_DIR}/SOP_PointsFromVoxels.h"
)

# Link against the Houdini libraries, and add required include directories and
# compile definitions.
target_link_libraries( ${library_name} Houdini )

# Sets several common target properties, such as the library's output directory.
houdini_configure_target( ${library_name} INSTDIR ${HOUDINI_DSO_BUILD_PATH} )
