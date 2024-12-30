# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""This module defines a custom dictionary to store DriverTarget objects."""

from __future__ import annotations
from typing import Self

from dufman.driver.driver_object import DriverTarget
from dufman.url import AssetAddress


# ============================================================================ #

class DriverDictionary:
    """A class which stores a mapping between a URL and a DriverTarget object.
    
    Any string which is passed to this class's methods will be split and form-
    atted by AssetAddress, ensuring the end user does not need to worry about
    URL quoting or what kind of slashes are used. However, the filepaths are
    stored in quoted format, so if the end user does a string comparison, they
    may need to use AssetAddress.format_filepath() to ensure the string to be
    checked matches.

    The components of a URL are:

    /data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf#abdomen_2?translation/x
    |                                              | |       | |           |
                        Filepath                     Asset ID  Property Path

    A URL string must have all the required components to access whatever is
    being requested in the method name. For instance, the URL

        /data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf
    
    will be able to extract all of the asset IDs associated with that DSF file
    using the method

        get_all_asset_ids(url_string)

    but they will not be able to extract the property paths of those assets.
    """

    # ======================================================================== #

    def __init__(self:DriverDictionary) -> Self:
        self._dict:dict = {}
        return


    # ======================================================================== #

    def add_driver_target(self:DriverDictionary, url_string:str, target:DriverTarget) -> None:
        """Add a DriverTarget to the dictionary and associate it with a URL."""

        # Ensure DriverTarget is valid
        if not (target and isinstance(target, DriverTarget)):
            raise TypeError

        # Format URL string
        address:AssetAddress = AssetAddress.from_url(url_string)

        # Filepath
        if not address.filepath:
            raise ValueError

        filepaths:dict = self._dict
        if address.filepath not in filepaths:
            filepaths[address.filepath] = {}

        # Asset ID
        if not address.asset_id:
            raise ValueError

        asset_ids:dict = filepaths[address.filepath]
        if address.asset_id not in asset_ids:
            asset_ids[address.asset_id] = {}

        # Property path
        if not address.property_path:
            raise ValueError

        properties:dict = asset_ids[address.asset_id]
        if address.property_path and address.property_path not in properties:
            properties[address.property_path] = {}

        # Store object
        properties[address.property_path] = target

        return


    # ------------------------------------------------------------------------ #

    def get_driver_target(self:DriverDictionary, url_string:str) -> DriverTarget:
        """Return a DriverTarget stored inside the dictionary using its URL."""

        address:AssetAddress = AssetAddress.from_url(url_string)

        filepaths:dict = self._dict
        if address.filepath not in filepaths:
            return None

        asset_ids:dict = filepaths[address.filepath]
        if address.asset_id not in asset_ids:
            return None

        properties:dict = asset_ids[address.asset_id]
        if address.property_path not in properties:
            return None

        return properties[address.property_path]


    # ======================================================================== #

    def get_all_filepaths(self:DriverDictionary) -> list[str]:
        """Return a list of all DSF files stored inside the dictionary."""
        return list(self._dict.keys())


    # ------------------------------------------------------------------------ #

    def get_all_asset_ids(self:DriverDictionary, url_string:str) -> list[str]:
        """Return a list of a designated DSF file's assets."""

        address:AssetAddress = AssetAddress.from_url(url_string)

        filepaths:dict = self._dict
        if address.filepath not in filepaths:
            return []

        return list(filepaths[address.filepath].keys())


    # ------------------------------------------------------------------------ #

    def get_all_property_paths(self:DriverDictionary, url_string:str) -> list[str]:
        """Return a list of the designated asset's driver targets."""

        address:AssetAddress = AssetAddress.from_url(url_string)

        filepaths:dict = self._dict
        if address.filepath not in filepaths:
            return []

        asset_ids:dict = filepaths[address.filepath]
        if address.asset_id not in asset_ids:
            return []

        return list(asset_ids[address.asset_id].keys())


    # ------------------------------------------------------------------------ #

    def get_all_stored_urls(self:DriverDictionary) -> list[str]:
        """Return all URLs stored inside the nested dictionaries."""

        result:list[str] = []

        for (filepath, filepaths) in self._dict.items():
            for (asset_id, asset_ids) in filepaths.items():
                for (prop_path, _prop_data) in asset_ids.items():
                    url_string:str = AssetAddress.format_url_as_string(filepath=filepath, asset_id=asset_id, property_path=prop_path)
                    result.append(url_string)

        return result


    # ======================================================================== #

    def has_filepath(self:DriverDictionary, url_string:str) -> bool:
        """Check if a DSF file has any DriverTargets in the dictionary."""

        # Format URL, ensure it has a filepath.
        address:AssetAddress = AssetAddress.from_url(url_string)
        if not address.filepath:
            raise ValueError

        filepaths:dict = self._dict

        return address.filepath in filepaths


    # ------------------------------------------------------------------------ #

    def has_asset_id(self:DriverDictionary, url_string:str) -> bool:
        """Check if a DSF file's assets have any DriverTargets in the dictionary."""

        # Format URL, ensure it has a filepath and an asset ID.
        address:AssetAddress = AssetAddress.from_url(url_string)
        if not address.filepath or not address.asset_id:
            raise ValueError

        filepaths:dict = self._dict
        if address.filepath not in filepaths:
            return False

        return address.asset_id in filepaths[address.filepath]


    # ------------------------------------------------------------------------ #

    def has_property_path(self:DriverDictionary, url_string:str) -> bool:
        """Check if an asset's properties have any DriverTargets in the dictionary."""

        # Format URL, ensure it has filepath, asset ID, and property path.
        address:AssetAddress = AssetAddress.from_url(url_string)
        if not address.filepath or not address.asset_id or not address.property_path:
            raise ValueError

        filepaths:dict = self._dict
        if address.filepath not in filepaths:
            return False

        asset_ids:dict = filepaths[address.filepath]
        if address.asset_id not in asset_ids:
            return False

        return address.property_path in asset_ids[address.asset_id]
