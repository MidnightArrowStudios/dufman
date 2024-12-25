# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from __future__ import annotations
from typing import Any, Iterator


class DsonColor:
    """A wrapper for three floats which define a color."""

    def __init__(self:DsonColor, *arguments) -> None:

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

    def __iter__(self:DsonColor) -> Iterator:
        return iter([ self.r, self.g, self.b ])
