# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

# python stdlib
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from dufman.enums import EdgeInterpolation, GeometryType, LibraryType
from dufman.file import check_path
from dufman.library import get_asset_json_from_library
from dufman.observers import _geometry_struct_created

from dufman.structs.graft import DsonGraft
from dufman.structs.region import DsonRegion
from dufman.structs.rigidity import DsonRigidity

from dufman.types import DsonVector, DsonPolygon


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


    # ======================================================================== #

    @staticmethod
    def load(dsf_filepath:Path, geometry_json:dict=None) -> Self:

        # Ensure type safety
        dsf_filepath = check_path(dsf_filepath)

        # Load DSON data from disk if it wasn't passed in.
        if not geometry_json:
            geometry_json = get_asset_json_from_library(dsf_filepath, LibraryType.GEOMETRY)

        # TODO: Validate mandatory properties

        struct:Self = DsonGeometry()
        struct.dsf_file = dsf_filepath

        # ID
        if "id" in geometry_json:
            struct.library_id = geometry_json["id"]
        else:
            raise ValueError("Missing required property \"id\"")

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
        _geometry_struct_created(struct, geometry_json)

        return struct


    # ======================================================================== #

    @staticmethod
    def save(struct:Self) -> dict:

        geometry_json:dict = {}

        # ID
        if struct.library_id:
            geometry_json["id"] = struct.library_id
        else:
            raise ValueError("DsonGeometry struct has no asset ID.")

        # Name
        if struct.name:
            geometry_json["name"] = struct.name

        # Label
        if struct.label:
            geometry_json["label"] = struct.label

        # Type
        if struct.geometry_type:
            geometry_json["type"] = struct.geometry_type.value

        # Source
        if struct.source:
            geometry_json["source"] = struct.source

        # Edge interpolation
        if struct.edge_interpolation:
            geometry_json["edge_interpolation_mode"] = struct.edge_interpolation.value

        # -------------------------------------------------------------------- #
        # Vertices
        if not struct.vertices:
            raise ValueError("DsonGeometry struct has no vertices.")

        vertex_dict:dict = {
            "count": len(struct.vertices),
            "values": [],
        }

        for vertex in struct.vertices:
            vertex_dict["values"].append(list(vertex))

        geometry_json["vertices"] = vertex_dict

        # -------------------------------------------------------------------- #
        # Polygons
        if not struct.face_group_indices:
            raise ValueError("DsonGeometry struct has no face group indices.")
        if not struct.material_indices:
            raise ValueError("DsonGeometry struct has no material indices.")
        if not struct.polygons:
            raise ValueError("DsonGeometry struct has no polygons.")

        polylist_dict:dict = {
            "count": len(struct.polygons),
            "values": [],
        }

        for (index, polygon) in enumerate(struct.polygons):
            fg:int = struct.face_group_indices[index]
            mi:int = struct.material_indices[index]
            polylist_dict["values"].append([ fg, mi, *polygon ])

        geometry_json["polylist"] = polylist_dict

        # -------------------------------------------------------------------- #
        # Face group names
        if not struct.face_group_names:
            raise ValueError("DsonGeometry struct has no face group names.")

        fg_dict:dict = {
            "count": len(struct.face_group_names),
            "values": [],
        }

        for fg_name in struct.face_group_names:
            fg_dict["values"].append(fg_name)

        geometry_json["polygon_groups"] = fg_dict

        # -------------------------------------------------------------------- #
        # Material surface names
        if not struct.material_names:
            raise ValueError("DsonGeometry struct has no material names.")

        mat_dict:dict = {
            "count": len(struct.material_names),
            "values": [],
        }

        for mat_name in struct.material_names:
            mat_dict["values"].append(mat_name)

        geometry_json["polygon_material_groups"] = mat_dict

        # -------------------------------------------------------------------- #

        # Default UV Set
        if struct.default_uv_set:
            geometry_json["default_uv_set"] = struct.default_uv_set

        # TODO: Add region, graft, and rigidity once structs are implemented.

        return geometry_json


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
