# ============================================================================ #
"""Utility module for working with asset URLs in DSON files."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import ParseResult, quote, unquote, urlparse, urlunparse

from ..exceptions import IncorrectArgument

# ============================================================================ #
#                                                                              #
# ============================================================================ #

@dataclass
class AssetURL:
    """Dataclass which wraps all the elements of a DSON URL."""

    node_path               : str       = None
    file_path               : str       = None
    asset_id                : str       = None
    property_path           : str       = None

    # Same as property_path, but the path has been pre-split.
    property_tokens         : list[str] = None

# ============================================================================ #

def parse_url_string(url_string:str) -> AssetURL:
    """Accepts a DSON-formatted URL and returns a wrapper object."""

    # Ensure type safety.
    if not isinstance(url_string, str):
        message:str = f"Could not parse URL. Argument \"{repr(url_string)}\" is not a string."
        raise IncorrectArgument(message)

    # urllib sucks at handling Scheme. Doesn't preserve capitalization, makes
    #   it a path if it has an underscore. So if there is a Scheme, handle it
    #   ourselves.
    scheme:str = None
    if url_string.find(":") >= 0:
        split_on_colon:tuple = url_string.partition(":")
        scheme = split_on_colon[0]
        url_string = split_on_colon[2]

    result:ParseResult = urlparse(unquote(url_string))

    asset_url:AssetURL = AssetURL()
    asset_url.node_path = scheme
    asset_url.file_path = result.path

    # DSON puts the query after the fragment, for some reason. This doesn't
    #   play nice with urllib.
    if result.fragment.find("?") == -1:
        asset_url.asset_id = result.fragment
    else:
        tokens:list[str] = result.fragment.split("?")
        asset_url.asset_id = tokens[0]
        asset_url.property_path = tokens[1]
        asset_url.property_tokens = tokens[1].split("/")

    return asset_url


# ============================================================================ #

def create_url_string(node_path:str="", dsf_path:str="", asset_id:str="",
                        property_path:Any=None) -> str:
    """Takes the components of a DSON-formatted URL and returns a complete URL string."""

    def check_for_errors(argument:str):
        if argument and not isinstance(argument, str):
            message:str = f"Could not create URL. Argument \"{repr(argument)}\" is not a string."
            raise IncorrectArgument(message)
        return

    check_for_errors(node_path)
    check_for_errors(dsf_path)
    check_for_errors(asset_id)

    if property_path and isinstance(property_path, list):
        if all(isinstance(item, str) for item in property_path):
            property_path = "/".join(property_path)
        else:
            message:str = "Could not create URL. property_path must be string or list of strings."
            raise IncorrectArgument(message)

    check_for_errors(property_path)

    scheme:str = quote(node_path)
    path:str = quote(dsf_path)
    fragment:str = None

    if property_path:
        fragment = f"{ quote(asset_id) }?{ quote(property_path) }"
    else:
        fragment = quote(asset_id)

    return urlunparse((scheme, "", path, "", "", fragment))
