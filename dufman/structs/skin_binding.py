# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from dataclasses import dataclass
from typing import Self

from dufman.structs.named_string_map import DsonNamedStringMap
from dufman.structs.weighted_joint import DsonWeightedJoint

@dataclass
class DsonSkinBinding:

    node                    : str                           = None
    geometry                : str                           = None
    expected_vertices       : int                           = 0
    weighted_joints         : list[DsonWeightedJoint]       = None
    selection_sets          : list[DsonNamedStringMap]      = None


    @staticmethod
    def load(binding_json:dict) -> Self:

        if not binding_json:
            return None

        struct:DsonSkinBinding = DsonSkinBinding()

        # Node URL
        if "node" in binding_json:
            struct.node = binding_json["node"]
        else:
            raise ValueError("Missing required property \"node\"")

        # Geometry URL
        if "geometry" in binding_json:
            struct.geometry = binding_json["geometry"]
        else:
            raise ValueError("Missing required property \"geometry\"")

        # Expected vertices
        if "vertex_count" in binding_json:
            struct.expected_vertices = binding_json["vertex_count"]
        else:
            raise ValueError("Missing required property \"vertex_count\"")

        # Weighted joint
        if "joints" in binding_json:
            struct.weighted_joints = []
            for joint_json in binding_json["joints"]:
                struct.weighted_joints.append(DsonWeightedJoint.load(joint_json))

        # Named string map
        map_list:list[list] = None

        if "selection_sets" in binding_json:
            map_list = binding_json["selection_sets"]

        # This is not defined in the DSON specs, but every official Daz figure
        #   seems to use it?
        if "selection_map" in binding_json:
            map_list = binding_json["selection_map"]

        if map_list:

            struct.selection_sets = []

            for map_json in map_list:
                struct.selection_sets.append(DsonNamedStringMap.load(map_json))

        return struct
