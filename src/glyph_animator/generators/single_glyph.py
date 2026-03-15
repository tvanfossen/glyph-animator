"""Generator for single glyph creation/destruction animations."""

from __future__ import annotations

from pathlib import Path

from glyph_animator.generators.base import GeneratorBase
from glyph_animator.models.config import AnimationType
from glyph_animator.pipeline.glyph_pipeline import GlyphPipeline
from glyph_animator.renderer.base import GlyphRendererBase
from glyph_animator.styles.base import StyleBase


class SingleGlyphGenerator(GeneratorBase):
    """Generate creation or destruction animation for a single glyph."""

    def __init__(
        self,
        pipeline: GlyphPipeline,
        renderer: GlyphRendererBase,
        style: StyleBase,
        output_dir: str | Path,
        animation_type: AnimationType = AnimationType.CREATION,
    ):
        super().__init__(pipeline, renderer, style, output_dir)
        self._animation_type = animation_type

    def generate_glyph(self, char: str) -> Path:
        """Generate animation for one character."""
        rendered = self._process_glyph(char)

        if self._animation_type == AnimationType.CREATION:
            layers = self._style.build_creation(rendered)
            prefix = "creation"
        else:
            layers = self._style.build_destruction(rendered)
            prefix = "destruction"

        w, h = self._canvas_size(rendered)
        filename = f"{self._style.name}_{prefix}_{char}.json"
        return self._build_and_save(
            f"{prefix}-{char}",
            w,
            h,
            layers,
            filename,
            frames=self._style.duration_frames + 30,
        )

    def generate(self) -> list[Path]:
        """Generate for default digit set."""
        return [self.generate_glyph(c) for c in "0123456789"]
