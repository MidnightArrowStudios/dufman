# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

"""DsonGraft defines how one mesh should be geografted to another."""

# stdlib
from dataclasses import dataclass
from typing import NamedTuple, Self


# ============================================================================ #
# Pair                                                                         #
# ============================================================================ #

class _Pair(NamedTuple):
    """Pairs a geograft vertex with its anchor vertex on the target geometry."""
    source:int
    target:int


# ============================================================================ #
# DsonGraft                                                                    #
# ============================================================================ #

@dataclass
class DsonGraft:

    expected_vertices:int = None
    expected_polygons:int = None

    vertex_pairs:list[_Pair] = None
    hidden_polygons:list[int] = None


    # ======================================================================== #

    @staticmethod
    def load(graft_json:dict) -> Self:
        """Factory method for the creation of DsonGraft structs."""

        # Some DSON files have empty graft dictionaries.
        if not graft_json:
            return None

        if not isinstance(graft_json, dict):
            raise TypeError

        struct:DsonGraft = DsonGraft()

        # -------------------------------------------------------------------- #

        # Expected vertices
        if "vertex_count" in graft_json:
            struct.expected_vertices = graft_json["vertex_count"]
        else:
            raise ValueError("Missing required property \"vertex_count\"")

        # Expected polygons
        if "poly_count" in graft_json:
            struct.expected_polygons = graft_json["poly_count"]
        else:
            raise ValueError("Missing required property \"poly_count\"")

        # Vertex pairs
        if "vertex_pairs" in graft_json:
            pairs:list[_Pair] = [ _Pair(i[0], i[1]) for i in graft_json["vertex_pairs"]["values"] ]
            struct.vertex_pairs = pairs
        else:
            raise ValueError("Missing required property \"vertex_pairs\"")

        # Hidden polygons
        if "hidden_polys" in graft_json:
            struct.hidden_polygons:list[int] = list(graft_json["hidden_polys"]["values"])
        else:
            raise ValueError("Missing required property \"hidden_polys\"")

        # -------------------------------------------------------------------- #

        return struct
