# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

"""DsonGraft defines how one mesh should be geografted to another."""

from dataclasses import dataclass
from typing import NamedTuple, Self



@dataclass
class DsonGraft:

    class Pair(NamedTuple):
        """Pairs a geograft vertex with its anchor vertex on the target geometry."""
        source:int
        target:int

    expected_vertices:int = None
    expected_polygons:int = None

    vertex_pairs:list[Pair] = None
    hidden_polygons:list[int] = None

    @staticmethod
    def load(graft_json:dict) -> Self:
        """Factory method for the creation of DsonGraft structs."""

        # Geometry has empty graft dictionary
        if not graft_json:
            return None

        # Expected vertices
        expected_vertices:int = None
        if "vertex_count" in graft_json:
            expected_vertices = graft_json["vertex_count"]
        else:
            raise ValueError("Missing required property \"vertex_count\"")

        # Expected polygons
        expected_polygons:int = None
        if "poly_count" in graft_json:
            expected_polygons = graft_json["poly_count"]
        else:
            raise ValueError("Missing required property \"poly_count\"")

        # Vertex pairs
        if not "vertex_pairs" in graft_json:
            raise ValueError("Missing required property \"vertex_pairs\"")

        vertex_pairs:list[DsonGraft.Pair] = [ DsonGraft.Pair(source=entry[0], target=entry[1]) for entry in graft_json["vertex_pairs"]["values"] ]

        # Hidden polygons
        if not "hidden_polys" in graft_json:
            raise ValueError("Missing required property \"hidden_polys\"")

        hidden_polygons:list[int] = list(graft_json["hidden_polys"]["values"])

        return DsonGraft(
            expected_vertices=expected_vertices,
            expected_polygons=expected_polygons,
            vertex_pairs=vertex_pairs,
            hidden_polygons=hidden_polygons,
            )
