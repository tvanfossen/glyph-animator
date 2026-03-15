"""Generator for seekable clock animation (0->1->2->...->9->0)."""

from __future__ import annotations

from pathlib import Path

from glyph_animator.generators.base import GeneratorBase
from glyph_animator.lottie.builder import LottieBuilder
from glyph_animator.pipeline.glyph_pipeline import GlyphPipeline
from glyph_animator.renderer.base import GlyphRendererBase
from glyph_animator.styles.base import StyleBase


class ClockGenerator(GeneratorBase):
    """Generate a seekable Lottie with all 10 sequential digit transitions.

    Layout: 10 transitions x duration_frames each.
    0->1, 1->2, 2->3, ..., 8->9, 9->0
    Total frames = 10 x duration_frames
    """

    def __init__(
        self,
        pipeline: GlyphPipeline,
        renderer: GlyphRendererBase,
        style: StyleBase,
        output_dir: str | Path,
    ):
        super().__init__(pipeline, renderer, style, output_dir)

    def generate(self) -> list[Path]:
        """Generate the seekable clock file."""
        digits = "0123456789"
        dur = self._style.duration_frames
        total_frames = 10 * dur

        # Use bounds from digit 0 as reference
        rendered_0 = self._process_glyph("0")
        w, h = self._canvas_size(rendered_0)

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

            rendered_a, rendered_b, pairs = self._process_pair(char_a, char_b)
            layers = self._style.build_transition(rendered_a, rendered_b, pairs)
            for layer in layers:
                layer["ip"] = frame_offset
                layer["op"] = frame_offset + dur
                builder.add_layer(layer)

        builder.add_background()
        path = self._save(builder, f"clock_{self._style.name}.json")
        return [path]
