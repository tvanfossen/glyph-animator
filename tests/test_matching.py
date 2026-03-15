"""Tests for contour matching, alignment, and morphing."""

from glyph_animator.algorithms.matching import (
    align_starting_points,
    contour_centroid,
    contour_signed_area,
    hungarian_match,
    make_degenerate_contour,
    match_contours,
    morph_contours,
)


# A square contour (4 segments, CW)
def _square(cx, cy, size):
    """Build a square contour centered at (cx, cy)."""
    h = size / 2
    # 4 line-like cubics forming a square
    pts = [(cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h)]
    segs = []
    for i in range(4):
        p0 = pts[i]
        p3 = pts[(i + 1) % 4]
        p1 = (p0[0] + (p3[0] - p0[0]) / 3, p0[1] + (p3[1] - p0[1]) / 3)
        p2 = (p0[0] + 2 * (p3[0] - p0[0]) / 3, p0[1] + 2 * (p3[1] - p0[1]) / 3)
        segs.append((p0, p1, p2, p3))
    return segs


SQ_A = _square(50, 50, 100)
SQ_B = _square(200, 200, 80)
SQ_C = _square(50, 50, 60)  # Same center as A, different size


class TestHungarianMatch:
    def test_trivial_1x1(self):
        assert hungarian_match([[5.0]]) == [(0, 0)]

    def test_identity_optimal(self):
        """Diagonal-dominant matrix → identity assignment."""
        cost = [[1.0, 100.0], [100.0, 1.0]]
        result = hungarian_match(cost)
        assert result == [(0, 0), (1, 1)]

    def test_swap_optimal(self):
        """Off-diagonal dominant → swapped assignment."""
        cost = [[100.0, 1.0], [1.0, 100.0]]
        result = hungarian_match(cost)
        assert result == [(0, 1), (1, 0)]


class TestContourGeometry:
    def test_centroid(self):
        c = contour_centroid(SQ_A)
        assert abs(c[0] - 50) < 1
        assert abs(c[1] - 50) < 1

    def test_signed_area_nonzero(self):
        area = contour_signed_area(SQ_A)
        assert abs(area) > 0

    def test_degenerate_contour(self):
        degen = make_degenerate_contour((50.0, 50.0), 4)
        assert len(degen) == 4
        assert all(seg[0] == (50.0, 50.0) for seg in degen)


class TestMatchContours:
    def test_equal_counts(self):
        """Two glyphs with 1 contour each → 1 pair."""
        pairs = match_contours([SQ_A], [SQ_B], 4)
        assert len(pairs) == 1

    def test_unequal_counts(self):
        """1 contour vs 2 → 2 pairs (one degenerate)."""
        pairs = match_contours([SQ_A], [SQ_B, SQ_C], 4)
        assert len(pairs) == 2


class TestAlignment:
    def test_reduces_cost(self):
        """Alignment should not increase total squared distance."""
        # Rotate SQ_A by 1 segment to create misalignment
        rotated = SQ_A[1:] + SQ_A[:1]
        k, unaligned, aligned, _ = align_starting_points(SQ_A, rotated)
        assert aligned <= unaligned + 1e-6

    def test_identical_contours(self):
        """Identical contours → k=0, cost=0."""
        k, _, aligned, _ = align_starting_points(SQ_A, SQ_A)
        assert k == 0
        assert aligned < 1e-6


class TestMorphContours:
    def test_alpha_zero(self):
        """α=0 returns source contour exactly."""
        result = morph_contours(SQ_A, SQ_B, 0.0)
        for seg_r, seg_a in zip(result, SQ_A, strict=False):
            for i in range(4):
                assert abs(seg_r[i][0] - seg_a[i][0]) < 1e-10
                assert abs(seg_r[i][1] - seg_a[i][1]) < 1e-10

    def test_alpha_one(self):
        """α=1 returns target contour exactly."""
        result = morph_contours(SQ_A, SQ_B, 1.0)
        for seg_r, seg_b in zip(result, SQ_B, strict=False):
            for i in range(4):
                assert abs(seg_r[i][0] - seg_b[i][0]) < 1e-10
                assert abs(seg_r[i][1] - seg_b[i][1]) < 1e-10

    def test_midpoint_between(self):
        """α=0.5 should produce points between A and B."""
        result = morph_contours(SQ_A, SQ_B, 0.5)
        for seg_r, seg_a, seg_b in zip(result, SQ_A, SQ_B, strict=False):
            expected_x = (seg_a[0][0] + seg_b[0][0]) / 2
            expected_y = (seg_a[0][1] + seg_b[0][1]) / 2
            assert abs(seg_r[0][0] - expected_x) < 1e-10
            assert abs(seg_r[0][1] - expected_y) < 1e-10
