# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

# stblib
from dataclasses import dataclass

# TODO: Which axis should drivers go on? X or Y? See which would be more
#   convenient for Blender.

# ============================================================================ #
# Knot Objects                                                                 #
# ============================================================================ #

# NOTE: If value is a bone rotation, X should be the morph strength and
#   Y should be the bone value. If value is a slider, then X should be
#   the bone rotation and Y should be the slider value.

@dataclass
class Knot:
    x:float = 0.0
    y:float = 0.0


# ---------------------------------------------------------------------------- #

class TcbKnot(Knot):
    tension:float = 0.0
    continuity:float = 0.0
    bias:float = 0.0


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def _get_knots(knots:list[Knot], value:float) -> tuple[Knot, Knot]:
    """Utility function to retrieve the two knots a value lies between."""

    # Sort knots so their bone rotations are in numerical order.
    knots = sorted(knots, key=lambda knot: knot.y)

    # If there is only one knot, the object stays at that position no matter
    #   what.
    if len(knots) == 1:
        return (knots[0], knots[0])

    # Clamp value to minimum knot.
    if value < knots[0].y:
        return (knots[0], knots[0])

    # Clamp value to maximum knot.
    if value > knots[-1].y:
        return (knots[-1], knots[-1])

    # Return values.
    knot1:Knot = None
    knot2:Knot = None

    # Determine which two knots the value lies between.
    for i in range(len(knots) - 1):
        if knots[i].y <= value <= knots[i+1].y:
            knot1 = knots[i]
            knot2 = knots[i+1]

    return (knot1, knot2)


# ============================================================================ #
#                                                                              #
# ============================================================================ #

def calculate_linear_spline(knots:list[Knot], value:float) -> float:

    # Sort knots so that Y (i.e. bone rotation) is in numerical order.
    knot1, knot2 = _get_knots(knots, value)

    # NOTE: In Daz Studio, the property hierarchy literally will not allow two
    #   keys to be created with the same value. So unless somebody is coding a
    #   DSON file by hand, two knots should never have the same Y value.

    # Scale value into the 0.0 - 1.0 range.
    try:
        normalized:float = (value - knot1.y) / (knot2.y - knot1.y)
    except ZeroDivisionError:
        # If Y values are identical, then do a simple halfway blend between
        #   the knots.
        normalized:float = 0.5

    # Use value to lerp between strength of knots.
    return knot1.x + (knot2.x - knot1.x) * normalized


# ---------------------------------------------------------------------------- #

def calculate_tcb_spline(knots:list[TcbKnot], value:float) -> float:
    # TODO: Implement a real TCB spline function.
    return calculate_linear_spline(knots, value)
