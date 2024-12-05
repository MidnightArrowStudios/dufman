# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from __future__ import annotations
from dataclasses import dataclass

@dataclass
class DsonContributor:
    """Identifies the person or entity that created a Daz Studio asset."""

    author      : str   = None
    email       : str   = None
    website     : str   = None

    @classmethod
    def load(cls:type, asset_json:dict) -> DsonContributor:
        """Factory method to validate the creation of Contributor objects."""

        struct:DsonContributor = cls()

        # Author
        if "author" in asset_json:
            struct.author = asset_json["author"]
        else:
            raise Exception("Missing required property \"author\"")

        # Email
        if "email" in asset_json:
            struct.email = asset_json["email"]

        # Website
        if "website" in asset_json:
            struct.website = asset_json["website"]

        return struct
