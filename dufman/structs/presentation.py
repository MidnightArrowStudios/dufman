# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from dufman.datatypes import DsonColor

@dataclass
class DsonPresentation:

    content_type            : str           = None
    label                   : str           = None
    description             : str           = None
    icon_large              : str           = None
    icon_small              : str           = None
    color1                  : DsonColor     = None
    color2                  : DsonColor     = None

    @classmethod
    def load(cls:type, presentation_json:dict) -> DsonPresentation:

        struct:DsonPresentation = cls()

        # Content type
        if "type" in presentation_json:
            struct.content_type = presentation_json["type"]
        else:
            raise Exception("Missing required property \"type\"")

        # Label
        if "label" in presentation_json:
            struct.label = presentation_json["label"]
        else:
            raise Exception("Missing required property \"label\"")

        # Description
        if "description" in presentation_json:
            struct.description = presentation_json["description"]
        else:
            raise Exception("Missing required property \"description\"")

        # Icon (large)
        if "icon_large" in presentation_json:
            struct.icon_large = presentation_json["icon_large"]
        else:
            raise Exception("Missing required property \"icon_large\"")

        # Icon (small)
        if "icon_small" in presentation_json:
            struct.icon_small = presentation_json["icon_small"]

        # Colors
        if not "colors" in presentation_json:
            raise Exception("Missing required property \"colors\"")

        colors:Any = presentation_json["colors"]
        if not (isinstance(colors, list) and len(colors) == 2):
            raise Exception("\"colors\" property must be an array with two elements")

        struct.color1 = DsonColor(colors[0])
        struct.color2 = DsonColor(colors[1])

        return struct
