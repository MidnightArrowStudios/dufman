# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""Utility module for working with DSON asset URLs."""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import ParseResult, quote, unquote, urlparse, urlunparse

from .exceptions import IncorrectArgument


# ============================================================================ #
#                                                                              #
# ============================================================================ #

@dataclass
class AssetURL:
    """Dataclass which wraps all the elements of a DSON URL."""

    node_name               : str       = None
    filepath                : str       = None
    asset_id                : str       = None
    property_path           : str       = None

    # Same as property_path, but the path has been tokenized.
    property_tokens         : list[str] = None
    

    def get_posix_filepath(self:AssetURL) -> str:
        return Path(filepath).as_posix()


    def get_valid_url_string(self:AssetURL, fallback_url:str=None) -> str:
        if self.filepath:
            return create_url_string(filepath=self.filepath, asset_id=self.asset_id)
        elif fallback_url:
            return create_url_string(filepath=fallback_url, asset_id=self.asset_id)
        else:
            return None


    def has_filepath(self:AssetURL) -> bool:
        result:bool = False
        if self.filepath:
            result = True
        return result


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
    asset_url.node_name = scheme
    asset_url.filepath = result.path

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

def create_url_string(node_name:str="", filepath:str="", asset_id:str="",
                        property_path:Any=None) -> str:
    """Takes the components of a DSON-formatted URL and returns a complete URL string."""

    # Ensures slashes are correct, per DSON format
    filepath = Path(filepath).as_posix()

    def check_for_errors(argument:str):
        if argument and not isinstance(argument, str):
            message:str = f"Could not create URL. Argument \"{repr(argument)}\" is not a string."
            raise IncorrectArgument(message)
        return

    check_for_errors(node_name)
    check_for_errors(filepath)
    check_for_errors(asset_id)

    if property_path and isinstance(property_path, list):
        if all(isinstance(item, str) for item in property_path):
            property_path = "/".join(property_path)
        else:
            message:str = "Could not create URL. property_path must be string or list of strings."
            raise IncorrectArgument(message)

    check_for_errors(property_path)

    # Characters which won't be encoded by quote().
    safe_characters:str = '/\\'

    scheme:str = quote(node_name, safe=safe_characters)
    path:str = quote(filepath, safe=safe_characters)
    fragment:str = None

    # Ensure path is formatted how DSON expects it to be.
    if not path.startswith("/"):
        path = f"/{path}"

    # DSON puts the query after the fragment, so we need to swap them if it is
    #   present.
    if property_path:
        fragment = f"{ quote(asset_id, safe=safe_characters) }?{ quote(property_path, safe=safe_characters) }"
    else:
        fragment = quote(asset_id, safe=safe_characters)

    return urlunparse((scheme, "", path, "", "", fragment))

# ============================================================================ #
