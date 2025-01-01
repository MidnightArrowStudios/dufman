from __future__ import annotations
from unittest import TestCase

from dufman.file import add_content_directory, remove_content_directory
from dufman.driver.driver_map import DriverMap
from dufman.structs.modifier import DsonModifier
from dufman.structs.node import DsonNode

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
        struct:DsonModifier = DsonModifier.load_from_file(base_url)
        driver_map.load_modifier(struct)
        self.assertTrue(driver_map.does_asset_id_have_driver(base_url))

        # -------------------------------------------------------------------- #
        # Check loaded URLs

        victoria_url:str = f"{base_url}?value"
        head_morph_url:str = "/data/DAZ%203D/Genesis%208/Female/Morphs/DAZ%203D/Victoria%208/FHMVictoria8.dsf#FHMVictoria8?value"
        body_morph_url:str = "/data/DAZ%203D/Genesis%208/Female/Morphs/DAZ%203D/Victoria%208/FBMVictoria8.dsf#FBMVictoria8?value"

        urls:list[str] = driver_map.get_all_driver_urls()
        self.assertIsNotNone(urls)
        self.assertIsInstance(urls, list)
        self.assertEqual(len(urls), 1512)

        # NOTE: "body_morph_url" is at the front, "head_morph_url" is at the
        #   back. This is because the body morph loads everything from the
        #   Genesis8Female.dsf between them.
        self.assertEqual(urls[0], victoria_url)
        self.assertEqual(urls[1], head_morph_url)
        self.assertEqual(urls[1511], body_morph_url)

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

        #morph:DsonMorph = driver_map.get_current_morph_shape(16556)

        # -------------------------------------------------------------------- #
        # Morph bone positions

        node_url:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#lCollar"
        node:DsonNode = driver_map.get_current_node_shape(node_url)

        # center_point
        self.assertAlmostEqual(node.center_point.x.current_value,   3.46, places=2)
        self.assertAlmostEqual(node.center_point.y.current_value, 147.35, places=2)
        self.assertAlmostEqual(node.center_point.z.current_value,  -3.79, places=2)

        # end_point
        self.assertAlmostEqual(node.end_point.x.current_value,  12.99, places=2)
        self.assertAlmostEqual(node.end_point.y.current_value, 147.69, places=2)
        self.assertAlmostEqual(node.end_point.z.current_value,  -4.91, places=2)

        # orientation
        self.assertAlmostEqual(node.orientation.x.current_value, 0.05, places=2)
        self.assertAlmostEqual(node.orientation.y.current_value, 3.51, places=2)
        self.assertAlmostEqual(node.orientation.z.current_value, 1.75, places=2)

        return
