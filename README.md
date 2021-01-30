This repository is for the Houdini Toolbox.


## Python 3

This repository is now entirely Python 3 based and is no longer compatible with Python 2.7 versions of Houdini. 
The old Python 2.7 compatible code is available in the **python2.7** branch.

---

## Installation

In order to use most of the features contained in this repo it is necessary to add/modify certain entries in your environment:
- HOUDINI_PATH
- PYTHONPATH

The following instructions assume **TOOLBOXDIR** is the location where you have downloaded this repository: ($HOME/Houdini-Toolbox, D:\Houdini-Toolbox, etc)

### Using Houdini Packages

The easiest way to get this working is to use [Houdini Packages](https://www.sidefx.com/docs/houdini/ref/plugins.html).

Simply add {TOOLBOXDIR} to **$HOUDINI_PACKAGE_DIR** in order for Houdini to find the package definition and load it.

### Manual Setup

You'll need to add the relevant folders within {TOOLBOXDIR} to the previously mentioned paths:

- HOUDINI_PATH needs to include '{TOOLBOXDIR}/houdini'
- PYTHONPATH needs to include '{TOOLBOXDIR}/python'

NOTE: When adding to the HOUDINI_PATH you MUST be sure to also include $HH ($HFS/houdini) in the path or Houdini will not work correctly.  The best thing to do is to insert Houdini's default path value '&' in the path at the end.

See http://www.sidefx.com/docs/houdini/basics/config_env for more info about configuring Houdini paths and variables.

On a unix based systems where you are launching Houdini from a terminal it is as simple as setting the variables in the shell before you launch.  For example in bash:
```
export HOUDINI_PATH="${HOME}/Houdini-Toolbox/houdini:&"
export PYTHONPATH="${HOME}/Houdini-Toolbox/python:${PYTHONPATH}"
```
