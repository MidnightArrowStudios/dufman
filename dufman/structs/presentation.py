# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from dataclasses import dataclass
from typing import Any, Self

from dufman.types import DsonColor

@dataclass
class DsonPresentation:

    content_type            : str           = None
    label                   : str           = None
    description             : str           = None
    icon_large              : str           = None
    icon_small              : str           = None
    color1                  : DsonColor     = None
    color2                  : DsonColor     = None

    @staticmethod
    def load(presentation_json:dict) -> Self:

        struct:DsonPresentation = DsonPresentation()

        # Content type
        if "type" in presentation_json:
            struct.content_type = presentation_json["type"]
        else:
            raise ValueError("Missing required property \"type\"")

        # Label
        if "label" in presentation_json:
            struct.label = presentation_json["label"]
        else:
            raise ValueError("Missing required property \"label\"")

        # Description
        if "description" in presentation_json:
            struct.description = presentation_json["description"]
        else:
            raise ValueError("Missing required property \"description\"")

        # Icon (large)
        if "icon_large" in presentation_json:
            struct.icon_large = presentation_json["icon_large"]
        else:
            raise ValueError("Missing required property \"icon_large\"")

        # Icon (small)
        if "icon_small" in presentation_json:
            struct.icon_small = presentation_json["icon_small"]

        # Colors
        if not "colors" in presentation_json:
            raise ValueError("Missing required property \"colors\"")

        colors:Any = presentation_json["colors"]
        if not (isinstance(colors, list) and len(colors) == 2):
            raise TypeError("\"colors\" property must be an array with two elements")

        struct.color1 = DsonColor(colors[0])
        struct.color2 = DsonColor(colors[1])

        return struct
