# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from __future__ import annotations
from typing import Any, Iterator


class DsonVector:
    """A wrapper for three floats which define a 3D coordinate."""

    def __init__(self:DsonVector, *arguments) -> None:

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

    def __iter__(self:DsonVector) -> Iterator:
        return iter([ self.x, self.y, self.z ])

    def __str__(self:DsonVector) -> str:
        return f"DsonVector({self.x}, {self.y}, {self.z})"
