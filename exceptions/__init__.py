# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
""" Custom exception library for working with DSON files."""

from __future__ import annotations
from typing import Any

# ============================================================================ #
#                                                                              #
# ============================================================================ #

class IncorrectArgument(Exception):
    """Raised when the argument to a function is the wrong datatype."""


class LibraryNotFound(Exception):
    """Raised when a DSF file does not have the requested data library."""


class MissingRequiredProperty(Exception):
    """Raised when a DSF file is missing a property the DSON specs say is required."""

    def __init__(self:MissingRequiredProperty, dsf_filepath:str, property_name:str) -> None:
        self.dsf_filepath = dsf_filepath
        self.property_name = property_name
        return

    def __str__(self:MissingRequiredProperty) -> str:
        return f"DSF file \"{ self.dsf_filepath }\" missing \"{ self.property_name }\""


class MultipleDsfFiles(Exception):
    """Raised when an identical path is found in multiple content directories."""


class NotDsfFile(Exception):
    """Raised when a URL does not have a \".dsf\" file extension."""
