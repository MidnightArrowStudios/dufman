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


class MultipleDsfFiles(Exception):
    """Raised when an identical path is found in multiple content directories."""


class NotDsfFile(Exception):
    """Raised when a URL does not have a \".dsf\" file extension."""
