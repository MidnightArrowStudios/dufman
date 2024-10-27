# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""Defines a wrapper struct for the DSON format's Node object."""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

# pylint: disable=E0402
from ..datatypes import DsonChannelVector
from ..enums import NodeType, RotationOrder

# ============================================================================ #
#                                                                              #
# ============================================================================ #

@dataclass
class DsonNode:
    """Struct-like object that encapsulates node data from a DSON file."""

    dsf_file                : Path                  = None
    library_id              : str                   = None
    instance_id             : str                   = None

    name                    : str                   = None
    label                   : str                   = None
    source                  : str                   = ""

    node_type               : NodeType              = NodeType.NODE
    content_type            : str                   = None

    parent                  : str                   = None
    inherits_scale          : bool                  = True

    center_point            : DsonChannelVector     = None
    end_point               : DsonChannelVector     = None
    translation             : DsonChannelVector     = None

    rotation_order          : RotationOrder         = RotationOrder.XYZ
    orientation             : DsonChannelVector     = None
    rotation                : DsonChannelVector     = None

    scale                   : DsonChannelVector     = None
    general_scale           : float                 = 1.0

# ============================================================================ #
