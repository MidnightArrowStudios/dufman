# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

# stdlib
from dataclasses import dataclass
from typing import Self


# ============================================================================ #
# DsonWeightedJoint struct                                                     #
# ============================================================================ #

@dataclass
class DsonWeightedJoint:

    joint_id:str = None
    node:str = None

    node_weights:dict = None
    scale_weights:dict = None
    local_weights:list = None
    bulge_weights:list = None


    # ======================================================================== #

    @staticmethod
    def load_from_dson(weighted_joint_dson:dict) -> Self:

        if not weighted_joint_dson:
            return None

        if not isinstance(weighted_joint_dson, dict):
            raise TypeError

        struct:Self = DsonWeightedJoint()

        # -------------------------------------------------------------------- #

        # ID
        if "id" in weighted_joint_dson:
            struct.joint_id = weighted_joint_dson["id"]
        else:
            raise ValueError("Missing required property \"ID\"")

        # Node URL
        if "node" in weighted_joint_dson:
            struct.node = weighted_joint_dson["node"]
        else:
            raise ValueError("Missing required property \"node\"")

        # Ensure weighted joint has at least one type of weighting
        has_weights:bool = False

        # Node weights
        if "node_weights" in weighted_joint_dson:
            has_weights = True
            struct.node_weights = { item[0]: item[1] for item in weighted_joint_dson["node_weights"]["values"] }

        # Scale weights
        if "scale_weights" in weighted_joint_dson:
            raise NotImplementedError

        # Local weights
        if "local_weights" in weighted_joint_dson:
            raise NotImplementedError

        # Bulge weights
        if "bulge_weights" in weighted_joint_dson:
            raise NotImplementedError

        # Weighted joint is not valid
        if not has_weights:
            raise ValueError("Weighted joint does not have any weights")

        # -------------------------------------------------------------------- #

        return struct
