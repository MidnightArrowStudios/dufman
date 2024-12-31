# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""Custom exception library for working with DSON files."""


# ============================================================================ #
#                                                                              #
# ============================================================================ #

class ChannelCannotBeClamped(TypeError):
    """Raised when a channel does not support clamping, minimum, or maximum."""


class LibraryNotFound(Exception):
    """Raised when a DSF file does not have the requested data library."""


class MultipleDsfFiles(Exception):
    """Raised when an identical path is found in multiple content directories."""


class NotDsfFile(Exception):
    """Raised when a URL does not have a \".dsf\" file extension."""


class SceneMissing(Exception):
    """Raised when a DSON file does not have a \"scene\" property."""
