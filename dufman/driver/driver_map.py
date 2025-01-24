# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

# stdlib
from copy import copy, deepcopy
from math import isclose
from typing import Any, Iterator, Self

# dufman
from dufman.driver.driver_object import DriverEquation, DriverTarget
from dufman.driver.utils import get_channel_object
from dufman.enums import LibraryType
from dufman.structs.channel import DsonChannel
from dufman.structs.formula import DsonFormula
from dufman.structs.modifier import DsonModifier
from dufman.structs.morph import DsonMorph
from dufman.structs.node import DsonNode
from dufman.types import DsonVector
from dufman.url import DazUrl


# ============================================================================ #
# Driver Map                                                                   #
# ============================================================================ #

class DriverMap:

    def __init__(self:Self, figure_name:str) -> Self:

        # This is the name of the figure the DriverMap is meant to drive. At
        #   the moment, it does nothing. In the future it may be used to check
        #   the "node path" in Daz asset addressing (i.e. "Genesis8Male:").
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
                self._urls:list[DazUrl] = driver_map.get_all_driver_urls()
                return

            def __iter__(self:Self) -> Self:
                return self

            def __next__(self:Self) -> DriverTarget:
                if self._index >= len(self._urls):
                    raise StopIteration
                url:DazUrl = self._urls[self._index]
                self._index += 1
                return self._driver_map.get_driver_target(url)
        # -------------------------------------------------------------------- #

        return _DriverIterator(self)


    # ======================================================================== #
    # DRIVER TARGET METHODS                                                    #
    # ======================================================================== #

    def add_driver_target(self:Self, target_url:DazUrl) -> DriverTarget:
        """Return a DriverTarget, and create it if it doesn't exist."""

        # -------------------------------------------------------------------- #
        # Type safety

        # Format URL string for consistency
        if not target_url.asset_id or not target_url.channel:
            raise ValueError

        # -------------------------------------------------------------------- #
        target_url = copy(target_url)

        # Create channel dictionary if it hasn't been created yet
        if target_url.asset_id not in self._drivers:
            self._drivers[target_url.asset_id] = {}

        # Store driver in nested dictionary (i.e. "rotation/x")
        drivers:dict = self._drivers[target_url.asset_id]

        # If driver has not been added, add it
        if not target_url.channel in drivers:

            # Add the DriverTarget to the dictionary
            drivers[target_url.channel] = DriverTarget(target_url)

        return drivers[target_url.channel]


    # ------------------------------------------------------------------------ #

    def get_driver_target(self:Self, target_url:DazUrl) -> DriverTarget:

        # -------------------------------------------------------------------- #
        # Type safety

        # Format URL string for consistency
        if not target_url.asset_id:
            raise ValueError

        target_url = copy(target_url)

        # If there is no channel and the target is a modifier, get the channel
        #   name of the channel from the DsonModifier.
        if not target_url.channel and target_url.asset_id in self._modifiers:
            modifier:DsonModifier = self._modifiers[target_url.asset_id]
            target_url.channel = modifier.channel.channel_id

        if not target_url.channel:
            raise ValueError

        # If the DriverTarget has not been added, return None
        if target_url.asset_id not in self._drivers or target_url.channel not in self._drivers[target_url.asset_id]:
            return None

        # Return the value from the nested dictionary
        return self._drivers[target_url.asset_id][target_url.channel]


    # ------------------------------------------------------------------------ #

    def remove_all_driver_targets(self:Self) -> None:
        self._drivers.clear()
        self._equations.clear()
        self._modifiers.clear()
        self._nodes.clear()
        return


    # ======================================================================== #
    # PUBLIC LOAD METHODS                                                      #
    # ======================================================================== #

    def load_empty_driver(self:Self, empty_url:DazUrl) -> DriverTarget:


        # -------------------------------------------------------------------- #
        # Type safety

        if not empty_url or not isinstance(empty_url, DazUrl):
            raise TypeError

        if not empty_url.asset_id or not empty_url.channel:
            raise ValueError

        # -------------------------------------------------------------------- #
        # Logic

        empty_url = copy(empty_url)

        # Ensure formulas are only iterated once
        if self.get_driver_target(empty_url) is None:
            target:DriverTarget = self.add_driver_target(empty_url)
        else:
            target:DriverTarget = self.get_driver_target(empty_url)

        return target


    # ======================================================================== #

    def load_modifier_driver(self:Self, modifier_url:DazUrl, struct:DsonModifier) -> DriverTarget:

        # -------------------------------------------------------------------- #
        # URL type safety
        if not modifier_url or not isinstance(modifier_url, DazUrl):
            raise TypeError

        # Ensure URL is valid
        if not modifier_url.filepath or not modifier_url.asset_id:
            raise ValueError

        # -------------------------------------------------------------------- #
        # Struct type safety
        if not struct or not isinstance(struct, DsonModifier):
            raise TypeError

        # -------------------------------------------------------------------- #
        # Logic

        modifier_url = copy(modifier_url)

        # If the URL doesn't have a property path, use the one from the struct
        if not modifier_url.channel:
            modifier_url.channel = struct.channel.channel_id

        # The driver object in question
        target:DriverTarget = self.get_driver_target(modifier_url)

        # This is our first time, or the target does not have an asset, so
        #   instantiate the modifier data.
        if target is None or not target.is_valid():

            # If DriverTarget already exists, this will return it. If not, it
            #   will create it. Either way, we get what we need.
            target = self.add_driver_target(modifier_url)
            target.set_asset(struct, LibraryType.MODIFIER)

            if struct.formulas:
                self._parse_formulas(modifier_url, struct.formulas)

            # Cache struct
            self._modifiers[modifier_url.asset_id] = struct

        return target


    # ======================================================================== #

    def load_modifier_folder(self:Self, directory_url:str) -> None:

        # FIXME: Change this to take a DazUrl (somehow).

        for daz_url in DazUrl.get_urls_in_directory(directory_url):
            for asset_url in daz_url.get_all_urls_in_file(LibraryType.MODIFIER):
                struct:DsonModifier = DsonModifier.load_from_file(asset_url)
                self.load_modifier_driver(asset_url, struct)

        return


    # ======================================================================== #

    def load_node_driver(self:Self, node_url:DazUrl, struct:DsonNode) -> DriverTarget:

        # -------------------------------------------------------------------- #
        # URL type safety
        if not node_url or not isinstance(node_url, DazUrl):
            raise TypeError

        # Ensure URL is valid
        if not node_url.filepath or not node_url.asset_id or not node_url.channel:
            raise ValueError

        # -------------------------------------------------------------------- #
        # Struct type safety
        if not struct or not isinstance(struct, DsonNode):
            raise TypeError

        # -------------------------------------------------------------------- #
        # Logic

        node_url = copy(node_url)

        # A node has multiple channels, but only one set of formulas. We need
        #   to ensure the formulas are only parsed once per node.
        should_parse_formulas:bool = True
        if node_url.asset_id in self._drivers:
            for target in self._drivers[node_url.asset_id].values():
                if target.is_valid():
                    should_parse_formulas = False

        # The driver target in question
        target:DriverTarget = self.get_driver_target(node_url)

        # This is our first time, or the target does not have an asset, so
        #   instantiate the node data
        if target is None or not target.is_valid():

            # If DriverTarget already exists, this will return it. If not, it
            #   will create it. Either way, we get what we need.
            target = self.add_driver_target(node_url)
            target.set_asset(struct, LibraryType.NODE)

            if should_parse_formulas and struct.formulas:
                self._parse_formulas(node_url, struct.formulas)

            # cache struct
            if node_url.asset_id not in self._nodes:
                self._nodes[node_url.asset_id] = struct

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
            ch:str = modifier.channel.channel_id
            daz_url:DazUrl = DazUrl.from_parts(asset_id=ai, channel=ch)

            # Get DriverTarget object
            target:DriverTarget = self.get_driver_target(daz_url)

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

    def get_current_node_shape(self:Self, target_url:DazUrl) -> DsonNode:

        # If there is no DsonNode, there's nothing to get
        if target_url.asset_id not in self._nodes:
            # TODO: Raise an exception instead?
            return None

        # Create a new copy of the DsonNode so we can update its values without
        #   changing the base object
        source_node:DsonNode = self._nodes[target_url.asset_id]
        copied_node:DsonNode = deepcopy(source_node)

        # Loop through all loaded property paths
        for (path, target) in self._drivers[target_url.asset_id].items():

            # Format URL, in the format "#asset_id?rotation/x"
            channel_url:DazUrl = DazUrl.from_parts(asset_id=target_url.asset_id, channel=path)

            # Get the DsonChannel object which corresponds to the property_path
            channel:DsonChannel = get_channel_object(copied_node, channel_url)

            # Get the current value of this channel
            channel.current_value = target.get_value()

        return copied_node


    # ======================================================================== #
    # DRIVER KEY METHODS                                                       #
    # ======================================================================== #

    def get_all_driver_urls(self:Self) -> list[DazUrl]:

        result:list[str] = []

        for (asset_id, channels) in self._drivers.items():
            for channel in channels:
                daz_url:DazUrl = DazUrl.from_parts(asset_id=asset_id, channel=channel)
                result.append(daz_url)

        return result


    # ------------------------------------------------------------------------ #

    def get_invalid_driver_keys(self:Self) -> list[DazUrl]:
        result:list[str] = []
        for url in self.get_all_driver_urls():
            target:DriverTarget = self.get_driver_target(url)
            if not target.is_valid():
                result.append(url)
        return result


    # ======================================================================== #
    # DRIVER ASSET METHODS                                                     #
    # ======================================================================== #

    def get_driver_value(self:Self, driver_url:DazUrl) -> Any:

        if not driver_url or not isinstance(driver_url, DazUrl):
            raise TypeError

        driver_target:DriverTarget = self.get_driver_target(driver_url)
        if not driver_target:
            raise ValueError

        return driver_target.get_value()


    # ------------------------------------------------------------------------ #

    def set_driver_value(self:Self, driver_url:DazUrl, new_value:Any) -> None:

        if not driver_url or not isinstance(driver_url, DazUrl):
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

    def _parse_url(self:Self, dsf_filepath:str, url_string:str, equation:DriverEquation, *, is_input:bool) -> None:

        # Convert URL from formula into a DazUrl object.
        formula_url:DazUrl = DazUrl.from_url(url_string)
        if not formula_url.asset_id or not formula_url.channel:
            raise ValueError

        # -------------------------------------------------------------------- #
        # If this DriverTarget has not been loaded from disk, try and load it
        if self.get_driver_target(formula_url) is None:

            # NOTE: Often, if a URL doesn't have a filepath, it refers to the
            #   containing file, but not always ("eJCMMemphisEyesClosedL"). So
            #   we cannot assume this will always point to a valid asset.
            # NOTE: dsf_filepath should've been passed in from a DazUrl object,
            #   so it should be formatted correctly already.
            if not formula_url.filepath:
                formula_url.filepath = dsf_filepath

            # If the DSF file exists on disk, add the struct to the DriverMap.
            if formula_url.is_dsf_valid():

                # Get DSON dict and LibraryType from DazUrl.
                _, asset_type = formula_url.get_asset_dson()

                # If asset_type is None, that means the ID could not be found
                #   in the file. Skip adding the struct.
                if asset_type is not None:

                    if asset_type == LibraryType.MODIFIER:
                        struct:DsonModifier = DsonModifier.load_from_file(formula_url)
                        self.load_modifier_driver(formula_url, struct)
                    elif asset_type == LibraryType.NODE:
                        struct:DsonNode = DsonNode.load_from_file(formula_url)
                        self.load_node_driver(formula_url, struct)
                    else:
                        # Future-proof against new asset types.
                        raise NotImplementedError(asset_type)

        # The modifier/node data is set in the calling method, not here.
        target:DriverTarget = self.load_empty_driver(formula_url)

        # -------------------------------------------------------------------- #

        # Link DriverTargets and DriverEquations.
        if is_input:
            target._subcomponents.append(equation)
            equation._inputs[url_string] = target
        else:
            target._controllers.append(equation)
            equation._output = target

        return


    # ------------------------------------------------------------------------ #

    def _parse_formulas(self:Self, daz_url:DazUrl, formula_list:list[DsonFormula]) -> None:

        # TODO: How does "auto-follow" work for JCMs?

        for formula in formula_list:
            equation:DriverEquation = DriverEquation(formula)
            self._equations.append(equation)

            # Handle input URLs
            for operation in formula.operations:
                if not operation.url:
                    continue
                self._parse_url(daz_url.filepath, operation.url, equation, is_input=True)

            # Handle output URL
            self._parse_url(daz_url.filepath, formula.output, equation, is_input=False)

        return
