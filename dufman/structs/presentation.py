# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

"""Defines a struct which encapsulates DSON's "presentation" datatype.

http://docs.daz3d.com/doku.php/public/dson_spec/object_definitions/presentation/start
"""

# stdlib
from dataclasses import dataclass
from typing import Any, Self

# dufman
from dufman.types import DsonColor


# ============================================================================ #
# DsonPresentation struct                                                      #
# ============================================================================ #

@dataclass
class DsonPresentation:

    content_type            : str           = None
    label                   : str           = None
    description             : str           = None
    icon_large              : str           = None
    icon_small              : str           = None
    color1                  : DsonColor     = None
    color2                  : DsonColor     = None


    # ======================================================================== #

    @staticmethod
    def load_from_dson(presentation_dson:dict) -> Self:

        if not presentation_dson:
            return None

        if not isinstance(presentation_dson, dict):
            raise TypeError

        struct:DsonPresentation = DsonPresentation()

        # -------------------------------------------------------------------- #

        # Content type
        if "type" in presentation_dson:
            struct.content_type = presentation_dson["type"]
        else:
            raise ValueError("Missing required property \"type\"")

        # Label
        if "label" in presentation_dson:
            struct.label = presentation_dson["label"]
        else:
            raise ValueError("Missing required property \"label\"")

        # Description
        if "description" in presentation_dson:
            struct.description = presentation_dson["description"]
        else:
            raise ValueError("Missing required property \"description\"")

        # Icon (large)
        if "icon_large" in presentation_dson:
            struct.icon_large = presentation_dson["icon_large"]
        else:
            raise ValueError("Missing required property \"icon_large\"")

        # Icon (small)
        if "icon_small" in presentation_dson:
            struct.icon_small = presentation_dson["icon_small"]

        # Colors
        if not "colors" in presentation_dson:
            raise ValueError("Missing required property \"colors\"")

        colors:Any = presentation_dson["colors"]
        if not (isinstance(colors, list) and len(colors) == 2):
            raise TypeError("\"colors\" property must be an array with two elements")

        struct.color1 = DsonColor(colors[0])
        struct.color2 = DsonColor(colors[1])

        # -------------------------------------------------------------------- #

        return struct
