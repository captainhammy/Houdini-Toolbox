
project( OPUI_GenericTextBadge )

set( library_name OPUI_GenericTextBadge )

# Add a library and its source files.
add_library( ${library_name} SHARED
    OPUI_GenericTextBadge.C
)

# Link against the Houdini libraries, and add required include directories and
# compile definitions.
target_link_libraries( ${library_name} Houdini )

# Include ${CMAKE_CURRENT_BINARY_DIR} for the generated header.
target_include_directories( ${library_name} PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}
)

# Sets several common target properties, such as the library's output directory.
houdini_configure_target( ${library_name} INSTDIR "${HOUDINI_OPUI_BUILD_PATH}" )
