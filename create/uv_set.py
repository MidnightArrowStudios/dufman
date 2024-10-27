# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""Functions to instantiate a DsonUVSet object."""

from pathlib import Path

from ..exceptions import MissingRequiredProperty
from ..library import get_asset_data_from_library
from ..observers import _uv_set_struct_created
from ..structs.uv_set import DsonUVSet
from ..url import AssetURL, parse_url_string
from ..utilities import check_path

# ============================================================================ #
#                                                                              #
# ============================================================================ #

def create_uv_set_struct(dsf_filepath:Path, instance_data:dict=None) -> DsonUVSet:
    """Parses a DSON UV Set dictionary into a DsonUVSet wrapper struct."""

    # Ensure type safety
    dsf_filepath = check_path(dsf_filepath)

    # Load the DSON data from disk
    library_data:dict = get_asset_data_from_library(dsf_filepath, "uv_set_library")

    # Raise exceptions if required data is missing
    _validate(dsf_filepath, library_data, instance_data)

    # Instantiate the geometry to return
    struct:DsonUVSet = DsonUVSet()

    # Header information
    asset_url:AssetURL = parse_url_string(str(dsf_filepath))
    struct.dsf_file = asset_url.file_path
    struct.library_id = library_data["id"]
    struct.instance_id = instance_data["id"] if instance_data else None

    # Extract properties
    _name(struct, library_data, instance_data)
    _label(struct, library_data, instance_data)
    _source(struct, library_data, instance_data)
    _uv_set(struct, library_data, instance_data)

    # Fire observer
    _uv_set_struct_created(struct, library_data, instance_data)

    return struct

# ============================================================================ #
#                                                                              #
# ============================================================================ #

def _validate(dsf_filepath:str, library_data:dict, instance_data:dict) -> None:

    if library_data and not "id" in library_data:
        raise MissingRequiredProperty(dsf_filepath, "id")

    if library_data and not "vertex_count" in library_data:
        raise MissingRequiredProperty(dsf_filepath, "vertex_count")

    if library_data and not "uvs" in library_data:
        raise MissingRequiredProperty(dsf_filepath, "uvs")

    return


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def _label(struct:DsonUVSet, library_data:dict, instance_data:dict) -> None:

    if library_data and "label" in library_data:
        struct.label = library_data["label"]
    if instance_data and "label" in instance_data:
        struct.label = instance_data["label"]

    return

# ============================================================================ #

def _name(struct:DsonUVSet, library_data:dict, instance_data:dict) -> None:

    if library_data and "name" in library_data:
        struct.name = library_data["name"]
    if instance_data and "name" in instance_data:
        struct.name = instance_data["name"]

    return

# ============================================================================ #

def _source(struct:DsonUVSet, library_data:dict, instance_data:dict) -> None:

    if library_data and "source" in library_data:
        struct.source = library_data["source"]
    if instance_data and "source" in instance_data:
        struct.source = instance_data["source"]

    return

# ============================================================================ #

def _uv_set(struct:DsonUVSet, library_data:dict, instance_data:dict) -> None:

    # Expected vertices
    if library_data and "vertex_count" in library_data:
        struct.expected_vertices = library_data["vertex_count"]
    if instance_data and "vertex_count" in instance_data:
        struct.expected_vertices = instance_data["vertex_count"]

    # UV coordinates
    co_list:list[tuple[int, int]] = None
    if library_data and "uvs" in library_data:
        co_list = library_data["uvs"]["values"]
    if instance_data and "uvs" in instance_data:
        co_list = instance_data["uvs"]["values"]

    if co_list:
        struct.uv_coordinates = [ (co[0], co[1]) for co in co_list ]

    # Hotswap data
    hotswap_list:list = None
    if library_data and "polygon_vertex_indices" in library_data:
        hotswap_list = library_data["polygon_vertex_indices"]
    if instance_data and "polygon_vertex_indices" in instance_data:
        hotswap_list = instance_data["polygon_vertex_indices"]

    # The hotswap data is stored in a DSON file as a flat list, with the first
    #   index indicating the polygon. This is inefficient for lookup purposes,
    #   so we convert the data to a dictionary with its poly index as the key.
    struct.hotswap = {}
    for hotswap_entry in (hotswap_list if hotswap_list else []):
        polygon_index:int = hotswap_entry[0]
        if not polygon_index in struct.hotswap:
            struct.hotswap[polygon_index] = []
        struct.hotswap[polygon_index].append(list(hotswap_entry))

    return

# ============================================================================ #
