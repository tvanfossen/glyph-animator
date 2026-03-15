"""Base class for animation generators.

Owns pipeline orchestration, canvas sizing, and Lottie build+save.
Concrete generators implement only generate().
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from glyph_animator.pipeline.glyph_pipeline import GlyphPipeline
from glyph_animator.renderer.base import GlyphRendererBase, RenderedGlyph
from glyph_animator.styles.base import StyleBase


class GeneratorBase(ABC):
    """Base class for generators that produce Lottie output files."""

    def __init__(
        self,
        pipeline: GlyphPipeline,
        renderer: GlyphRendererBase,
        style: StyleBase,
        output_dir: str | Path,
    ):
        self._pipeline = pipeline
        self._renderer = renderer
        self._style = style
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def generate(self) -> list[Path]:
        """Generate output files. Returns list of created file paths."""

    def _process_glyph(self, char: str) -> RenderedGlyph:
        """Run a character through the pipeline and renderer."""
        glyph = self._pipeline.process_glyph(char)
        return self._renderer.render(glyph)

    def _process_pair(self, char_a: str, char_b: str):
        """Process both glyphs and their matched pairs."""
        rendered_a = self._process_glyph(char_a)
        rendered_b = self._process_glyph(char_b)
        pairs = self._pipeline.process_pair(char_a, char_b)
        return rendered_a, rendered_b, pairs

    def _canvas_size(self, *glyphs: RenderedGlyph, margin: int = 50):
        """Compute canvas dimensions from rendered glyph bounds."""
        bounds = [g.glyph.bounds for g in glyphs]
        w = int(max(b.width for b in bounds) + 2 * margin)
        h = int(max(b.height for b in bounds) + 2 * margin)
        return w, h

    @property
    def _default_frames(self) -> int:
        """Total frames for the output file. Override for multi-segment generators."""
        return self._style.duration_frames + 45

    def _build_and_save(self, name, w, h, layers, filename):
        """Build a Lottie file from layers and save it."""
        from glyph_animator.lottie.builder import LottieBuilder

        builder = LottieBuilder(name, w, h, self._style.fps, self._default_frames)
        for layer in layers:
            builder.add_layer(layer)
        builder.add_background()
        return self._save(builder, filename)

    def _save(self, builder, filename: str) -> Path:
        """Save a LottieBuilder to the output directory."""
        path = self.output_dir / filename
        builder.save(path)
        return path
