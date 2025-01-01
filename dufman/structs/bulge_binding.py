# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

"""Defines a struct which encapsulates DSON's "bulge_binding" datatype.

http://docs.daz3d.com/doku.php/public/dson_spec/object_definitions/bulge_binding/start
"""

# stdlib
from dataclasses import dataclass
from typing import Self

# dufman
from dufman.structs.channel import DsonChannelFloat


# ============================================================================ #
# DsonBulgeBinding struct                                                      #
# ============================================================================ #

@dataclass
class DsonBulgeBinding:
    """Legacy (pre-Genesis 3) joint deformation data."""

    positive_left   : DsonChannelFloat  = None
    positive_right  : DsonChannelFloat  = None
    negative_left   : DsonChannelFloat  = None
    negative_right  : DsonChannelFloat  = None

    left_map        : dict              = None
    right_map       : dict              = None


    # ======================================================================== #

    @staticmethod
    def load_from_dson(bulge_binding_dson:dict) -> Self:
        """Factory method to create and validate DsonBulgeBinding objects."""

        if not bulge_binding_dson:
            return None

        if not isinstance(bulge_binding_dson, dict):
            raise TypeError

        struct:Self = DsonBulgeBinding()

        bulge_axes:dict = { axis["id"]: axis for axis in bulge_binding_dson["bulges"] }

        # -------------------------------------------------------------------- #

        # NOTE: I attempted to do a list comparison with the dictionary's keys,
        #   but it failed for unknown reasons.

        # Positive left
        if "positive-left" in bulge_axes:
            struct.positive_left = DsonChannelFloat.load_from_dson(bulge_axes["positive-left"])
        else:
            raise ValueError("Missing required property \"positive-left\"")

        # Positive right
        if "positive-right" in bulge_axes:
            struct.positive_right = DsonChannelFloat.load_from_dson(bulge_axes["positive-right"])
        else:
            raise ValueError("Missing required property \"positive-right\"")

        # Negative left
        if "negative-left" in bulge_axes:
            struct.negative_left = DsonChannelFloat.load_from_dson(bulge_axes["negative-left"])
        else:
            raise ValueError("Missing required property \"negative-left\"")

        # Negative right
        if "negative-right" in bulge_axes:
            struct.negative_right = DsonChannelFloat.load_from_dson(bulge_axes["negative-right"])
        else:
            raise ValueError("Missing required property \"negative-right\"")

        # Left map
        struct.left_map = { entry[0]: entry[1] for entry in bulge_binding_dson["left_map"]["values"] }

        # Right map
        struct.right_map = { entry[0]: entry[1] for entry in bulge_binding_dson["right_map"]["values"] }

        # -------------------------------------------------------------------- #

        return struct


# ============================================================================ #
# DsonBulgeWeights                                                             #
# ============================================================================ #

@dataclass
class DsonBulgeWeights:
    """Helper object which stores an XYZ vector of DsonBulgeBinding objects."""

    bulge_x     : DsonBulgeBinding = None
    bulge_y     : DsonBulgeBinding = None
    bulge_z     : DsonBulgeBinding = None


    # ======================================================================== #

    @staticmethod
    def load_from_dson(bulge_binding_vector:list) -> Self:
        """Factory method to create and validate DsonBulgeWeights object."""

        if not bulge_binding_vector:
            raise ValueError("Data array is None")

        struct:Self = DsonBulgeWeights()

        # -------------------------------------------------------------------- #

        axes:dict = { axis: bulge_binding_vector[axis] for axis in bulge_binding_vector }

        if 'x' in axes:
            struct.bulge_x = DsonBulgeBinding.load_from_dson(axes['x'])
        if 'y' in axes:
            struct.bulge_y = DsonBulgeBinding.load_from_dson(axes['y'])
        if 'z' in axes:
            struct.bulge_z = DsonBulgeBinding.load_from_dson(axes['z'])

        # -------------------------------------------------------------------- #

        return struct
