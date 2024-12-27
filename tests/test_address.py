from __future__ import annotations
from pathlib import Path
from typing import Any
from unittest import TestCase

from dufman.url import AssetAddress


class TestAddress(TestCase):

    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_invalid(self:TestAddress) -> None:

        self.assertRaises(TypeError, AssetAddress.from_url, 5)
        self.assertRaises(TypeError, AssetAddress.from_url, 10.0)
        self.assertRaises(TypeError, AssetAddress.from_url, True)

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_filepath(self:TestAddress) -> None:

        canonical_url:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf"

        def check_address(url_string:Any, *, node_name:str = None, asset_id:str = None, property_path:str = None) -> None:
            nonlocal canonical_url

            address:AssetAddress = AssetAddress.from_url(url_string)
            self.assertIsNotNone(address)
            self.assertEqual(address.node_name, node_name)
            self.assertEqual(address.filepath, canonical_url)
            self.assertEqual(address.asset_id, asset_id)
            self.assertEqual(address.property_path, property_path)
            return

        def check_filepath(url_string:str) -> None:
            asset_id:str = "Genesis8Female"
            node_name:str = "hip"
            props:str = "translation/y"

            check_address(f"{url_string}")
            check_address(f"{url_string}#{asset_id}", asset_id=asset_id)
            check_address(f"{node_name}:{url_string}#{node_name}", node_name=node_name, asset_id=node_name)
            check_address(f"{node_name}:{url_string}#{node_name}?{props}", node_name=node_name, asset_id=node_name, property_path=props)

            check_address(Path(f"{url_string}"))
            check_address(Path(f"{url_string}#{asset_id}"), asset_id=asset_id)
            check_address(Path(f"{node_name}:{url_string}#{node_name}"), node_name=node_name, asset_id=node_name)
            check_address(Path(f"{node_name}:{url_string}#{node_name}?{props}"), node_name=node_name, asset_id=node_name, property_path=props)

            return

        check_filepath("/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf")
        check_filepath(r"\data\DAZ 3D\Genesis 8\Female\Genesis8Female.dsf")
        check_filepath("\\data\\DAZ 3D\\Genesis 8\\Female\\Genesis8Female.dsf")

        return
