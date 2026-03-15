"""Contour sampling and angular sort assignment for glyph outlines."""

from __future__ import annotations

import math

from glyph_animator.algorithms.arc_length import arc_length_inverse, segment_arc_length
from glyph_animator.algorithms.base import Algorithm
from glyph_animator.algorithms.curves import eval_cubic

Pt = tuple[float, float]
Seg = tuple[Pt, Pt, Pt, Pt]


class ContourSampler(Algorithm[tuple, list[Pt]]):
    """Sample N equidistant points along contour outlines."""

    @property
    def proof_reference(self) -> str:
        return "docs/proofs/04_point_normalization.md"

    @property
    def complexity(self) -> str:
        return "O(N·S) where S = segments"

    @property
    def error_bound(self) -> str:
        return "< 10⁻⁶ (arc-length quadrature)"

    def execute(self, input_data: tuple) -> list[Pt]:
        contours, n_points = input_data
        return sample_glyph_outline(contours, n_points)


class AngularSortAssigner(Algorithm[tuple, list[tuple[int, int]]]):
    """Assign sources to targets by angular sorting — non-crossing paths."""

    @property
    def proof_reference(self) -> str:
        return "docs/proofs/08a_angular_sort_assignment.md"

    @property
    def complexity(self) -> str:
        return "O(N log N) for sorting"

    @property
    def error_bound(self) -> str:
        return "Non-crossing guarantee for convex targets"

    def execute(self, input_data: tuple) -> list[tuple[int, int]]:
        sources, targets, centroid = input_data
        return angular_sort_assignment(sources, targets, centroid)


# --- Free functions ---


def angular_sort_assignment(
    sources: list[Pt], targets: list[Pt], centroid: Pt
) -> list[tuple[int, int]]:
    """Assign sources to targets by angular sort. Non-crossing for convex targets."""
    cx, cy = centroid

    def angle(pt):
        return math.atan2(pt[1] - cy, pt[0] - cx)

    src_order = sorted(range(len(sources)), key=lambda i: angle(sources[i]))
    tgt_order = sorted(range(len(targets)), key=lambda i: angle(targets[i]))
    return list(zip(src_order, tgt_order, strict=False))


def sample_glyph_outline(contours: list[list[Seg]], n_points: int) -> list[Pt]:
    """Sample n_points along all contours, distributed by arc length."""
    all_segs: list[tuple[list[Seg], list[float], float]] = []
    grand_total = 0.0

    for contour in contours:
        seg_lens = [segment_arc_length(*s) for s in contour]
        total = sum(seg_lens)
        all_segs.append((contour, seg_lens, total))
        grand_total += total

    if grand_total < 1e-10:
        return [(0.0, 0.0)] * n_points

    points: list[Pt] = []
    for segs, seg_lens, total in all_segs:
        n_for = max(1, round(n_points * total / grand_total))
        points.extend(_sample_contour(segs, seg_lens, total, n_for))

    # Trim or pad to exactly n_points
    while len(points) < n_points:
        points.append(points[-1] if points else (0.0, 0.0))
    return points[:n_points]


def _sample_contour(segs, seg_lens, total, n):
    """Sample n points along a single contour."""
    delta = total / n
    pts = []
    seg_cum = 0.0
    seg_idx = 0

    for k in range(n):
        target_len = k * delta
        while seg_idx < len(segs) - 1 and seg_cum + seg_lens[seg_idx] < target_len:
            seg_cum += seg_lens[seg_idx]
            seg_idx += 1
        local = target_len - seg_cum
        t, _ = arc_length_inverse(*segs[seg_idx], local, seg_lens[seg_idx])
        pts.append(eval_cubic(*segs[seg_idx], t))
    return pts
