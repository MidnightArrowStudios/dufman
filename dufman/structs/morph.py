# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

"""Defines a struct which encapsulates DSON's "morph" datatype.

http://docs.daz3d.com/doku.php/public/dson_spec/object_definitions/morph/start
"""

# stdlib
from dataclasses import dataclass
from typing import Self

# dufman
from dufman.types import DsonVector


# ============================================================================ #
# DsonMorph struct
# ============================================================================ #

@dataclass
class DsonMorph:

    expected_vertices:int = 0
    deltas:dict = None


    # ======================================================================== #

    @staticmethod
    def load_from_dson(morph_dson:dict) -> Self:

        # If modifier has empty dictionary, return
        if not morph_dson:
            return None

        if not isinstance(morph_dson, dict):
            raise TypeError

        struct:DsonMorph = DsonMorph()

        # -------------------------------------------------------------------- #

        # Vertex count
        # NOTE: This property actually doesn't matter, since some assets like
        #   iSourceTextures's Evangeliya have a value of -1.
        if "vertex_count" in morph_dson:
            struct.expected_vertices = morph_dson["vertex_count"]
        else:
            raise ValueError("Missing required property \"vertex_count\"")

        # Morph deltas
        if "deltas" in morph_dson:
            struct.deltas = { item[0]: DsonVector(item[1:4]) for item in morph_dson["deltas"]["values"] }
        else:
            raise ValueError("Missing required property \"deltas\"")

        # -------------------------------------------------------------------- #

        return struct
