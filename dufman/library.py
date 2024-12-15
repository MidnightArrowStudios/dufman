# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""Module containing functions to extract data from DSF file libraries."""

from pathlib import Path
from typing import Any

from .enums import NodeType
from .file import check_path, handle_dsf_file
from .exceptions import IncorrectArgument, LibraryNotFound
from .url import AssetAddress, AssetURL, create_url_string, parse_url_string


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def get_all_asset_urls_from_library(asset_path:Path, library_name:str) -> list[str]:
    """Returns a list of all IDs from a designated DSF file's library."""

    # Ensure type safety
    asset_path = check_path(asset_path)

    # Convert URL from string to object
    asset_address:AssetAddress = AssetAddress.create_from_url(asset_path)

    # Ensure we have something to open
    if not asset_address.filepath:
        raise Exception(f"Asset URL \"{ asset_path }\" does not have a valid filepath.")

    # Open the DSF file
    dsf_file:dict = handle_dsf_file(asset_address.filepath)

    # Ensure we have the required library type
    if not library_name in dsf_file:
        raise LibraryNotFound(f"DSF file \"{ asset_path }\" does not contain { library_name }.")

    # Return value
    result:list[str] = []

    # Loop through library and compile list of quoted asset URLs for each one
    for entry in dsf_file[library_name]:
        fp:str = asset_address.filepath
        ai:str = entry["id"]
        full_url:str = AssetAddress.create_from_components(filepath=fp, asset_id=ai).get_valid_asset_url()
        result.append(full_url)

    return result


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def get_asset_json_from_library(asset_path:Path, library_name:str, duf_file:dict=None) -> dict:
    """Returns a dictionary object from the designated DSF file library."""

    asset_path = check_path(asset_path)

    asset_url:AssetURL = parse_url_string(str(asset_path))

    # ======================================================================== #
    # Assets can either be in a DSF file on disk, or the DUF file that is
    #   being parsed. The following code switches between the two based on
    #   the asset's DSON-formatted URL.
    #
    # DSF File:
    #   "/data/path/to/asset.dsf#asset_id"
    # DUF File:
    #   "#asset_id"
    # ======================================================================== #

    file_with_asset:dict = None

    if asset_url.filepath:
        file_with_asset = handle_dsf_file(asset_url.filepath)
    elif duf_file:
        file_with_asset = duf_file
    else:
        message:str = "Could not get asset data. URL was invalid or DUF argument was None."
        raise IncorrectArgument(message)

    if not library_name in file_with_asset:
        raise LibraryNotFound(f"DSF file \"{ asset_path }\" does not contain { library_name }.")

    library_json:dict = None

    for asset in file_with_asset[library_name]:
        if asset["id"] == asset_url.asset_id:
            library_json = asset
            break

    return library_json


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def get_node_hierarchy_urls_from_library(asset_path:Path) -> list[str]:
    """Returns a list of IDs for every bone which is part of a figure's armature."""

    # Ensure type safety
    asset_path = check_path(asset_path)

    # Encapsulate URL into object
    asset_url:AssetURL = parse_url_string(str(asset_path))

    if not asset_url.filepath:
        # TODO: Exception?
        return

    dsf_file:dict = handle_dsf_file(asset_url.filepath)

    if not "node_library" in dsf_file:
        raise LibraryNotFound(f"DSF file \"{ asset_path }\" does not contain node_library.")

    # List of all nodes in DSF file
    nodes:list[dict] = dsf_file["node_library"]

    # Return value (IDs of figure's child bones)
    result:list[str] = []

    # Get all direct children of figure node
    all_children:list[dict] = [ *_get_child_node_json(nodes, asset_url.asset_id) ]

    # Test each child to see if it's a bone. If not, discard it. If so, add
    #   its own children to the list of nodes to be parsed.
    while all_children:
        potential_bone:dict = all_children.pop(0)
        if NodeType(potential_bone["type"]) == NodeType.BONE:
            bone_id:str = potential_bone["id"]
            full_url:str = create_url_string(filepath=asset_url.filepath, asset_id=bone_id)
            result.append(full_url)
            all_children.extend( _get_child_node_json(nodes, bone_id) )

    return result


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def get_single_property_from_library(dsf_filepath:Path, property_path:list[str]) -> Any:
    """Gets a single piece of data from a DSF file based on its path."""

    invalid:Exception = Exception("Property could not be retrieved. Ensure property_path is valid.")

    dsf_filepath = check_path(dsf_filepath)

    tokens:list[str] = list(property_path)
    dsf_pointer:Any = handle_dsf_file(dsf_filepath)

    # The property path is split into components representing the hierarchy
    #   of the asset's property.
    # [ "geometry_library", 0, "polygon_material_groups", "values, 4 ]
    #   will return the fifth surface's name in the first geometry asset.
    while tokens:

        token = tokens.pop(0)

        # Current level is DSON object (i.e. dictionary).
        if isinstance(dsf_pointer, dict):

            if not token in dsf_pointer:
                raise invalid

            dsf_pointer = dsf_pointer[token]
            continue

        # Current level is list.
        if isinstance(dsf_pointer, list):

            # Need this to control branching. If we put a continue statement
            #   into the following for loop, then it will only continue that
            #   loop, instead of the loop we want ("while tokens:").
            was_found:bool = False

            # First, see if the token matches an ID.
            for entry in dsf_pointer:
                if isinstance(entry, dict) and "id" in entry and entry["id"] == token:
                    dsf_pointer = entry
                    was_found = True
                    break

            # Restart top-level loop if ID was found.
            if was_found:
                continue

            # If it doesn't match an ID, see if we can use it as an index.
            index:int = None

            try:
                index = int(token)
            except ValueError as ve:
                raise invalid from ve

            if not 0 <= index < len(dsf_pointer):
                raise IndexError

            dsf_pointer = dsf_pointer[index]
            continue

        # Neither a dictionary nor a list, so property_path is not valid.
        raise invalid

    return dsf_pointer


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def _get_child_node_json(node_library:list[dict], parent_id:str) -> list[dict]:
    """Returns a list of dictionary objects for a node's immediate children."""

    result:list[dict] = []

    for node in node_library:

        if not "parent" in node:
            continue

        # Parent URLs are stored with a pound sign. This strips them off.
        parent_url:AssetURL = parse_url_string(node["parent"])

        # TODO: Can a node have a parent in a different file? Doubtful, but it
        #   might be an edge case.
        if not parent_url.filepath and parent_url.asset_id == parent_id:
            result.append(node)

    return result
