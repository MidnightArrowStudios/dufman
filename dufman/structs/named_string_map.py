# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from __future__ import annotations
from dataclasses import dataclass
from typing import NamedTuple


@dataclass
class DsonNamedStringMap:

    class Mapping(NamedTuple):
        face_name:str
        node_name:str


    map_id              : str               = None
    mappings            : list[Mapping]     = None

    @classmethod
    def load(cls:type, map_json:dict) -> DsonNamedStringMap:

        if not map_json:
            return None

        struct:DsonNamedStringMap = cls()

        # ID
        if "id" in map_json:
            struct.map_id = map_json["id"]
        else:
            raise Exception("Missing required property \"ID\"")

        # Mappings
        if not "mappings" in map_json:
            raise Exception("Missing required property \"mappings\"")

        struct.mappings = []

        for mapping_list in map_json["mappings"]:
            face_name:str = mapping_list[0]
            node_name:str = mapping_list[1]
            mapping:DsonNamedStringMap.Mapping = DsonNamedStringMap.Mapping(face_name, node_name)
            struct.mappings.append(mapping)

        return struct
