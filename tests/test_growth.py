"""Tests for growth algorithms: Vogel, angular sort, contour sampling."""

import math

from glyph_animator.algorithms.growth import (
    angular_sort_assignment,
    sample_glyph_outline,
    vogel_positions,
)


class TestVogelPositions:
    def test_count(self):
        pts = vogel_positions(50, (0, 0), 100.0)
        assert len(pts) == 50

    def test_center_near_origin(self):
        """First point should be near center (r = radius * sqrt(0/N) = 0)."""
        pts = vogel_positions(50, (100, 200), 100.0)
        assert abs(pts[0][0] - 100) < 1e-10
        assert abs(pts[0][1] - 200) < 1e-10

    def test_bounded_by_radius(self):
        """All points should be within the specified radius."""
        pts = vogel_positions(100, (0, 0), 50.0)
        for x, y in pts:
            r = math.sqrt(x * x + y * y)
            assert r <= 50.0 + 1e-6


class TestAngularSortAssignment:
    def test_bijection(self):
        """Assignment should be a bijection (each source → unique target)."""
        sources = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        targets = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        centroid = (0, 0)
        assignments = angular_sort_assignment(sources, targets, centroid)

        src_idxs = [a[0] for a in assignments]
        tgt_idxs = [a[1] for a in assignments]
        assert len(set(src_idxs)) == 4
        assert len(set(tgt_idxs)) == 4

    def test_same_count(self):
        sources = vogel_positions(20, (0, 0), 100)
        targets = [(i * 10, 0) for i in range(20)]
        centroid = (0, 0)
        assignments = angular_sort_assignment(sources, targets, centroid)
        assert len(assignments) == 20


class TestContourSampling:
    def test_correct_count(self):
        """Should return exactly n_points."""
        # Simple line contour as cubics
        seg = ((0.0, 0.0), (33.0, 0.0), (67.0, 0.0), (100.0, 0.0))
        contours = [[seg]]
        pts = sample_glyph_outline(contours, 10)
        assert len(pts) == 10

    def test_points_on_contour(self):
        """Sampled points should lie on the contour."""
        seg = ((0.0, 0.0), (33.0, 0.0), (67.0, 0.0), (100.0, 0.0))
        contours = [[seg]]
        pts = sample_glyph_outline(contours, 5)
        for x, y in pts:
            assert 0.0 <= x <= 100.0 + 1e-6
            assert abs(y) < 1e-6
