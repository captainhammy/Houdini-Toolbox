This repository is for the Houdini Toolbox.

## Installation

In order to use most of the features contained in this repo it is necessary to add/modify certain entries in your environment:
- HOUDINI_PATH
- PYTHONPATH

Each entry must include the path to the relevant folders within the Houdini-Toolbox repo, where TOOLBOXDIR is the location you have placed the repo (eg. $HOME/Houdini-Toolbox, D:\Houdini-Toolbox, etc):
- HOUDINI_PATH needs to include '{TOOLBOXDIR}/houdini'
- PYTHONPATH needs to include '{TOOLBOXDIR}/python'

NOTE: When adding to the HOUDINI_PATH you MUST be sure to also include $HH ($HFS/houdini) in the path or Houdini will not work correctly.  The best thing to do is to insert Houdini's default path value '&' in the path at the end.

See http://www.sidefx.com/docs/houdini/basics/config_env for more info about configuring Houdini paths and variables.

On a unix based systems where you are launching Houdini from a terminal it is as simple as setting the variables in the shell before you launch.  For example in tcsh:
```
setenv HOUDINI_PATH "${HOME}/Houdini-Toolbox/houdini:&"
setenv PYTHONPATH "${HOME}/Houdini-Toolbox/python:${PYTHONPATH}"
```

### Using houdini.env
You can also use the `houdini.env` file to setup these variables.  This is often easier for Windows.

NOTE: Unix and Windows will use different path split characters so ensure you are using the correct one for your platform:
- **:** for unix: `/some/path:&`
- **;** for Windows: `c:\some\path;&`

```
Unix:
HOUDINI_PATH = "${HOME}/Houdini-Toolbox/houdini:&"
PYTHONPATH = "${HOME}/Houdini-Toolbox/python"

Windows:
HOUDINI_PATH = "D:\Houdini-Toolbox\houdini;&"
PYTHONPATH = "D:\Houdini-Toolbox\python"
```
