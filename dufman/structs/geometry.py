# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

"""Defines a struct which encapsulates DSON's "geometry" datatype.

http://docs.daz3d.com/doku.php/public/dson_spec/object_definitions/geometry/start
"""

# stdlib
from dataclasses import dataclass
from pathlib import Path
from typing import Self

# dufman
from dufman.enums import EdgeInterpolation, GeometryType, LibraryType
from dufman.observers import _geometry_struct_created

from dufman.structs.graft import DsonGraft
from dufman.structs.region import DsonRegion
from dufman.structs.rigidity import DsonRigidity

from dufman.types import DsonVector, DsonPolygon
from dufman.url import DazUrl


# ============================================================================ #
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
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
    # LOAD FROM DSON                                                           #
    # ======================================================================== #

    @staticmethod
    def load_from_dson(geometry_dson:dict) -> Self:

        if not geometry_dson:
            return None

        if not isinstance(geometry_dson, dict):
            raise TypeError

        struct:Self = DsonGeometry()

        # -------------------------------------------------------------------- #

        # ID
        if "id" in geometry_dson:
            struct.library_id = geometry_dson["id"]
        else:
            raise ValueError("Missing required property \"id\"")

        # Name
        if "name" in geometry_dson:
            struct.name = geometry_dson["name"]

        # Label
        if "label" in geometry_dson:
            struct.label = geometry_dson["label"]

        # Type
        if "type" in geometry_dson:
            struct.geometry_type = GeometryType(geometry_dson["type"])

        # Source
        if "source" in geometry_dson:
            struct.source = geometry_dson["source"]

        # Edge interpolation mode
        if "edge_interpolation_mode" in geometry_dson:
            struct.edge_interpolation = EdgeInterpolation(geometry_dson["edge_interpolation_mode"])

        # Vertices - Polygons
        _geometry(struct, geometry_dson)

        # Default UV Set
        if "default_uv_set" in geometry_dson:
            struct.default_uv_set = geometry_dson["default_uv_set"]

        # Region
        if "root_region" in geometry_dson:
            struct.regions = DsonRegion.load_from_dson(geometry_dson["root_region"])

        # Graft
        if "graft" in geometry_dson:
            struct.graft = DsonGraft.load_from_dson(geometry_dson["graft"])

        # Rigidity
        if "rigidity" in geometry_dson:
            struct.rigidity = DsonRigidity.load_from_dson(geometry_dson["rigidity"])

        # -------------------------------------------------------------------- #

        return struct


    # ======================================================================== #
    # LOAD FROM FILE                                                           #
    # ======================================================================== #

    @staticmethod
    def load_from_file(daz_url:DazUrl) -> Self:

        if not daz_url or not isinstance(daz_url, DazUrl):
            raise TypeError

        geometry_dson, _ = daz_url.get_asset_dson(LibraryType.GEOMETRY)

        struct:Self = DsonGeometry.load_from_dson(geometry_dson)
        struct.dsf_file = daz_url.get_url_to_asset()

        # Fire observer update.
        _geometry_struct_created(struct, geometry_dson)

        return struct


    # ======================================================================== #
    # SAVE TO DSON                                                             #
    # ======================================================================== #

    @staticmethod
    def save_to_dson(struct:Self) -> dict:

        geometry_dson:dict = {}

        # ID
        if struct.library_id:
            geometry_dson["id"] = struct.library_id
        else:
            raise ValueError("DsonGeometry struct has no asset ID.")

        # Name
        if struct.name:
            geometry_dson["name"] = struct.name

        # Label
        if struct.label:
            geometry_dson["label"] = struct.label

        # Type
        if struct.geometry_type:
            geometry_dson["type"] = struct.geometry_type.value

        # Source
        if struct.source:
            geometry_dson["source"] = struct.source

        # Edge interpolation
        if struct.edge_interpolation:
            geometry_dson["edge_interpolation_mode"] = struct.edge_interpolation.value

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

        geometry_dson["vertices"] = vertex_dict

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

        geometry_dson["polylist"] = polylist_dict

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

        geometry_dson["polygon_groups"] = fg_dict

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

        geometry_dson["polygon_material_groups"] = mat_dict

        # -------------------------------------------------------------------- #

        # Default UV Set
        if struct.default_uv_set:
            geometry_dson["default_uv_set"] = struct.default_uv_set

        # TODO: Add region, graft, and rigidity once structs are implemented.

        return geometry_dson


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def _geometry(struct:DsonGeometry, geometry_dson:dict) -> None:

    # TODO: Add exceptions

    # Vertices
    vertex_list:list = None
    if geometry_dson and "vertices" in geometry_dson:
        vertex_list = geometry_dson["vertices"]["values"]

    if vertex_list:
        struct.vertices = [ DsonVector(vertex) for vertex in vertex_list ]
    else:
        struct.vertices = []

    # Polygons
    polygon_list:list = None
    if geometry_dson and "polylist" in geometry_dson:
        polygon_list = geometry_dson["polylist"]["values"]

    struct.polygons = []
    struct.material_indices = []
    struct.face_group_indices = []

    for polygon in (polygon_list if polygon_list else []):
        struct.polygons.append( DsonPolygon(polygon[2:]) )
        struct.material_indices.append(polygon[1])
        struct.face_group_indices.append(polygon[0])

    # Material names
    material_names:list[str] = None
    if geometry_dson and "polygon_material_groups" in geometry_dson:
        material_names = geometry_dson["polygon_material_groups"]["values"]

    if material_names:
        struct.material_names = list(material_names)
    else:
        struct.material_names = []

    # Face group names
    face_group_names:list[str] = None
    if geometry_dson and "polygon_groups" in geometry_dson:
        face_group_names = geometry_dson["polygon_groups"]["values"]

    if face_group_names:
        struct.face_group_names = list(face_group_names)
    else:
        struct.face_group_names = []

    return
