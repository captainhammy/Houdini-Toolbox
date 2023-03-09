
project( ROP_Script )

set( OP_CONTEXT rop )
set( OP_NAME script )
set( OP_VERSION 1 )
set( OP_LABEL "${HT_LABEL_PREFIX} Script" )

set( library_name ROP_Script )

conifgure_operator_files( SHELF 1 ICON svg HELP 1 )

# Copy files so we can use cmake to replace naming bits.
configure_file( ROP_Script.C.in ROP_Script.C )
configure_file( ROP_Script.h ROP_Script.h COPYONLY )

# Add a library and its source files.
add_library( ${library_name} SHARED
    "${PROJECT_BINARY_DIR}/ROP_Script.C"
    "${PROJECT_BINARY_DIR}/ROP_Script.h"
)

# Link against the Houdini libraries, and add required include directories and
# compile definitions.
target_link_libraries( ${library_name} Houdini )

# Sets several common target properties, such as the library's output directory.
houdini_configure_target( ${library_name} INSTDIR ${HOUDINI_DSO_BUILD_PATH} )
