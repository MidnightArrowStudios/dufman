# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self

from dufman.enums import LibraryType, NodeType, RotationOrder
from dufman.file import check_path

from dufman.library import (
    get_asset_json_from_library,
    get_single_property_from_library,
)
from dufman.observers import _node_struct_created
from dufman.url import AssetAddress

from dufman.structs.channel import DsonChannelFloat, DsonChannelVector
from dufman.structs.formula import DsonFormula
from dufman.structs.presentation import DsonPresentation

from dufman.types import DsonColor


# ============================================================================ #
#                                                                              #
# ============================================================================ #

@dataclass
class DsonNode:

    dsf_file                        : Path                  = None
    library_id                      : str                   = None

    name                            : str                   = None
    label                           : str                   = None
    source                          : str                   = ""

    node_type                       : NodeType              = NodeType.NODE
    parent                          : str                   = None

    center_point                    : DsonChannelVector     = None
    end_point                       : DsonChannelVector     = None
    translation                     : DsonChannelVector     = None

    rotation_order                  : RotationOrder         = RotationOrder.XYZ
    orientation                     : DsonChannelVector     = None
    rotation                        : DsonChannelVector     = None

    inherits_scale                  : bool = True
    scale                           : DsonChannelVector     = None
    general_scale                   : DsonChannelFloat      = None

    presentation                    : DsonPresentation      = None
    formulas                        : list[DsonFormula]     = None


    # ======================================================================== #
    # CAMERA                                                                   #
    # ======================================================================== #

    @dataclass
    class CameraPerspective:
        clipping_z_near                     : float                 = None
        clipping_z_far                      : float                 = None
        magnification_y                     : float                 = None

    @dataclass
    class CameraOrthographic:
        clipping_z_near                     : float                 = None
        clipping_z_far                      : float                 = None
        field_of_view_y                     : float                 = 45.0
        focal_length                        : float                 = None
        depth_of_field                      : bool                  = False
        focal_distance                      : float                 = None
        f_stop                              : float                 = None

    perspective                         : CameraPerspective     = None
    orthographic                        : CameraOrthographic    = None


    # ======================================================================== #
    # LIGHT                                                                    #
    # ======================================================================== #

    @dataclass
    class LightPoint:
        pass

    @dataclass
    class LightDirectional:
        pass

    @dataclass
    class LightSpot:
        pass

    light_on:bool = True
    light_color:DsonColor = None
    light_point:LightPoint = None
    light_directional:LightDirectional = None
    light_spot:LightSpot = None


    # ======================================================================== #
    # CAMERA                                                                   #
    # ======================================================================== #

    @staticmethod
    def load(dsf_filepath:Path, node_json:dict=None) -> Self:

        # Ensure type safety
        dsf_filepath = check_path(dsf_filepath)

        # Load DSON data from disk if it wasn't passed in.
        if not node_json:
            node_json = get_asset_json_from_library(dsf_filepath, LibraryType.NODE)

        struct:DsonNode = DsonNode()
        struct.dsf_file = dsf_filepath

        # ID
        if "id" in node_json:
            struct.library_id = node_json["id"]
        else:
            raise ValueError("Missing required property \"ID\"")

        # Name
        if "name" in node_json:
            struct.name = node_json["name"]
        else:
            raise ValueError("Missing required property \"name\"")

        # Type
        if "type" in node_json:
            struct.node_type = NodeType(node_json["type"])

        # Label
        if "label" in node_json:
            struct.label = node_json["label"]
        else:
            raise ValueError("Missing required property \"label\"")

        # Source
        if "source" in node_json:
            struct.source = node_json["source"]

        # Parent
        if "parent" in node_json:
            struct.parent = node_json["parent"]

        # Rotation order
        if "rotation_order" in node_json:
            struct.rotation_order = RotationOrder(node_json["rotation_order"])

        # Inherits scale
        if "inherits_scale" in node_json:
            struct.inherits_scale = node_json["inherits_scale"]
        else:
            struct.inherits_scale = _inherits_scale_default(struct)

        # Center point
        center_point_json:dict = None
        if "center_point" in node_json:
            center_point_json = node_json["center_point"]
        struct.center_point = DsonChannelVector.load(center_point_json)

        # End point
        end_point_json:dict = None
        if "end_point" in node_json:
            end_point_json = node_json["end_point"]
        struct.end_point = DsonChannelVector.load(end_point_json)

        # Orientation
        orientation_json:dict = None
        if "orientation" in node_json:
            orientation_json = node_json["orientation"]
        struct.orientation = DsonChannelVector.load(orientation_json)

        # Rotation
        rotation_json:dict = None
        if "rotation" in node_json:
            rotation_json = node_json["rotation"]
        struct.rotation = DsonChannelVector.load(rotation_json)

        # Translation
        translation_json:dict = None
        if "translation" in node_json:
            translation_json = node_json["translation"]
        struct.translation = DsonChannelVector.load(translation_json)

        # Scale
        scale_json:dict = None
        if "scale" in node_json:
            scale_json = node_json["scale"]
        struct.scale = DsonChannelVector.load(scale_json, 1.0, 1.0, 1.0)

        # General scale
        general_scale_json:dict = None
        if "general_scale" in node_json:
            general_scale_json = node_json["general_scale"]
        struct.general_scale = DsonChannelFloat.load(general_scale_json, default_value=1.0)

        # Presentation
        if "presentation" in node_json:
            struct.presentation = DsonPresentation.load(node_json["presentation"])

        # Formulas
        if "formulas" in node_json:
            struct.formulas = DsonFormula.load(node_json["formulas"])

        # Fire observer update.
        _node_struct_created(struct, node_json)

        return struct


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def _inherits_scale_default(struct:DsonNode) -> bool:

    # All nodes default to inherit scale == True, except bones with bone
    #   parents.
    if not (struct.node_type == NodeType.BONE and struct.parent):
        return True

    # Create variables to access property.
    address:AssetAddress = AssetAddress.from_url(struct.parent)
    property_path:list[Any] = [ "node_library", address.asset_id, "type" ]

    # Get type as string
    parent_type:str = get_single_property_from_library(address.filepath, property_path)

    # Convert string to enum and compare. If bone w/ bone parent, then
    #   inherits scale is false.
    if NodeType(parent_type) == NodeType.BONE:
        return False

    # Not a bone with bone parent.
    return True
