# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from __future__ import annotations
from pathlib import Path
from typing import Any, Self
from unittest import TestCase

from dufman import file
from dufman import observers
from dufman.url import DazUrl

from tests import DEFAULT_CONTENT_DIRECTORY


# ============================================================================ #
#                                                                              #
# ============================================================================ #

class TestFileModule(TestCase):

    def setUp(self:Self) -> None:
        DazUrl.clear_dsf_cache()
        DazUrl.remove_all_content_directories()
        DazUrl.add_content_directory(DEFAULT_CONTENT_DIRECTORY)
        return

    def tearDown(self:Self) -> None:
        DazUrl.clear_dsf_cache()
        DazUrl.remove_all_content_directories()
        return


    # ======================================================================== #

    def test_check_path(self:Self) -> None:

        self.assertRaises(TypeError, file.check_path, None)
        self.assertRaises(TypeError, file.check_path, 5.0)
        self.assertRaises(TypeError, file.check_path,10)

        canonical:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf"
        canon_obj:Path = Path(canonical)
        self.assertEqual(file.check_path(canonical), canon_obj)
        self.assertEqual(file.check_path(canon_obj), canon_obj)

        return


    # ======================================================================== #

    def test_open_dson(self:Self) -> None:

        # Setup
        # DSON files uses leading slashes, but they interfere with pathlib, so
        #   they must be added/stripped when converting.
        g8f_url:DazUrl = DazUrl.from_url("/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf")
        absolute:Path = g8f_url.get_absolute_filepath()

        # -------------------------------------------------------------------- #
        # Create observers/callbacks
        user_dict:dict = {
            "filepath": str(g8f_url.filepath),
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
