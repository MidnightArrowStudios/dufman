from __future__ import annotations
from unittest import TestCase

from dufman.file import add_content_directory, remove_content_directory
from dufman.driver.driver_map import DriverMap
from dufman.structs.modifier import DsonModifier
from dufman.structs.morph import DsonMorph

class TestDriverMap(TestCase):

    # ======================================================================== #

    def setUp(self:TestDriverMap) -> None:
        add_content_directory("F:/Daz3D")
        return


    # ------------------------------------------------------------------------ #

    def tearDown(self:TestDriverMap) -> None:
        remove_content_directory("F:/Daz3D")
        return


    # ======================================================================== #

    def test_victoria8(self:TestDriverMap) -> None:

        # Modifier URLs
        base_url:str = "/data/DAZ%203D/Genesis%208/Female/Morphs/DAZ%203D/Victoria%208/CTRLVictoria8.dsf#CTRLVictoria8"

        # -------------------------------------------------------------------- #
        # Ensure object was created

        driver_map:DriverMap = DriverMap()
        self.assertIsNotNone(driver_map)

        # -------------------------------------------------------------------- #
        # Load character modifier

        driver_map.load_modifier(DsonModifier.load(base_url))
        self.assertTrue(driver_map.does_asset_id_have_driver(base_url))

        # -------------------------------------------------------------------- #
        # Check loaded URLs

        victoria_url:str = f"{base_url}?value"
        body_morph_url:str = "/data/DAZ%203D/Genesis%208/Female/Morphs/DAZ%203D/Victoria%208/FHMVictoria8.dsf#FHMVictoria8?value"
        head_morph_url:str = "/data/DAZ%203D/Genesis%208/Female/Morphs/DAZ%203D/Victoria%208/FBMVictoria8.dsf#FBMVictoria8?value"

        urls:list[str] = driver_map.get_all_driver_urls()
        self.assertIsNotNone(urls)
        self.assertIsInstance(urls, list)
        self.assertEqual(len(urls), 1512)

        # NOTE: "body_morph_url" is at the front, "head_morph_url" is at the
        #   back. This is because the body morph loads everything from the
        #   Genesis8Female.dsf between them.
        self.assertEqual(urls[0], victoria_url)
        self.assertEqual(urls[1], body_morph_url)
        self.assertEqual(urls[1511], head_morph_url)

        # -------------------------------------------------------------------- #
        # Dial Victoria 8 in

        self.assertAlmostEqual(driver_map.get_driver_value(head_morph_url), 0.0)
        self.assertAlmostEqual(driver_map.get_driver_value(body_morph_url), 0.0)

        driver_map.set_driver_value(victoria_url, 1.0)
        self.assertAlmostEqual(driver_map.get_driver_value(head_morph_url), 1.0)
        self.assertAlmostEqual(driver_map.get_driver_value(body_morph_url), 1.0)

        # -------------------------------------------------------------------- #
        # Bone positions

        bones:list[tuple[float, str]] = [
            (   8.60, "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#rThumb3?center_point/z"),
            ( 170.60, "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#rBrowMid?end_point/y"),
            (    1.0, "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#rThigh?scale/y"),
            ( 147.69, "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#lCollar?end_point/y"),
            (  -1.36, "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#rSmallToe4?center_point/y"),
            ( -20.32, "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#rBigToe_2?orientation/y"),
            (   3.21, "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#rCarpal2?end_point/z"),
            (  -2.88, "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#rNasolabialMiddle?center_point/x"),
            ( 163.72, "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#lLipBelowNose?center_point/y"),
            (   7.94, "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#lCheekUpperInner?end_point/z"),
        ]

        for bone in bones:
            self.assertAlmostEqual(driver_map.get_driver_value(bone[1]), bone[0], places=2)

        # -------------------------------------------------------------------- #
        # Morph vertex positions

        morph:DsonMorph = driver_map.get_current_morph_shape(16556)
        breakpoint()

        return



#   509: <Vector ( -0.8818,  5.3460, -0.0756)>
#  1792: <Vector (  0.3642,  4.5411, -1.1118)>
#  3092: <Vector ( -0.0720,  4.5140,  0.0623)>
#  5101: <Vector ( -1.1162,  5.4204,  0.0115)>
#  6829: <Vector ( -0.6213, -0.0989, -0.4503)>
#  7147: <Vector (  0.0796,  4.8020, -0.0700)>
#  7964: <Vector ( -0.4976, -0.1505, -0.6023)>
#  9571: <Vector (  0.7755,  5.0940, -0.2787)>
# 11176: <Vector (  0.4906,  3.9886, -0.0337)>
# 12640: <Vector (  1.0993,  5.3510,  0.0163)>
# 12644: <Vector (  1.0911,  5.3240,  0.0212)>
# 13059: <Vector ( -0.1015,  4.8790, -0.0299)>
# 13411: <Vector ( -0.0259,  4.8820, -0.0648)>
# 15589: <Vector ( -0.9834, -0.0785, -0.3598)>
# 16074: <Vector (  0.2307,  4.4590, -0.1460)>
# 16520: <Vector ( -0.2307,  4.4875, -0.1243)>