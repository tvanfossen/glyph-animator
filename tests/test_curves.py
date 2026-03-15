"""Tests for bezier evaluation, derivative, and subdivision."""

import math

from glyph_animator.algorithms.curves import (
    eval_cubic,
    eval_cubic_derivative,
    lerp_point,
    subdivide_cubic,
)

# A known cubic: straight line from (0,0) to (100,100) with control points on the line.
LINE_SEG = ((0.0, 0.0), (33.33, 33.33), (66.67, 66.67), (100.0, 100.0))

# A curved segment (quarter circle approximation)
CURVE_SEG = ((0.0, 100.0), (55.0, 100.0), (100.0, 55.0), (100.0, 0.0))


class TestEvalCubic:
    def test_endpoints(self):
        """B(0) = C₀, B(1) = C₃ exactly."""
        assert eval_cubic(*LINE_SEG, 0.0) == (0.0, 0.0)
        assert eval_cubic(*LINE_SEG, 1.0) == (100.0, 100.0)

    def test_midpoint_on_line(self):
        """For a linear cubic, B(0.5) should be the midpoint."""
        x, y = eval_cubic(*LINE_SEG, 0.5)
        assert abs(x - 50.0) < 0.1
        assert abs(y - 50.0) < 0.1

    def test_curve_midpoint(self):
        """Curved segment midpoint should be above the diagonal."""
        x, y = eval_cubic(*CURVE_SEG, 0.5)
        # Quarter circle approx: midpoint is roughly (75, 75)
        assert x > 50
        assert y > 50


class TestEvalDerivative:
    def test_nonzero_on_curve(self):
        """Derivative should be nonzero at interior points."""
        dx, dy = eval_cubic_derivative(*CURVE_SEG, 0.5)
        speed = math.sqrt(dx * dx + dy * dy)
        assert speed > 0


class TestLerp:
    def test_endpoints(self):
        assert lerp_point((0.0, 0.0), (10.0, 20.0), 0.0) == (0.0, 0.0)
        assert lerp_point((0.0, 0.0), (10.0, 20.0), 1.0) == (10.0, 20.0)

    def test_midpoint(self):
        result = lerp_point((0.0, 0.0), (10.0, 20.0), 0.5)
        assert abs(result[0] - 5.0) < 1e-10
        assert abs(result[1] - 10.0) < 1e-10


class TestSubdivide:
    def test_split_preserves_endpoints(self):
        """Left starts at C₀, right ends at C₃."""
        left, right = subdivide_cubic(*CURVE_SEG, 0.5)
        assert left[0] == CURVE_SEG[0]
        assert right[3] == CURVE_SEG[3]

    def test_split_point_matches_evaluation(self):
        """The split point S should equal B(t)."""
        t = 0.3
        left, right = subdivide_cubic(*CURVE_SEG, t)
        split_pt = left[3]  # S is the end of left / start of right
        eval_pt = eval_cubic(*CURVE_SEG, t)
        assert abs(split_pt[0] - eval_pt[0]) < 1e-10
        assert abs(split_pt[1] - eval_pt[1]) < 1e-10

    def test_left_right_continuity(self):
        """End of left == start of right."""
        left, right = subdivide_cubic(*CURVE_SEG, 0.7)
        assert left[3] == right[0]

    def test_halves_reproduce_original(self):
        """Evaluate both halves and verify they trace the original curve."""
        t_split = 0.4
        left, right = subdivide_cubic(*CURVE_SEG, t_split)

        # Points on the left half (original t in [0, t_split])
        for i in range(11):
            u = i / 10.0
            orig_t = t_split * u
            orig_pt = eval_cubic(*CURVE_SEG, orig_t)
            left_pt = eval_cubic(*left, u)
            assert abs(orig_pt[0] - left_pt[0]) < 1e-8
            assert abs(orig_pt[1] - left_pt[1]) < 1e-8

        # Points on the right half (original t in [t_split, 1])
        for i in range(11):
            u = i / 10.0
            orig_t = t_split + (1 - t_split) * u
            orig_pt = eval_cubic(*CURVE_SEG, orig_t)
            right_pt = eval_cubic(*right, u)
            assert abs(orig_pt[0] - right_pt[0]) < 1e-8
            assert abs(orig_pt[1] - right_pt[1]) < 1e-8
