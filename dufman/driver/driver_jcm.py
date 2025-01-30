# stdlib
from math import isclose
from typing import Any

# dufman
from dufman.enums import FormulaOperator, FormulaStage, LibraryType
from dufman.driver.driver_object import DriverTarget, DriverEquation
from dufman.spline import Knot


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def _parse_variable(variable:Any, nodes:list[DriverTarget]) -> str:

    if isinstance(variable, DriverTarget):
        return _parse_target(variable, nodes)

    # -------------------------------------------------------------------- #
    if isinstance(variable, str):
        return variable

    # -------------------------------------------------------------------- #
    if isinstance(variable, int|float):
        return str(variable)

    # -------------------------------------------------------------------- #
    if isinstance(variable, bool):
        return str(bool(variable))

    return


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def _parse_target(target:DriverEquation, nodes:list[DriverTarget]) -> str:

    asset_type:LibraryType = target.get_library_type()

    # ------------------------------------------------------------------------ #
    if asset_type == LibraryType.NODE:
        if not target in nodes:
            nodes.append(target)
        expression:str = target.format_expression_name()
        if target.is_rotation():
            expression = f"degrees({expression})"
        return expression

    # ------------------------------------------------------------------------ #
    if asset_type == LibraryType.MODIFIER:

        summed:list[DriverEquation] = []
        multiplied:list[DriverEquation] = []

        # -------------------------------------------------------------------- #
        # Sort by FormulaStage

        for equation in target._controllers:
            stage:FormulaStage = equation.get_stage()
            if stage == FormulaStage.SUM:
                summed.append(equation)
            elif stage == FormulaStage.MULTIPLY:
                multiplied.append(equation)
            else:
                # NOTE: Future-proofing
                raise NotImplementedError(stage)

        # -------------------------------------------------------------------- #
        # FormulaStage.SUM

        sum_expression:str = ""

        for equation in summed:

            # If DriverEquation has a node somewhere in its hierarchy, then we
            #   recursively traverse the hierarchy until we find it. If there
            #   is no node, then "bake" the value into the equation.
            if equation.is_driven_by_node():
                expression:str = _parse_equation(equation, nodes)
            else:
                value:Any = equation.get_value()
                expression:str = str(float(value))

            if sum_expression == "":
                sum_expression = expression
            else:
                sum_expression += f" + {expression}"

        if len(summed) > 1:
            sum_expression = f"({sum_expression})"

        # -------------------------------------------------------------------- #
        # FormulaStage.MULTIPLY

        mult_expression:str = ""

        for equation in multiplied:

            # If DriverEquation has a node somewhere in its hierarchy, then we
            #   recursively traverse the hierarchy until we find it. If there
            #   is no node, then "bake" the value into the equation.
            if equation.is_driven_by_node():
                expression:str = _parse_equation(equation, nodes)
            else:
                value:Any = equation.get_value()
                if isclose(value, 1.0):
                    # This value will have no effect, so it can be culled.
                    continue
                expression:str = str(float(value))

            if sum_expression == "" and mult_expression == "":
                mult_expression = expression
            else:
                mult_expression += f" * {expression}"

        # -------------------------------------------------------------------- #

        if mult_expression != "":
            return f"({sum_expression}{mult_expression})"
        else:
            return sum_expression


    # ------------------------------------------------------------------------ #

    # TODO: Should this fail with an exception, or should we skip and continue
    #   loading?
    raise RuntimeError


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def _parse_equation(equation:DriverEquation, nodes:list[DriverTarget]) -> str:

    stack:list[Any] = []

    for operation in equation._formula_struct.operations:
        match operation.operator:

            # ---------------------------------------------------------------- #
            # Push
            case FormulaOperator.PUSH:
                if operation.value is not None:
                    stack.append(operation.value)
                elif operation.url is not None:
                    stack.append(equation._inputs[operation.url])

            # ---------------------------------------------------------------- #
            # Add
            case FormulaOperator.ADD:
                value2:str = _parse_variable(stack.pop(), nodes)
                value1:str = _parse_variable(stack.pop(), nodes)
                result:str = f"({value1} + {value2})"
                stack.append(result)

            # ---------------------------------------------------------------- #
            # Subtract
            case FormulaOperator.SUB:
                value2:str = _parse_variable(stack.pop(), nodes)
                value1:str = _parse_variable(stack.pop(), nodes)
                result:str = f"({value1} - {value2})"
                stack.append(result)

            # ---------------------------------------------------------------- #
            # Multiply
            case FormulaOperator.MULT:
                value2:str = _parse_variable(stack.pop(), nodes)
                value1:str = _parse_variable(stack.pop(), nodes)
                result:str = f"({value1} * {value2})"
                stack.append(result)

            # ---------------------------------------------------------------- #
            # Divide
            case FormulaOperator.DIV:
                value2:str = _parse_variable(stack.pop(), nodes)
                value1:str = _parse_variable(stack.pop(), nodes)
                result:str = f"({value1} / {value2})"
                stack.append(result)

            # ---------------------------------------------------------------- #
            # Invert
            case FormulaOperator.INV:
                value:str = _parse_variable(stack.pop(), nodes)
                result:str = f"(1.0 / {value})"
                stack.append(result)

            # ---------------------------------------------------------------- #
            # Negate
            case FormulaOperator.NEG:
                value:str = _parse_variable(stack.pop(), nodes)
                result:str = f"(-1.0 * {value})"
                stack.append(result)

            # ---------------------------------------------------------------- #
            # Spline
            case FormulaOperator.SPL_LINEAR | FormulaOperator.SPL_TCB:

                # TODO: Handle actual TCB interpolation.

                knot_count:int = int(stack.pop())
                all_knots:list[Knot] = []

                for _ in range(knot_count):

                    knot:Knot = Knot()
                    data:list[float] = stack.pop()

                    knot.x = data[1]
                    knot.y = data[0]

                    all_knots.append(knot)

                # Value used as "t" for lerping.
                value:Any = _parse_variable(stack.pop(), nodes)

                if knot_count == 1:
                    # TODO: How does Daz Studio handle a single knot?
                    raise NotImplementedError

                elif knot_count == 2:
                    k1:Knot = all_knots[0]
                    k2:Knot = all_knots[1]

                    result:str = f"lerp({k1.x}, {k2.x}, clamp(({value} - {k1.y}) / ({k2.y} - {k1.y})))"
                    stack.append(result)

                else:
                    # TODO: Figure out how to handle an arbitrary number of knots.
                    raise NotImplementedError

            # ---------------------------------------------------------------- #
            # Unknown
            case _:
                # NOTE: Future-proofing for expansion of the DSON format.
                raise NotImplementedError(operation.operator)

    # Stack should have one element left on it, no more and no less.
    if len(stack) != 1:
        raise RuntimeError

    return _parse_variable(stack[0], nodes)


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def create_jcm_expression(target:DriverTarget) -> tuple[str, list[DriverTarget]]:

    # Target cannot be a JCM if it has no morph or controlling equations.
    if not target.has_morph() or len(target._controllers) == 0:
        return (None, None)

    # ------------------------------------------------------------------------ #
    # Check if morph is driven by a node.

    found_node:bool = False

    for controller in target._controllers:
        if controller.is_driven_by_node():
            found_node = True
            break

    if not found_node:
        return (None, None)

    # ------------------------------------------------------------------------ #
    # Separate equations by stage

    summed:list[DriverEquation] = []
    multiplied:list[DriverEquation] = []

    for equation in target._controllers:
        stage:FormulaStage = equation.get_stage()
        match stage:
            case FormulaStage.SUM:
                summed.append(equation)
            case FormulaStage.MULTIPLY:
                multiplied.append(equation)
            case _:
                # NOTE: Future-proofing
                raise NotImplementedError(stage)

    # ------------------------------------------------------------------------ #
    # Check if morph is nullified by a zeroed multiply stage.

    for equation in multiplied:
        if equation.is_driven_by_node():
            continue

        value:Any = equation.get_value()

        # Sanity check must be "value is None". Using "not value" will result
        #   in false positives if value is 0.0.
        if value is None or isclose(value, 0.0):
            return (None, None)

    # ------------------------------------------------------------------------ #

    nodes:list[DriverTarget] = []
    expression:str = _parse_target(target, nodes)

    return (expression, nodes)
