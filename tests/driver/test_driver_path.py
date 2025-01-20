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
from dufman.driver.driver_object import DriverTarget
from dufman.driver.driver_path import (
    DriverPath,
    get_jcm_paths_for_target,
)
from dufman.enums import FormulaStage
from dufman.file import add_content_directory, remove_content_directory
from dufman.structs.modifier import DsonModifier

from tests import DEFAULT_CONTENT_DIRECTORY


class TestDriverPath(TestCase):

    def setUp(self:Self) -> None:
        add_content_directory(DEFAULT_CONTENT_DIRECTORY)
        return


    def tearDown(self:Self) -> None:
        remove_content_directory(DEFAULT_CONTENT_DIRECTORY)
        return


    # ======================================================================== #

    def test_base_corrective(self:Self) -> None:

        morph_url:str = "/data/DAZ 3D/Genesis 8/Female/Morphs/DAZ 3D/Base Correctives/pJCMChestFwd_35.dsf#pJCMChestFwd_35"

        # Create DriverMap
        driver_map:DriverMap = DriverMap("Genesis8Female")
        self.assertIsNotNone(driver_map)

        # Load morph
        struct:DsonModifier = DsonModifier.load_from_file(morph_url)
        driver_map.load_modifier_driver(morph_url, struct)

        keys:list[str] = driver_map.get_all_driver_keys()
        self.assertEqual(len(keys), 2)
        self.assertEqual(keys[0], "#pJCMChestFwd_35?value")
        self.assertEqual(keys[1], "#chest?rotation/x")

        # Create driver paths
        target:DriverTarget = driver_map.get_driver_target(keys[0])
        driver_paths:list[DriverPath] = get_jcm_paths_for_target(target)
        self.assertEqual(len(driver_paths), 1)
        self.assertEqual(str(driver_paths[0]), "pJCMChestFwd_35")

        # Get node driving morph
        bone:DriverTarget = driver_map.get_driver_target(keys[1])

        # Ensure DriverPath is correct
        path:DriverPath = driver_paths[0]
        self.assertIs(path._path_segments[0].target, target)
        self.assertIs(path._path_segments[1].target, bone)
        self.assertEqual(path.get_equation_stage(), FormulaStage.SUM)
        self.assertAlmostEqual(path.get_equation_value(), 0.0)
        self.assertTrue(path.is_driven_by_node())
        self.assertFalse(path.is_strength_zero())
        self.assertTrue(path.is_useful_for_jcm())

        return
