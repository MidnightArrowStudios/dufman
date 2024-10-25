# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""Defines a wrapper struct for the DSON format's Modifier object."""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

# pylint: disable=E0402
from ..datatypes import DsonSkinBinding, DsonMorph

# ============================================================================ #
#                                                                              #
# ============================================================================ #

@dataclass
class DsonModifier:
    """Struct-like object that encapsulates modifier data from a DSON file."""

    dsf_file                    : Path              = None
    library_id                  : str               = None
    instance_id                 : str               = None

    content_type                : str               = None

    library_parent              : str               = None
    instance_parent             : str               = None

    skin_binding                : DsonSkinBinding   = None
    morph                       : DsonMorph         = None

    has_formulas                : bool              = False
    formula_list                : list              = None

# ============================================================================ #
