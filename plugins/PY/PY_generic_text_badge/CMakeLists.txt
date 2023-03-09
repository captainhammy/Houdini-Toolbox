
project( PY_generic_text_badge )

set( library_name _ht_generic_text_badge )

# Add a library and its source files.
add_library( ${library_name} SHARED
    PY_generic_text_badge.C
)

# Link against the Houdini libraries, and add required include directories and
# compile definitions.
target_link_libraries( ${library_name} Houdini )

# Sets several common target properties, such as the library's output directory.
houdini_configure_target( ${library_name} INSTDIR "${HOUDINI_PYTHON_BUILD_PATH}/houdini_toolbox/nodes" )

# Include the relevant OPUI source dir so we can find the necessary header.
target_include_directories( ${library_name} PRIVATE ${OPUI_GenericTextBadge_SOURCE_DIR} )
