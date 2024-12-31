from typing import Self
from unittest import TestCase

from dufman.spline import calculate_linear_spline, Knot

class TestSplineModule(TestCase):

    def test_linear_spline(self:Self) -> None:

        # Test two knots
        knot1:Knot = Knot(0, 25)
        knot2:Knot = Knot(1, 50)

        self.assertAlmostEqual(calculate_linear_spline([knot1, knot2], 20.0), 0.0)
        self.assertAlmostEqual(calculate_linear_spline([knot1, knot2], 25.0), 0.0)
        self.assertAlmostEqual(calculate_linear_spline([knot1, knot2], 30.0), 0.2)
        self.assertAlmostEqual(calculate_linear_spline([knot1, knot2], 35.0), 0.4)
        self.assertAlmostEqual(calculate_linear_spline([knot1, knot2], 40.0), 0.6)
        self.assertAlmostEqual(calculate_linear_spline([knot1, knot2], 45.0), 0.8)
        self.assertAlmostEqual(calculate_linear_spline([knot1, knot2], 50.0), 1.0)
        self.assertAlmostEqual(calculate_linear_spline([knot1, knot2], 55.0), 1.0)

        # Test three knots
        knot3:Knot = Knot(2, 100)

        self.assertAlmostEqual(calculate_linear_spline([knot3, knot1, knot2], 20.0), 0.0)
        self.assertAlmostEqual(calculate_linear_spline([knot1, knot2, knot3], 55.0), 1.1)
        self.assertAlmostEqual(calculate_linear_spline([knot2, knot3, knot1], 60.0), 1.2)
        self.assertAlmostEqual(calculate_linear_spline([knot3, knot1, knot2], 65.0), 1.3)
        self.assertAlmostEqual(calculate_linear_spline([knot1, knot2, knot3], 70.0), 1.4)
        self.assertAlmostEqual(calculate_linear_spline([knot2, knot3, knot1], 75.0), 1.5)
        self.assertAlmostEqual(calculate_linear_spline([knot3, knot1, knot2], 80.0), 1.6)
        self.assertAlmostEqual(calculate_linear_spline([knot1, knot2, knot3], 85.0), 1.7)
        self.assertAlmostEqual(calculate_linear_spline([knot2, knot3, knot1], 90.0), 1.8)
        self.assertAlmostEqual(calculate_linear_spline([knot3, knot1, knot2], 95.0), 1.9)
        self.assertAlmostEqual(calculate_linear_spline([knot1, knot2, knot3],100.0), 2.0)
        self.assertAlmostEqual(calculate_linear_spline([knot2, knot3, knot1],105.0), 2.0)

        # Test negative knots
        knot1 = Knot(-10, 0)
        knot2 = Knot(-100, -1)

        print(calculate_linear_spline([knot1, knot2], -0.5))

        return
