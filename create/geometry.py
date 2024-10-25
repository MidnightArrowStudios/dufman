# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""Functions to instantiate a DsonGeometry object."""

from pathlib import Path

from ..datatypes import DsonPolygon, DsonVector
from ..enums import EdgeInterpolation, GeometryType
from ..exceptions import MissingRequiredProperty
from ..library import get_asset_data_from_library
from ..observers import _geometry_struct_created
from ..structs.geometry import DsonGeometry
from ..structs.uv_set import DsonUVSet
from ..url import AssetURL, parse_url_string
from ..utilities import check_path

from .uv_set import create_uv_set_struct

# ============================================================================ #
#                                                                              #
# ============================================================================ #

def create_geometry_struct(dsf_filepath:Path, instance_data:dict=None) -> DsonGeometry:
    """Parses a DSON geometry dictionary into a DsonGeometry wrapper struct."""

    # Ensure type safety
    dsf_filepath = check_path(dsf_filepath)

    # Load the DSON dictionary from disk
    library_data:dict = get_asset_data_from_library(dsf_filepath, "geometry_library")

    # ======================================================================== #

    if not "id" in library_data:
        raise MissingRequiredProperty(str(dsf_filepath), "id")

    if not "vertices" in library_data:
        raise MissingRequiredProperty(str(dsf_filepath), "vertices")

    if not "polylist" in library_data:
        raise MissingRequiredProperty(str(dsf_filepath), "polylist")

    if not "polygon_groups" in library_data:
        raise MissingRequiredProperty(str(dsf_filepath), "polygon_groups")

    if not "polygon_material_groups" in library_data:
        raise MissingRequiredProperty(str(dsf_filepath), "polygon_material_groups")

    # TODO: Check instance properties

    # ======================================================================== #

    struct:DsonGeometry = DsonGeometry()

    asset_url:AssetURL = parse_url_string(str(dsf_filepath))
    struct.dsf_file = Path(asset_url.file_path)
    struct.library_id = library_data["id"]
    struct.instance_id = instance_data["id"] if instance_data else None

    # ======================================================================== #

    # Name
    if "name" in library_data:
        struct.name = library_data["name"]
    if instance_data and "name" in instance_data:
        struct.name = instance_data["name"]

    # Label
    if "label" in library_data:
        struct.label = library_data["label"]
    if instance_data and "label" in instance_data:
        struct.label = instance_data["label"]

    # Source
    if "source" in library_data:
        struct.source = library_data["source"]
    if instance_data and "source" in instance_data:
        struct.source = instance_data["source"]

    # Geometry type
    if "type" in library_data:
        struct.geometry_type = GeometryType(library_data["type"])
    if instance_data and "type" in instance_data:
        struct.geometry_type = GeometryType(instance_data["type"])

    # Edge interpolation
    if "edge_interpolation_mode" in library_data:
        struct.edge_interpolation = EdgeInterpolation(library_data["edge_interpolation_mode"])
    if instance_data and "edge_interpolation_mode" in instance_data:
        struct.edge_interpolation = EdgeInterpolation(instance_data["edge_interpolation_mode"])

    # Vertices
    vertex_data:list = library_data["vertices"]["values"]
    if instance_data and "vertices" in instance_data:
        vertex_data = instance_data["vertices"]["values"]

    struct.vertices = [ DsonVector.create(vertex) for vertex in vertex_data ]

    # Polygons
    polygon_data:list = library_data["polylist"]["values"]
    if instance_data and "polylist" in instance_data:
        polygon_data = instance_data["polylist"]["values"]

    struct.polygons = []
    struct.material_indices = []
    struct.facegroup_indices = []

    for polygon in polygon_data:
        struct.polygons.append( DsonPolygon.create(polygon[2:]) )
        struct.material_indices.append( polygon[1] )
        struct.facegroup_indices.append( polygon[0] )

    # Material names
    material_names:list = library_data["polygon_material_groups"]["values"]
    if instance_data and "polygon_material_groups" in instance_data:
        material_names = instance_data["polygon_material_groups"]["values"]

    struct.material_names = list(material_names)

    # Face group names
    facegroup_names:list = library_data["polygon_groups"]["values"]
    if instance_data and "polygon_groups" in instance_data:
        facegroup_names = instance_data["polygon_groups"]["values"]

    struct.facegroup_names = list(facegroup_names)

    # Default UV Set
    uv_url:str = None
    if "default_uv_set" in library_data:
        uv_url = library_data["default_uv_set"]
    if instance_data and "default_uv_set" in instance_data:
        uv_url = instance_data["default_uv_set"]

    uv_struct:DsonUVSet = None
    if uv_url:
        uv_struct = create_uv_set_struct(uv_url)

    struct.default_uv_url = uv_url
    struct.default_uv_set = uv_struct

    # ======================================================================== #

    _geometry_struct_created(struct, library_data, instance_data)

    return struct
