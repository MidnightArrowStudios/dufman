# stdlib
from typing import Self
from unittest import TestCase

# dufman
from dufman.driver.driver_map import DriverMap
from dufman.driver.driver_object import DriverEquation, DriverTarget
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

    def test_blender_equation(self:Self) -> None:

        url_string:str = "/data/DAZ 3D/Genesis 8/Female/Morphs/DAZ 3D/Base Correctives/pJCMChestFwd_35.dsf#pJCMChestFwd_35"
        daz_url:DazUrl = DazUrl.from_url(url_string)

        # Create modifier
        struct:DsonModifier = DsonModifier.load_from_file(daz_url)
        self.assertIsNotNone(struct)

        # Create and load DriverMap
        driver_map:DriverMap = DriverMap("Genesis8Female")
        driver_map.load_modifier_driver(daz_url, struct)
        
        target:DriverTarget = driver_map.get_driver_target(daz_url)
        equation:DriverEquation = target._controllers[0]
        
        print(equation.get_blender_expression())


        return
