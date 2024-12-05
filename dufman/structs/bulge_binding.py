# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from __future__ import annotations
from dataclasses import dataclass

from .channel import DsonChannelFloat

@dataclass
class DsonBulgeBinding:

    positive_left   : DsonChannelFloat  = None
    positive_right  : DsonChannelFloat  = None
    negative_left   : DsonChannelFloat  = None
    negative_right  : DsonChannelFloat  = None

    left_map        : dict              = None
    right_map       : dict              = None

    @classmethod
    def load(cls:type, bulge_json:dict) -> DsonBulgeBinding:
        """Factory method to create and validate DsonBulgeBinding objects."""

        struct:DsonBulgeBinding = cls()

        bulge_axes:dict = { axis["id"]: axis for axis in bulge_json["bulges"] }

        # NOTE: I attempted to do a list comparison with the dictionary's keys,
        #   but it failed for unknown reasons.

        # Positive left
        if "positive-left" in bulge_axes:
            struct.positive_left = DsonChannelFloat.load(bulge_axes["positive-left"])
        else:
            raise Exception("Missing required property \"positive-left\"")

        # Positive right
        if "positive-right" in bulge_axes:
            struct.positive_right = DsonChannelFloat.load(bulge_axes["positive-right"])
        else:
            raise Exception("Missing required property \"positive-right\"")

        # Negative left
        if "negative-left" in bulge_axes:
            struct.negative_left = DsonChannelFloat.load(bulge_axes["negative-left"])
        else:
            raise Exception("Missing required property \"negative-left\"")

        # Negative right
        if "negative-right" in bulge_axes:
            struct.negative_right = DsonChannelFloat.load(bulge_axes["negative-right"])
        else:
            raise Exception("Missing required property \"negative-right\"")

        # Left map
        struct.left_map = { entry[0]: entry[1] for entry in bulge_json["left_map"]["values"] }

        # Right map
        struct.right_map = { entry[0]: entry[1] for entry in bulge_json["right_map"]["values"] }

        return struct


@dataclass
class DsonBulgeWeights:

    bulge_x     : DsonBulgeBinding = None
    bulge_y     : DsonBulgeBinding = None
    bulge_z     : DsonBulgeBinding = None

    @classmethod
    def load(cls:type, array:list) -> DsonBulgeWeights:
        """Factory method to create and validate DsonBulgeWeights object."""

        if not array:
            raise Exception("Data array is None")

        struct:DsonBulgeWeights = cls()

        axes:dict = { axis: array[axis] for axis in array }

        if 'x' in axes:
            struct.bulge_x = DsonBulgeBinding.load(axes['x'])
        if 'y' in axes:
            struct.bulge_y = DsonBulgeBinding.load(axes['y'])
        if 'z' in axes:
            struct.bulge_z = DsonBulgeBinding.load(axes['z'])

        return struct
