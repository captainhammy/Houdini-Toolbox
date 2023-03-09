
project( SOP_DopImpactPoints )

set( OP_CONTEXT sop )
set( OP_NAME dopimpactpoints )
set( OP_VERSION 1 )
set( OP_LABEL "${HT_LABEL_PREFIX} DOP Impact Points" )

# Use custom values due to using internal Houdini icons.
set(icon_name "POP_hitinfo")
set(help_icon_name "POP/hitinfo")

set( library_name SOP_DopImpactPoints )

conifgure_operator_files( SHELF 1 HELP 1 )

# Copy files so we can use cmake to replace naming bits.
configure_file( SOP_DopImpactPoints.C.in SOP_DopImpactPoints.C )
configure_file( SOP_DopImpactPoints.h SOP_DopImpactPoints.h COPYONLY )

# Add a library and its source files.
add_library( ${library_name} SHARED
    "${PROJECT_BINARY_DIR}/SOP_DopImpactPoints.C"
    "${PROJECT_BINARY_DIR}/SOP_DopImpactPoints.h"
)

# Link against the Houdini libraries, and add required include directories and
# compile definitions.
target_link_libraries( ${library_name} Houdini )

# Sets several common target properties, such as the library's output directory.
houdini_configure_target( ${library_name} INSTDIR ${HOUDINI_DSO_BUILD_PATH} )
