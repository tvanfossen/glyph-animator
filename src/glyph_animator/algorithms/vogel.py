"""Vogel sunflower phyllotaxis spiral placement."""

from __future__ import annotations

import math

from glyph_animator.algorithms.base import Algorithm
from glyph_animator.constants import GOLDEN_ANGLE

Pt = tuple[float, float]


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


def vogel_positions(n: int, center: Pt, radius: float) -> list[Pt]:
    """Generate n Vogel spiral positions centered at (cx, cy)."""
    cx, cy = center
    positions = []
    for i in range(n):
        theta = i * GOLDEN_ANGLE
        r = radius * math.sqrt(i / n) if n > 0 else 0
        positions.append((cx + r * math.cos(theta), cy + r * math.sin(theta)))
    return positions
