"""Generator for single A→B transition animations."""

from __future__ import annotations

from pathlib import Path

from glyph_animator.generators.base import GeneratorBase
from glyph_animator.lottie.builder import LottieBuilder
from glyph_animator.pipeline.glyph_pipeline import GlyphPipeline
from glyph_animator.renderer.digit_renderer import DigitRenderer
from glyph_animator.styles.base import StyleBase


class TransitionGenerator(GeneratorBase):
    """Generate a single transition Lottie for glyph A → glyph B."""

    def __init__(
        self,
        pipeline: GlyphPipeline,
        renderer: DigitRenderer,
        style: StyleBase,
        output_dir: str | Path,
    ):
        super().__init__(output_dir)
        self._pipeline = pipeline
        self._renderer = renderer
        self._style = style

    def generate_pair(self, char_a: str, char_b: str) -> Path:
        """Generate transition for one pair."""
        glyph_a = self._pipeline.process_glyph(char_a)
        glyph_b = self._pipeline.process_glyph(char_b)
        pairs = self._pipeline.process_pair(char_a, char_b)
        rendered_a = self._renderer.render(glyph_a)
        rendered_b = self._renderer.render(glyph_b)

        layers = self._style.build_transition(rendered_a, rendered_b, pairs)

        ba, bb = glyph_a.bounds, glyph_b.bounds
        margin = 50
        w = int(max(ba.width, bb.width) + 2 * margin)
        h = int(max(ba.height, bb.height) + 2 * margin)

        builder = LottieBuilder(
            f"{self._style.name}-{char_a}-{char_b}",
            w,
            h,
            fps=self._style.fps,
            frames=self._style.duration_frames + 45,
        )
        for layer in layers:
            builder._layers.append(layer)
        builder.add_background()

        return self._save(builder, f"{self._style.name}_{char_a}_{char_b}.json")

    def generate(self) -> list[Path]:
        """Generate transitions for default digit pairs."""
        default_pairs = [("3", "8"), ("0", "8"), ("4", "9")]
        return [self.generate_pair(a, b) for a, b in default_pairs]
