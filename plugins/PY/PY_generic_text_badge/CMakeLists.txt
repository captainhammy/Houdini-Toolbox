
project( PY_generic_text_badge )

set( library_name _ht_generic_text_badge )

# Add a library and its source files.
add_library( ${library_name} SHARED
    PY_generic_text_badge.C
)

# Link against the Houdini libraries, and add required include directories and
# compile definitions.
target_link_libraries( ${library_name} Houdini )

# Include ${CMAKE_CURRENT_BINARY_DIR} for the generated header.
target_include_directories( ${library_name} PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}
)

# Sets several common target properties, such as the library's output directory.
houdini_configure_target( ${library_name} INSTDIR "$ENV{PLUGIN_BUILD_DIR}/python" )

target_include_directories( ${library_name} PRIVATE ${OPUI_GenericTextBadge_SOURCE_DIR} )

