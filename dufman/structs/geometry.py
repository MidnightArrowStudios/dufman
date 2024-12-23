# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

from .. import observers

from ..datatypes.vector import DsonVector
from ..datatypes.polygon import DsonPolygon
from ..enums import EdgeInterpolation, GeometryType, LibraryType
from ..file import check_path
from ..library import get_asset_json_from_library

from .graft import DsonGraft
from .region import DsonRegion
from .rigidity import DsonRigidity


# ============================================================================ #
#                                                                              #
# ============================================================================ #

@dataclass
class DsonGeometry:

    dsf_file                : Path                  = None
    library_id              : str                   = None

    name                    : str                   = None
    label                   : str                   = None
    source                  : str                   = ""

    geometry_type           : GeometryType          = GeometryType.POLYGON_MESH
    edge_interpolation      : EdgeInterpolation     = EdgeInterpolation.NO_INTERPOLATION

    vertices                : list[DsonVector]      = None
    polygons                : list[DsonPolygon]     = None

    material_indices        : list[int]             = None
    material_names          : list[str]             = None

    face_group_indices      : list[int]             = None
    face_group_names        : list[str]             = None

    default_uv_set          : str                   = None

    regions                 : list[DsonRegion]      = None
    graft                   : DsonGraft             = None
    rigidity                : DsonRigidity          = None


    @classmethod
    def load(cls:type, dsf_filepath:Path, geometry_json:dict=None) -> DsonGeometry:

        # Ensure type safety
        dsf_filepath = check_path(dsf_filepath)

        # Load DSON data from disk if it wasn't passed in.
        if not geometry_json:
            geometry_json = get_asset_json_from_library(dsf_filepath, LibraryType.GEOMETRY)

        # TODO: Validate mandatory properties

        struct:DsonGeometry = cls()
        struct.dsf_file = dsf_filepath

        # ID
        if "id" in geometry_json:
            struct.library_id = geometry_json["id"]
        else:
            raise Exception("Missing required property \"id\"")

        # Name
        if "name" in geometry_json:
            struct.name = geometry_json["name"]

        # Label
        if "label" in geometry_json:
            struct.label = geometry_json["label"]

        # Type
        if "type" in geometry_json:
            struct.geometry_type = GeometryType(geometry_json["type"])

        # Source
        if "source" in geometry_json:
            struct.source = geometry_json["source"]

        # Edge interpolation mode
        if "edge_interpolation_mode" in geometry_json:
            struct.edge_interpolation = EdgeInterpolation(geometry_json["edge_interpolation_mode"])

        # Vertices - Polygons
        _geometry(struct, geometry_json)

        # Default UV Set
        if "default_uv_set" in geometry_json:
            struct.default_uv_set = geometry_json["default_uv_set"]

        # Region
        if "root_region" in geometry_json:
            struct.regions = DsonRegion.load(geometry_json["root_region"])

        # Graft
        if "graft" in geometry_json:
            struct.graft = DsonGraft.load(geometry_json["graft"])

        # Rigidity
        if "rigidity" in geometry_json:
            struct.rigidity = DsonRigidity.load(geometry_json["rigidity"])

        # Fire observer update.
        observers._geometry_struct_created(struct, geometry_json)

        return struct


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def _geometry(struct:DsonGeometry, geometry_json:dict) -> None:

    # TODO: Add exceptions

    # Vertices
    vertex_list:list = None
    if geometry_json and "vertices" in geometry_json:
        vertex_list = geometry_json["vertices"]["values"]

    if vertex_list:
        struct.vertices = [ DsonVector(vertex) for vertex in vertex_list ]
    else:
        struct.vertices = []

    # Polygons
    polygon_list:list = None
    if geometry_json and "polylist" in geometry_json:
        polygon_list = geometry_json["polylist"]["values"]

    struct.polygons = []
    struct.material_indices = []
    struct.face_group_indices = []

    for polygon in (polygon_list if polygon_list else []):
        struct.polygons.append( DsonPolygon(polygon[2:]) )
        struct.material_indices.append(polygon[1])
        struct.face_group_indices.append(polygon[0])

    # Material names
    material_names:list[str] = None
    if geometry_json and "polygon_material_groups" in geometry_json:
        material_names = geometry_json["polygon_material_groups"]["values"]

    if material_names:
        struct.material_names = list(material_names)
    else:
        struct.material_names = []

    # Face group names
    face_group_names:list[str] = None
    if geometry_json and "polygon_groups" in geometry_json:
        face_group_names = geometry_json["polygon_groups"]["values"]

    if face_group_names:
        struct.face_group_names = list(face_group_names)
    else:
        struct.face_group_names = []

    return
