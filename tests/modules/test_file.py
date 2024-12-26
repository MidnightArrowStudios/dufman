from __future__ import annotations
from pathlib import Path
from platform import system
from unittest import TestCase

from dufman import file
from dufman.exceptions import IncorrectArgument

class TestFileModule(TestCase):

    def test_file_module(self:TestFileModule) -> None:

        content_directory:Path = Path("F:/Daz3D")

        # check_path()
        self.assertIsInstance(file.check_path(content_directory.as_posix()), Path)
        self.assertRaises(IncorrectArgument, file.check_path, None)

        # add_content_directory()
        file.add_content_directory(content_directory)
        self.assertIn(content_directory, file.get_content_directories())

        # remove_content_directory()
        file.remove_content_directory(content_directory)
        self.assertNotIn(content_directory, file.get_content_directories())

        # add_content_directories_automatically()
        # Only works on Windows
        if system() == "Windows":
            file.add_content_directories_automatically()
        else:
            file.add_content_directory(content_directory)
        self.assertIn(content_directory, file.get_content_directories())

        # remove_all_content_directories()
        file.remove_all_content_directories()
        self.assertEqual(len(file.get_content_directories()), 0)

        # get_absolute_filepath()
        relative:Path = Path("/data/DAZ 3D/Genesis 8/Female")
        self.assertRaises(FileNotFoundError, file.get_absolute_filepath, relative)
        file.add_content_directory(content_directory)
        absolute:Path = file.get_absolute_filepath(relative)
        self.assertTrue(absolute.is_relative_to(content_directory))

        # get_relative_filepath()
        self.assertEqual(file.get_relative_filepath(absolute), relative)

        return
