# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""Module for working with DSON-formatted URLs.

http://docs.daz3d.com/doku.php/public/dson_spec/format_description/asset_addressing/start

DSON requires URLs to be formatted a certain way. The DazUrl class encapsulates
functionality related to working with them to minimize formatting errors when
attempting to access DSF files.
"""

# stdlib
import platform
import sys
import winreg

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self
from urllib.parse import ParseResult, quote, unquote, urlparse

from dufman.enums import LibraryType, NodeType
from dufman.file import get_dson_memory_consumption, open_dson_file


# ============================================================================ #

# According to the DSON standard, a DUF file cannot be accessed from any other
#   file since they are assumed to be "user-facing". Thus, they do not need to
#   be cached. However, DSF files may be opened potentially dozens of times to
#   extract assets, thus it is useful to keep those loaded.
# Assets are keyed by a Path object, which wraps the DSON-formatted relative
#   path, i.e. Path("/data/path/to/asset.dsf").
_dsf_cache:dict = {}


# List of all content directories in the Daz Studio installation.
_content_directories:list[Path] = []


# ============================================================================ #
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
# ============================================================================ #

@dataclass
class DazUrl:

    node_name:str   = None
    filepath:str    = None
    asset_id:str    = None
    channel:str     = None


    # ======================================================================== #
    # CONTENT DIRECTORY METHODS                                                #
    # ======================================================================== #

    @staticmethod
    def add_content_directory(directory:Path) -> None:
        """Add a directory that DUFMan will use to search for asset files.
    
        This should match the content directories registered inside Daz Studio
        itself. Each directory should have a '/data' directory inside it that
        stores DSF files.

        On some platforms, the method 'add_content_directories_automatically()'
        can be used instead of adding them manually.
        """

        if isinstance(directory, str):
            directory = Path(directory)

        if not isinstance(directory, Path):
            raise TypeError

        if directory not in _content_directories:
            _content_directories.append(directory)

        return


    # ------------------------------------------------------------------------ #

    @staticmethod
    def add_content_directories_automatically() -> None:
        """Attempt to add content directories using Daz Studio's install files.

        This function is operating system-dependent. Currently, it is only impl-
        emented on Windows.
        """

        match platform.system():
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
                    DazUrl.add_content_directory(directory)

                # Clean up.
                winreg.CloseKey(registry_path)

            case _:
                raise NotImplementedError


    # ------------------------------------------------------------------------ #

    @staticmethod
    def get_content_directories() -> list[Path]:
        """Return a list of every content directory cached in DUFMan."""
        return list(_content_directories)


    # ------------------------------------------------------------------------ #

    @staticmethod
    def remove_all_content_directories() -> None:
        """Remove all content directories cached in DUFMan."""
        _content_directories.clear()
        return


    # ------------------------------------------------------------------------ #

    @staticmethod
    def remove_content_directory(directory:Path) -> None:
        """Remove a single content directory cached in DUFMan."""

        if isinstance(directory, str):
            directory = Path(directory)

        if not isinstance(directory, Path):
            raise TypeError

        if directory in _content_directories:
            _content_directories.remove(directory)

        return


    # ======================================================================== #
    # DSF CACHE METHODS                                                        #
    # ======================================================================== #

    @staticmethod
    def clear_dsf_cache() -> None:
        _dsf_cache.clear()
        return


    # ------------------------------------------------------------------------ #

    @staticmethod
    def get_cache_memory_consumption() -> int:
        memory_usage:int = get_dson_memory_consumption(_dsf_cache)
        memory_usage -= sys.getsizeof(_dsf_cache)
        return memory_usage


    # ------------------------------------------------------------------------ #

    @staticmethod
    def get_cached_file_count() -> int:
        return len(_dsf_cache)


    # ------------------------------------------------------------------------ #

    @staticmethod
    def handle_dsf_file(daz_url:Self, *, should_cache:bool=True, memory_limit:int=0) -> dict:

        if not daz_url.is_dsf_valid():
            raise ValueError

        if not daz_url.filepath and not daz_url.asset_id:
            raise ValueError

        # Relative filepath is used for dictionary access.
        # Absolute filepath is used for file system access.
        relative_filepath:Path = daz_url.get_relative_filepath()
        absolute_filepath:Path = daz_url.get_absolute_filepath()

        # Leaving early, not storing data.
        # Cache you on the flip side.
        if not should_cache:
            return open_dson_file(absolute_filepath)

        # File is already in cache.
        if relative_filepath in _dsf_cache:
            return _dsf_cache[relative_filepath]

        # Load file from disk.
        dson_file:dict = open_dson_file(absolute_filepath)

        # File is too large, don't cache it.
        if memory_limit > 0:
            if get_dson_memory_consumption(dson_file) > memory_limit:
                return dson_file

        # Add file to cache and return it.
        _dsf_cache[relative_filepath] = dson_file
        return _dsf_cache[relative_filepath]


    # ======================================================================== #
    # FORMATTING METHODS                                                       #
    # ======================================================================== #

    @staticmethod
    def format_filepath(filepath:str, *, is_quoted:bool=True, has_leading_slash:bool=True) -> str:

        # TODO: Strip content directory?

        if not filepath:
            return None

        # Type safety.
        if not isinstance(filepath, str):
            raise TypeError

        # Ensure filepath has forward slashes and is quoted properly according
        #   to DSON standard.
        result:str = quote(Path(unquote(str(filepath))).as_posix(), safe="/\\")

        # Ensure filepath either does or does not start with a forward slash,
        #   according to the method's arguments.
        if not has_leading_slash and result.startswith("/"):
            result = result.lstrip("/")
        elif has_leading_slash and not result.startswith("/"):
            result = f"/{result}"

        return result if is_quoted else unquote(result)


    # ------------------------------------------------------------------------ #

    @staticmethod
    def format_url(*, node_name:str=None, filepath:str=None, asset_id:str=None, channel:str=None) -> str:

        result:str = ""

        if node_name is not None:
            result += f"{node_name}:"

        if filepath is not None:
            formatted_filepath:str = DazUrl.format_filepath(filepath)
            result += formatted_filepath

        if asset_id is not None:
            result += f"#{asset_id}"

        if channel is not None:
            result += f"?{channel}"

        return result


    # ======================================================================== #
    # FACTORY METHODS                                                          #
    # ======================================================================== #

    @classmethod
    def from_url(cls:Self, url_string:str) -> Self:

        # If the argument is a Path, then force-convert it into a POSIX string 
        #   to ensure it has forward slashes.
        if isinstance(url_string, Path):
            url_string = url_string.as_posix()

        # Ensure type safety.
        if not isinstance(url_string, str):
            raise TypeError

        # urllib sucks at handling scheme part of URL. It doesn't preserve
        #   capitalization and it misreads it as a filepath if it has an
        #   underscore. If there is a scheme, we need to handle it ourselves.
        scheme:str = None
        if url_string.find(":") >= 0:
            split_on_colon:tuple[str, str, str] = url_string.partition(":")
            scheme = split_on_colon[0]
            url_string = split_on_colon[2]

        # Break URL into components and store them inside urllib object.
        result:ParseResult = urlparse(unquote(url_string))

        # The strings we will use to create the URL.
        node_name:str = scheme
        filepath:str = cls.format_filepath(result.path)
        asset_id:str = None
        channel:str = None

        # DSON puts the query after the fragment, for some reason. urllib does
        #   not like this.
        if result.fragment.find("?") == -1:
            asset_id = result.fragment
            channel = None
        else:
            split_on_qmark:tuple[str, str, str] = result.fragment.partition("?")
            asset_id = split_on_qmark[0]
            channel = Path(split_on_qmark[2]).as_posix()

        # Convert empty strings to None.
        node_name = node_name if node_name else None
        filepath = filepath if filepath else None
        asset_id = asset_id if asset_id else None
        channel = channel if channel else None

        return cls(node_name, filepath, asset_id, channel)


    # ------------------------------------------------------------------------ #

    @classmethod
    def from_parts(cls:Self, *, node_name:str=None, filepath:str=None, asset_id:str=None, channel:str=None) -> Self:
        filepath = cls.format_filepath(filepath)
        return cls(node_name, filepath, asset_id, channel)


    # ======================================================================== #
    # FILEPATH METHODS                                                         #
    # ======================================================================== #

    def get_absolute_filepath(self:Self) -> Path:

        # TODO: How to handle multiple content directories?

        content_directory:Path = self.get_content_directory()
        filepath:Path = self.get_relative_filepath()
        return content_directory.joinpath(filepath)


    # ------------------------------------------------------------------------ #

    def get_content_directory(self:Self) -> Path:

        # TODO: How to handle multiple content directories?

        if not self.filepath:
            return None

        fp:str = self.format_filepath(self.filepath, is_quoted=False, has_leading_slash=False)
        filepath:Path = Path(fp)

        result:list[Path] = []

        for directory in self.get_content_directories():
            potential:Path = directory.joinpath(filepath)
            if potential.exists():
                result.append(directory)

        count:int = len(result)

        if count <= 0:
            raise FileNotFoundError
        elif count == 1:
            return result[0]
        else:
            raise RuntimeError


    # ------------------------------------------------------------------------ #

    def get_relative_filepath(self:Self) -> Path:
        """Returns the relative filepath component as a Path object.

        This is a convenience method which returns the filepath in a format
        better suited for working with Path objects. The filepath is unquoted
        and has its leading slash stripped, allowing it to be used with methods
        like joinpath() without issue.
        """

        return Path(self.format_filepath(self.filepath, is_quoted=False, has_leading_slash=False))


    # ======================================================================== #
    # DIRECTORY METHODS                                                        #
    # ======================================================================== #

    @staticmethod
    def get_urls_in_directory(directory:Path) -> list[Self]:

        # TODO: Change this to accept DazUrl object?

        # String type check
        if isinstance(directory, str):
            directory = Path(unquote(directory))

        # Path type check
        if not isinstance(directory, Path):
            raise ValueError

        # -------------------------------------------------------------------- #
        # Format path object to remove URL quotes
        directory = Path(unquote(str(directory)))

        # -------------------------------------------------------------------- #
        absolute_path:Path = None

        # If path is absolute, ensure directory exists.
        if directory.is_absolute():
            if directory.exists() and directory.is_dir():
                absolute_path = directory
            else:
                return []

        # If path is relative, loop through all content directories to see if
        #   we can locate it.
        else:
            # Leading slashes interfere with pathlib, so strip them off
            stripped:Path = directory.relative_to(directory.anchor)

            absolute_paths:list[Path] = []

            for cont_dir in _content_directories:
                potential:Path = cont_dir.joinpath(stripped)
                if potential.exists() and potential.is_dir():
                    absolute_paths.append(potential)

            # Ensure we do not have multiple content directories.
            path_count:int = len(absolute_paths)
            if path_count == 1:
                absolute_path = absolute_paths[0]
            elif path_count > 1:
                raise RuntimeError

        # -------------------------------------------------------------------- #
        # Directory could not be found.
        if not absolute_path:
            return []

        # -------------------------------------------------------------------- #
        # Get the content directory this filepath belongs to.
        cont_dirs:list[Path] = []

        for cont_dir in _content_directories:
            if absolute_path.is_relative_to(cont_dir):
                cont_dirs.append(cont_dir)

        if len(cont_dirs) != 1:
            raise RuntimeError

        content_directory:Path = cont_dirs[0]

        # -------------------------------------------------------------------- #
        daz_urls:list[Self] = []

        for filepath in absolute_path.iterdir():
            if not filepath.suffix.lower() == ".dsf":
                continue
            relative_path:Path = filepath.relative_to(content_directory)
            formatted_url:str = DazUrl.format_filepath(str(relative_path))
            daz_urls.append(DazUrl.from_parts(filepath=formatted_url))

        return daz_urls


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def get_url_to_asset(self:Self, fallback:str=None) -> str:

        if not self.asset_id:
            return None

        fallback = self.format_filepath(fallback)

        if self.filepath:
            return self.format_url(filepath=self.filepath, asset_id=self.asset_id)
        elif fallback:
            return self.format_url(filepath=fallback, asset_id=self.asset_id)
        else:
            return None


    # ------------------------------------------------------------------------ #

    def get_url_to_channel(self:Self) -> str:
        return self.format_url(filepath=self.filepath, asset_id=self.asset_id, channel=self.channel)


    # ------------------------------------------------------------------------ #

    def get_key_to_driver_target(self:Self) -> str:
        return self.format_url(asset_id=self.asset_id, channel=self.channel)


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def get_all_urls_in_file(self:Self, library_type:LibraryType=None) -> list[Self]:

        if not self.filepath:
            raise RuntimeError

        dsf_file:dict = self.get_file_dson()

        result:list[DazUrl] = []

        if library_type:

            if library_type.value not in dsf_file:
                raise ValueError

            for entry in dsf_file[library_type.value]:
                daz_url:DazUrl = DazUrl.from_parts(filepath=self.filepath, asset_id=entry["id"])
                result.append(daz_url)

        else:

            for library in list(LibraryType):
                
                if not library.value in dsf_file:
                    continue

                for entry in dsf_file[library.value]:
                    daz_url:DazUrl = DazUrl.from_parts(filepath=self.filepath, asset_id=entry["id"])
                    result.append(daz_url)

        return result


    # ------------------------------------------------------------------------ #

    def get_asset_dson(self:Self, library_type:LibraryType=None) -> tuple[dict, LibraryType]:

        if not self.filepath or not self.asset_id:
            raise RuntimeError

        file_dson:dict = self.get_file_dson()

        # We know which library the asset is in.
        if library_type:

            # File doesn't have a library of this type.
            if not library_type.value in file_dson:
                raise ValueError

            # Search all assets in order.
            for asset in file_dson[library_type.value]:
                if asset["id"] == self.asset_id:
                    return (asset, library_type)

        # We don't know which library the asset is in and need to search all of
        #   them.
        else:

            # Loop through all libraries in order.
            for potential_library in list(LibraryType):

                # File doesn't have a library of this type.
                if not potential_library.value in file_dson:
                    continue

                # Search all assets in order.
                for asset in file_dson[potential_library.value]:
                    if asset["id"] == self.asset_id:
                        return (asset, potential_library)

        # Asset couldn't be found.
        return (None, None)


    # ------------------------------------------------------------------------ #

    def get_file_dson(self:Self) -> dict:

        if not self.filepath:
            raise RuntimeError

        return self.handle_dsf_file(self)


    # ------------------------------------------------------------------------ #

    def get_figure_hierarchy_urls(self:Self) -> list[Self]:


        # Check LibraryType
        asset_dson, asset_type = self.get_asset_dson()
        if asset_type != LibraryType.NODE:
            raise ValueError

        # Check NodeType
        node_type:NodeType = NodeType(asset_dson["type"])
        if node_type != NodeType.FIGURE:
            raise ValueError

        result:list[DazUrl] = []

        # -------------------------------------------------------------------- #
        file_dson:dict = self.get_file_dson()
        all_nodes:list[dict] = file_dson["node_library"]

        # working_list stores all the DSON dictionaries under consideration.
        working_list:list[dict] = [ *self._get_child_node_dson(all_nodes, self.asset_id) ]

        # The first entry is popped off the list to see if it's a bone. If it
        #   is, then it's added to working_list for processing. If not, it's
        #   discarded.
        # This stops nodes parented to nodes from being mistaken for bones.
        while working_list:
            potential_child:dict = working_list.pop(0)
            if NodeType(potential_child["type"]) == NodeType.BONE:
                bone_id:str = potential_child["id"]
                child_url:DazUrl = DazUrl.from_parts(filepath=self.filepath, asset_id=bone_id)
                result.append(child_url)
                working_list.extend( self._get_child_node_dson(all_nodes, bone_id) )
        # -------------------------------------------------------------------- #

        return result


    # ------------------------------------------------------------------------ #

    def get_value(self:Self, value_path:list[Any]) -> Any:
        """Extract a single value from a DSON file by its path.
        
        "value_path" should be a list of tokens from the root to the value. For
        instance, if we load "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf"
        as the root, we can extract the name of the fifth material surface with
        the value_path:

            [ "geometry_library", 0, "polygon_material_groups", "values", 4 ]
        
        When iterating over a list, this method will first compare the token to
        the asset ID, if it exists. If no match is found, it will attempt to 
        use it as an index into a list.

        For Genesis8Female.dsf, the following property paths are all equivalent:

            [ "node_library", 0, "label" ]
            [ "node_library", "0", "label" ]
            [ "node_library", "Genesis8Female", "label" ]

        """

        if not self.filepath:
            raise RuntimeError

        pointer:Any = self.get_file_dson()
        tokens:list[str] = list(value_path)

        while tokens:

            token:Any = tokens.pop(0)

            # Dictionary
            if isinstance(pointer, dict):

                if not token in pointer:
                    raise ValueError

                # Dirty hack to get around Daz Studio stupidity. Formulas may
                #   refer to "scale/general", but it is silently converted to
                #   "general_scale".
                if token == "scale" and len(tokens) == 1 and tokens[0] == "general":
                    tokens.pop(0)
                    token = "general_scale"

                pointer = pointer[token]
                continue

            # List
            if isinstance(pointer, list):

                # Because there is a nested loop ahead, the continue statement
                #   won't work. Instead, create a flag.
                was_found:bool = False

                # Loop through all items in list in search of matching ID.
                for entry in pointer:
                    if isinstance(entry, dict) and "id" in entry and entry["id"] == token:
                        pointer = entry
                        was_found = True
                        break

                # ID was found, restart outer loop.
                if was_found:
                    continue

                # If the token doesn't match an ID, try and use it as an index.
                index:int = None

                try:
                    index = int(token)
                except ValueError as ve:
                    raise ValueError from ve

                if not 0 <= index < len(pointer):
                    raise IndexError

                pointer = pointer[index]
                continue

            # Unknown
            # There is at least one token left, but the pointer is not pointing
            #   to a list or dictionary. This is illegal, so throw an exception.
            raise ValueError

        return pointer


    # ------------------------------------------------------------------------ #

    def is_dsf_valid(self:Self) -> bool:

        if not self.filepath:
            return False

        # Get content directory.
        try:
            content_directory:Path = self.get_content_directory()
        except FileNotFoundError:
            return False

        # Get path to DSF file in file system.
        absolute:Path = content_directory.joinpath(self.get_relative_filepath())

        # Return True if DSF file is valid.
        return absolute.exists() and absolute.is_file() and absolute.suffix.lower() == ".dsf"


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    @staticmethod
    def _get_child_node_dson(node_library:list[dict], parent_id:str) -> list[dict]:

        result:list[dict] = []

        # Loop through all nodes in search of ones with the desired parent.
        for node in node_library:

            # No parent at all, skip.
            if not "parent" in node:
                continue

            # Asset IDs are stored with a pound sign. This will strip them off.
            # TODO: Come up with a more robust way to handle this?
            potential_id:str = node["parent"].lstrip("#")

            # TODO: Can a node have a parent in a different file? It's doubtful,
            #   but it might be an edge case worth looking into.

            # Success, add it to the return list.
            if potential_id == parent_id:
                result.append(node)

        return result
