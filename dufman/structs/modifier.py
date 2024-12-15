# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

from .. import observers

from ..file import check_path
from ..library import get_asset_json_from_library

from .channel import DsonChannel
from .formula import DsonFormula
from .morph import DsonMorph
from .presentation import DsonPresentation
from .skin_binding import DsonSkinBinding


# ============================================================================ #
#                                                                              #
# ============================================================================ #

@dataclass
class DsonModifier:

    dsf_file                : Path                  = None
    library_id              : str                   = None

    name                    : str                   = ""
    label                   : str                   = None
    source                  : str                   = ""

    parent                  : str                   = None

    presentation            : DsonPresentation      = None
    channel                 : DsonChannel           = None
    region                  : str                   = None
    group                   : str                   = "/"

    formulas                : list[DsonFormula]     = None

    morph                   : DsonMorph             = None
    skin_binding            : DsonSkinBinding       = None


    @classmethod
    def load(cls:type, dsf_filepath:Path) -> DsonModifier:

        # Ensure type safety
        dsf_filepath = check_path(dsf_filepath)

        # Load DSON data from disk
        modifier_json:dict = get_asset_json_from_library(dsf_filepath, "modifier_library")

        struct:DsonModifier = cls()
        struct.dsf_file = dsf_filepath

        # ID
        if "id" in modifier_json:
            struct.library_id = modifier_json["id"]
        else:
            raise Exception("Missing required property \"ID\"")

        # Name
        if "name" in modifier_json:
            struct.name = modifier_json["name"]

        # Label
        if "label" in modifier_json:
            struct.label = modifier_json["label"]

        # Source
        if "source" in modifier_json:
            struct.source = modifier_json["source"]

        # Parent
        if "parent" in modifier_json:
            struct.parent = modifier_json["parent"]

        # Presentation
        if "presentation" in modifier_json:
            struct.presentation = DsonPresentation.load(modifier_json["presentation"])

        # Channel
        if "channel" in modifier_json:
            struct.channel = DsonChannel.load(modifier_json["channel"])

        # Region
        if "region" in modifier_json:
            struct.region = modifier_json["region"]

        # Group
        if "group" in modifier_json:
            struct.group = modifier_json["group"]

        # Formulas
        if "formulas" in modifier_json:
            struct.formulas = DsonFormula.load(modifier_json["formulas"])

        # Morph
        if "morph" in modifier_json:
            struct.morph = DsonMorph.load(modifier_json["morph"])

        # Skin binding
        if "skin" in modifier_json:
            struct.skin_binding = DsonSkinBinding.load(modifier_json["skin"])

        # Fire observer update.
        observers._modifier_struct_created(struct, modifier_json)

        return struct
