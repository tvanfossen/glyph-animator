"""Tests for contour resampling."""

from glyph_animator.algorithms.arc_length import contour_arc_lengths
from glyph_animator.algorithms.resampling import fit_cubic_to_group, resample_contour

# Simple contour: two segments forming an L-shape
SEG_A = ((0.0, 0.0), (33.0, 0.0), (67.0, 0.0), (100.0, 0.0))
SEG_B = ((100.0, 0.0), (100.0, 33.0), (100.0, 67.0), (100.0, 100.0))
L_CONTOUR = [SEG_A, SEG_B]


class TestResampleContour:
    def test_output_segment_count(self):
        """Resampled contour must have exactly target_n segments."""
        result = resample_contour(L_CONTOUR, 8)
        assert len(result) == 8

    def test_preserves_endpoints(self):
        """Start of first and end of last segment preserved."""
        result = resample_contour(L_CONTOUR, 8)
        # First point should be near (0, 0)
        assert abs(result[0][0][0]) < 1.0
        assert abs(result[0][0][1]) < 1.0
        # Last point should be near (100, 100)
        assert abs(result[-1][3][0] - 100.0) < 1.0
        assert abs(result[-1][3][1] - 100.0) < 1.0

    def test_segment_lengths_roughly_equal(self):
        """Resampled segments should have roughly equal arc lengths."""
        result = resample_contour(L_CONTOUR, 8)
        seg_lens, _ = contour_arc_lengths(result)
        mean_len = sum(seg_lens) / len(seg_lens)
        for sl in seg_lens:
            # Allow 20% deviation (resampling has bounded error)
            assert abs(sl - mean_len) / mean_len < 0.20

    def test_empty_contour(self):
        """Empty contour returns empty."""
        result = resample_contour([], 8)
        assert result == []

    def test_single_segment(self):
        """Single segment resampled to N segments."""
        result = resample_contour([SEG_A], 4)
        assert len(result) == 4


class TestFitCubicToGroup:
    def test_single_segment_passthrough(self):
        """Group of one segment returns itself."""
        result = fit_cubic_to_group([SEG_A])
        assert result[0] == SEG_A[0]
        assert result[3] == SEG_A[3]

    def test_preserves_group_endpoints(self):
        """Fitted cubic starts at group start, ends at group end."""
        result = fit_cubic_to_group(L_CONTOUR)
        assert result[0] == L_CONTOUR[0][0]
        assert result[3] == L_CONTOUR[-1][3]
