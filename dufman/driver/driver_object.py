# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""This module defines classes to calculate driver values."""

# stdlib
from typing import Any, Self

# dufman
from dufman.enums import (
    ChannelType,
    FormulaOperator,
    FormulaStage,
    LibraryType,
)
from dufman.library import (
    find_library_containing_asset_id,
    get_single_property_from_library,
)
from dufman.spline import (
    calculate_linear_spline,
    calculate_tcb_spline,
    Knot,
    TcbKnot,
)
from dufman.structs.channel import (
    DsonChannel,
    DsonChannelFloat,
)
from dufman.structs.formula import DsonFormula
from dufman.structs.modifier import DsonModifier
from dufman.structs.node import DsonNode
from dufman.url import AssetAddress


# ============================================================================ #
# DRIVER TARGET                                                                #
# ============================================================================ #

class DriverTarget:
    """A class containting a property used to control another property.

    DriverTarget is a wrapper around an object which contains a channel. It can
    be either a DsonModifier (which has a single channel) or a DsonNode (which
    has multiple channels that define its 3D transform). When the value of the
    channel is requested, this object will recursively travel up the chain of
    DriverTargets and DriverEquations to compute the final value.

    If the asset could not be loaded, this becomes a dummy property which stores
    its contextual relationships so they can be inserted later.
    """

    # ======================================================================== #

    def __init__(self:Self, target_url:str, asset_struct:Any, library_type:LibraryType) -> Self:

        # Object properties
        self._target_url:str = target_url
        self._asset:Any = asset_struct
        self._library_type:LibraryType = library_type

        # Relationship data
        self.controllers:list[DriverEquation] = []
        self.subcomponents:list[DriverEquation] = []

        # This is a dummy object which stores relational data, to be fixed
        #   later.
        if not self._asset:
            return

        # Since the object is valid, populate the data fields.
        self._channel:DsonChannel = DriverTarget.get_channel_object(self._asset, self._target_url)
        self._raw_value = self._channel.get_value()

        return


    # ------------------------------------------------------------------------ #

    def __str__(self:Self) -> str:
        return self._target_url


    # ------------------------------------------------------------------------ #

    def __repr__(self:Self) -> str:
        return f"DriverTarget(\"{ str(self) }\")"


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    @staticmethod
    def get_asset_library_info(target_url:str, *, property_path:str=None) -> tuple[str, LibraryType]:
        """Format the URL and the fetch the LibraryType from the DSF file."""

        # Ensure URL is formatted correctly.
        address:AssetAddress = AssetAddress.from_url(target_url)
        if not address.filepath or not address.asset_id:
            raise ValueError("URL argument requires both a filepath and an asset ID.")

        # Get filepath for library functions.
        asset_url:str = address.get_url_to_asset()

        # Extract asset type from DSF file.
        try:
            library_type:LibraryType = find_library_containing_asset_id(asset_url)
        except FileNotFoundError:
            library_type:LibraryType = None

        # If URL has no property_path and one was passed in as an argument,
        #   replace it.
        if not address.property_path and property_path:
            address.property_path = property_path

        # If URL still doesn't have a property_path and it is a DsonModifier,
        #   extract the channel's ID from the disk.
        if not address.property_path and library_type == LibraryType.MODIFIER:
            keys:list[str] = [ LibraryType.MODIFIER.value, address.asset_id, "channel", "id" ]
            channel_id:str = get_single_property_from_library(address.filepath, keys)
            address.property_path = channel_id

        # If we still don't have a property_path, we can't do anything.
        if not address.property_path:
            raise ValueError("\"property_path\" could not be deduced from URL.")

        return (address.get_url_to_property(), library_type)


    # ------------------------------------------------------------------------ #

    @staticmethod
    def load_asset(target_url:str, library_type:LibraryType) -> Any:
        """Load an asset containing a channel from disk."""

        # Validate URL.
        address:AssetAddress = AssetAddress.from_url(target_url)
        if not address.filepath and not address.asset_id and not address.property_path:
            raise ValueError("URL does not contain enough info to locate channel.")

        # The path to an asset inside a DSF file.
        asset_url:str = address.get_url_to_asset()

        # The struct which will hold the data extracted with the asset_url.
        struct:Any = None

        # If the DSF file could not be loaded, the null pointer will flag it
        #   as invalid.
        if library_type:
            match library_type:

                # DsonModifier
                case LibraryType.MODIFIER:
                    struct = DsonModifier.load(asset_url)

                # DsonNode
                case LibraryType.NODE:
                    struct = DsonNode.load(asset_url)

                # Unknown
                case _:
                    raise NotImplementedError(library_type)

        return struct


    # ------------------------------------------------------------------------ #

    @staticmethod
    def get_channel_object(asset:Any, property_url:str) -> DsonChannel:
        """Return the DsonChannel object from an asset struct."""

        # Validate URL
        address:AssetAddress = AssetAddress.from_url(property_url)
        if not address.filepath and not address.asset_id and not address.property_path:
            raise ValueError("URL does not contain enough info to locate channel.")

        # DsonModifier
        if isinstance(asset, DsonModifier):
            if address.property_path == asset.channel.channel_id:
                return asset.channel
            raise NotImplementedError(address.property_path)

        # DsonNode
        elif isinstance(asset, DsonNode):
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

                # Unknown
                case _:
                    raise NotImplementedError(address.property_path)

        return None


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def get_channel_type(self:Self) -> ChannelType:
        """Return the ChannelType of the underlying DsonChannel object."""
        if not self.is_valid():
            return None
        return self._channel.channel_type


    # ------------------------------------------------------------------------ #

    def get_value(self:Self) -> Any:
        """Return the current value of this DriverTarget."""

        if not self.is_valid():
            raise RuntimeError("Attempted to get a dummy DriverTarget's value.")

        channel_type:ChannelType = self.get_channel_type()
        match channel_type:
            case ChannelType.FLOAT:
                return self._get_float_value()
            case _:
                raise NotImplementedError(channel_type)


    # ------------------------------------------------------------------------ #

    def is_valid(self:Self) -> bool:
        """Check if this DriverTarget has a DsonChannel."""
        return self._asset is not None


    # ------------------------------------------------------------------------ #

    def set_value(self:Self, new_value:Any) -> None:
        """Update the current value of this DriverTarget."""

        if not self.is_valid():
            raise RuntimeError("Attempted to set a dummy DriverTarget's value.")

        # TODO: Is get_value() robust enough to recursively compute the value,
        #   or do we need to propagate and cache an update from this method?
        channel_type:ChannelType = self.get_channel_type()
        match channel_type:
            case ChannelType.BOOL:
                self._raw_value = bool(new_value)
            case ChannelType.FLOAT:
                self._raw_value = float(new_value)
            case _:
                raise NotImplementedError

        return


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def _get_float_value(self:Self) -> Any:

        # Sort equations which contribute to the final value.
        stage_sum:list[DriverEquation] = []
        stage_mult:list[DriverEquation] = []

        # Gather up equation objects.
        for controller in self.controllers:
            stage:FormulaStage = controller.get_stage()
            match stage:
                case FormulaStage.SUM:
                    stage_sum.append(controller)
                case FormulaStage.MULTIPLY:
                    stage_mult.append(controller)
                case _:
                    # NOTE: According to the DSON specs, more stage types may
                    #   be introduced in the future.
                    raise NotImplementedError(stage)

        # Convenience variable.
        channel:DsonChannelFloat = self._channel

        # Return value.
        value:float = float(self._raw_value)

        # Sum equations.
        for equation in stage_sum:
            value += float(equation.get_value())

        # Multiply equations.
        multiply:float = 1.0
        for equation in stage_mult:
            multiply *= float(equation.get_value())
        value *= multiply

        # Clamp value.
        if channel.clamp_values:
            value = max(channel.minimum_value, min(value, channel.maximum_value))

        return value


# ============================================================================ #
# DRIVER EQUATION                                                              #
# ============================================================================ #

class DriverEquation:
    """A class that handles calculating driver values.

    DriverEquation is a wrapper around a DsonFormula node. It stores the node
    itself along with contextual data pointing to the DriverTarget objects it
    needs to derive the equation's result.
    """

    # ======================================================================== #

    def __init__(self:Self, struct:DsonFormula) -> Self:

        if not struct or not isinstance(struct, DsonFormula):
            raise TypeError

        self.struct:DsonFormula = struct
        self.inputs:dict = {}
        self.output:DriverTarget = None

        return


    # ------------------------------------------------------------------------ #

    def __str__(self:Self) -> str:
        return self.get_equation_as_string()


    # ------------------------------------------------------------------------ #

    def __repr__(self:Self) -> str:
        return f"DriverEquation(\"{ str(self) }\")"


    # ======================================================================== #

    @staticmethod
    def _strip_url(url_string:str) -> str:
        """Format a URL so it consists of an asset ID and a property path."""
        address:AssetAddress = AssetAddress.from_url(url_string)
        return AssetAddress.format_url_as_string(asset_id=address.asset_id, property_path=address.property_path)


    # ======================================================================== #

    def get_equation_as_string(self:Self) -> str:
        """Create a user-readable string identifying how the equation works."""

        stack:list[Any] = []

        for operation in self.struct.operations:
            match operation.operator:

                case FormulaOperator.PUSH:
                    if operation.value:
                        stack.append(operation.value)
                    elif operation.url:
                        stack.append(self._strip_url(operation.url))

                case FormulaOperator.MULT:
                    value1:Any = stack.pop()
                    value2:Any = stack.pop()
                    result:str = f"({value1} * {value2})"
                    stack.append(result)

                case FormulaOperator.SPL_TCB | FormulaOperator.SPL_LINEAR:
                    number_of_knots:int = stack.pop()
                    knots:list[Knot] = []

                    for _ in range(number_of_knots):
                        data:list = stack.pop()
                        knot:Knot = Knot()
                        knot.x = data[0]
                        knot.y = data[1]
                        knots.append(knot)

                    _value:Any = stack.pop()
                    stack.append("IMPLEMENT SPLINE PRINTING")

                case _:
                    raise NotImplementedError(operation.operator)

        output:str = self._strip_url(self.struct.output)
        return f"{output} = {stack[0]}"


    # ------------------------------------------------------------------------ #

    def get_stage(self:Self) -> FormulaStage:
        """Return the FormulaStage of the underlying DsonFormula struct."""
        return self.struct.stage


    # ------------------------------------------------------------------------ #

    def get_value(self:Self) -> Any:
        """Return the final value of the equation.
        
        This is equivalent to calculating the "output" property of a DsonFormula
        struct.
        """

        stack:list[Any] = []

        for operation in self.struct.operations:
            match operation.operator:

                # ------------------------------------------------------------ #
                # Push
                case FormulaOperator.PUSH:

                    if operation.value:
                        stack.append(operation.value)

                    elif operation.url:
                        # NOTE: This code is indirectly recursive. It will call
                        #   a method of the same name on DriverTarget, which
                        #   will then call this method on all its equations,
                        #   until the top of the hierarchy has been reached.
                        input_property:DriverTarget = self.inputs[operation.url]
                        stack.append(input_property.get_value())

                # ------------------------------------------------------------ #
                # Multiply
                case FormulaOperator.MULT:
                    value1:Any = stack.pop()
                    value2:Any = stack.pop()
                    result:Any = value1 * value2
                    stack.append(result)

                # ------------------------------------------------------------ #
                # Spline (Linear)
                case FormulaOperator.SPL_LINEAR:

                    number_of_knots:int = int(stack.pop())
                    knots:list[Knot] = []

                    for _ in range(number_of_knots):

                        knot:Knot = Knot()
                        knot_list:list = stack.pop()

                        knot.x = knot_list[0]
                        knot.y = knot_list[1]

                        knots.append(knot)

                    value:Any = stack.pop()
                    result:Any = calculate_linear_spline(knots, value)
                    stack.append(result)

                # ------------------------------------------------------------ #
                # Spline (TCB)

                # The following JCMs use TCB spline interpolation:
                #   pJCMForeArmFwd_75_L
                #   pJCMThighFwd_57_L
                #   pJCMThighFwd_115_L
                #   pJCMShinBend_90_L
                #   pJCMShinBend_155_L

                # NOTE: Currently, this is an alias for linear interpolation.
                case FormulaOperator.SPL_TCB:

                    number_of_splines:int = int(stack.pop())
                    knots:list[TcbKnot] = []

                    for _ in range(number_of_splines):

                        knot:TcbKnot = TcbKnot()
                        knot_list:list = stack.pop()

                        knot.x=knot_list[0]
                        knot.y=knot_list[1]
                        knot.tension=knot_list[2]
                        knot.continuity=knot_list[3]
                        knot.bias=knot_list[4]

                        knots.append(knot)

                    value:Any = stack.pop()
                    result:Any = calculate_tcb_spline(knots, value)
                    stack.append(result)

                # ------------------------------------------------------------ #
                # Unknown
                case _:
                    raise NotImplementedError(operation.operator)

                # ------------------------------------------------------------ #

        if len(stack) != 1:
            raise RuntimeError

        return stack[0]

    # ======================================================================== #
