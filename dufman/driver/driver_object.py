# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""Defines child objects used internally by the DriverMap."""

# stdlib
from copy import copy
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
from dufman.url import DazUrl


# ============================================================================ #
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
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

    def __init__(self:Self, target_url:DazUrl) -> Self:

        # The name used to refer to this DriverTarget.
        self._target_url:DazUrl = copy(target_url)

        # The data this DriverTarget represents. Blank, until the asset data
        #   is set.
        self._asset_struct:Any = None
        self._channel_struct:DsonChannel = None
        self._raw_value = None

        # Linked lists representing other DriverTargets which can control this
        #   one.
        self._controllers:list[DriverEquation] = []
        self._subcomponents:list[DriverEquation] = []

        return


    # ------------------------------------------------------------------------ #

    def __str__(self:Self) -> str:
        return self.format_expression_name()


    # ------------------------------------------------------------------------ #

    def __repr__(self:Self) -> str:
        return f"DriverTarget(\"{ str(self) }\")"


    # ======================================================================== #
    # ASSET METHODS                                                            #
    # ======================================================================== #

    def get_asset(self:Self) -> Any:
        """Return the DsonModifier/DsonNode this DriverTarget targets."""
        return self._asset_struct


    # ------------------------------------------------------------------------ #

    def set_asset(self:Self, asset:Any) -> None:
        """Assign a DsonModifier/DsonNode this object should target."""

        if asset is None:
            raise TypeError

        if not isinstance(asset, DsonModifier) and not isinstance(asset, DsonNode):
            raise TypeError

        self._asset_struct = asset
        self._channel_struct = utils.get_channel_object(asset, self._target_url)
        self._raw_value = self._channel_struct.get_value()

        return


    # ======================================================================== #
    # VALUE METHODS                                                            #
    # ======================================================================== #

    def get_value(self:Self) -> Any:
        """Return the value of the asset/channel this object targets."""

        if not self.is_valid():
            # TODO: Proper logging
            # TODO: Correct return value?
            return 0

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
        """Set the value of the asset/channel this object targets."""

        if not self.is_valid():
            # TODO: Proper logging
            return

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
    # EXPRESSION STRINGS                                                       #
    # ======================================================================== #

    def get_asset_name(self:Self) -> str:
        """Return the name of the asset ID this object points to."""

        if self.get_library_type() in { LibraryType.MODIFIER, LibraryType.NODE }:
            return self._asset_struct.library_id

        return self._target_url.asset_id


    # ------------------------------------------------------------------------ #

    def get_channel_suffix(self:Self) -> str:
        """Return a sanitized version of the channel name for use in expressions."""

        if self.get_library_type() == LibraryType.MODIFIER:
            return "value"

        if self.get_library_type() == LibraryType.NODE:

            daz_channel_name:str = self._target_url.channel

            match daz_channel_name:

                # Rotation
                case "rotation/x":
                    return 'rot_x'
                case "rotation/y":
                    return 'rot_y'
                case "rotation/z":
                    return 'rot_z'

                # Unknown
                case _:
                    raise NotImplementedError(daz_channel_name)

        return "empty"


    # ------------------------------------------------------------------------ #

    def format_expression_name(self:Self) -> str:
        """Return a formatted name suitable for usage in an expression."""

        asset:str = self.get_asset_name()
        channel:str = self.get_channel_suffix()
        return f"{asset}_{channel}"


    # ======================================================================== #
    # BOOLEAN METHODS                                                          #
    # ======================================================================== #

    def has_morph(self:Self) -> bool:
        """Return True if this object points to a DsonModifier with valid morph data."""
        return (self.get_library_type() == LibraryType.MODIFIER) and (self._asset_struct.morph is not None)


    # ------------------------------------------------------------------------ #

    def is_driven_by_node(self:Self) -> bool:

        found_node:bool = False

        for controller in self._controllers:
            if controller.is_driven_by_node():
                found_node = True

        return found_node


    # ------------------------------------------------------------------------ #

    def is_rotation(self:Self) -> bool:
        """Return True if the target value should be converted to degrees/radians."""
        return self.get_channel_suffix() in { "rot_x", "rot_y", "rot_z" }


    # ------------------------------------------------------------------------ #

    def is_valid(self:Self) -> bool:
        """Return True if this object has a DsonModifier/DsonNode assigned."""
        return self._asset_struct is not None


    # ======================================================================== #
    # QUERY STATE INFORMATION                                                  #
    # ======================================================================== #

    def get_channel_type(self:Self) -> ChannelType:
        """Return the ChannelType of the asset this object targets."""
        if not self.is_valid():
            return None
        channel:DsonChannel = utils.get_channel_object(self._asset_struct, self._target_url)
        return channel.channel_type


    # ------------------------------------------------------------------------ #

    def get_library_type(self:Self) -> LibraryType:
        """Return the LibraryType of the asset this object targets."""

        if not self.is_valid():
            return None

        asset:Any = self._asset_struct

        if isinstance(asset, DsonModifier):
            return LibraryType.MODIFIER
        elif isinstance(asset, DsonNode):
            return LibraryType.NODE

        raise NotImplementedError(type(asset))


    # ------------------------------------------------------------------------ #

    def get_target_url(self:Self) -> DazUrl:
        """Return a DazUrl pointing to the asset this object targets."""
        return copy(self._target_url)


    # ======================================================================== #
    # PRIVATE VALUE GETTER METHODS                                             #
    # ======================================================================== #

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
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
# ============================================================================ #

class DriverEquation:
    """A class storing a formula used by one DriverTarget to control another.

    DriverEquation is a wrapper around a DsonFormula struct, storing the struct
    itself along with the contextual data necessary to refer to its parent and
    child DriverTargets so values can be computed as necessary.
    """


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
        output:str = self._output.format_expression_name()
        inputs:str = self.format_expression()
        return f"{output} = {inputs}"


    # ------------------------------------------------------------------------ #

    def __repr__(self:Self) -> str:
        return f"DriverEquation(\"{ str(self) }\")"


    # ======================================================================== #
    # BOOLEAN METHODS                                                          #
    # ======================================================================== #

    def is_driven_by_node(self:Self) -> bool:

        found_node:bool = False

        # Loop through all nodes/modifiers contributing to this equation.
        for input_target in self._inputs.values():

            asset_type:LibraryType = input_target.get_library_type()

            # If the asset struct is a node, set flag. If it's not, but it is
            #   indirectly driven, also set the flag.
            if asset_type == LibraryType.NODE:
                found_node = True
            else:
                if input_target.is_driven_by_node():
                    found_node = True

        return found_node


    # ======================================================================== #
    # PUBLIC QUERY METHODS                                                     #
    # ======================================================================== #

    def format_expression(self:Self) -> str:

        stack:list[Any] = []

        for operation in self._formula_struct.operations:
            match operation.operator:

                # ------------------------------------------------------------ #
                # Push
                case FormulaOperator.PUSH:
                    if operation.value is not None:
                        stack.append(str(operation.value))
                    elif operation.url is not None:
                        target:DriverTarget = self._inputs[operation.url]
                        stack.append(target.format_expression_name())

                # ------------------------------------------------------------ #
                # Add
                case FormulaOperator.ADD:
                    value2:str = str(stack.pop())
                    value1:str = str(stack.pop())
                    stack.append(f"({value1} + {value2})")

                # ------------------------------------------------------------ #
                # Subtract
                case FormulaOperator.SUB:
                    value2:str = str(stack.pop())
                    value1:str = str(stack.pop())
                    stack.append(f"({value1} - {value2})")

                # ------------------------------------------------------------ #
                # Multiply
                case FormulaOperator.MULT:
                    value2:str = str(stack.pop())
                    value1:str = str(stack.pop())
                    stack.append(f"({value1} * {value2})")

                # ------------------------------------------------------------ #
                # Divide
                case FormulaOperator.DIV:
                    value2:str = str(stack.pop())
                    value1:str = str(stack.pop())
                    stack.append(f"({value1} / {value2})")

                # ------------------------------------------------------------ #
                # Invert
                case FormulaOperator.INV:
                    value:str = str(stack.pop())
                    stack.append(f"(1.0 / {value})")

                # ------------------------------------------------------------ #
                # Negate
                case FormulaOperator.NEG:
                    value:str = str(stack.pop())
                    stack.append(f"({value} * -1.0)")

                # ------------------------------------------------------------ #
                # Unknown
                case _:
                    # NOTE: Future-proofing for expansion of the DSON format.
                    raise NotImplementedError(operation.operator)

        # Stack should have one element left on it, no more and no less.
        if len(stack) != 1:
            raise RuntimeError

        return stack[0]


    # ------------------------------------------------------------------------ #

    def get_stage(self:Self) -> FormulaStage:
        """Return if this equation should be added or multiplied to the result."""
        return self._formula_struct.stage


    # ------------------------------------------------------------------------ #

    def get_value(self:Self) -> Any:
        """Compute the equation this object represents and return the value."""

        stack:list[Any] = []

        for op in self._formula_struct.operations:
            match op.operator:

                # ------------------------------------------------------------ #
                # Push
                case FormulaOperator.PUSH:

                    if op.value:
                        stack.append(op.value)

                    # NOTE: This code is indirectly recursive. get_value() will
                    #   call the equivalent method on DriverTarget, which will
                    #   call this method on its controller equation.
                    elif op.url:
                        input_target:DriverTarget = self._inputs[op.url]
                        stack.append(input_target.get_value())

                # ------------------------------------------------------------ #
                # Add
                case FormulaOperator.ADD:
                    value2:Any = stack.pop()
                    value1:Any = stack.pop()
                    result:Any = value1 + value2
                    stack.append(result)

                # ------------------------------------------------------------ #
                # Subtract
                case FormulaOperator.SUB:
                    value2:Any = stack.pop()
                    value1:Any = stack.pop()
                    result:Any = value1 - value2
                    stack.append(result)

                # ------------------------------------------------------------ #
                # Multiply
                case FormulaOperator.MULT:
                    value2:Any = stack.pop()
                    value1:Any = stack.pop()
                    result:Any = value1 * value2
                    stack.append(result)

                # ------------------------------------------------------------ #
                # Divide
                case FormulaOperator.DIV:
                    value2:Any = stack.pop()
                    value1:Any = stack.pop()
                    result:Any = value1 / value2
                    stack.append(result)

                # ------------------------------------------------------------ #
                # Invert
                case FormulaOperator.INV:
                    value:Any = stack.pop()
                    result:Any = 1.0 / value
                    stack.append(result)

                # ------------------------------------------------------------ #
                # Negate
                case FormulaOperator.NEG:
                    value:Any = stack.pop()
                    result:Any = value * -1.0
                    stack.append(result)

                # ------------------------------------------------------------ #
                # Spline (Linear)
                case FormulaOperator.SPL_LINEAR:

                    knot_count:int = int(stack.pop())
                    knots:list[Knot] = []

                    for _ in range(knot_count):

                        knot:Knot = Knot()
                        knot_data:list[Any] = stack.pop()

                        knot.x = knot_data[1]
                        knot.y = knot_data[0]

                        knots.append(knot)

                    value:Any = stack.pop()
                    result:Any = calculate_linear_spline(knots, value)
                    stack.append(result)

                # ------------------------------------------------------------ #
                # Spline (TCB)
                case FormulaOperator.SPL_TCB:

                    knot_count:int = int(stack.pop())
                    knots:list[TcbKnot] = []

                    for _ in range(knot_count):

                        knot:TcbKnot = TcbKnot()
                        knot_data:list[Any] = stack.pop()

                        knot.x = knot_data[1]
                        knot.y = knot_data[0]
                        knot.tension = knot_data[2]
                        knot.continuity = knot_data[3]
                        knot.bias = knot_data[4]

                        knots.append(knot)

                    value:Any = stack.pop()
                    result:Any = calculate_tcb_spline(knots, value)
                    stack.append(result)

                # ------------------------------------------------------------ #
                # Unknown
                case _:
                    # NOTE: Future-proofing for additions to the DSON format.
                    raise NotImplementedError(op.operator)

        if len(stack) != 1:
            raise RuntimeError

        return stack[0]
