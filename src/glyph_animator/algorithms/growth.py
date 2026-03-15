"""Growth algorithms: Vogel spiral, angular sort, L-system, contour sampling."""

from __future__ import annotations

import math

from glyph_animator.algorithms.arc_length import arc_length_inverse, segment_arc_length
from glyph_animator.algorithms.base import Algorithm
from glyph_animator.algorithms.curves import eval_cubic
from glyph_animator.constants import GOLDEN_ANGLE, LENGTH_DECAY

Pt = tuple[float, float]
Seg = tuple[Pt, Pt, Pt, Pt]


class VogelSpiralPlacer(Algorithm[tuple[int, Pt, float], list[Pt]]):
    """Generate N positions using Vogel's sunflower phyllotaxis model.

    θₙ = n · golden_angle
    rₙ = radius · √(n/N)
    """

    @property
    def proof_reference(self) -> str:
        return "docs/proofs/08_vogel_phyllotaxis.md"

    @property
    def complexity(self) -> str:
        return "O(N) direct formula evaluation"

    @property
    def error_bound(self) -> str:
        return "Exact (closed-form positions)"

    def execute(self, input_data: tuple[int, Pt, float]) -> list[Pt]:
        n, center, radius = input_data
        return vogel_positions(n, center, radius)


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


class LSystemGrower(Algorithm[tuple, list[dict]]):
    """Grow L-system branches attracted to a glyph outline."""

    def __init__(
        self,
        attraction_bias: float = 0.92,
        prune_distance: float = 18.0,
        max_depth: int = 8,
        min_length: float = 3.0,
    ):
        self.attraction_bias = attraction_bias
        self.prune_distance = prune_distance
        self.max_depth = max_depth
        self.min_length = min_length
        self._attractors: list[Pt] = []
        self._branches: list[dict] = []

    @property
    def proof_reference(self) -> str:
        return "docs/proofs/09_lsystem_branching.md"

    @property
    def complexity(self) -> str:
        return "O(B) where B = number of branches"

    @property
    def error_bound(self) -> str:
        return "N/A (generative, not approximation)"

    def execute(self, input_data: tuple) -> list[dict]:
        root, angle, length, attractors = input_data
        self._attractors = attractors
        self._branches = []
        self._grow(root, angle, length, 0)
        return self._branches

    def _grow(self, pos: Pt, angle: float, length: float, depth: int) -> None:
        """Recursively grow branches toward attractors."""
        if depth > self.max_depth or length < self.min_length:
            return

        end = _advance(pos, angle, length)
        nearest, dist = _nearest_point(end, self._attractors)

        if dist > self.prune_distance:
            return

        self._branches.append(
            {
                "start": pos,
                "end": end,
                "depth": depth,
                "length": length,
                "has_flower": depth >= 3 and dist < 8.0,
            }
        )

        attract_angle = math.atan2(nearest[1] - end[1], nearest[0] - end[0])
        biased = angle * (1 - self.attraction_bias) + attract_angle * self.attraction_bias
        child_len = length * LENGTH_DECAY

        half_ga = GOLDEN_ANGLE / 2
        self._grow(end, biased - half_ga, child_len, depth + 1)
        self._grow(end, biased + half_ga, child_len * 0.85, depth + 1)


# --- Free functions ---


def vogel_positions(n: int, center: Pt, radius: float) -> list[Pt]:
    """Generate n Vogel spiral positions centered at (cx, cy)."""
    cx, cy = center
    positions = []
    for i in range(n):
        theta = i * GOLDEN_ANGLE
        r = radius * math.sqrt(i / n) if n > 0 else 0
        positions.append((cx + r * math.cos(theta), cy + r * math.sin(theta)))
    return positions


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


def _advance(pos: Pt, angle: float, length: float) -> Pt:
    """Move from pos in direction angle by length."""
    return (pos[0] + length * math.cos(angle), pos[1] + length * math.sin(angle))


def _nearest_point(pt: Pt, points: list[Pt]) -> tuple[Pt, float]:
    """Find nearest point and distance."""
    best_pt = points[0]
    best_dist = float("inf")
    for p in points:
        d = math.sqrt((pt[0] - p[0]) ** 2 + (pt[1] - p[1]) ** 2)
        if d < best_dist:
            best_dist = d
            best_pt = p
    return best_pt, best_dist
