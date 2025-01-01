# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

# stdlib
from dataclasses import dataclass
from typing import Self

# dufman
from dufman.enums import RigidRotation, RigidScale


# ============================================================================ #
# Group                                                                        #
# ============================================================================ #

@dataclass
class _Group:
    group_id                : str               = None
    rotation                : RigidRotation     = RigidRotation.NONE
    scale_x                 : RigidScale        = None
    scale_y                 : RigidScale        = None
    scale_z                 : RigidScale        = None
    reference_vertices      : list[int]         = None
    participant_vertices    : list[int]         = None
    reference               : str               = None
    transform_nodes         : list[str]         = None


# ============================================================================ #
# DsonRigidity struct                                                          #
# ============================================================================ #

@dataclass
class DsonRigidity:

    weights:dict = None
    groups:list[_Group] = None


    # ======================================================================== #

    @staticmethod
    def load_from_dson(rigidity_dson:dict) -> Self:

        if not rigidity_dson:
            return None

        if not isinstance(rigidity_dson, dict):
            raise TypeError

        struct:Self = DsonRigidity()

        # -------------------------------------------------------------------- #

        # Weights
        if "weights" in rigidity_dson:
            struct.weights = { entry[0]: entry[1] for entry in rigidity_dson["weights"]["values"] }

        # Groups
        if not "groups" in rigidity_dson:
            raise ValueError("Missing required property \"groups\"")
        struct.groups = []

        for group_dson in rigidity_dson["groups"]:

            group:_Group = _Group()

            # ---------------------------------------------------------------- #
            # TODO: Error handling

            group.group_id = group_dson["id"]
            group.scale_x = RigidScale(group_dson["scale_modes"][0])
            group.scale_y = RigidScale(group_dson["scale_modes"][1])
            group.scale_z = RigidScale(group_dson["scale_modes"][2])

            if "reference_vertices" in group_dson:
                group.reference_vertices = list(group_dson["reference_vertices"]["values"])

            if "mask_vertices" in group_dson:
                group.participant_vertices = list(group_dson["mask_vertices"]["values"])

            if "reference" in group_dson:
                group.reference = group_dson["reference"]

            if "transform_nodes" in group_dson:
                group.transform_nodes = list(group_dson["transform_nodes"])

            # ---------------------------------------------------------------- #

            struct.groups.append(group)

            # ---------------------------------------------------------------- #

        return struct
