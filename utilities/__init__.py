# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""Helper methods for miscellaneous functions."""

from pathlib import Path
from urllib.parse import unquote

from ..exceptions import IncorrectArgument

# ============================================================================ #

def check_path(potential_path:Path) -> Path:
    """Validates function arguments that accept pathlib Paths."""

    if isinstance(potential_path, str):
        potential_path = Path(unquote(potential_path))

    if not isinstance(potential_path, Path):
        # pylint: disable=C0301
        message:str = f"Argument \"{repr(potential_path)}\" is not Path or string."
        raise IncorrectArgument(message)

    return potential_path
