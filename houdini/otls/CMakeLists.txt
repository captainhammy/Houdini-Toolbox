# Handle installing digital asset files either by collapsing with hotl or
# copying as is.

# The path to collapse/copy digital assets to.
set( OTL_BUILD_DIR "$ENV{REZ_BUILD_PATH}/otls" )

file( MAKE_DIRECTORY ${OTL_BUILD_DIR} )

# Find all digital asset files.
file( GLOB otl_files "*.otl" "*.hda" )

foreach( otl_file ${otl_files} )
    # If the asset is a directory then we want to collapse it via hotl.
    if( IS_DIRECTORY ${otl_file} )
	# We want to collapse to a file of the same name as the directory so
	# extract the name to use as the target file name.
	get_filename_component( file_name ${otl_file} NAME )

	execute_process(
	    COMMAND hotl -l ${otl_file} "${OTL_BUILD_DIR}/${file_name}"
	    COMMAND_ECHO STDOUT
	)

    # Otherwise we should just copy it to the build dir for installation.
    else()
	configure_file( ${otl_file} ${OTL_BUILD_DIR} COPYONLY )

    endif()

endforeach()

# Install the collapsed or copied files.
rez_install_dirs( ${OTL_BUILD_DIR} DESTINATION houdini )
