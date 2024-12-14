from __future__ import annotations
from pathlib import Path
from typing import Any
from unittest import TestCase

from dufman.exceptions import IncorrectArgument
from dufman.url import AssetAddress


class TestAddress(TestCase):

    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_invalid(self:TestAddress) -> None:

        self.assertRaises(IncorrectArgument, AssetAddress.create_from_url, 5)
        self.assertRaises(IncorrectArgument, AssetAddress.create_from_url, 10.0)
        self.assertRaises(IncorrectArgument, AssetAddress.create_from_url, True)

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_filepath(self:TestAddress) -> None:

        canonical_url:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf"
        foreslash_url:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf"
        backslash_url:str = r"\data\DAZ 3D\Genesis 8\Female\Genesis8Female.dsf"
        double_backslash_url:str = "\\data\\DAZ 3D\\Genesis 8\\Female\\Genesis8Female.dsf"

        def check_address(url_string:Any, *, node_name:str = None, asset_id:str = None, property_path:str = None) -> None:
            nonlocal canonical_url

            address:AssetAddress = AssetAddress.create_from_url(url_string)
            self.assertIsNotNone(address)
            self.assertEqual(address.node_name, node_name)
            self.assertEqual(address.filepath, canonical_url)
            self.assertEqual(address.asset_id, asset_id)
            self.assertEqual(address.property_path, property_path)
            return

        # Filepath string
        check_address(foreslash_url)
        check_address(backslash_url)
        check_address(double_backslash_url)

        # Filepath as Path object
        check_address(Path(foreslash_url))
        check_address(Path(backslash_url))
        check_address(Path(double_backslash_url))

        # Test Asset ID
        asset_id:str = "Genesis8Female"

        # String
        check_address(f"{foreslash_url}#{asset_id}", asset_id=asset_id)
        check_address(f"{backslash_url}#{asset_id}", asset_id=asset_id)
        check_address(f"{double_backslash_url}#{asset_id}", asset_id=asset_id)

        # Path object
        check_address(Path(f"{foreslash_url}#{asset_id}"), asset_id=asset_id)
        check_address(Path(f"{backslash_url}#{asset_id}"), asset_id=asset_id)
        check_address(Path(f"{double_backslash_url}#{asset_id}"), asset_id=asset_id)

        # Test node name
        node_name:str = "hip"

        # String
        check_address(f"{node_name}:{foreslash_url}#{node_name}", node_name=node_name, asset_id=node_name)
        check_address(f"{node_name}:{backslash_url}#{node_name}", node_name=node_name, asset_id=node_name)
        check_address(f"{node_name}:{double_backslash_url}#{node_name}", node_name=node_name, asset_id=node_name)

        # Path object
        check_address(Path(f"{node_name}:{foreslash_url}#{node_name}"), node_name=node_name, asset_id=node_name)
        check_address(Path(f"{node_name}:{backslash_url}#{node_name}"), node_name=node_name, asset_id=node_name)
        check_address(Path(f"{node_name}:{double_backslash_url}#{node_name}"), node_name=node_name, asset_id=node_name)

        # Test property path
        props:str = "translation/y"

        # String
        check_address(f"{node_name}:{foreslash_url}#{node_name}?{props}", node_name=node_name, asset_id=node_name, property_path=props)
        check_address(f"{node_name}:{backslash_url}#{node_name}?{props}", node_name=node_name, asset_id=node_name, property_path=props)
        check_address(f"{node_name}:{double_backslash_url}#{node_name}?{props}", node_name=node_name, asset_id=node_name, property_path=props)

        # Path object
        check_address(Path(f"{node_name}:{foreslash_url}#{node_name}?{props}"), node_name=node_name, asset_id=node_name, property_path=props)
        check_address(Path(f"{node_name}:{backslash_url}#{node_name}?{props}"), node_name=node_name, asset_id=node_name, property_path=props)
        check_address(Path(f"{node_name}:{double_backslash_url}#{node_name}?{props}"), node_name=node_name, asset_id=node_name, property_path=props)

        return
