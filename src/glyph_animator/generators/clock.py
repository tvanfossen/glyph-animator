"""Generator for seekable clock animation (0→1→2→...→9→0)."""

from __future__ import annotations

from pathlib import Path

from glyph_animator.generators.base import GeneratorBase
from glyph_animator.lottie.builder import LottieBuilder
from glyph_animator.pipeline.glyph_pipeline import GlyphPipeline
from glyph_animator.renderer.digit_renderer import DigitRenderer
from glyph_animator.styles.base import StyleBase


class ClockGenerator(GeneratorBase):
    """Generate a seekable Lottie with all 10 sequential digit transitions.

    Layout: 10 transitions × duration_frames each.
    0→1, 1→2, 2→3, ..., 8→9, 9→0
    Total frames = 10 × duration_frames
    """

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

    def generate(self) -> list[Path]:
        """Generate the seekable clock file."""
        digits = "0123456789"
        dur = self._style.duration_frames
        total_frames = 10 * dur

        # Use bounds from digit 0 as reference
        glyph_0 = self._pipeline.process_glyph("0")
        b = glyph_0.bounds
        margin = 50
        w = int(b.width + 2 * margin)
        h = int(b.height + 2 * margin)

        builder = LottieBuilder(
            f"clock-{self._style.name}",
            w,
            h,
            fps=self._style.fps,
            frames=total_frames,
        )

        for i in range(10):
            char_a = digits[i]
            char_b = digits[(i + 1) % 10]
            frame_offset = i * dur

            glyph_a = self._pipeline.process_glyph(char_a)
            glyph_b = self._pipeline.process_glyph(char_b)
            pairs = self._pipeline.process_pair(char_a, char_b)
            rendered_a = self._renderer.render(glyph_a)
            rendered_b = self._renderer.render(glyph_b)

            layers = self._style.build_transition(rendered_a, rendered_b, pairs)
            for layer in layers:
                layer["ip"] = frame_offset
                layer["op"] = frame_offset + dur
                builder._layers.append(layer)

        builder.add_background()
        path = self._save(builder, f"clock_{self._style.name}.json")
        return [path]
