# Set some default operator naming options.
set( OP_NAMESPACE com.houdinitoolbox )

set( HT_LABEL_PREFIX "HT" )
set( HT_TAB_MENU_FOLDER "Houdini Toolbox")

function( get_help_context context )
    set( mymap_rop "out" )

    if( "${mymap_${context}}" STREQUAL "" )
        set( OP_HELP_CONTEXT "${context}" PARENT_SCOPE )

    else()
        set( OP_HELP_CONTEXT "${mymap_${context}}" PARENT_SCOPE )

    endif()

endfunction()

function( get_operator_table context )
    set( mymap_rop "driver")

    if( "${mymap_${context}}" STREQUAL "" )
        set( table "${context}" )

    else()
        set( table "${mymap_${context}}" )

    endif()

    string( SUBSTRING ${table} 0 1 FIRST_LETTER )
    string( TOUPPER ${FIRST_LETTER} FIRST_LETTER )
    string( REGEX REPLACE "^.(.*)" "${FIRST_LETTER}\\1" TITLE_TABLE "${table}" )

    set( OP_TABLE "${TITLE_TABLE}" PARENT_SCOPE )
    set( OP_TABLE_LOWER "${table}" PARENT_SCOPE )

endfunction()

function( conifgure_operator_files )
    cmake_parse_arguments( MY_INSTALL
        ""
        "SHELF;HELP;ICON"
        ""
        ${ARGN}
    )

	get_help_context( ${OP_CONTEXT} )
	get_operator_table( ${OP_CONTEXT} )

    set( HELP_NAME "${OP_NAMESPACE}--${OP_NAME}-${OP_VERSION}" )
    set( help_file_name "${OP_NAMESPACE}--${OP_NAME}-${OP_VERSION}.txt" )
    set( shelf_name "${OP_CONTEXT}_${OP_NAME}.shelf" )

    string(TOUPPER ${OP_CONTEXT} icon_context)

    set( NODE_TYPE_NAME "${OP_NAMESPACE}::${OP_NAME}::${OP_VERSION}" )
    set( NODE_TYPE_NAME ${NODE_TYPE_NAME} PARENT_SCOPE )
    set( NODE_TYPE_NAME_WITH_CATEGORY "${OP_NAMESPACE}::${OP_TABLE}/${OP_NAME}::${OP_VERSION}" )

    set( TOOL_NAME "${OP_NAMESPACE}::${OP_TABLE_LOWER}_${OP_NAME}::${OP_VERSION}" )
    set( SHELF_TOOL_ICON_NAME "${icon_context}_${OP_NAMESPACE}-${OP_NAME}-${OP_VERSION}" )
    set( TOOL_HELP_URL "operator:${NODE_TYPE_NAME_WITH_CATEGORY}" )

    if( MY_INSTALL_SHELF )
        configure_file( "${PROJECT_SOURCE_DIR}/tool.shelf" "${HOUDINI_BUILD_PATH}/toolbar/${shelf_name}" @ONLY )

    endif()

    # Copy the icon file to the correct name for both Houdini itself and the help server.  Sadly they can't use
    # the same one.
    if( MY_INSTALL_ICON )
        set( CUSTOM_HELP_ICON_NAME "${OP_NAMESPACE}--${OP_NAME}-${OP_VERSION}.${MY_INSTALL_ICON}" )

        configure_file( "${PROJECT_SOURCE_DIR}/icon.${MY_INSTALL_ICON}" "${HOUDINI_BUILD_PATH}/config/Icons/${SHELF_TOOL_ICON_NAME}.${MY_INSTALL_ICON}" COPYONLY )
        configure_file( "${PROJECT_SOURCE_DIR}/icon.${MY_INSTALL_ICON}" "${HOUDINI_BUILD_PATH}/help/nodes/${OP_HELP_CONTEXT}/${CUSTOM_HELP_ICON_NAME}" COPYONLY )

    endif()

    if( MY_INSTALL_HELP )
        configure_file( "${PROJECT_SOURCE_DIR}/help.txt" "${HOUDINI_BUILD_PATH}/help/nodes/${OP_HELP_CONTEXT}/${help_file_name}" @ONLY )

	endif()

endfunction()
