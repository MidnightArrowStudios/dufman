# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from dataclasses import dataclass
from typing import Self

from dufman.enums import RigidRotation, RigidScale


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


@dataclass
class DsonRigidity:

    weights:dict = None
    groups:list[_Group] = None


    @staticmethod
    def load(rigidity_json:dict) -> Self:

        # Weights
        weights:dict = None
        if "weights" in rigidity_json:
            weights = { entry[0]: entry[1] for entry in rigidity_json["weights"]["values"] }

        # Groups
        if not "groups" in rigidity_json:
            raise ValueError("Missing required property \"groups\"")

        groups:list[_Group] = []

        for group_json in rigidity_json["groups"]:

            group:_Group = _Group()
            groups.append(group)

            # TODO: Error handling

            group.group_id = group_json["id"]
            group.scale_x = RigidScale(group_json["scale_modes"][0])
            group.scale_y = RigidScale(group_json["scale_modes"][1])
            group.scale_z = RigidScale(group_json["scale_modes"][2])

            if "reference_vertices" in group_json:
                group.reference_vertices = list(group_json["reference_vertices"]["values"])

            if "mask_vertices" in group_json:
                group.participant_vertices = list(group_json["mask_vertices"]["values"])

            if "reference" in group_json:
                group.reference = group_json["reference"]

            if "transform_nodes" in group_json:
                group.transform_nodes = list(group_json["transform_nodes"])

        return DsonRigidity(weights, groups)
