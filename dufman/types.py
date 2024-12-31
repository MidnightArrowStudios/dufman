# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from typing import Any, Iterator, Self


# ============================================================================ #
#                                                                              #
# ============================================================================ #

class DsonColor:
    """A wrapper for three floats which define a color."""

    def __init__(self:Self, *arguments) -> None:

        message:str = "DsonColor only accepts three floats or a collection of three floats."

        values:list[Any] = []
        if len(arguments) == 1 and isinstance(arguments[0], (list, tuple, set)):
            values.extend(arguments[0])
        elif len(arguments) == 3:
            values.extend(arguments)
        else:
            raise ValueError(message)

        if len(values) != 3:
            raise ValueError(message)

        for value in values:
            try:
                float(value)
            except ValueError as ve:
                raise ValueError(message) from ve

        self.r = values[0]
        self.g = values[1]
        self.b = values[2]

        return None

    def __iter__(self:Self) -> Iterator:
        return iter([ self.r, self.g, self.b ])


# ============================================================================ #
#                                                                              #
# ============================================================================ #

class DsonPolygon:
    """A wrapper for the vertex indices which constitute a mesh's face."""

    def __init__(self:Self, *arguments) -> None:

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

    def __iter__(self:Self) -> Iterator:

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


# ============================================================================ #
#                                                                              #
# ============================================================================ #

class DsonVector:
    """A wrapper for three floats which define a 3D coordinate."""

    def __init__(self:Self, *arguments) -> None:

        message:str = "DsonVector only accepts three floats, or a collection of three floats."

        values:list[Any] = []
        if len(arguments) == 1 and isinstance(arguments[0], (list, tuple)):
            values.extend(arguments[0])
        elif len(arguments) == 3:
            values.extend(arguments)
        else:
            raise ValueError(message)

        if len(values) != 3:
            raise ValueError(message)

        for value in values:
            try:
                float(value)
            except ValueError as ve:
                raise ValueError(message) from ve

        self.x = values[0]
        self.y = values[1]
        self.z = values[2]

        return

    def __iter__(self:Self) -> Iterator:
        return iter([ self.x, self.y, self.z ])

    def __str__(self:Self) -> str:
        return f"DsonVector({self.x}, {self.y}, {self.z})"
