# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

"""DsonGraft defines how one mesh should be geografted to another."""

from __future__ import annotations
from dataclasses import dataclass
from typing import NamedTuple

@dataclass
class DsonGraft:

    expected_vertices:int = None
    expected_polygons:int = None

    vertex_pairs:list[Pair] = None
    hidden_polygons:list[int] = None

    class Pair(NamedTuple):
        """Pairs a geograft vertex with its anchor vertex on the target geometry."""
        source:int
        target:int


    @classmethod
    def load(cls:type, graft_json:dict) -> DsonGraft:
        """Factory method for the creation of DsonGraft structs."""

        # Geometry has empty graft dictionary
        if not graft_json:
            return None

        # Expected vertices
        expected_vertices:int = None
        if "vertex_count" in graft_json:
            expected_vertices = graft_json["vertex_count"]
        else:
            raise Exception("Missing required property \"vertex_count\"")

        # Expected polygons
        expected_polygons:int = None
        if "poly_count" in graft_json:
            expected_polygons = graft_json["poly_count"]
        else:
            raise Exception("Missing required property \"poly_count\"")

        # Vertex pairs
        if not "vertex_pairs" in graft_json:
            raise Exception("Missing required property \"vertex_pairs\"")

        vertex_pairs:list[cls.Pair] = [ cls.Pair(source=entry[0], target=entry[1]) for entry in graft_json["vertex_pairs"]["values"] ]

        # Hidden polygons
        if not "hidden_polys" in graft_json:
            raise Exception("Missing required property \"hidden_polys\"")

        hidden_polygons:list[int] = list(graft_json["hidden_polys"]["values"])

        return cls(
            expected_vertices=expected_vertices,
            expected_polygons=expected_polygons,
            vertex_pairs=vertex_pairs,
            hidden_polygons=hidden_polygons,
            )
