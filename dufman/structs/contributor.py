# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

"""Defines a struct to encapsulate DSON's "contributor" data type.

http://docs.daz3d.com/doku.php/public/dson_spec/object_definitions/contributor/start
"""

# stdlib
from dataclasses import dataclass
from typing import Self


# ============================================================================ #
# DsonContributor struct                                                       #
# ============================================================================ #

@dataclass
class DsonContributor:
    """Identifies the person or entity that created a Daz Studio asset."""

    author      : str   = None
    email       : str   = None
    website     : str   = None


    # ======================================================================== #

    @staticmethod
    def load_from_dson(contributor_dson:dict) -> Self:
        """Factory method to validate the creation of Contributor objects."""

        if not contributor_dson:
            return

        if not isinstance(contributor_dson, dict):
            raise TypeError

        struct:Self = DsonContributor()

        # -------------------------------------------------------------------- #

        # Author
        if "author" in contributor_dson:
            struct.author = contributor_dson["author"]
        else:
            raise ValueError("Missing required property \"author\"")

        # Email
        if "email" in contributor_dson:
            struct.email = contributor_dson["email"]

        # Website
        if "website" in contributor_dson:
            struct.website = contributor_dson["website"]

        # -------------------------------------------------------------------- #

        return struct
