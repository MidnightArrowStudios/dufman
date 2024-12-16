from __future__ import annotations
from typing import Self

from ..enums import LibraryType
from ..library import (
    find_library_containing_asset_id,
    get_asset_json_from_library,
    get_single_property_from_library,
)
from ..url import AssetAddress


class FormulaMap:

    def __init__(self:FormulaMap, figure_id:str, url:str) -> Self:
        self.property_map:dict = {}
        self._create_property_map(figure_id, url)
        for (key, obj) in self.property_map.items():
            channel_id:str = obj["id"]
            print(f"{key}: {channel_id}")
        return


    def _create_property_map(self:FormulaMap, figure_id:str, url_string:str) -> None:

        address:AssetAddress = AssetAddress.create_from_url(url_string)
        asset_url:str = address.get_valid_asset_url()
        library_type:LibraryType = find_library_containing_asset_id(asset_url)

        # Ensure object is either a modifier or a node.
        if not (library_type == LibraryType.MODIFIER or library_type == LibraryType.NODE):
            raise Exception(f"\"{url_string}\" has unexpected library_type: \"{library_type}\"")

        # If we are dealing with a root URL (passed in by user), it won't have
        #   a property path, so we append one.
        if (library_type == LibraryType.MODIFIER) and not address.property_path:
            address.property_path = "value"

        # This is the object that holds the formulas -- either a modifier or a
        #   node.
        json:dict = get_asset_json_from_library(asset_url, library_type)
        if not json:
            raise Exception(f"Could not retrieve JSON object from DSF file.")

        # Add channel object to property_map
        formula_url:str = address.get_valid_formula_url()
        if formula_url not in self.property_map:

            # Modifier
            if library_type == LibraryType.MODIFIER:
                self.property_map[formula_url] = json["channel"]

            # Node
            elif library_type == LibraryType.NODE:

                # e.g. [ "node_library", "hip", "translation", "y" ]
                prop_path:str = [ library_type.value, address.asset_id, *address.get_property_tokens() ]

                # Technically this loads the DSF file again, but it has
                #   specialized handling to extract properties with error
                #   checking, so just take the hit.
                prop_json:dict = get_single_property_from_library(address.filepath, prop_path)

                self.property_map[formula_url] = prop_json

        # Recursively call this function for input and output URLs
        for formula in json.get("formulas", []):
            for operation in formula["operations"]:

                # No URL, skip processing
                if not "url" in operation:
                    continue

                # Input URLs
                input_address:AssetAddress = AssetAddress.create_from_url(operation["url"])
                if input_address.filepath:
                    self._create_property_map(figure_id, input_address.get_valid_formula_url())

            # Output URLs
            output_address:AssetAddress = AssetAddress.create_from_url(formula["output"])
            if output_address.filepath:
                self._create_property_map(figure_id, output_address.get_valid_formula_url())

        return
