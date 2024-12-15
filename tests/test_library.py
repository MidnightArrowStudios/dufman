from __future__ import annotations

from dufman.enums import LibraryType

from dufman.library import (
    get_all_asset_urls_from_library,
    get_asset_json_from_library,
    get_node_hierarchy_urls_from_library,
)

from .test_directory import TestDirectory


class TestLibrary(TestDirectory):
    """Unit testing for DUFMan's library querying functions."""

    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_get_all_asset_urls(self:TestLibrary) -> None:

        url_string:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf"
        urls:list[str] = get_all_asset_urls_from_library(url_string, "node_library")

        self.assertIsNotNone(urls)
        self.assertEqual(len(urls), 171)
        self.assertEqual(urls[0], f"{url_string}#Genesis8Female")
        self.assertEqual(urls[1], f"{url_string}#hip")
        self.assertEqual(urls[169], f"{url_string}#lPectoral")
        self.assertEqual(urls[170], f"{url_string}#rPectoral")

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_get_asset_json(self:TestLibrary) -> None:

        url_string:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf"
        asset_id:str = "Genesis8Female"

        json:dict = get_asset_json_from_library(f"{url_string}#{asset_id}", LibraryType.NODE)

        # JSON object
        self.assertIsNotNone(json)
        self.assertIsInstance(json, dict)

        # ID
        self.assertIn("id", json)
        self.assertEqual(json["id"], asset_id)

        # Name
        self.assertIn("name", json)
        self.assertEqual(json["name"], asset_id)

        # Type
        self.assertIn("type", json)
        self.assertEqual(json["type"], "figure")

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_get_node_hierarchy_urls(self:TestLibrary) -> None:

        url_string:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf"
        asset_id:str = "Genesis8Female"

        bone_nodes:list[str] = get_node_hierarchy_urls_from_library(f"{url_string}#{asset_id}")

        self.assertIsNotNone(bone_nodes)
        self.assertEqual(len(bone_nodes), 170)
        self.assertEqual(bone_nodes[0], f"{url_string}#hip")
        self.assertEqual(bone_nodes[-5], f"{url_string}#lPinky3")
        self.assertEqual(bone_nodes[-1], f"{url_string}#rPinky3")

        return
