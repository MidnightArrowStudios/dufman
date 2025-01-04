from __future__ import annotations
from unittest import TestCase

from dufman.driver.driver_object import DriverTarget, DriverEquation
from dufman.enums import (
    ChannelType,
    FormulaStage,
    LibraryType,
)
from dufman.file import add_content_directory, remove_content_directory
from dufman.structs.channel import DsonChannel
from dufman.structs.formula import DsonFormula
from dufman.structs.modifier import DsonModifier
from dufman.structs.node import DsonNode

class TestDriverObject(TestCase):

    # ======================================================================== #

    def setUp(self:TestDriverObject) -> None:
        add_content_directory("F:/Daz3D")
        return


    # ------------------------------------------------------------------------ #

    def tearDown(self:TestDriverObject) -> None:
        remove_content_directory("F:/Daz3D")
        return


    # ======================================================================== #

    def test_static_methods(self:TestDriverObject) -> None:

        # Node data
        bone_url:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf#lCollar"
        property_url, library_type = DriverTarget.get_asset_library_info(bone_url, property_path="rotation/x")
        self.assertEqual(property_url, "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#lCollar?rotation/x")
        self.assertEqual(library_type, LibraryType.NODE)

        # DsonNode
        bone_struct:DsonNode = DriverTarget.load_asset(property_url, library_type)
        self.assertIsNotNone(bone_struct)
        self.assertEqual(bone_struct.library_id, "lCollar")

        # Channel
        x_rot:DsonChannel = DriverTarget.get_channel_object(bone_struct, property_url)
        self.assertIsNotNone(x_rot)
        self.assertEqual(x_rot.name, "XRotate")
        self.assertEqual(x_rot.channel_type, ChannelType.FLOAT)

        # Modifier data
        height_url:str = "/data/DAZ 3D/Genesis 8/Female/Morphs/DAZ 3D/Body/FBMHeight.dsf#FBMHeight"
        property_url, library_type = DriverTarget.get_asset_library_info(height_url)
        self.assertEqual(property_url, "/data/DAZ%203D/Genesis%208/Female/Morphs/DAZ%203D/Body/FBMHeight.dsf#FBMHeight?value")
        self.assertEqual(library_type, LibraryType.MODIFIER)

        # DsonModifier
        modifier_struct:DsonModifier = DriverTarget.load_asset(property_url, library_type)
        self.assertIsNotNone(modifier_struct)
        self.assertEqual(modifier_struct.library_id, "FBMHeight")

        # Channel
        value:DsonChannel = DriverTarget.get_channel_object(modifier_struct, property_url)
        self.assertIsNotNone(value)
        self.assertEqual(value.name, "Value")
        self.assertEqual(value.channel_type, ChannelType.FLOAT)

        return


    # ======================================================================== #

    def test_driver_objects(self:TestDriverObject) -> None:

        bone_url:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#abdomenLower"
        jcm_url:str = "/data/DAZ%203D/Genesis%208/Female/Morphs/DAZ%203D/Base%20Correctives/pJCMAbdomenFwd_35.dsf#pJCMAbdomenFwd_35"

        # -------------------------------------------------------------------- #
        # dummy
        dummy_target:DriverTarget = DriverTarget(bone_url, None, None)
        self.assertIsNotNone(dummy_target)
        self.assertIsNone(dummy_target.get_channel_type())
        self.assertFalse(dummy_target.is_valid())
        self.assertRaises(RuntimeError, dummy_target.get_value)
        self.assertRaises(RuntimeError, dummy_target.set_value, 1)

        # -------------------------------------------------------------------- #
        # AbdomenLower

        # node struct
        full_bone_url:str = f"{bone_url}?rotation/x"
        bone_struct:DsonNode = DsonNode.load_from_file(full_bone_url)
        self.assertIsNotNone(bone_struct)

        # driver
        bone_target:DriverTarget = DriverTarget(full_bone_url, bone_struct, LibraryType.NODE)
        self.assertEqual(str(bone_target), full_bone_url)
        self.assertTrue(bone_target.is_valid())
        self.assertEqual(bone_target.get_channel_type(), ChannelType.FLOAT)
        self.assertAlmostEqual(bone_target.get_value(), 0.0)

        # -------------------------------------------------------------------- #
        # pJCMAbdomenFwd_35

        # modifier struct
        full_jcm_url:str = f"{jcm_url}?value"
        jcm_struct:DsonModifier = DsonModifier.load_from_file(full_jcm_url)
        self.assertIsNotNone(jcm_struct)

        # driver
        jcm_target:DriverTarget = DriverTarget(full_jcm_url, jcm_struct, LibraryType.MODIFIER)
        self.assertEqual(str(jcm_target), full_jcm_url)
        self.assertTrue(jcm_target.is_valid())
        self.assertEqual(jcm_target.get_channel_type(), ChannelType.FLOAT)
        self.assertAlmostEqual(jcm_target.get_value(), 0.0)

        # value update
        jcm_target.set_value(1.0)
        self.assertAlmostEqual(jcm_target.get_value(), 1.0)
        jcm_target.set_value(0.0)

        # -------------------------------------------------------------------- #
        # DriverEquation

        # formula struct
        form_struct:DsonFormula = jcm_struct.formulas[0]
        self.assertIsNotNone(form_struct)

        input_url:str = form_struct.operations[0].url

        # driver
        equation:DriverEquation = DriverEquation(form_struct)
        self.assertIsNotNone(equation)
        self.assertEqual(equation.get_stage(), FormulaStage.SUM)

        # Assign relationships
        equation.inputs[input_url] = bone_target
        equation.output = jcm_target
        bone_target.subcomponents.append(equation)
        jcm_target.controllers.append(equation)

        # update hierarchical values
        bone_target.set_value(35.0)
        self.assertAlmostEqual(jcm_target.get_value(), 1.0)

        # -------------------------------------------------------------------- #

        return
