from __future__ import annotations
from pathlib import Path
from platform import system
from typing import Any
from unittest import TestCase
from urllib.parse import unquote

from dufman import file
from dufman import observers

class TestFileModule(TestCase):

    def setUp(self:TestFileModule) -> None:
        self.content_directory:Path = Path("F:/Daz3D")
        file.remove_all_content_directories()
        file.clear_dsf_cache()
        return


    def test_add_and_remove_single(self:TestFileModule) -> None:

        # Add
        file.add_content_directory(self.content_directory)
        self.assertIn(self.content_directory, file.get_content_directories())

        # Remove
        file.remove_content_directory(self.content_directory)
        files:list[Path] = file.get_content_directories()
        self.assertNotIn(self.content_directory, files)
        self.assertEqual(len(files), 0)

        return


    def test_add_duplicate_and_remove_all(self:TestFileModule) -> None:

        file.add_content_directory(self.content_directory)
        file.add_content_directory(self.content_directory)
        self.assertEqual(len(file.get_content_directories()), 1)

        # Remove
        file.remove_all_content_directories()
        self.assertEqual(len(file.get_content_directories()), 0)

        return


    def test_add_automatically(self:TestFileModule) -> None:

        # Only works on Windows.
        if system() == "Windows":
            file.add_content_directories_automatically()
            directories:list[Path] = file.get_content_directories()
            self.assertIn(self.content_directory, directories)
        else:
            self.assertRaises(NotImplementedError, file.add_content_directories_automatically)

        # Cleanup
        file.remove_all_content_directories()
        self.assertEqual(len(file.get_content_directories()), 0)

        return


    def test_check_path(self:TestFileModule) -> None:

        self.assertRaises(TypeError, file.check_path, None)

        contdir:str = self.content_directory.as_posix()
        result:Path = file.check_path(contdir)
        self.assertIsInstance(result, Path)
        self.assertEqual(result, Path(contdir))

        return


    def test_relative_absolute(self:TestFileModule) -> None:

        # Check relative path without adding content directory
        relative:Path = Path("/data/DAZ 3D/Genesis 8/Female")
        self.assertRaises(FileNotFoundError, file.get_absolute_filepath, relative)

        # Check with content directory added
        file.add_content_directory(self.content_directory)
        absolute:Path = file.get_absolute_filepath(relative)
        self.assertTrue(absolute.is_relative_to(self.content_directory))

        # Ensure absolute path matches relative path
        self.assertEqual(file.get_relative_filepath(absolute), relative)

        # Clean up
        file.remove_all_content_directories()

        return


    def test_relative_filepaths(self:TestFileModule) -> None:

        # Setup
        file.add_content_directory(self.content_directory)
        relative:Path = Path("/data/DAZ 3D/Genesis 8/Female")
        absolute:Path = file.get_absolute_filepath(relative)

        # Ensure files are extracted from file system
        g8f_path:Path = relative.joinpath("Genesis8Female.dsf")
        self.assertIn(g8f_path, file.get_relative_filepaths_from_directory(relative))
        self.assertIn(g8f_path, file.get_relative_filepaths_from_directory(absolute))

        # Cleanup
        file.remove_all_content_directories()

        return


    def test_file_caching(self:TestFileModule) -> None:

        # Setup
        file.add_content_directory(self.content_directory)
        g8f_path:Path = Path("/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf")

        # Cache is empty
        dson_file:dict = None
        self.assertEqual(file.get_cached_file_count(), 0)

        # Open file, but don't cache it
        dson_file = file.handle_dsf_file(g8f_path, should_cache=False)
        self.assertIsNotNone(dson_file)
        self.assertEqual(file.get_cached_file_count(), 0)

        # Open file and cache it
        dson_file = file.handle_dsf_file(g8f_path)
        self.assertIsNotNone(dson_file)
        self.assertEqual(file.get_cached_file_count(), 1)

        # Empty cache
        file.clear_dsf_cache()
        self.assertEqual(file.get_cached_file_count(), 0)

        # Cleanup
        file.remove_all_content_directories()

        return


    def test_memory_limit(self:TestFileModule) -> None:

        # Setup
        file.add_content_directory(self.content_directory)
        g8f_path:Path = Path("/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf")
        dson_file:dict = None

        # Open file without limits
        dson_file= file.handle_dsf_file(g8f_path)
        self.assertIsNotNone(dson_file)
        self.assertEqual(file.get_cache_memory_consumption(), 17469207)
        file.clear_dsf_cache()

        # Open file with memory limit of 10 MB
        dson_file = file.handle_dsf_file(g8f_path, memory_limit=10000000)
        self.assertIsNotNone(dson_file)
        self.assertEqual(file.get_cache_memory_consumption(), 0)
        file.clear_dsf_cache()

        # Cleanup
        file.remove_all_content_directories()

        return


    def test_open_dson(self:TestFileModule) -> None:

        # Setup
        # DSON files uses leading slashes, but they interfere with pathlib, so
        #   they must be added/stripped when converting.
        g8f_path:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf"
        absolute:Path = self.content_directory.joinpath(unquote(g8f_path[1:]))

        # -------------------------------------------------------------------- #
        # Create observers/callbacks
        user_dict:dict = {
            "filepath": str(g8f_path),
        }

        def callback(_userdata:dict, _absolute:Path, _dson_file:Any) -> None:
            nonlocal self

            # User data
            self.assertIsNotNone(_userdata)
            self.assertIsInstance(_userdata, dict)

            # Absolute filepath
            self.assertIsNotNone(_absolute)
            self.assertIsInstance(_absolute, Path)
            self.assertEqual(_absolute, absolute)

            # DSON file
            self.assertIsNotNone(_dson_file)

            # The "on_dson_file_opened" callback is fired when the DSON file is
            #   loaded as a string, before it has been instantiated as JSON.
            if isinstance(_dson_file, str):
                self.assertEqual(len(_dson_file), 3611309)
                self.assertEqual(_dson_file[59:111], _userdata["filepath"])

            # The "on_dson_file_loaded" callback is fired after the JSON file 
            #   has been instantiated as a JSON dictionary.
            elif isinstance(_dson_file, dict):
                self.assertIn("asset_info", _dson_file)
                asset_info:dict = _dson_file["asset_info"]
                self.assertIsInstance(asset_info, dict)
                self.assertIn("id", asset_info)
                self.assertEqual(asset_info["id"], _userdata["filepath"])

            else:
                raise TypeError(f"\"_dson_file\" is incorrect datatype \"{type(_dson_file)}\".")

            return

        observers.register_on_dson_file_opened(callback, user_dict)
        observers.register_on_dson_file_loaded(callback, user_dict)

        # -------------------------------------------------------------------- #

        # Load file from disk. Data is checked inside callbacks.
        dson_file:dict = file.open_dson_file(absolute)
        self.assertIsNotNone(dson_file)
        callback(user_dict, absolute, dson_file)

        # FIXME: Add methods to remove callbacks
        observers._on_dson_file_opened.clear()
        observers._on_dson_file_loaded.clear()

        return
