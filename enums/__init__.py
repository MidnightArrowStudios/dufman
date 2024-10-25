# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""Defines native Enum types for string-based enums found in DSON files."""

from enum import Enum

# ============================================================================ #

class EdgeInterpolation(Enum):
    """How subdivision surface should affect a mesh."""
    NO_INTERPOLATION = "no_interpolation"
    EDGES_AND_CORNERS = "edges_and_corners"
    EDGES_ONLY = "edges_only"

class GeometryType(Enum):
    """Whether a mesh should have a SubSurf modifier applied."""
    POLYGON_MESH = "polygon_mesh"
    SUBDIVISION_SURFACE = "subdivision_surface"

class NodeType(Enum):
    """What kind of node-object should be added to the scene."""
    NODE    = "node"
    BONE    = "bone"
    FIGURE  = "figure"
    CAMERA  = "camera"
    LIGHT   = "light"

class RotationOrder(Enum):
    """What order to apply Euler rotations in."""
    XYZ     = "XYZ"
    XZY     = "XZY"
    YXZ     = "YXZ"
    YZX     = "YZX"
    ZXY     = "ZXY"
    ZYX     = "ZYX"

# ============================================================================ #
