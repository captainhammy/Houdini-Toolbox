The compiled HDK plugins for **Houdini Toolbox** can be built using CMake and the custom wrapper **hcmake**

## Building The Plugins

To compile the plugins do the following from the root Houdini-Toolbox directory:
```
$> mkdir plugins/build
$> cd plugins/build
$> hcmake .. # This will invoke Cmake in a Houdini environment
$> make
```
### Individual plugins
To build an individual plugin you must do the first 3 steps above and then:
```
$> cd plugins/build
$> make {PLUGIN_NAME} # see 'make help' for details
```

### Cleaning
To clean the plugin files:
```
$> cd plugins/build
$> make clean
```

## Using Houdini Toolbox Makefile
The root Houdini-Toolbox directory also contains a Makefile with convenient targets for building the plugins:

```
# Build all the plugins
$> make build-plugins

# Initialize the Cmake generated files but don't build anything
$> make init-build

# Get a list of plugins
$> make list-targets

# Build a specific plugin
$> make build-plugin PLUGIN={PLUGIN NAME}

# Clean all the plugins
$> make clean-plugins

```
