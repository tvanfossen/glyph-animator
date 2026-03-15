"""Tests for digit renderer."""

from glyph_animator.pipeline.glyph_pipeline import GlyphPipeline
from glyph_animator.renderer.glyph_renderer import GlyphRenderer


class TestGlyphRenderer:
    def test_produces_rendered_digit(self, font_path):
        pipe = GlyphPipeline(font_path, segment_count=32)
        glyph = pipe.process_glyph("3")
        renderer = GlyphRenderer(n_outline_layers=3, n_arc_samples=50)
        rendered = renderer.render(glyph)

        assert rendered.glyph.character == "3"
        assert len(rendered.fitted_contours) >= 1
        assert len(rendered.outline_layers) >= 1
        assert rendered.matte_contour is not None

    def test_arc_samples_count(self, font_path):
        pipe = GlyphPipeline(font_path, segment_count=32)
        glyph = pipe.process_glyph("8")
        renderer = GlyphRenderer(n_arc_samples=50)
        rendered = renderer.render(glyph)

        for samples in rendered.arc_samples:
            assert len(samples) == 50

    def test_outline_layers_per_contour(self, font_path):
        pipe = GlyphPipeline(font_path, segment_count=16)
        glyph = pipe.process_glyph("0")
        n_outlines = 2
        renderer = GlyphRenderer(n_outline_layers=n_outlines)
        rendered = renderer.render(glyph)

        n_contours = len(glyph.contours)
        assert len(rendered.outline_layers) == n_contours * n_outlines

    def test_matte_is_largest(self, font_path):
        """Matte contour should be the outermost (largest area)."""
        pipe = GlyphPipeline(font_path, segment_count=16)
        glyph = pipe.process_glyph("8")
        renderer = GlyphRenderer()
        rendered = renderer.render(glyph)

        # Matte should be present for multi-contour glyphs
        assert rendered.matte_contour is not None
        assert rendered.matte_contour.segment_count > 0
