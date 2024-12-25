from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, field
from math import isclose
from typing import Any, Self

from dufman.datatypes.vector import DsonVector
from dufman.enums import (
    ChannelType,
    FormulaOperator,
    FormulaStage,
    LibraryType,
)
from dufman.library import find_library_containing_asset_id
from dufman.structs.channel import DsonChannel, DsonChannelFloat
from dufman.structs.formula import DsonFormula
from dufman.structs.modifier import DsonModifier
from dufman.structs.morph import DsonMorph
from dufman.structs.node import DsonNode
from dufman.url import AssetAddress


# ============================================================================ #
#                                                                              #
# ============================================================================ #

class PropertyMap:

    def __init__(self:PropertyMap) -> Self:

        # These dictionaries contain the nodes/modifiers which hold channel
        #   objects.
        self._modifiers:dict = {}
        self._nodes:dict = {}
        self._invalid:dict = {}

        # This stores the hierarchical list of Property objects. It is keyed
        #   with the property URL.
        #   i.e. "/data/path/to/asset.dsf#ModifierAsset?value"
        self._properties:dict = {}

        # This stores the list of Formula objects which have been created.
        #   It is keyed by the asset's URL, to ensure assets are only parsed
        #   once.
        #   i.e. "/data/path/to/asset.dsf#ModifierAsset"
        self._formulas:dict = {}

        return


    # ======================================================================== #
    # MODIFIER METHODS                                                         #
    # ======================================================================== #

    def get_loaded_modifiers(self:PropertyMap) -> list[str]:
        return list(self._modifiers.keys())


    # ------------------------------------------------------------------------ #

    def get_modifier(self:PropertyMap, target_url:str) -> DsonModifier:
        address:AssetAddress = AssetAddress.create_from_url(target_url)
        asset_url:str = address.get_url_to_asset()
        return self._modifiers[asset_url] if asset_url in self._modifiers else None


    # ------------------------------------------------------------------------ #

    def is_modifier_loaded(self:PropertyMap, target_url:str) -> bool:
        address:AssetAddress = AssetAddress.create_from_url(target_url)
        asset_url:str = address.get_url_to_asset()
        return asset_url in self._modifiers


    # ======================================================================== #
    # NODE METHODS                                                             #
    # ======================================================================== #

    def get_loaded_nodes(self:PropertyMap) -> list[str]:
        return list(self._nodes.keys())


    # ------------------------------------------------------------------------ #

    def get_node(self:PropertyMap, target_url:str) -> DsonNode:
        address:AssetAddress = AssetAddress.create_from_url(target_url)
        asset_url:str = address.get_url_to_asset()
        return self._nodes[asset_url] if asset_url in self._nodes else None


    # ------------------------------------------------------------------------ #

    def is_node_loaded(self:PropertyMap, target_url:str) -> bool:
        address:AssetAddress = AssetAddress.create_from_url(target_url)
        asset_url:str = address.get_url_to_asset()
        return asset_url in self._nodes


    # ======================================================================== #
    # FILEPATH METHODS                                                         #
    # ======================================================================== #

    def _get_filepath_dictionary(self:PropertyMap) -> dict:
        return self._properties


    # ------------------------------------------------------------------------ #

    def get_all_filepaths(self:PropertyMap) -> list[str]:
        filepaths:dict = self._get_filepath_dictionary()
        return list(filepaths.keys())


    # ------------------------------------------------------------------------ #

    def has_filepath(self:PropertyMap, target_url:str) -> bool:
        address:AssetAddress = AssetAddress.create_from_url(target_url)
        return address.filepath in self._properties


    # ======================================================================== #
    # ASSET METHODS                                                            #
    # ======================================================================== #

    def _get_asset_id_dictionary(self:PropertyMap, address:AssetAddress) -> dict:

        if isinstance(address, str):
            address = AssetAddress.create_from_url(address)

        if address.filepath in self._properties:
            return self._properties[address.filepath]

        return None


    # ------------------------------------------------------------------------ #

    def get_all_asset_ids(self:PropertyMap, target_url:str) -> list[str]:

        address:AssetAddress = AssetAddress.create_from_url(target_url)

        asset_ids:dict = self._get_asset_id_dictionary(address)
        if not asset_ids:
            return []

        return list(asset_ids.keys())


    # ------------------------------------------------------------------------ #

    def has_asset_id(self:PropertyMap, target_url:str, *, asset_id:str=None) -> bool:

        address:AssetAddress = AssetAddress.create_from_url(target_url)
        if not address.asset_id and asset_id:
            address.asset_id = asset_id

        asset_ids:dict = self._get_asset_id_dictionary(address)
        if not asset_ids:
            return False

        return address.asset_id in asset_ids


    # ======================================================================== #
    # PROPERTY METHODS                                                         #
    # ======================================================================== #

    def _add_property_object(self:PropertyMap, address:AssetAddress, new_property:Property) -> None:

        if isinstance(address, str):
            address = AssetAddress.create_from_url(address)

        filepaths:dict = self._properties
        if address.filepath not in filepaths:
            filepaths[address.filepath] = {}

        asset_ids:dict = filepaths[address.filepath]
        if address.asset_id not in asset_ids:
            asset_ids[address.asset_id] = {}

        properties:dict = asset_ids[address.asset_id]
        if address.property_path not in properties:
            properties[address.property_path] = {}

        properties[address.property_path] = new_property

        return


    # ------------------------------------------------------------------------ #

    def _get_property_dictionary(self:PropertyMap, address:AssetAddress) -> dict:

        if isinstance(address, str):
            address = AssetAddress.create_from_url(address)

        filepaths:dict = self._properties
        if address.filepath not in filepaths:
            return None

        asset_ids:dict = filepaths[address.filepath]
        if address.asset_id not in asset_ids:
            return None

        return asset_ids[address.asset_id]


    # ------------------------------------------------------------------------ #

    def get_property_object(self:PropertyMap, address:AssetAddress) -> Property:

        if isinstance(address, str):
            address = AssetAddress.create_from_url(address)

        # TODO: Exceptions?
        properties:dict = self._get_property_dictionary(address)
        if properties and address.property_path in properties:
            return properties[address.property_path]

        return None


    # ------------------------------------------------------------------------ #

    def get_property_value(self:PropertyMap, target_url:str) -> Any:
        prop:Property = self.get_property_object(target_url)
        return prop.get_value()


    # ------------------------------------------------------------------------ #

    def get_all_property_paths(self:PropertyMap, target_url:str) -> list[str]:

        address:AssetAddress = AssetAddress.create_from_url(target_url)

        properties:dict = self._get_property_dictionary(address)
        if not properties:
            return []

        return list(properties.keys())


    # ------------------------------------------------------------------------ #

    def get_all_property_urls(self:PropertyMap) -> list[str]:

        result:list[str] = []

        for (filepath, filepaths) in self._properties.items():
            for (asset_id, asset_ids) in filepaths.items():
                for (prop_path, _prop_paths) in asset_ids.items():
                    address:AssetAddress = AssetAddress.create_from_components(filepath=filepath, asset_id=asset_id, property_path=prop_path)
                    result.append(address.get_url_to_property())

        return result


    # ------------------------------------------------------------------------ #

    def has_property_path(self:PropertyMap, target_url:str, *, property_path:str=None) -> bool:

        address:AssetAddress = AssetAddress.create_from_url(target_url)
        if not address.property_path and property_path:
            address.property_path = property_path

        property_paths:dict = self._get_property_dictionary(address)
        if not property_paths:
            return False

        return address.property_path in property_paths


    # ------------------------------------------------------------------------ #

    def set_property_value(self:PropertyMap, target_url:str, new_value:Any) -> None:
        prop:Property = self.get_property_object(target_url)
        prop.set_value(new_value)
        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def load_property_from_file(self:PropertyMap, url_string:str) -> None:

        # Split URL into components.
        address:AssetAddress = AssetAddress.create_from_url(url_string)

        # Retrieve and/or instantiate the DSON dataclass associated with the
        #   asset.
        asset:Any = self._load_asset(address)

        # If the URL was passed into the function by a user and it does not
        #   have a property_path, then see if we can extract it.
        if not address.property_path:
            if isinstance(asset, DsonModifier):
                address.property_path = asset.channel.channel_id
            else:
                raise ValueError("URL does not have a property_path.")

        # The path to the channel we want to retrieve.
        property_url:str = address.get_url_to_property()

        # Property has already been parsed.
        if self.has_property_path(property_url):
            return

        # Find the channel inside the asset we want to use for this property.
        channel:DsonChannel = self._get_channel_from_asset(address, asset)

        # Create new property and add it to the internal dictionary.
        property_data:Property = Property(property_url, channel)
        self._add_property_object(property_url, property_data)

        # Parse the asset's formulas and link them together.
        self._parse_asset_formulas(address, asset)

        return


    # ------------------------------------------------------------------------ #

    def _load_asset(self:PropertyMap, address:AssetAddress) -> Any:
        """Loads and stores a DSON dataclass inside the PropertyMap."""

        # Validate input.
        if not address.filepath or not address.asset_id:
            raise ValueError("URL must have a filepath and an asset ID component.")

        # Get filepath to DSF file.
        asset_url:str = address.get_url_to_asset()

        # Extract asset type from DSF file.
        try:
            library_type:LibraryType = find_library_containing_asset_id(asset_url)
        except FileNotFoundError:
            library_type:LibraryType = None

        # Asset could not be loaded. Insert it into the dictionary so we can
        #   create dummy assets to be loaded later.
        if library_type is None:
            self._invalid[asset_url] = None
            return None

        # Determine which type of asset object to instantiate.
        match library_type:

            # Modifier
            case LibraryType.MODIFIER:
                if not asset_url in self._modifiers:
                    self._modifiers[asset_url] = DsonModifier.load(asset_url)
                return self._modifiers[asset_url]

            # Node
            case LibraryType.NODE:
                if not asset_url in self._nodes:
                    self._nodes[asset_url] = DsonNode.load(asset_url)
                return self._nodes[asset_url]

            # Unknown
            case _:
                raise NotImplementedError(library_type)


    # ------------------------------------------------------------------------ #

    def _get_channel_from_asset(self:PropertyMap, address:AssetAddress, asset:Any) -> DsonChannel:
        """Retrieves a DsonChannel dataclass using a URL's property path."""

        if isinstance(asset, DsonModifier):

            if address.property_path == asset.channel.channel_id:
                return asset.channel
            raise NotImplementedError(address.property_path)

        if isinstance(asset, DsonNode):

            match address.property_path:

                # Center point
                case "center_point/x":
                    return asset.center_point.x
                case "center_point/y":
                    return asset.center_point.y
                case "center_point/z":
                    return asset.center_point.z

                # End point
                case "end_point/x":
                    return asset.end_point.x
                case "end_point/y":
                    return asset.end_point.y
                case "end_point/z":
                    return asset.end_point.z

                # Translation
                case "translation/x":
                    return asset.translation.x
                case "translation/y":
                    return asset.translation.y
                case "translation/z":
                    return asset.translation.z

                # Orientation
                case "orientation/x":
                    return asset.orientation.x
                case "orientation/y":
                    return asset.orientation.y
                case "orientation/z":
                    return asset.orientation.z

                # Rotation
                case "rotation/x":
                    return asset.rotation.x
                case "rotation/y":
                    return asset.rotation.y
                case "rotation/z":
                    return asset.rotation.z

                # Scale
                case "scale/general":
                    return asset.general_scale
                case "scale/x":
                    return asset.scale.x
                case "scale/y":
                    return asset.scale.y
                case "scale/z":
                    return asset.scale.z

                case _:
                    raise NotImplementedError(address.property_path)


    # ------------------------------------------------------------------------ #

    def _parse_asset_formulas(self:PropertyMap, address:AssetAddress, asset:Any) -> None:
        """Loops through a DSON dataclass's formulas and builds the property hierarchy."""

        # TODO: How does "auto_follow" work for JCMs?

        # Modifiers only have a single property, but nodes have over two dozen.
        #   We need to make sure the formula list is only parsed once, or else
        #   we will end up with many duplicate formulas stacking operations on
        #   top of each other.
        # If the URL already exists, then return.
        if address.filepath in self._formulas and address.asset_id in self._formulas[address.filepath]:
            return

        # Ensure DSF filepath exists in dictionary.
        filepaths:dict = self._formulas
        if not address.filepath in filepaths:
            filepaths[address.filepath] = {}

        # Ensure Asset ID exists in dictionary.
        asset_ids:dict = filepaths[address.filepath]
        if not address.asset_id in asset_ids:
            asset_ids[address.asset_id] = []

        # Asset has nothing to parse.
        # TODO: Should this go before or after the other error checking?
        if not hasattr(asset, "formulas") or not asset.formulas:
            return

        for formula_struct in asset.formulas:

            formula:Formula = Formula(formula_struct)
            asset_ids[address.asset_id].append(formula)

            # Inputs
            for operation in formula_struct.operations:
                if not operation.url:
                    continue

                # Handle input URLs
                input_address:AssetAddress = AssetAddress.create_from_url(operation.url)
                if not input_address.filepath:
                    input_address.filepath = address.filepath
                input_url:str = input_address.get_url_to_property()
                self.load_property_from_file(input_url)

                # Link properties and formulas.
                input_property:Property = self.get_property_object(input_url)
                formula.inputs[operation.url] = input_property
                input_property.subcomponents.append(formula)

            # Output
            output_address:AssetAddress = AssetAddress.create_from_url(formula_struct.output)
            if not output_address.filepath:
                output_address.filepath = address.filepath
            output_url:str = output_address.get_url_to_property()
            self.load_property_from_file(output_url)

            # Link properties and formulas.
            output_property:Property = self.get_property_object(output_url)
            formula.output = output_property
            output_property.controllers.append(formula)

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def get_morph_shape(self:PropertyMap, vertex_count:int) -> DsonMorph:

        morph_deltas:dict = {}

        for (name, struct) in self._modifiers.items():

            # Modifier has no morph data, so skip it.
            if not struct.morph:
                continue

            # NOTE: iSourceTextures's Evangeliya has a value of -1, so clearly
            #   this property is not checked and doesn't matter.
            # if not struct.morph.expected_vertices == vertex_count:
            #     continue

            # Get URL to retrieve Property object.
            address:AssetAddress = AssetAddress.create_from_url(name)
            address.property_path = struct.channel.channel_id
            property_url:str = address.get_url_to_property()

            # Wrapper object to calculate hierarchical value.
            prop:Property = self.get_property_object(property_url)

            # Amount of morph to apply.
            strength:float = prop.get_value()

            # Morph will have no affect, skip it.
            if isclose(strength, 0.0):
                continue

            # Calculate vertex positions.
            for (index, vertices) in struct.morph.deltas.items():
                if not index in morph_deltas:
                    morph_deltas[index] = DsonVector(0.0, 0.0, 0.0)
                morph_deltas[index].x += vertices.x * strength
                morph_deltas[index].y += vertices.y * strength
                morph_deltas[index].z += vertices.z * strength

        # Create new DsonMorph object to return.
        result:DsonMorph = DsonMorph()
        result.expected_vertices = vertex_count
        result.deltas = morph_deltas

        return result


    # ------------------------------------------------------------------------ #

    def get_adjusted_node(self:PropertyMap, target_url:str) -> DsonNode:

        address:AssetAddress = AssetAddress.create_from_url(target_url)
        asset_url:str = address.get_url_to_asset()

        source_node:DsonNode = self.get_node(asset_url)
        copied_node:DsonNode = deepcopy(source_node)

        for prop in self.get_all_property_paths(asset_url):

            address.property_path = prop
            property_url:str = address.get_url_to_property()

            channel:DsonChannel = self._get_channel_from_asset(address, copied_node)
            channel.current_value = self.get_property_value(property_url)

        return copied_node


# ============================================================================ #
#                                                                              #
# ============================================================================ #

class Property:

    def __init__(self:Property, property_url:str, channel:DsonChannel) -> Self:

        # URL should be validated before being passed in.
        self._property_url = property_url
        self._channel:DsonChannel = channel
        self.controllers:list[Formula] = []
        self.subcomponents:list[Formula] = []

        # If DSF file could not be found, then this is a dummy object which
        #   caches relationship data so it can be inserted later.
        if not self._channel:
            return

        self._raw_value:Any = self._channel.get_value()

        return


    def __str__(self:Property) -> str:
        return self._property_url


    def __repr__(self:Property) -> str:
        return f"Property(\"{str(self)}\")"


    # ======================================================================== #

    def is_valid(self:Property) -> bool:
        return self._channel is not None


    # ------------------------------------------------------------------------ #

    def get_type(self:Property) -> ChannelType:
        """Returns the ChannelType of the property."""
        if self.is_valid():
            return self._channel.channel_type
        else:
            return None


    # ======================================================================== #

    # def get_clamped(self:Property) -> bool:
    #     """Returns whether the value will be clamped between minimum and maximum."""

    #     channel_type:ChannelType = self.get_type()

    #     if not channel_type in { ChannelType.BOOL, ChannelType.FLOAT, ChannelType.INT }:
    #         raise ChannelCannotBeClamped

    #     # if "clamped" in self._channel_json:
    #     #     return self._channel_json["clamped"]

    #     return False


    # def set_clamped(self:Property, should_clamp:bool) -> None:
    #     """Sets whether the value will be clamped between minimum and maximum."""

    #     channel_type:ChannelType = self.get_type()

    #     if not channel_type in { ChannelType.BOOL, ChannelType.FLOAT, ChannelType.INT }:
    #         raise ChannelCannotBeClamped

    #     #self._channel_json["clamped"] = bool(should_clamp)

    #     return


    # ======================================================================== #

    # def get_minimum(self:Property) -> Any:

    #     channel_type:ChannelType = self.get_type()

    #     if not channel_type in { ChannelType.BOOL, ChannelType.FLOAT, ChannelType.INT }:
    #         raise ChannelCannotBeClamped

    #     #return self._channel_json["min"] if "min" in self._channel_json else 0.0
    #     return None


    # def get_maximum(self:Property) -> Any:

    #     channel_type:ChannelType = self.get_type()

    #     if not channel_type in { ChannelType.BOOL, ChannelType.FLOAT, ChannelType.INT }:
    #         raise ChannelCannotBeClamped

    #     #return self._channel_json["max"] if "max" in self._channel_json else 0.0
    #     return None


    # ======================================================================== #

    def get_value(self:Property) -> Any:
        """Returns the value stored inside the property."""

        if not self.is_valid():
            return None

        match ChannelType(self.get_type()):
            case ChannelType.FLOAT:
                return self._get_float_value()
            case _:
                raise NotImplementedError


    # ------------------------------------------------------------------------ #

    def set_value(self:Property, new_value:Any) -> None:
        """Updates the value inside the stored property."""

        if not self.is_valid():
            return

        match ChannelType(self.get_type()):
            case ChannelType.FLOAT:
                self._set_float_value(new_value)
            case _:
                raise NotImplementedError


    # ======================================================================== #

    def _set_float_value(self:Property, new_value:Any) -> None:
        # TODO: Does this need to recursively update its subcomponents, or is
        #   get_value() robust enough to travel all the way up the hierarchy?
        self._raw_value = float(new_value)
        return


    def _get_float_value(self:Property) -> float:

        # Formula objects which contribute to the final value.
        stage_sum:list[Formula] = []
        stage_mult:list[Formula] = []

        # Gather Formula objects.
        for controller in self.controllers:
            stage:FormulaStage = controller.get_stage()
            match stage:
                case FormulaStage.SUM:
                    stage_sum.append(controller)
                case FormulaStage.MULTIPLY:
                    stage_mult.append(controller)
                case _:
                    raise NotImplementedError

        # Convenience variable
        channel:DsonChannelFloat = self._channel

        # Return value
        value:float = float(self._raw_value)

        # Sum formulas
        for formula in stage_sum:
            value += float(formula.get_value())

        # Multiply formulas
        multiply:float = 1.0
        for formula in stage_mult:
            multiply *= float(formula.get_value())
        value *= multiply

        # Clamp value
        if channel.clamp_values:
            value = max(channel.minimum_value, min(value, channel.maximum_value))

        return value


# ============================================================================ #
#                                                                              #
# ============================================================================ #

@dataclass
class Formula:

    formula:DsonFormula = None
    inputs:dict = field(default_factory=dict)
    output:Property = None


    def get_value(self:Formula) -> Any:

        stack:list[Any] = []

        for operation in self.formula.operations:

            match operation.operator:

                # Push
                case FormulaOperator.PUSH:
                    if operation.url:
                        input_property:Property = self.inputs[operation.url]
                        # NOTE: input_property.get_value() will travel up the
                        #   hierarchy, recursively calling this method to get
                        #   the value of all contributing formulas.
                        stack.append(input_property.get_value())
                    elif operation.value:
                        stack.append(operation.value)

                # Multiply
                case FormulaOperator.MULT:
                    value1:Any = stack.pop()
                    value2:Any = stack.pop()
                    result:Any = value1 * value2
                    stack.append(result)

        if len(stack) != 1:
            raise Exception("Stack should only have one value to return")

        return stack[0]


    def get_stage(self:Formula) -> FormulaStage:
        """Returns an enum determining how the result is applied to the property."""
        return self.formula.stage
