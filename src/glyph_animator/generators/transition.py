"""Generator for single A->B transition animations."""

from __future__ import annotations

from pathlib import Path

from glyph_animator.generators.base import GeneratorBase
from glyph_animator.pipeline.glyph_pipeline import GlyphPipeline
from glyph_animator.renderer.base import GlyphRendererBase
from glyph_animator.styles.base import StyleBase


class TransitionGenerator(GeneratorBase):
    """Generate a single transition Lottie for glyph A -> glyph B."""

    def __init__(
        self,
        pipeline: GlyphPipeline,
        renderer: GlyphRendererBase,
        style: StyleBase,
        output_dir: str | Path,
    ):
        super().__init__(pipeline, renderer, style, output_dir)

    def generate_pair(self, char_a: str, char_b: str) -> Path:
        """Generate transition for one pair."""
        rendered_a, rendered_b, pairs = self._process_pair(char_a, char_b)
        layers = self._style.build_transition(rendered_a, rendered_b, pairs)

        w, h = self._canvas_size(rendered_a, rendered_b)
        filename = f"{self._style.name}_{char_a}_{char_b}.json"
        return self._build_and_save(
            f"{self._style.name}-{char_a}-{char_b}",
            w,
            h,
            layers,
            filename,
        )

    def generate(self) -> list[Path]:
        """Generate transitions for default digit pairs."""
        default_pairs = [("3", "8"), ("0", "8"), ("4", "9")]
        return [self.generate_pair(a, b) for a, b in default_pairs]
