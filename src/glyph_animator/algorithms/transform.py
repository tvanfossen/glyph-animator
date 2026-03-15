"""Coordinate transformation utilities."""

from __future__ import annotations

from glyph_animator.algorithms.base import Algorithm

Pt = tuple[float, float]


class CoordinateTransform(Algorithm[tuple, Pt]):
    """Transform font coordinates to/from image coordinates.

    Font space: Y-up, origin at baseline.
    Image space: Y-down, origin at top-left, with padding and scale.
    """

    def __init__(self, bounds: tuple[float, float, float, float], size: int, padding: int):
        x_min, y_min, x_max, y_max = bounds
        glyph_w = x_max - x_min
        glyph_h = y_max - y_min
        available = size - 2 * padding

        self.scale = min(available / glyph_w, available / glyph_h) if glyph_w and glyph_h else 1.0
        self.x_min = x_min
        self.y_max = y_max
        self.padding = padding

    @property
    def proof_reference(self) -> str:
        return "docs/proofs/10_affine_transform.md"

    @property
    def complexity(self) -> str:
        return "O(1) per point"

    @property
    def error_bound(self) -> str:
        return "Machine epsilon (affine transform)"

    def execute(self, input_data: tuple) -> Pt:
        x, y = input_data
        px = self.padding + (x - self.x_min) * self.scale
        py = self.padding + (self.y_max - y) * self.scale
        return (px, py)
