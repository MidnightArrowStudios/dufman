# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""Unit testing functions for the DUFMan package."""

from typing import Self
from unittest import TestCase

from dufman.enums import (
    ChannelType,
    EdgeInterpolation,
    FormulaOperator,
    FormulaStage,
    GeometryType,
    NodeType,
    RigidRotation,
    RigidScale,
    RotationOrder,
)
from dufman.file import add_content_directory, remove_content_directory
from dufman.library import get_single_property_from_library
from dufman.observers import (
    register_on_geometry_struct_created,
    register_on_modifier_struct_created,
    register_on_node_struct_created,
    register_on_uv_set_struct_created,
)
from dufman.structs.asset_info import DsonAssetInfo
from dufman.structs.bulge_binding import DsonBulgeWeights
from dufman.structs.channel import DsonChannelFloat, DsonChannelVector
from dufman.structs.contributor import DsonContributor
from dufman.structs.formula import DsonFormula
from dufman.structs.graft import DsonGraft
from dufman.structs.geometry import DsonGeometry
from dufman.structs.modifier import DsonModifier
from dufman.structs.morph import DsonMorph
from dufman.structs.named_string_map import DsonNamedStringMap
from dufman.structs.node import DsonNode
from dufman.structs.presentation import DsonPresentation
from dufman.structs.region import DsonRegion
from dufman.structs.rigidity import DsonRigidity, _Group
from dufman.structs.skin_binding import DsonSkinBinding
from dufman.structs.uv_set import DsonUVSet, _Hotswap, _Coordinate
from dufman.structs.weighted_joint import DsonWeightedJoint
from dufman.types import DsonColor


class TestStruct(TestCase):
    """Unit testing for the DUFMan package's data structs."""

    def setUp(self:Self) -> None:
        add_content_directory("F:/Daz3D")
        return


    def tearDown(self:Self) -> None:
        remove_content_directory("F:/Daz3D")
        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_asset_info(self:Self) -> None:
        """Unit testing method for DsonAssetInfo."""

        url:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf"
        json:dict = get_single_property_from_library(url, ["asset_info"])
        struct:DsonAssetInfo = DsonAssetInfo.load(json)

        self.assertIsNotNone(struct)

        self.assertEqual(struct.asset_id, "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf")
        self.assertEqual(struct.asset_type, "figure")
        self.assertEqual(struct.revision, "1.0")
        self.assertEqual(struct.modified, "2017-05-15T17:10:58Z")

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_bulge_binding(self:Self) -> None:
        """Unit testing method for DsonBulgeBinding."""

        url:str = "/data/DAZ%203D/DAZ%20Horse%202/Base/DAZHorse2.dsf"
        json:dict = get_single_property_from_library(url, [ "modifier_library", 0, "skin", "joints", "rHoofFore", "bulge_weights" ])
        struct:DsonBulgeWeights = DsonBulgeWeights.load(json)

        # Bulge X
        self.assertIsNotNone(struct.bulge_x)

        self.assertEqual(struct.bulge_x.positive_left.name, "XBulgePosLeft")
        self.assertEqual(struct.bulge_x.positive_right.name, "XBulgePosRight")
        self.assertEqual(struct.bulge_x.negative_left.name, "XBulgeNegLeft")
        self.assertEqual(struct.bulge_x.negative_right.name, "XBulgeNegRight")

        self.assertEqual(len(struct.bulge_x.left_map), 93)
        self.assertIn(21477, struct.bulge_x.left_map)
        self.assertIn(21745, struct.bulge_x.left_map)
        self.assertAlmostEqual(struct.bulge_x.left_map[21477], 0.02221714)
        self.assertAlmostEqual(struct.bulge_x.left_map[21745], 0.5010605)

        self.assertEqual(len(struct.bulge_x.right_map), 50)
        self.assertIn(21478, struct.bulge_x.right_map)
        self.assertIn(21745, struct.bulge_x.right_map)
        self.assertAlmostEqual(struct.bulge_x.right_map[21478], 1.525902e-05)
        self.assertAlmostEqual(struct.bulge_x.right_map[21745], 0.2325017)

        # Bulge Y
        self.assertIsNone(struct.bulge_y)

        # Bulge Z
        self.assertIsNone(struct.bulge_z)

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_channel_float(self:Self) -> None:
        """Unit testing method for DsonChannelFloat."""

        url:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf"
        json:dict = get_single_property_from_library(url, [ "node_library", "Genesis8Female", "general_scale" ])
        struct:DsonChannelFloat = DsonChannelFloat.load(json)

        self.assertIsNotNone(struct)

        self.assertEqual(struct.channel_id, "general_scale")
        self.assertEqual(struct.channel_type, ChannelType.FLOAT)
        self.assertEqual(struct.name, "Scale")
        self.assertEqual(struct.label, "Scale")
        self.assertTrue(struct.auto_follow)
        self.assertAlmostEqual(struct.default_value, 1)
        self.assertAlmostEqual(struct.minimum_value, -10000)
        self.assertAlmostEqual(struct.maximum_value, 10000)
        self.assertTrue(struct.display_as_percent)
        self.assertAlmostEqual(struct.value_increment, 0.005)

        return


    # ======================================================================== #

    def test_channel_vector(self:Self) -> None:
        """Unit testing method for DsonChannelVector."""

        url:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf"
        json:dict = get_single_property_from_library(url, [ "node_library", "Genesis8Female", "scale" ])
        struct:DsonChannelVector = DsonChannelVector.load(json)

        self.assertIsNotNone(struct)

        def check_axis(channel:DsonChannelFloat, channel_id:str, name:str, label:str):
            self.assertEqual(channel.channel_id, channel_id)
            self.assertEqual(channel.channel_type, ChannelType.FLOAT)
            self.assertEqual(channel.name, name)
            self.assertEqual(channel.label, label)
            self.assertFalse(channel.visible)
            self.assertTrue(channel.locked)
            self.assertTrue(channel.auto_follow)
            self.assertAlmostEqual(channel.default_value, 1)
            self.assertAlmostEqual(channel.minimum_value, -10000)
            self.assertAlmostEqual(channel.maximum_value, 10000)
            self.assertTrue(channel.display_as_percent)
            self.assertAlmostEqual(channel.value_increment, 0.005)
            return

        check_axis(struct.x, "x", "XScale", "X Scale")
        check_axis(struct.y, "y", "YScale", "Y Scale")
        check_axis(struct.z, "z", "ZScale", "Z Scale")

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_contributor(self:Self) -> None:
        """Unit testing method for DsonContributor."""

        url:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf"
        json:dict = get_single_property_from_library(url, ["asset_info", "contributor"])
        struct:DsonContributor = DsonContributor.load(json)

        self.assertIsNotNone(struct)

        self.assertEqual(struct.author, "Daz 3D")
        self.assertEqual(struct.website, "www.daz3d.com")

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_formula(self:Self) -> None:
        """Unit testing method for DsonFormula."""

        url:str = "/data/DAZ 3D/Genesis 8/Female/Morphs/iSourceTextures/Evangeliya/CTRL-ISTEvangeliya.dsf"
        json:dict = get_single_property_from_library(url, [ "modifier_library", "CTRL-ISTEvangeliya", "formulas" ])
        structs:list[DsonFormula] = DsonFormula.load(json)

        self.assertIsNotNone(structs)
        self.assertEqual(len(structs), 2)

        self.assertEqual(structs[0].output,
            "Genesis8Female:/data/DAZ%203D/Genesis%208/Female/Morphs/iSourceTextures/Evangeliya/FHM-ISTEvangeliya.dsf#FHM-ISTEvangeliya?value")
        self.assertEqual(structs[1].output,
            "Genesis8Female:/data/DAZ%203D/Genesis%208/Female/Morphs/iSourceTextures/Evangeliya/FBM-ISTEvangeliya.dsf#FBM-ISTEvangeliya?value")

        for struct in structs:
            self.assertEqual(struct.stage, FormulaStage.SUM)
            self.assertEqual(len(struct.operations), 3)

            self.assertEqual(struct.operations[0].operator, FormulaOperator.PUSH)
            self.assertEqual(struct.operations[0].url, "Genesis8Female:#CTRL-ISTEvangeliya?value")

            self.assertEqual(struct.operations[1].operator, FormulaOperator.PUSH)
            self.assertAlmostEqual(struct.operations[1].value, 1)

            self.assertEqual(struct.operations[2].operator, FormulaOperator.MULT)

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_geometry(self:Self) -> None:
        """Unit testing method for DsonGeometry."""

        def callback(_user_data:dict, _struct:DsonGeometry, geometry_json:dict) -> None:
            self.assertEqual(geometry_json["id"], _user_data["id"])
            return

        register_on_geometry_struct_created(callback, {"id":"geometry"})

        url:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf#geometry"
        struct:DsonGeometry = DsonGeometry.load(url)

        self.assertIsNotNone(struct)

        # Naming
        self.assertEqual(struct.library_id, "geometry")
        self.assertEqual(struct.name, "geometry")
        self.assertEqual(struct.geometry_type, GeometryType.SUBDIVISION_SURFACE)
        self.assertEqual(struct.edge_interpolation, EdgeInterpolation.EDGES_ONLY)

        # Vertices
        self.assertEqual(len(struct.vertices), 16556)
        self.assertAlmostEqual(struct.vertices[0].x, 0)
        self.assertAlmostEqual(struct.vertices[0].y, 111.993)
        self.assertAlmostEqual(struct.vertices[0].z, 11.0073)
        self.assertAlmostEqual(struct.vertices[16555].x, -2.40592)
        self.assertAlmostEqual(struct.vertices[16555].y, 168.627)
        self.assertAlmostEqual(struct.vertices[16555].z, 4.91007)

        # Polygons
        self.assertEqual(len(struct.polygons), 16368)
        self.assertListEqual(list(struct.polygons[0]), [1594, 2551, 841, 1596])
        self.assertListEqual(list(struct.polygons[16367]), [16552, 16554, 16099, 16102])

        # Materials
        self.assertEqual(struct.material_indices[0], 0)
        self.assertEqual(struct.material_indices[16367], 10)

        self.assertEqual(len(struct.material_names), 16)
        self.assertEqual(struct.material_names[0], "Torso")
        self.assertEqual(struct.material_names[15], "Toenails")

        # Face groups
        self.assertEqual(struct.face_group_indices[0], 0)
        self.assertEqual(struct.face_group_indices[16367], 60)

        self.assertEqual(len(struct.face_group_names), 61)
        self.assertEqual(struct.face_group_names[0], "lPectoral")
        self.assertEqual(struct.face_group_names[60], "rEye")

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_graft(self:Self) -> None:
        """Unit testing method for DsonGraft."""

        url:str = "/data/DAZ 3D/Genesis 8 Centaur/G8Female Centaur/G8FCentaur.dsf"
        json:dict = get_single_property_from_library(url, [ "geometry_library", "G8FCentaur-1", "graft" ])
        struct:DsonGraft = DsonGraft.load(json)

        self.assertIsNotNone(struct)

        self.assertEqual(struct.expected_vertices, 16556)
        self.assertEqual(struct.expected_polygons, 16368)

        self.assertEqual(len(struct.vertex_pairs), 136)
        self.assertEqual(struct.vertex_pairs[0].source, 32)
        self.assertEqual(struct.vertex_pairs[0].target, 44)
        self.assertEqual(struct.vertex_pairs[135].source, 24814)
        self.assertEqual(struct.vertex_pairs[135].target, 3227)

        self.assertEqual(len(struct.hidden_polygons), 4566)
        self.assertEqual(struct.hidden_polygons[0], 3324)
        self.assertEqual(struct.hidden_polygons[4565], 16319)

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_modifier(self:Self) -> None:
        """Unit testing method for DsonModifier."""

        def callback(_user_data:dict, _struct:DsonModifier, modifier_json:dict) -> None:
            self.assertEqual(modifier_json["id"], _user_data["id"])
            return

        register_on_modifier_struct_created(callback, {"id":"CTRL-ISTEvangeliya"})

        url:str = "/data/DAZ 3D/Genesis 8/Female/Morphs/iSourceTextures/Evangeliya/CTRL-ISTEvangeliya.dsf#CTRL-ISTEvangeliya"
        struct:DsonModifier = DsonModifier.load(url)

        self.assertIsNotNone(struct)

        self.assertEqual(struct.name, "CTRL-ISTEvangeliya")
        self.assertEqual(struct.parent, "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#Genesis8Female")
        self.assertEqual(struct.presentation.content_type, "Modifier/Shape")
        self.assertEqual(struct.presentation.icon_large, "/data/DAZ%203D/Genesis%208/Female/Morphs/iSourceTextures/Evangeliya/CTRL-ISTEvangeliya.png")
        self.assertEqual(struct.channel.name, "CTRL-ISTEvangeliya")
        self.assertEqual(struct.region, "Actor")
        self.assertEqual(struct.group, "/People/Real World")

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_morph(self:Self) -> None:
        """Unit testing method for DsonMorph."""

        url:str = "/data/DAZ 3D/Genesis 8/Female/Morphs/DAZ 3D/Base Correctives/pJCMAbdomen2Fwd_40.dsf"
        json:dict = get_single_property_from_library(url, [ "modifier_library", "pJCMAbdomen2Fwd_40", "morph" ])
        struct:DsonMorph = DsonMorph.load(json)

        self.assertIsNotNone(struct)

        self.assertEqual(struct.expected_vertices, 16556)
        self.assertEqual(len(struct.deltas), 774)

        self.assertIn(0, struct.deltas)
        self.assertAlmostEqual(struct.deltas[0].x, 0)
        self.assertAlmostEqual(struct.deltas[0].y, -0.3170013)
        self.assertAlmostEqual(struct.deltas[0].z, 1.9065)

        self.assertIn(12071, struct.deltas)
        self.assertAlmostEqual(struct.deltas[12071].x, -0.149706)
        self.assertAlmostEqual(struct.deltas[12071].y, -0.4710007)
        self.assertAlmostEqual(struct.deltas[12071].z, 1.465001)

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_named_string_map(self:Self) -> None:
        """Unit testing method for DsonNamedStringMap."""

        url:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf"
        json:dict = get_single_property_from_library(url, [ "modifier_library", "SkinBinding", "skin", "selection_map", 0 ])
        struct:DsonNamedStringMap = DsonNamedStringMap.load(json)

        self.assertIsNotNone(struct)

        self.assertEqual(struct.map_id, "Genesis8Female_selMap")
        self.assertEqual(len(struct.mappings), 61)
        self.assertEqual(struct.mappings[0].face_name, "lCollar")
        self.assertEqual(struct.mappings[0].node_name, "lCollar")
        self.assertEqual(struct.mappings[55].face_name, "Abdomen")
        self.assertEqual(struct.mappings[55].node_name, "abdomenLower")
        self.assertEqual(struct.mappings[60].face_name, "rEye")
        self.assertEqual(struct.mappings[60].node_name, "rEye")

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_node(self:Self) -> None:
        """Unit testing method for DsonNode."""

        def callback(_user_data:dict, _struct:DsonGeometry, node_json:dict) -> None:
            self.assertEqual(node_json["id"], _user_data["id"])
            return

        register_on_node_struct_created(callback, {"id":"lThighTwist"})

        url:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf#lThighTwist"
        struct:DsonNode = DsonNode.load(url)

        self.assertIsNotNone(struct)

        self.assertEqual(struct.name, "lThighTwist")
        self.assertEqual(struct.node_type, NodeType.BONE)
        self.assertEqual(struct.label, "Left Thigh Twist")
        self.assertEqual(struct.parent, "#lThigh")
        self.assertEqual(struct.rotation_order, RotationOrder.YZX)
        self.assertFalse(struct.inherits_scale, False)

        # Center point
        self.assertAlmostEqual(struct.center_point.x.current_value, 10.78465)
        self.assertAlmostEqual(struct.center_point.y.current_value, 75.66734)
        self.assertAlmostEqual(struct.center_point.z.current_value, -0.04346678)

        # End point
        self.assertAlmostEqual(struct.end_point.x.current_value, 13.7365)
        self.assertAlmostEqual(struct.end_point.y.current_value, 54.19333)
        self.assertAlmostEqual(struct.end_point.z.current_value, -0.6480957)

        # Orientation
        self.assertAlmostEqual(struct.orientation.x.current_value, 1.163925)
        self.assertAlmostEqual(struct.orientation.y.current_value, 4.855467)
        self.assertAlmostEqual(struct.orientation.z.current_value, 7.945159)

        # Rotation
        self.assertAlmostEqual(struct.rotation.y.minimum_value, -75)
        self.assertAlmostEqual(struct.rotation.y.maximum_value, 75)

        # Translation
        self.assertAlmostEqual(struct.translation.x.current_value, 0)
        self.assertAlmostEqual(struct.translation.y.current_value, 0)
        self.assertAlmostEqual(struct.translation.z.current_value, 0)

        # Scale
        self.assertAlmostEqual(struct.scale.x.value_increment, 0.005)
        self.assertAlmostEqual(struct.scale.y.value_increment, 0.005)
        self.assertAlmostEqual(struct.scale.z.value_increment, 0.005)

        # General scale
        self.assertAlmostEqual(struct.general_scale.current_value, 1)

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_presentation(self:Self) -> None:
        """Unit testing method for DsonPresentation."""

        url:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf"
        json:dict = get_single_property_from_library(url, [ "node_library", "Genesis8Female", "presentation" ])
        struct:DsonPresentation = DsonPresentation.load(json)

        self.assertIsNotNone(struct)
        self.assertEqual(struct.content_type, "Actor/Character")
        self.assertEqual(struct.label, "")
        self.assertEqual(struct.description, "")
        self.assertEqual(struct.icon_large, "")

        color1:DsonColor = struct.color1
        self.assertAlmostEqual(color1.r, 0.3529412)
        self.assertAlmostEqual(color1.g, 0.3529412)
        self.assertAlmostEqual(color1.b, 0.3529412)

        color2:DsonColor = struct.color2
        self.assertAlmostEqual(color2.r, 1)
        self.assertAlmostEqual(color2.g, 1)
        self.assertAlmostEqual(color2.b, 1)

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_region(self:Self) -> None:
        """Unit testing method for DsonRegion."""

        url:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf"
        json:dict = get_single_property_from_library(url, [ "geometry_library", "geometry", "root_region" ])
        structs:list[DsonRegion] = DsonRegion.load(json)

        self.assertIsNotNone(structs)
        self.assertEqual(len(structs), 16)

        loaded_ids:list[str] = list(struct.id for struct in structs)
        loaded_labels:list[str] = list(struct.label for struct in structs)
        compare_strings:list[str] = [ "Actor", "Head", "Face", "Eyes", "Nose",
                    "Mouth", "Ears", "Hip", "Legs", "Feet", "Arms",
                    "Back", "Chest", "Hands", "Waist", "Neck" ]

        self.assertListEqual(loaded_ids, compare_strings)
        self.assertListEqual(loaded_labels, compare_strings)

        self.assertEqual(structs[0].display_hint, "cards_on")
        self.assertListEqual([ struct.display_hint for struct in structs[1:] ], [ "cards_off" ] * 15 )

        self.assertEqual(len(structs[0].face_indices), 2286)
        self.assertEqual(structs[0].face_indices[0], 14082)
        self.assertEqual(structs[0].face_indices[2285], 16367)

        for parent in structs:
            for child in parent.children:
                self.assertIs(child.parent, parent)

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_rigidity(self:Self) -> None:
        """Unit testing method for DsonRigidity."""

        url:str = "/data/Mada/Nyx/Nyx_Dress/V6O2_Dress.dsf"
        json:dict = get_single_property_from_library(url, [ "geometry_library", "Nyx_Dress", "rigidity" ])
        struct:DsonRigidity = DsonRigidity.load(json)

        self.assertIsNotNone(struct)

        # Weights
        self.assertEqual(len(struct.weights), 1706)
        self.assertIn(4687, struct.weights)
        self.assertIn(27980, struct.weights)
        self.assertEqual(struct.weights[4687], 1)
        self.assertEqual(struct.weights[27980], 1)

        # Groups
        self.assertEqual(len(struct.groups), 1)

        group:_Group = struct.groups[0]

        self.assertEqual(group.group_id, "Broach")

        self.assertEqual(group.rotation, RigidRotation.NONE)
        self.assertEqual(group.scale_x, RigidScale.NONE)
        self.assertEqual(group.scale_y, RigidScale.NONE)
        self.assertEqual(group.scale_z, RigidScale.NONE)

        self.assertEqual(len(group.reference_vertices), 77)
        self.assertEqual(group.reference_vertices[0], 1810)
        self.assertEqual(group.reference_vertices[76], 9494)

        self.assertEqual(len(group.participant_vertices), 1706)
        self.assertEqual(group.participant_vertices[0], 26669)
        self.assertEqual(group.participant_vertices[1705], 5080)

        self.assertEqual(group.reference, "#chest")

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_skin_binding(self:Self) -> None:

        url:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf"
        json:dict = get_single_property_from_library(url, [ "modifier_library", "SkinBinding", "skin" ])
        struct:DsonSkinBinding = DsonSkinBinding.load(json)

        self.assertIsNotNone(struct)

        self.assertEqual(struct.node, "#Genesis8Female")
        self.assertEqual(struct.geometry, "#geometry")
        self.assertEqual(struct.expected_vertices, 16556)

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_uv_set(self:Self) -> None:
        """Unit testing method for DsonUVSet."""

        def callback(_user_data:dict, _struct:DsonUVSet, uv_set_json:dict) -> None:
            self.assertEqual(uv_set_json["id"], _user_data["id"])
            return

        register_on_uv_set_struct_created(callback, {"id": "Base Female"})

        url:str = "/data/DAZ 3D/Genesis 8/Female/UV Sets/DAZ 3D/Base/Base Female.dsf#Base Female"
        struct:DsonUVSet = DsonUVSet.load(url)

        self.assertIsNotNone(struct)

        self.assertEqual(struct.library_id, "Base Female")
        self.assertEqual(struct.name, "Base Female")
        self.assertEqual(struct.label, "Base Female")
        self.assertEqual(struct.expected_vertices, 16556)

        # Coordinates
        self.assertEqual(len(struct.uv_coordinates), 18332)
        self.assertIsInstance(struct.uv_coordinates[0], _Coordinate)
        self.assertAlmostEqual(struct.uv_coordinates[0].x, 1.5)
        self.assertAlmostEqual(struct.uv_coordinates[0].y, 0.318154)
        self.assertIsInstance(struct.uv_coordinates[18331], _Coordinate)
        self.assertAlmostEqual(struct.uv_coordinates[18331].x, 2.48818)
        self.assertAlmostEqual(struct.uv_coordinates[18331].y, 0.251876)

        # Hotswap
        self.assertEqual(len(struct.hotswap_indices), 1924)

        self.assertEqual(len(struct.hotswap_indices[177]), 2)
        self.assertIsInstance(struct.hotswap_indices[177][0], _Hotswap)
        self.assertListEqual(struct.hotswap(177, [2]), [ 17046 ])

        self.assertEqual(len(struct.hotswap_indices[15252]), 2)
        self.assertIsInstance(struct.hotswap_indices[15252][0], _Hotswap)
        self.assertListEqual(struct.hotswap(15252, [16535]), [ 17921 ])

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_weighted_joint(self:Self) -> None:

        url:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf"
        json:list = get_single_property_from_library(url, [ "modifier_library", "SkinBinding", "skin", "joints", 0 ])
        struct:DsonWeightedJoint = DsonWeightedJoint.load(json)

        self.assertIsNotNone(struct)

        self.assertEqual(struct.joint_id, "lIndex3")
        self.assertEqual(struct.node, "#lIndex3")
        self.assertEqual(len(struct.node_weights), 152)

        self.assertIn(1016, struct.node_weights)
        self.assertAlmostEqual(struct.node_weights[1016], 0.5418784)
        self.assertIn(14343, struct.node_weights)
        self.assertAlmostEqual(struct.node_weights[14343], 1)

        return
