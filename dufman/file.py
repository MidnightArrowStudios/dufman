# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""This module provides I/O functions for loading DSON files from disk."""

import gzip
import json
import platform
import winreg

from io import TextIOWrapper
from pathlib import Path
from urllib.parse import unquote

from .exceptions import IncorrectArgument, MultipleDsfFiles, NotDsfFile
from .observers import _dson_file_opened, _dson_file_loaded


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
    """Removes all DSF files which have been cached, freeing up memory."""
    _dsf_cache.clear()
    return


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

    if count <= 0:
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

def handle_dsf_file(dsf_filepath:Path, should_cache:bool=True, _memory_limit:int=0) -> dict:
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

    # TODO: Add memory size checks

    # Add file to cache and return it.
    _dsf_cache[dsf_filepath] = open_dson_file(absolute_filepath)
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
        _dson_file_opened(filepath, absolute_filepath, text)

        data = json.loads(text)
        _dson_file_loaded(filepath, absolute_filepath, data)

    except gzip.BadGzipFile:
        file:TextIOWrapper = open(absolute_filepath, "rt", encoding="utf-8")
        text = file.read()
        file.close()
        _dson_file_opened(filepath, absolute_filepath, text)

        data = json.loads(text)
        _dson_file_loaded(filepath, absolute_filepath, data)

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
