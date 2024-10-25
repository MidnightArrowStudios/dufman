# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""Defines a wrapper struct for the DSON format's UVSet object."""


from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path


# ============================================================================ #
#                                                                              #
# ============================================================================ #

@dataclass
class DsonUVSet:
    """Struct-like object that encapsulates UV Set data from a DSON file."""

    dsf_file                    : Path              = None
    library_id                  : str               = None
    instance_id                 : str               = None

    name                        : str               = ""
    label                       : str               = ""
    source                      : str               = ""

    # TODO: Custom datatypes?
    expected_vertices           : int               = None
    uv_coordinates              : list[list[int]]   = None
    hotswap                     : dict              = None


    def hotswap_polygon(self:DsonUVSet, index:int, face_indices:list[int]) -> list[int]:
        """Swaps a face's vertex indices so they can index into a UVSet's UV array."""

        if not index in self.hotswap:
            return None

        # ==================================================================== #
        # The DSON format's UV handling is weird. For reference, we'll use
        #   Stonemason's Urban Sprawl 3 asset "us03Bldg09" for demonstation.
        # ==================================================================== #

        # Each face has a list of vertices that make it up. This creates a copy
        #   of their indices. For us03Bldg09, face #587 is [ 922, 934, 924 ].
        copied_indices:list[int] = list(face_indices)


        # Daz Studio allows a face to use the same index multiple times,
        #   but Blender does not. These duplicates are culled when geometry
        #   is built, but a UV Set may still contain multiple entries for
        #   one vertex. The following code will cull them to prevent errors.
        # "/Environments/Architecture/Polish/College Classroom/College Classroom Complete Scene.duf"
        all_hotswaps:list[int] = []
        for hotswap_entry in self.hotswap[index]:
            if not hotswap_entry in all_hotswaps:
                all_hotswaps.append(hotswap_entry)


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

        for hotswap_entry in all_hotswaps:
            index_to_swap:int = hotswap_entry[1]
            replacement_index:int = hotswap_entry[2]

            if index_to_swap in copied_indices:
                position:int = copied_indices.index(index_to_swap)
                copied_indices[position] = replacement_index
            else:
                # TODO: Exception?
                pass

        return copied_indices

# ============================================================================ #
