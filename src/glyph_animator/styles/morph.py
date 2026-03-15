"""Morph style: direct contour interpolation with fade-in/fade-out."""

from __future__ import annotations

from glyph_animator.lottie.builder import (
    _fill,
    animated_shape,
    animated_val,
    shape_group,
    static_shape,
)
from glyph_animator.lottie.easing import EASE_IN_OUT, ORGANIC
from glyph_animator.lottie.keyframes import opacity_keyframe, shape_keyframe
from glyph_animator.lottie.paths import contour_to_lottie_path
from glyph_animator.models.geometry import MatchedPair
from glyph_animator.renderer.base import RenderedGlyph
from glyph_animator.styles.base import StyleBase
from glyph_animator.styles.registry import register_style


class MorphStyle(StyleBase):
    """Direct contour interpolation morph.

    Creation: fade in from transparent
    Destruction: fade out to transparent
    Transition: Lottie shape path interpolation between matched contours
    """

    def __init__(self, duration_frames: int = 60, fps: int = 30):
        super().__init__("morph", duration_frames, fps)

    def _create_layers(self, rendered: RenderedGlyph) -> list[dict]:
        """Fade in: opacity 0 -> 100 over duration."""
        shapes = self._static_glyph_shapes(rendered)
        opacity_kfs = [
            opacity_keyframe(0, 0, EASE_IN_OUT),
            opacity_keyframe(self.duration_frames, 100, is_final=True),
        ]
        return [
            self._make_animated_layer(
                "creation",
                [shape_group("creation", shapes)],
                {"o": animated_val(opacity_kfs)},
            )
        ]

    def _destroy_layers(self, rendered: RenderedGlyph) -> list[dict]:
        """Fade out: opacity 100 -> 0 over duration."""
        shapes = self._static_glyph_shapes(rendered)
        opacity_kfs = [
            opacity_keyframe(0, 100, EASE_IN_OUT),
            opacity_keyframe(self.duration_frames, 0, is_final=True),
        ]
        return [
            self._make_animated_layer(
                "destruction",
                [shape_group("destruction", shapes)],
                {"o": animated_val(opacity_kfs)},
            )
        ]

    def _transition_layers(
        self, rendered_a: RenderedGlyph, rendered_b: RenderedGlyph, pairs: list[MatchedPair]
    ) -> list[dict]:
        """Shape path morph between matched contour pairs."""
        hold = 15
        morph_end = hold + self.duration_frames

        shape_items: list[dict] = []
        for pi, pair in enumerate(pairs):
            ca = pair.contour_a.to_tuples()
            cb = pair.contour_b.to_tuples()
            path_a = contour_to_lottie_path(ca)
            path_b = contour_to_lottie_path(cb)

            kfs = [
                shape_keyframe(0, path_a, path_a),
                shape_keyframe(hold, path_a, path_b, easing=ORGANIC),
                shape_keyframe(morph_end, path_b),
            ]
            shape_items.append(animated_shape(f"path-{pi}", kfs))

        shape_items.append(_fill([0.95, 0.95, 0.95, 1], rule=1))
        group = shape_group("glyph", shape_items)

        return [self._make_shape_layer("morph-transition", [group], op=morph_end + 30)]

    def _static_glyph_shapes(self, rendered: RenderedGlyph) -> list[dict]:
        """Build static shape items from RenderedGlyph contours."""
        paths = self._contours_to_paths(rendered)
        items: list[dict] = []
        for ci, path in enumerate(paths):
            items.append(static_shape(f"contour-{ci}", path))
        items.append(_fill([0.95, 0.95, 0.95, 1], rule=1))
        return items


register_style("morph", MorphStyle)
