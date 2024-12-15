from __future__ import annotations
from unittest import TestCase

from dufman.file import (
    add_content_directory,
    clear_dsf_cache,
    add_content_directories_automatically,
    remove_all_content_directories,
)

class TestDirectory(TestCase):
    """Abstract base class for unit tests that require a content directory."""

    # ======================================================================== #

    def setUp(self:TestDirectory) -> None:

        # NOTE: Adding content directories automatically is only supported on
        #   Windows at present. On other OSes, they must be added manually.
        try:
            add_content_directories_automatically()
        except Exception:
            content_directories:list[str] = [ "F:/Daz3D" ]
            for directory in content_directories:
                add_content_directory(directory)

        return


    # ======================================================================== #

    def tearDown(self:TestDirectory) -> None:
        remove_all_content_directories()
        clear_dsf_cache()
        return


    # ======================================================================== #
