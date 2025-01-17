from typing import Self
from unittest import TestCase

from dufman.driver2.driver_map import DriverMap
from dufman.file import add_content_directory, remove_all_content_directories
from dufman.structs.modifier import DsonModifier
from dufman.structs.morph import DsonMorph
from dufman.structs.node import DsonNode

from tests import DEFAULT_CONTENT_DIRECTORY


class TestCharacterMemphis(TestCase):

    def setUp(self:Self) -> None:
        add_content_directory(DEFAULT_CONTENT_DIRECTORY)
        return


    def tearDown(self:Self) -> None:
        remove_all_content_directories()
        return


    # ======================================================================== #

    def test_character_memphis(self:Self) -> None:

        memphis_url:str = "/data/DAZ 3D/Genesis 8/Female/Morphs/Mousso/Memphis/Memphis.dsf#Memphis"

        # Create character morph
        struct:DsonModifier = DsonModifier.load_from_file(memphis_url)
        self.assertIsNotNone(struct)

        # Create DriverMap
        driver_map:DriverMap = DriverMap("Genesis8Female")
        self.assertIsNotNone(driver_map)

        # Load character morph
        driver_map.load_modifier_driver(memphis_url, struct)

        # Dial in character morph
        driver_map.set_driver_value("#Memphis?value", 1.0)

        # -------------------------------------------------------------------- #
        # Morph

        # Confirm morph is valid
        morph:DsonMorph = driver_map.get_current_morph_shape(16556)
        self.assertIsNotNone(morph)
        self.assertEqual(morph.expected_vertices, 16556)
        self.assertEqual(len(morph.deltas), 16556)

        # These three vertices have the greatest distance between the Genesis 8
        #   figure and the Memphis morph
        self.assertAlmostEqual(morph.deltas[4625].x,  0.0268, places=4)
        self.assertAlmostEqual(morph.deltas[4625].y, -0.3983, places=4)
        self.assertAlmostEqual(morph.deltas[4625].z, -2.2407, places=4)

        self.assertAlmostEqual(morph.deltas[4584].x,  0.0360, places=4)
        self.assertAlmostEqual(morph.deltas[4584].y, -0.3979, places=4)
        self.assertAlmostEqual(morph.deltas[4584].z, -2.2077, places=4)

        self.assertAlmostEqual(morph.deltas[92].x,  0.0086, places=4)
        self.assertAlmostEqual(morph.deltas[92].y, -0.5878, places=4)
        self.assertAlmostEqual(morph.deltas[92].z, -2.1168, places=4)

        # -------------------------------------------------------------------- #
        # Node

        node:DsonNode = driver_map.get_current_node_shape("#lShldr")
        self.assertIsNotNone(node)

        # center_point
        self.assertAlmostEqual(node.center_point.x.current_value, 14.4946, places=4)
        self.assertAlmostEqual(node.center_point.y.current_value, 145.3723, places=4)
        self.assertAlmostEqual(node.center_point.z.current_value, -4.8660, places=4)

        # end_point
        self.assertAlmostEqual(node.end_point.x.current_value, 21.9895, places=4)
        self.assertAlmostEqual(node.end_point.y.current_value, 136.9345, places=4)
        self.assertAlmostEqual(node.end_point.z.current_value, -4.6754, places=4)

        return
