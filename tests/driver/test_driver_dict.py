from __future__ import annotations
from unittest import TestCase

from dufman.driver.driver_dict import DriverDictionary
from dufman.driver.driver_object import DriverTarget
from dufman.url import AssetAddress


# ============================================================================ #

class TestDriverDict(TestCase):

    def test_driver_dict(self:TestDriverDict) -> None:

        # URLs
        filepath:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf"
        asset_id:str = "lCollar"
        prop_path:str = "rotation/x"
        invalid_filepath:str = f"{filepath}#{asset_id}"

        filepath_x:str = f"{invalid_filepath}?{prop_path}"
        filepath_y:str = f"{invalid_filepath}?rotation/y"        
        filepath_z:str = f"{invalid_filepath}?rotation/z"

        # -------------------------------------------------------------------- #
        # Object instantiation
        driver_dict:DriverDictionary = DriverDictionary()
        driver_x:DriverTarget = DriverTarget(filepath_x, None, None)
        driver_y:DriverTarget = DriverTarget(filepath_y, None, None)
        driver_z:DriverTarget = DriverTarget(filepath_z, None, None)

        self.assertIsNotNone(driver_dict)
        self.assertIsNotNone(driver_x)
        self.assertIsNotNone(driver_y)
        self.assertIsNotNone(driver_z)

        # -------------------------------------------------------------------- #
        # Invalid filepath
        self.assertRaises(ValueError, driver_dict.add_driver_target, invalid_filepath, driver_x)

        # Valid filepath but wrong argument
        self.assertRaises(TypeError, driver_dict.add_driver_target, filepath_x, None)
        self.assertRaises(TypeError, driver_dict.add_driver_target, filepath_x, 5)

        # Valid filepath and correct argument
        driver_dict.add_driver_target(filepath_x, driver_x)
        self.assertEqual(driver_dict.get_driver_target(filepath_x), driver_x)

        # -------------------------------------------------------------------- #
        # Get filepaths
        filepaths:list[str] = driver_dict.get_all_filepaths()
        self.assertEqual(len(filepaths), 1)
        self.assertEqual(filepaths[0], AssetAddress.format_filepath(filepath))

        # Get asset IDs
        asset_ids:list[str] = driver_dict.get_all_asset_ids(filepath_x)
        self.assertEqual(len(asset_ids), 1)
        self.assertEqual(asset_ids[0], asset_id)

        # Get property path
        prop_paths:list[str] = driver_dict.get_all_property_paths(filepath_x)
        self.assertEqual(len(prop_paths), 1)
        self.assertEqual(prop_paths[0], prop_path)

        # -------------------------------------------------------------------- #
        # Has filepath
        self.assertTrue(driver_dict.has_filepath(filepath))
        self.assertTrue(driver_dict.has_asset_id(invalid_filepath))
        self.assertTrue(driver_dict.has_property_path(filepath_x))

        # Has asset ID
        self.assertTrue(driver_dict.has_asset_id(invalid_filepath))
        self.assertTrue(driver_dict.has_property_path(filepath_x))

        # Has property path
        self.assertTrue(driver_dict.has_property_path(filepath_x))

        # -------------------------------------------------------------------- #
        # Multiple filepaths
        driver_dict.add_driver_target(filepath_y, driver_y)
        driver_dict.add_driver_target(filepath_z, driver_z)

        props:list[str] = [ "rotation/x", "rotation/y", "rotation/z" ]
        self.assertEqual(driver_dict.get_all_property_paths(invalid_filepath), props)

        # -------------------------------------------------------------------- #
        # Check return values
        self.assertNotEqual(driver_dict.get_driver_target(filepath_x), driver_y)
        self.assertNotEqual(driver_dict.get_driver_target(filepath_y), driver_z)
        self.assertNotEqual(driver_dict.get_driver_target(filepath_z), driver_x)
        
        self.assertEqual(driver_dict.get_driver_target(filepath_x), driver_x)
        self.assertEqual(driver_dict.get_driver_target(filepath_y), driver_y)
        self.assertEqual(driver_dict.get_driver_target(filepath_z), driver_z)

        return
