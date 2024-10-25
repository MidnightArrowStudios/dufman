# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""Module containing functions to extract data from DSF file libraries."""

from pathlib import Path

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
