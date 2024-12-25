from __future__ import annotations

from dufman.enums import ChannelType
from dufman.objects.property_map import PropertyMap
from dufman.structs import DsonModifier, DsonMorph, DsonNode

from ..test_directory import TestDirectory

class TestISTEvangeliya(TestDirectory):

    def test_ist_evangeliya_properties(self:TestISTEvangeliya) -> None:

        # Modifier URLs
        evangeliya_url:str = "/data/DAZ%203D/Genesis%208/Female/Morphs/iSourceTextures/Evangeliya/CTRL-ISTEvangeliya.dsf#CTRL-ISTEvangeliya"
        body_morph_url:str = "/data/DAZ%203D/Genesis%208/Female/Morphs/iSourceTextures/Evangeliya/FHM-ISTEvangeliya.dsf#FHM-ISTEvangeliya"
        head_morph_url:str = "/data/DAZ%203D/Genesis%208/Female/Morphs/iSourceTextures/Evangeliya/FBM-ISTEvangeliya.dsf#FBM-ISTEvangeliya"

        # Node URLs
        g8f_hip_url:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#hip"
        g8f_head_url:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#head"

        # -------------------------------------------------------------------- #
        # PropertyMap Object
        property_map:PropertyMap = PropertyMap()
        property_map.load_property_from_file(evangeliya_url)

        self.assertIsNotNone(property_map)

        # -------------------------------------------------------------------- #
        # Property URLs
        property_urls:list[str] = property_map.get_all_property_urls()
        self.assertIsInstance(property_urls[0], str)
        self.assertEqual(property_urls[0], f"{evangeliya_url}?value")

        # -------------------------------------------------------------------- #
        # Filepaths
        filepaths:list[str] = property_map.get_all_filepaths()

        evan_path:str = evangeliya_url.split("#", maxsplit=1)[0]
        head_path:str = head_morph_url.split("#", maxsplit=1)[0]
        body_path:str = body_morph_url.split("#", maxsplit=1)[0]

        self.assertIn(evan_path, filepaths)
        self.assertIn(head_path, filepaths)
        self.assertIn(body_path, filepaths)

        self.assertTrue(property_map.has_filepath(evan_path))
        self.assertTrue(property_map.has_filepath(head_path))
        self.assertTrue(property_map.has_filepath(body_path))

        # -------------------------------------------------------------------- #
        # Asset IDs
        asset_ids:list[str] = property_map.get_all_asset_ids(evangeliya_url)

        self.assertIn("CTRL-ISTEvangeliya", asset_ids)

        self.assertTrue(property_map.has_asset_id(f"{evan_path}#CTRL-ISTEvangeliya"))
        self.assertTrue(property_map.has_asset_id(evan_path, asset_id="CTRL-ISTEvangeliya"))

        # -------------------------------------------------------------------- #
        # Properties
        property_paths:list[str] = property_map.get_all_property_paths(evangeliya_url)

        self.assertIn("value", property_paths)
        self.assertTrue(property_map.has_property_path(f"{evangeliya_url}?value"))
        self.assertTrue(property_map.has_property_path(evangeliya_url, property_path="value"))

        prop = property_map.get_property_object(f"{evangeliya_url}?value")

        self.assertIsNotNone(prop)
        self.assertEqual(str(prop), f"{evangeliya_url}?value")
        self.assertTrue(prop.is_valid())
        self.assertEqual(prop.get_type(), ChannelType.FLOAT)

        # -------------------------------------------------------------------- #
        # Modifiers
        modifier_urls:list[str] = property_map.get_loaded_modifiers()

        self.assertIn(evangeliya_url, modifier_urls)
        self.assertIn(body_morph_url, modifier_urls)
        self.assertIn(head_morph_url, modifier_urls)

        self.assertTrue(property_map.is_modifier_loaded(evangeliya_url))
        self.assertTrue(property_map.is_modifier_loaded(body_morph_url))
        self.assertTrue(property_map.is_modifier_loaded(head_morph_url))

        modifier_struct:DsonModifier = property_map.get_modifier(evangeliya_url)

        self.assertIsNotNone(modifier_struct)
        self.assertIsInstance(modifier_struct, DsonModifier)
        self.assertEqual(modifier_struct.library_id, "CTRL-ISTEvangeliya")

        # -------------------------------------------------------------------- #
        # Nodes
        node_urls:list[str] = property_map.get_loaded_nodes()

        self.assertIn(g8f_hip_url, node_urls)
        self.assertIn(g8f_head_url, node_urls)

        self.assertTrue(property_map.is_node_loaded(g8f_hip_url))
        self.assertTrue(property_map.is_node_loaded(g8f_head_url))

        node_struct:DsonNode = property_map.get_node(g8f_hip_url)

        self.assertIsNotNone(node_struct)
        self.assertIsInstance(node_struct, DsonNode)
        self.assertEqual(node_struct.library_id, "hip")

        # -------------------------------------------------------------------- #
        # Property values

        self.assertAlmostEqual(property_map.get_property_value(f"{body_morph_url}?value"), 0.0)
        self.assertAlmostEqual(property_map.get_property_value(f"{head_morph_url}?value"), 0.0)

        property_map.set_property_value(f"{evangeliya_url}?value", 1.0)
        self.assertAlmostEqual(property_map.get_property_value(f"{body_morph_url}?value"), 1.0)
        self.assertAlmostEqual(property_map.get_property_value(f"{head_morph_url}?value"), 1.0)

        # -------------------------------------------------------------------- #
        # Morphs

        vertex_count:int = 16556
        morph:DsonMorph = property_map.get_morph_shape(vertex_count)

        self.assertIsNotNone(morph)
        self.assertEqual(morph.expected_vertices, vertex_count)

        # -------------------------------------------------------------------- #
        # Bone positions

        url0:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#lCheekUpperInner?center_point/z"
        url1:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#lBigToe?center_point/z"
        url2:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#lThigh?scale/x"
        url3:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#rLipCorner?center_point/y"
        url4:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#rNasolabialLower?center_point/z"
        url5:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#rSmallToe2?center_point/z"
        url6:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#rCarpal1?center_point/x"
        url7:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#lowerTeeth?center_point/x"
        url8:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#lShldrTwist?end_point/z"
        url9:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#lEyelidLower?center_point/x"

        self.assertAlmostEqual(property_map.get_property_value(url0), 6.95, places=2)
        self.assertAlmostEqual(property_map.get_property_value(url1), 8.07, places=2)
        self.assertAlmostEqual(property_map.get_property_value(url2), 1.00, places=2)
        self.assertAlmostEqual(property_map.get_property_value(url3), 161.63, places=2)
        self.assertAlmostEqual(property_map.get_property_value(url4), 6.79, places=2)
        self.assertAlmostEqual(property_map.get_property_value(url5), 7.68, places=2)
        self.assertAlmostEqual(property_map.get_property_value(url6), -50.80, places=2)
        self.assertAlmostEqual(property_map.get_property_value(url7), -0.037, places=2)
        self.assertAlmostEqual(property_map.get_property_value(url8), -4.46, places=2)
        self.assertAlmostEqual(property_map.get_property_value(url9), 3.28, places=2)

        # -------------------------------------------------------------------- #
        # Bone nodes

        bone_url:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf#lCollar"

        collar_node:DsonNode = property_map.get_adjusted_node(bone_url)

        self.assertIsNotNone(collar_node)
        self.assertIsInstance(collar_node, DsonNode)
        self.assertAlmostEqual(collar_node.center_point.x.current_value, 3.29, places=2)
        self.assertAlmostEqual(collar_node.end_point.x.current_value, 12.74, places=2)

        return
