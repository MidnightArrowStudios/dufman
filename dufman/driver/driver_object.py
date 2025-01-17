# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""Defines child objects used internally by the DriverMap."""

# stdlib
from typing import Any, Self

# dufman
from dufman.driver import utils
from dufman.enums import (
    ChannelType,
    FormulaOperator,
    FormulaStage,
    LibraryType,
)
from dufman.structs.channel import (
    DsonChannel,
    DsonChannelFloat,
    #DsonChannelInt,
)
from dufman.spline import (
    calculate_linear_spline,
    calculate_tcb_spline,
    Knot,
    TcbKnot,
)
from dufman.structs.formula import DsonFormula
from dufman.structs.modifier import DsonModifier
from dufman.structs.node import DsonNode
from dufman.url import AssetAddress


# ============================================================================ #
# Driver Target                                                                #
# ============================================================================ #

class DriverTarget:
    """A class representing a value which can be controlled by another value.
    
    DriverTarget is a wrapper around a DsonModifier/DsonNode struct and its
    data channel. Data channels can control each other, resulting in a chain
    of DriverTargets stored as a doubly-linked list. When the value of a 
    channel is requested, the DriverTarget will travel up the chain and
    compute the value of all its parent DriverTargets.

    If an asset could not be loaded from disk, this becomes a dummy object
    which stores its contextual relationships so that the asset's struct can be
    inserted later, if necessary.
    """


    # ======================================================================== #
    # DUNDER METHODS                                                           #
    # ------------------------------------------------------------------------ #

    def __init__(self:Self, target_url:str) -> Self:

        # The name used to refer to this DriverTarget.
        self._target_url:str = target_url

        # The data this DriverTarget represents. Blank, until the asset data
        #   is set.
        self._asset_struct:Any = None
        self._channel_struct:DsonChannel = None
        self._library_type:LibraryType = None
        self._raw_value = None

        # Linked lists representing other DriverTargets which can control this
        #   one.
        self._controllers:list[DriverEquation] = []
        self._subcomponents:list[DriverEquation] = []

        return


    # ------------------------------------------------------------------------ #

    def __str__(self:Self) -> str:
        return str(self._target_url)


    # ------------------------------------------------------------------------ #

    def __repr__(self:Self) -> str:
        return f"DriverTarget({ str(self) })"


    # ======================================================================== #
    # PUBLIC QUERY METHODS                                                     #
    # ------------------------------------------------------------------------ #

    def get_channel_type(self:Self) -> ChannelType:
        if not self.is_valid():
            return None
        channel:DsonChannel = utils.get_channel_object(self._asset_struct, self._target_url)
        return channel.channel_type


    # ------------------------------------------------------------------------ #

    def get_library_type(self:Self) -> LibraryType:
        return self._library_type


    # ------------------------------------------------------------------------ #

    def has_morph(self:Self) -> bool:
        return (self._library_type == LibraryType.MODIFIER) and (self._asset_struct.morph is not None)


    # ------------------------------------------------------------------------ #

    def is_valid(self:Self) -> bool:
        return self._asset_struct is not None


    # ======================================================================== #
    # PUBLIC ASSET METHODS                                                     #
    # ------------------------------------------------------------------------ #

    def get_asset(self:Self) -> tuple[Any, LibraryType]:
        return (self._asset_struct, self._library_type)


    # ------------------------------------------------------------------------ #

    def set_asset(self:Self, asset:Any, library_type:LibraryType) -> None:

        if asset is None:
            raise TypeError

        if not isinstance(asset, DsonModifier) and not isinstance(asset, DsonNode):
            raise TypeError

        self._asset_struct = asset
        self._channel_struct = utils.get_channel_object(asset, self._target_url)
        self._library_type = library_type
        self._raw_value = self._channel_struct.get_value()

        return


    # ======================================================================== #
    # PUBLIC VALUE METHODS                                                     #
    # ------------------------------------------------------------------------ #

    def get_value(self:Self) -> Any:

        if not self.is_valid():
            raise RuntimeError

        channel_type:ChannelType = self.get_channel_type()
        match channel_type:
            case ChannelType.BOOL:
                return self._get_bool_value()
            case ChannelType.FLOAT:
                return self._get_float_value()
            case ChannelType.INT:
                return self._get_int_value()
            case _:
                raise NotImplementedError(channel_type)


    # ------------------------------------------------------------------------ #

    def set_value(self:Self, new_value:Any) -> None:

        if not self.is_valid():
            raise RuntimeError

        channel_type:ChannelType = self.get_channel_type()
        match channel_type:
            case ChannelType.BOOL:
                self._raw_value = bool(new_value)
            case ChannelType.FLOAT:
                self._raw_value = float(new_value)
            case ChannelType.INT:
                self._raw_value = int(new_value)
            case _:
                raise NotImplementedError(channel_type)


    # ======================================================================== #
    #                                                                          #
    # ------------------------------------------------------------------------ #

    def _get_bool_value(self:Self) -> bool:
        # TODO: Experiment with how adding and multiplying a bool works in Daz
        return bool(self._raw_value)


    # ------------------------------------------------------------------------ #

    def _get_float_value(self:Self) -> float:

        # Sort DriverEquations by stage
        summed, multiplied = self._sort_by_stage()

        # Value we will be working with
        result:float = float(self._raw_value)

        # FormulaStage.SUM
        for equation in summed:
            result += float(equation.get_value())

        # FormulaStage.MULTIPLY
        multiply:float = 1.0
        for equation in multiplied:
            multiply *= float(equation.get_value())
        result *= multiply

        # For convenience
        channel:DsonChannelFloat = self._channel_struct

        # Clamp value
        if channel.clamp_values:
            result = max(channel.minimum_value, min(result, channel.maximum_value))

        return result


    # ------------------------------------------------------------------------ #

    def _get_int_value(self:Self) -> int:

        # Sort DriverEquations by stage
        summed, multiplied = self._sort_by_stage()

        # Value we will be working with
        result:int = int(self._raw_value)

        # FormulaStage.SUM
        for equation in summed:
            result += equation.get_value()

        # FormulaStage.MULTIPLY
        # TODO: Should multiplication be int or float?
        multiply:float = 1.0
        for equation in multiplied:
            multiply *= equation.get_value()
        result *= int(multiply)

        # For convenience
        # FIXME: Implement DsonChannelInt struct
        #channel:DsonChannelInt = self._channel_struct
        channel = self._channel_struct

        # Clamp value
        if channel.clamp_values:
            result = max(channel.minimum_value, min(result, channel.maximum_value))

        return result


    # ======================================================================== #
    #                                                                          #
    # ------------------------------------------------------------------------ #

    def _sort_by_stage(self:Self) -> tuple[list, list]:

        summed:list[DriverEquation] = []
        multiplied:list[DriverEquation] = []

        for controller in self._controllers:
            stage:FormulaStage = controller.get_stage()
            match stage:
                case FormulaStage.SUM:
                    summed.append(controller)
                case FormulaStage.MULTIPLY:
                    multiplied.append(controller)
                case _:
                    raise NotImplementedError(stage)

        return (summed, multiplied)


# ============================================================================ #
# Driver Equation                                                              #
# ============================================================================ #

class DriverEquation:
    """A class storing a formula used by one DriverTarget to control another.

    DriverEquation is a wrapper around a DsonFormula struct, storing the struct
    itself along with the contextual data necessary to refer to its parent and
    child DriverTargets so values can be computed as necessary.
    """

    # ======================================================================== #
    #                                                                          #
    # ------------------------------------------------------------------------ #

    def __init__(self:Self, struct:DsonFormula) -> Self:

        # Type safety
        if not struct or not isinstance(struct, DsonFormula):
            raise TypeError

        # The data this object is a wrapper for
        self._formula_struct:DsonFormula = struct

        # Linked lists
        self._inputs:dict = {}
        self._output:DriverTarget = None

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

        for operation in self._formula_struct.operations:
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
                        knot.x = data[1]
                        knot.y = data[0]
                        knots.append(knot)

                    _value:Any = stack.pop()
                    stack.append("IMPLEMENT SPLINE PRINTING")

                case _:
                    raise NotImplementedError(operation.operator)

        output:str = self._strip_url(self._formula_struct.output)
        return f"{output} = {stack[0]}"


    # ------------------------------------------------------------------------ #

    def get_stage(self:Self) -> FormulaStage:
        """Return the FormulaStage of the underlying DsonFormula struct."""
        return self._formula_struct.stage


    # ------------------------------------------------------------------------ #

    def get_value(self:Self) -> Any:
        """Return the final value of the equation.
        
        This is equivalent to calculating the "output" property of a DsonFormula
        struct.
        """

        stack:list[Any] = []

        for operation in self._formula_struct.operations:
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
                        input_property:DriverTarget = self._inputs[operation.url]
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

                        knot.x = knot_list[1]
                        knot.y = knot_list[0]

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

                        knot.x=knot_list[1]
                        knot.y=knot_list[0]
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
