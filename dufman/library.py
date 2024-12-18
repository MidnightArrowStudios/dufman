# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""Module containing functions to extract data from DSF file libraries."""

from pathlib import Path
from typing import Any

from .enums import LibraryType, NodeType
from .file import check_path, handle_dsf_file
from .exceptions import IncorrectArgument, LibraryNotFound
from .url import AssetAddress



# ============================================================================ #
#                                                                              #
# ============================================================================ #

def find_library_containing_asset_id(asset_path:Path) -> LibraryType:

    # Ensure type safety
    asset_path = check_path(asset_path)

    # Convert URL from string to object
    asset_address:AssetAddress = AssetAddress.create_from_url(asset_path)

    # Ensure we have something to open
    if not asset_address.filepath:
        raise Exception(f"Asset URL \"{ asset_path }\" does not have a valid filepath.")

    # Open the DSF file
    dsf_file:dict = handle_dsf_file(asset_address.filepath)

    # geometry_library
    for geometry_json in dsf_file.get(LibraryType.GEOMETRY.value, []):
        if geometry_json["id"] == asset_address.asset_id:
            return LibraryType.GEOMETRY

    # image_library
    for image_json in dsf_file.get(LibraryType.IMAGE.value, []):
        if image_json["id"] == asset_address.asset_id:
            return LibraryType.IMAGE

    # material_library
    for material_json in dsf_file.get(LibraryType.MATERIAL.value, []):
        if material_json["id"] == asset_address.asset_id:
            return LibraryType.MATERIAL

    # modifier_library
    for modifier_json in dsf_file.get(LibraryType.MODIFIER.value, []):
        if modifier_json["id"] == asset_address.asset_id:
            return LibraryType.MODIFIER

    # node_library
    for node_json in dsf_file.get(LibraryType.NODE.value, []):
        if node_json["id"] == asset_address.asset_id:
            return LibraryType.NODE

    # uv_set_library
    for uv_set_json in dsf_file.get(LibraryType.UV_SET.value, []):
        if uv_set_json["id"] == asset_address.asset_id:
            return LibraryType.UV_SET

    return None


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

    # Ensure the library actually exists inside the DSON file
    if not library_name in dsf_file:
        raise LibraryNotFound(f"DSF file \"{ asset_path }\" does not contain { library_name }.")

    # Return value
    result:list[str] = []

    # Loop through library and compile list of quoted asset URLs for each one
    for entry in dsf_file[library_name]:
        fp:str = asset_address.filepath
        ai:str = entry["id"]
        full_url:str = AssetAddress.create_from_components(filepath=fp, asset_id=ai).get_url_to_asset()
        result.append(full_url)

    return result


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def get_asset_json_from_library(asset_path:Path, library_type:LibraryType, *, duf_file:dict=None) -> dict:
    """Returns a dictionary object from the designated DSF file library."""

    # Ensure type safety
    asset_path = check_path(asset_path)

    # Convert URL from string to object
    asset_address:AssetAddress = AssetAddress.create_from_url(asset_path)

    # ======================================================================== #
    # Assets can either be in the file we are currently parsing, in which case
    #   they will have no filepath (i.e. "#asset_id"), or they can be in
    #   another file on disk (i.e. "/data/path/to/asset.dsf#asset_id"). The
    #   following code switches between the two based on the URL.

    file_with_asset:dict = None

    # "/data/path/to/asset.dsf#asset_id"
    if asset_address.filepath:
        file_with_asset = handle_dsf_file(asset_address.filepath)

    # "#asset_id"
    elif duf_file:
        file_with_asset = duf_file

    # No URL, failure
    else:
        message:str = "Could not get asset data. URL was invalid or DUF argument was None."
        raise IncorrectArgument(message)
    # ======================================================================== #

    # Ensure the DSON file contains a library of the requested type
    if not library_type.value in file_with_asset:
        raise LibraryNotFound(f"DSF file \"{ asset_path }\" does not contain { library_type.value }.")

    # Return value
    result:dict = None

    # Loop through the designated library and search for the requested ID
    for asset in file_with_asset[library_type.value]:
        if asset["id"] == asset_address.asset_id:
            result = asset
            break

    return result


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def get_node_hierarchy_urls_from_library(asset_path:Path) -> list[str]:
    """Returns a list of IDs for every bone which is part of a figure's armature."""

    # Ensure type safety
    asset_path = check_path(asset_path)

    # Convert URL from string to object
    asset_address:AssetAddress = AssetAddress.create_from_url(asset_path)

    # Ensure we have something to open
    if not asset_address.filepath:
        raise Exception(f"Asset URL \"{ asset_path }\" does not have a valid filepath.")

    # Open the DSF file
    dsf_file:dict = handle_dsf_file(asset_address.filepath)

    # Ensure the DSF file has nodes in it
    if not "node_library" in dsf_file:
        raise LibraryNotFound(f"DSF file \"{ asset_path }\" does not contain node_library.")

    # Get list of all nodes contained in file for parsing
    all_nodes:list[dict] = dsf_file["node_library"]

    # Return value
    result:list[str] = []

    # Loop through nodes, get all direct children
    dsf_url:str = asset_address.filepath
    sought_id:str = asset_address.asset_id
    working_list:list[dict] = [ *_get_child_node_json(all_nodes, sought_id) ]

    # As long as working list has something in it, test it to see if it's a
    #   bone. If so, add it to the working list. If not, discard it.
    while working_list:
        potential_child:dict = working_list.pop(0)
        if NodeType(potential_child["type"]) == NodeType.BONE:
            bone_id:str = potential_child["id"]
            bone_address:AssetAddress = AssetAddress.create_from_components(filepath=dsf_url, asset_id=bone_id)
            result.append(bone_address.get_url_to_asset())
            working_list.extend( _get_child_node_json(all_nodes, bone_id) )

    return result


# ============================================================================ #
#                                                                              #
# ============================================================================ #

# TODO: Break the file loading and the file parsing into separate functions,
#   so we can parse already-opened files.
def get_single_property_from_library(dsf_filepath:Path, property_path:list[str]) -> Any:
    """Gets a single piece of data from a DSF file based on its path."""

    invalid:Exception = Exception("Property could not be retrieved. Ensure property_path is valid.")

    dsf_filepath = check_path(dsf_filepath)

    tokens:list[str] = list(property_path)
    dsf_pointer:Any = handle_dsf_file(dsf_filepath)

    # The property path is split into components representing the hierarchy
    #   of the asset's property.
    # [ "geometry_library", 0, "polygon_material_groups", "values", 4 ]
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

    # Return value
    result:list[dict] = []

    # Loop through all nodes in file searching for children
    for node in node_library:

        if not "parent" in node:
            continue

        # Parent URLs are stored with a pound sign. This will strip them off.
        parent_address:AssetAddress = AssetAddress.create_from_url(node["parent"])

        # TODO: Can a node have a parent in a different file? It's doubtful,
        #   but it might be an edge case worth handling.

        if parent_address.filepath:
            node_id:str = node["id"]
            raise Exception(f"Node \"{node_id}\" has parent with filepath")

        if parent_address.asset_id == parent_id:
            result.append(node)

    return result
