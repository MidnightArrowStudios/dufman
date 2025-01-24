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
from dufman.structs.modifier import DsonModifier
from dufman.url import DazUrl

from tests import DEFAULT_CONTENT_DIRECTORY


class TestDriverPath(TestCase):

    def setUp(self:Self) -> None:
        DazUrl.add_content_directory(DEFAULT_CONTENT_DIRECTORY)
        return


    def tearDown(self:Self) -> None:
        DazUrl.remove_content_directory(DEFAULT_CONTENT_DIRECTORY)
        return


    # ======================================================================== #

    def test_base_corrective(self:Self) -> None:

        url_string:str = "/data/DAZ 3D/Genesis 8/Female/Morphs/DAZ 3D/Base Correctives/pJCMChestFwd_35.dsf#pJCMChestFwd_35"
        daz_url:DazUrl = DazUrl.from_url(url_string)

        # Create DriverMap
        driver_map:DriverMap = DriverMap("Genesis8Female")
        self.assertIsNotNone(driver_map)

        # Load morph
        struct:DsonModifier = DsonModifier.load_from_file(daz_url)
        driver_map.load_modifier_driver(daz_url, struct)

        keys:list[str] = driver_map.get_all_driver_urls()
        self.assertEqual(len(keys), 2)
        self.assertEqual(keys[0].get_key_to_driver_target(), "#pJCMChestFwd_35?value")
        self.assertEqual(keys[1].get_key_to_driver_target(), "#chest?rotation/x")

        # Create driver paths
        target:DriverTarget = driver_map.get_driver_target(keys[0])
        driver_paths:list[DriverPath] = get_jcm_paths_for_target(target)
        self.assertEqual(len(driver_paths), 1)
        self.assertEqual(str(driver_paths[0]), "chest")

        # Get node driving morph
        bone:DriverTarget = driver_map.get_driver_target(keys[1])

        # Ensure DriverPath is correct
        path:DriverPath = driver_paths[0]
        self.assertIs(path._path_segments[0].target, bone)
        self.assertEqual(path.get_equation_stage(), FormulaStage.SUM)
        self.assertAlmostEqual(path.get_equation_value(), 0.0)
        self.assertTrue(path.is_driven_by_node())
        self.assertFalse(path.is_strength_zero())
        self.assertTrue(path.is_useful_for_jcm())

        # Check Blender driver expression
        expression:str = path.get_blender_expression()
        self.assertEqual(expression, "(chest * 1.6370223536534656)")

        return
