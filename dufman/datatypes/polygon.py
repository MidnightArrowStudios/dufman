# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from __future__ import annotations
from typing import Any, Iterator


# ============================================================================ #
#                                                                              #
# ============================================================================ #

class DsonPolygon:
    """A wrapper for the vertex indices which constitute a mesh's face."""

    def __init__(self:DsonPolygon, *arguments) -> None:

        message:str = "DsonPolygon only accepts 3-4 integers, or a collection of 3-4 integers."

        values:list[Any] = []
        if len(arguments) == 1 and isinstance(arguments, (list, tuple)):
            values.extend(arguments[0])
        elif len(arguments) == 3:
            values.extend(arguments)
        else:
            raise ValueError(message)

        # Daz Studio faces can be triangles or quads.
        if not 3 <= len(values) <= 4:
            raise ValueError(message)

        self.vertex_indices:list[int] = []
        for value in values:
            try:
                self.vertex_indices.append(int(value))
            except ValueError as ve:
                raise Exception(message) from ve

        return None

    def __iter__(self:DsonPolygon) -> Iterator:

        # Duplicate indices will cause an error in BMesh, so we need to cull
        #   those out.
        result:list[int] = []
        for index in self.vertex_indices:
            if not index in result:
                result.append(index)

        # If there are less than 3 vertices after culling, the face will cause
        #   an error in BMesh, so return None to indicate the face should not
        #   be processed.
        if len(result) < 3:
            return None

        return iter(result)
