# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from __future__ import annotations
from dataclasses import dataclass

from dufman.datatypes.vector import DsonVector

@dataclass
class DsonMorph:

    expected_vertices:int = 0
    deltas:dict = None


    @classmethod
    def load(cls:type, morph_json:dict) -> DsonMorph:

        # If modifier has empty dictionary, return
        if not morph_json:
            return None

        struct:DsonMorph = cls()

        # Vertex count
        # NOTE: This property actually doesn't matter, since some assets like
        #   iSourceTextures's Evangeliya have a value of -1.
        if "vertex_count" in morph_json:
            struct.expected_vertices = morph_json["vertex_count"]
        else:
            raise Exception("Missing required property \"vertex_count\"")

        # Morph deltas
        if "deltas" in morph_json:
            struct.deltas = { item[0]: DsonVector(item[1:4]) for item in morph_json["deltas"]["values"] }
        else:
            raise Exception("Missing required property \"deltas\"")

        return struct
