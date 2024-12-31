# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from dataclasses import dataclass
from typing import Self

from dufman.structs.contributor import DsonContributor

@dataclass
class DsonAssetInfo:
    """Header data about the creation of a Daz Studio asset."""

    # TODO: Convert modified to use Python's datetime?

    asset_id        : str               = None
    asset_type      : str               = None
    contributor     : DsonContributor   = None
    revision        : str               = "1.0"
    modified        : str               = None

    @staticmethod
    def load(info_json:dict) -> Self:
        """Factory method to create and validate AssetInfo object."""

        struct:Self = DsonAssetInfo()

        # "ID"
        if "id" in info_json:
            struct.asset_id = info_json["id"]
        else:
            raise ValueError("Missing required property \"id\"")

        # "type"
        if "type" in info_json:
            struct.asset_type = info_json["type"]

        # "Contributor"
        if "contributor" in info_json:
            struct.contributor = DsonContributor.load(info_json["contributor"])
        else:
            raise ValueError("Missing required property \"contributor\"")

        # "Revision"
        if "revision" in info_json:
            struct.revision = info_json["revision"]
        else:
            raise ValueError("Missing required property \"revision\"")

        # "Modified"
        if "modified" in info_json:
            struct.modified = info_json["modified"]

        return struct
