"""Generator for single glyph creation/destruction animations."""

from __future__ import annotations

from pathlib import Path

from glyph_animator.generators.base import GeneratorBase
from glyph_animator.lottie.builder import LottieBuilder
from glyph_animator.models.config import AnimationType
from glyph_animator.pipeline.glyph_pipeline import GlyphPipeline
from glyph_animator.renderer.digit_renderer import DigitRenderer
from glyph_animator.styles.base import StyleBase


class SingleGlyphGenerator(GeneratorBase):
    """Generate creation or destruction animation for a single glyph."""

    def __init__(
        self,
        pipeline: GlyphPipeline,
        renderer: DigitRenderer,
        style: StyleBase,
        output_dir: str | Path,
        animation_type: AnimationType = AnimationType.CREATION,
    ):
        super().__init__(output_dir)
        self._pipeline = pipeline
        self._renderer = renderer
        self._style = style
        self._animation_type = animation_type

    def generate_glyph(self, char: str) -> Path:
        """Generate animation for one character."""
        glyph = self._pipeline.process_glyph(char)
        rendered = self._renderer.render(glyph)

        if self._animation_type == AnimationType.CREATION:
            layers = self._style.build_creation(rendered)
            prefix = "creation"
        else:
            layers = self._style.build_destruction(rendered)
            prefix = "destruction"

        b = glyph.bounds
        margin = 50
        w = int(b.width + 2 * margin)
        h = int(b.height + 2 * margin)

        builder = LottieBuilder(
            f"{prefix}-{char}",
            w,
            h,
            fps=self._style.fps,
            frames=self._style.duration_frames + 30,
        )
        for layer in layers:
            builder._layers.append(layer)
        builder.add_background()

        filename = f"{self._style.name}_{prefix}_{char}.json"
        return self._save(builder, filename)

    def generate(self) -> list[Path]:
        """Generate for default digit set."""
        return [self.generate_glyph(c) for c in "0123456789"]
