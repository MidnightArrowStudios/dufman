# ============================================================================ #
"""Module containing functions to open DSON files using a Path-type URL value."""

import gzip
import json

from io import TextIOWrapper
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from .. import observers
from ..exceptions import IncorrectArgument, MultipleDsfFiles, NotDsfFile
from ..utilities import check_path

# pylint: disable=W0212

# ============================================================================ #
#                                                                              #
# ============================================================================ #

# According to the DSON standard, a DUF file cannot be accessed from any other
#   file since they are assumed to be "user-facing". Thus, they do not need to
#   be cached. However, DSF files may be opened potentially dozens of times to
#   extract assets, thus it is useful to keep those loaded.
# Assets are keyed by a Path object, which wraps the DSON-formatted relative
#   path, i.e. Path("/data/path/to/asset.dsf")
_dsf_cache:dict = {}

# List of all content directories that Daz assets have been installed to.
_content_directories:list[Path] = []

# ============================================================================ #
#                                                                              #
# ============================================================================ #

def add_content_directory(directory_path:Path) -> None:
    """Adds a filepath anchor to the internal array of valid content directories."""
    content_directory:Path = check_path(directory_path)
    if content_directory not in _content_directories:
        _content_directories.append(content_directory)
    return

# ============================================================================ #

def clear_dsf_cache() -> None: # pylint: disable=R1711
    """Removes all DSF files which have been cached, freeing up memory."""
    _dsf_cache.clear()
    return

# ============================================================================ #

def extract_single_property(dsf_filepath:Path, property_path:list[str]) -> Any:
    """Gets a single piece of data from a DSF file based on its path."""

    invalid:Exception = Exception("Property could not be retrieved. Ensure property_path is valid.")

    dsf_filepath = check_path(dsf_filepath)

    tokens:list[str] = list(property_path)
    dsf_pointer:Any = handle_dsf_file(dsf_filepath)

    while tokens:
        token = tokens.pop(0)

        if isinstance(dsf_pointer, dict):

            if not token in dsf_pointer:
                raise invalid

            dsf_pointer = dsf_pointer[token]
            continue

        elif isinstance(dsf_pointer, list):

            index:int = None

            try:
                index = int(token)
            except ValueError as ve:
                raise invalid from ve

            if not 0 <= index < len(dsf_pointer):
                raise IndexError

            dsf_pointer = dsf_pointer[index]
            continue

        else:
            raise invalid

    return dsf_pointer

# ============================================================================ #

def get_absolute_filepath(relative_path:Path) -> Path:
    """Converts a relative DSON path to an absolute path."""

    # Ensure type safety
    relative_path = check_path(relative_path)

    # Leading lashes interfere with pathlib, so strip them off.
    stripped:Path = relative_path.relative_to(relative_path.anchor)

    # Return value
    absolute_filepaths:list[Path] = []

    for directory in _content_directories:
        potential:Path = directory.joinpath(stripped)
        if potential.exists():
            absolute_filepaths.append(potential)

    count:int = len(absolute_filepaths)

    if count <= 0: # pylint: disable=R1720
        raise FileNotFoundError
    elif count == 1:
        return absolute_filepaths[0]
    else:
        raise MultipleDsfFiles

# ============================================================================ #

def get_absolute_filepaths_in_directory(relative_path:Path) -> list[Path]:
    """Takes a relative DSON directory path and extracts its absolute DSF paths."""

    # Ensure type safety
    relative_path = check_path(relative_path)

    absolute_path:Path = get_absolute_filepath(relative_path)

    filepaths:list[Path] = []

    for filepath in absolute_path.iterdir():
        if not filepath.suffix.lower() == ".dsf":
            continue
        filepaths.append(filepath)

    return filepaths

# ============================================================================ #

def get_content_directories() -> list[str]:
    """Returns a list of every registered Daz Studio content directory."""
    return [ str(directory) for directory in _content_directories ]

# ============================================================================ #

# pylint: disable-next=W0613
def handle_dsf_file(dsf_filepath:Path, should_cache:bool=True, memory_limit:int=0) -> dict:
    """Opens and caches the DSF file located at the (relative) filepath."""

    dsf_filepath = check_path(dsf_filepath)

    if dsf_filepath.suffix.lower() != ".dsf":
        raise NotDsfFile

    # Absolute filepath is used for disk access.
    # DSF filepath is used for dictionary access.
    absolute_filepath:Path = get_absolute_filepath(dsf_filepath)

    # Leaving early, not storing data.
    # Cache you on the flipside.
    if not should_cache:
        return open_dson_file(absolute_filepath)

    # File was already stored.
    if dsf_filepath in _dsf_cache:
        return _dsf_cache[dsf_filepath]

    # pylint: disable=W0511
    # TODO: Add memory size checks

    # Add file to cache and return it.
    _dsf_cache[dsf_filepath] = open_dson_file(absolute_filepath)
    return _dsf_cache[dsf_filepath]

# ============================================================================ #

def open_dson_file(filepath:Path) -> dict:
    """Loads a DSON file (DUF or DSF) from disk and returns it as a dictionary."""

    # Ensure type safety
    filepath = check_path(filepath)

    if not filepath.is_absolute():
        filepath = get_absolute_filepath(filepath)

    # Return value
    data:dict = None

    try:
        file:TextIOWrapper = gzip.open(filepath, "rt")
        text = file.read()
        file.close()
        observers._dson_file_opened(filepath, text)

        data = json.loads(text)
        observers._dson_file_loaded(filepath, data)

    except gzip.BadGzipFile:
        file:TextIOWrapper = open(filepath, "rt", encoding="utf-8")
        text = file.read()
        file.close()
        observers._dson_file_opened(filepath, text)

        data = json.loads(text)
        observers._dson_file_loaded(filepath, data)

    return data

# ============================================================================ #

def remove_content_directory(directory_path:Path) -> None:
    """Removes a filepath anchor from the internal array of valid content directories."""
    content_directory:Path = check_path(directory_path)
    if content_directory in _content_directories:
        _content_directories.remove(content_directory)
    return

# ============================================================================ #
