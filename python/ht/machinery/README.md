# Houdini Wrapper 

## Houdini Package Configuration 

The Houdini wrapper and environment can be configured by way of the
**$HOME/houdini_package_config.json** file.  A default implementation exists in the
package folder but you can copy the file to your $HOME folder and set user
defined settings there.

This file has two components:

### System Settings

These are used to tell the wrapper where installed builds are, where to look
for files to install and where they will be installed.  It can also provide
information about where you might have compiled plugins.

### Environment settings

These are used to defined various env variables and paths that should be set
when running.  Variables will be set first so that any paths you wish to set
can include them if necessary. The test_* versions are for when running using
the --test-path flag for testing purposes.


## Build Data

The **build_data.json** file  is used to define information about builds and
machine types.  It is how the wrapper and supporting code can determine what
files you can install or use.


## Build Downloading

The wrapper can automatically handle downloading and installing builds from
SideFX.  It is possible to download a specific build number
(17.5.123) or to try to get "today's" build for a specific major.minor (17.5)
combination.  Use the **--dl-install** wrapper flag.

**NOTE**: Automatic installation is only supported on Linux.

To download and install a specific build:

`wrapper --dl-install 17.5.123`

To download and install the latest available build:

`wrapper --dl-install 17.5`

### Configuration

Automatic downloading is handled via the **SideFX Web API**.  In order to use this
feature you'll need to create credentials and have them available to the tooling.

Please see https://www.sidefx.com/docs/api/index.html for instructions on how to
create credentials to download.

Once you have your credentials you just need to place them in **$HOME/sesi_app_info.json**
and the tooling will use that to connect and
download available builds.

The following is the simple template for the sesi_app_info.json file:

```
{
    "access_token_url": "https://www.sidefx.com/oauth2/application_token",
    "client_id": "your OAuth application ID",
    "client_secret": "your OAuth application secret"
    "endpoint_url": "https://www.sidefx.com/api/"
}
```

When automatically downloading builds they will be downloaded to the first
location in the 'archive_locations' list.
