cmake_minimum_required( VERSION 3.6 )

project( HoudiniToolboxPlugins )

# CMAKE_PREFIX_PATH must contain the path to the toolkit/cmake subdirectory of
# the Houdini installation. See the "Compiling with CMake" section of the HDK
# documentation for more details, which describes several options for
# specifying this path.
list( APPEND CMAKE_PREFIX_PATH "$ENV{HFS}/toolkit/cmake" )

# Locate Houdini's libraries and header files.
# Registers an imported library target named 'Houdini'.
find_package( Houdini REQUIRED )

# Add out plugin cmake directory to the module path.
list( APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake" )

include( HoudiniToolboxPlugins )

# Set useful paths for building Houdini items under.
set( HOUDINI_BUILD_PATH "$ENV{REZ_BUILD_PATH}/houdini" )
set( HOUDINI_DSO_BUILD_PATH "${HOUDINI_BUILD_PATH}/dso" )
set( HOUDINI_OPUI_BUILD_PATH "${HOUDINI_BUILD_PATH}/dso/opui" )

# Add project directories to build.
add_subdirectory( OPUI/OPUI_GenericImageBadge )
add_subdirectory( OPUI/OPUI_GenericTextBadge )
add_subdirectory( ROP/ROP_Script )
add_subdirectory( SOP/SOP_DopImpactPoints )
add_subdirectory( SOP/SOP_PointsFromVoxels )
add_subdirectory( SOP/SOP_PrimCentroid )
add_subdirectory( SOP/SOP_PrimGroupCentroid )

# Path for building Python items under.
set( HOUDINI_PYTHON_BUILD_PATH "$ENV{REZ_BUILD_PATH}/python" )

add_subdirectory( PY/PY_generic_image_badge )
add_subdirectory( PY/PY_generic_text_badge )

# Install the main Houdini plugin build directory to the package.
rez_install_dirs(
    ${HOUDINI_BUILD_PATH}
    DESTINATION .
)

# Install any built Python files to the package.
rez_install_dirs(
    ${HOUDINI_PYTHON_BUILD_PATH}
    DESTINATION .
)
