# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

"""Defines a struct which encapsulates DSON's "formula" datatype.

http://docs.daz3d.com/doku.php/public/dson_spec/object_definitions/formula/start
"""

# stdlib
from dataclasses import dataclass
from typing import Any, Self

# dufman
from dufman.enums import FormulaOperator, FormulaStage


# ============================================================================ #
# DsonOperation struct                                                         #
# ============================================================================ #

@dataclass
class DsonOperation:

    operator        : FormulaOperator       = None
    url             : str                   = None
    value           : Any                   = None


# ============================================================================ #
# DsonFormula struct                                                           #
# ============================================================================ #

@dataclass
class DsonFormula:

    output          : str                   = None
    operations      : list[DsonOperation]   = None
    stage           : FormulaStage          = FormulaStage.SUM


    # ======================================================================== #

    @staticmethod
    def load_from_dson(formula_array:list[dict]) -> list[Self]:
        """Factory method for creating an array of DsonFormula objects."""

        if not formula_array:
            return None

        if not isinstance(formula_array, list):
            raise TypeError("\"formulas\" property is not a list")

        if not all(isinstance(item, dict) for item in formula_array):
            raise ValueError("\"formulas\" property contains a non-dictionary item")

        all_structs:list[Self] = []

        for formula_dson in formula_array:

            formula:Self = DsonFormula()

            # ---------------------------------------------------------------- #

            # Output
            if "output" in formula_dson:
                formula.output = formula_dson["output"]
            else:
                raise ValueError("Missing required property \"output\"")

            # Stage
            if "stage" in formula_dson:

                stage_string:str = formula_dson["stage"]

                # DSON specs dictate this is spelled "multiply", but official
                #   Daz files also abbreviate it, so we need to check.
                # "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf#lThigh"
                if stage_string == "mult":
                    stage_string = "multiply"

                formula.stage = FormulaStage(stage_string)

            # Operations
            if not "operations" in formula_dson:
                raise ValueError("Missing required property \"operations\"")

            formula.operations = []

            for op_dson in formula_dson["operations"]:

                operation:DsonOperation = DsonOperation()
                formula.operations.append(operation)

                # Operator
                if "op" in op_dson:
                    operation.operator = FormulaOperator(op_dson["op"])
                else:
                    raise ValueError("Missing required property \"op\"")

                # URL
                if "url" in op_dson:
                    operation.url = op_dson["url"]

                # Value
                if "val" in op_dson:
                    operation.value = op_dson["val"]

            # ---------------------------------------------------------------- #

            all_structs.append(formula)

        return all_structs
