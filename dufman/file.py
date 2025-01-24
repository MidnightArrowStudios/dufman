# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""This module provides I/O functions for loading DSON files from disk."""

import gzip
import json
import sys

from io import TextIOWrapper
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from dufman.observers import _dson_file_opened, _dson_file_loaded


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def check_path(potential_path:Path) -> Path:
    """Validate function arguments to ensure they are Path objects.
    
    If the value can be converted into a Path, the function will do so rather
    then fail.

    :param potential_path: The path to inspect
    :types potential_path: pathlib.Path object or string
    """

    if isinstance(potential_path, str):
        potential_path = Path(unquote(potential_path))

    if not isinstance(potential_path, Path):
        raise TypeError

    return potential_path


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def get_dson_memory_consumption(obj:Any) -> int:

    running_total:int = 0
    pointer_stack:list[Any] = [ obj ]

    while pointer_stack:
        pointer:Any = pointer_stack.pop()
        running_total += sys.getsizeof(pointer)
        if isinstance(pointer, dict):
            pointer_stack.extend(pointer.values())
        elif isinstance(pointer, list):
            pointer_stack.extend(pointer)

    return running_total


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def open_dson_file(absolute_filepath:Path) -> dict:
    """Loads a DSON file (DUF or DSF) from disk and returns it as a dictionary."""

    absolute_filepath = check_path(absolute_filepath)

    # Return value
    data:dict = None

    try:
        file:TextIOWrapper = gzip.open(absolute_filepath, "rt")
        text = file.read()
        file.close()
        _dson_file_opened(absolute_filepath, text)

        data = json.loads(text)
        _dson_file_loaded(absolute_filepath, data)

    except gzip.BadGzipFile:
        file:TextIOWrapper = open(absolute_filepath, "rt", encoding="utf-8")
        text = file.read()
        file.close()
        _dson_file_opened(absolute_filepath, text)

        data = json.loads(text)
        _dson_file_loaded(absolute_filepath, data)

    return data


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def save_uncompressed_dson_file(filepath:Path, output_folder:Path=None, *, suffix:str="", overwrite:bool=False) -> None:
    """Open a compressed DSON file and save it back to disk uncompressed."""

    # TODO: Fix this function so it can take relative filepaths.
    # TODO: Implement ensure folder exists?

    # Ensure filepath argument is formatted correctly.
    filepath = check_path(filepath)
    if not filepath.is_file():
        raise ValueError("Filepath must point to a file, not a directory")

    # Load file from disk.
    dson_file:dict = open_dson_file(filepath)

    # If output folder is not passed in, save the file in the same directory
    #   as the original.
    if not output_folder:
        output_folder = filepath.parent

    # Ensure output filepath is formatted correctly.
    output_folder = check_path(output_folder)

    # Ensure output folder path is not a file.
    if not output_folder.is_dir():
        output_folder = output_folder.parent

    # Handle the name of the file.
    file_name:str = f"{filepath.stem}{suffix}{filepath.suffix}"
    output_filepath:str = output_folder.joinpath(Path(file_name))

    # Check if a file will be overwritten.
    if output_filepath.exists() and not overwrite:
        raise ValueError("File already exists. Pass \"overwrite=True\" to enable overwriting.")

    # Open file and save contents to disk.
    with open(output_filepath, mode='w', encoding='utf-8') as output_file:
        json.dump(dson_file, output_file, indent='\t')

    return
