# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

# stdlib
from typing import Self
from unittest import TestCase

# dufman
from dufman.driver.driver_map import DriverMap
from dufman.driver.driver_object import DriverEquation, DriverTarget
from dufman.enums import ChannelType, FormulaStage, LibraryType
from dufman.structs.modifier import DsonModifier
from dufman.url import DazUrl

from tests import DEFAULT_CONTENT_DIRECTORY


class TestDriverObject(TestCase):

    def setUp(self:Self) -> None:
        DazUrl.add_content_directory(DEFAULT_CONTENT_DIRECTORY)
        return

    def tearDown(self:Self) -> None:
        DazUrl.remove_content_directory(DEFAULT_CONTENT_DIRECTORY)
        return


    # ======================================================================== #

    def test_jcm_abdomen2_forward(self:Self) -> None:

        # Morph variables
        morph_path:str = "/data/DAZ 3D/Genesis 8/Female/Morphs/DAZ 3D/Base Correctives/pJCMAbdomen2Fwd_40.dsf#pJCMAbdomen2Fwd_40"
        morph_url:DazUrl = DazUrl.from_url(morph_path)
        morph_struct:DsonModifier = DsonModifier.load_from_file(morph_url)

        # Bone variables
        bone_url:DazUrl = DazUrl.from_parts(asset_id="abdomen2", channel="rotation/x")

        # -------------------------------------------------------------------- #
        # Create DriverMap
        driver_map:DriverMap = DriverMap("Genesis8Female")
        driver_map.load_modifier_driver(morph_url, morph_struct)

        # Get morph DriverTarget
        morph_target:DriverTarget = driver_map.get_driver_target(morph_url)
        self.assertIsNotNone(morph_target)

        # Get bone DriverTarget
        bone_target:DriverTarget = driver_map.get_driver_target(bone_url)
        self.assertIsNotNone(bone_target)

        # -------------------------------------------------------------------- #
        # Check names
        self.assertEqual(morph_target.format_expression_name(), "pJCMAbdomen2Fwd_40_value")
        self.assertEqual(bone_target.format_expression_name(), "abdomen2_rot_x")

        # Check URLs
        url1:DazUrl = morph_target.get_target_url()
        self.assertEqual(url1.asset_id, "pJCMAbdomen2Fwd_40")
        self.assertEqual(url1.channel, "value")

        url2:DazUrl = bone_target.get_target_url()
        self.assertEqual(url2.asset_id, "abdomen2")
        self.assertEqual(url2.channel, "rotation/x")

        # Check boolean methods
        self.assertTrue(morph_target.has_morph())
        self.assertFalse(bone_target.has_morph())

        self.assertTrue(morph_target.is_driven_by_node())
        self.assertFalse(bone_target.is_driven_by_node())

        self.assertFalse(morph_target.is_rotation())
        self.assertTrue(bone_target.is_rotation())

        self.assertTrue(morph_target.is_valid())
        self.assertTrue(bone_target.is_valid())

        # Check state methods
        self.assertEqual(morph_target.get_channel_type(), ChannelType.FLOAT)
        self.assertEqual(bone_target.get_channel_type(), ChannelType.FLOAT)

        self.assertEqual(morph_target.get_library_type(), LibraryType.MODIFIER)
        self.assertEqual(bone_target.get_library_type(), LibraryType.NODE)

        # -------------------------------------------------------------------- #
        # Check values
        self.assertAlmostEqual(morph_target.get_value(), 0.0)
        self.assertAlmostEqual(bone_target.get_value(), 0.0)

        bone_target.set_value(40.0)

        self.assertAlmostEqual(morph_target.get_value(), 1.0)
        self.assertAlmostEqual(bone_target.get_value(), 40.0)

        bone_target.set_value(0.0)

        return
