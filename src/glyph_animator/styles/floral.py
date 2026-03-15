"""Floral scatter style: Vogel spiral bloom -> digit outline."""

from __future__ import annotations

import math

from glyph_animator.algorithms.growth import angular_sort_assignment, sample_glyph_outline
from glyph_animator.algorithms.shapes import DaisyGenerator
from glyph_animator.algorithms.vogel import vogel_positions
from glyph_animator.constants import GOLDEN_ANGLE
from glyph_animator.lottie.builder import (
    animated_val,
    make_transform,
)
from glyph_animator.lottie.keyframes import (
    position_keyframe,
    position_keyframe_final,
)
from glyph_animator.models.geometry import MatchedPair
from glyph_animator.renderer.base import RenderedGlyph
from glyph_animator.styles.base import StyleBase
from glyph_animator.styles.registry import register_style


class FloralStyle(StyleBase):
    """Flowers in a Vogel spiral converge to form a digit."""

    def __init__(self, n_flowers: int = 50, duration_frames: int = 60, fps: int = 30):
        super().__init__("floral", duration_frames, fps)
        self.n_flowers = n_flowers

    def _create_layers(self, rendered: RenderedGlyph) -> list[dict]:
        """Flowers gather from Vogel spiral to digit outline."""
        data, targets = self._resolve_animation(rendered)
        return _build_gather_layers(data, targets)

    def _destroy_layers(self, rendered: RenderedGlyph) -> list[dict]:
        """Flowers scatter from digit outline back to Vogel spiral."""
        data, targets = self._resolve_animation(rendered)
        return _build_scatter_layers(data, targets)

    def _transition_layers(
        self, rendered_a: RenderedGlyph, rendered_b: RenderedGlyph, pairs: list[MatchedPair]
    ) -> list[dict]:
        """Flowers scatter from A, regroup on B."""
        data_a, targets_a = self._resolve_animation(rendered_a)
        data_b, targets_b = self._resolve_animation(rendered_b)
        return _build_transition_layers(data_a, data_b, targets_a, targets_b)

    def _resolve_animation(self, rendered: RenderedGlyph):
        """Compute Vogel positions, outline targets, and assignments."""
        contours = [c.to_tuples() for c in rendered.fitted_contours]
        center, radius = self._extract_geometry(rendered)
        vogel = vogel_positions(self.n_flowers, center, radius)
        targets = sample_glyph_outline(contours, self.n_flowers)
        centroid = _centroid(targets)
        assignments_list = angular_sort_assignment(vogel, targets, centroid)
        lookup = {si: ti for si, ti in assignments_list}
        data = _FloralAnimationData(vogel, lookup, self.duration_frames)
        return data, targets


def _centroid(pts):
    n = len(pts)
    return (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n)


class _FloralAnimationData:
    """Resolved animation data for a set of flowers."""

    __slots__ = ("vogel", "assignments", "duration")

    def __init__(self, vogel: list, assignments: dict, duration: int):
        self.vogel = vogel
        self.assignments = assignments
        self.duration = duration


def _build_gather_layers(data: _FloralAnimationData, targets: list) -> list[dict]:
    """Build flower layers that gather from Vogel to targets."""
    layers = []
    for idx in range(len(data.vogel)):
        start = data.vogel[idx]
        end = targets[data.assignments[idx]]
        bloom = _bloom_offset(idx, data.duration)
        kfs = _travel_keyframes(start, end, bloom, data.duration)
        layers.append(_make_flower_layer(idx, kfs, data.duration))
    return layers


def _build_scatter_layers(data: _FloralAnimationData, targets: list) -> list[dict]:
    """Build flower layers that scatter from targets to Vogel."""
    layers = []
    for idx in range(len(data.vogel)):
        start = targets[data.assignments[idx]]
        end = data.vogel[idx]
        kfs = _travel_keyframes(start, end, 0, data.duration)
        layers.append(_make_flower_layer(idx, kfs, data.duration))
    return layers


def _build_transition_layers(data_a, data_b, targets_a, targets_b):
    """Scatter from A -> Vogel -> gather to B."""
    layers = []
    half = data_a.duration // 2

    for idx in range(len(data_a.vogel)):
        src = targets_a[data_a.assignments[idx]]
        via = data_a.vogel[idx]
        dst = targets_b[data_b.assignments[idx]]

        pos_kfs = [
            _spatial_keyframe(0, src, via),
            _spatial_keyframe(half, via, dst),
            position_keyframe_final(data_a.duration, dst[0], dst[1]),
        ]
        layers.append(_make_flower_layer(idx, pos_kfs, data_a.duration))
    return layers


def _spatial_keyframe(frame, start, end):
    """Position keyframe with spatial tangents from start->end."""
    dx, dy = (end[0] - start[0]) / 6, (end[1] - start[1]) / 6
    return position_keyframe(frame, start[0], start[1], to=(dx, dy, 0), ti=(-dx, -dy, 0))


def _travel_keyframes(start, end, start_frame, duration):
    """Two-keyframe travel from start to end."""
    dx, dy = (end[0] - start[0]) / 6, (end[1] - start[1]) / 6
    return [
        position_keyframe(start_frame, start[0], start[1], to=(dx, dy, 0), ti=(-dx, -dy, 0)),
        position_keyframe_final(duration, end[0], end[1]),
    ]


def _bloom_offset(idx, duration):
    return int(((idx * GOLDEN_ANGLE / (2 * math.pi)) % 1.0) * duration * 0.3)


_DAISY = DaisyGenerator()


def _make_flower_layer(idx, pos_kfs, duration):
    """Build a flower shape layer with given position keyframes."""
    shapes = [{"ty": "gr", "nm": "flower", "it": _DAISY.generate(idx)}]
    return {
        "ty": 4,
        "nm": f"flower-{idx}",
        "sr": 1,
        "ks": make_transform(pos=animated_val(pos_kfs)),
        "ao": 0,
        "shapes": shapes,
        "ip": 0,
        "op": duration + 30,
        "st": 0,
    }


register_style("floral", FloralStyle)
