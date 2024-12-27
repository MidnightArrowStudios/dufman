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
from urllib.parse import ParseResult, quote, unquote, urlparse

from dufman.exceptions import IncorrectArgument


# ============================================================================ #
#                                                                              #
# ============================================================================ #

@dataclass
class AssetAddress:
    """Dataclass which wraps all the components of a DSON URL."""

    node_name:str = None
    filepath:str = None
    asset_id:str = None
    property_path:str = None


    # ======================================================================== #
    # FORMAT METHODS                                                           #
    # ======================================================================== #

    @staticmethod
    def format_filepath(filepath:str, *, is_quoted:bool=True, has_leading_slash:bool=True) -> str:
        """Ensure filepath string is formatted according to DSON standards.
        
        The resulting filepath will have forward slashes and be quoted using
        urllib, ensuring it matches the format that DSON files use to access
        other files. It will also have a forward slash appended to the front,
        if there isn't one already.
        """

        if not filepath:
            return None

        # Ensure filepath has forward slashes and is quoted
        result:str = quote(Path(unquote(str(filepath))).as_posix(), safe="/\\")

        # Ensure filepath starts with forward slash
        if not has_leading_slash and result.startswith("/"):
            result = result.lstrip("/")
        elif has_leading_slash and not result.startswith("/"):
            result = "/" + result

        return result if is_quoted else unquote(result)


    # ------------------------------------------------------------------------ #

    @staticmethod
    def format_url_as_string(*, node_name:str=None, filepath:str=None, asset_id:str=None, property_path:str=None) -> str:
        """Construct and format a DSON URL string from its component parts."""

        result:str = ""

        # For the following documentation, we will use the following example:
        #   Genesis8Female:/data/DAZ 3D/Genesis 8/Female/Genesis8Female#Genesis8Female?translation/x
        #   |             ||                                          ||             ||            |
        #      node_name                    filepath                      asset_id    property_path

        # Node name
        if node_name:
            result += f"{node_name}:"

        # Filepath
        if filepath:
            filepath = AssetAddress.format_filepath(filepath)
            result += f"{filepath}"

        # Asset ID
        if asset_id:
            result += f"#{asset_id}"

        # Property path
        if property_path:
            result += f"?{property_path}"

        return result


    # ======================================================================== #
    # STRING GENERATION METHODS                                                #
    # ======================================================================== #

    @staticmethod
    def generate_asset_url(url_string:str, *, filepath:str=None) -> str:
        address:AssetAddress = AssetAddress.from_url(url_string)
        if not address.filepath and filepath:
            address.filepath = filepath
        return address.get_url_to_asset()


    # ------------------------------------------------------------------------ #

    @staticmethod
    def generate_property_url(url_string:str, *, filepath:str=None, property_path:str=None) -> str:
        address:AssetAddress = AssetAddress.from_url(url_string)
        if not address.filepath and filepath:
            address.filepath = filepath
        if not address.property_path and property_path:
            address.property_path = property_path
        return address.get_url_to_property()


    # ======================================================================== #
    # FACTORY METHODS                                                          #
    # ======================================================================== #

    @classmethod
    def from_components(cls:type, *, node_name:str=None, filepath:str=None, asset_id:str=None, property_path:str=None) -> AssetAddress:
        """Factory method to create an AssetAddress from a DSON-formatted URL's parts."""

        filepath = cls.format_filepath(filepath)

        return cls(node_name, filepath, asset_id, property_path)


    # ------------------------------------------------------------------------ #

    @classmethod
    def from_url(cls:type, url_string:Any) -> AssetAddress:
        """Factory method to create an AssetAddress from a DSON-formatted URL."""

        # Force-convert Path object to string, using as_posix() to ensure it
        #   has forward slashes.
        if isinstance(url_string, Path):
            url_string = url_string.as_posix()

        # Ensure type safety.
        if not isinstance(url_string, str):
            message:str = f"Could not create AssetAddress. Argument \"{url_string}\" is a {type(url_string)}, not a string or a Path object."
            raise IncorrectArgument(message)

        # urllib sucks at handling Scheme. Doesn't preserve capitalization and
        #   makes it a path if it has an underscore. If there is a Scheme, we
        #   need to handle it ourselves.
        scheme:str = None
        if url_string.find(":") >= 0:
            split_on_colon:tuple = url_string.partition(":")
            scheme = split_on_colon[0]
            url_string = split_on_colon[2]

        # Break URL into components and store them inside object.
        result:ParseResult = urlparse(unquote(url_string))

        node_name:str = scheme
        filepath:str = cls.format_filepath(result.path)
        asset_id:str = None
        property_path:str = None

        # DSON puts the query after the fragment, for some reason. urllib
        #   doesn't like this.
        if result.fragment.find("?") == -1:
            asset_id = result.fragment
            property_path = None
        else:
            split_on_qmark:tuple = result.fragment.partition("?")
            asset_id = split_on_qmark[0]
            property_path = Path(split_on_qmark[2]).as_posix()

        # Convert empty strings to None
        node_name = node_name if node_name else None
        asset_id = asset_id if asset_id else None
        property_path = property_path if property_path else None

        return cls(node_name, filepath, asset_id, property_path)


    # ======================================================================== #
    # URL CREATION METHODS                                                     #
    # ======================================================================== #

    def get_url_to_asset(self:AssetAddress, fallback:str = None) -> str:
        """Returns a URL suitable for retrieving data from a DSF file."""

        if not self.asset_id:
            return None

        fallback = self.format_filepath(fallback)

        if self.filepath:
            return self.format_url_as_string(filepath=self.filepath, asset_id=self.asset_id)
        if fallback:
            return self.format_url_as_string(filepath=fallback, asset_id=self.asset_id)

        return None


    # ------------------------------------------------------------------------ #

    def get_url_to_property(self:AssetAddress) -> str:
        return self.format_url_as_string(filepath=self.filepath, asset_id=self.asset_id, property_path=self.property_path)


    # ======================================================================== #
    # QUERY METHODS                                                            #
    # ======================================================================== #

    def get_property_tokens(self:AssetAddress) -> list[str]:
        """Break the property path into a list of tokens.

        :returns: The path to the property
        :rtype: List of strings
        """
        return self.property_path.split("/") if self.property_path else []


# ============================================================================ #

# def parse_url_string(url_string:str) -> AssetURL:
#     """Accepts a DSON-formatted URL and returns a wrapper object."""

#     # Ensure type safety.
#     if not isinstance(url_string, str):
#         message:str = f"Could not parse URL. Argument \"{repr(url_string)}\" is not a string."
#         raise IncorrectArgument(message)

#     # urllib sucks at handling Scheme. Doesn't preserve capitalization, makes
#     #   it a path if it has an underscore. So if there is a Scheme, handle it
#     #   ourselves.
#     scheme:str = None
#     if url_string.find(":") >= 0:
#         split_on_colon:tuple = url_string.partition(":")
#         scheme = split_on_colon[0]
#         url_string = split_on_colon[2]

#     result:ParseResult = urlparse(unquote(url_string))

#     asset_url:AssetURL = AssetURL()
#     asset_url.node_name = scheme
#     asset_url.filepath = result.path

#     # DSON puts the query after the fragment, for some reason. This doesn't
#     #   play nice with urllib.
#     if result.fragment.find("?") == -1:
#         asset_url.asset_id = result.fragment
#     else:
#         tokens:list[str] = result.fragment.split("?")
#         asset_url.asset_id = tokens[0]
#         asset_url.property_path = tokens[1]
#         asset_url.property_tokens = tokens[1].split("/")

#     return asset_url


# ============================================================================ #

# def create_url_string(node_name:str="", filepath:str="", asset_id:str="",
#                         property_path:Any=None) -> str:
#     """Takes the components of a DSON-formatted URL and returns a complete URL string."""

#     # Ensures slashes are correct, per DSON format
#     filepath = Path(filepath).as_posix()

#     def check_for_errors(argument:str):
#         if argument and not isinstance(argument, str):
#             message:str = f"Could not create URL. Argument \"{repr(argument)}\" is not a string."
#             raise IncorrectArgument(message)
#         return

#     check_for_errors(node_name)
#     check_for_errors(filepath)
#     check_for_errors(asset_id)

#     if property_path and isinstance(property_path, list):
#         if all(isinstance(item, str) for item in property_path):
#             property_path = "/".join(property_path)
#         else:
#             message:str = "Could not create URL. property_path must be string or list of strings."
#             raise IncorrectArgument(message)

#     check_for_errors(property_path)

#     # Characters which won't be encoded by quote().
#     safe_characters:str = '/\\'

#     scheme:str = quote(node_name, safe=safe_characters)
#     path:str = quote(filepath, safe=safe_characters)
#     fragment:str = None

#     # Ensure path is formatted how DSON expects it to be.
#     if not path.startswith("/"):
#         path = f"/{path}"

#     # DSON puts the query after the fragment, so we need to swap them if it is
#     #   present.
#     if property_path:
#         fragment = f"{ quote(asset_id, safe=safe_characters) }?{ quote(property_path, safe=safe_characters) }"
#     else:
#         fragment = quote(asset_id, safe=safe_characters)

#     return urlunparse((scheme, "", path, "", "", fragment))


# ============================================================================ #
