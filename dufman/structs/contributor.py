# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from dataclasses import dataclass
from typing import Self

@dataclass
class DsonContributor:
    """Identifies the person or entity that created a Daz Studio asset."""

    author      : str   = None
    email       : str   = None
    website     : str   = None

    @staticmethod
    def load(asset_json:dict) -> Self:
        """Factory method to validate the creation of Contributor objects."""

        struct:Self = DsonContributor()

        # Author
        if "author" in asset_json:
            struct.author = asset_json["author"]
        else:
            raise ValueError("Missing required property \"author\"")

        # Email
        if "email" in asset_json:
            struct.email = asset_json["email"]

        # Website
        if "website" in asset_json:
            struct.website = asset_json["website"]

        return struct
