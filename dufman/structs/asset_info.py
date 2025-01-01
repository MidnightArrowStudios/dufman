# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

"""Defines a struct which encapsulates DSON's "asset_info" datatype.

http://docs.daz3d.com/doku.php/public/dson_spec/object_definitions/asset_info/start
"""

# stdlib
from dataclasses import dataclass
from typing import Self

# dufman
from dufman.structs.contributor import DsonContributor


# ============================================================================ #
# DsonAssetInfo struct                                                         #
# ============================================================================ #

@dataclass
class DsonAssetInfo:
    """Header data about the creation of a Daz Studio asset."""

    # TODO: Convert modified to use Python's datetime?

    asset_id        : str               = None
    asset_type      : str               = None
    contributor     : DsonContributor   = None
    revision        : str               = "1.0"
    modified        : str               = None


    # ======================================================================== #

    @staticmethod
    def load_from_dson(asset_info_dson:dict) -> Self:
        """Factory method to create and validate AssetInfo object."""

        if not asset_info_dson:
            return None

        if not isinstance(asset_info_dson, dict):
            raise TypeError

        struct:Self = DsonAssetInfo()

        # -------------------------------------------------------------------- #

        # "ID"
        if "id" in asset_info_dson:
            struct.asset_id = asset_info_dson["id"]
        else:
            raise ValueError("Missing required property \"id\"")

        # "type"
        if "type" in asset_info_dson:
            struct.asset_type = asset_info_dson["type"]

        # "Contributor"
        if "contributor" in asset_info_dson:
            struct.contributor = DsonContributor.load_from_dson(asset_info_dson["contributor"])
        else:
            raise ValueError("Missing required property \"contributor\"")

        # "Revision"
        if "revision" in asset_info_dson:
            struct.revision = asset_info_dson["revision"]
        else:
            raise ValueError("Missing required property \"revision\"")

        # "Modified"
        if "modified" in asset_info_dson:
            struct.modified = asset_info_dson["modified"]

        # -------------------------------------------------------------------- #

        return struct
