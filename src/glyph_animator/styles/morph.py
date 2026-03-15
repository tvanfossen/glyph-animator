"""Morph style: direct contour interpolation with fade-in/fade-out."""

from __future__ import annotations

from glyph_animator.lottie.builder import (
    _fill,
    animated_shape,
    animated_val,
    shape_group,
    static_shape,
    static_val,
)
from glyph_animator.lottie.easing import EASE_IN_OUT, ORGANIC
from glyph_animator.lottie.keyframes import opacity_keyframe, shape_keyframe
from glyph_animator.lottie.paths import contour_to_lottie_path
from glyph_animator.models.geometry import MatchedPair
from glyph_animator.pipeline.glyph_pipeline import _contour_to_tuples
from glyph_animator.renderer.base import RenderedDigit
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

    def _build_creation(self, rendered: RenderedDigit) -> list[dict]:
        """Fade in: opacity 0 → 100 over duration."""
        shapes = _static_glyph_shapes(rendered)
        opacity_kfs = [
            opacity_keyframe(0, 0, EASE_IN_OUT),
            opacity_keyframe(self.duration_frames, 100, is_final=True),
        ]
        return [_glyph_layer("creation", shapes, opacity_kfs, self.duration_frames)]

    def _build_destruction(self, rendered: RenderedDigit) -> list[dict]:
        """Fade out: opacity 100 → 0 over duration."""
        shapes = _static_glyph_shapes(rendered)
        opacity_kfs = [
            opacity_keyframe(0, 100, EASE_IN_OUT),
            opacity_keyframe(self.duration_frames, 0, is_final=True),
        ]
        return [_glyph_layer("destruction", shapes, opacity_kfs, self.duration_frames)]

    def _build_transition(
        self, rendered_a: RenderedDigit, rendered_b: RenderedDigit, pairs: list[MatchedPair]
    ) -> list[dict]:
        """Shape path morph between matched contour pairs."""
        hold = 15
        morph_end = hold + self.duration_frames

        shape_items: list[dict] = []
        for pi, pair in enumerate(pairs):
            ca = _contour_to_tuples(pair.contour_a)
            cb = _contour_to_tuples(pair.contour_b)
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

        return [
            {
                "ty": 4,
                "nm": "morph-transition",
                "sr": 1,
                "ks": _default_ks(),
                "ao": 0,
                "shapes": [group],
                "ip": 0,
                "op": morph_end + 30,
                "st": 0,
            }
        ]


def _static_glyph_shapes(rendered: RenderedDigit) -> list[dict]:
    """Build static shape items from RenderedDigit contours."""
    items: list[dict] = []
    for ci, contour in enumerate(rendered.fitted_contours):
        segs = _contour_to_tuples(contour)
        path = contour_to_lottie_path(segs)
        items.append(static_shape(f"contour-{ci}", path))
    items.append(_fill([0.95, 0.95, 0.95, 1], rule=1))
    return items


def _glyph_layer(name, shapes, opacity_kfs, duration):
    """Build a shape layer with animated opacity."""
    ks = _default_ks()
    ks["o"] = animated_val(opacity_kfs)
    group = shape_group(name, shapes)
    return {
        "ty": 4,
        "nm": name,
        "sr": 1,
        "ks": ks,
        "ao": 0,
        "shapes": [group],
        "ip": 0,
        "op": duration + 30,
        "st": 0,
    }


def _default_ks():
    return {
        "p": static_val([0, 0, 0]),
        "a": static_val([0, 0, 0]),
        "s": static_val([100, 100, 100]),
        "r": static_val(0),
        "o": static_val(100),
    }


register_style("morph", MorphStyle)
