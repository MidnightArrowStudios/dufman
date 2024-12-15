# ============================================================================ #
# Copyright (c) 2024, Midnight Arrow.
# https://github.com/MidnightArrowStudios/dufman
# Licensed under the MIT license.
# ============================================================================ #
"""Unit testing functions for DUFMan formulas."""

from __future__ import annotations

from dufman.datatypes.formula_map import FormulaMap

from .test_directory import TestDirectory

class TestFormula(TestDirectory):

    def test_formula(self:TestFormula) -> None:

        url_string:str = "/data/DAZ%203D/Genesis%208/Female/Morphs/DAZ%203D/Body/FBMHeight.dsf#FBMHeight"
        formula_map:FormulaMap = FormulaMap("Genesis8Female", url_string)

        self.assertIsNotNone(formula_map)

        return
