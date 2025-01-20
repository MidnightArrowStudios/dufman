# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

# stdlib
from copy import deepcopy
from math import isclose
from pathlib import Path
from typing import Any, Iterator, Self

# dufman
from dufman.driver.driver_object import DriverEquation, DriverTarget
from dufman.driver.utils import get_channel_object
from dufman.enums import LibraryType
from dufman.file import get_relative_filepaths_from_directory
from dufman.library import (
    find_asset_dson_in_library,
    get_all_asset_urls_from_library,
)
from dufman.structs.channel import DsonChannel
from dufman.structs.formula import DsonFormula
from dufman.structs.modifier import DsonModifier
from dufman.structs.morph import DsonMorph
from dufman.structs.node import DsonNode
from dufman.types import DsonVector
from dufman.url import AssetAddress


# ============================================================================ #
# Driver Map                                                                   #
# ============================================================================ #

class DriverMap:

    def __init__(self:Self, figure_name:str) -> Self:

        # This is the name of the figure the DriverMap is meant to drive. At
        #   the moment, it does nothing. In the future it may be used as part
        #   of the "node path" in Daz asset addressing (i.e. "Genesis8Male:").
        self._figure_name:str = figure_name

        # Stores all DriverTargets which have been loaded.
        self._drivers:dict = {}

        # Caches the assets inside the DriverTargets.
        self._modifiers:dict = {}
        self._nodes:dict = {}

        # Cache equations (mostly for debugging).
        self._equations:list[DriverEquation] = []

        return


    # ------------------------------------------------------------------------ #

    def __str__(self:Self) -> str:
        return f"DriverMap: \"{self._figure_name}\""


    # ------------------------------------------------------------------------ #

    def __repr__(self:Self) -> str:
        return f"DriverMap(\"{self._figure_name}\")"


    # ------------------------------------------------------------------------ #

    def __iter__(self:Self) -> Iterator[DriverTarget]:

        # -------------------------------------------------------------------- #
        class _DriverIterator(Iterator[DriverTarget]):
            def __init__(self:Self, driver_map:DriverMap) -> Self:
                self._driver_map:DriverMap = driver_map
                self._index:int = 0
                self._urls:list[str] = driver_map.get_all_driver_keys()
                return

            def __iter__(self:Self) -> Self:
                return self

            def __next__(self:Self) -> DriverTarget:
                if self._index >= len(self._urls):
                    raise StopIteration
                url:str = self._urls[self._index]
                self._index += 1
                return self._driver_map.get_driver_target(url)
        # -------------------------------------------------------------------- #

        return _DriverIterator(self)


    # ======================================================================== #
    # PUBLIC LOAD METHODS                                                      #
    # ======================================================================== #

    def load_empty_driver(self:Self, dummy_url:str) -> DriverTarget:

        # -------------------------------------------------------------------- #
        # URL type safety
        if not dummy_url or not isinstance(dummy_url, str):
            raise TypeError

        address:AssetAddress = AssetAddress.from_url(dummy_url)
        if not address.asset_id or not address.property_path:
            raise ValueError

        # -------------------------------------------------------------------- #
        # Logic

        # Convert URL object to string, in format "pJCMCorrectiveMorph_90?value"
        driver_url:str = address.get_key_to_driver_target()

        # Ensure formulas are only iterated once
        if self.get_driver_target(driver_url) is None:
            target:DriverTarget = self.add_driver_target(driver_url)
        else:
            target:DriverTarget = self.get_driver_target(driver_url)

        return target


    # ======================================================================== #

    def load_modifier_driver(self:Self, modifier_url:str, struct:DsonModifier) -> DriverTarget:

        # -------------------------------------------------------------------- #
        # URL type safety
        if not modifier_url or not isinstance(modifier_url, str):
            raise TypeError

        # Ensure URL is valid
        address:AssetAddress = AssetAddress.from_url(modifier_url)
        if not address.filepath or not address.asset_id:
            raise ValueError

        # -------------------------------------------------------------------- #
        # Struct type safety
        if not struct or not isinstance(struct, DsonModifier):
            raise TypeError

        # -------------------------------------------------------------------- #
        # Logic

        # If the URL doesn't have a property path, use the one from the struct
        if not address.property_path:
            address.property_path = struct.channel.channel_id

        # Convert URL object to string, in format "pJCMCorrectiveMorph_90?value"
        driver_url:str = address.get_key_to_driver_target()

        # The driver object in question
        target:DriverTarget = self.get_driver_target(driver_url)

        # This is our first time, or the target does not have an asset, so
        #   instantiate the modifier data.
        if target is None or not target.is_valid():

            # If DriverTarget already exists, this will return it. If not, it
            #   will create it. Either way, we get what we need.
            target = self.add_driver_target(driver_url)
            target.set_asset(struct, LibraryType.MODIFIER)

            if struct.formulas:
                self._parse_formulas(address.filepath, struct.formulas)

            # Cache struct
            self._modifiers[address.asset_id] = struct

        return target


    # ======================================================================== #

    def load_modifier_folder(self:Self, directory_url:str) -> None:

        filepaths:list[Path] = get_relative_filepaths_from_directory(directory_url)
        for filepath in filepaths:
            for asset_url in get_all_asset_urls_from_library(filepath, LibraryType.MODIFIER):
                struct:DsonModifier = DsonModifier.load_from_file(asset_url)
                self.load_modifier_driver(asset_url, struct)

        return


    # ======================================================================== #

    def load_node_driver(self:Self, node_url:str, struct:DsonNode) -> DriverTarget:

        # -------------------------------------------------------------------- #
        # URL type safety
        if not node_url or not isinstance(node_url, str):
            raise TypeError

        # Ensure URL is valid
        address:AssetAddress = AssetAddress.from_url(node_url)
        if not address.filepath or not address.asset_id or not address.property_path:
            raise ValueError

        # -------------------------------------------------------------------- #
        # Struct type safety
        if not struct or not isinstance(struct, DsonNode):
            raise TypeError

        # -------------------------------------------------------------------- #
        # Logic

        # Convert URL object to string, in format "bone_name?rotation/x"
        driver_url:str = address.get_key_to_driver_target()

        # A node has multiple channels, but only one set of formulas. We need
        #   to ensure the formulas are only parsed once per node.
        should_parse_formulas:bool = True
        if address.asset_id in self._drivers:
            for target in self._drivers[address.asset_id].values():
                if target.is_valid():
                    should_parse_formulas = False

        # The driver target in question
        target:DriverTarget = self.get_driver_target(driver_url)

        # This is our first time, or the target does not have an asset, so
        #   instantiate the node data
        if target is None or not target.is_valid():

            # If DriverTarget already exists, this will return it. If not, it
            #   will create it. Either way, we get what we need.
            target = self.add_driver_target(driver_url)
            target.set_asset(struct, LibraryType.NODE)

            if should_parse_formulas and struct.formulas:
                self._parse_formulas(address.filepath, struct.formulas)

            # cache struct
            if address.asset_id not in self._nodes:
                self._nodes[address.asset_id] = struct

        return target


    # ======================================================================== #
    # GET DATA METHODS                                                         #
    # ======================================================================== #

    def get_current_morph_shape(self:Self, vertex_count:int) -> DsonMorph:

        # Caches the vertex positions which will be applied to the mesh
        morph_deltas:dict = {}

        # Loop through all cached modifiers
        for modifier in self._modifiers.values():

            # Ensure this modifier has a morph
            if not modifier.morph:
                continue

            # NOTE: Some morphs (i.e. iSourceTexture's Evangeliya) have a value
            #   of -1, so clearly this is not checked and doesn't matter.
            # if not struct.morph.expected_vertices == vertex_count:
            #     continue

            # Format key to retrieve driver
            ai:str = modifier.library_id
            pp:str = modifier.channel.channel_id
            address:AssetAddress = AssetAddress.from_components(asset_id=ai, property_path=pp)
            driver_key:str = address.get_key_to_driver_target()

            # Get DriverTarget object
            target:DriverTarget = self.get_driver_target(driver_key)

            # How much to dial the morph in
            strength:float = target.get_value()

            # Morph will have no effect, so skip it
            if isclose(strength, 0.0):
                continue

            # Accumulate vertex positions
            for (index, vertex) in modifier.morph.deltas.items():

                # If the vertex hasn't been stored in the dictionary yet, then
                #   add an entry
                if index not in morph_deltas:
                    morph_deltas[index] = DsonVector(0.0, 0.0, 0.0)

                # Add vertex positions
                morph_deltas[index].x += (vertex.x * strength)
                morph_deltas[index].y += (vertex.y * strength)
                morph_deltas[index].z += (vertex.z * strength)

        # Assign deltas to new DsonMorph object and return it
        result:DsonMorph = DsonMorph()
        result.expected_vertices = vertex_count
        result.deltas = morph_deltas

        return result


    # ======================================================================== #

    def get_current_node_shape(self:Self, target_url:str) -> DsonNode:

        # NOTE: If passing an Asset ID in by itself as a string, it MUST have a
        #   pound sign or it will be parsed as a filepath

        # Extract the Asset ID
        address:AssetAddress = AssetAddress.from_url(target_url)

        # If there is no DsonNode, there's nothing to get
        if address.asset_id not in self._nodes:
            # TODO: Raise an exception instead?
            return None

        # Create a new copy of the DsonNode so we can update its values without
        #   changing the base object
        source_node:DsonNode = self._nodes[address.asset_id]
        copied_node:DsonNode = deepcopy(source_node)

        # Loop through all loaded property paths
        for (path, target) in self._drivers[address.asset_id].items():

            # Format URL, in the format "#asset_id?rotation/x"
            driver_key:str = AssetAddress.format_url_as_string(asset_id=address.asset_id, property_path=path)

            # Get the DsonChannel object which corresponds to the property_path
            channel:DsonChannel = get_channel_object(copied_node, driver_key)

            # Get the current value of this channel
            channel.current_value = target.get_value()

        return copied_node


    # ======================================================================== #
    # DRIVER TARGET METHODS                                                    #
    # ======================================================================== #

    def add_driver_target(self:Self, target_url:str) -> DriverTarget:
        """Return a DriverTarget, and create it if it doesn't exist."""

        # Format URL string for consistency
        address:AssetAddress = AssetAddress.from_url(target_url)
        if not address.asset_id or not address.property_path:
            raise ValueError

        # Create property_path dictionary if it hasn't been created yet
        if address.asset_id not in self._drivers:
            self._drivers[address.asset_id] = {}

        # Store driver in nested dictionary by ID (i.e. "rotation/x")
        drivers:dict = self._drivers[address.asset_id]

        # If driver has not been added, add it
        if not address.property_path in drivers:

            # Create a string from formatted URL object
            formatted_url:str = AssetAddress.format_url_as_string(asset_id=address.asset_id, property_path=address.property_path)

            # Add the DriverTarget to the dictionary
            drivers[address.property_path] = DriverTarget(formatted_url)

        return drivers[address.property_path]


    # ------------------------------------------------------------------------ #

    def get_driver_target(self:Self, target_url:str) -> DriverTarget:

        # Format URL string for consistency
        address:AssetAddress = AssetAddress.from_url(target_url)
        if not address.asset_id:
            raise ValueError

        # If there is not property_path and the target is a modifier, then get
        #   the name of the channel from the DsonModifier
        if not address.property_path and address.asset_id in self._modifiers:
            modifier:DsonModifier = self._modifiers[address.asset_id]
            address.property_path = modifier.channel.channel_id

        if not address.property_path:
            raise ValueError

        # If the DriverTarget has not been added, return None
        if address.asset_id not in self._drivers or address.property_path not in self._drivers[address.asset_id]:
            return None

        # Return the value from the nested dictionary
        return self._drivers[address.asset_id][address.property_path]


    # ------------------------------------------------------------------------ #

    def remove_all_driver_targets(self:Self) -> None:
        self._drivers.clear()
        self._equations.clear()
        self._modifiers.clear()
        self._nodes.clear()
        return


    # ======================================================================== #
    # DRIVER KEY METHODS                                                       #
    # ======================================================================== #

    def get_all_driver_keys(self:Self) -> list[str]:

        result:list[str] = []

        for (asset_id, prop_paths) in self._drivers.items():
            for prop_path in prop_paths:
                driver_key:str = AssetAddress.format_url_as_string(asset_id=asset_id, property_path=prop_path)
                result.append(driver_key)

        return result


    # ------------------------------------------------------------------------ #

    def get_invalid_driver_keys(self:Self) -> list[str]:
        result:list[str] = []
        for key in self.get_all_driver_keys():
            target:DriverTarget = self.get_driver_target(key)
            if not target.is_valid():
                result.append(key)
        return result


    # ======================================================================== #
    # DRIVER ASSET METHODS                                                     #
    # ======================================================================== #

    def get_driver_value(self:Self, driver_url:str) -> Any:

        if not driver_url or not isinstance(driver_url, str):
            raise TypeError

        driver_target:DriverTarget = self.get_driver_target(driver_url)
        if not driver_target:
            raise ValueError

        return driver_target.get_value()


    # ------------------------------------------------------------------------ #

    def set_driver_value(self:Self, driver_url:str, new_value:Any) -> None:

        if not driver_url or not isinstance(driver_url, str):
            raise TypeError

        driver_target:DriverTarget = self.get_driver_target(driver_url)
        if not driver_target:
            raise ValueError

        driver_target.set_value(new_value)
        return


    # ======================================================================== #
    # EQUATION METHODS                                                         #
    # ======================================================================== #

    def get_equation_count(self:Self) -> int:
        return len(self._equations)


    # ======================================================================== #
    # PRIVATE METHODS                                                          #
    # ======================================================================== #

    def _parse_url(self:Self, dsf_filepath:str, property_url:str, equation:DriverEquation, *, is_input:bool) -> None:

        # Format URL string for consistency
        address:AssetAddress = AssetAddress.from_url(property_url)
        if not address.asset_id or not address.property_path:
            raise ValueError

        # property_url is the string defined in the DsonFormula object. It must
        #   stay the same so it can be used as a dictionary key, so we create a
        #   new URL string.
        formatted_url = address.get_key_to_driver_target()

        # -------------------------------------------------------------------- #
        # If this DriverTarget has not been loaded from disk, try and load it
        if self.get_driver_target(formatted_url) is None:

            # NOTE: Often, if a URL doesn't have a filepath, it refers to the
            #   containing file, but not always ("eJCMMemphisEyesClosedL"). So
            #   we cannot assume this will always point to a valid asset.
            if not address.filepath:
                address.filepath = dsf_filepath

            # Format URL
            asset_url:str = address.get_url_to_asset()

            # Flag to check if asset data could be loaded from disk
            is_valid:bool = True

            # Retrieve asset data from disk
            try:
                asset_type, asset_dson = find_asset_dson_in_library(asset_url)
            except FileNotFoundError:
                is_valid = False

            # Asset was not found inside the DSF file
            if is_valid and not asset_dson:
                is_valid = False

            # If data could be loaded from DSF file, then instantiate an
            #   object
            if is_valid:

                full_url:str = address.get_url_to_property()

                # Load nodes and modifiers into DriverMap (which will then
                #   recursively call this method for all their dependents)
                if asset_type == LibraryType.MODIFIER:
                    struct:DsonModifier = DsonModifier.load_from_file(asset_url)
                    self.load_modifier_driver(full_url, struct)
                elif asset_type == LibraryType.NODE:
                    struct:DsonNode = DsonNode.load_from_file(asset_url)
                    self.load_node_driver(full_url, struct)
                else:
                    # Future-proofing for new library types
                    raise NotImplementedError(asset_type)

        # The Node/Modifier properties are set in the calling function, not
        #   here
        target:DriverTarget = self.load_empty_driver(formatted_url)

        # -------------------------------------------------------------------- #
        # Link DriverTargets and DriverEquations
        if is_input:
            target._subcomponents.append(equation)
            equation._inputs[property_url] = target
        else:
            target._controllers.append(equation)
            equation._output = target

        return


    # ------------------------------------------------------------------------ #

    def _parse_formulas(self:Self, dsf_filepath:str, formula_list:list[DsonFormula]) -> None:

        # TODO: How does "auto-follow" work for JCMs?

        for formula in formula_list:
            equation:DriverEquation = DriverEquation(formula)
            self._equations.append(equation)

            # Handle input URLs
            for operation in formula.operations:
                if not operation.url:
                    continue
                self._parse_url(dsf_filepath, operation.url, equation, is_input=True)

            # Handle output URL
            self._parse_url(dsf_filepath, formula.output, equation, is_input=False)

        return
