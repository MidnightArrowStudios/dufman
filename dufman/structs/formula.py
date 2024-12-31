# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #

from dataclasses import dataclass
from typing import Any, Self

from dufman.enums import FormulaOperator, FormulaStage


@dataclass
class DsonOperation:

    operator        : FormulaOperator       = None
    url             : str                   = None
    value           : Any                   = None


@dataclass
class DsonFormula:

    output          : str                   = None
    operations      : list[DsonOperation]   = None
    stage           : FormulaStage          = FormulaStage.SUM


    @staticmethod
    def load(formula_array:list[dict]) -> list[Self]:
        """Factory method for creating an array of DsonFormula objects."""

        if not isinstance(formula_array, list):
            raise TypeError("\"formulas\" property is not a list")

        if not all(isinstance(item, dict) for item in formula_array):
            raise ValueError("\"formulas\" property contains a non-dictionary item")

        all_structs:list[Self] = []

        for formula_json in formula_array:

            formula:Self = DsonFormula()
            all_structs.append(formula)

            # Output
            if "output" in formula_json:
                formula.output = formula_json["output"]
            else:
                raise ValueError("Missing required property \"output\"")

            # Stage
            if "stage" in formula_json:

                stage_string:str = formula_json["stage"]

                # DSON specs dictate this is spelled "multiply", but official
                #   Daz files also abbreviate it, so we need to check.
                # "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf#lThigh"
                if stage_string == "mult":
                    stage_string = "multiply"

                formula.stage = FormulaStage(stage_string)

            # Operations
            if not "operations" in formula_json:
                raise ValueError("Missing required property \"operations\"")

            formula.operations = []

            for op_json in formula_json["operations"]:

                operation:DsonOperation = DsonOperation()
                formula.operations.append(operation)

                # Operator
                if "op" in op_json:
                    operation.operator = FormulaOperator(op_json["op"])
                else:
                    raise ValueError("Missing required property \"op\"")

                # URL
                if "url" in op_json:
                    operation.url = op_json["url"]

                # Value
                if "val" in op_json:
                    operation.value = op_json["val"]

        return all_structs
