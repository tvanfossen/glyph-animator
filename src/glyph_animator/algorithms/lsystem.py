"""L-system branching growth toward glyph outline attractors."""

from __future__ import annotations

import math

from glyph_animator.algorithms.base import Algorithm
from glyph_animator.constants import GOLDEN_ANGLE, LENGTH_DECAY

Pt = tuple[float, float]


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
