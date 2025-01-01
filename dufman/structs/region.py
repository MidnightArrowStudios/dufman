# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

# stdlib
from dataclasses import dataclass
from typing import Self


# ============================================================================ #
# DsonRegion struct                                                            #
# ============================================================================ #

@dataclass
class DsonRegion:

    id                      : str                   = None
    label                   : str                   = None
    display_hint            : str                   = None
    face_indices            : list[int]             = None
    parent                  : Self                  = None
    children                : list[Self]            = None


    # ======================================================================== #

    @staticmethod
    def load_from_dson(root_region_dson:dict) -> list[Self]:

        if not root_region_dson:
            return None

        if not isinstance(root_region_dson, dict):
            raise TypeError

        # -------------------------------------------------------------------- #

        all_structs:list[Self] = []

        def recursive(parent:Self, parent_dson:dict) -> None:

            parent.id = parent_dson["id"]
            all_structs.append(parent)

            if "label" in parent_dson:
                parent.label = parent_dson["label"]

            if "display_hint" in parent_dson:
                parent.display_hint = parent_dson["display_hint"]

            if "map" in parent_dson:
                parent.face_indices = list(parent_dson["map"]["values"])

            parent.children = []

            for child_dict in parent_dson.get("children", []):
                child:DsonRegion = DsonRegion()
                child.parent = parent
                parent.children.append(child)
                recursive(child, child_dict)

        # -------------------------------------------------------------------- #

        recursive(DsonRegion(), root_region_dson)

        return all_structs
