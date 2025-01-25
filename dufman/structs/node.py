# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self

from dufman.enums import LibraryType, NodeType, RotationOrder
from dufman.observers import _node_struct_created
from dufman.url import DazUrl

from dufman.structs.channel import DsonChannelFloat, DsonChannelVector
from dufman.structs.formula import DsonFormula
from dufman.structs.presentation import DsonPresentation


# ============================================================================ #
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
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
    # LOAD FROM DSON                                                           #
    # ======================================================================== #

    @staticmethod
    def load_from_dson(node_dson:dict) -> Self:

        if not node_dson:
            return None

        if not isinstance(node_dson, dict):
            raise TypeError

        struct:DsonNode = DsonNode()

        # -------------------------------------------------------------------- #

        # ID
        if "id" in node_dson:
            struct.library_id = node_dson["id"]
        else:
            raise ValueError("Missing required property \"ID\"")

        # Name
        if "name" in node_dson:
            struct.name = node_dson["name"]
        else:
            raise ValueError("Missing required property \"name\"")

        # Type
        if "type" in node_dson:
            struct.node_type = NodeType(node_dson["type"])

        # Label
        if "label" in node_dson:
            struct.label = node_dson["label"]
        else:
            raise ValueError("Missing required property \"label\"")

        # Source
        if "source" in node_dson:
            struct.source = node_dson["source"]

        # Parent
        if "parent" in node_dson:
            struct.parent = node_dson["parent"]

        # Rotation order
        if "rotation_order" in node_dson:
            struct.rotation_order = RotationOrder(node_dson["rotation_order"])

        # Inherits scale
        if "inherits_scale" in node_dson:
            struct.inherits_scale = node_dson["inherits_scale"]
        else:
            struct.inherits_scale = _inherits_scale_default(struct)

        # Center point
        center_point_dson:dict = None
        if "center_point" in node_dson:
            center_point_dson = node_dson["center_point"]
        struct.center_point = DsonChannelVector.load_from_dson(center_point_dson)

        # End point
        end_point_dson:dict = None
        if "end_point" in node_dson:
            end_point_dson = node_dson["end_point"]
        struct.end_point = DsonChannelVector.load_from_dson(end_point_dson)

        # Orientation
        orientation_dson:dict = None
        if "orientation" in node_dson:
            orientation_dson = node_dson["orientation"]
        struct.orientation = DsonChannelVector.load_from_dson(orientation_dson)

        # Rotation
        rotation_dson:dict = None
        if "rotation" in node_dson:
            rotation_dson = node_dson["rotation"]
        struct.rotation = DsonChannelVector.load_from_dson(rotation_dson)

        # Translation
        translation_dson:dict = None
        if "translation" in node_dson:
            translation_dson = node_dson["translation"]
        struct.translation = DsonChannelVector.load_from_dson(translation_dson)

        # Scale
        scale_dson:dict = None
        if "scale" in node_dson:
            scale_dson = node_dson["scale"]
        struct.scale = DsonChannelVector.load_from_dson(scale_dson, default_value=1.0)

        # General scale
        general_scale_dson:dict = None
        if "general_scale" in node_dson:
            general_scale_dson = node_dson["general_scale"]
        struct.general_scale = DsonChannelFloat.load_from_dson(general_scale_dson, default_value=1.0)

        # Presentation
        if "presentation" in node_dson:
            struct.presentation = DsonPresentation.load_from_dson(node_dson["presentation"])

        # Formulas
        if "formulas" in node_dson:
            struct.formulas = DsonFormula.load_from_dson(node_dson["formulas"])

        # -------------------------------------------------------------------- #

        return struct


    # ======================================================================== #
    # LOAD FROM FILE                                                           #
    # ======================================================================== #

    @staticmethod
    def load_from_file(daz_url:DazUrl) -> Self:

        if not daz_url or not isinstance(daz_url, DazUrl):
            raise TypeError

        node_dson, _ = daz_url.get_asset_dson(LibraryType.NODE)

        struct:Self = DsonNode.load_from_dson(node_dson)
        struct.dsf_file = daz_url.get_url_to_asset()

        # Fire observer update.
        _node_struct_created(struct, node_dson)

        return struct


# ============================================================================ #
# UTILITY FUNCTIONS                                                            #
# ============================================================================ #

def _inherits_scale_default(struct:DsonNode) -> bool:

    # All nodes default to inherit scale == True, except bones with bone
    #   parents.
    if not (struct.node_type == NodeType.BONE and struct.parent):
        return True

    # Create variables to access property.
    daz_url:DazUrl = DazUrl.from_url(struct.parent)
    value_path:list[Any] = [ "node_library", daz_url.asset_id, "type" ]

    # Get type as string
    parent_type:str = daz_url.get_value(value_path)

    # Convert string to enum and compare. If bone w/ bone parent, then
    #   inherits scale is false.
    if NodeType(parent_type) == NodeType.BONE:
        return False

    # Not a bone with bone parent.
    return True
