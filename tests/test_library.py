from __future__ import annotations

from dufman.library import get_all_asset_urls_from_library

from .test_directory import TestDirectory


class TestLibrary(TestDirectory):
    """Unit testing for DUFMan's library querying functions."""

    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_get_all_asset_urls(self:TestLibrary) -> None:

        #breakpoint()

        url_string:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf"
        urls:list[str] = get_all_asset_urls_from_library(url_string, "node_library")

        self.assertIsNotNone(urls)
        self.assertEqual(len(urls), 171)
        self.assertEqual(urls[0], f"{url_string}#Genesis8Female")
        self.assertEqual(urls[170], f"{url_string}#rPectoral")

        return
