# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

# stdlib
from pathlib import Path
from typing import Any, Callable, Self
from unittest import TestCase

# dufman
from dufman.enums import LibraryType
from dufman.url import DazUrl

from tests import DEFAULT_CONTENT_DIRECTORY


# ============================================================================ #
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
# ============================================================================ #

class TestUrlModule(TestCase):
    """Unit testing for DUFMan's URL functions."""


    def setUp(self:Self) -> None:
        DazUrl.remove_all_content_directories()
        DazUrl.clear_dsf_cache()
        return


    def tearDown(self:Self) -> None:
        DazUrl.remove_all_content_directories()
        DazUrl.clear_dsf_cache()
        return


    # ======================================================================== #
    # CONTENT DIRECTORY TESTS                                                  #
    # ======================================================================== #

    def test_add_content_directory(self:Self) -> None:

        cont_dirs:list[Path] = None

        DazUrl.remove_all_content_directories()

        # Add string
        DazUrl.add_content_directory(DEFAULT_CONTENT_DIRECTORY)
        cont_dirs = DazUrl.get_content_directories()
        self.assertEqual(len(cont_dirs), 1)
        self.assertEqual(cont_dirs[0], Path(DEFAULT_CONTENT_DIRECTORY))
        self.assertNotEqual(cont_dirs[0], DEFAULT_CONTENT_DIRECTORY)

        # Add Path object
        DazUrl.add_content_directory(Path(DEFAULT_CONTENT_DIRECTORY))
        cont_dirs = DazUrl.get_content_directories()
        self.assertEqual(len(cont_dirs), 1)
        self.assertEqual(cont_dirs[0], Path(DEFAULT_CONTENT_DIRECTORY))
        self.assertNotEqual(cont_dirs[0], DEFAULT_CONTENT_DIRECTORY)

        DazUrl.remove_all_content_directories()

        return


    # ------------------------------------------------------------------------ #

    def test_add_content_directory_trailing_slash(self:Self) -> None:

        # Setup
        DazUrl.remove_all_content_directories()

        get_cont_dir:Callable = DazUrl.get_content_directories

        original_count:int = len(get_cont_dir())

        no_slash:str = "C:/Files/Daz3D"
        DazUrl.add_content_directory(no_slash)
        self.assertIn(Path(no_slash), get_cont_dir())
        self.assertEqual(len(get_cont_dir()), original_count + 1)

        yes_slash:str = "C:/Files/Daz3D/"
        DazUrl.add_content_directory(yes_slash)
        self.assertIn(Path(yes_slash), get_cont_dir())
        self.assertEqual(len(get_cont_dir()), original_count + 1)

        DazUrl.remove_content_directory(no_slash)
        DazUrl.remove_content_directory(yes_slash)
        self.assertEqual(len(get_cont_dir()), original_count)

        return


    # ------------------------------------------------------------------------ #

    def test_remove_content_directory(self:Self) -> None:

        cont_dirs:list[Path] = None

        DazUrl.remove_all_content_directories()

        # Remove string
        DazUrl.add_content_directory(Path(DEFAULT_CONTENT_DIRECTORY))
        DazUrl.remove_content_directory(DEFAULT_CONTENT_DIRECTORY)
        cont_dirs = DazUrl.get_content_directories()
        self.assertEqual(len(cont_dirs), 0)

        # Remove Path
        DazUrl.add_content_directory(Path(DEFAULT_CONTENT_DIRECTORY))
        DazUrl.remove_content_directory(Path(DEFAULT_CONTENT_DIRECTORY))
        cont_dirs = DazUrl.get_content_directories()
        self.assertEqual(len(cont_dirs), 0)

        DazUrl.remove_all_content_directories()

        return


    # ======================================================================== #
    # DSF CACHE TESTS                                                          #
    # ======================================================================== #

    def test_dsf_file_caching(self:Self) -> None:

        # Setup
        DazUrl.clear_dsf_cache()
        DazUrl.remove_all_content_directories()
        DazUrl.add_content_directory(DEFAULT_CONTENT_DIRECTORY)

        # URLs
        g8f_url:DazUrl = DazUrl.from_parts(filepath="/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf")

        # Cache is empty
        dson_file:dict = None
        self.assertEqual(DazUrl.get_cached_file_count(), 0)

        # Open file, but don't cache it
        dson_file = DazUrl.handle_dsf_file(g8f_url, should_cache=False)
        self.assertIsNotNone(dson_file)
        self.assertEqual(DazUrl.get_cached_file_count(), 0)

        # Open file and cache it
        dson_file = DazUrl.handle_dsf_file(g8f_url)
        self.assertIsNotNone(dson_file)
        self.assertEqual(DazUrl.get_cached_file_count(), 1)

        # Empty cache
        DazUrl.clear_dsf_cache()
        self.assertEqual(DazUrl.get_cached_file_count(), 0)

        # Cleanup
        DazUrl.clear_dsf_cache()
        DazUrl.remove_all_content_directories()

        return


    # ------------------------------------------------------------------------ #

    def test_dsf_cache_memory_limit(self:Self) -> None:

        # Setup
        DazUrl.clear_dsf_cache()
        DazUrl.remove_all_content_directories()
        DazUrl.add_content_directory(DEFAULT_CONTENT_DIRECTORY)

        # URLs
        g8f_url:DazUrl = DazUrl.from_url("/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf")

        # Variables
        dson_file:dict = None

        # Open file without limits
        # NOTE: 17 MB determined by testing. May need tweaking?
        dson_file = DazUrl.handle_dsf_file(g8f_url)
        self.assertIsNotNone(dson_file)
        self.assertGreater(DazUrl.get_cache_memory_consumption(), 17000000)
        DazUrl.clear_dsf_cache()

        # Open file with 10 MB limit
        dson_file = DazUrl.handle_dsf_file(g8f_url, memory_limit=10000000)
        self.assertIsNotNone(dson_file)
        self.assertEqual(DazUrl.get_cache_memory_consumption(), 0)

        # Cleanup
        DazUrl.clear_dsf_cache()
        DazUrl.remove_all_content_directories()

        return


    # ======================================================================== #
    # FORMATING METHODS                                                        #
    # ======================================================================== #

    def test_format_filepath(self:Self) -> None:

        canonical:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf"

        # Test forwardslash, unquoted
        url1:str = "data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf"
        url2:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf"

        self.assertEqual(canonical, DazUrl.format_filepath(url1))
        self.assertEqual(canonical, DazUrl.format_filepath(url2))

        # Test single backslash, unquoted
        url3:str = r"data\DAZ 3D\Genesis 8\Female\Genesis8Female.dsf"
        url4:str = r"\data\DAZ 3D\Genesis 8\Female\Genesis8Female.dsf"

        self.assertEqual(canonical, DazUrl.format_filepath(url3))
        self.assertEqual(canonical, DazUrl.format_filepath(url4))

        # Test double backslash, unquoted
        url5:str = "data\\DAZ 3D\\Genesis 8\\Female\\Genesis8Female.dsf"
        url6:str = "\\data\\DAZ 3D\\Genesis 8\\Female\\Genesis8Female.dsf"

        self.assertEqual(canonical, DazUrl.format_filepath(url5))
        self.assertEqual(canonical, DazUrl.format_filepath(url6))

        # Test forwardslash, quoted
        url7:str = "data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf"
        url8:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf"

        self.assertEqual(canonical, DazUrl.format_filepath(url7))
        self.assertEqual(canonical, DazUrl.format_filepath(url8))

        # Test single backslash, quoted
        url9:str = r"data\DAZ%203D\Genesis%208\Female\Genesis8Female.dsf"
        url10:str = r"\data\DAZ%203D\Genesis%208\Female\Genesis8Female.dsf"

        self.assertEqual(canonical, DazUrl.format_filepath(url9))
        self.assertEqual(canonical, DazUrl.format_filepath(url10))

        # Test double backslash, quoted
        url11:str = "data\\DAZ%203D\\Genesis%208\\Female\\Genesis8Female.dsf"
        url12:str = "\\data\\DAZ%203D\\Genesis%208\\Female\\Genesis8Female.dsf"

        self.assertEqual(canonical, DazUrl.format_filepath(url11))
        self.assertEqual(canonical, DazUrl.format_filepath(url12))

        # Test leading slash
        self.assertEqual(canonical[1:], DazUrl.format_filepath(canonical, has_leading_slash=False))

        # Test unquoted
        self.assertEqual(url2, DazUrl.format_filepath(canonical, is_quoted=False))

        # Test unquoted and leading slash
        self.assertEqual(url1, DazUrl.format_filepath(canonical, is_quoted=False, has_leading_slash=False))

        return


    # ------------------------------------------------------------------------ #

    def test_format_url(self:Self) -> None:

        # URL parts
        node_name:str = "Genesis8Female"
        filepath:str = "data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf"
        asset_id:str = "hip"
        channel:str = "rotation/x"

        # Variables
        url:str = None

        # Filepath only
        url = DazUrl.format_url(filepath=filepath)
        self.assertEqual(url, "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf")

        # Filepath and asset ID
        url = DazUrl.format_url(filepath=filepath, asset_id=asset_id)
        self.assertEqual(url, "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#hip")

        # Filepath, asset ID, and channel
        url = DazUrl.format_url(filepath=filepath, asset_id=asset_id, channel=channel)
        self.assertEqual(url, "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#hip?rotation/x")

        # All components
        url = DazUrl.format_url(node_name=node_name, filepath=filepath, asset_id=asset_id, channel=channel)
        self.assertEqual(url, "Genesis8Female:/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#hip?rotation/x")

        # Formula URL
        url = DazUrl.format_url(node_name=node_name, asset_id=asset_id, channel=channel)
        self.assertEqual(url, "Genesis8Female:#hip?rotation/x")

        return


    # ======================================================================== #
    # FILEPATH METHODS                                                         #
    # ======================================================================== #

    def test_absolute_filepath(self:Self) -> None:

        # Setup
        DazUrl.remove_all_content_directories()
        DazUrl.add_content_directory(DEFAULT_CONTENT_DIRECTORY)

        # URLs
        canonical:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf"
        
        daz_url:DazUrl = DazUrl.from_parts(filepath=canonical)
        self.assertIsNotNone(daz_url)

        # Check get_content_directory()
        con_path:Path = daz_url.get_content_directory()
        def_path:Path = Path(DEFAULT_CONTENT_DIRECTORY)
        self.assertEqual(con_path, def_path)

        # Check get_absolute_filepath()
        abs_path:Path = daz_url.get_absolute_filepath()
        filepath:Path = Path(DazUrl.format_filepath(canonical, is_quoted=False, has_leading_slash=False))
        self.assertEqual(abs_path, def_path.joinpath(Path(filepath)))

        return


    # ------------------------------------------------------------------------ #

    def test_relative_filepath(self:Self) -> None:

        # Setup
        DazUrl.remove_all_content_directories()
        DazUrl.add_content_directory(DEFAULT_CONTENT_DIRECTORY)

        canonical:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf"
        daz_url:DazUrl = DazUrl.from_parts(filepath=canonical)
        self.assertIsNotNone(daz_url)

        # Check get_relative_filepath()
        rel_path:Path = Path("data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf")
        self.assertEqual(daz_url.get_relative_filepath(), rel_path)

        return


    # ======================================================================== #
    # DIRECTORY METHODS                                                        #
    # ======================================================================== #

    def test_directory_urls(self:Self) -> None:

        # Setup
        DazUrl.remove_all_content_directories()
        DazUrl.add_content_directory(DEFAULT_CONTENT_DIRECTORY)

        # URLs
        canonical:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf"

        # -------------------------------------------------------------------- #
        def check_folder(url:Any) -> None:

            url_strings:list[DazUrl] = DazUrl.get_urls_in_directory(url)
            self.assertIsInstance(url_strings[0], DazUrl)
            self.assertEqual(url_strings[0].filepath, canonical)

            url_paths:list[DazUrl] = DazUrl.get_urls_in_directory(Path(url))
            self.assertIsInstance(url_paths[0], DazUrl)
            self.assertEqual(url_paths[0].filepath, canonical)

            return

        # -------------------------------------------------------------------- #
        # Unquoted, foreslash
        check_folder("/data/DAZ 3D/Genesis 8/Female/")
        check_folder("/data/DAZ 3D/Genesis 8/Female")
        check_folder("data/DAZ 3D/Genesis 8/Female/")
        check_folder("data/DAZ 3D/Genesis 8/Female")

        # Unquoted, one backslash r-string
        check_folder(r"\data\DAZ 3D\Genesis 8\Female\\")
        check_folder(r"\data\DAZ 3D\Genesis 8\Female")
        check_folder(r"data\DAZ 3D\Genesis 8\Female\\")
        check_folder(r"data\DAZ 3D\Genesis 8\Female")

        # Unquoted, double backslash
        check_folder("\\data\\DAZ 3D\\Genesis 8\\Female\\")
        check_folder("\\data\\DAZ 3D\\Genesis 8\\Female")
        check_folder("data\\DAZ 3D\\Genesis 8\\Female\\")
        check_folder("data\\DAZ 3D\\Genesis 8\\Female")

        # -------------------------------------------------------------------- #
        # Quoted, foreslash
        check_folder("/data/DAZ%203D/Genesis%208/Female/")
        check_folder("/data/DAZ%203D/Genesis%208/Female")
        check_folder("data/DAZ%203D/Genesis%208/Female/")
        check_folder("data/DAZ%203D/Genesis%208/Female")

        # Quoted, one backslash r-string
        check_folder(r"\data\DAZ%203D\Genesis%208\Female\\")
        check_folder(r"\data\DAZ%203D\Genesis%208\Female")
        check_folder(r"data\DAZ%203D\Genesis%208\Female\\")
        check_folder(r"data\DAZ%203D\Genesis%208\Female")

        # Quoted, double backslash
        check_folder("\\data\\DAZ%203D\\Genesis%208\\Female\\")
        check_folder("\\data\\DAZ%203D\\Genesis%208\\Female")
        check_folder("data\\DAZ%203D\\Genesis%208\\Female\\")
        check_folder("data\\DAZ%203D\\Genesis%208\\Female")

        # -------------------------------------------------------------------- #

        # foreslash
        check_folder(f"{DEFAULT_CONTENT_DIRECTORY}/data/DAZ 3D/Genesis 8/Female")
        check_folder(f"{DEFAULT_CONTENT_DIRECTORY}/data/DAZ 3D/Genesis 8/Female/")
        check_folder(f"{DEFAULT_CONTENT_DIRECTORY}/data/DAZ%203D/Genesis%208/Female")
        check_folder(f"{DEFAULT_CONTENT_DIRECTORY}/data/DAZ%203D/Genesis%208/Female/")

        # Double Backslash
        check_folder(f"{DEFAULT_CONTENT_DIRECTORY}\\data\\DAZ 3D\\Genesis 8\\Female")
        check_folder(f"{DEFAULT_CONTENT_DIRECTORY}\\data\\DAZ 3D\\Genesis 8\\Female\\")
        check_folder(f"{DEFAULT_CONTENT_DIRECTORY}\\data\\DAZ%203D\\Genesis%208\\Female")
        check_folder(f"{DEFAULT_CONTENT_DIRECTORY}\\data\\DAZ%203D\\Genesis%208\\Female\\")

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def test_get_file_dson(self:Self) -> None:

        # Setup
        DazUrl.remove_all_content_directories()
        DazUrl.add_content_directory(DEFAULT_CONTENT_DIRECTORY)

        # URLs
        g8f_url:DazUrl = DazUrl.from_url("data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf")

        # get_file_dson()
        dson:dict = g8f_url.get_file_dson()
        self.assertIsNotNone(dson)
        self.assertIsInstance(dson, dict)
        self.assertEqual(list(dson.keys()), ["file_version", "asset_info", "geometry_library", "node_library", "modifier_library"])
        self.assertEqual(dson["asset_info"]["id"], g8f_url.filepath)

        return


    # ------------------------------------------------------------------------ #

    def test_get_urls_in_file(self:Self) -> None:

        # Setup
        DazUrl.remove_all_content_directories()
        DazUrl.add_content_directory(DEFAULT_CONTENT_DIRECTORY)

        # Variables
        urls:list[DazUrl] = None

        # URLs
        g8f_url:DazUrl = DazUrl.from_url("data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf")

        # -------------------------------------------------------------------- #
        # get_urls_in_file(GEOMETRY)
        urls = g8f_url.get_all_urls_in_file(LibraryType.GEOMETRY)
        self.assertIsNotNone(urls)
        self.assertEqual(len(urls), 1)

        # Index 0
        self.assertEqual(urls[0].filepath, "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf")
        self.assertEqual(urls[0].asset_id, "geometry")

        # -------------------------------------------------------------------- #
        # get_urls_in_file(NODE)
        urls = g8f_url.get_all_urls_in_file(LibraryType.NODE)
        self.assertIsNotNone(urls)
        self.assertEqual(len(urls), 171)

        # Indices
        self.assertEqual(urls[0].asset_id, "Genesis8Female")
        self.assertEqual(urls[1].asset_id, "hip")
        self.assertEqual(urls[169].asset_id, "lPectoral")
        self.assertEqual(urls[170].asset_id, "rPectoral")

        # -------------------------------------------------------------------- #
        # get_urls_in_file()
        urls = g8f_url.get_all_urls_in_file()
        self.assertIsNotNone(urls)
        self.assertEqual(len(urls), 173)

        # Index 0
        self.assertEqual(urls[0].filepath, "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf")
        self.assertEqual(urls[0].asset_id, "geometry")

        # Index 172
        self.assertEqual(urls[172].filepath, "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf")
        self.assertEqual(urls[172].asset_id, "rPectoral")

        return


    # ------------------------------------------------------------------------ #

    def test_get_asset_dson(self:Self) -> None:

        # Setup
        DazUrl.remove_all_content_directories()
        DazUrl.add_content_directory(DEFAULT_CONTENT_DIRECTORY)

        # URLs
        hip_url:DazUrl = DazUrl.from_url("data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf#hip")
        
        # Check DazUrl
        self.assertTrue(hip_url.is_dsf_valid())
        self.assertEqual(hip_url.filepath, "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf")
        self.assertEqual(hip_url.asset_id, "hip")

        # Get DSON
        asset_dson, asset_type = hip_url.get_asset_dson()
        self.assertIsInstance(asset_dson, dict)
        self.assertIsInstance(asset_type, LibraryType)
        self.assertEqual(asset_type, LibraryType.NODE)

        # Test DSON dict
        keys:list[str] = [ 'id', 'name', 'type', 'label', 'parent',
                'rotation_order', 'inherits_scale', 'center_point', 'end_point',
                'orientation', 'rotation', 'translation', 'scale', 
                'general_scale', 'extra'
            ]
        self.assertEqual(list(asset_dson.keys()), keys)
        self.assertEqual(asset_dson["id"], "hip")
        self.assertEqual(asset_dson["name"], "hip")
        self.assertEqual(asset_dson["type"], "bone")
        self.assertEqual(asset_dson["label"], "Hip")

        return


    # ------------------------------------------------------------------------ #

    def test_get_value(self:Self) -> None:

        # Setup
        DazUrl.remove_all_content_directories()
        DazUrl.add_content_directory(DEFAULT_CONTENT_DIRECTORY)

        # URLs
        g8f_url:DazUrl = DazUrl.from_url("data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf")

        # get_value()
        value_path:list[str] = [ "node_library", "Genesis8Female", "label" ]
        self.assertEqual(g8f_url.get_value(value_path), "Genesis 8 Female")

        return


    # ------------------------------------------------------------------------ #

    def test_get_value_general_scale(self:Self) -> None:
        """Unit test for the \"get_single_property_from_library()\" method.
        
        Daz Studio has a 'quirk' where 'scale/general' is converted under the
        hood to 'general_scale', making this worthy of a dedicated unit test.
        """

        # Setup
        DazUrl.remove_all_content_directories()
        DazUrl.add_content_directory(DEFAULT_CONTENT_DIRECTORY)

        # Variables
        url_string:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf"
        value_path:list[str] = [ "node_library", "lThighTwist", "scale", "general" ]

        # URLs
        daz_url:DazUrl = DazUrl.from_url(url_string)

        # get_value()
        dson:dict = daz_url.get_value(value_path)
        self.assertIsNotNone(dson)
        self.assertEqual(dson["id"], "general_scale")

        return


    # ------------------------------------------------------------------------ #

    def test_get_node_hierarchy_urls(self:Self) -> None:

        # Setup
        DazUrl.remove_all_content_directories()
        DazUrl.add_content_directory(DEFAULT_CONTENT_DIRECTORY)

        # Variables
        canonical:str = "/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf"

        # URLs
        g8f_url:DazUrl = DazUrl.from_url("data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf#Genesis8Female")

        # get_node_hierarchy_urls()
        child_urls:list[DazUrl] = g8f_url.get_figure_hierarchy_urls()
        self.assertIsNotNone(child_urls)
        self.assertEqual(len(child_urls), 170)

        # Index 0
        self.assertEqual(child_urls[0].filepath, canonical)
        self.assertEqual(child_urls[0].asset_id, "hip")

        # Index 169
        self.assertEqual(child_urls[169].filepath, canonical)
        self.assertEqual(child_urls[169].asset_id, "rPinky3")

        return
