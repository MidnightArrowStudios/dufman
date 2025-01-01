# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

"""Defines a struct which encapsulates DSON's "named_string_map" datatype.

http://docs.daz3d.com/doku.php/public/dson_spec/object_definitions/named_string_map/start
"""

# stdlib
from dataclasses import dataclass
from typing import NamedTuple, Self


# ============================================================================ #
# NameMapping struct                                                           #
# ============================================================================ #

class NameMapping(NamedTuple):
    face_name:str
    node_name:str


# ============================================================================ #
# DsonNamedStringMap struct                                                    #
# ============================================================================ #

@dataclass
class DsonNamedStringMap:

    map_id              : str               = None
    mappings            : list[NameMapping] = None


    # ======================================================================== #

    @staticmethod
    def load_from_dson(map_dson:dict) -> Self:

        if not map_dson:
            return None

        if not isinstance(map_dson, dict):
            raise TypeError

        struct:DsonNamedStringMap = DsonNamedStringMap()

        # -------------------------------------------------------------------- #

        # ID
        if "id" in map_dson:
            struct.map_id = map_dson["id"]
        else:
            raise ValueError("Missing required property \"ID\"")

        # Mappings
        if not "mappings" in map_dson:
            raise ValueError("Missing required property \"mappings\"")

        struct.mappings = []

        for mapping_list in map_dson["mappings"]:
            face_name:str = mapping_list[0]
            node_name:str = mapping_list[1]
            mapping:NameMapping = NameMapping(face_name, node_name)
            struct.mappings.append(mapping)

        # -------------------------------------------------------------------- #

        return struct
