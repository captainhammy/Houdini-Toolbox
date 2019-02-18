
project( ROP_Script )

set( help_context out )
set( op_context rop )
set( op_name script )
set( op_namespace com.houdinitoolbox )
set( op_version 1 )

set( library_name ROP_Script )

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

add_secondary_files( SHELF 1 ICON svg HELP 1 )


