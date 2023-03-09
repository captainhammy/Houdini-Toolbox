
project( SOP_PrimCentroid )

set( OP_CONTEXT sop )
set( OP_NAME primcentroid )
set( OP_VERSION 1 )
set( OP_LABEL "${HT_LABEL_PREFIX} Primitive Centroid" )

set( library_name SOP_PrimCentroid )

conifgure_operator_files( SHELF 1 ICON svg HELP 1 )

# Copy files so we can use cmake to replace naming bits.
configure_file( SOP_PrimCentroid.C.in SOP_PrimCentroid.C )
configure_file( SOP_PrimCentroid.h SOP_PrimCentroid.h COPYONLY )

# Add a library and its source files.
add_library( ${library_name} SHARED
    "${PROJECT_BINARY_DIR}/SOP_PrimCentroid.C"
    "${PROJECT_BINARY_DIR}/SOP_PrimCentroid.h"
)

# Link against the Houdini libraries, and add required include directories and
# compile definitions.
target_link_libraries( ${library_name} Houdini )

# Sets several common target properties, such as the library's output directory.
houdini_configure_target( ${library_name} INSTDIR ${HOUDINI_DSO_BUILD_PATH} )
