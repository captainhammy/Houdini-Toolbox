This repository is for the Houdini Toolbox.

## Library Versions

This repository will generally closely follow the [VFX Platform](https://vfxplatform.com/) versions matching the most
recently released version of [Houdini](https://www.sidefx.com/docs/houdini/licenses/index.html).

### Legacy (Python 2.7) Support

Python 2.7 compatible code is still available in the **python2.7** branch.

---

## Installation

This project primarily uses [rez](https://github.com/AcademySoftwareFoundation/rez/) in order to build and package
itself, including compiled HDK plugins and Qt resources.

That said, if you want to use it without those, in order to use most of the features contained in this repo it is
necessary to add/modify certain entries in your environment:
- HOUDINI_PATH
- PYTHONPATH

### Using Houdini Packages

The easiest way to get this working is to use [Houdini Packages](https://www.sidefx.com/docs/houdini/ref/plugins.html).

Simply add the location of this repository to **$HOUDINI_PACKAGE_DIR** in order for Houdini to find the package definition and load it.
