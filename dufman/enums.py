# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""Defines native Enum types for string-based enums found in DSON files."""

from enum import Enum


# ============================================================================ #
#                                                                              #
# ============================================================================ #

class ChannelType(Enum):
    """What kind of data a channel stores."""
    ALIAS           = "alias"
    BOOL            = "bool"
    COLOR           = "color"
    ENUM            = "enum"
    FLOAT           = "float"
    IMAGE           = "image"
    INT             = "int"
    STRING          = "string"


class EdgeInterpolation(Enum):
    """How subdivision surface should affect a mesh."""
    NO_INTERPOLATION = "no_interpolation"
    EDGES_AND_CORNERS = "edges_and_corners"
    EDGES_ONLY = "edges_only"


class FormulaOperator(Enum):
    """Which operation to perform on a formula's inputs."""
    PUSH            = "push"
    ADD             = "add"
    SUB             = "sub"
    MULT            = "mult"
    DIV             = "div"
    INV             = "inv"
    NEG             = "neg"
    SPL_LINEAR      = "spline_linear"
    SPL_CONSTANT    = "spline_constant"
    SPL_TCB         = "spline_tcb"


class FormulaStage(Enum):
    """How a formula contributes to a final value."""
    MULTIPLY = "multiply"
    SUM = "sum"


class GeometryType(Enum):
    """Whether a mesh should have a SubSurf modifier applied."""
    POLYGON_MESH = "polygon_mesh"
    SUBDIVISION_SURFACE = "subdivision_surface"


class LibraryType(Enum):
    """What kind of asset library a DSON dictionary belongs to."""
    GEOMETRY = "geometry_library"
    IMAGE = "image_library"
    MATERIAL = "material_library"
    MODIFIER = "modifier_library"
    NODE = "node_library"
    UV_SET = "uv_set_library"


class NodeType(Enum):
    """What kind of node-object should be added to the scene."""
    NODE    = "node"
    BONE    = "bone"
    FIGURE  = "figure"
    CAMERA  = "camera"
    LIGHT   = "light"


class RigidRotation(Enum):
    NONE        = "none"
    FULL        = "full"
    PRIMARY     = "primary"
    SECONDARY   = "secondary"


class RigidScale(Enum):
    NONE        = "none"
    PRIMARY     = "primary"
    SECONDARY   = "secondary"
    TERTIARY    = "tertiary"


class RotationOrder(Enum):
    """What order to apply Euler rotations in."""
    XYZ     = "XYZ"
    XZY     = "XZY"
    YXZ     = "YXZ"
    YZX     = "YZX"
    ZXY     = "ZXY"
    ZYX     = "ZYX"


# ============================================================================ #
