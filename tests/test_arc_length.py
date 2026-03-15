"""Tests for arc-length computation and Newton inverse."""

import math

from glyph_animator.algorithms.arc_length import (
    arc_length_inverse,
    contour_arc_lengths,
    segment_arc_length,
)

# Straight line from (0,0) to (100,0) as a degenerate cubic
LINE = ((0.0, 0.0), (33.33, 0.0), (66.67, 0.0), (100.0, 0.0))

# Quarter circle approximation
QUARTER = ((0.0, 100.0), (55.0, 100.0), (100.0, 55.0), (100.0, 0.0))


class TestSegmentArcLength:
    def test_straight_line(self):
        """Arc length of a straight line should equal Euclidean distance."""
        length = segment_arc_length(*LINE)
        assert abs(length - 100.0) < 0.1

    def test_quarter_circle(self):
        """Quarter circle (r=100) arc length ≈ π/2 * 100 ≈ 157.08."""
        length = segment_arc_length(*QUARTER)
        expected = math.pi / 2 * 100
        # Bezier approximation of circle is close but not exact
        assert abs(length - expected) < 5.0

    def test_partial_range(self):
        """Arc length of [0, 0.5] should be roughly half of [0, 1]."""
        full = segment_arc_length(*QUARTER)
        half = segment_arc_length(*QUARTER, t_start=0.0, t_end=0.5)
        assert half < full
        assert half > 0

    def test_zero_range(self):
        """Arc length of [t, t] should be ~0."""
        length = segment_arc_length(*LINE, t_start=0.5, t_end=0.5)
        assert abs(length) < 1e-10


class TestArcLengthInverse:
    def test_endpoints(self):
        """target=0 → t=0, target=total → t=1."""
        total = segment_arc_length(*LINE)
        t, _ = arc_length_inverse(*LINE, 0.0, total)
        assert t == 0.0
        t, _ = arc_length_inverse(*LINE, total, total)
        assert t == 1.0

    def test_midpoint_on_line(self):
        """For a line, half arc length should give t ≈ 0.5."""
        total = segment_arc_length(*LINE)
        t, iters = arc_length_inverse(*LINE, total / 2, total)
        assert abs(t - 0.5) < 1e-6
        assert iters < 20

    def test_monotonicity(self):
        """Larger target → larger t."""
        total = segment_arc_length(*QUARTER)
        t1, _ = arc_length_inverse(*QUARTER, total * 0.25, total)
        t2, _ = arc_length_inverse(*QUARTER, total * 0.50, total)
        t3, _ = arc_length_inverse(*QUARTER, total * 0.75, total)
        assert t1 < t2 < t3


class TestContourArcLengths:
    def test_cumulative(self):
        """Cumulative lengths should be monotonically increasing."""
        contour = [LINE, QUARTER]
        seg_lens, cum_lens = contour_arc_lengths(contour)
        assert len(seg_lens) == 2
        assert len(cum_lens) == 2
        assert cum_lens[0] == seg_lens[0]
        assert abs(cum_lens[1] - (seg_lens[0] + seg_lens[1])) < 1e-10
        assert cum_lens[0] < cum_lens[1]
