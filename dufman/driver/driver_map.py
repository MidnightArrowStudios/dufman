# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

# stdlib
from copy import deepcopy
from math import isclose
from typing import Any, Self, TypeAlias

# dufman
from dufman.driver.driver_dict import DriverDictionary
from dufman.driver.driver_object import DriverTarget, DriverEquation
from dufman.enums import LibraryType
from dufman.library import find_asset_dson_in_library
from dufman.structs.channel import DsonChannel
from dufman.structs.formula import DsonFormula
from dufman.structs.modifier import DsonModifier
from dufman.structs.morph import DsonMorph
from dufman.structs.node import DsonNode
from dufman.types import DsonVector
from dufman.url import AssetAddress


# ============================================================================ #
# DriverTarget iterator                                                        #
# ============================================================================ #

_DriverMap:TypeAlias = 'DriverMap'

class _DriverIterator:
    def __init__(self:Self, driver_map:_DriverMap) -> Self:
        self._driver_map:DriverMap = driver_map
        self._index:int = 0
        self._urls:list[str] = driver_map.get_all_driver_urls()
        return

    def __next__(self:Self) -> DriverTarget:
        if self._index >= len(self._urls):
            raise StopIteration
        url:str = self._urls[self._index]
        self._index += 1
        return self._driver_map._drivers.get_driver_target(url)


# ============================================================================ #
# DriverMap                                                                    #
# ============================================================================ #

class DriverMap:

    # ======================================================================== #

    def __init__(self:Self) -> Self:

        # Stores a hierarchical list of DriverTarget objects.
        self._drivers:DriverDictionary = DriverDictionary()

        # Store nodes and modifiers in separate dictionaries, for convenience.
        #   These are keyed by the asset_url.
        self._modifiers:dict = {}
        self._nodes:dict = {}

        # Dictionary holding all formulas found per DSF file. These are keyed
        #   by the asset_url.
        self._equations:dict = {}

        return


    # ------------------------------------------------------------------------ #

    def __iter__(self:Self) -> _DriverIterator:
        return _DriverIterator(self)


    # ------------------------------------------------------------------------ #

    def __str__(self:Self) -> str:
        return "DriverMap"


    # ------------------------------------------------------------------------ #

    def __repr__(self:Self) -> str:
        return f"DriverMap(drivers={ len(self.get_all_driver_urls()) })"


    # ======================================================================== #
    # PUBLIC FUNCTIONALITY                                                     #
    # ======================================================================== #

    def load_invalid(self:Self, target_url:str, property_path:str) -> None:
        return


    # ------------------------------------------------------------------------ #

    def load_modifier(self:Self, struct:DsonModifier) -> None:
        """Add a channel-containing DsonModifier struct to the DriverMap."""
        self._load_asset(struct, struct.channel.channel_id, LibraryType.MODIFIER)
        return


    # ------------------------------------------------------------------------ #

    def load_node(self:Self, struct:DsonNode, property_path:str) -> None:
        """Add a channel-containing DsonNode struct to the DriverMap."""
        self._load_asset(struct, property_path, LibraryType.NODE)
        return


    # ======================================================================== #
    # ======================================================================== #

    def get_driver_value(self:Self, target_url:str) -> Any:
        """Calculate and return a channel's current value."""
        driver_target:DriverTarget = self._drivers.get_driver_target(target_url)
        return driver_target.get_value()


    # ------------------------------------------------------------------------ #

    def set_driver_value(self:Self, target_url:str, new_value:Any) -> None:
        """Update a channel's current value."""
        driver_target:DriverTarget = self._drivers.get_driver_target(target_url)
        driver_target.set_value(new_value)
        return


    # ======================================================================== #
    # ======================================================================== #

    def get_all_driver_urls(self:Self) -> list[str]:
        """Return a list of every URL that has been loaded."""
        return self._drivers.get_all_stored_urls()


    # ========================================================================= #
    # ========================================================================= #

    def does_filepath_have_driver(self:Self, target_url:str) -> bool:
        """Check if a DSF file has been loaded."""
        return self._drivers.has_filepath(target_url)


    # ------------------------------------------------------------------------ #

    def does_asset_id_have_driver(self:Self, target_url:str) -> bool:
        """Check if an asset inside a DSF file has been loaded."""
        return self._drivers.has_asset_id(target_url)


    # ------------------------------------------------------------------------ #

    def does_property_path_have_driver(self:Self, target_url:str) -> bool:
        """Check if a property inside an asset has been loaded."""
        return self._drivers.has_property_path(target_url)


    # ======================================================================== #
    # ======================================================================== #

    def get_current_morph_shape(self:Self, vertex_count:int) -> DsonMorph:

        morph_deltas:dict = {}

        for (name, struct) in self._modifiers.items():

            # Modifier has no morph data, so skip it.
            if not struct.morph:
                continue

            # NOTE: iSourceTextures's Evangeliya has a value of -1, so clearly
            #   this is not checked and doesn't matter.
            # if not struct.morph.expected_vertices == vertex_count:
            #     continue

            # Construct URL to get DriverTarget object.
            address:AssetAddress = AssetAddress.from_url(name)
            address.property_path = struct.channel.channel_id
            property_url:str = address.get_url_to_property()

            # Get wrapper object which holds channel data.
            driver_target:DriverTarget = self._drivers.get_driver_target(property_url)

            # Amount of morph to apply.
            strength:float = driver_target.get_value()

            # Morph will have no affect, so skip it.
            if isclose(strength, 0.0):
                continue

            # Calculate vertex positions.
            for (index, vertex) in struct.morph.deltas.items():

                # Add an empty vector if vertex hasn't been added yet.
                if index not in morph_deltas:
                    morph_deltas[index] = DsonVector(0.0, 0.0, 0.0)

                # Update the vertex's positions.
                morph_deltas[index].x += (vertex.x * strength)
                morph_deltas[index].y += (vertex.y * strength)
                morph_deltas[index].z += (vertex.z * strength)

        # Return new DsonMorph object.
        result:DsonMorph = DsonMorph()
        result.expected_vertices = vertex_count
        result.deltas = morph_deltas

        return result


    # ------------------------------------------------------------------------ #

    def get_current_node_shape(self:Self, target_url:str) -> DsonNode:

        # We want to loop through all of a node's properties and update all of
        #   them at once, so convert it to an asset_url which will be used to
        #   retrieve all its stored property_paths.
        address:AssetAddress = AssetAddress.from_url(target_url)
        asset_url:str = address.get_url_to_asset()

        # Ensure DsonNode was actually loaded.
        if not asset_url in self._nodes:
            # TODO: Raise an exception instead?
            return None

        # Get the node stored inside the DriverMap, then copy it so we can
        #   return a new copy with the updated values.
        source_node:DsonNode = self._nodes[asset_url]
        copied_node:DsonNode = deepcopy(source_node)

        # Get all property_path variables and loop through them.
        for property_path in self._drivers.get_all_property_paths(asset_url):

            # The URL pointing to the property stored inside the DsonNode.
            property_url:str = AssetAddress.format_url_as_string(filepath=address.filepath, asset_id=address.asset_id, property_path=property_path)

            # Use helper method to extract the nested DsonChannel object from
            #   the DsonNode object.
            channel:DsonChannel = DriverTarget.get_channel_object(copied_node, property_url)

            # Update the node's properties.
            channel.current_value = self.get_driver_value(property_url)

        return copied_node


    # ======================================================================== #
    # ======================================================================== #

    def get_joint_controlled_morphs(self:Self) -> None:

        for property_url in self._drivers.get_all_stored_urls():
            driver_target:DriverTarget = self._drivers.get_driver_target(property_url)
            print(repr(driver_target))

        return


    # ======================================================================== #
    # PRIVATE IMPLEMENTATION METHODS                                           #
    # ======================================================================== #

    def _load_asset(self:Self, struct:Any, property_path:str, library_type:LibraryType) -> None:

        # TODO: How and where to implement dummy properties?
        # TODO: Should the struct argument replace or update an earlier one?

        # Format and validate URL
        address:AssetAddress = AssetAddress.from_url(str(struct.dsf_file))
        if not address.filepath and not address.asset_id:
            raise ValueError
        address.property_path = property_path

        # Used to instantiate asset struct.
        asset_url:str = address.get_url_to_asset()

        # Create a flag to see if DsonNode/DsonModifier has been parsed already.
        # Modifiers only have a single property, but nodes have two dozen. We
        #   need to make sure the formulas are only parsed once per asset, or
        #   else we will end up with many duplicate formulas stacking operations
        #   on top of each other.
        is_first_time:bool = False

        # This is an alias for the struct argument.
        asset:Any = None

        # Add object to internal dictionary
        if library_type == LibraryType.MODIFIER:
            if not asset_url in self._modifiers:
                self._modifiers[asset_url] = struct
                is_first_time = True
            asset = self._modifiers[asset_url]

        elif library_type == LibraryType.NODE:
            if not asset_url in self._nodes:
                self._nodes[asset_url] = struct
                is_first_time = True
            asset = self._nodes[asset_url]

        elif not library_type:
            pass

        else:
            raise NotImplementedError(library_type)

        # Used as key for DriverDictionary
        property_url:str = address.get_url_to_property()

        # Get DriverTarget associated with this URL, or create one if it doesn't
        #   exist.
        # TODO: Update the struct stored inside the DriverTarget if it already
        #   exists?
        driver_target:DriverTarget = self._drivers.get_driver_target(property_url)
        if not driver_target:
            driver_target = DriverTarget(property_url, asset, library_type)
            self._drivers.add_driver_target(property_url, driver_target)

        # Create formula objects.
        if is_first_time:

            equations:list[DriverEquation] = None

            # DsonModifier
            if library_type == LibraryType.MODIFIER and asset.formulas:
                equations = self._parse_formulas(address.filepath, asset.formulas)

            # DsonNode
            elif library_type == LibraryType.NODE and asset.formulas:
                equations = self._parse_formulas(address.filepath, asset.formulas)

            self._equations[asset_url] = equations

        return


    # ======================================================================== #
    # ======================================================================== #

    def _parse_formulas(self:Self, filepath:str, formula_list:list[DsonFormula]) -> list[DriverEquation]:

        # TODO: How does "auto_follow" work for JCMs?

        equations:list[DriverEquation] = []

        for formula in formula_list:

            equation:DriverEquation = DriverEquation(formula)
            equations.append(equation)

            # Handle input URLs
            for operation in formula.operations:
                if not operation.url:
                    continue
                self._parse_url(equation, operation.url, filepath, True)

            # Handle output URLs
            self._parse_url(equation, formula.output, filepath, False)

        return equations


    # ======================================================================== #
    # ======================================================================== #

    def _parse_url(self:Self, equation:DriverEquation, url_string:str, dsf_filepath:str, is_input:bool) -> None:

        # Format URL
        address:AssetAddress = AssetAddress.from_url(url_string)
        if not address.filepath:
            address.filepath = dsf_filepath

        # Create variables to instantiate assets
        asset_url:str = address.get_url_to_asset()

        # TODO: Reuse "asset_dson" to streamline this
        # TODO: Daz Studio has faulty logic. An AssetAddress should have a URL
        #   unless it points to the same file. But according to
        #   eJCMMemphisEyesClosedL.dsf, it can also refer to the Genesis8Female
        #   file. So clearly it checks if the property exists on the figure,
        #   and only uses the URL to load it if it doesn't.
        #   Use the "parent" property to keep track of which object it belongs
        #   to instead.

        try:
            asset_type, asset_dson = find_asset_dson_in_library(asset_url)
        except FileNotFoundError:
            # FIXME: Quick and dirty hack. Should be replaced when implementing
            #   dummy properties.
            return

        # Recursively load any dependencies (which may call _parse_formulas()
        #   again) this driver relies on.
        if asset_type == LibraryType.MODIFIER:
            struct:DsonModifier = DsonModifier.load_from_file(asset_url)
            self.load_modifier(struct)
        elif asset_type == LibraryType.NODE:
            struct:DsonNode = DsonNode.load_from_file(asset_url)
            self.load_node(struct, address.property_path)
        else:
            raise NotImplementedError(asset_type)

        # Get the DriverTarget from the internal database. This should have
        #   been added before _parse_formulas() was called.
        target_url:str = address.get_url_to_property()
        driver_target:DriverTarget = self._drivers.get_driver_target(target_url)

        # Link DriverTargets and DriverEquations
        if is_input:
            driver_target.subcomponents.append(equation)
            equation.inputs[url_string] = driver_target
        else:
            driver_target.controllers.append(equation)
            equation.output = driver_target

        return
