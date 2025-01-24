# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

"""Defines a struct which encapsulates DSON's "modifier" datatype.

http://docs.daz3d.com/doku.php/public/dson_spec/object_definitions/modifier/start
"""

# stdlib
from dataclasses import dataclass
from typing import Self

# dufman
from dufman.enums import LibraryType
from dufman.observers import _modifier_struct_created

from dufman.structs.channel import DsonChannel
from dufman.structs.formula import DsonFormula
from dufman.structs.morph import DsonMorph
from dufman.structs.presentation import DsonPresentation
from dufman.structs.skin_binding import DsonSkinBinding
from dufman.url import DazUrl


# ============================================================================ #
# DsonModifier struct                                                          #
# ============================================================================ #

@dataclass
class DsonModifier:

    dsf_file                : str                   = None
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


    # ======================================================================== #

    @staticmethod
    def load_from_dson(modifier_dson:dict) -> Self:

        if not modifier_dson:
            return None

        if not isinstance(modifier_dson, dict):
            raise TypeError

        struct:DsonModifier = DsonModifier()

        # -------------------------------------------------------------------- #

        # ID
        if "id" in modifier_dson:
            struct.library_id = modifier_dson["id"]
        else:
            raise ValueError("Missing required property \"ID\"")

        # Name
        if "name" in modifier_dson:
            struct.name = modifier_dson["name"]

        # Label
        if "label" in modifier_dson:
            struct.label = modifier_dson["label"]

        # Source
        if "source" in modifier_dson:
            struct.source = modifier_dson["source"]

        # Parent
        if "parent" in modifier_dson:
            struct.parent = modifier_dson["parent"]

        # Presentation
        if "presentation" in modifier_dson:
            struct.presentation = DsonPresentation.load_from_dson(modifier_dson["presentation"])

        # Channel
        if "channel" in modifier_dson:
            struct.channel = DsonChannel.load_from_dson(modifier_dson["channel"])

        # Region
        if "region" in modifier_dson:
            struct.region = modifier_dson["region"]

        # Group
        if "group" in modifier_dson:
            struct.group = modifier_dson["group"]

        # Formulas
        if "formulas" in modifier_dson:
            struct.formulas = DsonFormula.load_from_dson(modifier_dson["formulas"])

        # Morph
        if "morph" in modifier_dson:
            struct.morph = DsonMorph.load_from_dson(modifier_dson["morph"])

        # Skin binding
        if "skin" in modifier_dson:
            struct.skin_binding = DsonSkinBinding.load_from_dson(modifier_dson["skin"])

        # -------------------------------------------------------------------- #

        return struct


    # ------------------------------------------------------------------------ #

    @staticmethod
    def load_from_file(daz_url:DazUrl) -> Self:

        modifier_dson, _ = daz_url.get_asset_dson(LibraryType.MODIFIER)

        struct:Self = DsonModifier.load_from_dson(modifier_dson)
        struct.dsf_file = daz_url.get_url_to_asset()

        # Fire observer update.
        _modifier_struct_created(struct, modifier_dson)

        return struct
