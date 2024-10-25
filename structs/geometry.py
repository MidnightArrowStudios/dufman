# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""Defines a wrapper struct for the DSON format's Geometry object."""


from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

from ..datatypes import DsonVector, DsonPolygon
from ..enums import EdgeInterpolation, GeometryType

from .uv_set import DsonUVSet


# ============================================================================ #
#                                                                              #
# ============================================================================ #

@dataclass
class DsonGeometry:
    """Struct-like object that encapsulates geometry data from a DSON file."""

    dsf_file                : Path              = None
    library_id              : str               = None
    instance_id             : str               = None

    name                    : str               = None
    label                   : str               = None
    source                  : str               = ""

    geometry_type           : GeometryType      = GeometryType.POLYGON_MESH
    edge_interpolation      : EdgeInterpolation = EdgeInterpolation.NO_INTERPOLATION

    vertices                : list[DsonVector]  = None
    polygons                : list[DsonPolygon] = None

    material_indices        : list[int]         = None
    material_names          : list[str]         = None
    facegroup_indices       : list[int]         = None
    facegroup_names         : list[str]         = None

    default_uv_url          : str               = None
    default_uv_set          : DsonUVSet         = None

# ============================================================================ #
