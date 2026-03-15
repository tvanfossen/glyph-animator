"""Tests for Lottie path conversion (contour ↔ Lottie path round-trip)."""

from glyph_animator.lottie.paths import (
    contour_to_lottie_path,
    lottie_path_to_contour,
    offset_contour,
)

# A simple square contour as 4 cubic segments (lines as degenerate cubics)
SQUARE = [
    ((0.0, 0.0), (33.0, 0.0), (67.0, 0.0), (100.0, 0.0)),
    ((100.0, 0.0), (100.0, 33.0), (100.0, 67.0), (100.0, 100.0)),
    ((100.0, 100.0), (67.0, 100.0), (33.0, 100.0), (0.0, 100.0)),
    ((0.0, 100.0), (0.0, 67.0), (0.0, 33.0), (0.0, 0.0)),
]


class TestContourToLottiePath:
    def test_vertex_count(self):
        """One vertex per segment."""
        path = contour_to_lottie_path(SQUARE)
        assert len(path["v"]) == 4
        assert len(path["i"]) == 4
        assert len(path["o"]) == 4

    def test_closed(self):
        assert contour_to_lottie_path(SQUARE)["c"] is True

    def test_vertices_are_segment_starts(self):
        path = contour_to_lottie_path(SQUARE)
        for i, seg in enumerate(SQUARE):
            assert path["v"][i] == [seg[0][0], seg[0][1]]

    def test_tangents_are_relative(self):
        """Out-tangent = C1 - C0 (relative, not absolute)."""
        path = contour_to_lottie_path(SQUARE)
        c0, c1, _, _ = SQUARE[0]
        assert abs(path["o"][0][0] - (c1[0] - c0[0])) < 1e-10
        assert abs(path["o"][0][1] - (c1[1] - c0[1])) < 1e-10


class TestRoundTrip:
    def test_round_trip_preserves_shape(self):
        """contour → lottie_path → contour should preserve all control points."""
        path = contour_to_lottie_path(SQUARE)
        recovered = lottie_path_to_contour(path)

        assert len(recovered) == len(SQUARE)
        for orig, rec in zip(SQUARE, recovered, strict=False):
            for pi in range(4):
                assert abs(orig[pi][0] - rec[pi][0]) < 1e-8
                assert abs(orig[pi][1] - rec[pi][1]) < 1e-8


class TestOffsetContour:
    def test_y_flip(self):
        """Y should be flipped: font Y-up → canvas Y-down."""
        offset = offset_contour(SQUARE, ox=0, oy=0, canvas_h=200)
        # Original (0, 0) → canvas (0, 200)
        assert abs(offset[0][0][1] - 200.0) < 1e-10
        # Original (0, 100) → canvas (0, 100)
        assert abs(offset[2][0][1] - 100.0) < 1e-10

    def test_offset_applied(self):
        """ox/oy shift should be applied before Y-flip."""
        offset = offset_contour(SQUARE, ox=10, oy=20, canvas_h=200)
        # (0,0) + offset (10,20) → (10, 20) → y-flip → (10, 200-20) = (10, 180)
        assert abs(offset[0][0][0] - 10.0) < 1e-10
        assert abs(offset[0][0][1] - 180.0) < 1e-10
