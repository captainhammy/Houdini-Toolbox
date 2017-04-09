The houdini_wrapper script is used to execute Houdini applications.  It
is intended that various Houdini app names be symlinked to the wrapper so that
the wrapper assumes execution control of them.  When the wrapper is run it uses
ht.houdini.wrapper to setup an envirionment for the applications to run under.
This wrapper allows you to use Houdini without having to execute to a Houdini
install directory and 'source houdini_setup'.  The -version argument will display
available versions and allow you to run specific versions.

The install_houdini_wrapper script is used to automatically generate symlinks
for Houdini application names to houdini_wrapper.  It allows you to easily
create and remove them.

Example:

./install_houdini_wrapper -directory /usr/bin/ -wrapper /home/gthompson/Houdini-Toolbox/bin/houdini_wrapper -install

