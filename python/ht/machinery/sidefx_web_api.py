"""Utilities to download builds from sidefx.com."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library Imports
from __future__ import division
import base64
import datetime
import hashlib
import json
import os
import sys
import time

# Third Party Imports
import humanfriendly
from humanfriendly.tables import format_pretty_table
import requests
import six
from termcolor import colored, cprint

# =============================================================================
# GLOBALS
# =============================================================================

_RELEASE_TYPE_MAP = {"devel": ("Daily", "white"), "gold": ("Production", "blue")}

_STATUS_MAP = {"good": "white", "bad": "red"}


# =============================================================================
# CLASSES
# =============================================================================


class _Service(object):
    """Class representing a connection to the SideFX Web API."""

    def __init__(self):
        # Get the API credentials.
        data = _get_sidefx_app_credentials()

        # Get the access token information based on those credentials.
        access_token, access_token_expiry_time = _get_access_token_and_expiry_time(
            data["access_token_url"], data["client_id"], data["client_secret"]
        )

        self.access_token = access_token
        self.access_token_expiry_time = access_token_expiry_time
        self.endpoint_url = data["endpoint_url"]

    def __getattr__(self, attr_name):
        return _APIFunction(attr_name, self)

    def get_available_builds(
        self, product, version=None, platform=None, only_production=None
    ):
        """Get a list of available builds matching the criteria.

        :param product: The name of the product to download.
        :type product: str
        :param version: The major.minor version to download.
        :type version: str
        :param platform: The platform to download for.
        :type platform: str
        :param only_production: Only consider production builds.
        :type only_production: bool
        :return: A list of found builds.
        :rtype: list(dict)

        """
        releases_list = self.download.get_daily_builds_list(
            product, version=version, platform=platform, only_production=only_production
        )

        # Sort the release list by integer version/build since it will be sorted by string
        def sorter(data):  # pylint: disable=missing-docstring
            return [int(val) for val in data["version"].split(".")], int(data["build"])

        releases_list.sort(reverse=True, key=sorter)

        return releases_list

    def get_daily_build_download(self, product, version, build, platform):
        """Get the release information for a specific build.

        :param product: The name of the product to download.
        :type product: str
        :param version: The major.minor version to download.
        :type version: str
        :param build: The build number.
        :type build: str
        :param platform: The platform to download for.
        :type platform: str
        :return: The release information.
        :rtype: dict

        """
        release_info = self.download.get_daily_build_download(
            product, version, build, platform
        )

        return release_info


class _APIFunction(object):
    """Class representing a Web API function.

    :param function_name: The name of the function.
    :type function_name: str
    :param service: The API connection service.
    :type service: _Service

    """

    def __init__(self, function_name, service):
        self.function_name = function_name
        self.service = service

    def __getattr__(self, attr_name):
        # This isn't actually an API function, but a family of them.  Append
        # the requested function name to our name.
        return _APIFunction("{}.{}".format(self.function_name, attr_name), self.service)

    def __call__(self, *args, **kwargs):
        return _call_api_with_access_token(
            self.service.endpoint_url,
            self.service.access_token,
            self.function_name,
            args,
            kwargs,
        )


# =============================================================================
# EXCEPTIONS
# =============================================================================


class APIError(Exception):
    """Raised from the client if the server generated an error while calling
    into the API.

    """

    def __init__(self, http_code, message):
        super(APIError, self).__init__(message)
        self.http_code = http_code


class AuthorizationError(Exception):
    """Raised from the client if the server generated an error while generating
    an access token.

    """

    def __init__(self, http_code, message):
        super(AuthorizationError, self).__init__(message)
        self.http_code = http_code


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _get_access_token_and_expiry_time(access_token_url, client_id, client_secret_key):
    """Given an API client (id and secret key) that is allowed to make API
    calls, return an access token that can be used to make calls.

    :param access_token_url: The access token url.
    :type access_token_url: str
    :param client_id: The client ID.
    :type client_id: str
    :param client_secret_key: The client secret key.
    :type client_secret_key: str
    :return: An access token and token expiration time.
    :rtype: tuple(str, float)

    """
    response = requests.post(
        access_token_url,
        headers={
            "Authorization": u"Basic {}".format(
                base64.b64encode(
                    "{}:{}".format(client_id, client_secret_key).encode()
                ).decode("utf-8")
            )
        },
    )

    if response.status_code != 200:
        raise AuthorizationError(
            response.status_code,
            "{}: {}".format(
                response.status_code, _extract_traceback_from_response(response)
            ),
        )

    response_json = response.json()
    access_token_expiry_time = time.time() - 2 + response_json["expires_in"]

    return response_json["access_token"], access_token_expiry_time


def _call_api_with_access_token(
    endpoint_url, access_token, function_name, args, kwargs
):
    """Call into the API using an access token.

    :param endpoint_url: The service endpoint url.
    :type endpoint_url: str
    :param access_token: The access token.
    :type access_token: str
    :param function_name: The name of the function being called.
    :type function_name: str
    :param args: The function args.
    :type args: list(str)
    :param kwargs: The keyword function args.
    :type kwargs: dict
    :return: The response data.
    :rtype: dict

    """

    response = requests.post(
        endpoint_url,
        headers={"Authorization": "Bearer " + access_token},
        data=dict(json=json.dumps([function_name, args, kwargs])),
    )

    if response.status_code == 200:
        return response.json()

    raise APIError(response.status_code, _extract_traceback_from_response(response))


def _extract_traceback_from_response(response):
    """Helper function to extract a traceback from the web server response if
    an API call generated a server-side exception.

    :param response: A web server response.
    :type response: requests.Response
    :return: Traceback information from the response.
    :rtype: str

    """
    error_message = response.text

    if response.status_code != 500:
        return error_message

    traceback = ""

    for line in error_message.split("\n"):
        if traceback and line == "</textarea>":
            break

        if line == "Traceback:" or traceback:
            traceback += line + "\n"

    if not traceback:
        traceback = error_message

    return str(six.moves.html_parser.HTMLParser().unescape(traceback))


def _get_build_to_download(
    version,
    build=None,
    product="houdini",
    platform="linux",
    only_production=False,
    allow_bad=False,
):
    """Determine the build to actually download.

    :param version: The major.minor version to download.
    :type version: str
    :param build: Optional build number.
    :type build: str
    :param product: The name of the product to download.
    :type product: str
    :param platform: The platform to download for.
    :type platform: str
    :param only_production: Only consider production builds.
    :type only_production: bool
    :param allow_bad: Allow downloading builds marked as 'bad'.
    :type allow_bad: bool
    :return: The target build information.
    :rtype: dict or None

    """
    # Initialize the API service.
    service = _Service()

    # Get a list of builds which match the criteria.
    releases_list = service.get_available_builds(
        product, version=version, platform=platform, only_production=only_production
    )

    # A filtered list of builds.
    filtered = []

    # Filter the builds based on additional settings.
    for release in releases_list:
        # Ignore bad builds when not allowing for them.
        if release["status"] == "bad" and not allow_bad:
            continue

        # If we explicitly passed along a build number then we only want builds
        # which match that number.
        if build is not None:
            if build != release["build"]:
                continue

        # The build passed, so add it to the list.
        filtered.append(release)

    if not filtered:
        return None

    # We choose the first build from the remaining builds.  Since the list is
    # supposed to be returned from the API with the latest builds first this should be
    # the most recent build which matched.
    release = filtered[0]
    build = release["build"]

    # Get the actual release information for this build.
    release_info = service.get_daily_build_download(product, version, build, platform)

    return release_info


def _get_sidefx_app_credentials():
    """Load the SideFX API credentials.

    :return: The loaded api credentials.
    :rtype: dict

    """
    with open(os.path.expandvars("$HOME/sesi_app_info.json")) as handle:
        data = json.load(handle)

    return data


def _verify_file_checksum(file_path, hash_value):
    """Verify the md5 hash of the downloaded file.

    :param file_path: The path to the downloaded file.
    :type file_path: str
    :param hash_value: The server provided hash value.
    :type hash_value: str
    :return:

    """
    # Verify the file checksum is matching
    file_hash = hashlib.md5()

    with open(file_path, "rb") as handle:
        for chunk in iter(lambda: handle.read(4096), b""):
            file_hash.update(chunk)

    if file_hash.hexdigest() != hash_value:
        raise Exception("Checksum does not match!")


# =============================================================================
# FUNCTIONS
# =============================================================================


def download_build(  # pylint: disable=too-many-locals
    download_path,
    version,
    build=None,
    product="houdini",
    platform="linux",
    only_production=False,
    allow_bad=False,
):
    """Download a build to target path.

    :param download_path: The path to download the build to.
    :type download_path: str
    :param version: The major.minor version to download.
    :type version: str
    :param build: Optional build number.
    :type build: str
    :param product: The name of the product to download.
    :type product: str
    :param platform: The platform to download for.
    :type platform: str
    :param only_production: Only consider production builds.
    :type only_production: bool
    :param allow_bad: Allow downloading builds marked as 'bad'.
    :type allow_bad: bool
    :return: The path to the downloaded file.
    :rtype: str

    """
    release_info = _get_build_to_download(
        version, build, product, platform, only_production, allow_bad
    )

    if release_info is None:
        build_str = version

        if build is not None:
            build_str = "{}.{}".format(build_str, build)

        six.print_("No such build {}".format(build_str))

        return None

    file_size = release_info["size"]
    chunk_size = file_size // 10

    if not os.path.isdir(download_path):
        os.makedirs(download_path)

    target_path = os.path.join(download_path, release_info["filename"])

    request = requests.get(release_info["download_url"], stream=True)

    if request.status_code == 200:
        six.print_("Downloading to {}".format(target_path))
        six.print_(
            "\tFile size: {}".format(humanfriendly.format_size(file_size, binary=True))
        )
        six.print_(
            "\tDownload chunk size: {}\n".format(
                humanfriendly.format_size(chunk_size, binary=True)
            )
        )

        total = 0

        with open(target_path, "wb") as handle:
            sys.stdout.write("0% complete")
            sys.stdout.flush()

            for chunk in request.iter_content(chunk_size=chunk_size):
                total += chunk_size

                sys.stdout.write(
                    "\r{}% complete".format(min(int((total / file_size) * 100), 100))
                )
                sys.stdout.flush()

                handle.write(chunk)

        six.print_("\n\nDownload complete")

    else:
        raise Exception("Error downloading file!")

    # Verify the file checksum is matching
    _verify_file_checksum(target_path, release_info["hash"])

    return target_path


def list_builds(
    version=None, product="houdini", platform="linux", only_production=False
):
    """Display a table of builds available to download.

    Dates which care colored green indicate they are today's build.

    :param version: The major.minor version to download.
    :type version: str
    :param product: The name of the product to download.
    :type product: str
    :param platform: The platform to download for.
    :type platform: str
    :param only_production: Only consider production builds.
    :type only_production: bool
    :return:

    """
    service = _Service()

    # Get a list of builds which match the criteria.
    releases_list = service.get_available_builds(
        product, version=version, platform=platform, only_production=only_production
    )

    headers = ["Build", "Date", "Type"]

    # A filtered list of builds.
    rows = []

    today = datetime.datetime.now().date()

    # Filter the builds based on additional settings.
    for release in releases_list:
        release_type, release_color = _RELEASE_TYPE_MAP[release["release"]]

        build_date = datetime.datetime.strptime(release["date"], "%Y/%m/%d").date()

        if build_date == today:
            build_date = colored(build_date, "green")

        row = [
            colored(
                "{}.{}".format(release["version"], release["build"]),
                _STATUS_MAP[release["status"]],
            ),
            build_date,
            colored(release_type, release_color),
        ]

        rows.append(row)

    cprint(format_pretty_table(rows, headers))
