from __future__ import annotations
from unittest import TestCase

from dufman.url import AssetAddress


class TestUrlModule(TestCase):
    """Unit testing for DUFMan's URL functions."""

    def test_format_filepath(self:TestUrlModule) -> None:

        canonical:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf"

        # Test forwardslash, unquoted
        url1:str = "data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf"
        url2:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf"

        self.assertEqual(canonical, AssetAddress.format_filepath(url1))
        self.assertEqual(canonical, AssetAddress.format_filepath(url2))

        # Test single backslash, unquoted
        url3:str = r"data\DAZ 3D\Genesis 8\Female\Genesis8Female.dsf"
        url4:str = r"\data\DAZ 3D\Genesis 8\Female\Genesis8Female.dsf"

        self.assertEqual(canonical, AssetAddress.format_filepath(url3))
        self.assertEqual(canonical, AssetAddress.format_filepath(url4))

        # Test double backslash, unquoted
        url5:str = "data\\DAZ 3D\\Genesis 8\\Female\\Genesis8Female.dsf"
        url6:str = "\\data\\DAZ 3D\\Genesis 8\\Female\\Genesis8Female.dsf"

        self.assertEqual(canonical, AssetAddress.format_filepath(url5))
        self.assertEqual(canonical, AssetAddress.format_filepath(url6))

        # Test forwardslash, quoted
        url7:str = "data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf"
        url8:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf"

        self.assertEqual(canonical, AssetAddress.format_filepath(url7))
        self.assertEqual(canonical, AssetAddress.format_filepath(url8))

        # Test single backslash, quoted
        url9:str = r"data\DAZ%203D\Genesis%208\Female\Genesis8Female.dsf"
        url10:str = r"\data\DAZ%203D\Genesis%208\Female\Genesis8Female.dsf"

        self.assertEqual(canonical, AssetAddress.format_filepath(url9))
        self.assertEqual(canonical, AssetAddress.format_filepath(url10))

        # Test double backslash, quoted
        url11:str = "data\\DAZ%203D\\Genesis%208\\Female\\Genesis8Female.dsf"
        url12:str = "\\data\\DAZ%203D\\Genesis%208\\Female\\Genesis8Female.dsf"

        self.assertEqual(canonical, AssetAddress.format_filepath(url11))
        self.assertEqual(canonical, AssetAddress.format_filepath(url12))

        # Test leading slash
        self.assertEqual(canonical[1:], AssetAddress.format_filepath(canonical, has_leading_slash=False))

        # Test unquoted
        self.assertEqual(url2, AssetAddress.format_filepath(canonical, is_quoted=False))

        # Test unquoted and leading slash
        self.assertEqual(url1, AssetAddress.format_filepath(canonical, is_quoted=False, has_leading_slash=False))

        return
