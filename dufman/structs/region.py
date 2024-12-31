# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from dataclasses import dataclass
from typing import Self

@dataclass
class DsonRegion:

    id                      : str                   = None
    label                   : str                   = None
    display_hint            : str                   = None
    face_indices            : list[int]             = None
    parent                  : Self                  = None
    children                : list[Self]            = None

    @staticmethod
    def load(root_region_json:dict) -> list[Self]:

        all_structs:list[Self] = []

        def recursive(parent:Self, parent_json:dict) -> None:

            parent.id = parent_json["id"]
            all_structs.append(parent)

            if "label" in parent_json:
                parent.label = parent_json["label"]

            if "display_hint" in parent_json:
                parent.display_hint = parent_json["display_hint"]

            if "map" in parent_json:
                parent.face_indices = list(parent_json["map"]["values"])

            parent.children = []

            for child_dict in parent_json.get("children", []):
                child:DsonRegion = DsonRegion()
                child.parent = parent
                parent.children.append(child)
                recursive(child, child_dict)

        recursive(DsonRegion(), root_region_json)

        return all_structs
