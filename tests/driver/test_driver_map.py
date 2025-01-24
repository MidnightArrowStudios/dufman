from copy import copy
from typing import Self
from unittest import TestCase

from dufman.driver.driver_map import DriverMap
from dufman.driver.driver_object import DriverEquation, DriverTarget
from dufman.enums import LibraryType
from dufman.structs.formula import DsonFormula
from dufman.structs.modifier import DsonModifier
from dufman.structs.node import DsonNode
from dufman.url import DazUrl

from tests import DEFAULT_CONTENT_DIRECTORY

class TestDriverMap(TestCase):

    def setUp(self:Self) -> None:
        DazUrl.add_content_directory(DEFAULT_CONTENT_DIRECTORY)
        return


    def tearDown(self:Self) -> None:
        DazUrl.remove_all_content_directories()
        return


    # ======================================================================== #

    def test_modifier_loading_navel(self:Self) -> None:

        url_string:str = "/data/DAZ 3D/Genesis 8/Female/Morphs/DAZ 3D/Base/PBMNavel.dsf#PBMNavel"
        daz_url:DazUrl = DazUrl.from_url(url_string)

        # Load struct
        struct:DsonModifier = DsonModifier.load_from_file(daz_url)
        self.assertIsNotNone(struct)

        # Create DriverMap
        driver_map:DriverMap = DriverMap("Genesis8Female")
        self.assertIsNotNone(driver_map)

        # Forward-declare variables
        driver_urls:list[DazUrl] = None
        driver_target:DriverTarget = None

        # -------------------------------------------------------------------- #
        # Test modifier driver

        # Insert morph into DriverMap and check URL exists
        driver_map.load_modifier_driver(daz_url, struct)
        driver_urls = driver_map.get_all_driver_urls()
        self.assertEqual(len(driver_urls), 1)
        self.assertEqual(driver_urls[0].asset_id, "PBMNavel")
        self.assertEqual(driver_urls[0].channel, "value")

        # Retrieve DriverTarget object and verify its fields
        driver_target = driver_map.get_driver_target(driver_urls[0])
        self.assertIsNotNone(driver_target)
        self.assertIsInstance(driver_target, DriverTarget)
        self.assertEqual(str(driver_target), driver_urls[0].get_key_to_driver_target())
        self.assertTrue(driver_target.is_valid())
        self.assertEqual(driver_target.get_library_type(), LibraryType.MODIFIER)

        # -------------------------------------------------------------------- #
        # Test empty driver

        driver_map.remove_all_driver_targets()
        daz_url.channel = "value"

        # Add URL as empty target first
        driver_map.load_empty_driver(daz_url)
        driver_urls = driver_map.get_all_driver_urls()
        self.assertEqual(len(driver_urls), 1)
        self.assertEqual(driver_urls[0].asset_id, "PBMNavel")
        self.assertEqual(driver_urls[0].channel, "value")

        # Retrieve target, verify fields again
        driver_target = driver_map.get_driver_target(driver_urls[0])
        self.assertIsNotNone(driver_target)
        self.assertIsInstance(driver_target, DriverTarget)
        self.assertEqual(str(driver_target), driver_urls[0].get_key_to_driver_target())
        self.assertFalse(driver_target.is_valid())
        self.assertIsNone(driver_target.get_library_type())

        daz_url.channel = None

        # -------------------------------------------------------------------- #
        # Test reassigning empty driver with modifier data

        # Add same URL as empty driver target, but with struct
        driver_map.load_modifier_driver(daz_url, struct)
        driver_urls = driver_map.get_all_driver_urls()
        self.assertEqual(len(driver_urls), 1)
        self.assertEqual(driver_urls[0].asset_id, "PBMNavel")
        self.assertEqual(driver_urls[0].channel, "value")

        # Verify fields again
        self.assertTrue(driver_target.is_valid())
        self.assertEqual(driver_target.get_library_type(), LibraryType.MODIFIER)

        return


    # ======================================================================== #

    def test_node_loading_abdomen(self:Self) -> None:

        url_string:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf#abdomenLower"
        daz_url:DazUrl = DazUrl.from_url(url_string)

        # Load struct
        struct:DsonNode = DsonNode.load_from_file(daz_url)
        self.assertIsNotNone(struct)

        # Create DriverMap
        driver_map:DriverMap = DriverMap("Genesis8Female")
        self.assertIsNotNone(driver_map)

        # Forward-declare variables
        driver_urls:list[str] = None
        driver_target:DriverTarget = None

        # -------------------------------------------------------------------- #
        # Test node driver

        self.assertRaises(ValueError, driver_map.load_node_driver, daz_url, struct)
        daz_url.channel = "rotation/x"

        driver_map.load_node_driver(daz_url, struct)
        driver_urls = driver_map.get_all_driver_urls()
        self.assertEqual(len(driver_urls), 1)
        self.assertEqual(driver_urls[0].asset_id, "abdomenLower")
        self.assertEqual(driver_urls[0].channel, "rotation/x")

        driver_target = driver_map.get_driver_target(driver_urls[0])
        self.assertIsNotNone(driver_target)
        self.assertIsInstance(driver_target, DriverTarget)
        self.assertEqual(str(driver_target), driver_urls[0].get_key_to_driver_target())
        self.assertTrue(driver_target.is_valid())
        self.assertEqual(driver_target.get_library_type(), LibraryType.NODE)

        # -------------------------------------------------------------------- #
        # Test empty driver
        driver_map.remove_all_driver_targets()

        driver_map.load_empty_driver(daz_url)
        driver_urls = driver_map.get_all_driver_urls()
        self.assertEqual(len(driver_urls), 1)
        self.assertEqual(driver_urls[0].asset_id, "abdomenLower")
        self.assertEqual(driver_urls[0].channel, "rotation/x")

        driver_target = driver_map.get_driver_target(driver_urls[0])
        self.assertIsNotNone(driver_target)
        self.assertIsInstance(driver_target, DriverTarget)
        self.assertEqual(str(driver_target), driver_urls[0].get_key_to_driver_target())
        self.assertFalse(driver_target.is_valid())
        self.assertIsNone(driver_target.get_library_type())

        # -------------------------------------------------------------------- #
        # Test reassignment

        driver_map.load_node_driver(daz_url, struct)
        driver_urls = driver_map.get_all_driver_urls()
        self.assertEqual(len(driver_urls), 1)
        self.assertEqual(driver_urls[0].asset_id, "abdomenLower")
        self.assertEqual(driver_urls[0].channel, "rotation/x")

        self.assertTrue(driver_target.is_valid())
        self.assertEqual(driver_target.get_library_type(), LibraryType.NODE)

        return


    # ======================================================================== #

    def test_node_formula_loading(self:Self) -> None:

        url_string:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf#lCollar?rotation/y"
        collar_url:DazUrl = DazUrl.from_url(url_string)

        # Load struct
        struct:DsonNode = DsonNode.load_from_file(collar_url)
        self.assertIsNotNone(struct)

        driver_map:DriverMap = DriverMap("Genesis8Female")
        self.assertIsNotNone(driver_map)

        # -------------------------------------------------------------------- #
        driver_map.load_node_driver(collar_url, struct)

        # Ensure all four drivers define in formula are loaded
        driver_urls:list[str] = driver_map.get_all_driver_urls()
        self.assertEqual(len(driver_urls), 4)

        self.assertEqual(driver_urls[0].asset_id, "lCollar")
        self.assertEqual(driver_urls[0].channel, "rotation/y")
        
        self.assertEqual(driver_urls[1].asset_id, "lCollar")
        self.assertEqual(driver_urls[1].channel, "rotation/z")
        
        self.assertEqual(driver_urls[2].asset_id, "lPectoral")
        self.assertEqual(driver_urls[2].channel, "rotation/x")
        
        self.assertEqual(driver_urls[3].asset_id, "lPectoral")
        self.assertEqual(driver_urls[3].channel, "rotation/y")

        # Test number of DriverEquations created
        self.assertEqual(driver_map.get_equation_count(), 2)

        # -------------------------------------------------------------------- #
        # Test Collar-RotY
        # Loaded manually
        croty:DriverTarget = driver_map.get_driver_target(driver_urls[0])
        self.assertIsNotNone(croty)
        self.assertIsInstance(croty, DriverTarget)
        self.assertTrue(croty.is_valid())
        self.assertEqual(croty.get_library_type(), LibraryType.NODE)

        # Test Collar-RotZ
        # Loaded automatically
        crotz:DriverTarget = driver_map.get_driver_target(driver_urls[1])
        self.assertIsNotNone(crotz)
        self.assertIsInstance(crotz, DriverTarget)
        self.assertTrue(crotz.is_valid())
        self.assertEqual(crotz.get_library_type(), LibraryType.NODE)

        # -------------------------------------------------------------------- #
        # Check driver URLs again to make sure no more were loaded
        driver_urls = driver_map.get_all_driver_urls()
        self.assertEqual(len(driver_urls), 4)

        self.assertEqual(driver_urls[0].asset_id, "lCollar")
        self.assertEqual(driver_urls[0].channel, "rotation/y")
        
        self.assertEqual(driver_urls[1].asset_id, "lCollar")
        self.assertEqual(driver_urls[1].channel, "rotation/z")
        
        self.assertEqual(driver_urls[2].asset_id, "lPectoral")
        self.assertEqual(driver_urls[2].channel, "rotation/x")
        
        self.assertEqual(driver_urls[3].asset_id, "lPectoral")
        self.assertEqual(driver_urls[3].channel, "rotation/y")
        

        # Check number of equations again to ensure they haven't been loaded
        #   twice
        self.assertEqual(driver_map.get_equation_count(), 2)

        return


    # ======================================================================== #

    def test_loading_scale_chest(self:Self) -> None:

        url_string:str = "/data/DAZ 3D/Genesis 8/Female/Morphs/DAZ 3D/Base/SCLPropagatingChest.dsf#SCLPropagatingChest"
        daz_url:DazUrl = DazUrl.from_url(url_string)

        # Load struct
        struct:DsonModifier = DsonModifier.load_from_file(daz_url)
        self.assertIsNotNone(struct)

        driver_map:DriverMap = DriverMap("Genesis8Female")
        self.assertIsNotNone(driver_map)

        driver_map.load_modifier_driver(daz_url, struct)
        self.assertEqual(driver_map.get_equation_count(), 22)

        for (index, equation) in enumerate(driver_map._equations):

            self.assertIsInstance(equation, DriverEquation)
            self.assertIsInstance(equation._formula_struct, DsonFormula)

            match index:
                case 7:
                    self.assertIn("lCollar:#lCollar?rotation/z", equation._inputs)
                case 8:
                    self.assertIn("lCollar:#lCollar?rotation/y", equation._inputs)
                case 12:
                    self.assertIn("rCollar:#rCollar?rotation/z", equation._inputs)
                case 13:
                    self.assertIn("rCollar:#rCollar?rotation/y", equation._inputs)
                case _:
                    self.assertIn("Genesis8Female:#SCLPropagatingChest?value", equation._inputs)

        return


    # ======================================================================== #

    def test_loading_without_filepath(self:Self) -> None:

        memphis_url:DazUrl = DazUrl.from_url("/data/DAZ%203D/Genesis%208/Female/Morphs/Mousso/Memphis/eJCMMemphisEyesClosedL.dsf#eJCMMemphisEyesClosedL")
        genesis_url:DazUrl = DazUrl.from_url("/data/DAZ 3D/Genesis 8/Female/Morphs/DAZ 3D/Base Pose Head/eCTRLEyesClosedL.dsf#ECTRLEyesClosedL")

        # Forward-declare variables
        struct:DsonModifier = None
        invalid_keys:list[str] = None

        # Instantiate DriverMap
        driver_map:DriverMap = DriverMap("Genesis8Female")
        self.assertIsNotNone(driver_map)

        # Create Memphis eye morph
        struct = DsonModifier.load_from_file(memphis_url)
        self.assertIsNotNone(struct)

        # Load eye morph into DriverMap
        memphis_morph:DriverTarget = driver_map.load_modifier_driver(memphis_url, struct)

        # Check state of DriverMap/equations
        self.assertEqual(driver_map.get_equation_count(), 474)

        # Ensure Genesis eye morph is not valid
        invalid_keys = driver_map.get_invalid_driver_keys()
        self.assertEqual(len(invalid_keys), 1)
        self.assertEqual(invalid_keys[0].asset_id, "ECTRLEyesClosedL")
        self.assertEqual(invalid_keys[0].channel, "value")

        # Get invalid morph
        invalid_url:DazUrl = copy(genesis_url)
        invalid_url.channel = "value"
        invalid_morph:DriverTarget = driver_map.get_driver_target(invalid_url)
        self.assertIsNotNone(invalid_morph)
        self.assertFalse(invalid_morph.is_valid())

        # Create Genesis eye morph
        struct = DsonModifier.load_from_file(genesis_url)
        self.assertIsNotNone(struct)

        # Load eye morph into DriverMap
        driver_map.load_modifier_driver(genesis_url, struct)

        # Check state of DriverMap/equations
        self.assertEqual(driver_map.get_equation_count(), 492)

        # Ensure no morphs are invalid
        invalid_keys = driver_map.get_invalid_driver_keys()
        self.assertEqual(len(invalid_keys), 0)

        # Check formerly-invalid morph
        self.assertTrue(invalid_morph.is_valid())
        equation:DriverEquation = invalid_morph._subcomponents[0]
        self.assertIs(equation._output, memphis_morph)
        self.assertIs(list(equation._inputs.values())[0], invalid_morph)

        return


    # ======================================================================== #

    def test_folder_loading(self:Self) -> None:

        url:str = "/data/DAZ 3D/Genesis 8/Female/Morphs/DAZ 3D/Base/"

        # Create DriverMap
        driver_map:DriverMap = DriverMap("Genesis8Female")
        self.assertIsNotNone(driver_map)

        # Load folder
        driver_map.load_modifier_folder(url)
        driver_keys:str = [ url.get_key_to_driver_target() for url in driver_map.get_all_driver_urls() ]
        self.assertIn("#BaseFlexions?value", driver_keys)
        self.assertIn("#JCMs On?value", driver_keys)
        self.assertIn("#PBMNailsLength?value", driver_keys)
        self.assertIn("#PBMNavel?value", driver_keys)
        self.assertIn("#PBMNipples?value", driver_keys)
        self.assertIn("#PHMEyeRimRefineHD_div2?value", driver_keys)
        self.assertIn("#PHMMouthRealism_HD_div2?value", driver_keys)

        return
