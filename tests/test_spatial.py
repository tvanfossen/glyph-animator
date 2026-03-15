"""Tests for spatial algorithms: ray casting, interior sampling."""

from glyph_animator.algorithms.spatial import (
    point_in_contours,
    point_in_polygon,
    sample_interior_points,
)

# Unit square
SQUARE = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]


class TestPointInPolygon:
    def test_inside(self):
        assert point_in_polygon((50, 50), SQUARE) is True

    def test_outside(self):
        assert point_in_polygon((150, 50), SQUARE) is False

    def test_edge_case_origin(self):
        """On the edge — implementation-specific, just shouldn't crash."""
        point_in_polygon((0, 0), SQUARE)


class TestPointInContours:
    def test_inside_outer(self):
        assert point_in_contours((50, 50), [SQUARE]) is True

    def test_inside_hole(self):
        """Point inside both outer and hole → outside glyph (even crossings)."""
        hole = [(25.0, 25.0), (75.0, 25.0), (75.0, 75.0), (25.0, 75.0)]
        assert point_in_contours((50, 50), [SQUARE, hole]) is False

    def test_outside_all(self):
        assert point_in_contours((150, 150), [SQUARE]) is False


class TestInteriorSampling:
    def test_correct_count(self):
        pts = sample_interior_points([SQUARE], (0, 0, 100, 100), 20)
        assert len(pts) == 20

    def test_all_inside(self):
        pts = sample_interior_points([SQUARE], (0, 0, 100, 100), 50)
        for x, y in pts:
            assert 0 <= x <= 100
            assert 0 <= y <= 100

    def test_deterministic(self):
        """Same seed → same points."""
        pts1 = sample_interior_points([SQUARE], (0, 0, 100, 100), 10, seed=42)
        pts2 = sample_interior_points([SQUARE], (0, 0, 100, 100), 10, seed=42)
        assert pts1 == pts2
