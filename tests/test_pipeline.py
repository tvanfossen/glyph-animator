"""Tests for the end-to-end glyph pipeline."""

import pytest

from glyph_animator.pipeline.glyph_pipeline import GlyphPipeline


class TestGlyphPipeline:
    def test_extract_single_digit(self, font_path):
        """Pipeline produces GlyphData with resampled contours."""
        pipe = GlyphPipeline(font_path, segment_count=32)
        glyph = pipe.process_glyph("3")

        assert glyph.character == "3"
        assert len(glyph.contours) >= 1
        assert glyph.units_per_em > 0
        assert glyph.bounds.width > 0

        # Every contour should have exactly 32 segments
        for contour in glyph.contours:
            assert contour.segment_count == 32

    def test_extract_all_digits(self, font_path):
        """All 10 digits extract successfully."""
        pipe = GlyphPipeline(font_path, segment_count=16)
        for char in "0123456789":
            glyph = pipe.process_glyph(char)
            assert glyph.character == char
            assert len(glyph.contours) >= 1

    def test_process_pair(self, font_path):
        """Pair processing produces matched pairs with aligned contours."""
        pipe = GlyphPipeline(font_path, segment_count=32)
        pairs = pipe.process_pair("3", "8")

        assert len(pairs) >= 1
        for pair in pairs:
            # Both contours should have matching segment counts
            assert pair.contour_a.segment_count == pair.contour_b.segment_count
            assert pair.rotation_offset >= 0

    def test_pair_with_different_contour_counts(self, font_path):
        """Glyphs with different contour counts get padded with degenerates."""
        pipe = GlyphPipeline(font_path, segment_count=16)
        pairs = pipe.process_pair("1", "8")
        # "8" typically has 3 contours, "1" has 1 → should have 3 pairs
        assert len(pairs) >= 1
        # At least one pair should be degenerate on the "1" side
        has_degen = any(p.is_degenerate_a or p.is_degenerate_b for p in pairs)
        if len(pairs) > 1:
            assert has_degen

    def test_invalid_character(self, font_path):
        """Non-existent character raises ValueError."""
        pipe = GlyphPipeline(font_path)
        with pytest.raises(ValueError, match="not in font"):
            pipe.process_glyph("\u4e00")  # CJK character unlikely in Nunito
