"""Tests for style infrastructure and morph style."""

import pytest

from glyph_animator.pipeline.glyph_pipeline import GlyphPipeline
from glyph_animator.renderer.digit_renderer import DigitRenderer
from glyph_animator.styles.morph import MorphStyle
from glyph_animator.styles.registry import get_style_class, list_styles


class TestRegistry:
    def test_morph_registered(self):
        assert "morph" in list_styles()

    def test_get_morph(self):
        cls = get_style_class("morph")
        assert cls is MorphStyle

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown style"):
            get_style_class("nonexistent")


class TestMorphStyle:
    def test_creation(self, font_path):
        pipe = GlyphPipeline(font_path, segment_count=16)
        renderer = DigitRenderer()
        style = MorphStyle(duration_frames=30)

        glyph = pipe.process_glyph("3")
        rendered = renderer.render(glyph)
        layers = style.build_creation(rendered)

        assert len(layers) >= 1
        assert layers[0]["ty"] == 4

    def test_destruction(self, font_path):
        pipe = GlyphPipeline(font_path, segment_count=16)
        renderer = DigitRenderer()
        style = MorphStyle(duration_frames=30)

        glyph = pipe.process_glyph("3")
        rendered = renderer.render(glyph)
        layers = style.build_destruction(rendered)

        assert len(layers) >= 1

    def test_transition(self, font_path):
        pipe = GlyphPipeline(font_path, segment_count=16)
        renderer = DigitRenderer()
        style = MorphStyle(duration_frames=30)

        glyph_a = pipe.process_glyph("3")
        glyph_b = pipe.process_glyph("8")
        pairs = pipe.process_pair("3", "8")
        rendered_a = renderer.render(glyph_a)
        rendered_b = renderer.render(glyph_b)
        layers = style.build_transition(rendered_a, rendered_b, pairs)

        assert len(layers) >= 1
        # Should have animated shape keyframes
        shapes = layers[0].get("shapes", [])
        assert len(shapes) >= 1
