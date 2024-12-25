# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

from dufman.enums import LibraryType
from dufman.file import check_path
from dufman.library import get_asset_json_from_library
from dufman.observers import _uv_set_struct_created


# ============================================================================ #
#                                                                              #
# ============================================================================ #

@dataclass
class DsonUVSet:

    dsf_file                    : Path                  = None
    library_id                  : str                   = None

    name                        : str                   = ""
    label                       : str                   = ""
    source                      : str                   = ""

    expected_vertices           : int                   = None
    uv_coordinates              : list[Coordinate]      = None
    hotswap_indices             : dict                  = None


    class Coordinate(NamedTuple):
        x:float
        y:float


    class Hotswap(NamedTuple):
        face_index:int
        original_vertex:int
        replacement_vertex:int


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    @classmethod
    def load(cls:type, dsf_filepath:Path, uv_set_json:dict=None) -> DsonUVSet:

        # Ensure type safety
        dsf_filepath:Path = check_path(dsf_filepath)

        # Load DSON data from disk if it wasn't passed in.
        if not uv_set_json:
            uv_set_json = get_asset_json_from_library(dsf_filepath, LibraryType.UV_SET)

        # TODO: Validate mandatory properties

        struct:DsonUVSet = cls()
        struct.dsf_file = dsf_filepath

        # ID
        if "id" in uv_set_json:
            struct.library_id = uv_set_json["id"]
        else:
            raise Exception("Missing required property \"id\"")

        # Name
        if "name" in uv_set_json:
            struct.name = uv_set_json["name"]

        # Label
        if "label" in uv_set_json:
            struct.label = uv_set_json["label"]

        # Source
        if "source" in uv_set_json:
            struct.source = uv_set_json["source"]

        # Expected vertices
        if "vertex_count" in uv_set_json:
            struct.expected_vertices = uv_set_json["vertex_count"]
        else:
            raise Exception("Missing required property \"vertex_count\"")

        # UV coordinates
        if "uvs" in uv_set_json:
            uv_values:list[dict] = uv_set_json["uvs"]["values"]
            struct.uv_coordinates = [ cls.Coordinate(x=entry[0], y=entry[1]) for entry in uv_values ]
        else:
            raise Exception("Missing required property \"uvs\"")

        # The hotswap data is stored in a DSON file as a flat list, with the
        #   first index indicating the polygon. This is inefficient for lookup
        #   purposes, so we convert the data to a dictionary with its poly
        #   index as the key.
        struct.hotswap_indices = {}
        if "polygon_vertex_indices" in uv_set_json:
            for entry in uv_set_json["polygon_vertex_indices"]:

                face_index:int = entry[0]

                # If key does not exist, create it.
                if not face_index in struct.hotswap_indices:
                    struct.hotswap_indices[face_index] = []

                struct.hotswap_indices[face_index].append(
                    cls.Hotswap(
                        face_index=face_index,
                        original_vertex=entry[1],
                        replacement_vertex=entry[2],
                    )
                )

        # Fire observer update.
        _uv_set_struct_created(struct, uv_set_json)

        return struct


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def hotswap(self:DsonUVSet, index:int, face_indices:list[int]) -> list[int]:
        """Swaps a face's vertex indices so they can index into a UVSet's UV array."""

        # ==================================================================== #
        # The DSON format's UV handling is weird. For reference, we'll use
        #   Stonemason's Urban Sprawl 3 asset "us03Bldg09" for demonstation.
        # ==================================================================== #

        # Each face has a list of vertices that make it up. This creates a copy
        #   of their indices. For us03Bldg09, face #587 is [ 922, 934, 924 ].
        copied_indices:list[int] = list(face_indices)

        # Nothing to hotswap, return original vertices.
        if not index in self.hotswap_indices:
            return copied_indices

        # Daz Studio allows a face to use the same index multiple times,
        #   but Blender does not. These duplicates are culled when geometry
        #   is built, but a UV Set may still contain multiple entries for
        #   one vertex. The following code will cull them to prevent errors.
        # "/Environments/Architecture/Polish/College Classroom/College Classroom Complete Scene.duf"
        all_hotswaps:list[self.Hotswap] = []
        for entry in self.hotswap_indices[index]:
            if not entry in all_hotswaps:
                all_hotswaps.append(entry)


        # ==================================================================== #
        # Each hotswap value contains:
        #   -A face index
        #   -An index of a vertex inside that face
        #   -A value to swap the vertex index in "vertex_indices" with
        #
        # For instance, using the following hotswap data for Face #587
        #   [ 587, 922, 6477 ]
        # we would take 922 and replace it with 6477. The new list would
        # then be
        #   [ 6477, 934, 924 ]
        # With the other two lists stored inside the dictionary, the vertex
        # indices are transformed into
        #   [ 6477, 6472, 6471 ]
        # These are the per-vertex indices into the self.uv_coordinates array.
        # ==================================================================== #

        for hotswap in all_hotswaps:

            if hotswap.original_vertex in copied_indices:
                position:int = copied_indices.index(hotswap.original_vertex)
                copied_indices[position] = hotswap.replacement_vertex
            else:
                # TODO: Exception?
                pass

        return copied_indices
