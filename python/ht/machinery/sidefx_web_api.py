"""Utilities to download builds from sidefx.com."""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard Library
import base64
import datetime
import hashlib
import html.parser
import json
import os
import time
from typing import List, Optional, Tuple

# Third Party
import humanfriendly
import requests
from humanfriendly.tables import format_pretty_table
from termcolor import colored, cprint
from tqdm import tqdm

# =============================================================================
# GLOBALS
# =============================================================================

_RELEASE_TYPE_MAP = {"devel": ("Daily", "white"), "gold": ("Production", "blue")}

_STATUS_MAP = {"good": "white", "bad": "red"}

_VERSION_PLATFORM_MAP = {"19.0": "linux_x86_64_gcc9.3"}

# =============================================================================
# CLASSES
# =============================================================================


class _Service:
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
        self,
        product: str,
        version: Optional[str] = None,
        platform: Optional[str] = None,
        only_production: bool = False,
    ) -> List[dict]:
        """Get a list of available builds matching the criteria.

        :param product: The name of the product to download.
        :param version: The major.minor version to download.
        :param platform: The platform to download for.
        :param only_production: Only consider production builds.
        :return: A list of found builds.

        """
        releases_list = self.download.get_daily_builds_list(
            product, version=version, platform=platform, only_production=only_production
        )

        releases_list = [
            release
            for release in releases_list
            if release["platform"]
            == _VERSION_PLATFORM_MAP.get(release["version"], release["platform"])
        ]

        # Sort the release list by integer version/build since it will be sorted by string
        def sorter(data):
            """Function to build key generation for sorting builds."""
            return [int(val) for val in data["version"].split(".")], int(data["build"])

        releases_list.sort(reverse=True, key=sorter)

        return releases_list

    def get_daily_build_download(
        self, product: str, version: str, build: str, platform: str
    ) -> dict:
        """Get the release information for a specific build.

        :param product: The name of the product to download.
        :param version: The major.minor version to download.
        :param build: The build number.
        :param platform: The platform to download for.
        :return: The release information.

        """
        release_info = self.download.get_daily_build_download(
            product, version, build, platform
        )

        return release_info


class _APIFunction:
    """Class representing a Web API function.

    :param function_name: The name of the function.
    :param service: The API connection service.

    """

    def __init__(self, function_name: str, service: _Service):
        self.function_name = function_name
        self.service = service

    def __getattr__(self, attr_name):
        # This isn't actually an API function, but a family of them.  Append
        # the requested function name to our name.
        return _APIFunction(f"{self.function_name}.{attr_name}", self.service)

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

    def __init__(self, http_code: int, message: str):
        super().__init__(message)
        self.http_code = http_code


class AuthorizationError(Exception):
    """Raised from the client if the server generated an error while generating
    an access token.

    """

    def __init__(self, http_code: int, message: str):
        super().__init__(message)
        self.http_code = http_code


# =============================================================================
# NON-PUBLIC FUNCTIONS
# =============================================================================


def _get_access_token_and_expiry_time(
    access_token_url: str, client_id: str, client_secret_key: str
) -> Tuple[str, float]:
    """Given an API client (id and secret key) that is allowed to make API
    calls, return an access token that can be used to make calls.

    :param access_token_url: The access token url.
    :param client_id: The client ID.
    :param client_secret_key: The client secret key.
    :return: An access token and token expiration time.

    """
    basic_value = base64.b64encode(f"{client_id}:{client_secret_key}".encode()).decode(
        "utf-8"
    )

    response = requests.post(
        access_token_url,
        headers={"Authorization": f"Basic {basic_value}"},
    )

    if response.status_code != 200:
        raise AuthorizationError(
            response.status_code,
            f"{response.status_code}: {_extract_traceback_from_response(response)}",
        )

    response_json = response.json()
    access_token_expiry_time = time.time() - 2 + response_json["expires_in"]

    return response_json["access_token"], access_token_expiry_time


def _call_api_with_access_token(
    endpoint_url: str, access_token: str, function_name: str, args, kwargs
) -> dict:
    """Call into the API using an access token.

    :param endpoint_url: The service endpoint url.
    :param access_token: The access token.
    :param function_name: The name of the function being called.
    :param args: The function args.
    :param kwargs: The keyword function args.
    :return: The response data.

    """

    response = requests.post(
        endpoint_url,
        headers={"Authorization": "Bearer " + access_token},
        data=dict(json=json.dumps([function_name, args, kwargs])),
    )

    if response.status_code == 200:
        return response.json()

    raise APIError(response.status_code, _extract_traceback_from_response(response))


def _extract_traceback_from_response(response: requests.Response) -> str:
    """Helper function to extract a traceback from the web server response if
    an API call generated a server-side exception.

    :param response: A web server response.
    :return: Traceback information from the response.

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

    return str(html.unescape(traceback))


def _get_build_to_download(
    version: str,
    build: Optional[str] = None,
    product: str = "houdini",
    platform: str = "linux",
    only_production: bool = False,
    allow_bad: bool = False,
) -> Optional[dict]:
    """Determine the build to actually download.

    :param version: The major.minor version to download.
    :param build: Optional build number.
    :param product: The name of the product to download.
    :param platform: The platform to download for.
    :param only_production: Only consider production builds.
    :param allow_bad: Allow downloading builds marked as 'bad'.
    :return: The target build information.

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

    # Get the actual release information for this build.
    release_info = service.get_daily_build_download(
        product, version, release["build"], platform
    )

    return release_info


def _get_sidefx_app_credentials() -> dict:
    """Load the SideFX API credentials.

    :return: The loaded api credentials.

    """
    with open(
        os.path.expandvars("$HOME/sesi_app_info.json"), encoding="utf-8"
    ) as handle:
        data = json.load(handle)

    return data


def _verify_file_checksum(file_path: str, hash_value: str):
    """Verify the md5 hash of the downloaded file.

    :param file_path: The path to the downloaded file.
    :param hash_value: The server provided hash value.
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
    download_path: str,
    version: str,
    build: Optional[str] = None,
    product: str = "houdini",
    platform: str = "linux",
    only_production: bool = False,
    allow_bad: bool = False,
) -> Optional[str]:
    """Download a build to target path.

    :param download_path: The path to download the build to.
    :param version: The major.minor version to download.
    :param build: Optional build number.
    :param product: The name of the product to download.
    :param platform: The platform to download for.
    :param only_production: Only consider production builds.
    :param allow_bad: Allow downloading builds marked as 'bad'.
    :return: The path to the downloaded file.

    """
    release_info = _get_build_to_download(
        version, build, product, platform, only_production, allow_bad
    )

    if release_info is None:
        build_str = version

        if build is not None:
            build_str = f"{build_str}.{build}"

        print(f"No such build {build_str}")

        return None

    file_size = release_info["size"]

    number_of_chunks = 10
    chunk_size = file_size // number_of_chunks

    if not os.path.isdir(download_path):
        os.makedirs(download_path)

    target_path = os.path.join(download_path, release_info["filename"])

    request = requests.get(release_info["download_url"], stream=True)

    if request.status_code == 200:
        print(f"Downloading to {target_path}")
        print(f"\tFile size: {humanfriendly.format_size(file_size, binary=True)}")

        print(
            f"\tDownload chunk size: {humanfriendly.format_size(chunk_size, binary=True)}\n"
        )

        with tqdm(
            desc="Downloading build",
            total=file_size,
            unit="MB",
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            with open(target_path, "wb") as handle:
                for chunk in request.iter_content(chunk_size=chunk_size):
                    progress_bar.update(chunk_size)
                    handle.write(chunk)

        print("\n\nDownload complete")

    else:
        raise Exception("Error downloading file!")

    # Verify the file checksum is matching
    _verify_file_checksum(target_path, release_info["hash"])

    return target_path


def list_builds(
    version: Optional[str] = None,
    product: str = "houdini",
    platform: str = "linux",
    only_production: bool = False,
):
    """Display a table of builds available to download.

    Dates which care colored green indicate they are today's build.

    :param version: The major.minor version to download.
    :param product: The name of the product to download.
    :param platform: The platform to download for.
    :param only_production: Only consider production builds.
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

        date_string = str(build_date)

        if build_date == today:
            date_string = colored(date_string, "green")

        row = [
            colored(
                f"{release['version']}.{release['build']}",
                _STATUS_MAP[release["status"]],
            ),
            date_string,
            colored(release_type, release_color),
        ]

        rows.append(row)

    cprint(format_pretty_table(rows, headers))
