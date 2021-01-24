# Using Custom Python Filtering

The following is based upon the basic Python filtering (sometimes call PyFilter) provided by Mantra as detailed here: http://www.sidefx.com/docs/houdini/render/python.html

## Components

In order to get filtering working using code contained in Houdini Toolbox you'll need to make sure a few things are set up correctly.

### Filter Script

The filter script (**houdini/pyfilter/ht-pyfilter.py**) is executed by Mantra using the **-P** argument and is responsible for initalizing the manager and executing any filter operations.

```
mantra -f test.ifd -P /path/to/script.py ip

```
If you are intending to pass any arguments to this script you will need to enclose the path and all args in quotes

```
mantra -f test.ifd -P "/path/to/script.py ip arg1 arg2"

```
This script is really treated more like a module than a script, however it is loaded twice on startup so don't be alarmed if you have output which will show up twice.

### Operations Loading File

Because everything is happening at Mantra run time there is no great way in order to automatically initialize the required operations.  To get around this the system looks for any **pyfilter/operations.json** files located throughout the **$HOUDINI_PATH**.  This .json file defines a list of modules to load and classes in those modules to register as operations.

```json
{
    "operations":
    [
        ["ht.pyfilter.operations.deepimage", "SetDeepImage"],
        ["ht.pyfilter.operations.ipoverrides", "IpOverrides"]
    ]
}
```

## Operations

The manager class/script will run PyFilterOperation objects that can perform arbitrary actions and data manipulation.  By including the module and class name in the operations files these will be loaded automatically.

These operation classes can implement functions which match the filter* functions described in the Mantra documentation above.  If an object has such a named function when that stage is called in the main script the manager will execute that function if the operation should run.

Operations can run all the time or can explicitly look for particular flags to be passed.  *PyFilterOperation* classes can provide a static method **register_parser_args** which can be used to add arguments to a supplied *argparse.ArgumentParser* object which will automatically be used to parse the command args with any added arguments.  The resulting parsed data is passed back to the operation to extract any args that might have been passed and set up the operation to run.

To conveniently build these args they also can provide a static *build_arg_string* method which will take some arguments and return a string containing the necessary command line args to execute those options.

For example, to build the arg string to include to set the primary image path you can do the following:

```python
>>> from ht.pyfilter.operations.primaryimage import SetPrimaryImage
>>> arg_string = SetPrimaryImage.build_arg_string(primary_image_path="/path/to/image.exr")
>>> print(arg_string)
'--primary-image-path=/path/to/image.exr'
```
