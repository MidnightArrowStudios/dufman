# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""Module containing functions to extract data from DSF file libraries."""

from pathlib import Path

from ..enums import NodeType
from ..file import handle_dsf_file
from ..exceptions import IncorrectArgument, LibraryNotFound
from ..url import AssetURL, parse_url_string
from ..utilities import check_path

# ============================================================================ #
#                                                                              #
# ============================================================================ #

def get_asset_data_from_library(asset_path:Path, library_name:str, duf_file:dict=None) -> dict:
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

    if asset_url.file_path:
        file_with_asset = handle_dsf_file(asset_url.file_path)
    elif duf_file:
        file_with_asset = duf_file
    else:
        message:str = "Could not get asset data. URL was invalid or DUF argument was None."
        raise IncorrectArgument(message)

    if not library_name in file_with_asset:
        raise LibraryNotFound(f"DSF file \"{ asset_path }\" does not contain { library_name }.")

    library_data:dict = None

    for asset in file_with_asset[library_name]:
        if asset["id"] == asset_url.asset_id:
            library_data = asset
            break

    return library_data


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def get_all_asset_ids_from_library(asset_path:Path, library_name:str) -> list[str]:
    """Returns a list of all IDs from a designated DSF file's library."""

    asset_path = check_path(asset_path)

    asset_url:AssetURL = parse_url_string(str(asset_path))

    if not asset_url.file_path:
        # TODO: Exception?
        return

    dsf_file:dict = handle_dsf_file(asset_url.file_path)

    if not library_name in dsf_file:
        raise LibraryNotFound(f"DSF file \"{ asset_path }\" does not contain { library_name }.")

    result:list[str] = []

    for entry in dsf_file[library_name]:
        result.append(entry["id"])

    return result


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def get_bone_hierarchy_ids_from_library(asset_path:Path, figure_name:str) -> list[str]:
    """Returns a list of IDs for every bone which is part of a figure's armature."""

    # Ensure type safety
    asset_path = check_path(asset_path)

    # Encapsulate URL into object
    asset_url:AssetURL = parse_url_string(str(asset_path))

    if not asset_url.file_path:
        # TODO: Exception?
        return

    dsf_file:dict = handle_dsf_file(asset_url.file_path)

    if not "node_library" in dsf_file:
        raise LibraryNotFound(f"DSF file \"{ asset_path }\" does not contain node_library.")

    # List of all nodes in DSF file
    nodes:list[dict] = dsf_file["node_library"]

    # Return value (IDs of figure's child bones)
    result:list[str] = []

    # Get all direct children of figure node
    all_children:list[dict] = [ *_get_child_node_data(nodes, figure_name) ]

    # Test each child to see if it's a bone. If not, discard it. If so, add
    #   its own children to the list of nodes to be parsed.
    while all_children:
        potential_bone:dict = all_children.pop(0)
        if NodeType(potential_bone["type"]) == NodeType.BONE:
            bone_id:str = potential_bone["id"]
            result.append(bone_id)
            all_children.extend( _get_child_node_data(nodes, bone_id) )

    return result


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def _get_child_node_data(node_library:list[dict], parent_id:str) -> list[dict]:

    result:list[dict] = []

    for node in node_library:

        if not "parent" in node:
            continue
        
        # Parent URLs are stored with a pound sign. This strips them off.
        parent_url:AssetURL = parse_url_string(node["parent"])

        # TODO: Can a node have a parent in a different file? Doubtful, but it
        #   might be an edge case.
        if not parent_url.file_path and parent_url.asset_id == parent_id:
            result.append(node)

    return result
