# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from __future__ import annotations
from dataclasses import dataclass

@dataclass
class DsonWeightedJoint:

    joint_id:str = None
    node:str = None

    node_weights:dict = None
    scale_weights:dict = None
    local_weights:list = None
    bulge_weights:list = None


    @classmethod
    def load(cls:type, joint_json:dict) -> DsonWeightedJoint:

        if not joint_json:
            return None

        struct:DsonWeightedJoint = cls()

        # ID
        if "id" in joint_json:
            struct.joint_id = joint_json["id"]
        else:
            raise Exception("Missing required property \"ID\"")

        # Node URL
        if "node" in joint_json:
            struct.node = joint_json["node"]
        else:
            raise Exception("Missing required property \"node\"")

        # Ensure weighted joint has at least one type of weighting
        has_weights:bool = False

        # Node weights
        if "node_weights" in joint_json:
            has_weights = True
            struct.node_weights = { item[0]: item[1] for item in joint_json["node_weights"]["values"] }

        # Scale weights
        if "scale_weights" in joint_json:
            raise NotImplementedError

        # Local weights
        if "local_weights" in joint_json:
            raise NotImplementedError

        # Bulge weights
        if "bulge_weights" in joint_json:
            raise NotImplementedError

        # Weighted joint is not valid
        if not has_weights:
            raise Exception("Weighted joint does not have any weights")

        return struct
