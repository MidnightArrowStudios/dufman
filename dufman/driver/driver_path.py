# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

# stdlib
from math import degrees, isclose
from typing import Any, NamedTuple, Self

# dufman
from dufman.driver.driver_object import DriverEquation, DriverTarget
from dufman.enums import FormulaOperator, FormulaStage, LibraryType


# ============================================================================ #
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
# ============================================================================ #

class PathSegment(NamedTuple):
    """NamedTuple used to compactly store an equation and one of its inputs.
    
    A DriverEquation can have multiple inputs, but only one output. It is
    trivial to go down to its singular output, but more complicated to figure
    out which input a DriverPath is using. This tuple removes the ambiguity by
    storing a reference to the exact input.
    """
    equation:DriverEquation
    target:DriverTarget


# ============================================================================ #
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
# ============================================================================ #

class DriverPath:
    """Class which represents the relationship between different DriverTargets.
    
    For instance, if "pJCMCorrective" is driven by "bone?rotation/x" and dialed
    in with "CTRLCharacter", then [ pJCMCorrective, bone/rotation/x ] and 
    [ pJCMCorrective, CTRLCharacter ] will be two separate DriverPath objects.
    Each DriverPath stores a different part of the mathematical equation used 
    to derive the final value of a particular DriverTarget.
    """

    def __init__(self:Self, segments:list[PathSegment]) -> Self:

        # List type safety
        if not segments or not isinstance(segments, list):
            raise TypeError

        # List contents type safety
        if not all(isinstance(segment, PathSegment) for segment in segments):
            raise ValueError

        self._path_segments = list(segments)

        return


    # ------------------------------------------------------------------------ #

    def __str__(self:Self) -> str:
        return self._path_segments[0].target.get_target_name()


    # ------------------------------------------------------------------------ #

    def __repr__(self:Self) -> str:
        return f"DriverPath(\"{ str(self) }\")"


    # ======================================================================== #
    #                                                                          #
    # ======================================================================== #

    def get_blender_expression(self:Self) -> str:

        # TODO: Need to rewrite this so sum and multiply stages are separate.

        stack:Any = []

        for segment in self._path_segments:
            for operation in segment.equation._formula_struct.operations:

                match operation.operator:

                    # Push
                    case FormulaOperator.PUSH:

                        # TODO: Need to inspect the node type, both to avoid
                        #   name clashes by including "_rot_x", etc. and to
                        #   check if we should multiply value by degrees.
                        if operation.url:
                            value:str = segment.target.get_target_name()
                            stack.append(value)
                        elif operation.value:
                            value:str = str(degrees(operation.value))
                            stack.append(value)

                    # Multiply
                    case FormulaOperator.MULT:
                        value2:str = stack.pop()
                        value1:str = stack.pop()
                        result:str = f"({value1} * {value2})"
                        stack.append(result)

                    # Unknown
                    case _:
                        raise NotImplementedError(operation.operator)

        if len(stack) > 1:
            raise RuntimeError

        return stack[0]


    # ------------------------------------------------------------------------ #

    def get_equation_stage(self:Self) -> FormulaStage:
        """Get the FormulaStage determining how this path influences the target."""
        return self._path_segments[0].equation.get_stage()


    # ------------------------------------------------------------------------ #

    def get_equation_value(self:Self) -> Any:
        """Compute the current value influencing this target."""
        return self._path_segments[0].equation.get_value()


    # ------------------------------------------------------------------------ #

    def get_target_urls(self:Self) -> list[str]:
        return [ segment.target.get_target_url() for segment in self._path_segments ]


    # ------------------------------------------------------------------------ #

    def is_driven_by_node(self:Self) -> bool:
        """Check if there is a node in this path."""

        has_node:bool = False
        for segment in self._path_segments:
            if segment.target.get_library_type() == LibraryType.NODE:
                has_node = True

        return has_node


    # ------------------------------------------------------------------------ #

    def is_strength_zero(self:Self) -> bool:
        """Check if the target's value will be nullified by this path."""

        is_node_driven:bool = self.is_driven_by_node()
        is_multiplied:bool = self.get_equation_stage() == FormulaStage.MULTIPLY
        is_zeroed:bool = False

        value:Any = self.get_equation_value()
        if not value or isclose(value, 0.0):
            is_zeroed = True

        return (not is_node_driven and is_multiplied and is_zeroed)


    # ------------------------------------------------------------------------ #

    def is_useful_for_jcm(self:Self) -> bool:
        """Verify this path has a meaningful influence on the target."""

        # Standalone shaping morphs will return None, so we know it can't be a
        #   JCM if the stage is None.
        stage:FormulaStage = self.get_equation_stage()
        if stage is None:
            return False

        # Again, if the value is None we know it cannot be a JCM.
        # NOTE: Sanity check must be "if value is None:" since "if not value:" 
        #   will return false positives when value is 0.0.
        value:Any = self.get_equation_value()
        if value is None:
            return False

        # There is a node somewhere in this DriverPath.
        is_node_driven:bool = self.is_driven_by_node()
        if is_node_driven:
            return True

        # DriverPath is an identity value which will make the target equal to
        #   itself, so it can be culled.
        # TODO: Should this have a MULTIPLY check? The original implementation
        #   didn't, but I don't remember if that was an oversight that happened
        #   to work correctly or a workaround for an actual problem.
        if stage == FormulaStage.MULTIPLY and isclose(value, 1.0):
            return False

        # DriverPath will have no effect on the target's value, so it can be
        #   culled.
        if stage == FormulaStage.SUM and isclose(0.0):
            return False

        # DriverPath does not have a node, but it does influence the strength
        #   of the node-driven values.
        return True


# ============================================================================ #
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
# ============================================================================ #

def _build_controller_path(result:list[DriverPath], working_path:list[PathSegment], target:DriverTarget) -> None:

    # TODO: Should we check for type (i.e. LibraryType.NODE) here or get the
    #   whole path and do the type-checking in the calling function?

    # If there's nothing controlling this target, we've reached the top of
    #   the hierarchy.
    if not target._controllers:
        result.append(DriverPath(working_path))
        return

    # Loop through all equations driving this one, create a new segment
    #   (DriverEquation + DriverTarget), and recursively pass it into this
    #   function.
    for equation in target._controllers:
        for input_target in equation._inputs.values():
            segment:PathSegment = PathSegment(equation, input_target)
            working_path.append(segment)
            _build_controller_path(result, list(working_path), input_target)

    return


# ============================================================================ #

def get_jcm_paths_for_target(target:DriverTarget) -> list[DriverPath]:

    # Get all target's DriverPaths (regardless of whether they're JCMs).
    paths:list[DriverPath] = []
    _build_controller_path(paths, [], target)

    # If none of the DriverPaths have a node, it can't be a JCM.
    has_node:bool = False
    for path in paths:
        if path.is_driven_by_node():
            has_node = True
    if not has_node:
        return []

    # If any of the DriverPaths have a multiply stage of 0.0, we can skip it
    #   since it won't have any effect.
    for path in paths:
        if path.is_strength_zero():
            return []

    # Return paths, but cull those which won't have an effect.
    return [ path for path in paths if path.is_useful_for_jcm() ]
