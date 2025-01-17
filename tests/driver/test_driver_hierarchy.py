from typing import Self
from unittest import TestCase

from dufman.driver.driver_map import DriverMap
from dufman.driver.driver_object import DriverTarget
from dufman.file import add_content_directory, remove_content_directory
from dufman.structs.modifier import DsonModifier

from tests import DEFAULT_CONTENT_DIRECTORY


class TestDriverHierarchy(TestCase):

    def setUp(self:Self) -> None:
        add_content_directory(DEFAULT_CONTENT_DIRECTORY)
        return

    def tearDown(self:Self) -> None:
        remove_content_directory(DEFAULT_CONTENT_DIRECTORY)
        return


    # ======================================================================== #

    def test_hierarchy(self:Self) -> None:

        morph_url:str = "/data/DAZ%203D/Genesis%208/Female/Morphs/DAZ%203D/Base%20Correctives/pJCMShldrFront_n110_Bend_n40_L.dsf#pJCMShldrFront_n110_Bend_n40_L"

        # Create DriverMap
        driver_map:DriverMap = DriverMap()
        self.assertIsNotNone(driver_map)

        # Load morph
        struct:DsonModifier = DsonModifier.load_from_file(morph_url)
        driver_map.load_modifier(struct)
        self.assertTrue(driver_map.does_asset_id_have_driver(morph_url))

        # Get hierarchy info
        target:DriverTarget = driver_map._drivers.get_driver_target(f"{morph_url}?value")

        # Our sample file is driven by a CTRLMD property, so it has no direct
        #   node parents. This should fail.
        is_driven:bool = target.is_driven_by_node({"rotation/x", "rotation/y", "rotation/z"}, recursive=False)
        self.assertFalse(is_driven)

        # However, it has an indirect node parent, so this should succeed.
        is_driven:bool = target.is_driven_by_node({"rotation/x", "rotation/y", "rotation/z"}, recursive=True)
        self.assertTrue(is_driven)

        return


    # ======================================================================== #

    def test_abdomen_jcm(self:Self) -> None:

        # URLs
        jcm_url:str = "/data/DAZ%203D/Genesis%208/Female/Morphs/DAZ%203D/Base%20Correctives/pJCMAbdomenFwd_35.dsf#pJCMAbdomenFwd_35"

        # Create DriverMap
        driver_map:DriverMap = DriverMap()
        self.assertIsNotNone(driver_map)

        # Load morph
        struct:DsonModifier = DsonModifier.load_from_file(jcm_url)
        driver_map.load_modifier(struct)
        self.assertTrue(driver_map.does_asset_id_have_driver(jcm_url))

        # Test DriverTarget
        morph_target:DriverTarget = driver_map._drivers.get_driver_target(f"{jcm_url}?value")
        self.assertTrue(morph_target.is_driven_by_node({"rotation/x", "rotation/y", "rotation/z"}))

        return


    # ======================================================================== #

    def test_abdomen_jcm_with_navel_morph(self:Self) -> None:

        # URLs
        corrective_url:str = "/data/DAZ%203D/Genesis%208/Female/Morphs/DAZ%203D/Base%20Correctives/pJCMAbdomenLowerFwd_Navel.dsf#pJCMAbdomenLowerFwd_Navel"
        navel_url:str = "/data/DAZ%203D/Genesis%208/Female/Morphs/DAZ%203D/Base/PBMNavel.dsf#PBMNavel"

        # Create DriverMap
        driver_map:DriverMap = DriverMap()
        self.assertIsNotNone(driver_map)

        # Load morph
        struct:DsonModifier = DsonModifier.load_from_file(corrective_url)
        driver_map.load_modifier(struct)
        self.assertTrue(driver_map.does_asset_id_have_driver(corrective_url))

        # Get DriverTarget for Abdomen morph
        morph_target = driver_map._drivers.get_driver_target(f"{corrective_url}?value")
        properties:set[str] = {"rotation/x", "rotation/y", "rotation/z"}

        # Test morph with 0.0 strength
        self.assertFalse(morph_target.is_driven_by_node(properties))

        # Test morph with 1.0 strength
        driver_map.set_driver_value(f"{navel_url}?value", 1.0)
        self.assertTrue(morph_target.is_driven_by_node(properties))

        return


    # ======================================================================== #

    def test_shoulder_jcm(self:Self) -> None:

        # URLs
        shoulder_morph_url:str = "/data/DAZ%203D/Genesis%208/Female/Morphs/DAZ%203D/Base%20Correctives/pJCMShldrFront_n110_Bend_n40_L.dsf#pJCMShldrFront_n110_Bend_n40_L"

        # Create DriverMap
        driver_map:DriverMap = DriverMap()
        self.assertIsNotNone(driver_map)

        # Load morph
        struct:DsonModifier = DsonModifier.load_from_file(shoulder_morph_url)
        driver_map.load_modifier(struct)
        self.assertTrue(driver_map.does_asset_id_have_driver(shoulder_morph_url))

        # Get DriverTarget for shoulder morph
        morph_target:DriverTarget = driver_map._drivers.get_driver_target(f"{shoulder_morph_url}?value")
        properties:set[str] = {"rotation/x", "rotation/y", "rotation/z"}

        # Test non-recursive
        self.assertFalse(morph_target.is_driven_by_node(properties, recursive=False))

        # Test recursive
        self.assertTrue(morph_target.is_driven_by_node(properties, recursive=True))

        return


    # ======================================================================== #

    def test_neck_twist(self:Self) -> None:

        # URLs
        neck_twist_url:str = "/data/DAZ%203D/Genesis%208/Female/Morphs/DAZ%203D/Base%20Correctives/pJCMNeckTwist_22_L.dsf#pJCMNeckTwist_22_L"
        neck_reverse_url:str = "/data/DAZ%203D/Genesis%208/Female/Morphs/DAZ%203D/Base%20Correctives/pJCMNeckTwist_Reverse.dsf#pJCMNeckTwist_Reverse"

        # Create DriverMap
        driver_map:DriverMap = DriverMap()
        self.assertIsNotNone(driver_map)

        # Load morph
        struct:DsonModifier = DsonModifier.load_from_file(neck_twist_url)
        driver_map.load_modifier(struct)
        self.assertTrue(driver_map.does_asset_id_have_driver(neck_twist_url))

        # Get DriverTarget for neck morph
        morph_target:DriverTarget = driver_map._drivers.get_driver_target(f"{neck_twist_url}?value")
        properties:set[str] = {"rotation/x", "rotation/y", "rotation/z"}

        # Test morph
        self.assertTrue(morph_target.is_driven_by_node(properties))

        # Load reverse morph
        struct:DsonModifier = DsonModifier.load_from_file(neck_reverse_url)
        driver_map.load_modifier(struct)
        self.assertTrue(driver_map.does_asset_id_have_driver(neck_reverse_url))

        # Re-test morph
        self.assertTrue(morph_target.is_driven_by_node(properties))

        # Test reverse
        reverse_target:DriverTarget = driver_map._drivers.get_driver_target(f"{neck_reverse_url}?value")
        self.assertTrue(reverse_target.is_driven_by_node(properties))

        return
