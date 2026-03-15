"""Floral scatter style: Vogel spiral bloom → digit outline."""

from __future__ import annotations

import math

from glyph_animator.algorithms.growth import (
    angular_sort_assignment,
    sample_glyph_outline,
    vogel_positions,
)
from glyph_animator.constants import GOLDEN_ANGLE, PHI
from glyph_animator.lottie.builder import (
    animated_val,
    make_transform,
    static_val,
)
from glyph_animator.lottie.keyframes import (
    position_keyframe,
    position_keyframe_final,
)
from glyph_animator.models.geometry import MatchedPair
from glyph_animator.pipeline.glyph_pipeline import _contour_to_tuples
from glyph_animator.renderer.base import RenderedDigit
from glyph_animator.styles.base import StyleBase
from glyph_animator.styles.registry import register_style

FLOWER_PALETTE = [
    [1.0, 0.51, 0.59],
    [1.0, 0.71, 0.39],
    [1.0, 0.39, 0.39],
    [0.71, 0.51, 1.0],
    [1.0, 0.86, 0.39],
    [1.0, 0.59, 0.78],
]
PETAL_COUNTS = [5, 6, 5, 8, 5, 6]


class FloralStyle(StyleBase):
    """Flowers in a Vogel spiral converge to form a digit."""

    def __init__(self, n_flowers: int = 50, duration_frames: int = 60, fps: int = 30):
        super().__init__("floral", duration_frames, fps)
        self.n_flowers = n_flowers

    def _build_creation(self, rendered: RenderedDigit) -> list[dict]:
        """Flowers gather from Vogel spiral to digit outline."""
        data, targets = self._resolve_animation(rendered)
        return _build_gather_layers(data, targets)

    def _build_destruction(self, rendered: RenderedDigit) -> list[dict]:
        """Flowers scatter from digit outline back to Vogel spiral."""
        data, targets = self._resolve_animation(rendered)
        return _build_scatter_layers(data, targets)

    def _build_transition(
        self, rendered_a: RenderedDigit, rendered_b: RenderedDigit, pairs: list[MatchedPair]
    ) -> list[dict]:
        """Flowers scatter from A, regroup on B."""
        data_a, targets_a = self._resolve_animation(rendered_a)
        data_b, targets_b = self._resolve_animation(rendered_b)
        return _build_transition_layers(data_a, data_b, targets_a, targets_b)

    def _resolve_animation(self, rendered: RenderedDigit):
        """Compute Vogel positions, outline targets, and assignments."""
        contours, center, radius = _glyph_geometry(rendered)
        vogel = vogel_positions(self.n_flowers, center, radius)
        targets = sample_glyph_outline(contours, self.n_flowers)
        centroid = _centroid(targets)
        assignments_list = angular_sort_assignment(vogel, targets, centroid)
        lookup = {si: ti for si, ti in assignments_list}
        data = _FloralAnimationData(vogel, lookup, self.duration_frames)
        return data, targets


def _glyph_geometry(rendered):
    """Extract contour tuples, center, and radius from RenderedDigit."""
    contours = [_contour_to_tuples(c) for c in rendered.fitted_contours]
    b = rendered.glyph.bounds
    center = ((b.x_min + b.x_max) / 2, (b.y_min + b.y_max) / 2)
    radius = max(b.width, b.height) * 0.6
    return contours, center, radius


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
    """Scatter from A → Vogel → gather to B."""
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
    """Position keyframe with spatial tangents from start→end."""
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


def _make_flower_layer(idx, pos_kfs, duration):
    """Build a flower shape layer with given position keyframes."""
    n_petals = PETAL_COUNTS[idx % len(PETAL_COUNTS)]
    color = FLOWER_PALETTE[idx % len(FLOWER_PALETTE)]
    size_factor = 0.7 + 0.6 * ((idx * PHI) % 1.0)

    petal_shapes = _flower_shapes(n_petals, size_factor, color)

    return {
        "ty": 4,
        "nm": f"flower-{idx}",
        "sr": 1,
        "ks": make_transform(pos=animated_val(pos_kfs)),
        "ao": 0,
        "shapes": petal_shapes,
        "ip": 0,
        "op": duration + 30,
        "st": 0,
    }


def _flower_shapes(n_petals, size_factor, color):
    """Build petal ellipses + pistil for one flower."""
    rx = 8.0 * size_factor
    ry = 5.0 * size_factor
    dist = 6.0 * size_factor
    items = []

    for i in range(n_petals):
        angle = i * (2 * math.pi / n_petals)
        pcx = dist * math.cos(angle)
        pcy = dist * math.sin(angle)
        items.append(
            {
                "ty": "el",
                "nm": f"petal-{i}",
                "p": static_val([pcx, pcy]),
                "s": static_val([rx * 2, ry * 2]),
            }
        )

    items.append(
        {"ty": "fl", "nm": "fill", "c": static_val(color + [1]), "r": 1, "o": static_val(100)}
    )

    # Pistil
    pistil_r = 3.0 * size_factor
    items.append(
        {
            "ty": "el",
            "nm": "pistil",
            "p": static_val([0, 0]),
            "s": static_val([pistil_r * 2, pistil_r * 2]),
        }
    )
    pistil_col = [color[0] * 0.6, color[1] * 0.6, color[2] * 0.3, 1]
    items.append(
        {
            "ty": "fl",
            "nm": "pistil-fill",
            "c": static_val(pistil_col),
            "r": 1,
            "o": static_val(100),
        }
    )

    # Group transform (must be last)
    items.append(
        {
            "ty": "tr",
            "p": static_val([0, 0]),
            "a": static_val([0, 0]),
            "s": static_val([100, 100]),
            "r": static_val(0),
            "o": static_val(100),
        }
    )

    return [{"ty": "gr", "nm": "flower", "it": items}]


register_style("floral", FloralStyle)
