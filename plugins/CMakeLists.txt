

cmake_minimum_required( VERSION 3.6 )

project( HoudiniToolbox )

# CMAKE_PREFIX_PATH must contain the path to the toolkit/cmake subdirectory of
# the Houdini installation. See the "Compiling with CMake" section of the HDK
# documentation for more details, which describes several options for
# specifying this path.
list( APPEND CMAKE_PREFIX_PATH "$ENV{HFS}/toolkit/cmake" )

# Locate Houdini's libraries and header files.
# Registers an imported library target named 'Houdini'.
find_package( Houdini REQUIRED )

function ( add_secondary_files )
    cmake_parse_arguments( MY_INSTALL
        ""
        "SHELF;HELP;ICON"
        ""
        ${ARGN}
    )

    set( files_to_clean "")

    if ( MY_INSTALL_SHELF )
	add_custom_command(
	    TARGET ${library_name} POST_BUILD 
	    COMMAND "${CMAKE_COMMAND}" -E copy
		    "${PROJECT_SOURCE_DIR}/${MY_INSTALL_SHELF}"
		    "$ENV{PLUGIN_BUILD_DIR}/toolbar/${MY_INSTALL_SHELF}"
	    COMMENT "Copying shelf file to target")
	
	list(APPEND files_to_clean "$ENV{PLUGIN_BUILD_DIR}/toolbar/${MY_INSTALL_SHELF}")

    endif()

    if ( MY_INSTALL_ICON )
	add_custom_command(
	    TARGET ${library_name} POST_BUILD 
	    COMMAND "${CMAKE_COMMAND}" -E copy
		    "${PROJECT_SOURCE_DIR}/${MY_INSTALL_ICON}"
		    "$ENV{PLUGIN_BUILD_DIR}/config/Icons/${MY_INSTALL_ICON}"
	    COMMENT "Copying icon file to target")

	list(APPEND files_to_clean "$ENV{PLUGIN_BUILD_DIR}/config/Icons/${MY_INSTALL_ICON}")

    endif()

    if ( MY_INSTALL_HELP )
	add_custom_command(
	    TARGET ${library_name} POST_BUILD 
	    COMMAND "${CMAKE_COMMAND}" -E copy
		    "${PROJECT_SOURCE_DIR}/${MY_INSTALL_HELP}"
		    "$ENV{PLUGIN_BUILD_DIR}/help/nodes/${op_context}/${MY_INSTALL_HELP}"
	    COMMENT "Copying help file to target")

	list(APPEND files_to_clean "$ENV{PLUGIN_BUILD_DIR}/help/nodes/${op_context}/${MY_INSTALL_HELP}")

    endif()

    set_directory_properties(PROPERTIES ADDITIONAL_MAKE_CLEAN_FILES "${files_to_clean}")

endfunction ()

add_subdirectory( ROP/ROP_Script )
add_subdirectory( SOP/SOP_DopImpactPoints )
add_subdirectory( SOP/SOP_PointsFromVoxels )
add_subdirectory( SOP/SOP_PrimCentroid )
add_subdirectory( SOP/SOP_PrimGroupCentroid )

