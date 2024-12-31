# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from dataclasses import dataclass
from typing import NamedTuple, Self


@dataclass
class DsonNamedStringMap:

    class Mapping(NamedTuple):
        face_name:str
        node_name:str


    map_id              : str               = None
    mappings            : list[Mapping]     = None

    @staticmethod
    def load(map_json:dict) -> Self:

        if not map_json:
            return None

        struct:DsonNamedStringMap = DsonNamedStringMap()

        # ID
        if "id" in map_json:
            struct.map_id = map_json["id"]
        else:
            raise ValueError("Missing required property \"ID\"")

        # Mappings
        if not "mappings" in map_json:
            raise ValueError("Missing required property \"mappings\"")

        struct.mappings = []

        for mapping_list in map_json["mappings"]:
            face_name:str = mapping_list[0]
            node_name:str = mapping_list[1]
            mapping:DsonNamedStringMap.Mapping = DsonNamedStringMap.Mapping(face_name, node_name)
            struct.mappings.append(mapping)

        return struct
