# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from dataclasses import dataclass
from typing import Self

from dufman.structs.channel import DsonChannelFloat

@dataclass
class DsonBulgeBinding:

    positive_left   : DsonChannelFloat  = None
    positive_right  : DsonChannelFloat  = None
    negative_left   : DsonChannelFloat  = None
    negative_right  : DsonChannelFloat  = None

    left_map        : dict              = None
    right_map       : dict              = None

    @staticmethod
    def load(bulge_json:dict) -> Self:
        """Factory method to create and validate DsonBulgeBinding objects."""

        struct:Self = DsonBulgeBinding()

        bulge_axes:dict = { axis["id"]: axis for axis in bulge_json["bulges"] }

        # NOTE: I attempted to do a list comparison with the dictionary's keys,
        #   but it failed for unknown reasons.

        # Positive left
        if "positive-left" in bulge_axes:
            struct.positive_left = DsonChannelFloat.load(bulge_axes["positive-left"])
        else:
            raise ValueError("Missing required property \"positive-left\"")

        # Positive right
        if "positive-right" in bulge_axes:
            struct.positive_right = DsonChannelFloat.load(bulge_axes["positive-right"])
        else:
            raise ValueError("Missing required property \"positive-right\"")

        # Negative left
        if "negative-left" in bulge_axes:
            struct.negative_left = DsonChannelFloat.load(bulge_axes["negative-left"])
        else:
            raise ValueError("Missing required property \"negative-left\"")

        # Negative right
        if "negative-right" in bulge_axes:
            struct.negative_right = DsonChannelFloat.load(bulge_axes["negative-right"])
        else:
            raise ValueError("Missing required property \"negative-right\"")

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

    @staticmethod
    def load(array:list) -> Self:
        """Factory method to create and validate DsonBulgeWeights object."""

        if not array:
            raise ValueError("Data array is None")

        struct:Self = DsonBulgeWeights()

        axes:dict = { axis: array[axis] for axis in array }

        if 'x' in axes:
            struct.bulge_x = DsonBulgeBinding.load(axes['x'])
        if 'y' in axes:
            struct.bulge_y = DsonBulgeBinding.load(axes['y'])
        if 'z' in axes:
            struct.bulge_z = DsonBulgeBinding.load(axes['z'])

        return struct
