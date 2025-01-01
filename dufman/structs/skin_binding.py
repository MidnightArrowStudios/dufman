# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

# stdlib
from dataclasses import dataclass
from typing import Self

# dufman
from dufman.structs.named_string_map import DsonNamedStringMap
from dufman.structs.weighted_joint import DsonWeightedJoint


# ============================================================================ #
# DsonSkinBinding                                                              #
# ============================================================================ #

@dataclass
class DsonSkinBinding:

    node                    : str                           = None
    geometry                : str                           = None
    expected_vertices       : int                           = 0
    weighted_joints         : list[DsonWeightedJoint]       = None
    selection_sets          : list[DsonNamedStringMap]      = None


    # ======================================================================== #

    @staticmethod
    def load_from_dson(skin_binding_dson:dict) -> Self:

        if not skin_binding_dson:
            return None

        if not isinstance(skin_binding_dson, dict):
            raise TypeError

        struct:DsonSkinBinding = DsonSkinBinding()

        # -------------------------------------------------------------------- #

        # Node URL
        if "node" in skin_binding_dson:
            struct.node = skin_binding_dson["node"]
        else:
            raise ValueError("Missing required property \"node\"")

        # Geometry URL
        if "geometry" in skin_binding_dson:
            struct.geometry = skin_binding_dson["geometry"]
        else:
            raise ValueError("Missing required property \"geometry\"")

        # Expected vertices
        if "vertex_count" in skin_binding_dson:
            struct.expected_vertices = skin_binding_dson["vertex_count"]
        else:
            raise ValueError("Missing required property \"vertex_count\"")

        # Weighted joint
        if "joints" in skin_binding_dson:
            struct.weighted_joints = []
            for joint_dson in skin_binding_dson["joints"]:
                struct.weighted_joints.append(DsonWeightedJoint.load_from_dson(joint_dson))

        # Named string map
        map_list:list[list] = None

        if "selection_sets" in skin_binding_dson:
            map_list = skin_binding_dson["selection_sets"]

        # This is not defined in the DSON specs, but every official Daz figure
        #   seems to use it?
        if "selection_map" in skin_binding_dson:
            map_list = skin_binding_dson["selection_map"]

        if map_list:

            struct.selection_sets = []

            for map_dson in map_list:
                struct.selection_sets.append(DsonNamedStringMap.load_from_dson(map_dson))

        # -------------------------------------------------------------------- #

        return struct
