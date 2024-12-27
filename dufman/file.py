# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""This module provides I/O functions for loading DSON files from disk."""

import gzip
import json
import platform
import sys
import winreg

from io import TextIOWrapper
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from dufman.exceptions import IncorrectArgument, MultipleDsfFiles, NotDsfFile
from dufman.observers import _dson_file_opened, _dson_file_loaded


# ============================================================================ #
#                                                                              #
# ============================================================================ #

# According to the DSON standard, a DUF file cannot be accessed from any other
#   file since they are assumed to be "user-facing". Thus, they do not need to
#   be cached. However, DSF files may be opened potentially dozens of times to
#   extract assets, thus it is useful to keep those loaded.
# Assets are keyed by a Path object, which wraps the DSON-formatted relative
#   path, i.e. Path("/data/path/to/asset.dsf").
_dsf_cache:dict = {}

# List of all content directories that Daz assets may have been installed to.
_content_directories:list[Path] = []


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def add_content_directory(directory_path:Path) -> None:
    """Add a root directory that DUFMan will use to search for asset files.
    
    These directories should match the content directories created and used by
    the Daz Studio application itself. Each content directory should have a 
    '/data' and a '/runtime' directory directly inside them.
    
    On some platforms, the function 'add_content_directories_automatically()'
    can be used to extract the directories from the Daz Studio installation.

    :param directory_path: The root directory
    :types directory_path: A string or a pathlib.Path object
    """
    content_directory:Path = check_path(directory_path)
    if content_directory not in _content_directories:
        _content_directories.append(content_directory)
    return


# ============================================================================ #

def add_content_directories_automatically() -> None:
    """Attempt to add content directories using Daz Studio's install files.

    This function is operating system-dependent. Currently, it is only imple-
    mented on Windows.

    :raises NotImplementedError: If the OS is not supported, the function does
        nothing.
    """

    os_name:str = platform.system()

    match os_name:
        case "Windows":

            # Creates a readonly path to the Daz Studio registry entry.
            registry_path = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, r"SOFTWARE\DAZ\Studio4", access=winreg.KEY_READ)

            # Tuple with number of sub-keys, number of values, and last time
            #   registry was edited.
            info:tuple = winreg.QueryInfoKey(registry_path)

            # The list of content directories that will be added.
            directories:list[str] = []

            # Loop through values, check to ensure they are zero-terminated
            #   strings ("winreg.REG_SZ") and that their names begin with
            #   "ContentDir", and add them to the filepath list.
            for index in range(info[1]):
                value:tuple = winreg.EnumValue(registry_path, index)
                if (value[2] == winreg.REG_SZ) and (value[0].startswith("ContentDir")):
                    directories.append(value[1])

            # Add content directory filepaths.
            for directory in directories:
                add_content_directory(directory)

            # Clean up.
            winreg.CloseKey(registry_path)

        case _:
            raise NotImplementedError("Operating system is not supported. Add content directories manually.")

    return

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
        message:str = f"Argument \"{repr(potential_path)}\" is not Path or string."
        raise IncorrectArgument(message)

    return potential_path


# ============================================================================ #

def clear_dsf_cache() -> None:
    """Removes all DSF files from cache, freeing up memory."""
    _dsf_cache.clear()
    return


# ============================================================================ #

def get_absolute_filepath(relative_path:Path) -> Path:
    """Converts a relative DSON path to an absolute path."""

    # Ensure type safety
    relative_path = check_path(relative_path)

    # Leading slashes interfere with pathlib, so strip them off.
    stripped:Path = relative_path.relative_to(relative_path.anchor)

    # Return value
    absolute_filepaths:list[Path] = []

    for directory in _content_directories:
        potential:Path = directory.joinpath(stripped)
        if potential.exists():
            absolute_filepaths.append(potential)

    count:int = len(absolute_filepaths)

    if count <= 0:
        raise FileNotFoundError
    elif count == 1:
        return absolute_filepaths[0]
    else:
        raise MultipleDsfFiles

# ============================================================================ #

def get_cache_memory_consumption() -> int:
    memory_usage:int = _get_memory_consumption(_dsf_cache)
    memory_usage -= sys.getsizeof(_dsf_cache)
    return memory_usage

# ============================================================================ #

def get_cached_file_count() -> int:
    return len(_dsf_cache)

# ============================================================================ #

def get_content_directories() -> list[Path]:
    """Returns a list of every registered Daz Studio content directory."""
    return [ directory for directory in _content_directories ]

# ============================================================================ #

def get_property_from_dson_file(root_dson:dict, property_path:list[Any]) -> Any:
    """Extract a single arbitrary property from a DSON file by its path.
    
    The property_path variable should be a list of tokens representing the path
    from the root_dson variable to the desired property. For instance, if we
    load "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf" and use that as the
    root_dson, we can extract the name of its fifth material surface with the
    following property_path:

        [ "geometry_library", 0, "polygon_material_groups", "values", 4 ]

    When iterating over a list, the function will first compare the token to
    each entry's asset ID. If no match is found, then it will use the token as
    an index into the list.
    
    For Genesis8Female.dsf, the following property paths are all equivalent:

        [ "node_library", 0, "label" ]
        [ "node_library", "0", "label" ]
        [ "node_library", "Genesis8Female", "label" ]

    """

    dsf_pointer:Any = root_dson
    tokens:list[str] = list(property_path)

    while tokens:
        token:Any = tokens.pop(0)

        # Current level of hierarchy is a dictionary.
        if isinstance(dsf_pointer, dict):

            # The token is not in this level of the hierarchy.
            if not token in dsf_pointer:
                raise ValueError(f"Token \"{token}\" is not valid.")

            # This is a dirty hack to get around some Daz Studio stupidity.
            #   Formulas may refer to "scale/general", but under the hood it
            #   is converted to "general_scale".
            if token == "scale" and len(tokens) == 1 and tokens[0] == "general":
                tokens.pop(0)
                token = "general_scale"

            # Extract item from dictionary.
            dsf_pointer = dsf_pointer[token]
            continue

        # Current level of hierarchy is a list.
        if isinstance(dsf_pointer, list):

            # We want to restart the "while tokens:" loop if the token matches
            #   an ID, but we can't use a continue statement inside a nested
            #   loop. Instead, create a flag.
            was_found:bool = False

            # If the token matches an ID, then accept it.
            for entry in dsf_pointer:
                if isinstance(entry, dict) and "id" in entry and entry["id"] == token:
                    dsf_pointer = entry
                    was_found = True
                    break

            # Restart top-level loop if ID was found.
            if was_found:
                continue

            # If token doesn't match an ID, see if we can use it as an index.
            index:int = None

            # Convert token to integer.
            try:
                index = int(token)
            except ValueError as ve:
                raise ValueError(f"Token \"{token}\" is not valid.") from ve
            
            # Index is out of bounds
            if not 0 <= index < len(dsf_pointer):
                raise IndexError

            dsf_pointer = dsf_pointer[index]
            continue

        # If the property_path still has something in it, but the current level
        #   is not a dict or list, then it is not a valid property path.
        raise ValueError("\"property_path\" is not valid.")

    return dsf_pointer

# ============================================================================ #

def get_relative_filepaths_from_directory(directory:Path, *, filter_dsf:bool=True) -> list[Path]:

    directory = check_path(directory)

    if not directory.is_absolute():
        directory = get_absolute_filepath(directory)

    result:list[Path] = []

    for filepath in directory.iterdir():
        if filter_dsf and not filepath.suffix.lower() == ".dsf":
            continue
        relative:Path = get_relative_filepath(filepath)
        result.append(relative)

    return result

# ============================================================================ #

def get_relative_filepath(absolute_path:Path) -> Path:

    # Ensure type safety
    absolute_path = check_path(absolute_path)

    if not absolute_path.is_absolute():
        raise ValueError("Path argument is not an absolute path.")

    # Return value
    relative_filepaths:list[Path] = []

    for directory in _content_directories:
        if absolute_path.exists() and absolute_path.is_relative_to(directory):
            relative_path = absolute_path.relative_to(directory)
            relative_path = Path("/").joinpath(relative_path)
            relative_filepaths.append(relative_path)

    count:int = len(relative_filepaths)

    if count <= 0:
        raise FileNotFoundError
    elif count == 1:
        return relative_filepaths[0]
    else:
        raise MultipleDsfFiles

# ============================================================================ #

def handle_dsf_file(dsf_filepath:Path, *, should_cache:bool=True, memory_limit:int=0) -> dict:
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

    # Load the file from disk.
    dson_file:dict = open_dson_file(absolute_filepath)

    # If the file is too large, don't cache it.
    if memory_limit > 0:
        # Memory limit is in megabytes.
        if _get_memory_consumption(dson_file) > memory_limit:
            return dson_file

    # Add file to cache and return it.
    _dsf_cache[dsf_filepath] = dson_file
    return _dsf_cache[dsf_filepath]

# ============================================================================ #

def open_dson_file(filepath:Path) -> dict:
    """Loads a DSON file (DUF or DSF) from disk and returns it as a dictionary."""

    # Ensure type safety
    filepath = check_path(filepath)

    absolute_filepath:Path = None
    if filepath.is_absolute():
        absolute_filepath = filepath
    else:
        absolute_filepath = get_absolute_filepath(filepath)

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

def remove_content_directory(directory_path:Path) -> None:
    """Removes a filepath anchor from the internal array of valid content directories."""
    content_directory:Path = check_path(directory_path)
    if content_directory in _content_directories:
        _content_directories.remove(content_directory)
    return


# ============================================================================ #

def remove_all_content_directories() -> None:
    """Removes all filepath anchors that have previously been loaded."""
    for directory in get_content_directories():
        remove_content_directory(directory)
    return


# ============================================================================ #

def save_uncompressed_dson_file(filepath:Path, output_folder:Path=None, *, suffix:str="", overwrite:bool=False) -> None:
    """Open a compressed DSON file and save it back to disk uncompressed."""

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


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def _get_memory_consumption(obj:Any) -> int:

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
