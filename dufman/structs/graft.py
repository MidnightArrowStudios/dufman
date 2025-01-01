# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

"""Defines a struct which encapsulates DSON's "graft" datatype.

http://docs.daz3d.com/doku.php/public/dson_spec/object_definitions/graft/start
"""

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
# DsonGraft struct                                                             #
# ============================================================================ #

@dataclass
class DsonGraft:

    expected_vertices:int = None
    expected_polygons:int = None

    vertex_pairs:list[_Pair] = None
    hidden_polygons:list[int] = None


    # ======================================================================== #

    @staticmethod
    def load_from_dson(graft_dson:dict) -> Self:
        """Factory method for the creation of DsonGraft structs."""

        if not graft_dson:
            return None

        if not isinstance(graft_dson, dict):
            raise TypeError

        struct:DsonGraft = DsonGraft()

        # -------------------------------------------------------------------- #

        # Expected vertices
        if "vertex_count" in graft_dson:
            struct.expected_vertices = graft_dson["vertex_count"]
        else:
            raise ValueError("Missing required property \"vertex_count\"")

        # Expected polygons
        if "poly_count" in graft_dson:
            struct.expected_polygons = graft_dson["poly_count"]
        else:
            raise ValueError("Missing required property \"poly_count\"")

        # Vertex pairs
        if "vertex_pairs" in graft_dson:
            pairs:list[_Pair] = [ _Pair(i[0], i[1]) for i in graft_dson["vertex_pairs"]["values"] ]
            struct.vertex_pairs = pairs
        else:
            raise ValueError("Missing required property \"vertex_pairs\"")

        # Hidden polygons
        if "hidden_polys" in graft_dson:
            struct.hidden_polygons:list[int] = list(graft_dson["hidden_polys"]["values"])
        else:
            raise ValueError("Missing required property \"hidden_polys\"")

        # -------------------------------------------------------------------- #

        return struct
