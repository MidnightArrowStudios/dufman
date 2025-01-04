from __future__ import annotations
from pathlib import Path
from unittest import TestCase

from dufman import file
from dufman.enums import LibraryType
from dufman.library import (
    find_asset_dson_in_library,
    get_all_asset_urls_from_library,
    get_asset_dson_from_library,
    get_node_hierarchy_urls_from_library,
    get_single_property_from_library,
)


class TestLibraryModule(TestCase):
    """Unit testing for DUFMan's library querying functions."""

    def setUp(self:TestLibraryModule) -> None:
        self.content_directory = Path("F:/Daz3D")
        file.add_content_directory(self.content_directory)
        return

    def tearDown(self:TestLibraryModule) -> None:
        file.remove_content_directory(self.content_directory)
        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_find_library(self:TestLibraryModule) -> None:

        url_string:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf"

        # Geometry
        geo_url:str = f"{url_string}#geometry"
        self.assertEqual(find_asset_dson_in_library(geo_url)[0], LibraryType.GEOMETRY)

        # Node
        hip_url:str = f"{url_string}#hip"
        self.assertEqual(find_asset_dson_in_library(hip_url)[0], LibraryType.NODE)

        # Modifier
        mod_url:str = f"{url_string}#SkinBinding"
        self.assertEqual(find_asset_dson_in_library(mod_url)[0], LibraryType.MODIFIER)

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_get_all_asset_urls(self:TestLibraryModule) -> None:

        url_string:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf"
        urls:list[str] = get_all_asset_urls_from_library(url_string, LibraryType.NODE)

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

    def test_get_asset_dson(self:TestLibraryModule) -> None:

        url_string:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf"
        asset_id:str = "Genesis8Female"

        dson:dict = get_asset_dson_from_library(f"{url_string}#{asset_id}", LibraryType.NODE)

        # DSON object
        self.assertIsNotNone(dson)
        self.assertIsInstance(dson, dict)

        # ID
        self.assertIn("id", dson)
        self.assertEqual(dson["id"], asset_id)

        # Name
        self.assertIn("name", dson)
        self.assertEqual(dson["name"], asset_id)

        # Type
        self.assertIn("type", dson)
        self.assertEqual(dson["type"], "figure")

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_get_node_hierarchy_urls(self:TestLibraryModule) -> None:

        url_string:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf"
        asset_id:str = "Genesis8Female"

        bone_nodes:list[str] = get_node_hierarchy_urls_from_library(f"{url_string}#{asset_id}")

        self.assertIsNotNone(bone_nodes)
        self.assertEqual(len(bone_nodes), 170)
        self.assertEqual(bone_nodes[0], f"{url_string}#hip")
        self.assertEqual(bone_nodes[-5], f"{url_string}#lPinky3")
        self.assertEqual(bone_nodes[-1], f"{url_string}#rPinky3")

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_single_property_general_scale(self:TestLibraryModule) -> None:
        """Unit test for the \"get_single_property_from_library()\" method.
        
        Daz Studio has a 'quirk' where 'scale/general' is converted under the
        hood to 'general_scale', making this worthy of a dedicated unit test.
        """

        url_string:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf"
        property_path:list[str] = [ "node_library", "lThighTwist", "scale", "general" ]

        dson:dict = get_single_property_from_library(url_string, property_path)

        self.assertIsNotNone(dson)
        self.assertEqual(dson["id"], "general_scale")

        return
