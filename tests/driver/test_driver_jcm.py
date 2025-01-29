# stdlib
from typing import Self
from unittest import TestCase

# dufman
from dufman.driver.driver_jcm import create_jcm_expression
from dufman.driver.driver_map import DriverMap
from dufman.driver.driver_object import DriverTarget
from dufman.structs.modifier import DsonModifier
from dufman.url import DazUrl

from tests import DEFAULT_CONTENT_DIRECTORY


# ============================================================================ #
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
# ============================================================================ #

class TestDriverJcm(TestCase):

    def setUp(self:Self) -> None:
        DazUrl.add_content_directory(DEFAULT_CONTENT_DIRECTORY)
        return

    def tearDown(self:Self) -> None:
        DazUrl.remove_all_content_directories()
        return


    # ======================================================================== #

    def test_jcm_abdomen(self:Self) -> None:

        # URLs
        morph_url:DazUrl = DazUrl.from_url("/data/DAZ 3D/Genesis 8/Female/Morphs/DAZ 3D/Base Correctives/pJCMAbdomen2Fwd_40.dsf#pJCMAbdomen2Fwd_40")
        bool_url:DazUrl = DazUrl.from_url("/data/DAZ 3D/Genesis 8/Female/Morphs/DAZ 3D/Base/BaseJointCorrectives.dsf#JCMs On")

        # Structs
        morph_struct:DsonModifier = DsonModifier.load_from_file(morph_url)
        bool_struct:DsonModifier = DsonModifier.load_from_file(bool_url)

        # Create DriverMap and load modifiers
        driver_map:DriverMap = DriverMap("Genesis8Female")
        driver_map.load_modifier_driver(morph_url, morph_struct)
        driver_urls:list[DazUrl] = driver_map.get_all_driver_urls()
        self.assertEqual(len(driver_urls), 2)
        self.assertEqual(driver_urls[0].asset_id, "pJCMAbdomen2Fwd_40")
        self.assertEqual(driver_urls[0].channel, "value")
        self.assertEqual(driver_urls[1].asset_id, "abdomen2")
        self.assertEqual(driver_urls[1].channel, "rotation/x")

        # Get DriverTargets
        morph_target:DriverTarget = driver_map.get_driver_target(driver_urls[0])
        bone_target:DriverTarget = driver_map.get_driver_target(driver_urls[1])

        # Check DriverTarget fields
        self.assertEqual(morph_target.format_expression_name(), "pJCMAbdomen2Fwd_40_value")
        self.assertEqual(bone_target.format_expression_name(), "abdomen2_rot_x")

        # Test expression loading
        canonical_expression:str = "(degrees(abdomen2_rot_x) * 0.025)"
        expression, nodes = create_jcm_expression(morph_target)
        self.assertEqual(expression, canonical_expression)
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes, [bone_target])

        # Add bool modifier
        driver_map.load_modifier_driver(bool_url, bool_struct)
        expression, nodes = create_jcm_expression(morph_target)
        self.assertEqual(expression, canonical_expression)
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes, [bone_target])

        # Get bool modifier target
        bool_target:DriverTarget = driver_map.get_driver_target(bool_url)

        # Check expression with bool modifier set to False
        bool_target.set_value(False)
        expression, nodes = create_jcm_expression(morph_target)
        self.assertIsNone(expression)
        self.assertIsNone(nodes)

        return


    # ======================================================================== #

    def test_jcm_abdomen_navel(self:Self) -> None:

        # URLs
        morph_url:DazUrl = DazUrl.from_url("/data/DAZ 3D/Genesis 8/Female/Morphs/DAZ 3D/Base Correctives/pJCMAbdomenLowerFwd_Navel.dsf#pJCMAbdomenLowerFwd_Navel")

        # Structs
        morph_struct:DsonModifier = DsonModifier.load_from_file(morph_url)

        # Create DriverMap and load modifiers
        driver_map:DriverMap = DriverMap("Genesis8Female")
        driver_map.load_modifier_driver(morph_url, morph_struct)
        driver_urls:list[DazUrl] = driver_map.get_all_driver_urls()
        self.assertEqual(len(driver_urls), 3)
        self.assertEqual(driver_urls[0].asset_id, "pJCMAbdomenLowerFwd_Navel")
        self.assertEqual(driver_urls[0].channel, "value")
        self.assertEqual(driver_urls[1].asset_id, "abdomenLower")
        self.assertEqual(driver_urls[1].channel, "rotation/x")
        self.assertEqual(driver_urls[2].asset_id, "PBMNavel")
        self.assertEqual(driver_urls[2].channel, "value")

        # Get DriverTarget
        jcm_target:DriverTarget = driver_map.get_driver_target(driver_urls[0])
        bone_target:DriverTarget = driver_map.get_driver_target(driver_urls[1])
        morph_target:DriverTarget = driver_map.get_driver_target(driver_urls[2])

        # Variables
        canon_exp:str = None

        # Test expression when morph is 0.0
        # The morph should have no effect, so the return values should be None.
        expression, nodes = create_jcm_expression(jcm_target)
        self.assertIsNone(expression)
        self.assertIsNone(nodes)

        # Test expression when morph is 1.0
        morph_target.set_value(1.0)
        canon_exp = "(degrees(abdomenLower_rot_x) * 0.02857143)"
        expression, nodes = create_jcm_expression(jcm_target)
        self.assertEqual(expression, canon_exp)
        self.assertEqual(nodes, [bone_target])

        # Test expression when morph is 0.5
        morph_target.set_value(0.5)
        canon_exp = f"({canon_exp} * 0.5)"
        expression, nodes = create_jcm_expression(jcm_target)
        self.assertEqual(expression, canon_exp)
        self.assertEqual(nodes, [bone_target])

        return


    # ======================================================================== #

    def test_jcm_neck_reverse(self:Self) -> None:

        # URLs
        twist_url:DazUrl = DazUrl.from_url("/data/DAZ 3D/Genesis 8/Female/Morphs/DAZ 3D/Base Correctives/pJCMNeckTwist_22_L.dsf#pJCMNeckTwist_22_L")
        reverse_url:DazUrl = DazUrl.from_url("/data/DAZ 3D/Genesis 8/Female/Morphs/DAZ 3D/Base Correctives/pJCMNeckTwist_Reverse.dsf#pJCMNeckTwist_Reverse")
        bool_url:DazUrl = DazUrl.from_url("/data/DAZ 3D/Genesis 8/Female/Morphs/DAZ 3D/Base/BaseJointCorrectives.dsf#JCMs On")

        # Structs
        twist_struct:DsonModifier = DsonModifier.load_from_file(twist_url)
        reverse_struct:DsonModifier = DsonModifier.load_from_file(reverse_url)
        bool_struct:DsonModifier = DsonModifier.load_from_file(bool_url)

        # Create DriverMap and load modifiers
        driver_map:DriverMap = DriverMap("Genesis8Female")
        driver_map.load_modifier_driver(twist_url, twist_struct)
        driver_map.load_modifier_driver(reverse_url, reverse_struct)

        # Check loaded URLs
        driver_urls:list[str] = driver_map.get_all_driver_urls()

        self.assertEqual(driver_urls[0].asset_id, "pJCMNeckTwist_22_L")
        self.assertEqual(driver_urls[0].channel, "value")
        self.assertEqual(driver_urls[4].asset_id, "pJCMNeckTwist_22_R")
        self.assertEqual(driver_urls[4].channel, "value")
        self.assertEqual(driver_urls[3].asset_id, "pJCMNeckTwist_Reverse")
        self.assertEqual(driver_urls[3].channel, "value")

        self.assertEqual(driver_urls[1].asset_id, "neck")
        self.assertEqual(driver_urls[1].channel, "rotation/y")
        self.assertEqual(driver_urls[2].asset_id, "neck")
        self.assertEqual(driver_urls[2].channel, "rotation/x")

        # Get DriverTargets
        twist_target:DriverTarget = driver_map.get_driver_target(driver_urls[0])
        bone_y:DriverTarget = driver_map.get_driver_target(driver_urls[1])
        bone_x:DriverTarget = driver_map.get_driver_target(driver_urls[2])

        # Test expression
        canon_exp:str = "((degrees(neck_rot_y) * 0.0454546) + ((degrees(neck_rot_x) * 0.025) * -1))"
        expression, nodes = create_jcm_expression(twist_target)
        self.assertEqual(expression, canon_exp)
        self.assertEqual(nodes, [bone_y, bone_x])

        # Ensure bone expressions are None
        expression, nodes = create_jcm_expression(bone_x)
        self.assertIsNone(expression)
        self.assertIsNone(nodes)

        expression, nodes = create_jcm_expression(bone_y)
        self.assertIsNone(expression)
        self.assertIsNone(nodes)

        # Load "JCMs On" for testing
        driver_map.load_modifier_driver(bool_url, bool_struct)

        # Test expression with JCMs on
        expression, nodes = create_jcm_expression(twist_target)
        self.assertEqual(expression, canon_exp)
        self.assertEqual(nodes, [bone_y, bone_x])

        # Turn "JCMs On" off
        bool_target:DriverTarget = driver_map.get_driver_target(bool_url)
        bool_target.set_value(False)

        # Test expression with JCMs off
        expression, nodes = create_jcm_expression(twist_target)
        self.assertIsNone(expression)
        self.assertIsNone(nodes)

        return


    # ======================================================================== #

    def test_jcm_shoulder_front(self:Self) -> None:

        # URLs
        morph_url:DazUrl = DazUrl.from_url("/data/DAZ 3D/Genesis 8/Female/Morphs/DAZ 3D/Base Correctives/pJCMShldrFront_n110_Bend_p90_L.dsf#pJCMShldrFront_n110_Bend_p90_L")

        # Structs
        morph_struct:DsonModifier = DsonModifier.load_from_file(morph_url)

        # Create DriverMap
        driver_map:DriverMap = DriverMap("Genesis8Female")
        driver_map.load_modifier_driver(morph_url, morph_struct)

        # Check target URLs
        driver_urls:list[DazUrl] = driver_map.get_all_driver_urls()
        self.assertIsNotNone(driver_urls)
        self.assertEqual(len(driver_urls), 13)

        self.assertEqual(driver_urls[0].asset_id, "pJCMShldrFront_n110_Bend_p90_L")
        self.assertEqual(driver_urls[0].channel, "value")

        self.assertEqual(driver_urls[1].asset_id, "CTRLMD_N_YRotate_n110")
        self.assertEqual(driver_urls[1].channel, "value")
        self.assertEqual(driver_urls[12].asset_id, "CTRLMD_N_ZRotate_90")
        self.assertEqual(driver_urls[12].channel, "value")

        self.assertEqual(driver_urls[2].asset_id, "lShldr")
        self.assertEqual(driver_urls[2].channel, "rotation/y")
        self.assertEqual(driver_urls[7].asset_id, "lShldr")
        self.assertEqual(driver_urls[7].channel, "rotation/z")

        # Get targets
        morph_target:DriverTarget = driver_map.get_driver_target(morph_url)
        bone_y:DriverTarget = driver_map.get_driver_target(driver_urls[2])
        bone_z:DriverTarget = driver_map.get_driver_target(driver_urls[7])

        # Test morph expression
        canon_exp:str = "((degrees(lShldr_rot_y) * -0.009090909) * (degrees(lShldr_rot_z) * 0.01111111))"
        expression, nodes = create_jcm_expression(morph_target)
        self.assertEqual(expression, canon_exp)
        self.assertEqual(nodes, [bone_y, bone_z])

        # Ensure bone expressions are None
        expression, nodes = create_jcm_expression(bone_y)
        self.assertIsNone(expression)
        self.assertIsNone(nodes)

        expression, nodes = create_jcm_expression(bone_z)
        self.assertIsNone(expression)
        self.assertIsNone(nodes)

        return


    # ======================================================================== #

    def test_jcm_thigh_forward(self:Self) -> None:

        # URLs
        thigh_57_url:DazUrl = DazUrl.from_url("/data/DAZ 3D/Genesis 8/Female/Morphs/DAZ 3D/Base Correctives/pJCMThighFwd_57_L.dsf#pJCMThighFwd_57_L")
        thigh_115_url:DazUrl = DazUrl.from_url("/data/DAZ 3D/Genesis 8/Female/Morphs/DAZ 3D/Base Correctives/pJCMThighFwd_115_L.dsf#pJCMThighFwd_115_L")

        # Structs
        thigh_57_struct:DsonModifier = DsonModifier.load_from_file(thigh_57_url)
        thigh_115_struct:DsonModifier = DsonModifier.load_from_file(thigh_115_url)

        # Create DriverMap and load modifiers
        driver_map:DriverMap = DriverMap("Genesis8Female")
        driver_map.load_modifier_driver(thigh_57_url, thigh_57_struct)
        driver_map.load_modifier_driver(thigh_115_url, thigh_115_struct)

        # Check target URLs
        driver_urls:list[DazUrl] = driver_map.get_all_driver_urls()
        self.assertEqual(len(driver_urls), 211)
        self.assertEqual(driver_urls[0].asset_id, "pJCMThighFwd_57_L")
        self.assertEqual(driver_urls[0].channel, "value")

        # Get targets
        thigh_57_target:DriverTarget = driver_map.get_driver_target(driver_urls[0])
        thigh_115_target:DriverTarget = driver_map.get_driver_target(driver_urls[47])
        bone_target:DriverTarget = driver_map.get_driver_target(driver_urls[1])

        # Test morph expression Thigh-57
        canon_thigh_57:str = "lerp(0, 1, clamp((degrees(lThigh_rot_x) - 0) / (-57 - 0))"
        expression, nodes = create_jcm_expression(thigh_57_target)
        self.assertEqual(expression, canon_thigh_57)
        self.assertEqual(nodes, [bone_target])

        # Test morph expression Thigh-115
        canon_thigh_115:str = "lerp(0, 1, clamp((degrees(lThigh_rot_x) - -57) / (-115 - -57))"
        expression, nodes = create_jcm_expression(thigh_115_target)
        self.assertEqual(expression, canon_thigh_115)
        self.assertEqual(nodes, [bone_target])

        # Ensure bone expression is None
        expression, nodes = create_jcm_expression(bone_target)
        self.assertIsNone(expression)
        self.assertIsNone(nodes)

        return


    # ======================================================================== #

    def test_jcm_neck_forward(self:Self) -> None:

        # URLs
        morph_url:DazUrl = DazUrl.from_url("/data/DAZ 3D/Genesis 8/Female/Morphs/DAZ 3D/Base Correctives/pJCMNeckFwd_35.dsf#pJCMNeckFwd_35")

        # Structs
        morph_struct:DsonModifier = DsonModifier.load_from_file(morph_url)

        # Create DriverMap and load modifiers
        driver_map:DriverMap = DriverMap("Genesis8Female")
        driver_map.load_modifier_driver(morph_url, morph_struct)

        # Check target URLs
        driver_urls:list[DazUrl] = driver_map.get_all_driver_urls()
        self.assertEqual(len(driver_urls), 3)
        self.assertEqual(driver_urls[0].asset_id, "pJCMNeckFwd_35")
        self.assertEqual(driver_urls[0].channel, "value")
        self.assertEqual(driver_urls[1].asset_id, "neck_2")
        self.assertEqual(driver_urls[1].channel, "rotation/x")
        self.assertEqual(driver_urls[2].asset_id, "neck")
        self.assertEqual(driver_urls[2].channel, "rotation/x")

        # Get targets
        morph:DriverTarget = driver_map.get_driver_target(driver_urls[0])
        neck2:DriverTarget = driver_map.get_driver_target(driver_urls[1])
        neck1:DriverTarget = driver_map.get_driver_target(driver_urls[2])

        # Test morph expression
        canon_exp:str = "((degrees(neck_2_rot_x) * 0.0133) + (degrees(neck_rot_x) * 0.021))"
        expression, nodes = create_jcm_expression(morph)
        self.assertEqual(expression, canon_exp)
        self.assertEqual(nodes, [neck2, neck1])

        # Ensure bone expressions are None
        expression, nodes = create_jcm_expression(neck2)
        self.assertIsNone(expression)
        self.assertIsNone(nodes)

        expression, nodes = create_jcm_expression(neck2)
        self.assertIsNone(expression)
        self.assertIsNone(nodes)

        return
