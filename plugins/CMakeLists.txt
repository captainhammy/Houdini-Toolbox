

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

    if (NOT help_context)
	set ( help_context "${op_context}" )

    endif()

    set ( help_name "${op_namespace}--${op_name}-${op_version}.txt" )
    set ( shelf_name "${op_context}_${op_name}.shelf" )

    string(TOUPPER ${op_context} icon_context)

    set ( tool_icon_name "${icon_context}_${op_namespace}-${op_name}-${op_version}" )
    set ( tool_icon_file "${tool_icon_name}.${MY_INSTALL_ICON}" )
    set ( help_icon_name "${op_namespace}--${op_name}-${op_version}.${MY_INSTALL_ICON}" )


    set( files_to_clean "")

    if ( MY_INSTALL_SHELF )
	add_custom_command(
	    TARGET ${library_name} POST_BUILD 
	    COMMAND "${CMAKE_COMMAND}" -E copy
		    "${PROJECT_SOURCE_DIR}/tool.shelf"
		    "$ENV{PLUGIN_BUILD_DIR}/toolbar/${shelf_name}"
	    COMMENT "Copying shelf file to target"
	)
	
	list(APPEND files_to_clean "$ENV{PLUGIN_BUILD_DIR}/toolbar/${shelf_name}")

    endif()

    if ( MY_INSTALL_HELP )

	add_custom_command(
	    TARGET ${library_name} POST_BUILD 
	    COMMAND "${CMAKE_COMMAND}" -E copy
		    "${PROJECT_SOURCE_DIR}/help.txt"
		    "$ENV{PLUGIN_BUILD_DIR}/help/nodes/${help_context}/${help_name}"
	    COMMENT "Copying help file to target"
	)

	list(APPEND files_to_clean "$ENV{PLUGIN_BUILD_DIR}/help/nodes/${help_context}/${help_name}")

    endif()

    if ( MY_INSTALL_ICON )
	add_custom_command(
	    TARGET ${library_name} POST_BUILD 
	    COMMAND "${CMAKE_COMMAND}" -E copy
		    "${PROJECT_SOURCE_DIR}/icon.${MY_INSTALL_ICON}"
		    "$ENV{PLUGIN_BUILD_DIR}/config/Icons/${tool_icon_file}"
	    COMMENT "Copying icon file for operator"
	)

	add_custom_command(
	    TARGET ${library_name} POST_BUILD 
	    COMMAND "${CMAKE_COMMAND}" -E copy
		    "${PROJECT_SOURCE_DIR}/icon.${MY_INSTALL_ICON}"
		    "$ENV{PLUGIN_BUILD_DIR}/help/nodes/${help_context}/${help_icon_name}"
	    COMMENT "Copying icon file for help card"
	)

	if ( MY_INSTALL_SHELF )
	    add_custom_command(
		TARGET ${library_name} POST_BUILD 
		COMMAND sed -i -e "s/\{ICON_INSTALL_NAME\}/${tool_icon_name}/g" "$ENV{PLUGIN_BUILD_DIR}/toolbar/${shelf_name}"
		COMMENT "Updating shelf icon path"
	    )

	endif()

	if ( MY_INSTALL_HELP )
	    add_custom_command(
		TARGET ${library_name} POST_BUILD 
		COMMAND sed -i -e "s/\{ICON_INSTALL_PATH\}/${help_icon_name}/g" "$ENV{PLUGIN_BUILD_DIR}/help/nodes/${help_context}/${help_name}"
	    )

	endif()


	list(APPEND files_to_clean "$ENV{PLUGIN_BUILD_DIR}/config/Icons/${tool_icon_file}")
	list(APPEND files_to_clean "$ENV{PLUGIN_BUILD_DIR}/help/nodes/${help_context}/${help_icon_name}")

    endif()

    set_directory_properties(PROPERTIES ADDITIONAL_MAKE_CLEAN_FILES "${files_to_clean}")

endfunction ()

add_subdirectory( OPUI/OPUI_GenericTextBadge )
add_subdirectory( ROP/ROP_Script )
add_subdirectory( SOP/SOP_DopImpactPoints )
add_subdirectory( SOP/SOP_PointsFromVoxels )
add_subdirectory( SOP/SOP_PrimCentroid )
add_subdirectory( SOP/SOP_PrimGroupCentroid )

