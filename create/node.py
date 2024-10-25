# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""Functions to instantiate a DsonNode object."""

from pathlib import Path

from ..datatypes import DsonChannelVector
from ..enums import NodeType, RotationOrder
from ..exceptions import MissingRequiredProperty
from ..file import extract_single_property
from ..library import get_asset_data_from_library
from ..observers import _node_struct_created
from ..structs.node import DsonNode
from ..url import AssetURL, parse_url_string
from ..utilities import check_path

# ============================================================================ #
#                                                                              #
# ============================================================================ #

def create_node_struct(dsf_filepath:Path, instance_data:dict=None) -> DsonNode:
    """Parses a DSON node dictionary into a DsonNode wrapper struct."""

    # Ensure type safety
    dsf_filepath:Path = check_path(dsf_filepath)

    # Load the DSON dictionary from disk
    library_data:dict = get_asset_data_from_library(dsf_filepath, "node_library")

    # ======================================================================== #

    if not "id" in library_data:
        raise MissingRequiredProperty(str(dsf_filepath), "id")

    if not "name" in library_data:
        raise MissingRequiredProperty(str(dsf_filepath), "name")

    if not "label" in library_data:
        raise MissingRequiredProperty(str(dsf_filepath), "label")

    # ======================================================================== #

    struct:DsonNode = DsonNode()

    asset_url:AssetURL = parse_url_string(str(dsf_filepath))
    struct.dsf_file = asset_url.file_path
    struct.library_id = library_data["id"]
    struct.instance_id = instance_data["id"] if instance_data else None

    # ======================================================================== #

    # Name
    struct.name = library_data["name"]
    if instance_data and "name" in instance_data:
        struct.name = instance_data["name"]

    # Label
    struct.label = library_data["label"]
    if instance_data and "label" in instance_data:
        struct.name = instance_data["label"]

    # Source
    if "source" in library_data:
        struct.source = library_data["source"]
    if instance_data and "source" in instance_data:
        struct.source = instance_data["source"]

    # Node type
    if "type" in library_data:
        struct.node_type = NodeType(library_data["type"])
    if instance_data and "type" in instance_data:
        struct.node_type = NodeType(instance_data["type"])

    # Content type
    if "presentation" in library_data:
        struct.content_type = library_data["presentation"]["type"]
    if instance_data and "presentation" in instance_data:
        struct.content_type = instance_data["presentation"]["type"]

    # Parent
    if "parent" in library_data:
        struct.library_parent = library_data["parent"]
    if instance_data and "parent" in instance_data:
        struct.instance_parent = instance_data["parent"]

    # Inherit scale
    # All nodes inherit scale by default, except bones with bone parents.
    default_inherits_scale:bool = True
    if struct.node_type == NodeType.BONE and struct.library_parent:
        parent_url:AssetURL = parse_url_string(struct.library_parent)
        parent_path:list[str] = [ "node_library", parent_url.asset_id, "type" ]
        parent_type:str = None

        if parent_url.file_path:
            parent_type = extract_single_property(parent_url.file_path, parent_path)
        else:
            parent_type = extract_single_property(str(dsf_filepath), parent_path)

        if parent_type and parent_type == "bone":
            default_inherits_scale = False

    struct.inherits_scale = default_inherits_scale
    if "inherits_scale" in library_data:
        struct.inherits_scale = library_data["inherits_scale"]
    if instance_data and "inherits_scale" in instance_data:
        struct.inherits_scale = instance_data["inherits_scale"]

    # RotationOrder
    if "rotation_order" in library_data:
        struct.rotation_order = RotationOrder(library_data["rotation_order"])
    if instance_data and "rotation_order" in instance_data:
        struct.rotation_order = RotationOrder(instance_data["rotation_order"])

    # Center point
    struct.center_point = DsonChannelVector.create_from_dson_data("center_point",
        library_data, instance_data, default=(0.0, 0.0, 0.0))

    # End point
    struct.end_point = DsonChannelVector.create_from_dson_data("end_point",
        library_data, instance_data, default=(0.0, 0.0, 0.0))

    # Translation
    struct.translation = DsonChannelVector.create_from_dson_data("translation",
        library_data, instance_data, default=(0.0, 0.0, 0.0))

    # Orientation
    struct.orientation = DsonChannelVector.create_from_dson_data("orientation",
        library_data, instance_data, default=(0.0, 0.0, 0.0))

    # Rotation
    struct.rotation = DsonChannelVector.create_from_dson_data("rotation",
        library_data, instance_data, default=(0.0, 0.0, 0.0))

    # Scale
    struct.scale = DsonChannelVector.create_from_dson_data("scale",
        library_data, instance_data, default=(1.0, 1.0, 1.0))

    # General scale
    if "general_scale" in library_data:
        struct.general_scale = library_data["general_scale"]
    if instance_data and "general_scale" in instance_data:
        struct.general_scale = instance_data["general_scale"]

    # ======================================================================== #

    _node_struct_created(struct, library_data, instance_data)

    return struct
